---
name: roblox-sharp-edges
description: "Use before shipping or reviewing Roblox code involving player data, remotes, monetization, or memory to catch high-impact production footguns."
last_reviewed: 2026-07-12
sources:
  - https://create.roblox.com/docs/cloud-services/data-stores
  - https://create.roblox.com/docs/scripting/security/security-tactics
  - https://create.roblox.com/docs/production/monetization/developer-products
  - https://create.roblox.com/docs/scripting/scripts
  - original
---

# roblox sharp edges

## When to Load

Load before shipping or reviewing code that handles persistence, remotes, purchases, lifecycle cleanup, or high-volume instances.

## Quick Reference

| Risk | Failure mode | First check |
| --- | --- | --- |
| Shared player data | two servers overwrite one profile | session ownership and release path |
| Remote handlers | client manufactures a reward | validate against server state |
| Receipts | a purchase is acknowledged without a grant | idempotent grant before acknowledgement |
| Connections | old players retain callbacks | disconnect on removal or destroy the owner |
| Shutdown | saves exceed the close window | bounded, observable flush |
| Instances | mobile frame time collapses | profile and stream before adding detail |
| Yields | startup hangs or deadlocks | explicit lifecycle phases and timeouts |
| Tables | length or mutation assumptions break | use explicit counts and constructors |
| Async work | abandoned tasks keep running | cancellation or an owner lifetime |

**Need the details?** Load `references/full.md` for the review checklist and small corrective patterns.
