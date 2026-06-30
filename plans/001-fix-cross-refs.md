# Plan 001: Fix broken cross-references to renamed/non-existent skills

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat e494289..HEAD -- skills/`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: docs
- **Planned at**: commit `e494289`, 2026-06-29

## Why this matters

The repo has two classes of broken cross-references. (1) `roblox-architecture/references/full.md` references "roblox-luau-mastery → OOP Patterns", "→ Anti-Patterns", and "→ Task Library" — but roblox-luau-mastery was split into roblox-luau-core, roblox-luau-types, and roblox-luau-patterns. An agent following these references will load the router skill, find no sections matching those names, and get lost. (2) `roblox-cloud/SKILL.md` line 48 references "roblox-api" as a hand-off target, but no `roblox-api` skill exists. An agent will try to load it and fail.

These are the most impactful issues because cross-references are the navigation system. A broken reference defeats the progressive disclosure design.

## Current state

**File 1**: `skills/roblox-architecture/references/full.md`

Line 446:
```markdown
For metatable-based classes, type annotations, inheritance, and the `.` vs `:` conventions, see **roblox-luau-mastery** → OOP Patterns.
```

Line 800:
```markdown
For polling vs event-driven patterns, see **roblox-luau-mastery** → Anti-Patterns.
```

Line 812:
```markdown
For deprecated `wait()`/`spawn()`/`delay()` vs the `task` library, see **roblox-luau-mastery** → Task Library.
```

**File 2**: `skills/roblox-sharp-edges/references/full.md`

Line 174:
```markdown
**See roblox-luau-mastery → Task Library for full details.**
```

**File 3**: `skills/roblox-cloud/SKILL.md`

Line 48:
```markdown
- Engine API lookup only → `roblox-api`
```

**Correct targets** (verified to exist in roblox-luau-patterns/references/full.md):
- "OOP Patterns" → `## OOP Patterns` exists at line 64 of `skills/roblox-luau-patterns/references/full.md`
- "Anti-Patterns" → `## Anti-Patterns` exists at line 728
- "Task Library" → `### Task Library` exists at line 448

**What "roblox-api" should be**: There is no `roblox-api` skill. The intended hand-off target for "pure engine API lookups" is the `roblox-studio-mcp` skill (which covers runtime tool access) or simply remove the line. The studio-mcp skill already covers API access via `script_search`, `script_grep`, and `execute_luau`. The cleanest fix is to point to `roblox-studio-mcp` since that's the closest match for engine API interaction.

## Commands you will need

| Purpose | Command | Expected on success |
|-----------|--------|---------------------|
| Validate  | `python3 validate_skills.py` | "All checks passed" |
| Check refs| `grep -rn "roblox-luau-mastery →" skills/` | empty (0 matches) |
| Check refs| `grep -rn "roblox-api" skills/` | empty (0 matches) |

## Scope

**In scope** (the only files you should modify):
- `skills/roblox-architecture/references/full.md`
- `skills/roblox-sharp-edges/references/full.md`
- `skills/roblox-cloud/SKILL.md`

**Out of scope** (do NOT touch):
- Any other skills or references
- `skill_index.md` (no broken refs there)
- `README.md`

## Git workflow

- Branch: `advisor/001-fix-cross-refs`
- Commit per file or all together.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Fix roblox-architecture/references/full.md

Replace three references:

1. Line 446: Change `**roblox-luau-mastery** → OOP Patterns` to `**roblox-luau-patterns** → OOP Patterns`
2. Line 800: Change `**roblox-luau-mastery** → Anti-Patterns` to `**roblox-luau-patterns** → Anti-Patterns`
3. Line 812: Change `**roblox-luau-mastery** → Task Library` to `**roblox-luau-patterns** → Task Library`

**Verify**: `grep -n "roblox-luau-mastery" skills/roblox-architecture/references/full.md` → 0 matches

### Step 2: Fix roblox-sharp-edges/references/full.md

Line 174: Change `**See roblox-luau-mastery → Task Library for full details.**` to `**See roblox-luau-patterns → Task Library for full details.**`

**Verify**: `grep -n "roblox-luau-mastery" skills/roblox-sharp-edges/references/full.md` → 0 matches

### Step 3: Fix roblox-cloud/SKILL.md

Line 48: Change `- Engine API lookup only → \`roblox-api\`` to `- Engine API lookup only → \`roblox-studio-mcp\``

**Verify**: `grep -n "roblox-api" skills/roblox-cloud/SKILL.md` → 0 matches

### Step 4: Final verification

Run all checks across the entire repo to confirm zero broken references remain:

**Verify**:
```
grep -rn "roblox-luau-mastery →" skills/    → 0 matches
grep -rn "roblox-api" skills/              → 0 matches (excluding comments like <!-- Source: brockmartin/roblox-game-skill -->)
python3 validate_skills.py                 → "Validated 28 skills" + "All checks passed"
```

## Done criteria

ALL must hold:

- [ ] `grep -rn "roblox-luau-mastery →" skills/` returns 0 matches
- [ ] `grep -rn "roblox-api" skills/` returns 0 matches (excluding source comments)
- [ ] `python3 validate_skills.py` exits 0
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:
- The line numbers in "Current state" don't match the live file (content has drifted).
- You find additional broken cross-references beyond the 4 documented here (report them, don't fix them in this plan).
- A referenced section name ("OOP Patterns", "Anti-Patterns", "Task Library") doesn't exist in `roblox-luau-patterns/references/full.md`.

## Maintenance notes

- When new skills are added or skills are renamed, search for cross-references with `grep -rn "roblox-<old-name>" skills/` and update them.
- The `roblox-luau-mastery` router skill itself is fine — it's the references *to* it using section names that belong to its sub-skills that are broken.
- Future: consider adding a cross-reference validator to `validate_skills.py` (see Plan 006).
