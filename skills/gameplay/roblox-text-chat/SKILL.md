---
name: roblox-text-chat
description: "Use when adding, customizing or fixing Roblox text chat: TextChatService channels, commands, bubbles, filtering, chat compliance."
when_to_use: "Also when chat commands don't fire, custom chat or radio channels break, bubbles don't show, chat text reads empty, a game got temporary text limits, signs or pet names need filtering, or legacy Chat needs migrating."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/chat/in-experience-text-chat
  - https://create.roblox.com/docs/chat/guidelines
  - https://create.roblox.com/docs/chat/platform-integrated-chat
  - https://create.roblox.com/docs/chat/quick-words
  - https://create.roblox.com/docs/chat/preset-system-guidelines
  - https://create.roblox.com/docs/chat/bubble-chat
  - https://create.roblox.com/docs/chat/cross-server-chat
  - https://create.roblox.com/docs/ui/temporary-limits
  - https://create.roblox.com/docs/reference/engine/classes/TextChatCommand
  - https://create.roblox.com/docs/reference/engine/classes/TextChannelWindow
  - original
---

# Roblox Text Chat

## When to Load

Any player-to-player text: chat windows, channels, commands, bubbles, presets, and editable text others can see (signs, names, boards). Remote validation: `roblox-networking`; abuse paths: `roblox-security`; chat UI placement: `roblox-gui`.

## Quick Reference

- **Chat = a back-and-forth in under 60 s,** and it must use `TextChatService` (radios, phones, DMs, team or admin chat included). Anything else risks takedown or temporary text limits.
- **Editable text others see:** server `TextService:FilterStringAsync` + at most one submission per player per 60 s; comments can't have replies.
- **Channels:** `TextChannel` under `TextChatService`; server `ShouldDeliverCallback` decides who receives. Direct chat: `SetDirectChatRequester`. Gate UI with `CanUserChatAsync`/`CanUsersChatAsync`.
- **Commands:** `TextChatCommand` (`PrimaryAlias`/`SecondaryAlias`, case-insensitive; `TextChatCommandMatchMode` `StartsWith` default). `Triggered` fires on the sender's client and the server: authorize on the server.
- **Callbacks never yield.** `OnIncomingMessage`, `OnBubbleAdded`, `OnChatWindowAdded` are client-only; `ShouldDeliverCallback` server-only.
- **Bubbles:** `BubbleChatConfiguration`; per-bubble via `OnBubbleAdded`; NPCs via client `DisplayBubble`.
- **Platform-integrated chat** <!-- temporal: 2026-11 -->: required for all games from May 2027. Enable in Studio only. Then message text reads `""`, custom UIs use `TextChannelWindow` (one `Target` channel), commands must be `TextChatCommand`, presets go through Quick Words.
- **Quick Words:** Creator Hub, up to 3 categories of 3–10 phrases, under 25 chars, English, auto-translated, reviewed.
- **Legacy `Chat` is deprecated:** set `ChatVersion = TextChatService`; replace `SetExtraData` with attributes + `OnChatWindowAdded`.

> Pipeline, compliance, migration, code: [references/full.md](references/full.md)
