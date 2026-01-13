# Paper Analysis Agent

A skill-based AI agent that reads, analyzes, summarizes, explains, and generates reproduction code for academic papers.

## Features

- **Read papers** from arXiv IDs, PDF URLs, or local files
- **Summarize** with key takeaways
- **Analyze** methodology, strengths, and weaknesses
- **Explain** in simple language for non-experts
- **Generate pseudo-code** for reproducing methods (when applicable)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
cp .env.example .env
# Edit .env and add your API key

# Run the agent
python skill_agent.py
```

## Usage

### Interactive Mode

```bash
python skill_agent.py
```

Then chat with the agent:
```
You: Read the paper arxiv:2301.00001
You: Summarize this paper
You: What are the weaknesses?
You: Explain this like I'm not an expert
You: Generate code to reproduce the method
```

### Automated Pipeline

Run all 5 analysis steps automatically:

```bash
# Using arXiv ID
python skill_agent.py arxiv:2301.00001

# Using PDF URL
python skill_agent.py https://arxiv.org/pdf/2301.00001.pdf

# Or in interactive mode
You: analyze arxiv:2301.00001
```

The pipeline runs:
1. **Read** - Download and extract text
2. **Summarize** - Generate detailed summary
3. **Analyze** - Methodology, contributions, strengths/weaknesses
4. **Explain** - Simple explanation for non-experts
5. **Reproduce** - Generate pseudo-code (if applicable)

Reports are saved to `paper_reports/` as markdown files.

## Architecture

This project demonstrates **Claude-style skills** - markdown files that guide LLM behavior.

```
User Request
     ↓
SkillAgent (LLM)
     ↓
LLM decides: "I need the paper-reader skill"
     ↓
use_skill("paper-reader") → Returns SKILL.md instructions
     ↓
LLM follows instructions, calls run_script() if needed
     ↓
Response
```

### How Skills Work

1. Skills are defined in `claude_skills/<skill-name>/SKILL.md`
2. Each skill has a `name` and `description` (in YAML frontmatter)
3. The LLM sees all skill descriptions and **decides which to use**
4. When activated, the skill's instructions guide the LLM's approach
5. Skills can include executable scripts in a `scripts/` subdirectory

### Available Skills

| Skill | Purpose |
|-------|---------|
| `paper-reader` | Download and extract text from papers |
| `paper-analyzer` | Analyze methodology, strengths, weaknesses |
| `paper-summarizer` | Generate summaries at different detail levels |
| `paper-explainer` | Explain papers in simple language for non-experts |
| `paper-reproducer` | Generate reproduction pseudo-code |

## Project Structure

```
skills_learning/
├── skill_agent.py          # Main agent and pipeline
├── skill_loader.py         # Parses SKILL.md files
├── requirements.txt        # Dependencies
├── .env.example            # API key template
├── claude_skills/          # Skill definitions
│   ├── paper-reader/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── download_paper.py
│   ├── paper-analyzer/
│   │   └── SKILL.md
│   ├── paper-summarizer/
│   │   └── SKILL.md
│   ├── paper-explainer/
│   │   └── SKILL.md
│   └── paper-reproducer/
│       └── SKILL.md
└── paper_reports/          # Generated reports
```

## Creating New Skills

1. Create a directory: `claude_skills/my-skill/`
2. Create `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: When to use this skill (LLM reads this to decide)
---

# My Skill

## Instructions

Step-by-step guidance for the LLM...
```

3. Optionally add scripts in `scripts/` subdirectory

The LLM will automatically discover and use your skill when appropriate.

## TO-DOs

1. Step 6 - Cataloger: Extend the pipeline to automatically append a high-level summary (Question, Method, Setting) to a central catalog.md journal.

2. Discovery Agent: Add a module to fetch Top-K trending papers from research hubs and feed them into the pipeline in batch mode.

## Requirements

- Python 3.10+
- OpenAI API key (GPT-4o-mini or similar)

## Dependencies

- `openai` - OpenAI API client
- `PyMuPDF` - PDF text extraction
- `arxiv` - arXiv paper downloading
- `pyyaml` - SKILL.md parsing
- `python-dotenv` - Environment variable loading
- `requests` - HTTP requests

## License

MIT


