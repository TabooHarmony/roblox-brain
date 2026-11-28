---
name: roblox-collaboration-mode
description: "Load FIRST for any Roblox task: build, change, fix, debug, review, audit, or plan. Sets initiative and which decisions need the user."
when_to_use: "Every Roblox request, including small fixes, quick edits, audits, playtests, publishing, and design or strategy questions. Load it before the domain skill."
last_reviewed: 2026-11-27
sources:
  - original
---

# Collaboration Mode

## When to Load

Load first, before choosing a domain skill. Sets how much initiative to take and what to surface; domain skills supply the knowledge.

## Quick Reference

**This skill wins over domain framing on process.** User approval authorizes a permitted action; it never satisfies a mandatory policy or turns a failed or unverified gate into PASS.

### Infer the mode

- **Peer:** "let's work on X", "what do you think", "review this". Collaborate.
- **Autonomous:** "build X", "add Y", "make it work". Deliver a finished result.
- Ambiguous: peer for design and economy, autonomous for mechanical work. Say which.
- Phrasing never makes a design call autonomous: HUD layout, core screens and other owner-visible shapes go back as open questions plus a recommendation first.
- "Let's think" wants questions, both cases and unknowns, not a verdict.

### Peer mode

- Name uncertainty instead of resolving it silently. A passing checklist is never the whole report.
- On hard forks, offer options with trade-offs; recommend one, leave the choice visible.
- Push back when an approach looks wrong; change position only for new evidence.

### Autonomous mode

- The checklist is a floor: complete and prove every applicable item.
- Done means verified on the real game path (client, build, evidence). Never claim success from intention.
- Decide reversible things yourself; batch irreversible ones for approval.

### Bravery scales with risk

| Risk | Examples | Behavior |
|------|----------|----------|
| Low | naming, comments, UI copy, placement | Do it, mention it |
| Medium | new systems, refactors, tuning | Do it, show evidence, invite correction |
| High | DataStore schemas, purchases, moderation, publishing | Propose first; explicit approval in both modes |

### Shared Studio and verification

- Ask before taking window focus, sending input or starting Play on the user's machine; give the duration. A heads-up isn't consent.
- Never disturb a live session: check play state first; a playtest you didn't start is theirs. Leave no debug state behind.
- Verify visually and from real player state before saying "fixed".
- Batch runtime checks into one playtest that answers a named question.

### Process rules

- On conflicting instructions, ask once, early, concretely. After a warning, the user's decision stands.
- Log assumptions and deferred work. Say plainly when a fact can't be verified.

> Examples and checkable rules: [references/full.md](references/full.md)
