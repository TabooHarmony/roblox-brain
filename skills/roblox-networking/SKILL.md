---
name: roblox-networking
description: "Use when validating RemoteEvent or RemoteFunction arguments, adding rate limits, designing server-authoritative systems, or preventing exploits."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/scripting/events/remote
  - https://create.roblox.com/docs/scripting/security/security-tactics
  - https://create.roblox.com/docs/scripting/security/client-server-boundary
  - https://create.roblox.com/docs/reference/engine/classes/UnreliableRemoteEvent
  - https://devforum.roblox.com/t/introducing-unreliableremoteevents/2724155
  - https://devforum.roblox.com/t/remote-packet-size-counter-accurately-measure-the-amount-of-bytes-for-remotes/2320709
  - https://sleitnick.github.io/RbxUtil/api/TypedRemote/
  - original
---

# roblox networking

## When to Load

Load when adding a remote, handling untrusted client input, implementing cooldowns, or deciding which side owns a gameplay result.

## Quick Reference

- Treat every client argument as attacker-controlled input.
- Validate type, size, ownership, state, distance, and cooldown on the server.
- Look up prices, damage, rewards, and permissions from server-owned definitions.
- Use events for most gameplay requests. Keep `RemoteFunction` calls short and bounded.
- Use `RemoteEvent` for reliable ordered state changes. Use `UnreliableRemoteEvent` only for replaceable or ephemeral data such as VFX and continuous snapshots.
- Unreliable does not mean automatically faster: delivery is unordered, packets may be dropped, and payloads should stay at or below the documented 900-byte limit.
- Measure payload size and fire rate under load. Do not treat a community packet-size estimator as an official wire-format specification.
- Validate numeric inputs for NaN and infinity before applying range checks. `NaN` makes ordinary `<` and `>` checks return false.
- Rate limits protect the server, but validation must still reject invalid requests.
- Record suspicious behavior and use thresholds. Do not punish a player for one malformed packet.

**Need the details?** Load `references/full.md` for reusable validation and throttling patterns.
