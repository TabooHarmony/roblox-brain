# Plan 007: Add AGENTS.md for contributors and AI agents

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `test -f AGENTS.md && echo exists || echo missing`
> If AGENTS.md already exists, read it and reconcile rather than overwriting.

## Status

- **Priority**: P3
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: dx
- **Planned at**: commit `e494289`, 2026-06-29

## Why this matters

The repo has no `AGENTS.md` or `CONTRIBUTING.md`. Contributors and AI agents working on this repo have no guide for: the progressive disclosure architecture, the skill structure conventions, how to add a new skill, how validation works, or the sourcing/licensing rules. The README has some of this but it's user-facing, not contributor-facing. An AGENTS.md gives the next agent (or human contributor) the context they need to make good changes.

## Current state

The repo has:
- `README.md` — user-facing install + architecture overview + skill list
- `validate_skills.py` — validation script
- `.github/workflows/ci.yml` — CI pipeline
- `skill_index.md` — the index agents load first
- No `AGENTS.md`, no `CONTRIBUTING.md`

## Commands you will need

| Purpose | Command | Expected on success |
|-----------|--------|---------------------|
| Check exists | `test -f AGENTS.md && echo exists` | "exists" after creation |

## Scope

**In scope** (the only file you should modify):
- `AGENTS.md` (create)

**Out of scope** (do NOT touch):
- `README.md`
- `CONTRIBUTING.md` (if you want one, derive from AGENTS.md later)
- Any skill files
- `validate_skills.py`

## Git workflow

- Branch: `advisor/007-add-agents-md`
- Single commit.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Create AGENTS.md

Create `AGENTS.md` in the repo root with the following content (adapt as needed to match actual repo state):

```markdown
# AGENTS.md — Guide for AI Agents and Contributors

## What This Repo Is

`roblox-brain` is a skills-only repository for AI coding agents working with Roblox Studio. 28 curated skills covering Luau language, Roblox engine APIs, architecture, security, monetization, and workflow. Distributed via `npx skills add TabooHarmony/roblox-brain`.

No plugin code. No build system. No npm package. Just SKILL.md files.

## Architecture: Progressive Disclosure

Each skill follows a 3-level disclosure pattern:

1. **skill_index.md** (~2,800 tokens) — agent loads this first, knows what's available
2. **SKILL.md** (~600 tokens, max 3,000 chars) — quick reference, enough for most tasks
3. **references/full.md** (~5,000-8,000 tokens) — complete reference with code examples, API tables

```
skills/roblox-gui/
├── SKILL.md              ← Quick Reference (under 3,000 chars)
└── references/
    └── full.md           ← Full Reference (loaded on demand)
```

The one exception is `roblox-luau-mastery`, a router skill that redirects to three sub-skills (`roblox-luau-core`, `roblox-luau-types`, `roblox-luau-patterns`). It has no `references/full.md`.

## Skill File Structure

Every SKILL.md must have:

```yaml
---
name: roblox-<name>
description: >
  One-line description, under 150 chars.
last_reviewed: YYYY-MM-DD
sources:
  - https://github.com/... (MIT)   # or "Roblox creator-docs" or []
---

# Skill Title

## When to Load

1-3 sentences on when an agent should load this skill.

## Quick Reference

Dense table or list format. The most useful info inline. Code examples in ```luau blocks.

> Full code examples and API tables: [references/full.md](references/full.md)
```

## Adding a New Skill

1. Create `skills/roblox-<name>/SKILL.md` following the structure above
2. Create `skills/roblox-<name>/references/full.md` with complete reference
3. Add a row to `skill_index.md` in the appropriate section
4. Add a row to `README.md` in the appropriate table, update the skill count
5. Run `python3 validate_skills.py` — must pass
6. If the skill cross-references other skills, verify those skills exist

## Validation

Run `python3 validate_skills.py` before committing. Checks:
- SKILL.md under 3,000 chars
- Description under 150 chars
- Required frontmatter: name, description, last_reviewed, sources
- `## When to Load` section present
- `## Quick Reference` section present
- No `## Full Reference` in SKILL.md
- `references/full.md` exists (router skills exempt)
- Cross-references point to existing skills

CI (`.github/workflows/ci.yml`) runs validation on push and PR, plus an install test on ubuntu and windows.

## Sourcing Rules

- All skill content must trace to a real source: official Roblox creator-docs, MIT/Apache licensed repos, or original work.
- Training-data-only content is unacceptable. Verify API references against current docs.
- Track sources in the `sources:` frontmatter field.
- When lifting from MIT repos, preserve attribution and note the repo URL.

## Conventions

- Luau code blocks use ```luau (not ```lua)
- API names in backticks: \`UserInputService\`, \`RemoteEvent\`
- Cross-skill references: \`roblox-skill-name\` → \`Section Name\`
- Last reviewed date: update when you verify content against current docs
- Keep SKILL.md lean — if it hits 2,500+ chars, move detail to references/full.md

## Key Files

| File | Purpose |
|------|---------|
| `skills/*/SKILL.md` | Quick reference for each skill |
| `skills/*/references/full.md` | Full reference for each skill |
| `skill_index.md` | Compact index of all skills (~2,800 tokens) |
| `validate_skills.py` | Validation script for skill structure |
| `.github/workflows/ci.yml` | CI: validation + install test |
| `README.md` | User-facing documentation |

## What NOT to Do

- Don't add plugin code, build systems, or npm packaging (this is skills-only)
- Don't vendor Roblox libraries (Fusion, RBXUtil) — teach patterns, point to Wally
- Don't write skills from training data without verifying against current Roblox docs
- Don't break cross-references when renaming or splitting skills
- Don't commit without running `python3 validate_skills.py`
```

### Step 2: Verify

**Verify**: `test -f AGENTS.md && echo exists` → "exists"

## Done criteria

ALL must hold:

- [ ] `AGENTS.md` exists in repo root
- [ ] Content covers: architecture, skill structure, adding new skills, validation, sourcing, conventions, key files, what not to do
- [ ] No files outside `AGENTS.md` are modified
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:
- `AGENTS.md` already exists (read it, reconcile, don't overwrite).
- The repo state has changed significantly (different skill count, different validation checks) and the AGENTS.md content would be inaccurate.

## Maintenance notes

- Update AGENTS.md when the skill count changes, validation checks change, or conventions evolve.
- This file is the primary onboarding doc for any AI agent or human contributor working on the repo.
