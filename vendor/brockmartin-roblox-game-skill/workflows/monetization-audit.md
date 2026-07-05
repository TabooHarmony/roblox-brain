# Monetization Audit Workflow

A step-by-step guided workflow for auditing, improving, and ethically evaluating monetization in a Roblox game.

---

## Step 1: Current State Scan

Map all existing monetization in the project.

### MCP Full (Rojo/Argon project on disk)

- Use `get_project_structure` to locate all scripts.
- Use `grep_scripts` to search for:
  - `MarketplaceService` — all usages.
  - `PromptGamePassPurchase` — GamePass purchase prompts.
  - `PromptProductPurchase` — DevProduct purchase prompts.
  - `UserOwnsGamePassAsync` — GamePass ownership checks.
  - `ProcessReceipt` — DevProduct receipt handling.
  - `PromptPremiumPurchase` — Roblox Premium prompts.
  - `PlayerMembershipChanged` — Premium status changes.
  - `PolicyService` — region-specific monetization restrictions.
- Build a complete monetization inventory:
  - GamePass name, ID, price, what it grants.
  - DevProduct name, ID, price, what it grants, repeat purchase behavior.
  - Premium benefits.
  - Any ad integrations.

### MCP Standard (partial access)

- Use available MCP tools to search for the patterns above.
- Ask the user to fill gaps in the inventory.

### Offline (no MCP / in-Studio only)

- Ask the user to provide:
  - Full list of GamePasses (name, price, benefit).
  - Full list of Developer Products (name, price, benefit, is it repeatable).
  - Whether Premium benefits exist.
  - Monthly revenue range (if comfortable sharing) for context.

---

## Step 2: GamePass Review

Evaluate each GamePass for value, clarity, and discoverability.

### Value Clarity

For each GamePass, answer:
- Is the benefit immediately obvious from the name and description?
- Does the player know exactly what they get before purchasing?
- Is the benefit meaningful enough to justify the price?
- Does it provide lasting value (not a one-time consumable dressed as a permanent pass)?

### Pricing

- Under 50 Robux: Impulse buy range. Good for small conveniences.
- 50-200 Robux: Standard range. Should provide clear, ongoing value.
- 200-1000 Robux: Premium range. Must provide significant, game-changing benefit.
- Over 1000 Robux: Whale range. Only justified for truly transformative features (e.g., VIP access with major perks).

### Discoverability

- Are GamePasses surfaced in-game at the right moment (not just in the store)?
- Does the player experience the *lack* of the benefit before being prompted? (Show value before asking for money.)
- Is there an in-game shop UI, or are players expected to find passes on the game page?

### Common Issues

- **Overpowered passes** — A single GamePass that trivializes the game, reducing engagement.
- **Underpowered passes** — Passes that offer so little value no one buys them.
- **Duplicate value** — Multiple passes with overlapping benefits confusing the buyer.
- **Missing passes** — Obvious monetization gaps (e.g., a simulator with no auto-collect pass).

---

## Step 3: DevProduct Review

Evaluate Developer Products (consumables) for compelling repeat-purchase design.

### Compelling Design

- Does the product solve a real player need (not an artificial gate)?
- Is the benefit immediate and satisfying?
- Does buying feel rewarding, not punishing (avoiding "pay to remove annoyance" patterns)?

### Pricing for Repeat Purchase

- Are products priced to encourage multiple purchases over a session?
- Is there a quantity tier system (buy 100 coins for 50R$, 500 coins for 200R$, 1000 coins for 350R$)?
- Do larger bundles offer meaningful discounts?

### ProcessReceipt Correctness

This is the most critical technical check for DevProducts:

```lua
-- CORRECT: Grant THEN acknowledge
MarketplaceService.ProcessReceipt = function(receiptInfo)
    local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then return Enum.ProductPurchaseDecision.NotProcessedYet end

    local success = grantProduct(player, receiptInfo.ProductId)
    if not success then return Enum.ProductPurchaseDecision.NotProcessedYet end

    -- Save to DataStore BEFORE acknowledging
    local saved = savePlayerData(player)
    if not saved then return Enum.ProductPurchaseDecision.NotProcessedYet end

    return Enum.ProductPurchaseDecision.PurchaseGranted
end
```

Common mistakes:
- Returning `PurchaseGranted` before saving to DataStore (data loss on crash).
- Not handling the case where the player left before receipt processing.
- Not handling unknown ProductIds.
- Having multiple `ProcessReceipt` assignments (only the last one works).

---

## Step 4: Missing Opportunities

Suggest genre-appropriate monetization the game is not currently using.

### Simulator Games

- Auto-collect / auto-farm pass.
- 2x multiplier passes (coins, XP, damage).
- Extra inventory/storage slots.
- Exclusive areas.
- Pet/companion eggs (DevProduct, repeatable).
- Lucky/rare boost (temporary, DevProduct).
- Instant rebirth (DevProduct).

### Tycoon Games

- Auto-dropper speed boost pass.
- Extra tycoon slot / second base.
- Premium building materials / decorations.
- Income multiplier.
- Skip stage / instant unlock (DevProduct).

### Obby / Adventure Games

- Skip stage (DevProduct).
- Checkpoint save pass.
- Cosmetic trails and effects.
- Speed boost pass.
- Extra lives (DevProduct).

### RPG / Combat Games

- Cosmetic skins and weapon appearances.
- Extra character slots.
- XP boost (timed, DevProduct).
- Inventory expansion.
- Fast travel pass.
- Premium character classes (GamePass, if balanced).

### Horror Games

- Cosmetic flashlight skins.
- Emotes and gestures.
- Spectator mode pass.
- Extra role selection weight.

### Battle Royale

- Battle pass / season pass (custom implementation).
- Cosmetic skins, emotes, sprays.
- Lobby effects.
- Stat tracker pass.

### General (all genres)

- VIP server benefits.
- Radio/music player pass.
- Chat effects (bubble chat colors, name tags).
- Trade system access.
- Daily reward multiplier.

---

## Step 5: Pricing Analysis

Compare pricing to Roblox platform norms and genre competition.

### Roblox Market Norms (approximate, 2024-2026)

| Category | Typical Range | Notes |
|----------|--------------|-------|
| Utility GamePass (2x coins, auto-collect) | 49-199 R$ | Most common price range |
| VIP GamePass | 99-499 R$ | Depends on benefits |
| Cosmetic GamePass | 25-149 R$ | Lower perceived value |
| Currency bundle (small) | 25-49 R$ | Impulse buy |
| Currency bundle (medium) | 99-199 R$ | Best value ratio |
| Currency bundle (large) | 399-999 R$ | Whale pricing |
| Skip/boost (DevProduct) | 5-25 R$ | Micro-transaction |

### Analysis Steps

1. List each product with its current price.
2. Compare to genre competitors (search for top games in the same genre).
3. Flag products priced significantly above or below market norms.
4. Evaluate if the price-to-value ratio encourages or discourages purchase.
5. Recommend price adjustments with reasoning.

---

## Step 6: Premium Integration Check

Evaluate Roblox Premium integration.

### Checklist

- [ ] **Premium detection** — Game checks `player.MembershipType == Enum.MembershipType.Premium` correctly.
- [ ] **Premium benefits** — Premium players receive meaningful but not game-breaking perks (e.g., 10-20% bonus currency, exclusive cosmetics, daily bonus).
- [ ] **Premium prompt** — `MarketplaceService:PromptPremiumPurchase()` is offered at an appropriate moment (not on join, not during critical gameplay).
- [ ] **Premium payouts** — The game earns Premium Payouts based on Premium player engagement. More Premium player time = more revenue.
- [ ] **Membership change handling** — `Players.PlayerMembershipChanged` is connected to update benefits if a player subscribes during a session.

### Recommendations

- If no Premium integration exists, recommend adding it as a low-effort revenue stream.
- Premium benefits should incentivize Premium players to play more (engagement = payouts), not just give a one-time bonus.

---

## Step 7: Ad Integration Evaluation

Evaluate whether advertising fits the game.

### Immersive Ads (Roblox native)

- Available for games meeting Roblox ad eligibility requirements.
- In-game ad placements (billboards, portals) that do not disrupt gameplay.
- Revenue is passive and based on impressions/clicks.
- Evaluate: Does the game have natural locations for ad placements (lobby walls, loading areas)?

### Rewarded Video Ads

- Players opt-in to watch an ad in exchange for in-game rewards.
- Must comply with Roblox policies (`PolicyService:GetPolicyInfoForPlayerAsync()` to check eligibility by region).
- Best for: Games with clear reward moments (extra life, bonus spin, temporary boost).
- Avoid: Showing ads to players under 13 or in restricted regions without policy checks.

### Considerations

- Ads should never be mandatory or block gameplay.
- Ad rewards should not undermine paid monetization (if watching an ad gives the same thing as a 100 R$ DevProduct, no one buys the product).
- Test ad frequency — too many ads drive players away.

---

## Step 8: Ethical Review

Flag predatory or player-hostile monetization patterns.

### Red Flags to Check

- [ ] **Pay-to-win** — Can paying players gain unfair competitive advantages over non-paying players in PvP or leaderboard contexts?
- [ ] **Artificial friction** — Are gameplay pain points deliberately created to sell the solution? (e.g., absurdly slow progression without a boost).
- [ ] **Hidden odds** — Are random reward mechanics (loot boxes, egg hatching) transparent about their odds?
- [ ] **Pressure tactics** — Limited-time offers with countdown timers designed to create urgency and prevent rational decision-making.
- [ ] **Currency obfuscation** — Multiple layers of virtual currency that make it hard to understand real-money costs.
- [ ] **Targeting children** — Flashy, high-pressure purchase prompts targeting the platform's younger demographic.
- [ ] **Sunk cost exploitation** — Systems designed to make players feel they must keep spending to justify past spending.
- [ ] **Incomplete without purchase** — Core gameplay that is unplayable or unenjoyable without spending money.

### Ethical Guidelines

- Free players should be able to enjoy the full core experience.
- Paying players should get convenience, cosmetics, or acceleration — not exclusive content that locks out free players from the core game.
- Random reward odds should be disclosed or easily discoverable.
- Purchase prompts should not interrupt critical gameplay moments.
- The game should be fun *before* asking for money.

---

## Step 9: Recommendations Report

Compile all findings into an actionable report.

### Format

```
## Monetization Audit Report

### Current Revenue Streams
- [List all existing GamePasses, DevProducts, Premium, Ads]

### Revenue Optimization Opportunities
1. [Opportunity] — [Expected impact] — [Implementation effort]
2. ...

### Pricing Adjustments
- [Product]: Current [X R$] -> Recommended [Y R$] — [Reasoning]

### Missing Monetization
- [Suggestion] — [Why it fits this game] — [Recommended price]

### Technical Issues
- [ProcessReceipt bugs, missing ownership checks, etc.]

### Ethical Concerns
- [Any flagged issues with severity and recommendation]

### Priority Actions
1. [Highest impact, lowest effort first]
2. ...

### Estimated Revenue Impact
- [Qualitative assessment: significant / moderate / minor improvement expected]
```

Order recommendations by impact-to-effort ratio. Quick wins first, then strategic improvements, then long-term suggestions.
