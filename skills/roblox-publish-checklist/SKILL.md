---
name: roblox-publish-checklist
description: "Use before publishing or updating a Roblox experience to run evidence-backed release gates for the surfaces that changed."
last_reviewed: 2026-07-26
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/production/publishing/publish-games-and-places.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/production/publishing/adaptive-design.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/production/publishing/accessibility.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/production/publishing/descriptions.md
---

# Roblox Publish Checklist

## When to Load

Load before publishing a new experience or updating a live one. This is a release router, not a universal coding standard. Test the surfaces that exist and the risks introduced by the change.

## Quick Reference

### 1. Define the release

Record the changed places, scripts, assets, configuration, schemas, products, supported devices, and rollback path. Classify each gate as required, conditional, or not applicable before testing.

### 2. Block on high-consequence failures

- **Persistence changed:** load, save, migration, duplicate-session, disconnect, and shutdown behavior. Load `roblox-data` or `roblox-server-data`.
- **Remotes or authority changed:** validate types, bounds, state, ownership, replay, and abusive frequency. Load `roblox-networking` and `roblox-security`.
- **Purchases changed:** test durable, idempotent receipt grants and retries. Load `roblox-monetization`.
- **Cloud auth or webhooks changed:** verify secrets, scopes, callback state, retries, signatures, and deduplication. Load `roblox-cloud`.

A failed high-consequence gate means NOT READY. Do not average it into a percentage.

### 3. Exercise the shipped surface

- Run one normal flow plus failure, retry, leave/rejoin, and rapid-input cases relevant to the change.
- Test every supported input mode and representative viewport/device tier.
- Inspect runtime errors, memory growth, frame/network hot spots, and streaming behavior from measurements, not fixed object-count rules.
- Verify focus, touch targets, readable contrast, non-color state cues, reduced motion, and localized overflow where applicable.
- Confirm experience metadata, visibility, places, thumbnails/icons, permissions, and policy declarations in the current Creator Dashboard.

### 4. Require evidence

Every PASS cites a test, log, profiler capture, readback, screenshot, or dashboard inspection. If a capability is unavailable, mark UNVERIFIED, not PASS.

### Output

`READY`, `NOT READY`, or `READY WITH ACCEPTED RISK`; blockers first, then warnings, unverified gates, evidence, rollback plan, and skipped gates with reasons.

> Full gate design and conditional matrix: [references/full.md](references/full.md)
