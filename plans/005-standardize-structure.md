# Plan 005: Standardize skill structure across all 28 skills

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

- **Priority**: P2
- **Effort**: M
- **Risk**: LOW
- **Depends on**: 001 (cross-references must be fixed first so structural changes don't conflict)
- **Category**: tech-debt
- **Planned at**: commit `e494289`, 2026-06-29

## Why this matters

The 28 skills are inconsistent in structure. Some have `## When to Load`, some don't. Some have `sources:` in frontmatter, some have HTML comments like `<!-- Source: brockmartin/roblox-game-skill (MIT) -->`, some have nothing. This inconsistency makes it harder for agents to navigate skills predictably and harder for contributors to know the expected format.

## Current state

**Structural inconsistencies found** (verified via grep):

| Skill | Has `## When to Load` | Has `sources:` in frontmatter | Has HTML source comment |
|-------|----------------------|------------------------------|------------------------|
| roblox-analytics | NO | NO | NO |
| roblox-animation-vfx | NO | NO | NO |
| roblox-architecture | NO | NO | YES (`<!-- Source: brockmartin/roblox-game-skill (MIT) -->`) |
| roblox-audio | YES | YES | NO |
| roblox-building | YES | NO | NO |
| roblox-cloud | YES | NO | NO |
| roblox-code-review | YES | NO | NO |
| roblox-data | NO | NO | YES |
| roblox-debug | YES | NO | NO |
| roblox-economy | YES | NO | NO |
| roblox-gui | NO | NO | YES |
| roblox-lighting | NO | YES | NO |
| roblox-luau-core | YES | NO | NO |
| roblox-luau-mastery | NO | NO | NO |
| roblox-luau-patterns | YES | NO | NO |
| roblox-luau-types | YES | NO | NO |
| roblox-monetization | NO | NO | YES |
| roblox-networking | NO | NO | YES |
| roblox-npc-ai | NO | YES | NO |
| roblox-oauth | YES | NO | NO |
| roblox-performance | YES | NO | NO |
| roblox-physics | YES | YES | NO |
| roblox-publish-checklist | YES | NO | NO |
| roblox-security | YES | NO | NO |
| roblox-sharp-edges | YES | NO | NO |
| roblox-studio-mcp | YES | NO | NO |
| roblox-testing | YES | YES | NO |
| roblox-tooling | YES | YES | NO |

**Three source-tracking styles exist**:
1. `sources:` in YAML frontmatter (5 skills: audio, lighting, npc-ai, physics, testing, tooling)
2. HTML comment after frontmatter (6 skills: architecture, data, gui, monetization, networking, sharp-edges)
3. No source tracking (17 skills)

**Target standard**:
- Every SKILL.md has `## When to Load` section
- Every SKILL.md has `sources:` in frontmatter (move HTML comments into frontmatter, preserve the original source attribution)
- Every SKILL.md has `last_reviewed` (already present on all)

## Commands you will need

| Purpose | Command | Expected on success |
|-----------|--------|---------------------|
| Validate  | `python3 validate_skills.py` | "All checks passed" |
| Check When to Load | `for d in skills/*/; do grep -q "## When to Load" "$d/SKILL.md" \|\| echo "MISSING: $(basename $d)"; done` | 0 lines output |
| Check sources | `for d in skills/*/; do fm=$(sed -n '/^---$/,/^---$/p' "$d/SKILL.md"); echo "$fm" \| grep -q "sources:" \|\| echo "MISSING: $(basename $d)"; done` | 0 lines output |

## Scope

**In scope** (modify only these):
- All `skills/*/SKILL.md` files that need structural alignment (22 of 28 need at least one fix)

**Out of scope** (do NOT touch):
- Any `references/full.md` files (unless moving a source comment that's embedded in body text)
- `skill_index.md`
- `README.md`
- `validate_skills.py`

## Git workflow

- Branch: `advisor/005-standardize-structure`
- Commit in batches (e.g. "add When to Load to skills missing it", then "standardize sources to frontmatter").
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Add `## When to Load` to the 10 skills missing it

These skills need a `## When to Load` section added (after the `# Title` heading, before `## Quick Reference`):
- roblox-analytics
- roblox-animation-vfx
- roblox-architecture
- roblox-data
- roblox-gui
- roblox-lighting
- roblox-luau-mastery
- roblox-monetization
- roblox-networking
- roblox-npc-ai

For each, write 1-3 sentences describing when an agent should load this skill. Match the style of existing ones (e.g. `skills/roblox-audio/SKILL.md`):
```markdown
## When to Load

Load when implementing audio playback, spatial/3D sound, background music, sound effects, audio mixing (SoundGroups), or dynamic effects.
```

**Verify**: `for d in skills/*/; do grep -q "## When to Load" "$d/SKILL.md" || echo "MISSING: $(basename $d)"; done` → 0 lines

### Step 2: Standardize source attribution to frontmatter

For the 6 skills with HTML source comments (`<!-- Source: ... -->`), move the attribution into the `sources:` frontmatter field and remove the HTML comment:
- roblox-architecture: `<!-- Source: brockmartin/roblox-game-skill (MIT) -->` → `sources:\n  - https://github.com/brockmartin/roblox-game-skill (MIT)`
- roblox-data: same
- roblox-gui: same
- roblox-monetization: same
- roblox-networking: same
- roblox-sharp-edges: same

For the 17 skills with no source tracking, add a `sources:` field where the source is known. Many were sourced from Roblox creator-docs during the initial build. For skills where the source is genuinely unknown or original, add `sources: []` or omit the field (the validate script doesn't require it — but for consistency, add it where known).

**Verify**: `for d in skills/*/; do fm=$(sed -n '/^---$/,/^---$/p' "$d/SKILL.md"); echo "$fm" | grep -q "sources:" || echo "MISSING: $(basename $d)"; done` → fewer missing than before (0 if all known sources added)

### Step 3: Verify no HTML source comments remain

**Verify**: `grep -rn "<!-- Source:" skills/*/SKILL.md` → 0 matches (all moved to frontmatter)

### Step 4: Final validation

**Verify**:
```
python3 validate_skills.py    → "All checks passed"
for d in skills/*/; do grep -q "## When to Load" "$d/SKILL.md" || echo "MISSING: $(basename $d)"; done  → 0 lines
```

## Done criteria

ALL must hold:

- [ ] Every `skills/*/SKILL.md` has a `## When to Load` section
- [ ] No `skills/*/SKILL.md` has `<!-- Source:` HTML comments (all moved to frontmatter `sources:`)
- [ ] `python3 validate_skills.py` exits 0
- [ ] No `references/full.md` files modified
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:
- Adding `## When to Load` to a skill causes its SKILL.md to exceed 3000 chars (trim the Quick Reference instead).
- A skill's source attribution is ambiguous and you can't determine where it came from (leave `sources: []` and note it).
- The `roblox-luau-mastery` router skill doesn't fit the `## When to Load` pattern cleanly (it's a router — adapt the section to say "Load to route to the correct Luau sub-skill").

## Maintenance notes

- After this plan, `validate_skills.py` should be updated (Plan 006) to enforce `## When to Load` and `sources:` as required fields.
- New skills must include both `## When to Load` and `sources:` in frontmatter.
- The `sources:` field is important for license compliance — always track where content came from.
