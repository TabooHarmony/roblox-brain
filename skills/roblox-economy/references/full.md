# Roblox Economy Design — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## Currency Types

- **Soft Currency** (e.g. "Gold"): Earned through gameplay. Primary transaction currency.
- **Premium Currency** (e.g. "Gems"): Earned rarely or purchased with Robux. For premium items, boosts, skips.
- **Tokens** (e.g. "Event Points"): Limited-time currency for event rewards. Expires or resets per event.
- **XP/Level**: Not a currency but follows similar curve design.

Rule: never more than 3 currencies. Players can't track more than that.

## Faucets vs Sinks

The economy must have BOTH, roughly balanced over time.

### Faucets (currency enters)
- Quest/mission rewards
- Level-up bonuses
- Daily login rewards
- Enemy/NPC drops
- PvP/minigame wins
- Selling items (inventory → currency)
- Achievement rewards
- Rebirth/prestige bonuses

### Sinks (currency leaves)
- Item purchases
- Upgrades (permanent improvements)
- Repair/durability costs
- Cosmetic purchases
- Trading taxes (10-20%)
- Revive/retry fees
- Expiring consumables
- Gacha/lootbox rolls

**If faucets > sinks**: inflation. Currency becomes worthless. Players hoard items instead.
**If sinks > faucets**: deflation. New players can't afford anything. Retention drops.

## Time-to-Earn Targets

For every major item, calculate expected earn time:

```
Item: Legendary Sword
Price: 10,000 Gold
Average gold/min (new player): 50/min → 200 min (3.3 hours)
Average gold/min (level 20): 150/min → 67 min (1.1 hours)
```

Target brackets:

| Goal Type | Time to Earn |
|-----------|-------------|
| Early goals (first hour) | 5-15 minutes |
| Session goals | 30-60 minutes |
| Multi-session goals | 2-5 hours |
| Long-term goals | 10-50 hours |
| Prestige/completionist | 100+ hours |

**Critical rule**: Players must feel meaningful progress every 30-60 seconds. If the next reward is 3 hours away with no intermediate feedback, they quit.

## Inflation Control

Over time, currency supply grows faster than demand. Counter with:

- **Hard sinks**: Premium upgrades that scale with progression
- **Variable pricing**: Scale prices with player level or economy velocity
- **Seasonal resets**: Event currencies that expire
- **Luxury goods**: High-tier items that absorb large currency amounts
- **Trading taxes**: 10-20% removed per transaction
- **Durability/repair**: Ongoing costs for powerful items
- **Prestige/rebirth**: Reset currency for permanent multipliers

## Trading System Design

### Atomic Trade Pattern

Trades MUST be atomic. Either both sides complete or neither does.

```luau
-- Server-side trade execution
local function executeTrade(player1Data, player2Data, offer1, offer2): boolean
    -- Verify both players still have their offered items
    if not hasItems(player1Data, offer1) then return false end
    if not hasItems(player2Data, offer2) then return false end

    -- Execute atomically
    removeItems(player1Data, offer1)
    removeItems(player2Data, offer2)
    addItems(player1Data, offer2)
    addItems(player2Data, offer1)

    -- Apply tax (remove currency portion)
    local tax1 = math.floor(offer1.currency * 0.1)
    local tax2 = math.floor(offer2.currency * 0.1)
    player1Data.Gold -= tax1
    player2Data.Gold -= tax2

    return true
end
```

### Anti-Scam Rules
- Both players must confirm twice (propose → review → confirm)
- Show exact items being traded with rarity/value indicators
- Cooldown between trades (prevent rapid-fire scam attempts)
- Log all trades server-side for rollback capability
- Value warnings: "You are trading a Legendary item for a Common item. Are you sure?"

## Monetization Integration

### Robux → Premium Currency
- Never sell soft currency directly for Robux (causes instant inflation)
- Sell premium currency that buys exclusive items OR time-skips
- Time-skips should save time, not provide power (pay-to-skip, not pay-to-win)

### GamePass Design
- Permanent multipliers (2x Gold) are inflation accelerators. Cap them or scale prices.
- Cosmetic-only passes have zero economy impact (safest)
- Inventory expansion passes are good sinks (player pays for convenience)

### Battle Pass / Season Pass
- Free track: enough rewards to feel progress
- Premium track: cosmetics + currency + exclusive items
- End-of-season: unconverted premium currency expires (sink)

## Economy Health Metrics

Track these server-side:

```luau
-- Log economy metrics per player session
AnalyticsService:LogEconomyEvent(player, {
    flowType = Enum.AnalyticsEconomyFlowType.Source, -- or Sink
    currencyType = "Gold",
    amount = amount,
    transactionType = "QuestReward", -- or "Purchase", "Trade", etc.
    itemSKU = itemId, -- what was bought/earned
})
```

Key ratios to monitor:
- **Earn rate by level**: Are high-level players earning disproportionately?
- **Sink participation**: What % of players use each sink?
- **Currency stockpile distribution**: Are top 1% hoarding?
- **Time-to-first-purchase**: How long before new players buy something?
- **Trade volume**: Is the trading economy healthy or dead?

## Common Mistakes

- **Infinite faucets, finite sinks**: Eventually everyone has everything. Game dies.
- **Rewarding AFK**: Players will AFK-farm any passive income. Gate rewards behind active play.
- **Linear scaling**: If level 1 earns 10/min and level 100 earns 1000/min, prices must scale too or early content becomes free.
- **No early wins**: If the first meaningful purchase is 2 hours away, new players leave in 10 minutes.
- **Tradeable premium currency**: Creates real-money trading (RMT) markets. Usually bad.
- **No tax on trades**: Currency circulates forever without leaving the economy.
