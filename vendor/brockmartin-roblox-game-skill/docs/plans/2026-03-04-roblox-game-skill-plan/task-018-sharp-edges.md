# Task 018: Write sharp-edges.md

**depends-on:** 001
**phase:** 3 - Specialized References
**files:** `references/sharp-edges.md`

## Description

Write a comprehensive sharp edges reference — severity-rated critical gotchas that every Roblox developer must know. This is the "save you from disaster" file.

## What To Do

Create a severity-rated list of gotchas following the pattern: ID, Severity, Description, Symptoms, Solution, Luau Code Fix.

Include at minimum these sharp edges:

1. **SE-1 (Critical): DataStore Data Loss** — Improper session handling causes data loss when players server-hop quickly. Symptoms: players lose items/currency. Solution: Use ProfileService with session locking.
2. **SE-2 (Critical): Client-Side Currency** — Storing currency on client allows exploiters to set arbitrary values. Symptoms: players have impossible amounts. Solution: All currency server-side only.
3. **SE-3 (Critical): ProcessReceipt Mishandling** — Not returning PurchaseGranted correctly causes Roblox to repeatedly retry or refund. Symptoms: duplicate items or lost purchases. Solution: Grant item THEN return PurchaseGranted.
4. **SE-4 (High): Memory Leaks from Events** — Not disconnecting event connections causes growing memory usage. Symptoms: increasing memory, eventual crash. Solution: Store and disconnect connections.
5. **SE-5 (High): RemoteEvent Flooding** — No rate limiting allows exploiters to spam remotes. Symptoms: server lag, crashes. Solution: Per-player rate limiting.
6. **SE-6 (High): BindToClose Timeout** — Only 30 seconds to save all data on server shutdown. Symptoms: data loss on shutdown. Solution: Use task.spawn for parallel saves.
7. **SE-7 (Medium): Part Count on Mobile** — Too many parts tanks mobile performance. Symptoms: lag, crashes on mobile. Solution: Stay under 10K parts, use StreamingEnabled.
8. **SE-8 (Medium): Yielding in Require** — Module scripts that yield during require block all dependent scripts. Symptoms: game fails to load. Solution: No yields in module body, use init functions.
9. **SE-9 (Medium): Table Length with Gaps** — The `#` operator is unreliable with nil gaps. Symptoms: incorrect counts. Solution: Track length explicitly or use table.move/ipairs.
10. **SE-10 (Low): wait() vs task.wait()** — Deprecated wait() has minimum 0.03s and inconsistent behavior. Solution: Always use task.wait().

Each entry must include: ID, Severity, Description, Symptoms, Solution, and a Luau code example showing the fix.

## Verification

- File exists at `references/sharp-edges.md`
- At least 10 sharp edges documented
- Each has ID, Severity, Description, Symptoms, Solution, Code
- Severity levels: Critical, High, Medium, Low
- Top 3 are DataStore, client trust, and ProcessReceipt issues
