"""Agent that uses markdown-based skills (Claude-style)."""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

from skill_loader import SkillLoader, Skill

load_dotenv()


class PaperAnalysisPipeline:
    """
    Automated pipeline that processes a paper through all analysis steps.

    Pipeline steps:
    1. Read paper (download and extract text)
    2. Summarize (generate summary)
    3. Analyze (methodology, strengths, weaknesses)
    4. Explain (simple explanation for non-experts)
    5. Reproduce (generate pseudo-code if applicable)
    """

    def __init__(self, agent: "SkillAgent", output_dir: str = "paper_reports"):
        self.agent = agent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def run(self, paper_source: str, verbose: bool = True) -> dict:
        """
        Run the full analysis pipeline on a paper.

        Args:
            paper_source: arXiv ID, PDF path, or URL
            verbose: Print progress updates

        Returns:
            Dict with all analysis results
        """
        results = {
            "source": paper_source,
            "timestamp": datetime.now().isoformat(),
            "steps": {},
        }

        conversation_history = []

        # Step 1: Read the paper
        if verbose:
            print("\n" + "=" * 60)
            print("Step 1/5: Reading paper...")
            print("=" * 60)

        read_prompt = f"Read the paper: {paper_source}"
        read_response = self.agent.run(read_prompt, conversation_history)
        results["steps"]["read"] = read_response
        conversation_history.append({"role": "user", "content": read_prompt})
        conversation_history.append({"role": "assistant", "content": read_response})

        if verbose:
            print(f"\n{read_response[:500]}..." if len(read_response) > 500 else f"\n{read_response}")

        # Step 2: Summarize
        if verbose:
            print("\n" + "=" * 60)
            print("Step 2/5: Generating summary...")
            print("=" * 60)

        summary_prompt = "Now provide a detailed summary of this paper, including key takeaways."
        summary_response = self.agent.run(summary_prompt, conversation_history)
        results["steps"]["summary"] = summary_response
        conversation_history.append({"role": "user", "content": summary_prompt})
        conversation_history.append({"role": "assistant", "content": summary_response})

        if verbose:
            print(f"\n{summary_response}")

        # Step 3: Analyze
        if verbose:
            print("\n" + "=" * 60)
            print("Step 3/5: Analyzing methodology, strengths, and weaknesses...")
            print("=" * 60)

        analyze_prompt = """Analyze this paper in detail:
1. What is the core methodology?
2. What are the key contributions?
3. What are the strengths of this work?
4. What are the weaknesses and limitations?
5. What technical details are important for understanding the approach?"""
        analyze_response = self.agent.run(analyze_prompt, conversation_history)
        results["steps"]["analysis"] = analyze_response
        conversation_history.append({"role": "user", "content": analyze_prompt})
        conversation_history.append({"role": "assistant", "content": analyze_response})

        if verbose:
            print(f"\n{analyze_response}")

        # Step 4: Explain for non-experts
        if verbose:
            print("\n" + "=" * 60)
            print("Step 4/5: Creating simple explanation for non-experts...")
            print("=" * 60)

        explain_prompt = """Now explain this paper in simple, accessible language for someone who is NOT an expert.

Use everyday analogies, avoid jargon, and focus on:
- Why should anyone care about this?
- What problem does it solve in simple terms?
- How does the solution work (using analogies)?
- What's the real-world impact?

Make it engaging and easy to understand for a general audience."""
        explain_response = self.agent.run(explain_prompt, conversation_history)
        results["steps"]["explanation"] = explain_response
        conversation_history.append({"role": "user", "content": explain_prompt})
        conversation_history.append({"role": "assistant", "content": explain_response})

        if verbose:
            print(f"\n{explain_response}")

        # Step 5: Reproduce (only if applicable)
        if verbose:
            print("\n" + "=" * 60)
            print("Step 5/5: Checking if reproduction is applicable...")
            print("=" * 60)

        reproduce_prompt = """Based on your analysis of this paper, determine if code reproduction is applicable.

If the paper proposes a novel method, algorithm, model architecture, or technique that can be implemented:
- Generate Python/PyTorch pseudo-code to reproduce the main method
- Include: model architecture, training loop, key hyperparameters, important implementation details

If the paper is a survey, position paper, empirical study, dataset paper, or does NOT propose a reproducible method:
- Explain why reproduction is not applicable
- Instead, summarize what kind of code/tools the paper discusses or evaluates (if any)

Be explicit about your decision and reasoning."""
        reproduce_response = self.agent.run(reproduce_prompt, conversation_history)
        results["steps"]["reproduction"] = reproduce_response
        conversation_history.append({"role": "user", "content": reproduce_prompt})
        conversation_history.append({"role": "assistant", "content": reproduce_response})

        if verbose:
            print(f"\n{reproduce_response}")

        # Save report
        report_path = self._save_report(results, paper_source)
        results["report_path"] = str(report_path)

        if verbose:
            print("\n" + "=" * 60)
            print(f"Pipeline complete! Report saved to: {report_path}")
            print("=" * 60)

        return results

    def _save_report(self, results: dict, paper_source: str) -> Path:
        """Save the analysis report to a markdown file."""
        # Create filename from source
        safe_name = "".join(c if c.isalnum() or c in ".-_" else "_" for c in paper_source)
        safe_name = safe_name[:50]  # Limit length
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{safe_name}_{timestamp}.md"
        filepath = self.output_dir / filename

        # Build markdown report
        report = f"""# Paper Analysis Report

**Source:** {results['source']}
**Generated:** {results['timestamp']}

---

## Summary

{results['steps'].get('summary', 'Not available')}

---

## Detailed Analysis

{results['steps'].get('analysis', 'Not available')}

---

## Simple Explanation (For Non-Experts)

{results['steps'].get('explanation', 'Not available')}

---

## Reproduction Code

{results['steps'].get('reproduction', 'Not available')}

---

## Raw Paper Reading Output

<details>
<summary>Click to expand</summary>

{results['steps'].get('read', 'Not available')}

</details>
"""

        filepath.write_text(report, encoding="utf-8")
        return filepath


class SkillAgent:
    """
    An agent that uses markdown-based skills.

    Skills are loaded from SKILL.md files and provide instructions
    that guide the agent's behavior. The agent can also execute
    scripts bundled with skills.

    The LLM can dynamically select which skills to use via the use_skill tool.
    """

    def __init__(
        self,
        skills_dir: str = "claude_skills",
        model: str = "gpt-4o-mini",
    ):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.skills_dir = skills_dir

        # Load skills
        self.skill_loader = SkillLoader(skills_dir)
        self.skills = self.skill_loader.load_all()

        # Track currently active skill (selected by LLM)
        self.active_skill: Skill | None = None

        print(f"Loaded {len(self.skills)} skills: {list(self.skills.keys())}")

    def _build_system_prompt(self, active_skill: Skill | None = None) -> str:
        """Build the system prompt, optionally including an active skill."""
        base_prompt = """You are a helpful research assistant specialized in academic papers.

## Available Skills

You have access to the following skills. Use the `use_skill` tool to activate a skill when appropriate:
"""
        # Add skill descriptions
        for skill in self.skills.values():
            base_prompt += f"\n- **{skill.name}**: {skill.description}"

        base_prompt += """

## How to Use Skills

1. **Decide if a skill is needed**: Based on the user's request, determine which skill (if any) would help.
2. **Activate the skill**: Call `use_skill` with the skill name to load its instructions.
3. **Follow the instructions**: Once activated, the skill's detailed instructions will guide your approach.
4. **Skip if not applicable**: If no skill is relevant (e.g., paper has no method to reproduce), don't use that skill.

## Tools Available
- `use_skill`: Activate a skill to get its detailed instructions
- `run_script`: Execute a Python script from a skill's scripts directory
- `read_file`: Read a file from disk
"""

        # If a skill is active, include its full instructions
        if active_skill:
            base_prompt += f"""

---
## Active Skill: {active_skill.name}

{active_skill.instructions}
---
"""

        return base_prompt

    def _get_tools(self) -> list[dict]:
        """Define tools the agent can use."""
        # Build skill names for the enum
        skill_names = list(self.skills.keys())

        return [
            {
                "type": "function",
                "function": {
                    "name": "use_skill",
                    "description": (
                        "Activate a skill to get its detailed instructions. "
                        "Call this when you need guidance on how to approach a specific task. "
                        "The skill's instructions will be returned and you should follow them."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "enum": skill_names,
                                "description": "Name of the skill to activate",
                            },
                            "reason": {
                                "type": "string",
                                "description": "Brief reason why this skill is needed for the current task",
                            },
                        },
                        "required": ["skill_name", "reason"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "run_script",
                    "description": "Execute a Python script from a skill's scripts directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "Name of the skill containing the script",
                            },
                            "script_name": {
                                "type": "string",
                                "description": "Name of the script file (e.g., 'download_paper.py')",
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Arguments to pass to the script",
                            },
                        },
                        "required": ["skill_name", "script_name", "args"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a file from disk",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file to read",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
        ]

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool and return the result."""
        if tool_name == "use_skill":
            return self._use_skill(
                arguments["skill_name"],
                arguments.get("reason", ""),
            )
        elif tool_name == "run_script":
            return self._run_script(
                arguments["skill_name"],
                arguments["script_name"],
                arguments.get("args", []),
            )
        elif tool_name == "read_file":
            return self._read_file(arguments["path"])
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def _use_skill(self, skill_name: str, reason: str) -> str:
        """Activate a skill and return its instructions."""
        skill = self.skills.get(skill_name)
        if not skill:
            return json.dumps({"error": f"Skill not found: {skill_name}"})

        self.active_skill = skill

        # Return the skill instructions
        result = {
            "skill_activated": skill_name,
            "reason": reason,
            "instructions": skill.instructions,
        }

        # List available scripts if any
        scripts = skill.list_scripts()
        if scripts:
            result["available_scripts"] = [s.name for s in scripts]

        return json.dumps(result, indent=2, default=str)

    def _run_script(self, skill_name: str, script_name: str, args: list) -> str:
        """Run a script from a skill's scripts directory."""
        skill = self.skills.get(skill_name)
        if not skill:
            return json.dumps({"error": f"Skill not found: {skill_name}"})

        script_path = skill.directory / "scripts" / script_name
        if not script_path.exists():
            return json.dumps({"error": f"Script not found: {script_path}"})

        try:
            result = subprocess.run(
                ["python", str(script_path)] + args,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path.cwd()),
            )

            if result.returncode != 0:
                return json.dumps({
                    "error": result.stderr or "Script failed",
                    "stdout": result.stdout,
                })

            return result.stdout

        except subprocess.TimeoutExpired:
            return json.dumps({"error": "Script timed out"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _read_file(self, path: str) -> str:
        """Read a file and return its contents."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return content[:50000]  # Truncate if too long
        except Exception as e:
            return json.dumps({"error": str(e)})

    def run(
        self,
        user_input: str,
        conversation_history: list[dict] | None = None,
    ) -> str:
        """
        Process user input and return the agent's response.

        The agent will:
        1. Decide which skills to use (via use_skill tool)
        2. Load skill instructions when activated
        3. Execute any needed tools
        4. Return the final response
        """
        # Build messages - LLM will choose skills dynamically
        messages = [
            {"role": "system", "content": self._build_system_prompt(self.active_skill)}
        ]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_input})

        # Get tools
        tools = self._get_tools()

        # Chat loop with tool execution
        max_iterations = 10
        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # If no tool calls, return the response
            if not assistant_message.tool_calls:
                return assistant_message.content or ""

            # Add assistant message
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ],
            })

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                result = self._execute_tool(tool_name, arguments)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        return "Max iterations reached."


def run_pipeline(paper_source: str, model: str = "gpt-4o-mini"):
    """Run the automated paper analysis pipeline."""
    agent = SkillAgent(model=model)
    pipeline = PaperAnalysisPipeline(agent)
    return pipeline.run(paper_source)


def run_interactive():
    """Run an interactive session with the skill-based agent."""
    print("=" * 60)
    print("Paper Analysis Agent (Claude-style Skills)")
    print("=" * 60)

    agent = SkillAgent()

    print("""
Modes:
- Interactive: Chat with the agent step by step
- Pipeline: Type 'analyze <paper>' to run full automatic analysis

Examples:
- "analyze arxiv:2301.00001"  (runs full 5-step pipeline)
- "Read the paper arxiv:2301.00001"
- "Summarize this paper"
- "What are the weaknesses?"
- "Explain this paper simply for a non-expert"
- "ELI5 this paper"

Type 'quit' to exit.
""")

    conversation_history = []
    pipeline = PaperAnalysisPipeline(agent)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        # Check for pipeline command
        if user_input.lower().startswith("analyze "):
            paper_source = user_input[8:].strip()
            if paper_source:
                print(f"\nStarting full analysis pipeline for: {paper_source}")
                pipeline.run(paper_source)
                # Reset conversation after pipeline
                conversation_history = []
                continue
            else:
                print("Please provide a paper source (arXiv ID, path, or URL)")
                continue

        print("\nAgent: Processing...\n")

        response = agent.run(user_input, conversation_history)

        print(f"Agent: {response}")

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})


def main():
    """Entry point - supports command line args or interactive mode."""
    import sys

    if len(sys.argv) > 1:
        # Command line mode: python skill_agent.py <paper_source>
        paper_source = " ".join(sys.argv[1:])
        print(f"Running pipeline for: {paper_source}")
        run_pipeline(paper_source)
    else:
        # Interactive mode
        run_interactive()


if __name__ == "__main__":
    main()
