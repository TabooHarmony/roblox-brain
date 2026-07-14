# /code-review - Code Quality Review


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

You are performing a code quality review on a Roblox project. Follow these 8 steps. Apply the relevant lens based on what changed. Don't apply all lenses every time.

---

## Quick Reference

**Load lenses below only when code matching that domain changed. Don't apply all lenses every time.**

Key rules:
- **Remote types:** RemoteEvent (fire-and-forget), UnreliableRemoteEvent (loss-tolerant VFX/position), RemoteFunction (request-response, use sparingly), BindableEvent/BindableFunction (intra-client/server internal, never cross-boundary).
- **Data persistence:** ALWAYS ProfileStore for player state. Never raw DataStore. Schema template with defaults, DataVersion, migration functions, session locking, BindToClose.
- **Security:** Validate every remote parameter server-side. Rate-limit all remotes per-player.
- **Performance:** Consolidate Heartbeat loops. Cache services. Disconnect unused events.

---

## Step 1: Project Scan

Read the project directory structure. Survey script count, naming patterns, and organization.

Record:
- Total script count
- Folder organization
- Module naming patterns
- Whether the project uses Rojo/Wally or in-Studio editing

---

## Step 2: Organization Review

Check:
- Scripts in correct locations (ServerScriptService, StarterPlayerScripts, etc.)
- Proper use of services vs standalone scripts
- Clean folder structure (no orphaned scripts, no nesting > 3 levels deep)
- Module naming conventions consistent (PascalCase for ModuleScripts, camelCase for functions)
- No scripts with duplicate or overlapping responsibilities

---

## Step 3: Code Quality Scan

Search for anti-patterns:

```
Deprecated APIs:
- wait( → replace with task.wait()
- spawn( → replace with task.spawn()
- delay( → replace with task.delay()

Code smells:
- Global variables (should be module-scoped)
- Missing type annotations on public functions
- Instance.new() in client scripts (should be server-created)
- while true without task.wait() (unbounded loops)
```

Check for:
- Deprecated APIs (`wait()`, `spawn()`, `delay()`)
- Global variable usage (should be module-scoped)
- Missing type annotations on public functions
- Inconsistent naming conventions
- Dead code / unreachable code
- Duplicate code across scripts
- Overly long functions (>100 lines, should be refactored)

---

## Step 4: Architecture Review

Check:
- Module boundaries - Does each module have a single responsibility?
- Dependency direction - Do modules depend on abstractions, not concrete implementations?
- Circular requires - Any modules that depend on each other?
- Separation of concerns - Server vs Client logic properly separated
- Framework usage - If using a framework, is it used consistently?
- Configuration - Hardcoded values should be in config modules

---

## Step 5: Security Quick-Check

Quick scan for:
- Unvalidated RemoteEvent handlers (server-side)
- Client-trusted logic (currency, inventory, damage, position)
- Sensitive data in ReplicatedStorage or StarterPlayer
- Missing rate limiting on remotes
- ProcessReceipt implementation correctness

> **For a deep security review, run the Security Lens below.**

---

## Step 6: Performance Quick-Check

Quick scan for:
- `wait()` or `spawn()` in tight loops
- Multiple `RunService.Heartbeat:Connect()` in same script
- Large tables without cleanup
- Undisconnected events (memory leaks)
- Unanchored parts without collision groups
- Excessive RemoteEvent usage

> **For a deep performance review, run the Performance Lens below.**

---

## Step 7: Quality Report

Rate overall quality:

- **A** - Production-ready. Clean, organized, secure, performant
- **B** - Solid with minor issues. Safe to ship with minor cleanup
- **C** - Functional but needs work. Ship with caveats
- **D** - Significant issues. Needs refactoring before ship
- **F** - Critical problems. Do not ship in current state

List findings by severity:
- **Critical** - Security vulnerabilities, data loss risk, crashes
- **High** - Memory leaks, performance bottlenecks, broken features
- **Medium** - Code smells, deprecated APIs, poor organization
- **Low** - Style inconsistencies, missing documentation

For each finding, provide:
1. File and line (or function name)
2. What's wrong
3. The specific fix (code)

---

## Step 8: Refactoring Suggestions

If significant issues found, suggest refactoring priorities:

1. **Immediate** - Must fix before next publish
2. **Short-term** - Fix in the next development cycle
3. **Long-term** - Plan for when the project grows

For each suggestion:
- What to change
- Why it matters
- Estimated effort (small/medium/large)

---

# Specialized Review Lenses

The dedicated skills own detailed domain checks. Load only the relevant skill instead of applying every lens to every review.

| Concern | Canonical skill | Review focus |
|---------|-----------------|--------------|
| Footguns and production preflight | `roblox-sharp-edges` | High-impact data, remotes, monetization, and lifecycle mistakes |
| Security and exploit resistance | `roblox-security` | Server authority, trust boundaries, abuse cases, and hardening |
| Remote implementation | `roblox-networking` | Argument validation, rate limits, remotes, and network ownership |
| Player persistence | `roblox-data` | Profile lifecycle, schemas, migrations, and save safety |
| Shared and cross-server state | `roblox-server-data` | OrderedDataStore, MessagingService, and GlobalDataStore |
| Monetization | `roblox-monetization` | Receipts, products, policy, and reconciliation |
| Performance | `roblox-performance` | CPU, memory, network, mobile, and profiling evidence |
| Luau correctness | `roblox-luau-core`, `roblox-luau-types` | Runtime behavior, annotations, narrowing, and type contracts |

## Lens Prompts

### Security

Map the remote surface, identify client-trusted state, check server-side validation and authorization, then route implementation findings to `roblox-networking`.

### Performance

Locate hot paths, repeated work, event leaks, excessive instance or network churn, and mobile-specific risks. Prefer profiler or measurement evidence over fixed thresholds.

### Monetization

Check receipt idempotency, grant-before-acknowledge behavior, server authority, policy-sensitive flows, and reconciliation after retries or reconnects.

### Persistence

Check profile acquisition and release, session conflicts, schema defaults, migrations, shutdown behavior, and validation before writes. Use `roblox-server-data` for non-player state.

### Networking

Enumerate remotes, classify direction and payloads, validate types/ranges/ownership, add abuse controls, and avoid unnecessary client-to-server `RemoteFunction` calls.

## Review Handoff

Use this file for project scan, quality grading, severity ordering, and the final report. Use the canonical domain skill for detailed rules and examples. Do not duplicate a domain checklist here when that skill already owns it.
