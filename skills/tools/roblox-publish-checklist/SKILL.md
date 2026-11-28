---
name: roblox-publish-checklist
description: "Use before publishing or updating a Roblox experience to run evidence-backed release gates and a pre-release audit."
when_to_use: "Also when asked to ship, release, push an update, restart servers, or check whether a build is ready, safe or tested enough."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/production/publishing/publish-games-and-places
  - https://create.roblox.com/docs/production/promotion/content-ratings
  - https://create.roblox.com/docs/production/publishing/ip-guidelines
  - https://create.roblox.com/docs/production/publishing/accessibility
  - original
  - https://create.roblox.com/docs/reference/engine/classes/DataModel
---

# Roblox Publish Checklist

## When to Load

Load before publishing or updating a live experience. Test the surfaces and risks the change introduces.

## Quick Reference

### 1. Define the release

Record the changed places, scripts, assets, configuration, schemas, products, supported devices, and rollback path. Classify each gate as required, conditional, or not applicable before testing.

### 2. Block on high-consequence failures

- **Persistence changed:** load, save, migration, duplicate-session, disconnect, and shutdown behavior. Load `roblox-data` or `roblox-server-data`.
- **Remotes or authority changed:** validate types, bounds, state, ownership, replay, and abusive frequency. Load `roblox-networking` and `roblox-security`.
- **Purchases changed:** test durable, idempotent receipt grants and retries. Load `roblox-monetization`.
- **Cloud auth or webhooks changed:** verify secrets, scopes, callback state, retries, signatures, and deduplication. Load `roblox-cloud`.

A failed high-consequence gate means NOT READY. Do not average it into a percentage. Precedence: user approval authorizes an otherwise permitted action; it does not satisfy a mandatory policy and does not turn a failed or unverified gate into PASS.

- **Content and live build:** answer the Content Ratings questionnaire accurately, strip real-world brands from text, and prove the serving build matches the commit (build stamp, no stale Studio window). full.md §7a–7b.

### 3. Exercise the shipped surface

- Run one normal flow plus failure, retry, leave/rejoin, and rapid-input cases relevant to the change.
- Test every supported input mode and representative viewport/device tier.
- Measure errors, memory, frame/network cost and streaming.
- Verify focus, touch targets, readable contrast, non-color state cues, reduced motion, and localized overflow where applicable.
- Confirm Dashboard metadata, permissions and policy; after publishing, verify the version actually serving players.

### 4. Require evidence

Every PASS cites a test, log, profiler capture, readback, screenshot, or dashboard inspection. UNVERIFIED if unavailable; approval is not evidence.

### Output

`READY`, `NOT READY`, or `READY WITH ACCEPTED RISK`; blockers first, then warnings, unverified gates, evidence, rollback plan, and skipped gates with reasons.

> Details: [references/full.md](references/full.md)
