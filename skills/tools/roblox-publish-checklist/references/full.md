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

### Policy precedence

User approval authorizes an otherwise permitted action; it does not satisfy a mandatory policy and does not turn a failed or unverified gate into PASS. A mandatory platform policy (for example, paid-random-item restrictions) is not risk-acceptable: "I accept the risk; ship unchanged" maps to NOT READY, not to READY WITH ACCEPTED RISK. READY WITH ACCEPTED RISK exists for non-policy risks (named risk, impact, owner, rollback); approval is never evidence and never upgrades UNVERIFIED or FAILED to PASS.

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

Load `roblox-input`, `roblox-gui`, and `roblox-localization` for the relevant surfaces.

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

## 7a. Content ratings, IP, and data requests (official)

<!-- temporal: 2026-11 -->

**Content ratings.** Content maturity labels are now **Content Ratings**: an IARC rating (shown in some regions) plus a Roblox rating, generated from the Content Ratings Questionnaire.

- A game without content ratings has restricted playability for all players.
- A game with no restricted content starts at 16+ after the age-restricted question. Once it meets the Kids and Select requirements, Roblox reviewers assign IARC ratings for you to review and accept.
- Minimal or Mild ratings are required for Kids (5–8) and Select (9–15) eligibility (`roblox-growth-design`).
- The questionnaire covers violence, gambling depictions, media sharing, AI interaction, cross-experience content, social hangouts, free-form creation, and continuous feeds.
- Inaccurate answers expose the game and account to moderation, and moderation checks for discrepancies.
- Before launch, map innocuous-seeming mechanics to categories. Chasing or hitting can count as violence.

**Intellectual property.**

| Notice | Where to send it | Notes |
|---|---|---|
| DMCA copyright | `copyright_agent@roblox.com` | Counter notices: restoration in about 14 business days |
| Trademark | `trademark_agent@roblox.com` | |
| EU Digital Services Act IP | `dsa-ip-reporting@roblox.com` | Appeals within 6 months |

Your own release gate: list every piece of visible text in the map (signs, `SurfaceGui`, decals, item names), and replace real-world brands and street names. Maps adapted from other sources often carry them (observed). Check item names in a live server too, since names can be moderated into hashes after release.

**Right to be forgotten.** Roblox sends a daily message listing RTBF requests that need action. It can delete data automatically through data store deletion templates and fires the **Right to Erasure Request** webhook. You remain responsible for deleting personal data outside those templates (`roblox-data` §1b, `roblox-cloud` §8.9).

Sources: [Content ratings](https://create.roblox.com/docs/production/promotion/content-ratings), [IP guidelines](https://create.roblox.com/docs/production/publishing/ip-guidelines), [DSA IP reporting](https://create.roblox.com/docs/production/publishing/dsa-ip-reporting), [RTBF and creators](https://create.roblox.com/docs/production/publishing/RTBF-and-creators), [Adaptive design](https://create.roblox.com/docs/production/publishing/adaptive-design), [Descriptions](https://create.roblox.com/docs/production/publishing/descriptions).

## 7b. Release-verification traps (observed)

**A commit isn't a publish.** A built and committed fix isn't live until it's published and servers run it. In one case, the old build served for about 15 more hours.

- After each publish, confirm the new `game.PlaceVersion` or build stamp appears in your own telemetry.
- Alarm when source commits are hours newer than the build serving sessions.

**Stale Studio windows.** A Studio window opened before a deploy keeps the old build. Saving or publishing from it pushes the old build back.

- Stamp a build attribute (commit plus UTC time) at build time.
- Compare it in the running place before you claim a fix is live.
- Close stale windows without saving.

**Kits and templates need a fresh-profile audit.** Reviewed kits shipped with:

- inflated default saves (`math.huge` coins, 1B XP)
- empty tutorial handlers
- daily rewards granting 0
- codes and wheel spins whose used-state lived only in memory, so they reset on rejoin
- offline earnings with no writer
- friend boosts fed by an empty list

Read the default profile, play the first session on a new account, leave and rejoin, and claim every reward once.

**Subplace avatar settings.** Avatar settings from the start place applied in a start-place playtest but not in a subplace playtest. `game:FindService("AvatarSettings")` returned nil. Verify subplace avatars on a live server.

**Two real accounts for multiplayer claims.** Check friendly fire, party payouts, and spawn protection with two accounts on two machines against the dev universe. Add a temporary server-side damage and death log, so every claim comes from the server log rather than one screen.

- Engine messages (asset load failures) don't reach custom error telemetry, so also read each client's F9 log.
- Some third-party clients drop launch data from deep links. Test invite flows on official clients.
- Test activity lands in dev leaderboards and saves, so restore them afterward.

**Soft releases for lobby-plus-match universes** (reported by one team):

- Stamp a build id on every place.
- After publishing, have outdated lobbies show a short countdown and teleport players to fresh lobbies on the new build.
- Drain only the lobby place's old versions with the Open Cloud restart-servers API and a bleed-off window, and leave match servers alone so rounds finish.
- Name the place in every restart request. One that names no place restarts everything (as reported).
- Keep the previous release's place files for rollback.

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

Group evidence by class in the report: edits that succeeded (readback-confirmed), runtime behavior actually observed, and checks that could not run (reported as Unverified). A successful edit is not runtime proof. The checklist documents rollback; it does not supply transactional rollback. Recovery relies on the compensating action recorded per mutation (`roblox-studio-mcp`).

`READY WITH ACCEPTED RISK` requires a named risk, impact, owner, and rollback or mitigation. It is not a softer spelling of NOT READY.

## Close the release against the serving build

Track the source revision, installed Studio payload, published place version, and versions actually serving sessions separately. After an authorized publication, join through the intended player entry path and record the experience, place, runtime `PlaceVersion`, build marker, access state, and smoke-test result. Existing servers keep their loaded place version when a newer version is published. Report old and new live versions separately before attributing telemetry to a fix.

Inventory models, UI templates, and other place-owned dependencies referenced by the changed code. Exercise their spawn/open path in the release place and inspect the result: a silent fallback can leave the console clean while an asset is missing. Match this inventory to the saved/published candidate, not only the working Studio tree.

### Player-state transition matrix

For round or shared-state changes, cross the relevant events with active survivors, eliminated players already respawned, spectators, mid-round joiners, revived players, and leavers. Include join/data-ready during setup, role reveal, teleport, active play, results, cleanup, and the next round where applicable. Observe each affected client's controls, camera, UI, tools, and participation state. Include human and bot paths when both exist. A solo round that ends immediately on death cannot verify an eliminated player's behavior during a continuing multiplayer round.
