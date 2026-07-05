---
name: roblox-code-review
description: "Code review with security, performance, and monetization lenses for Roblox projects"
last_reviewed: 2026-07-04
sources: [original]
---

# Code Review

Review Roblox projects with security, performance, and monetization lenses. Apply relevant lenses based on what changed — not all every time.

## When to Load

- User asks for code review on Roblox/Luau code
- User asks to audit security, performance, networking, monetization, or data persistence
- User asks about Roblox best practices for remotes, data saving, or code organization

## Quick Reference

### 8-Step Review
1. **Project Scan** — scripts, folders, naming, Rojo/Wally/Studio
2. **Organization** — correct services, PascalCase modules, no orphans
3. **Code Quality** — `wait()`→`task.wait()`, `spawn()`→`task.spawn()`, globals
4. **Architecture** — single responsibility, no circular requires, server/client split
5. **Security** — validate remotes server-side, no client-trusted state, rate-limit
6. **Performance** — consolidate Heartbeat, cache services, disconnect events
7. **Report** — Grade A-F. Severity: Critical/High/Medium/Low
8. **Refactor** — Immediate → Short-term → Long-term

### Routing — Load These Skills for Each Lens

| Lens | Load |
|------|------|
| Gotchas & footguns | `roblox-sharp-edges` |
| Security audit | `roblox-security` |
| Remote validation | `roblox-networking` |
| Data persistence | `roblox-data` |
| Monetization | `roblox-monetization` |
| Performance | `roblox-performance` |
| Luau correctness | `roblox-luau-core`, `roblox-luau-types` |

### Output Format
1. READY / NOT READY
2. Critical blockers
3. Warnings
4. Pass count/%
5. Failed items + fixes

📖 Full reference: `references/full.md`
