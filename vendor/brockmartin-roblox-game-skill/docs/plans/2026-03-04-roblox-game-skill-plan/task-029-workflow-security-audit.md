# Task 029: Write security-audit.md Workflow

**depends-on:** 001
**phase:** 5 - Workflows
**files:** `workflows/security-audit.md`

## Description

Write the security review workflow.

## What To Do

1. **Step 1: Remote Surface Scan** — MCP: search for all RemoteEvent/RemoteFunction instances. Offline: Ask user to list all remotes
2. **Step 2: Validation Check** — For each remote, verify: argument type checking, range validation, cooldown enforcement, authorization check
3. **Step 3: Client Trust Audit** — Search for client-side logic that should be server-side: currency operations, inventory changes, damage calculation, position setting
4. **Step 4: Data Exposure Check** — Verify no sensitive data in ReplicatedStorage, StarterPlayer, or sent to client via remotes
5. **Step 5: Rate Limiting Check** — Verify all remotes have per-player rate limiting
6. **Step 6: Vulnerability Report** — Categorize findings: Critical (exploitable for advantage) → High (data exposure) → Medium (potential abuse) → Low (best practice)
7. **Step 7: Hardening** — MCP: apply hardened code. Offline: provide fixed code
8. **Step 8: Re-verify** — Confirm all vulnerabilities addressed

## Verification

- File exists at `workflows/security-audit.md`
- Covers remotes, client trust, data exposure, rate limiting
- Prioritized vulnerability format
- Produces actionable fixes not just findings
