---
name: roblox-networking
description: "Use when validating RemoteEvent or RemoteFunction arguments, adding rate limits, designing server-authoritative systems, or preventing exploits."
last_reviewed: 2026-09-13
sources:
  - https://create.roblox.com/docs/scripting/events/remote
  - https://create.roblox.com/docs/scripting/security/security-tactics
  - https://create.roblox.com/docs/scripting/security/client-server-boundary
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/reference/engine/classes/UnreliableRemoteEvent
  - original
---

# roblox networking

## When to Load

Load when adding a remote, handling untrusted input, implementing cooldowns, or deciding which side owns a result.

## Quick Reference

- Treat every client argument as attacker-controlled input.
- Validate type, size, ownership, state, distance, and cooldown on the server.
- Look up prices, damage, rewards, and permissions from server-owned definitions.
- Choose the authority model before designing movement or continuous simulation: Server Authority uses client prediction and server rollback, and is not `SetNetworkOwner`.
- For simulation input under Server Authority use `InputAction`/`InputContext` with `RunService:BindToSimulation()`, not a `RemoteEvent`.
- Use events for most gameplay requests. Keep `RemoteFunction` calls short and bounded.
- Use `RemoteEvent` for reliable state changes. It is not ordered relative to property or attribute replication: use one explicit state channel or version the state when ordering matters. Reserve `UnreliableRemoteEvent` for replaceable data such as VFX and snapshots.
- Unreliable is not automatically faster: delivery is unordered, packets may be dropped, and payloads should stay at or below the documented 1000-byte limit.
- Measure payload size and fire rate under load; community packet-size estimators are not an official wire-format spec.
- Check numbers for NaN and infinity (`x ~= x`, `math.abs(x) == math.huge`) before range checks: `NaN` defeats `<`/`>`. Strings get the same treatment (`utf8.len(s)` catches malformed UTF-8 that would fail a DataStore save).
- Serialization decides validation: functions arrive as `nil`, metatables are stripped, mixed-key tables are mangled, `nil` in a table truncates the payload, and tables are copies, not references. Validate field by field; share state via server-owned snapshots or ids.
- Server Authority needs `Workspace.AuthorityMode = Server` plus the full bundle: NextGenerationReplication, PlayerScriptsUseInputActionSystem, deferred SignalBehavior, UseFixedSimulation, StreamingEnabled. Misprediction and rollback are normal (debug surface in full.md).
- Rate limits protect the server; validation still has to reject invalid requests.
- Record suspicious behavior with thresholds; never punish a player for one malformed packet.

**Need the details?** Load `references/full.md` for reusable validation and throttling patterns.
