# Task 010: Write monetization-systems.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/monetization-systems.md`

## Description

Write a comprehensive monetization reference covering GamePasses, Developer Products, Premium Payouts, Rewarded Video Ads, DevEx, and ethical monetization for Roblox's young audience.

## What To Do

1. **Overview** — When to load (adding purchases, monetization strategy, revenue optimization)
2. **GamePasses** — MarketplaceService:UserOwnsGamePassAsync, PromptGamePassPurchase, ProcessReceipt. One-time permanent purchases. Implementation code for checking ownership and granting perks
3. **Developer Products** — Consumable purchases (currency, boosts, lives). MarketplaceService:PromptProductPurchase, ProcessReceipt callback pattern. Critical: ProcessReceipt must return Enum.ProductPurchaseDecision.PurchaseGranted only after granting the item
4. **Premium Payouts** — How Premium subscription revenue sharing works, Players:GetPropertyChangedSignal("MembershipType"), incentivizing Premium play time
5. **Rewarded Video Ads (2026)** — New ad monetization system, implementation patterns, recommended reward values (3-10 Robux equivalent), ad placement best practices
6. **Pricing Strategy** — Roblox pricing tiers, anchoring, bundle psychology, conversion from Robux to USD for DevEx planning
7. **DevEx Math** — Exchange rate ($0.0035-$0.0038/Robux), minimum 30,000 earned Robux, revenue projections based on DAU
8. **Ethical Monetization** — Roblox's young audience considerations, avoiding predatory patterns, providing value, no pay-to-win in competitive games, transparency in odds
9. **Best Practices** — Server-side purchase verification, graceful handling of purchase failures, receipt logging, A/B testing prices
10. **Anti-Patterns** — Client-side purchase granting, not handling ProcessReceipt properly (causes refunds), aggressive monetization, misleading descriptions

Include complete Luau implementations for GamePass and Developer Product systems.

## Verification

- File exists at `references/monetization-systems.md`
- GamePass and DevProduct implementations include complete Luau code
- ProcessReceipt pattern is correct and handles edge cases
- Rewarded Video Ads (2026) section included
- Ethical monetization considerations addressed
