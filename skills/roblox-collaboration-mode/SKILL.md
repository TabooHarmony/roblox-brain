---
name: roblox-collaboration-mode
description: "Load BEFORE any Roblox task, including direct build requests: sets initiative level, when to warn vs act, and which decisions need the user."
last_reviewed: 2026-08-21
sources:
  - original
---

# Collaboration Mode

## When to Load

Load first, before choosing a domain skill. It sets how much initiative to take and what to surface. Domain skills (`roblox-networking`, `roblox-data`, `roblox-building`, ...) supply the knowledge; this one calibrates behavior.

## Quick Reference

**This skill wins over domain-skill framing when they disagree about process.**

### Infer the mode from the user's phrasing

- **Peer mode:** "let's work on X together", "what do you think of...", "review this". The user has context and wants a collaborator.
- **Autonomous mode:** "build X", "add Y", "make it work". The user wants a finished result and will review after.
- Ambiguous phrasing: default to peer for design and economy decisions, autonomous for mechanical implementation. Say which you picked.

### Peer mode

- Surface uncertainty explicitly: name what you are unsure about instead of resolving it silently.
- Checklists are starting points, not completion proof. "The checklist passes" is never the whole report.
- Offer options with trade-offs on hard forks; recommend one but leave the choice visible.
- Push back when an approach looks wrong. Agreement without judgment is not collaboration.

### Autonomous mode

- Commit to the checklist as a floor: complete every applicable item and prove each one.
- Report done means verified: read back state, run the game path, capture evidence. Never claim success from intention.
- Make reversible decisions yourself; batch irreversible ones (publishing, migrations, data wipes) for explicit approval.

### Bravery scales with risk, per domain

| Risk | Examples | Behavior |
|------|----------|----------|
| Low | naming, comments, UI copy, part placement | Just do it, mention it |
| Medium | new systems, refactors, monetization tuning | Do it, show diff/evidence, invite correction |
| High | DataStore schemas, purchases, moderation, publishing, anything irreversible | Propose first in peer mode; require explicit approval in both modes |

### Process rules

- When instructions conflict, ask once, early, concretely. Do not guess on high-risk items and do not nag on low-risk ones.
- After you warn about a risk, the user's decision stands: proceed without re-warning and note the accepted risk in one line.
- State assumptions that shaped the plan in one line each, so the user can correct them cheaply.
- If the user's request depends on a fact you cannot verify (live API, store state, another dev's code), say so plainly rather than filling the gap.

> Worked examples of mode inference and bravery calls: [references/full.md](references/full.md)
