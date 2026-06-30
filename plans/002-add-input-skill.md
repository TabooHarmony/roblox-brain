# Plan 002: Add roblox-input skill (UserInputService, ContextActionService, gamepad/touch)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat e494289..HEAD -- skills/ skill_index.md README.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW
- **Depends on**: none
- **Category**: direction
- **Planned at**: commit `e494289`, 2026-06-29

## Why this matters

Input handling is a core skill every Roblox developer needs in their first week, and the repo has no skill for it. `UserInputService`, `ContextActionService`, gamepad, touch, and keyboard input are mentioned in passing in `roblox-architecture` (2 lines) and `roblox-gui` (tangentially), but there's no actionable reference. An agent asked "how do I handle gamepad input?" or "how do I detect touch on mobile?" has nothing to load.

## Current state

The repo follows a progressive disclosure pattern. Each skill has:

```
skills/roblox-input/
├── SKILL.md              (~600-800 tokens, under 3000 chars)
└── references/
    └── full.md           (~5000-8000 tokens, complete reference)
```

**SKILL.md frontmatter pattern** (from `skills/roblox-audio/SKILL.md`):
```yaml
---
name: roblox-input
description: >
  UserInputService, ContextActionService, keyboard, gamepad, touch input,
  cross-platform input binding, input state tracking.
last_reviewed: 2026-06-29
sources:
  - https://github.com/Roblox/creator-docs (input categories)
---
```

**SKILL.md body pattern** (from `skills/roblox-audio/SKILL.md`):
- `## When to Load` — one sentence on when to use this skill
- `## Quick Reference` — dense table/list format, the most useful info inline
- Hand-off line at the bottom: `> Full tool descriptions, code examples, and setup instructions: [references/full.md](references/full.md)`

**Reference file pattern** (from `skills/roblox-audio/references/full.md`):
- Starts with `# Roblox Input — Full Reference`
- `## Available Tools` style sections with API tables
- Code examples in ```luau blocks
- Pitfalls section at the end

**Existing cross-references to update**: `skills/roblox-architecture/references/full.md` mentions "Input handling systems" and "InputManager.client.lua" but doesn't point to a skill. After this skill exists, add a pointer.

**skill_index.md** needs a new row in the "Building & UI" section.

**README.md** needs the new skill added to the skills table and the count updated from 28 to 29.

## Commands you will need

| Purpose | Command | Expected on success |
|-----------|--------|---------------------|
| Validate  | `python3 validate_skills.py` | "Validated 29 skills" + "All checks passed" |
| Check size| `wc -c skills/roblox-input/SKILL.md` | under 3000 |
| Check ref | `test -f skills/roblox-input/references/full.md && echo exists` | "exists" |

## Scope

**In scope** (the only files you should create/modify):
- `skills/roblox-input/SKILL.md` (create)
- `skills/roblox-input/references/full.md` (create)
- `skill_index.md` (add row)
- `README.md` (add row, update count 28→29)

**Out of scope** (do NOT touch):
- Any other skill files
- `validate_skills.py`
- CI config

## Git workflow

- Branch: `advisor/002-add-input-skill`
- Commit per logical unit (skill files, then index/readme updates).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Create SKILL.md

Create `skills/roblox-input/SKILL.md` with:
- Frontmatter: name, description (under 150 chars), last_reviewed, sources
- `## When to Load` section
- `## Quick Reference` section covering:
  - **UserInputService**: `InputBegan`, `InputChanged`, `InputEnded` events. `UserInputState`, `InputObjectType` (Keyboard, MouseButton, Touch, Gamepad). `GetGamepadState`, `GetMouseLocation`, `TouchEnabled`, `GamepadEnabled`, `KeyboardEnabled` properties for platform detection.
  - **ContextActionService**: `BindAction`, `BindActionAtPriority`, `UnbindAction`. Priority-based binding. Mobile button auto-creation. Use for gamepad+keyboard+touch unified bindings.
  - **Platform detection**: `UserInputService.TouchEnabled`, `UserInputService.GamepadEnabled`, `UserInputService.KeyboardEnabled` — check at startup to adapt UI/controls.
  - **Gamepad**: `GetConnectedGamepads`, `GetGamepadState`, `Enum.KeyCode` gamepad buttons (ButtonA, ButtonB, etc.), thumbstick deadzone.
  - **Touch**: `TouchTap`, `TouchPan`, `TouchPinch`, `TouchRotate` gestures. `UserInputService.TouchEnabled`.
  - **Key patterns**: Always check `gameProcessedEvent` in InputBegan to ignore key presses consumed by UI (chat, text boxes). Debounce input. Distinguish tap vs hold.
  - **Pitfalls**: `gameProcessedEvent` true means UI ate it. Don't hardcode platform assumptions. ContextActionService creates on-screen buttons on mobile automatically. Use `InputBegan` for discrete actions, `InputChanged` for continuous (mouse move, thumbstick).
- Bottom hand-off line: `> Full code examples, API tables, and edge cases: [references/full.md](references/full.md)`

**Verify**: `wc -c skills/roblox-input/SKILL.md` → under 3000. `python3 validate_skills.py` → passes (will need ref file to exist first, so do Step 2 before verifying).

### Step 2: Create references/full.md

Create `skills/roblox-input/references/full.md` with:
- `# Roblox Input — Full Reference`
- `## UserInputService` — full API table: events (InputBegan, InputChanged, InputEnded, TouchTap, TouchPan, TouchPinch, TouchRotate, GamepadConnected, GamepadDisconnected), properties (TouchEnabled, GamepadEnabled, KeyboardEnabled, MouseEnabled, MouseBehavior, MouseDeltaSensitivity), methods (GetGamepadState, GetConnectedGamepads, GetMouseLocation, IsKeyDown)
- `## ContextActionService` — full API: BindAction(name, function, createTouchButton, inputTypes...), BindActionAtPriority, UnbindAction, UnbindAllActions. Priority enum values. Example of binding jump to space + gamepad ButtonA + touch button in one call.
- `## Platform Detection Patterns` — code example: detect platform on startup, store in a module, adapt UI
- `## Gamepad Input` — connected gamepads enumeration, GetGamepadState return shape, thumbstick deadzone pattern, button mapping table
- `## Touch Input` — gesture events (TouchTap, TouchPan, TouchPinch, TouchRotate), when to use each, multitouch patterns
- `## Keyboard Input` — KeyCode enum reference, modifier keys, text input via TextBox vs raw key detection
- `## Mouse Input` — MouseLocation, MouseDelta, MouseBehavior (Default, LockCenter, LockCurrentPosition), raycasting from mouse
- `## Cross-Platform Binding Pattern` — full code example: bind an action to keyboard + gamepad + touch in one ContextActionService call
- `## Pitfalls` — gameProcessedEvent, platform assumptions, debounce, InputChanged spam, disconnect on player leave

**Verify**: `test -f skills/roblox-input/references/full.md && echo exists` → "exists"

### Step 3: Add to skill_index.md

Add a new row in the "Building & UI" section (after roblox-gui):

```markdown
| `roblox-input` | UserInputService, ContextActionService, keyboard, gamepad, touch, cross-platform input binding |
```

**Verify**: `grep "roblox-input" skill_index.md` → 1 match

### Step 4: Update README.md

Update the skill count from 28 to 29 in:
- Line 3: `28 curated skills` → `29 curated skills`
- Line 42: `## Skills (28)` → `## Skills (29)`

Add a new row in the "Building & UI" table (after the roblox-gui row):
```markdown
| `roblox-input` | UserInputService, ContextActionService, keyboard, gamepad, touch, cross-platform input binding |
```

**Verify**: `grep -c "roblox-input" README.md` → at least 1

### Step 5: Final verification

**Verify**:
```
python3 validate_skills.py                 → "Validated 29 skills" + "All checks passed"
wc -c skills/roblox-input/SKILL.md         → under 3000
test -f skills/roblox-input/references/full.md && echo exists  → "exists"
grep "roblox-input" skill_index.md         → 1 match
grep "29 curated" README.md               → 1 match
```

## Done criteria

ALL must hold:

- [ ] `skills/roblox-input/SKILL.md` exists, under 3000 chars, has frontmatter + Quick Reference
- [ ] `skills/roblox-input/references/full.md` exists
- [ ] `python3 validate_skills.py` exits 0 with "Validated 29 skills"
- [ ] `skill_index.md` has a roblox-input row
- [ ] `README.md` says "29 curated skills" and has the new skill in the table
- [ ] No files outside the in-scope list are modified
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:
- Any API name you're writing doesn't match the official Roblox creator docs (verify UserInputService, ContextActionService method names against https://create.roblox.com/docs before writing).
- The SKILL.md exceeds 3000 chars after writing (trim the Quick Reference, move detail to full.md).
- The reference file seems too thin (under 2000 words) — the skill won't be useful without real depth.

## Maintenance notes

- When Roblox adds new input APIs (e.g. VR controllers, new gesture types), update the reference file.
- Cross-reference from `roblox-architecture` input handling section to this skill.
- `roblox-gui` may reference this skill for button input handling.
- Update `last_reviewed` when verifying against current docs.
