#!/usr/bin/env python3
"""
Validate roblox-brain skills for size and structure compliance.

Checks:
- SKILL.md under 3,000 chars
- references/full.md under 35,000 chars
- Description under 150 chars
- Frontmatter has name, description, last_reviewed, sources
- sources field is not empty (use [original] for synthesis)
- '## When to Load' section exists
- '## Quick Reference' section exists
- No '## Overview' or '## 1. Overview' in SKILL.md
- No '## Full Reference' in SKILL.md (should be in references/)
- No unbalanced or nested fenced code blocks
- references/full.md exists (router skills exempt)
- Cross-references (backtick-enclosed `roblox-X`) point to existing skills
- Local `references/...` links point to real files
- Supporting files under `references/` are linked from the skill

Exit code 0 = all checks pass, 1 = failures found.
"""

import os
import re
import sys
from pathlib import Path

MAX_SKILL_CHARS = 3000
MAX_DESC_CHARS = 150
MAX_REF_CHARS = 35000
REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from SKILL.md as a flat key→value dict.

    Multi-line 'description: >' blocks are joined into one string.
    List-valued fields like 'sources:' keep only the first list item as
    a marker; check for field existence with `field in fm`.
    """
    match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    body = match.group(1)
    # Multi-line description: collect indented continuation lines
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
                # Single-line form: "description: foo bar"
                fm["description"] = val.strip().strip("\"'")
            continue
        if key.startswith("  -") or key.startswith("-"):
            continue  # list item, skip — we only care about field presence
        fm[key] = val.strip()
    return fm


def extract_description(content: str) -> str:
    """Get the description string from frontmatter, handling multi-line form."""
    fm = parse_frontmatter(content)
    return fm.get("description", "")


def validate_code_fences(content: str, label: str) -> list[str]:
    """Reject unclosed fences and language-tagged nested openings."""
    errors = []
    fence_pattern = re.compile(r"^ *```([^` ]*)? *$")
    open_line = None
    open_language = ""

    for line_number, line in enumerate(content.splitlines(), 1):
        match = fence_pattern.match(line)
        if not match:
            continue
        language = match.group(1) or ""
        if open_line is None:
            open_line = line_number
            open_language = language
        elif language:
            errors.append(
                f"{label}:{line_number}: nested fenced block '{language}' "
                f"inside {open_language or 'untyped'} fence opened at line {open_line}"
            )
        else:
            open_line = None
            open_language = ""

    if open_line is not None:
        errors.append(
            f"{label}:{open_line}: unclosed {open_language or 'untyped'} fenced block"
        )
    return errors


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
    for field in ("name", "description", "last_reviewed", "sources"):
        if field not in fm:
            errors.append(f"{skill_name}: missing frontmatter field '{field}'")

    # Description length
    desc = extract_description(content)
    if len(desc) > MAX_DESC_CHARS:
        errors.append(
            f"{skill_name}: description is {len(desc)} chars (max {MAX_DESC_CHARS})"
        )

    # '## When to Load' section
    if "## When to Load" not in content:
        errors.append(f"{skill_name}: missing '## When to Load' section")

    # Quick Reference check
    if "## Quick Reference" not in content:
        errors.append(f"{skill_name}: missing '## Quick Reference' section")

    # Full Reference should NOT be in SKILL.md
    if "## Full Reference" in content:
        errors.append(
            f"{skill_name}: '## Full Reference' found in SKILL.md (move to references/)"
        )

    # references/full.md check (router skills are exempt)
    ref_path = os.path.join(skill_dir, "references", "full.md")
    desc_lower = desc.lower()
    is_router = "router" in desc_lower
    if not is_router and not os.path.exists(ref_path):
        errors.append(f"{skill_name}: missing references/full.md")

    # references/full.md size check (router skills exempt)
    if not is_router and os.path.exists(ref_path):
        with open(ref_path, encoding="utf-8") as f:
            ref_content = f.read()
        if len(ref_content) > MAX_REF_CHARS:
            errors.append(
                f"{skill_name}: references/full.md is {len(ref_content)} chars (max {MAX_REF_CHARS})"
            )

    # No '## Overview' or '## 1. Overview' in SKILL.md
    if re.search(r"^##\s+(?:1\.\s+)?Overview\s*$", content, re.MULTILINE):
        errors.append(
            f"{skill_name}: '## Overview' found in SKILL.md (remove it, use When to Load → Quick Reference)"
        )

    # No ```lua code blocks (must use ```luau)
    if re.search(r"```lua *$", content, re.MULTILINE):
        errors.append(
            f"{skill_name}: found ```lua code block (use ```luau instead)"
        )
    errors.extend(validate_code_fences(content, f"{skill_name}: SKILL.md"))
    # Also check references/full.md
    if not is_router and os.path.exists(ref_path):
        with open(ref_path, encoding="utf-8") as f:
            ref_content = f.read()
        if re.search(r"```lua *$", ref_content, re.MULTILINE):
            errors.append(
                f"{skill_name}: found ```lua code block in references/full.md (use ```luau instead)"
            )
        errors.extend(validate_code_fences(ref_content, f"{skill_name}: references/full.md"))

    # sources field must not be empty
    if "sources" in fm:
        # Check if sources is empty ([]) or contains no list items
        fm_match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
        if fm_match:
            fm_body = fm_match.group(1)
            # Check for sources: [] or sources: with no list items
            sources_match = re.search(r"^sources:\s*\[\]?\s*$", fm_body, re.MULTILINE)
            if sources_match:
                errors.append(
                    f"{skill_name}: sources is empty (use [original] for synthesis, or cite real sources)"
                )

    return errors


def collect_all_skill_names() -> set[str]:
    """Return the set of skill directory names under SKILLS_DIR."""
    names = set()
    for entry in os.listdir(SKILLS_DIR):
        path = os.path.join(SKILLS_DIR, entry)
        if os.path.isdir(path):
            names.add(entry)
    return names


def validate_cross_references(all_skill_names: set[str]) -> list[str]:
    """Find `roblox-X` references that don't point to an existing skill.

    Pattern matches cross-refs enclosed in backticks:
      `roblox-name`

    Any `roblox-X` in backticks in the body (not frontmatter) is
    treated as a cross-reference and must point to an existing skill.
    """
    errors = []
    ref_pattern = re.compile(r"`?(roblox-[a-z]+(?:-[a-z]+)*)`?(?:\s*→|\s*\|)")
    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(skill_dir):
            continue
        for filepath in [
            os.path.join(skill_dir, "SKILL.md"),
            os.path.join(skill_dir, "references", "full.md"),
        ]:
            if not os.path.exists(filepath):
                continue
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            # Only scan body, not frontmatter — frontmatter has
            # `sources:` URLs we don't want to flag.
            fm_match = re.match(r"^---\n.+?\n---\n?", content, re.DOTALL)
            body = content[fm_match.end():] if fm_match else content
            for match in ref_pattern.finditer(body):
                ref_name = match.group(1)
                if ref_name not in all_skill_names:
                    line_num = body[: match.start()].count("\n") + 1
                    errors.append(
                        f"{entry}: references non-existent skill '{ref_name}' "
                        f"at {os.path.basename(filepath)}:{line_num}"
                    )
    return errors


def _resolve_local_reference(filepath: Path, reference: str) -> Path:
    """Resolve a reference as written from SKILL.md or references/full.md."""
    reference = reference.lstrip("./")
    if filepath.parent.name == "references" and reference.startswith("references/"):
        return filepath.parent.parent / reference
    return filepath.parent / reference


def _local_reference_matches(filepath: Path, content: str):
    """Yield (reference, position) for local reference paths in a document."""
    patterns = [
        re.compile(r"\]\((?!https?://|mailto:|#)([^)#\s]+)"),
        re.compile(
            r"(?<![\w/])references/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.(?:md|luau)(?![\w])"
        ),
    ]
    seen = set()
    for pattern in patterns:
        for match in pattern.finditer(content):
            reference = match.group(1) if pattern is patterns[0] else match.group(0)
            reference = reference.strip("<>")
            if not reference.startswith("references/") or reference in seen:
                continue
            seen.add(reference)
            yield reference, match.start()


def validate_local_references() -> list[str]:
    """Ensure local references mentioned by skills actually exist."""
    errors = []
    for skill_dir in sorted(Path(SKILLS_DIR).iterdir()):
        if not skill_dir.is_dir():
            continue
        documents = [skill_dir / "SKILL.md"]
        full_reference = skill_dir / "references" / "full.md"
        if full_reference.exists():
            documents.append(full_reference)
        for filepath in documents:
            content = filepath.read_text(encoding="utf-8")
            for reference, position in _local_reference_matches(filepath, content):
                target = _resolve_local_reference(filepath, reference)
                if not target.is_file():
                    line = content[:position].count("\n") + 1
                    errors.append(
                        f"{skill_dir.name}: missing local reference '{reference}' "
                        f"at {filepath.relative_to(REPO_ROOT)}:{line}"
                    )
    return errors


def validate_reference_resources() -> list[str]:
    """Reject unlinked resource files under a skill's references directory."""
    errors = []
    for skill_dir in sorted(Path(SKILLS_DIR).iterdir()):
        if not skill_dir.is_dir():
            continue
        references_dir = skill_dir / "references"
        if not references_dir.is_dir():
            continue
        documents = [skill_dir / "SKILL.md", references_dir / "full.md"]
        searchable = "\n".join(
            path.read_text(encoding="utf-8") for path in documents if path.is_file()
        )
        for resource in sorted(references_dir.rglob("*")):
            if not resource.is_file() or resource.name == "full.md":
                continue
            relative = resource.relative_to(skill_dir).as_posix()
            if relative not in searchable:
                errors.append(
                    f"{skill_dir.name}: unlinked reference resource '{relative}'"
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

    # Cross-reference validation runs across all skills
    all_skill_names = collect_all_skill_names()
    all_errors.extend(validate_cross_references(all_skill_names))
    all_errors.extend(validate_local_references())
    all_errors.extend(validate_reference_resources())

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