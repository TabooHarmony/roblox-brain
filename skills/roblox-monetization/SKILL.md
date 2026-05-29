---
name: roblox-monetization
description: ProcessReceipt correctness, prompt APIs, purchase reconciliation, session-lock interaction.
last_reviewed: 2026-05-26
---

<!-- Source: brockmartin/roblox-game-skill (MIT) -->

# Roblox Monetization Systems Reference

## 1. Overview

**Load this reference when:**

- Adding in-game purchases (GamePasses, Developer Products)
- Designing or revising a monetization strategy
- Optimizing revenue (pricing, placement, conversion funnels)
- Implementing Premium Payouts or Rewarded Video Ads
- Calculating DevEx projections
- Reviewing monetization ethics and Roblox policy compliance

Roblox provides four primary monetization channels: **GamePasses** (one-time permanent unlocks), **Developer Products** (consumable/repeatable purchases), **Premium Payouts** (revenue from Premium subscribers playing your game), and **Rewarded Video Ads** (ad-based revenue). Each channel serves a different purpose and should be combined strategically.

**Key principle:** All purchase granting MUST happen on the server. Never trust the client to determine what a player owns or has purchased.

---

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
- DevEx: dual-rate system. New Rate $0.0038/R$ (earned after Sept 5, 2025). Old Rate $0.0035/R$ (earned before). Must clear Old Rate balance first before New Rate kicks in.
- Premium Payouts: engagement-based, detect with player.MembershipType.
- Subscriptions: recurring monthly revenue via PromptSubscriptionPurchase. Tiered benefits.
- Private Servers: monetizable via PromptCreatePrivateServer / PromptPurchasePrivateServer.
- Paid Access: one-time Robux or local currency fee via PromptPurchaseExperience. Common for closed betas.
- Immersive Ads: AdService image/portal/video ad units. Earn via ad views, separate from Rewarded Video Ads.
- PolicyService: must-check for compliance (age/region restrictions on subscriptions, random items, ads).
- Commerce Products: sell physical merchandise through Roblox.
- Creator Store: sell plugins ($4.99+) and models ($2.99+) for USD. 30-day escrow hold.
- Never store purchase state only in DataStore without session locking (use ProfileStore).
