# AGENTS.md — Guide for AI Agents and Contributors

## What This Repo Is

`roblox-brain` is a skills-only repository for AI coding agents working with Roblox Studio. 30 curated skills covering Luau language, Roblox engine APIs, architecture, security, monetization, localization, and workflow. Distributed via `npx skills add TabooHarmony/roblox-brain`.

No plugin code. No build system. No npm package. Just SKILL.md files.

## Architecture: Progressive Disclosure

Each skill follows a 3-level disclosure pattern. Skills are designed to be loaded in this order — platforms that respect the SKILL.md entry point will load efficiently; others may load all files at once (content is still correct, just less context-efficient).

1. **skill_index.md** (~2,800 tokens) — agent loads this first, knows what's available
2. **SKILL.md** (~600 tokens, max 3,000 chars) — quick reference, enough for most tasks
3. **references/full.md** (up to ~10,000 tokens, max 35,000 chars) — complete reference with code examples, API tables

```
skills/roblox-gui/
├── SKILL.md              ← Quick Reference (under 3,000 chars)
└── references/
    └── full.md           ← Full Reference (under 35,000 chars)
```

## Skill File Structure

Every SKILL.md must have:

```yaml
---
name: roblox-<name>
description: >
  One-line description, under 150 chars.
last_reviewed: YYYY-MM-DD
sources:
  - https://create.roblox.com/docs/...    # or [original] for synthesis
---

# Skill Title

## When to Load

1-3 sentences on when an agent should load this skill. Include cross-refs to related skills in backticks.

## Quick Reference

Dense table or list format. The most useful info inline. Code examples in ```luau blocks.

> Full code examples and API tables: [references/full.md](references/full.md)
```

**Required sections**: `## When to Load`, `## Quick Reference`
**Banned sections**: `## Overview`, `## 1. Overview`, `## Full Reference` (use references/full.md)

## Adding a New Skill

1. Create `skills/roblox-<name>/SKILL.md` following the structure above
2. Create `skills/roblox-<name>/references/full.md` with complete reference (under 35,000 chars)
3. Add the skill to a category in `generate_index.py` (CATEGORIES dict)
4. Run `python3 generate_index.py` to regenerate `skill_index.md`
5. Add a row to `README.md` in the appropriate skills table, update the skill count badge
6. Run `python3 validate_skills.py` — must pass
7. If the skill makes API claims, add entries to `api_drift_registry.yaml`

## Validation

Run `python3 validate_skills.py` before committing. Checks:
- SKILL.md under 3,000 chars
- references/full.md under 35,000 chars
- Description under 150 chars
- Required frontmatter: name, description, last_reviewed, sources
- sources field is not empty (use `[original]` for synthesis)
- `## When to Load` section present
- `## Quick Reference` section present
- No `## Overview` or `## 1. Overview` in SKILL.md
- No `## Full Reference` in SKILL.md
- No ```lua code blocks (use ```luau)
- references/full.md exists
- Cross-references (`` `roblox-X` `` in backticks) point to existing skills

Additional CI checks:
- `python3 verify_api_drift.py` — API claims against live Roblox creator-docs
- `python3 verify_source_urls.py` — source URLs are reachable
- `python3 verify_version_pins.py` — tool version pins (non-blocking)

CI runs on all branches (`.github/workflows/ci.yml`).

## Sourcing Rules

- All skill content must trace to a real source: official Roblox creator-docs, repositories with a compatible license or explicit reuse permission, or original work
- Training-data-only content is unacceptable. Verify API references against current docs
- Track sources in the `sources:` frontmatter field
- Use `sources: [original]` for synthesis/opinion/design heuristics
- When lifting from external repos, preserve attribution and record the license or reuse terms in the relevant vendor note
- Use `raw.githubusercontent.com` URLs (not `github.com/blob/`) for source links
- Mark temporal claims with event dates: `<!-- temporal: 2026-06 -->`

## Conventions

- Luau code blocks use ```luau (not ```lua)
- API names in backticks: `UserInputService`, `RemoteEvent`
- Cross-skill references in backticks: `` `roblox-networking` ``, `` `roblox-data` ``
- Last reviewed date: update when you verify content against current docs
- Keep SKILL.md lean — if it hits 2,500+ chars, move detail to references/full.md
- Reference code is illustrative — all reference files have a disclaimer at top
- No orphaned reference files — all content goes in `references/full.md`

## Key Files

| File | Purpose |
|------|---------|
| `skills/*/SKILL.md` | Quick reference for each skill |
| `skills/*/references/full.md` | Full reference for each skill |
| `skill_index.md` | Auto-generated index (run `generate_index.py`) |
| `validate_skills.py` | Validation script for skill structure |
| `generate_index.py` | Auto-generates `skill_index.md` from frontmatter |
| `verify_api_drift.py` | API drift checker against live creator-docs |
| `verify_source_urls.py` | Source URL reachability checker |
| `verify_version_pins.py` | Tool version pin monitor (non-blocking) |
| `api_drift_registry.yaml` | Registry of API claims to verify |
| `requirements.txt` | Python dependencies (pyyaml) |
| `vendor/brockmartin-roblox-game-skill/` | Snapshotted source for 8 skills |
| `.github/workflows/ci.yml` | CI: validation + drift + source URLs + install test |

## What NOT to Do

- Don't add plugin code, build systems, or npm packaging (this is skills-only)
- Don't write skills from training data without verifying against current Roblox docs
- Don't break cross-references when renaming or splitting skills
- Don't commit without running `python3 validate_skills.py`
- Don't leave `sources: []` — use `[original]` for synthesis
- Don't use ```lua — use ```luau
- Don't add `## Overview` sections — use `## When to Load` → `## Quick Reference` directly
- Don't create standalone reference files — all content goes in `references/full.md`
- Don't exceed 35,000 chars in reference files
- Don't use `github.com/blob/` URLs — use `raw.githubusercontent.com`
