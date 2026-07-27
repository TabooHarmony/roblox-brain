---
name: roblox-code-review
description: "Use when reviewing Roblox or Luau code for security, performance, monetization, data persistence, or architecture risks."
last_reviewed: 2026-07-04
sources: [original]
kind: router
---

# Roblox Code Review

Route a Roblox code review to the right domain skills and produce a structured report. Apply relevant lenses based on what changed, not all every time.

## When to Load

- User asks for code review on Roblox/Luau code
- User asks to audit security, performance, networking, monetization, or data persistence
- User asks about Roblox best practices for remotes, data saving, or code organization

## Quick Reference

### Routing — Load These Skills for Each Lens

| Lens | Load |
|------|------|
| Security audit | `roblox-security` |
| Remote validation | `roblox-networking` |
| Data persistence | `roblox-data` |
| Cross-server state | `roblox-server-data` |
| Monetization | `roblox-monetization` |
| Performance | `roblox-performance` |
| Luau correctness | `roblox-luau-core`, `roblox-luau-types` |
| Architecture | `roblox-architecture` |

### Output Format

1. **READY / NOT READY**
2. Critical blockers (security, data loss, crashes)
3. Warnings (leaks, bottlenecks, deprecated APIs)
4. Unverified risks and unavailable evidence
5. Findings with specific fixes

Severity: Critical / High / Medium / Low. For each finding: file + line, what's wrong, impact, and the smallest correct fix. The routed domain skill owns detailed checks.
