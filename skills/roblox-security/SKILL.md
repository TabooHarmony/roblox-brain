---
name: roblox-security
description: Anti-exploit design, server authority, RemoteEvent validation, rate limiting, audit checklist.
last_reviewed: 2026-05-27
---

## When to Load

Load this skill when designing security systems, auditing code for vulnerabilities, or hardening a Roblox game against exploit vectors. Covers movement hacks, remote abuse, economy attacks, DataStore exploits, and server-authority patterns.

## Quick Reference

**Core:** Client is always compromised. Server = only source of truth.

### Vectors & Mitigations

| Vector | Attack | Fix |
|--------|--------|-----|
| Movement | Speed/teleport/fly/noclip | Server velocity+pos checks per Heartbeat |
| Remote | Spam, arg spoof, replay | Rate limiter + validate arg types + idempotency |
| Economy | Dupe, negative qty | Session lock, atomic ops, qty > 0 |
| DataStore | Save spam, session hijack | Server-controlled saves, JobId session lock |
| General | Client trusts values | Server computes ALL game state |

### Key Patterns

```luau
-- Rate limiter
local function checkRate(player, remote): boolean
    local now = os.clock(); local lim = rateLimits[player]
    if not lim then lim = {}; rateLimits[player] = lim end
    if now - (lim[remote] or 0) < 0.1 then return false end
    lim[remote] = now; return true
end

-- Server-authoritative damage (never trust client)
AttackRemote.OnServerEvent:Connect(function(player, targetId)
    local weapon = getEquippedWeapon(player)
    local target = resolveTarget(targetId)
    if not weapon or not target or not isInRange(player, target) then return end
    target.Humanoid:TakeDamage(weapon.BaseDamage * getMultiplier(player))
end)
```

### Audit Checklist

**CRITICAL:** Server-authoritative state · Validate all arg types · Rate limit remotes · Session-lock DataStore · No client currency mutations · ProcessReceipt verification · No sensitive LocalScript logic

**HIGH:** Server-validated movement · BindToClose protection · Atomic trading · Never trust client values

**MEDIUM:** Server cooldowns · Server leaderboards · Anti-AFK rewards · TextService filtering

### Anti-Patterns

Don't: obfuscate client, use `_G` for security, kick without logging, over-validate movement, rely on client anti-cheat

See `references/full.md` for detailed examples.
