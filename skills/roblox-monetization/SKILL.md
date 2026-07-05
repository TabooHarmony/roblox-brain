---
name: roblox-monetization
description: ProcessReceipt correctness, prompt APIs, purchase reconciliation, session-lock interaction.
last_reviewed: 2026-05-26
sources:
  - https://github.com/brockmartin/roblox-game-skill (MIT)
---

# Roblox Monetization Systems Reference

## When to Load

Load when adding in-game purchases (GamePasses, Developer Products), designing monetization strategy, implementing Premium payouts, or reviewing policy compliance.

## Quick Reference

**Load Full Reference below only when you need specific API implementations or pricing formulas.**

Key rules:
- GamePasses: one-time purchase, check with UserOwnsGamePassAsync on join + cache.
- Developer Products: consumable, ProcessReceipt is the ONLY place to grant items.
- ProcessReceipt contract: grant item THEN return PurchaseGranted. If grant fails, return NotProcessedYet. Never return PurchaseGranted before granting.
- All purchase logic is SERVER-SIDE. Client only prompts.
- PromptGamePassPurchase / PromptProductPurchase from client, handle on server.
- TOS: odds disclosure MANDATORY for random items. Games get removed without it.
- TOS: no real-world trading, no misleading purchase UI, no pay-to-win that ruins gameplay.
- DevEx: dual-rate system. New Rate $0.0038/R$ (earned after Sept 5, 2025). Old Rate $0.0035/R$ (earned before). Must clear Old Rate balance first. US 18+ creators get higher rate ~$0.0054/R$ (as of June 2026). <!-- temporal: 2026-06 -->
- Premium Payouts: engagement-based, detect with player.MembershipType.
- Subscriptions: recurring monthly revenue via PromptSubscriptionPurchase. Tiered benefits.
- Private Servers: monetizable via PromptCreatePrivateServer / PromptPurchasePrivateServer.
- Paid Access: one-time Robux or local currency fee via PromptPurchaseExperience. Common for closed betas.
- Immersive Ads: AdService image/portal/video ad units. Earn via ad views, separate from Rewarded Video Ads.
- PolicyService: must-check for compliance (age/region restrictions on subscriptions, random items, ads).
- Commerce Products: sell physical merchandise through Roblox.

### Economy Design Impact
For how monetization affects in-game economy (inflation, sinks, currency flow), see `roblox-economy`.
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
