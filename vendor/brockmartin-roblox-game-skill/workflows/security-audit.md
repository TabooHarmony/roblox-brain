# Security Audit Workflow

A step-by-step guided workflow for auditing and hardening security in a Roblox game project.

---

## Step 1: Remote Surface Scan

Identify every RemoteEvent and RemoteFunction in the project to map the attack surface.

### MCP Full (Rojo/Argon project on disk)

- Use `get_project_structure` to locate all script files.
- Use `grep_scripts` to search for:
  - `RemoteEvent` — all declarations and references.
  - `RemoteFunction` — all declarations and references.
  - `BindableEvent` / `BindableFunction` — internal communication that could be exploited if misplaced.
  - `:FireServer(` — client-to-server calls.
  - `:FireClient(` / `:FireAllClients(` — server-to-client calls.
  - `:InvokeServer(` / `:InvokeClient(` — synchronous remote calls.
- Build a complete remote inventory: name, location, direction (client->server or server->client), and purpose.

### MCP Standard (partial access)

- Use available MCP tools to read script files and search for the patterns above.
- Ask the user to confirm completeness of the inventory.

### Offline (no MCP / in-Studio only)

- Ask the user to:
  - List all RemoteEvents and RemoteFunctions (check ReplicatedStorage, ServerStorage, and any folders).
  - For each remote, describe: what data is sent, who fires it, who listens.
- Review any pasted server-side handler code.

---

## Step 2: Validation Check

For each RemoteEvent/RemoteFunction handler on the server, verify the following defenses are in place.

### 2a. Type Checking

- Every argument received from the client must be type-checked before use.
- Use `typeof()` or explicit `type()` checks.
- Reject the request entirely if any argument fails validation (do not attempt to coerce).

```lua
-- GOOD
RemoteEvent.OnServerEvent:Connect(function(player, itemId, quantity)
    if typeof(itemId) ~= "string" then return end
    if typeof(quantity) ~= "number" then return end
    if quantity ~= math.floor(quantity) then return end -- must be integer
    -- proceed
end)
```

### 2b. Range Validation

- Numeric values must be bounds-checked (e.g., quantity between 1 and 99).
- String values must be length-checked and sanitized.
- Enum-like values must be checked against a whitelist.

### 2c. Cooldowns

- Verify that rate limiting or cooldown logic exists to prevent spam-firing.
- Typical pattern: per-player timestamp table with minimum interval.

```lua
local lastFire = {}
RemoteEvent.OnServerEvent:Connect(function(player, ...)
    local now = tick()
    if lastFire[player] and now - lastFire[player] < 0.5 then return end
    lastFire[player] = now
    -- proceed
end)
```

### 2d. Authorization

- Verify the player is allowed to perform the requested action.
- Examples: Does the player own the item they are trying to equip? Are they in the right game state?
- Never trust the client to report its own permissions.

---

## Step 3: Client Trust Audit

Search for game logic on the client that should only exist on the server.

### Red Flags

- **Currency manipulation**: Any client script that sets or modifies currency/coins/gems values and sends the result to the server.
- **Damage calculation**: Client computing damage and telling the server the result instead of the server computing it.
- **Inventory operations**: Client adding items to its own inventory and syncing to the server.
- **Position/teleport authority**: Client setting its own CFrame and the server trusting it without validation.
- **Purchase completion**: Client telling the server a purchase succeeded without server-side MarketplaceService verification.

### MCP Search Patterns

- `grep_scripts` for: `leaderstats`, `Currency`, `Coins`, `Gems`, `Gold`, `Damage`, `Health` in client scripts (StarterPlayerScripts, StarterGui).
- Look for patterns where client fires a remote with a value it computed rather than an action request.

### Correct Pattern

The client should send **intent** ("I want to buy item X"), and the server should:
1. Validate the request.
2. Check if the player can afford it.
3. Deduct currency.
4. Grant the item.
5. Notify the client of the result.

---

## Step 4: Data Exposure Check

Audit what data is visible or accessible to clients.

1. **ReplicatedStorage contents** — Everything here is visible to all clients. Search for:
   - Admin keys, API tokens, or secrets (should never be here).
   - Server configuration data that reveals game mechanics exploitably (e.g., exact drop rates, spawn timers).
   - ModuleScripts containing server logic that should be in ServerScriptService or ServerStorage.
2. **Remote payloads** — Review what data is sent via `FireClient` / `FireAllClients`:
   - Other players' private data (inventory, currency, stats) should not be broadcast.
   - Internal IDs or keys that could be replayed in forged requests.
3. **Attribute exposure** — Attributes set on replicated instances (Players, Characters, Workspace objects) are visible to all clients. Ensure sensitive values are not stored as attributes.
4. **StringValues / ObjectValues** — Check for value objects under replicated instances containing sensitive data.

---

## Step 5: Rate Limiting Check

Verify that all server-side remote handlers have rate limiting.

### Requirements

- Every `OnServerEvent` / `OnServerInvoke` handler must have a cooldown mechanism.
- Cooldowns should be **per-player** (not global).
- Recommended minimum intervals:
  - Combat actions: 0.1-0.5 seconds.
  - Economy actions (buy/sell): 0.5-1.0 seconds.
  - Chat/social actions: 1.0-3.0 seconds.
  - UI/cosmetic actions: 0.2-0.5 seconds.
- Players who exceed rate limits should be warned or kicked, not just silently ignored (to detect exploit attempts).

### Additional Checks

- **RemoteFunction abuse** — `OnServerInvoke` is synchronous and blocks the calling thread. An exploiter can spam-invoke to exhaust server threads. Prefer RemoteEvents where possible; if RemoteFunctions are used, they must have aggressive rate limiting.
- **Payload size** — Large tables sent via remotes can be used for denial-of-service. Validate table size/depth.

---

## Step 6: Vulnerability Report

Compile findings into a prioritized security report.

### Format

```
## Security Audit Report

### Critical (actively exploitable, immediate fix required)
- [Finding]: [File:Line] — [Description, attack vector, and impact]
  - Fix: [Specific remediation]

### High (exploitable with moderate effort)
- [Finding]: [File:Line] — [Description, attack vector, and impact]
  - Fix: [Specific remediation]

### Medium (defense-in-depth gaps)
- [Finding]: [File:Line] — [Description and impact]
  - Fix: [Specific remediation]

### Low (best practice improvements)
- [Finding]: [File:Line] — [Description]
  - Fix: [Specific remediation]

### Summary
- Total remotes audited: X
- Remotes missing validation: X
- Client-trusted logic found: X
- Data exposure issues: X
- Rate limiting gaps: X
```

### Severity Criteria

- **Critical**: An exploiter can directly manipulate currency, items, stats, or crash the server. No validation on a sensitive remote.
- **High**: An exploiter can gain unfair advantage (speed, damage, duplication) or access other players' data.
- **Medium**: Missing defense-in-depth layers (e.g., cooldowns exist but no type checking, or vice versa).
- **Low**: Best practice gaps that do not currently create an exploit path but weaken the security posture.

---

## Step 7: Apply Hardened Code

For each vulnerability found, provide or apply the fix.

### Fix Categories

1. **Validation wrappers** — Create a reusable validation module:
   ```lua
   -- ServerStorage/Modules/RemoteValidator.lua
   local Validator = {}

   function Validator.validateArgs(args, schema)
       for i, expected in ipairs(schema) do
           local arg = args[i]
           if typeof(arg) ~= expected.type then return false end
           if expected.range and (arg < expected.range[1] or arg > expected.range[2]) then return false end
           if expected.maxLength and typeof(arg) == "string" and #arg > expected.maxLength then return false end
           if expected.whitelist and not table.find(expected.whitelist, arg) then return false end
       end
       return true
   end

   return Validator
   ```

2. **Rate limiting module** — Centralized cooldown management.
3. **Server-authoritative rewrites** — Move any client-trusted logic to the server.
4. **Data relocation** — Move sensitive modules/data from ReplicatedStorage to ServerStorage/ServerScriptService.

Apply fixes directly if MCP write access is available. Otherwise, provide the complete corrected code for each file.

---

## Step 8: Re-Verify

After fixes are applied, re-run the audit to confirm all issues are resolved.

1. Repeat Step 1 (Remote Surface Scan) to confirm no new unprotected remotes were introduced.
2. Repeat Step 2 (Validation Check) on all modified handlers.
3. Confirm all Critical and High findings are resolved.
4. Document any accepted risks (Medium/Low findings intentionally deferred) with justification.

### Final Output

```
## Re-Verification Results

- Findings resolved: X/Y
- Remaining accepted risks: X (with justifications)
- New issues introduced: X (if any)
- Security posture: [Hardened / Improved / Unchanged]
```
