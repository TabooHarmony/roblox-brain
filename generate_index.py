#!/usr/bin/env python3
"""Auto-generate skill_index.md from SKILL.md frontmatter.

Reads name + description from every skill's frontmatter and writes
skill_index.md with skills grouped by category.

Usage:
    python3 generate_index.py

The categories and ordering match the README skills section.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
INDEX_PATH = ROOT / "skill_index.md"

# Category ordering (must match README)
CATEGORIES = [
    ("Core Language & Architecture", [
        "roblox-luau-core",
        "roblox-luau-types",
        "roblox-luau-patterns",
        "roblox-architecture",
        "roblox-sharp-edges",
    ]),
    ("Economy & Monetization", [
        "roblox-economy",
        "roblox-monetization",
    ]),
    ("Systems & Networking", [
        "roblox-networking",
        "roblox-security",
        "roblox-data",
        "roblox-server-data",
        "roblox-analytics",
        "roblox-npc-ai",
    ]),
    ("Performance & Runtime", [
        "roblox-performance",
    ]),
    ("Building & UI", [
        "roblox-building",
        "roblox-physics",
        "roblox-gui",
        "roblox-animation-vfx",
        "roblox-lighting",
        "roblox-audio",
        "roblox-input",
        "roblox-camera",
    ]),
    ("MCP & Cloud", [
        "roblox-studio-mcp",
        "roblox-cloud",
        "roblox-oauth",
    ]),
    ("Workflow", [
        "roblox-debug",
        "roblox-code-review",
        "roblox-publish-checklist",
        "roblox-tooling",
    ]),
    ("Localization", [
        "roblox-localization",
    ]),
]


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from SKILL.md."""
    match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    body = match.group(1)
    # Multi-line description
    desc_match = re.search(
        r"^description:\s*>\s*\n((?:\s+.+\n?)+)", body, re.MULTILINE
    )
    if desc_match:
        fm["description"] = " ".join(desc_match.group(1).split())
    for line in body.split("\n"):
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        if key == "description":
            if "description" not in fm:
                fm["description"] = val.strip().strip("\"'")
            continue
        if key.startswith("  -") or key.startswith("-"):
            continue
        fm[key] = val.strip()
    return fm


def main() -> int:
    # Collect all skill names + descriptions
    skills = {}
    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = SKILLS_DIR / entry
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        with open(skill_md, encoding="utf-8") as f:
            content = f.read()
        fm = parse_frontmatter(content)
        skills[entry] = fm.get("description", "")

    # Build the index
    lines = [
        "# Skill Index",
        "",
        "Compact index of all roblox-brain skills (~2,800 tokens). Load this at startup to know what's available, then load specific skills as needed.",
        "",
    ]

    # Track which skills we've output
    outputted = set()

    for category_name, skill_names in CATEGORIES:
        # Only output categories that have at least one existing skill
        existing = [s for s in skill_names if s in skills]
        if not existing:
            continue

        lines.append(f"## {category_name}")
        lines.append("")
        lines.append("| Skill | Description |")
        lines.append("|-------|-------------|")
        for name in existing:
            desc = skills[name]
            lines.append(f"| `{name}` | {desc} |")
            outputted.add(name)
        lines.append("")

    # Output any skills not in a category (shouldn't happen, but catches new skills)
    uncategorized = set(skills.keys()) - outputted
    if uncategorized:
        lines.append("## Uncategorized")
        lines.append("")
        lines.append("| Skill | Description |")
        lines.append("|-------|-------------|")
        for name in sorted(uncategorized):
            desc = skills[name]
            lines.append(f"| `{name}` | {desc} |")
        lines.append("")

    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {INDEX_PATH} with {len(skills)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
