#!/usr/bin/env python3
"""
Validate roblox-brain skills for size and structure compliance.

Checks:
- SKILL.md under 3,000 chars
- Description under 150 chars
- Frontmatter has name, description, last_reviewed
- '## Quick Reference' section exists
- No '## Full Reference' in SKILL.md (should be in references/)

Exit code 0 = all checks pass, 1 = failures found.
"""

import os
import re
import sys

MAX_SKILL_CHARS = 3000
MAX_DESC_CHARS = 150
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from SKILL.md."""
    match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip()
    return fm


def validate_skill(skill_dir: str) -> list[str]:
    """Validate a single skill directory. Returns list of errors."""
    errors = []
    skill_name = os.path.basename(skill_dir)
    skill_md = os.path.join(skill_dir, "SKILL.md")

    if not os.path.exists(skill_md):
        return [f"{skill_name}: SKILL.md not found"]

    with open(skill_md, encoding="utf-8") as f:
        content = f.read()

    # Size check
    if len(content) > MAX_SKILL_CHARS:
        errors.append(
            f"{skill_name}: SKILL.md is {len(content)} chars (max {MAX_SKILL_CHARS})"
        )

    # Frontmatter checks
    fm = parse_frontmatter(content)
    for field in ("name", "description", "last_reviewed"):
        if field not in fm:
            errors.append(f"{skill_name}: missing frontmatter field '{field}'")

    # Description length
    desc = fm.get("description", "")
    # Handle multi-line descriptions
    if desc == ">":
        # Multi-line: extract from content
        desc_match = re.search(
            r"description:\s*>\n((?:\s+.+\n?)+)", content
        )
        if desc_match:
            desc = " ".join(desc_match.group(1).split())

    if len(desc) > MAX_DESC_CHARS:
        errors.append(
            f"{skill_name}: description is {len(desc)} chars (max {MAX_DESC_CHARS})"
        )

    # Quick Reference check
    if "## Quick Reference" not in content:
        errors.append(f"{skill_name}: missing '## Quick Reference' section")

    # Full Reference should NOT be in SKILL.md
    if "## Full Reference" in content:
        errors.append(
            f"{skill_name}: '## Full Reference' found in SKILL.md (move to references/)"
        )

    return errors


def main():
    if not os.path.isdir(SKILLS_DIR):
        print(f"Error: skills directory not found: {SKILLS_DIR}")
        sys.exit(1)

    all_errors = []
    skill_count = 0

    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(skill_dir):
            continue
        skill_count += 1
        errors = validate_skill(skill_dir)
        all_errors.extend(errors)

    print(f"Validated {skill_count} skills")

    if all_errors:
        print(f"\n❌ {len(all_errors)} error(s):\n")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ All checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
