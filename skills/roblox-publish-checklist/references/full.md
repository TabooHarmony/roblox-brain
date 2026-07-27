# Roblox Publish Checklist: Full Reference

This is a release gate, not a list of universal architecture rules. A gate is a check that can block publication. Define applicability first, then collect evidence.

## 1. Freeze the payload

Record:

- target experience, universe, and places;
- changed scripts, assets, configuration, schemas, products, and permissions;
- supported device and input matrix;
- expected player/data compatibility;
- rollback or forward-fix procedure.

Test the exact payload intended for publication. A passing local file that is not in the published place is irrelevant.

## 2. Classify gates before running them

Use four states:

- **Required:** the release touches this risk or the experience depends on it.
- **Conditional:** run when the named feature exists.
- **Not applicable:** feature is absent, with a reason.
- **Unverified:** required evidence could not be collected.

Do not convert Not Applicable or Unverified into PASS. Do not calculate a readiness percentage that can hide one data-loss or purchase blocker.

## 3. High-consequence gates

### Persistence, conditional on stored state

Load `roblox-data` for player profiles and `roblox-server-data` for shared or cross-server state. Verify the actual storage abstraction used by the project.

- Existing data loads without being replaced by defaults.
- Schema migrations are deterministic and safe to retry.
- A failed session acquisition does not create a new empty profile.
- Duplicate joins, teleport overlap, crashes, and stale ownership follow the documented policy.
- Disconnect and shutdown paths preserve the library's release/save contract.
- Parallel writes cannot overwrite newer state.
- A failed save is observable and does not produce a false success.

### Trust boundaries, conditional on client requests or authority changes

Load `roblox-networking` and `roblox-security`.

- Inventory the changed remotes and their direction, payload, caller, and side effects.
- Validate type, finite numbers, bounds, state, ownership, permissions, and replay semantics as appropriate to each action.
- Use abuse controls based on action cost and semantics. Do not require one arbitrary rate limit for every remote.
- Keep currency, inventory, rewards, permissions, and purchase outcomes server-owned.
- Test malformed, stale, repeated, unauthorized, and high-frequency requests.
- For Server Authority projects, verify its required Studio settings and simulation path. Do not apply classic CFrame correction blindly.

### Monetization, conditional on paid products or entitlements

Load `roblox-monetization`.

- Developer Product grants are durable and idempotent by purchase ID.
- `ProcessReceipt` returns `PurchaseGranted` only after durable success.
- Retry, server handoff, player absence, and already-granted receipt cases are tested.
- Pass and subscription entitlements are checked on the server and refreshed after purchase when needed.
- Prompt completion events are not treated as proof of payment.
- Product IDs, amounts, and ownership come from trusted configuration.

### Cloud and webhooks, conditional on external integration

Load `roblox-cloud`.

- No key, secret, authorization code, access token, or refresh token appears in replicated content, URLs, client bundles, analytics, or ordinary logs.
- API-key permissions or OAuth scopes and resource grants are minimal and current.
- OAuth state, PKCE, redirect URL, token rotation, and revocation behavior are tested when applicable.
- Webhook verification runs before side effects; repeat delivery is safely deduplicated.
- Retries are bounded and limited to safe transient failures.

Any unresolved failure in these four groups is a release blocker.

## 4. Runtime and gameplay gates

Choose specimens from the changed surface. At minimum include:

1. normal completion;
2. invalid or denied action;
3. retry or repeat action;
4. leave/rejoin or reconnect when state is involved;
5. rapid input or concurrency when the flow can overlap.

For multiplayer changes, test at the actual participant count needed to exercise ownership, replication, team, trade, or matchmaking behavior. A solo playtest is not proof of multiplayer correctness.

Capture runtime errors and warnings. Verify cleanup after players, characters, rounds, UI screens, and temporary instances are destroyed or replaced.

## 5. Performance gates

Load `roblox-performance` when the release changes hot loops, physics, rendering, networking, streaming, UI density, or asset load.

- Capture a before and after measurement on representative device tiers.
- Inspect frame time, script hot spots, memory trend, network traffic, and load/streaming behavior relevant to the change.
- Investigate sustained regressions and growth, not generic part, texture, particle, or millisecond commandments.
- Test a realistic session and population. A short empty-place profile is not enough.

Record the tested device, viewport, graphics level, player count, place, and scenario with each result.

## 6. Input, UI, accessibility, and localization

Run only supported combinations, but state the support matrix explicitly.

- Keyboard/mouse, touch, and gamepad paths can reach every required action.
- Focus order, selected state, activation, back/close behavior, and modal boundaries work without a mouse.
- Representative small and large viewports have no clipping, overlap, hidden actions, or unsafe-inset collisions.
- State is not communicated by color alone. Text and controls remain readable over the game view.
- Reduced-motion behavior does not depend on animation to convey state.
- Localized strings fit representative long locales; missing keys and fallback behavior are visible.
- Audio-dependent information has a non-audio route where required.

Load `roblox-input`, `roblox-gui`, `roblox-ui-design`, and `roblox-localization` for the relevant surfaces.

## 7. Creator Dashboard and publication configuration

Inspect the current dashboard rather than copying old dimensions or policy rules from this checklist.

- Correct owner, experience, start place, and place versions are selected.
- Visibility and access settings match the release intent.
- Supported devices, server size, permissions, and private-server settings are intentional.
- Experience questionnaire, content maturity, privacy, and policy declarations are complete and truthful.
- Name, description, icon, thumbnails, genre, and localization reflect the shipped experience.
- Paid items and prices point at the intended experience and products.
- Any required API services, secrets, webhooks, Open Cloud scopes, or external endpoints are configured for production rather than a test environment.

Dashboard UI and policy can change. Use the linked current Creator Hub pages as authority.

## 8. Evidence contract

A PASS must cite one or more of:

- test name and result;
- playtest scenario and runtime log;
- Studio or MCP inspection/readback;
- profiler capture with scenario metadata;
- screenshot or video for visual/input claims;
- dashboard inspection with the relevant setting;
- durable-state readback for data or purchase claims.

A clean console does not prove data integrity, visual quality, accessibility, or purchase idempotency. A screenshot does not prove runtime behavior.

## 9. Final report

Use this structure:

1. **Verdict:** READY, NOT READY, or READY WITH ACCEPTED RISK.
2. **Payload:** exact experience/places and change scope.
3. **Blockers:** failed required high-consequence gates.
4. **Warnings:** nonblocking regressions or debt.
5. **Unverified:** required checks lacking evidence.
6. **Evidence:** pass results grouped by gate.
7. **Not applicable:** skipped gates with reasons.
8. **Rollback:** owner, trigger, and procedure.

`READY WITH ACCEPTED RISK` requires a named risk, impact, owner, and rollback or mitigation. It is not a softer spelling of NOT READY.
