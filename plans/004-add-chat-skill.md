# Plan 004: Add roblox-chat skill (TextChatService, modern chat system)

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

- **Priority**: P2
- **Effort**: M
- **Risk**: LOW
- **Depends on**: none
- **Category**: direction
- **Planned at**: commit `e494289`, 2026-06-29

## Why this matters

Roblox replaced the legacy chat system with `TextChatService` (the "new" TextChat system). The repo has zero coverage of chat systems. An agent asked "how do I send a chat message?" or "how do I create a custom chat command?" has nothing to load. The legacy chat system is deprecated but many games still use it, so the skill should cover both but emphasize TextChatService as the current system.

## Current state

The repo follows a progressive disclosure pattern (same as Plan 002/003).

No existing skill mentions TextChatService. The `roblox-security` skill references `TextService:FilterStringAsync` for chat filtering but doesn't cover the chat system itself.

## Commands you will need

| Purpose | Command | Expected on success |
|-----------|--------|---------------------|
| Validate  | `python3 validate_skills.py` | passes with N+1 skills |
| Check size| `wc -c skills/roblox-chat/SKILL.md` | under 3000 |

## Scope

**In scope** (the only files you should create/modify):
- `skills/roblox-chat/SKILL.md` (create)
- `skills/roblox-chat/references/full.md` (create)
- `skill_index.md` (add row)
- `README.md` (add row, update count)

**Out of scope** (do NOT touch):
- Any other skill files
- `roblox-security` (optionally add a cross-reference to this skill for chat filtering context)

## Git workflow

- Branch: `advisor/004-add-chat-skill`
- Commit per logical unit.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Create SKILL.md

Create `skills/roblox-chat/SKILL.md` with:
- Frontmatter: name, description (under 150 chars), last_reviewed, sources
- `## When to Load`
- `## Quick Reference` covering:
  - **TextChatService (current)**: The modern chat system. Properties: `TextChatService.CanUserChatAsync` (check if user can chat). `TextChatService.MessageReceived` event. `TextChannel` — get/create channels via `TextChatService:CreateTextChannel()`, `TextChatService:GetChannel()`. `TextChannel:DisplaySystemMessage()`, `TextChannel:SendAsync()`.
  - **TextChannel API**: `SendAsync(messageText)` sends a message. `OnIncomingMessage` callback for intercepting/modifying messages. `ShouldBubbleMessage` callback for filtering.
  - **TextChatMessage**: The message object. Properties: `Text`, `TextSource` (who sent), `Timestamp`, `Metadata`, `Priority`. `TextSource` has `UserId`, `DisplayName`, `CanSend`.
  - **Custom chat commands**: Hook `MessageReceived` or `OnIncomingMessage` on a TextChannel. Parse message text, execute command, optionally cancel the message.
  - **Legacy chat (deprecated)**: `ChatService` (server), `Chat` (client). `Players:Chat()`. `Chat:InvokeChatCallback`. Mention this exists for migration context but TextChatService is the current system.
  - **Text filtering**: All user-generated chat text MUST be filtered via `TextService:FilterStringAsync()` or `TextService:FilterStringAsync()` before display. Non-negotiable for compliance.
  - **Bubble chat**: `Chat:Chat(part, message, color)` for speech bubbles over characters. Or use `TextChatService` bubble chat.
  - **Pitfalls**: TextChatService is per-client for some operations. Filtering is mandatory. Don't use legacy `ChatService` for new games. `MessageReceived` fires on client for received messages, `SendAsync` is for sending. Custom commands must check sender permissions server-side.
- Bottom hand-off line

**Verify**: `wc -c skills/roblox-chat/SKILL.md` → under 3000

### Step 2: Create references/full.md

Create `skills/roblox-chat/references/full.md` with:
- `# Roblox Chat — Full Reference`
- `## TextChatService (Current System)` — full API: TextChatService properties and methods, TextChannel full API, TextChatMessage object properties, TextSource object
- `## Creating Custom Channels` — code example: create a team chat channel, send messages
- `## Message Interception` — `OnIncomingMessage` callback, modifying/canceling messages, code example
- `## Custom Chat Commands` — full code example: `!heal` command, `!give` command, permission checking, parsing
- `## Text Filtering` — `TextService:FilterStringAsync()` usage, `GetChatForUserAsync()` for per-user filtered text, code example. MANDATORY for compliance.
- `## Bubble Chat` — `Chat:Chat()` legacy bubble, TextChatService bubble chat configuration
- `## Legacy Chat System (Deprecated)` — ChatService, Chat modules, migration notes from legacy to TextChatService
- `## Chat via MCP` — how to trigger chat via Studio MCP execute_luau in playtest mode
- `## Pitfalls` — filtering mandatory, client vs server boundaries, legacy vs new system mixing, permission checks

**Verify**: `test -f skills/roblox-chat/references/full.md && echo exists` → "exists"

### Step 3: Add to skill_index.md

Add a new row in the "Systems & Networking" section:
```markdown
| `roblox-chat` | TextChatService, TextChannel, custom chat commands, message filtering, bubble chat |
```

### Step 4: Update README.md

Update skill count. Add row in "Systems & Networking" table.

### Step 5: Final verification

**Verify**:
```
python3 validate_skills.py                 → passes
wc -c skills/roblox-chat/SKILL.md          → under 3000
test -f skills/roblox-chat/references/full.md && echo exists  → "exists"
grep "roblox-chat" skill_index.md          → 1 match
```

## Done criteria

ALL must hold:

- [ ] `skills/roblox-chat/SKILL.md` exists, under 3000 chars, has frontmatter + Quick Reference
- [ ] `skills/roblox-chat/references/full.md` exists
- [ ] `python3 validate_skills.py` exits 0
- [ ] `skill_index.md` has a roblox-chat row
- [ ] `README.md` has the new skill in the table and count is updated
- [ ] No files outside the in-scope list are modified
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:
- TextChatService API names don't match current Roblox docs (verify against https://create.roblox.com/docs/reference/engine/classes/TextChatService — this is a newer API that has changed).
- The TextChatService API has been updated since May 2026 and method names differ from what the plan describes.
- The SKILL.md exceeds 3000 chars.

## Maintenance notes

- TextChatService is relatively new and may have API changes. Check `last_reviewed` against Roblox release notes.
- Cross-reference from `roblox-security` chat filtering checklist to this skill.
- `roblox-npc-ai` may reference this for NPC chat behavior.
