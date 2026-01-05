"""Skill loader - loads and manages markdown-based skills."""

import os
import re
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Skill:
    """A loaded skill from SKILL.md."""
    name: str
    description: str
    instructions: str
    allowed_tools: list[str] | None = None
    model: str | None = None
    directory: Path | None = None

    def get_supporting_file(self, filename: str) -> str | None:
        """Read a supporting file from the skill directory."""
        if not self.directory:
            return None
        filepath = self.directory / filename
        if filepath.exists():
            return filepath.read_text(encoding="utf-8")
        return None

    def list_scripts(self) -> list[Path]:
        """List all scripts in the skill's scripts/ directory."""
        if not self.directory:
            return []
        scripts_dir = self.directory / "scripts"
        if not scripts_dir.exists():
            return []
        return list(scripts_dir.glob("*.py"))


class SkillLoader:
    """
    Loads markdown-based skills from directories.

    Skills are stored as SKILL.md files with YAML frontmatter:
    ---
    name: skill-name
    description: What this skill does
    allowed-tools: Read, Bash  # optional
    ---

    # Instructions
    ...
    """

    def __init__(self, skills_dir: str | Path = "skills"):
        self.skills_dir = Path(skills_dir)
        self._skills: dict[str, Skill] = {}

    def load_all(self) -> dict[str, Skill]:
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            return {}

        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill = self._parse_skill_file(skill_file, skill_dir)
                    if skill:
                        self._skills[skill.name] = skill

        return self._skills

    def _parse_skill_file(self, filepath: Path, directory: Path) -> Skill | None:
        """Parse a SKILL.md file into a Skill object."""
        try:
            content = filepath.read_text(encoding="utf-8")

            # Extract YAML frontmatter
            frontmatter_match = re.match(
                r'^---\s*\n(.*?)\n---\s*\n(.*)$',
                content,
                re.DOTALL
            )

            if not frontmatter_match:
                print(f"Warning: No frontmatter in {filepath}")
                return None

            yaml_content = frontmatter_match.group(1)
            markdown_content = frontmatter_match.group(2).strip()

            # Parse YAML
            metadata = yaml.safe_load(yaml_content)

            if not metadata.get("name") or not metadata.get("description"):
                print(f"Warning: Missing name or description in {filepath}")
                return None

            # Parse allowed-tools if present
            allowed_tools = None
            if "allowed-tools" in metadata:
                tools_str = metadata["allowed-tools"]
                if isinstance(tools_str, str):
                    allowed_tools = [t.strip() for t in tools_str.split(",")]
                elif isinstance(tools_str, list):
                    allowed_tools = tools_str

            return Skill(
                name=metadata["name"],
                description=metadata["description"],
                instructions=markdown_content,
                allowed_tools=allowed_tools,
                model=metadata.get("model"),
                directory=directory,
            )

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self._skills.get(name)

    def match_skill(self, user_input: str) -> Skill | None:
        """
        Find the best matching skill for user input.

        Uses simple keyword matching. In production, you'd use
        embeddings or the LLM for semantic matching.
        """
        user_lower = user_input.lower()

        best_match = None
        best_score = 0

        for skill in self._skills.values():
            # Simple keyword matching on description
            desc_words = set(skill.description.lower().split())
            input_words = set(user_lower.split())
            overlap = len(desc_words & input_words)

            # Also check skill name
            if skill.name.replace("-", " ") in user_lower:
                overlap += 5

            if overlap > best_score:
                best_score = overlap
                best_match = skill

        return best_match if best_score > 0 else None

    def get_all_descriptions(self) -> list[dict]:
        """Get name and description for all skills (for LLM context)."""
        return [
            {"name": s.name, "description": s.description}
            for s in self._skills.values()
        ]
