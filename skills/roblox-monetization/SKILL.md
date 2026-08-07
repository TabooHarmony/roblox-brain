---
name: roblox-monetization
description: "Use when implementing Roblox GamePasses, Developer Products, subscriptions, private servers, Creator Rewards, or purchase policy checks."
last_reviewed: 2026-08-07
sources:
  - https://create.roblox.com/docs/reference/engine/classes/MarketplaceService
  - https://create.roblox.com/docs/production/monetization/passes
  - https://create.roblox.com/docs/production/monetization/developer-products
  - https://create.roblox.com/docs/production/monetization/subscriptions
  - https://create.roblox.com/docs/production/monetization/paid-random-items
  - https://create.roblox.com/docs/reference/engine/classes/PolicyService
  - https://create.roblox.com/docs/creator-rewards
  - https://devforum.roblox.com/t/creator-rewards-is-live/3838257
  - original
---

# roblox monetization

## When to Load

Load when adding a Game Pass, Developer Product, subscription, private server, Creator Rewards-related product decision, or purchase eligibility check.

## Quick Reference

- Prompt purchases from the client, but grant value only from server-owned code.
- Passes: durable ownership for an experience. Check ownership server-side and refresh after a purchase.
- Developer Products: repeatable consumables. `ProcessReceipt` is the grant path; `PromptProductPurchaseFinished` is not purchase confirmation.
- `BindReceiptHandler` handles Robux-transfer receipts, not Developer Products.
- A receipt that cannot be safely granted must return `NotProcessedYet`. Roblox redelivers it when the player rejoins (there is no time-based retry).
- Use `PolicyService` and the current monetization documentation for eligibility-sensitive features.
- Creator Rewards is a platform program, not a grant API. Track eligibility, attribution, engagement, and dashboard reporting separately from purchases and inventory.
- Test failed grants, duplicate receipts, player absence, and interrupted saves before shipping.
- Static presence of `ProcessReceipt` is not receipt correctness; inspect its single owner, durable idempotent grant, and retry paths for unknown products or absent players.

**Need the details?** Load `references/full.md` for purchase flows and failure handling.
