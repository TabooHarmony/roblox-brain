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

import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

MAX_SKILL_CHARS = 3000
# Conversational/strategic skills are loaded at planning time, not hot-loaded
# mid-development, so the tight hot-load budget does not apply. Keep the
# explicit list small and justified.
CHAR_CAP_EXEMPT = {"roblox-growth-design"}
MAX_DESC_CHARS = 150
MAX_REF_CHARS = 50000
REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")



def parse_frontmatter(content: str) -> dict:
    """Parse the leading YAML mapping. Invalid YAML is a validation error."""
    match = re.match(r"^---\r?\n(.+?)\r?\n---(?:\r?\n|$)", content, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def extract_description(content: str) -> str:
    """Get the description string from frontmatter, handling multi-line form."""
    fm = parse_frontmatter(content)
    return str(fm.get("description", ""))


def extract_luau_blocks(content: str):
    """Yield (line, code) for complete Luau fences."""
    pattern = re.compile(
        r"^ *```luau(?:[ ,][^`\r\n]*)?\r?\n(.*?)^ *```\s*$",
        re.MULTILINE | re.DOTALL,
    )
    for match in pattern.finditer(content):
        yield content.count("\n", 0, match.start()) + 1, match.group(1)


def validate_luau_syntax(
    documents: list[Path], sources: list[Path] | None = None
) -> list[str]:
    """Compile Luau fences and standalone source references."""
    compiler = shutil.which("luau-compile")
    if compiler is None:
        return ["luau-compile not found; install the pinned Luau release before validation"]

    errors = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for document in documents:
            content = document.read_text(encoding="utf-8")
            for index, (line, code) in enumerate(extract_luau_blocks(content)):
                fixture = Path(temp_dir) / f"block-{len(errors)}-{index}.luau"
                fixture.write_text(code, encoding="utf-8")
                result = subprocess.run(
                    [compiler, str(fixture)], capture_output=True, text=True, check=False
                )
                if result.returncode:
                    detail = (result.stderr or result.stdout).strip().splitlines()[0]
                    try:
                        label = document.relative_to(REPO_ROOT)
                    except ValueError:
                        label = document
                    errors.append(
                        f"{label}:{line}: Luau syntax error: {detail}"
                    )
        for source in sources or []:
            result = subprocess.run(
                [compiler, str(source)], capture_output=True, text=True, check=False
            )
            if result.returncode:
                detail = (result.stderr or result.stdout).strip().splitlines()[0]
                try:
                    label = source.relative_to(REPO_ROOT)
                except ValueError:
                    label = source
                errors.append(f"{label}: Luau syntax error: {detail}")
    return errors


def validate_code_fences(content: str, label: str) -> list[str]:
    """Reject unclosed fences and language-tagged nested openings."""
    errors = []
    fence_pattern = re.compile(r"^ *```([^`]*)? *$")
    open_line = None
    open_language = ""

    for line_number, line in enumerate(content.splitlines(), 1):
        match = fence_pattern.match(line)
        if not match:
            continue
        language = (match.group(1) or "").strip()
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
    if len(content) > MAX_SKILL_CHARS and skill_name not in CHAR_CAP_EXEMPT:
        errors.append(
            f"{skill_name}: SKILL.md is {len(content)} chars (max {MAX_SKILL_CHARS})"
        )

    # Frontmatter checks
    fm = parse_frontmatter(content)
    for field in ("name", "description", "last_reviewed", "sources"):
        if field not in fm:
            errors.append(f"{skill_name}: missing frontmatter field '{field}'")

    if fm.get("name") != skill_name:
        errors.append(
            f"{skill_name}: frontmatter name must match directory (got {fm.get('name')!r})"
        )
    reviewed = fm.get("last_reviewed")
    if type(reviewed) is not dt.date:
        errors.append(f"{skill_name}: last_reviewed must be an unquoted YYYY-MM-DD date")
    elif reviewed > dt.date.today():
        errors.append(f"{skill_name}: last_reviewed cannot be in the future")
    sources = fm.get("sources")
    if not isinstance(sources, list) or not sources or not all(
        isinstance(source, str) and source.strip() for source in sources
    ):
        errors.append(
            f"{skill_name}: sources must be a non-empty YAML list (use original for synthesis)"
        )

    # Description length
    desc = extract_description(content)
    if not desc.strip():
        errors.append(f"{skill_name}: description must be non-empty")
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
    if re.search(r"^## Full Reference\s*$", content, re.MULTILINE):
        errors.append(
            f"{skill_name}: '## Full Reference' found in SKILL.md (move to references/)"
        )

    # references/full.md check (router skills are exempt)
    ref_path = os.path.join(skill_dir, "references", "full.md")
    is_router = fm.get("kind") == "router"
    if not is_router and not os.path.exists(ref_path):
        errors.append(f"{skill_name}: missing references/full.md")

    # references/full.md size check (router skills exempt)
    if not is_router and os.path.exists(ref_path):
        with open(ref_path, encoding="utf-8") as f:
            ref_content = f.read()
        if len(ref_content) > MAX_REF_CHARS and skill_name not in CHAR_CAP_EXEMPT:
            errors.append(
                f"{skill_name}: references/full.md is {len(ref_content)} chars (max {MAX_REF_CHARS})"
            )

    # No '## Overview' or '## 1. Overview' in SKILL.md
    if re.search(
        r"^##\s+(?:1\.\s+)?Overview\s*$", content, re.MULTILINE | re.IGNORECASE
    ):
        errors.append(
            f"{skill_name}: '## Overview' found in SKILL.md (remove it, use When to Load → Quick Reference)"
        )

    # No ```lua code blocks (must use ```luau)
    if re.search(r"^ *```lua(?:[\s,]|$)", content, re.MULTILINE):
        errors.append(
            f"{skill_name}: found ```lua code block (use ```luau instead)"
        )
    errors.extend(validate_code_fences(content, f"{skill_name}: SKILL.md"))
    # Also check references/full.md
    if not is_router and os.path.exists(ref_path):
        with open(ref_path, encoding="utf-8") as f:
            ref_content = f.read()
        if re.search(r"^ *```lua(?:[\s,]|$)", ref_content, re.MULTILINE):
            errors.append(
                f"{skill_name}: found ```lua code block in references/full.md (use ```luau instead)"
            )
        errors.extend(validate_code_fences(ref_content, f"{skill_name}: references/full.md"))

    return errors


def collect_all_skill_names() -> set[str]:
    """Return the set of skill directory names under SKILLS_DIR."""
    names = set()
    for entry in os.listdir(SKILLS_DIR):
        path = os.path.join(SKILLS_DIR, entry)
        if os.path.isdir(path):
            names.add(entry)
    return names


def validate_catalog(all_skill_names: set[str], root: Path = REPO_ROOT) -> list[str]:
    """Keep public skill counts and README catalog rows tied to the real tree."""
    errors = []
    expected_count = len(all_skill_names)
    readme_path = root / "README.md"
    agents_path = root / "AGENTS.md"
    if not readme_path.is_file() or not agents_path.is_file():
        return ["catalog validation requires README.md and AGENTS.md"]

    readme = readme_path.read_text(encoding="utf-8")
    agents = agents_path.read_text(encoding="utf-8")
    count_patterns = (
        (readme, r"(?m)^- (\d+) focused skills\b", "README summary"),
        (readme, r"(?m)^## Skills \((\d+)\)$", "README heading"),
        (agents, r"(?m)\b(\d+) curated skills\b", "AGENTS summary"),
    )
    for document, pattern, label in count_patterns:
        match = re.search(pattern, document)
        if not match:
            errors.append(f"{label}: skill count not found")
        elif int(match.group(1)) != expected_count:
            errors.append(
                f"{label}: says {match.group(1)} skills, found {expected_count}"
            )

    catalog_row_names = re.findall(
        r"(?m)^\| `(roblox-[a-z0-9]+(?:-[a-z0-9]+)*)` \|", readme
    )
    catalog_rows = set(catalog_row_names)
    missing = sorted(all_skill_names - catalog_rows)
    extra = sorted(catalog_rows - all_skill_names)
    if missing:
        errors.append(f"README catalog missing: {', '.join(missing)}")
    if extra:
        errors.append(f"README catalog has unknown skills: {', '.join(extra)}")
    duplicates = sorted(
        name for name in catalog_rows if catalog_row_names.count(name) > 1
    )
    if duplicates:
        errors.append(f"README catalog has duplicate rows: {', '.join(duplicates)}")
    return errors


def validate_cross_references(all_skill_names: set[str]) -> list[str]:
    """Find `roblox-X` references that don't point to an existing skill.

    Pattern matches cross-refs enclosed in backticks:
      `roblox-name`

    Any `roblox-X` in backticks in the body (not frontmatter) is
    treated as a cross-reference and must point to an existing skill.
    """
    errors = []
    ref_pattern = re.compile(r"`(roblox-[a-z0-9]+(?:-[a-z0-9]+)*)`")
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
            if not filepath.is_file():
                continue
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
    all_errors.extend(validate_catalog(all_skill_names))
    all_errors.extend(validate_cross_references(all_skill_names))
    all_errors.extend(validate_local_references())
    all_errors.extend(validate_reference_resources())
    documents = sorted(Path(SKILLS_DIR).glob("*/SKILL.md"))
    documents.extend(sorted(Path(SKILLS_DIR).glob("*/references/full.md")))
    sources = sorted(Path(SKILLS_DIR).glob("*/references/**/*.luau"))
    all_errors.extend(validate_luau_syntax(documents, sources))
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