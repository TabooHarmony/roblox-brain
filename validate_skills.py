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


BACKTICK_FENCE_RE = re.compile(r"^ *(?P<fence>`{3,})(?P<info>[^`]*)$")
TILDE_FENCE_RE = re.compile(r"^ *(?P<fence>~{3,})(?P<info>.*)$")


def _fence_line(line: str):
    """Return (fence_char, fence_length, language) for a fence line, else None."""
    for pattern in (BACKTICK_FENCE_RE, TILDE_FENCE_RE):
        match = pattern.match(line)
        if match:
            fence = match.group("fence")
            return fence[0], len(fence), match.group("info").strip()
    return None


def _closes_fence(line: str, fence_char: str, fence_length: int) -> bool:
    """True when line closes a fence opened with fence_char x fence_length."""
    fence = _fence_line(line)
    if fence is None or fence[0] != fence_char or fence[1] < fence_length:
        return False
    return fence[2] == ""  # closing fences carry no info string


def _iter_fenced_blocks(content: str):
    """Yield (open_line, language, code, close_line) for complete fenced blocks.

    Recognizes 3+ backtick and 3+ tilde fences (CommonMark: a block closes
    at a fence of the same character that is at least as long and carries
    no info string).
    """
    lines = content.splitlines()
    open_fence = None  # (char, length, language, open_line)
    for line_number, line in enumerate(lines, 1):
        fence = _fence_line(line)
        if open_fence is None:
            if fence is not None:
                open_fence = (*fence, line_number)
        elif _closes_fence(line, open_fence[0], open_fence[1]):
            _char, _length, language, open_line = open_fence
            code = "\n".join(lines[open_line : line_number - 1])
            yield open_line, language, code, line_number
            open_fence = None
    # A fence left open at EOF is not yielded here; unclosed detection
    # lives in validate_code_fences.


def extract_luau_blocks(content: str):
    """Yield (line, code) for complete Luau fences.

    Recognizes ```luau, longer backtick fences such as ````luau, and tilde
    fences such as ~~~luau, each with optional comma/space annotations
    (```luau,linenos).
    """
    for open_line, language, code, _close_line in _iter_fenced_blocks(content):
        if language == "luau" or language.startswith(("luau ", "luau,")):
            yield open_line, code


def validate_luau_syntax(
    documents: list[Path], sources: list[Path] | None = None
) -> tuple[list[str], int, int]:
    """Compile Luau fences and standalone source references.

    Returns (errors, snippets_recognized, snippets_compiled) so callers can
    surface a silent zero (recognition misses) in the validator output.
    """
    compiler = shutil.which("luau-compile")
    if compiler is None:
        return (
            ["luau-compile not found; install the pinned Luau release before validation"],
            0,
            0,
        )

    errors = []
    recognized = 0
    compiled = 0
    with tempfile.TemporaryDirectory() as temp_dir:
        for document in documents:
            content = document.read_text(encoding="utf-8")
            blocks = list(extract_luau_blocks(content))
            recognized += len(blocks)
            for index, (line, code) in enumerate(blocks):
                fixture = Path(temp_dir) / f"block-{compiled}-{index}.luau"
                fixture.write_text(code, encoding="utf-8")
                result = subprocess.run(
                    [compiler, str(fixture)], capture_output=True, text=True, check=False
                )
                compiled += 1
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
            compiled += 1
            if result.returncode:
                detail = (result.stderr or result.stdout).strip().splitlines()[0]
                try:
                    label = source.relative_to(REPO_ROOT)
                except ValueError:
                    label = source
                errors.append(f"{label}: Luau syntax error: {detail}")
    return errors, recognized, compiled


def validate_code_fences(content: str, label: str) -> list[str]:
    """Reject unclosed fences and language-tagged nested openings.

    Recognizes 3+ backtick and 3+ tilde fences so alternate Luau fence
    spellings (````luau, ~~~luau) get the same structural checks.
    """
    errors = []
    open_line = None
    open_char = ""
    open_length = 0
    open_language = ""

    for line_number, line in enumerate(content.splitlines(), 1):
        fence = _fence_line(line)
        if fence is None:
            continue
        fence_char, fence_length, language = fence
        if open_line is None:
            open_line = line_number
            open_char = fence_char
            open_length = fence_length
            open_language = language
        elif _closes_fence(line, open_char, open_length):
            open_line = None
            open_char = ""
            open_length = 0
            open_language = ""
        elif language:
            errors.append(
                f"{label}:{line_number}: nested fenced block '{language}' "
                f"inside {open_language or 'untyped'} fence opened at line {open_line}"
            )

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


def skill_directories() -> list[Path]:
    """Find skills in flat or one-category-deep layouts, including incomplete dirs."""
    directories = []
    for entry in sorted(Path(SKILLS_DIR).iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in {"core", "gameplay", "design", "tools"}:
            directories.extend(sorted(path for path in entry.iterdir() if path.is_dir()))
        else:
            directories.append(entry)
    return directories


def collect_all_skill_names() -> set[str]:
    return {directory.name for directory in skill_directories()}


def validate_catalog(all_skill_names: set[str], root: Path = REPO_ROOT) -> list[str]:
    """Keep the public README's skill counts and catalog tied to the real tree."""
    errors = []
    expected_count = len(all_skill_names)
    readme_path = root / "README.md"
    if not readme_path.is_file():
        return ["catalog validation requires README.md"]

    readme = readme_path.read_text(encoding="utf-8")
    count_patterns = (
        (readme, r"(?m)^## Skills \((\d+)\)$", "README heading"),
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
    for directory in skill_directories():
        entry = directory.name
        for filepath in [
            str(directory / "SKILL.md"),
            str(directory / "references" / "full.md"),
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


def _normalize_local_reference(reference: str) -> str:
    """Strip redundant leading ./ segments without erasing ../ meaning."""
    while reference.startswith("./"):
        reference = reference[2:]
    return reference


def _resolve_local_reference(filepath: Path, reference: str) -> Path:
    """Resolve a reference as written from SKILL.md or references/full.md."""
    normalized = _normalize_local_reference(reference)
    if filepath.parent.name == "references" and normalized.startswith("references/"):
        return filepath.parent.parent / normalized
    return filepath.parent / normalized


def _local_reference_matches(filepath: Path, content: str):
    """Yield (reference, position) for local reference paths in a document.

    The yielded reference is normalized (leading ./ stripped) so the
    `references/x.md` and `./references/x.md` spellings classify alike.
    """
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
            reference = _normalize_local_reference(reference.strip("<>"))
            is_local_doc = (
                reference.startswith("references/")
                or reference.startswith("../")
                or (reference.startswith("./") and "/../" in reference)
            )
            if not is_local_doc or reference in seen:
                continue
            seen.add(reference)
            yield reference, match.start()


def _display_path(path: Path) -> str:
    """Path relative to the repo root when possible, else the absolute path."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def validate_local_references() -> list[str]:
    """Ensure local references mentioned by skills actually exist and stay
    inside their skill directory."""
    errors = []
    for skill_dir in skill_directories():
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
                line = content[:position].count("\n") + 1
                if not target.is_file():
                    errors.append(
                        f"{skill_dir.name}: missing local reference '{reference}' "
                        f"at {_display_path(filepath)}:{line}"
                    )
                    continue
                try:
                    target.resolve().relative_to(skill_dir.resolve())
                except ValueError:
                    errors.append(
                        f"{skill_dir.name}: local reference escapes skill directory "
                        f"'{reference}' at {_display_path(filepath)}:{line}"
                    )
    return errors


def validate_reference_resources() -> list[str]:
    """Reject unlinked resource files under a skill's references directory."""
    errors = []
    for skill_dir in skill_directories():
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

    directories = skill_directories()
    all_errors = []
    for skill_dir in directories:
        all_errors.extend(validate_skill(str(skill_dir)))

    # Cross-reference validation runs across all skills
    all_skill_names = collect_all_skill_names()
    if len(all_skill_names) != len(directories):
        all_errors.append("duplicate skill directory name across categories")
    all_errors.extend(validate_catalog(all_skill_names))
    all_errors.extend(validate_cross_references(all_skill_names))
    all_errors.extend(validate_local_references())
    all_errors.extend(validate_reference_resources())
    documents = [path for directory in directories for path in
                 (directory / "SKILL.md", directory / "references" / "full.md")
                 if path.is_file()]
    sources = [path for directory in directories
               for path in (directory / "references").rglob("*.luau")]
    luau_errors, luau_recognized, luau_compiled = validate_luau_syntax(documents, sources)
    all_errors.extend(luau_errors)
    print(f"Validated {len(directories)} skills")
    print(
        f"Luau snippets: {luau_recognized} recognized, "
        f"{luau_compiled} compiled"
    )

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