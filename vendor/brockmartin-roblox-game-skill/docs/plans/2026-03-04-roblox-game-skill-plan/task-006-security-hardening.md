# Task 006: Write security-hardening.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/security-hardening.md`

## Description

Write a comprehensive security reference covering anti-exploit techniques, server-side validation, and secure coding patterns for Roblox games.

## What To Do

1. **Overview** — When to load (building RemoteEvents, handling player input, security reviews)
2. **The Golden Rule** — "Never trust the client" explained with concrete examples of what exploiters can do (modify LocalScripts, fire RemoteEvents with arbitrary data, speed hack, fly hack, teleport)
3. **RemoteEvent Validation Patterns** — Type checking all arguments, range validation, cooldown enforcement, rate limiting, whitelist validation. Include full Luau code for a secure remote handler
4. **Server-Authoritative Design** — Server owns all game state, client is a display layer. Patterns for: movement validation, damage validation, currency transactions, inventory operations
5. **Common Exploit Vectors** — Speed hacks (validate position delta), fly hacks (check ground contact), teleport exploits (validate distance), currency manipulation (server-side only), item duplication (session locking), RemoteSpy (minimize remote surface area)
6. **Data Exposure Prevention** — What NOT to put in ReplicatedStorage/StarterPlayer, hiding server logic, minimizing data sent to client
7. **Rate Limiting Patterns** — Per-player cooldown tracking, request throttling, flood detection with Luau implementation
8. **Obfuscation vs Real Security** — Why obfuscation is not security, focus on server-side validation instead
9. **Best Practices** — Validate everything server-side, minimize remote surface area, use sanity checks, log suspicious activity
10. **Anti-Patterns** — Trusting client-reported positions, client-side currency, unvalidated remote arguments, exposing admin remotes

## Verification

- File exists at `references/security-hardening.md`
- "Never trust the client" is prominently featured
- RemoteEvent validation includes complete Luau code
- At least 5 exploit vectors covered with defenses
- Rate limiting pattern includes working Luau implementation
