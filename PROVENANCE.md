# Provenance

Notes on sources examined for this library: what was removed, what was reviewed, and under what terms.

## Removed source: brockmartin/roblox-game-skill

A reference snapshot was examined on 2026-07-04 while developing eight Roblox skills. The snapshot was removed from this repository after provenance review because the upstream repository has no documented license or reuse permission.

The affected skills were independently re-authored on 2026-07-12 from Roblox Creator Hub documentation and original examples. The removed snapshot is not part of the release.

## License Note

No LICENSE file or explicit reuse permission was found in the upstream repository. This note records why the historical copy was removed; it is not permission to reuse upstream text.

## Verification

The current skills use official documentation and original synthesis. Automated structure, source-URL, API-drift, version-pin, and fenced-code checks run in CI.

## Third-party skill review: MSayib/roblox-dev-skill and andrian-syh/roblox-best-practices-skill

Both repositories were read as comparative material on 2026-09-13 to find coverage gaps in this library. Neither was integrated as source text.

| Repository | License | Snapshot |
|---|---|---|
| https://github.com/MSayib/roblox-dev-skill | MIT, "Copyright (c) 2026" (no named holder) | commit `21b56c0`, 2026-09-06, self-described v2.7.0 accuracy pass |
| https://github.com/andrian-syh/roblox-best-practices-skill | MIT, Copyright (c) 2026 Muhammad Andriansyah | commit `300a79d`, 2026-08-28 |

## Reuse terms

MIT permits reuse with attribution. No upstream text was copied. Findings from both repository snapshots were re-derived from Roblox Creator Hub documentation and this library's own conventions, and every added claim in skills/ carries a documentation URL. The working copies were temporary and were removed after the review.

## Claims examined and not adopted

- MSayib's canonical `ProcessReceipt` example grants the product and returns `PurchaseGranted` without recording the `PurchaseId`. That is the duplicate-grant pattern `roblox-monetization` prohibits by name, so the example was rejected rather than borrowed.
- MSayib's monetization reference lists Engagement-Based Payouts as a current program. `roblox-monetization` marks it deprecated with a temporal marker.
- A MemoryStore counter primitive attributed to `MemoryStoreService` could not be confirmed: the class page documents `GetHashMap`, `GetQueue`, and `GetSortedMap` only.
- The upstream repositories have self-corrected fabricated members on their own side (the v2.7.0 accuracy pass retracts invented API surface). Treating either repository as an API authority is unsupported; this review used the engine reference only.

## Third-party code review: MaximumADHD/Roblox-Boilerplate

Reviewed on 2026-09-19 (commit `4358d1a`, MIT, "Copyright (c) 2025-Present MaximumADHD") as comparative material for general practices. Repository: https://github.com/MaximumADHD/Roblox-Boilerplate

No upstream code was copied. Five general practices were identified and re-derived in this library's own words and examples: typed signal payload aliases (`roblox-luau-patterns`), an edit-mode loopback mock for the network layer (`roblox-networking`), environment-suffixed store names (`roblox-data`), template reconciliation for added fields (`roblox-data`), and gated custom MicroProfiler labels via the `debug` library (`roblox-performance`). Upstream's project-specific machinery (ConVar console, CrunchTable binary serialization, TOML settings backend, AVLTree, StackModifier, React story tooling) was examined and deliberately not adopted as not generalizable. A correctness note: upstream's `PlayerData.Save` returns the transform result from `UpdateAsync` without handling the cancelled-transform (nil) case, a failure path this library already documents; the pattern was not borrowed.
