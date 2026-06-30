# Plan 006: Strengthen validate_skills.py to catch structural issues

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat e494289..HEAD -- validate_skills.py`
> If this file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: 005 (structure must be standardized first or validation will fail)
- **Category**: dx
- **Planned at**: commit `e494289`, 2026-06-29

## Why this matters

The current `validate_skills.py` checks 5 things: SKILL.md size, description length, required frontmatter fields, Quick Reference section, and no Full Reference in SKILL.md. It does NOT check for `## When to Load` (which 10 skills were missing), `sources:` field, or cross-reference validity. After Plan 005 standardizes the structure, the validator should enforce it so future contributions don't regress.

## Current state

File: `validate_skills.py` (repo root, 113 lines)

```python
MAX_SKILL_CHARS = 3000
MAX_DESC_CHARS = 150

def validate_skill(skill_dir: str) -> list[str]:
    # Checks:
    # 1. SKILL.md exists
    # 2. len(content) > MAX_SKILL_CHARS
    # 3. Frontmatter has: name, description, last_reviewed
    # 4. Description length > MAX_DESC_CHARS
    # 5. "## Quick Reference" in content
    # 6. "## Full Reference" NOT in content
```

**What it does NOT check** (the gaps):
- `## When to Load` section presence
- `sources:` field in frontmatter
- Cross-reference targets exist (e.g. `roblox-api` referenced but doesn't exist)
- `references/full.md` exists (the router skill is the only exception)

## Commands you will need

| Purpose | Command | Expected on success |
|-----------|--------|---------------------|
| Run validator | `python3 validate_skills.py` | "All checks passed" |
| Test fail case | `python3 -c "import validate_skills; ..."` | (manual testing) |

## Scope

**In scope** (the only files you should modify):
- `validate_skills.py`

**Out of scope** (do NOT touch):
- Any skill files
- CI config
- README

## Git workflow

- Branch: `advisor/006-strengthen-validation`
- Single commit.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Add `## When to Load` check

In the `validate_skill()` function, after the Quick Reference check, add:

```python
# When to Load check
if "## When to Load" not in content:
    errors.append(f"{skill_name}: missing '## When to Load' section")
```

### Step 2: Add `sources:` field check

In the frontmatter validation loop, add `sources` to the required fields. BUT: some skills may legitimately have `sources: []` or the field may be multiline. Handle both:

```python
# Check for sources field (can be empty list or populated)
if "sources:" not in match.group(1):
    errors.append(f"{skill_name}: missing 'sources:' field in frontmatter")
```

Note: The `roblox-luau-mastery` router skill should pass all checks including `sources:`. If it has no external source, use `sources: []`.

### Step 3: Add references/full.md existence check

After the frontmatter checks, add:

```python
# references/full.md check (router skills are exempt)
ref_path = os.path.join(skill_dir, "references", "full.md")
is_router = "router" in fm.get("description", "").lower()
if not is_router and not os.path.exists(ref_path):
    errors.append(f"{skill_name}: missing references/full.md")
```

### Step 4: Add basic cross-reference validation

After all skills are validated, check that any `roblox-<name>` reference in SKILL.md or references/full.md points to a skill that exists:

```python
# Cross-reference validation (in main(), after all_errors is populated)
import re
import os

all_skill_names = set()
for entry in os.listdir(SKILLS_DIR):
    skill_path = os.path.join(SKILLS_DIR, entry)
    if os.path.isdir(skill_path):
        all_skill_names.add(entry)

ref_pattern = re.compile(r'`?(roblox-[a-z]+(?:-[a-z]+)*)`?(?:\s*→|\s*\|)')

for entry in sorted(os.listdir(SKILLS_DIR)):
    skill_dir = os.path.join(SKILLS_DIR, entry)
    if not os.path.isdir(skill_dir):
        continue
    for filepath in [os.path.join(skill_dir, "SKILL.md"),
                     os.path.join(skill_dir, "references", "full.md")]:
        if not os.path.exists(filepath):
            continue
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        for match in ref_pattern.finditer(content):
            ref_name = match.group(1)
            if ref_name not in all_skill_names:
                # Only flag as error if it looks like a skill reference,
                # not a source attribution comment
                line_num = content[:match.start()].count('\n') + 1
                all_errors.append(
                    f"{entry}: references non-existent skill '{ref_name}' "
                    f"at {os.path.basename(filepath)}:{line_num}"
                )
```

**Important**: This regex must NOT match source attribution comments like `<!-- Source: brockmartin/roblox-game-skill (MIT) -->` or URL paths like `github.com/brockmartin/roblox-game-skill`. The pattern `roblox-[a-z]+(?:-[a-z]+)*` followed by `→` or `|` should avoid these, but test carefully.

### Step 5: Update the docstring

Update the module docstring to reflect the new checks:

```python
"""
Validate roblox-brain skills for size and structure compliance.

Checks:
- SKILL.md under 3,000 chars
- Description under 150 chars
- Frontmatter has name, description, last_reviewed, sources
- '## When to Load' section exists
- '## Quick Reference' section exists
- No '## Full Reference' in SKILL.md (should be in references/)
- references/full.md exists (router skills exempt)
- Cross-references to other skills point to existing skills

Exit code 0 = all checks pass, 1 = failures found.
"""
```

### Step 6: Verify

**Verify**:
```
python3 validate_skills.py    → "All checks passed" (assuming Plan 005 is done)
```

If Plan 005 is NOT done yet, the validator will report errors for the missing `## When to Load` sections and missing `sources:` fields. That's correct behavior — it means the validator is working.

## Done criteria

ALL must hold:

- [ ] `python3 validate_skills.py` exits 0 (after Plan 005 standardization is complete)
- [ ] Validator checks for `## When to Load` section
- [ ] Validator checks for `sources:` in frontmatter
- [ ] Validator checks for `references/full.md` existence (with router exemption)
- [ ] Validator checks cross-references point to existing skills
- [ ] No files outside `validate_skills.py` are modified
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:
- The cross-reference regex matches false positives (e.g. matches source attribution comments, URLs, or `roblox-game-skill` which is a GitHub repo name, not a skill name). Test against all existing content before finalizing.
- Adding checks causes the validator to fail on skills that are currently passing (if Plan 005 hasn't been done yet — coordinate ordering).
- The `roblox-luau-mastery` router skill fails the `references/full.md` check (it should be exempt via the `is_router` flag — verify the description contains "router").

## Maintenance notes

- When new skills are added, the validator automatically picks them up via `os.listdir(SKILLS_DIR)`.
- The cross-reference checker is a simple regex — it won't catch every possible reference format, but it catches the `roblox-name →` and `` `roblox-name` `` patterns that are the standard cross-reference syntax.
- If the regex produces false positives, refine the pattern rather than removing the check.
- Update the regex if new cross-reference syntax is adopted (e.g. markdown links to skill files).
