## Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## 1. AnalyticsService API

All methods are called on the server via `game:GetService("AnalyticsService")`.

### Custom Events

Track any game-specific metric. Two forms: counter (no value) and valued.

```luau
local AnalyticsService = game:GetService("AnalyticsService")

-- Counter: tracks occurrence count + unique users automatically
AnalyticsService:LogCustomEvent(player, "MissionStarted")

-- With value: enables sum/mean/min/max aggregations
AnalyticsService:LogCustomEvent(player, "MissionCompletedDuration", 120)

-- With custom fields (up to 3): enables filtering/breakdown on dashboard
AnalyticsService:LogCustomEvent(player, "EnemyDefeated", 1, {
    [Enum.AnalyticsCustomFieldKeys.CustomField01.Name] = "Enemy - Zombie",
    [Enum.AnalyticsCustomFieldKeys.CustomField02.Name] = "Weapon - Sword",
    [Enum.AnalyticsCustomFieldKeys.CustomField03.Name] = "Wave - 5",
})
```

### Economy Events

Track virtual currency flow. Enables revenue analysis, inflation detection, economy health.

```luau
-- Player EARNED currency (source)
AnalyticsService:LogEconomyEvent(
    player,
    Enum.AnalyticsEconomyFlowType.Source, -- Source = earned/gained
    "Coins",                               -- Currency name (max 5 types)
    50,                                    -- Amount
    player.leaderstats.Coins.Value + 50,   -- Balance AFTER transaction
    Enum.AnalyticsEconomyTransactionType.Gameplay.Name, -- Transaction type
    "QuestReward_Daily",                   -- Item SKU (what triggered it)
    {
        [Enum.AnalyticsCustomFieldKeys.CustomField01.Name] = "Quest - 001",
    }
)

-- Player SPENT currency (sink)
AnalyticsService:LogEconomyEvent(
    player,
    Enum.AnalyticsEconomyFlowType.Sink, -- Sink = spent/consumed
    "Coins",
    200,
    player.leaderstats.Coins.Value - 200,
    Enum.AnalyticsEconomyTransactionType.Shop.Name,
    "SpeedBoost_30min"
)
```

Transaction types: `IAP`, `Shop`, `Gameplay`, `ContextualPurchase`, `TimedReward`, `Onboarding`.

### Funnel Events

Track step-by-step progression through a flow. Max 10 funnels, 100 steps each.

```luau
-- Onboarding funnel: track where players drop off
AnalyticsService:LogOnboardingFunnelStepEvent(player, 1, "WelcomeScreen")
-- ... player progresses ...
AnalyticsService:LogOnboardingFunnelStepEvent(player, 2, "PickCharacter")
-- ... player progresses ...
AnalyticsService:LogOnboardingFunnelStepEvent(player, 3, "FirstBattle")
-- ... player progresses ...
AnalyticsService:LogOnboardingFunnelStepEvent(player, 4, "CompleteTutorial")

-- Recurring shop funnel: keep one ID for this checkout attempt
local HttpService = game:GetService("HttpService")
local checkoutSessionId = HttpService:GenerateGUID(false)
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", checkoutSessionId, 1, "OpenedShop")
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", checkoutSessionId, 2, "ViewedItem")
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", checkoutSessionId, 3, "ClickedBuy")
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", checkoutSessionId, 4, "ConfirmedPurchase")
```

Use the same session ID for every step of one recurring funnel attempt. If a
step is skipped, Analytics treats the intermediate step as completed.

---

## 2. Rate Limits and Batching

| Constraint | Limit |
|-----------|-------|
| Total AnalyticsService calls/minute | 120 + (20 × CCU) |
| Custom event names | 100 |
| Unique currency types | 5 |
| Funnels | 10 |
| Steps per funnel | 100 |
| Custom fields per event | 3 |
| Unique values per custom field | 8,000 (then grouped as "Other") |

### Batching Strategy

For high-frequency events such as kills or pickups, aggregate counters in the
project's canonical analytics owner and flush on its existing scheduler.
Preserve failed sends for a later retry; do not clear the whole batch after a
partial failure. Do not hide a permanent task loop inside a reference module's
top-level `require`; startup, player cleanup, and shutdown need an explicit
owner in the consuming project.

---

## 3. Event Taxonomy (Recommended)

Use consistent naming. Custom fields for breakdown, not separate event names.

### DO: Use custom fields for variants

```luau
-- ONE event, broken down by weapon type via custom field
AnalyticsService:LogCustomEvent(player, "EnemyKill", 1, {
    [Enum.AnalyticsCustomFieldKeys.CustomField01.Name] = tostring(weaponType),
    [Enum.AnalyticsCustomFieldKeys.CustomField02.Name] = tostring(enemyType),
})
```

### DON'T: Create separate events per variant

```luau
-- BAD: burns through your 100 event limit fast
AnalyticsService:LogCustomEvent(player, "EnemyKill_Sword")
AnalyticsService:LogCustomEvent(player, "EnemyKill_Bow")
AnalyticsService:LogCustomEvent(player, "EnemyKill_Magic")
```

### Common Event Taxonomy

**Retention signals:**
- `SessionStart` - counter, fire on PlayerAdded
- `SessionDuration` - value (seconds), fire on PlayerRemoving
- `DayNReturn` - counter with custom field for day number (Day1, Day7, Day30)

**Engagement:**
- `FeatureUsed` - custom field 1 = feature name
- `QuestCompleted` - custom field 1 = quest ID
- `LevelReached` - value = level number

**Monetization funnel:**
- Funnel "Purchase": OpenedShop → ViewedItem → ClickedBuy → Confirmed → Granted
- Economy source: IAP, QuestReward, DailyLogin, Trade
- Economy sink: ShopPurchase, Upgrade, Trade

**Progression:**
- Funnel "Onboarding": each tutorial step
- Funnel "BossAttempt": Started → Phase1 → Phase2 → Defeated

---

## 4. Validation and Debugging

### Real-time event validation

1. Navigate to Creator Hub → Analytics → Custom/Economy/Funnel
2. Click "View Events" at the top
3. Events appear in near real-time (seconds, not the 24-hour dashboard delay)
4. Refresh to see new events

### Common mistakes

- Logging on attempt instead of success (inflates metrics)
- Logging from client (exploiters can spam fake events)
- Exceeding rate limits silently (events get dropped, no error)
- Using too many unique event names (100 limit, then new ones are ignored)
- Firing funnel steps out of order (skipped intermediate steps are automatically back-filled as completed, so the visualization still works, but the data may not reflect the actual player journey)
- Not logging economy balance (makes inflation analysis impossible)

---

## 5. Creator Rewards and analytics

Creator Rewards is not an `AnalyticsService` event and should not be reconstructed from client telemetry. The platform determines qualifying users, attribution, and reward amounts. Use server-side analytics to measure the product signals you control:

- session duration and the 10-minute engagement milestone;
- onboarding and first-session completion;
- referral or share-link landing flows when your product exposes them;
- retention and return behavior;
- economy sources and sinks separately from platform rewards.

Use Creator Dashboard as the authority for Creator Rewards eligibility, rewarded active spenders, signups, reactivations, and estimated payout. Do not label a local event as “Creator Reward Granted” or promise a Robux amount based on it.

---

## 6. Economy Health Signals (Decision Layer)

**Instrument before you need it.** Complex-economy games fail without telemetry: when the economy breaks (inflation, sink collapse, whale concentration) the diagnosis is only as good as the events you started logging months earlier. Log economy events from day one, not when something goes wrong. You cannot backfill history.

### Which events to log for a complex economy

For every currency (max 5 types), log the full loop:

- **Sources (earned):** quest rewards, daily login, gameplay drops, trades in, IAP top-ups. Use distinct SKUs so you know *which* source inflates ("QuestReward_Daily" vs "QuestReward_Event").
- **Sinks (spent):** shop purchases, upgrades, repairs, trade fees, consumables. Same SKU discipline — a missing sink is the classic hidden deflation/inflation culprit.
- **Balance AFTER transaction:** always pass `balanceAfterTransaction` so you can reconstruct balances over time and detect hoarding or loss.
- **Item/feature acquisition:** custom event "ItemUnlocked" with item ID field; lets you see which content drives spending.
- **Conversion funnel:** "Purchase" funnel (OpenedShop → ViewedItem → ClickedBuy → Confirmed → Granted) plus economy sink events. This links monetization health to the purchase funnel.

### Economy health signals

| Signal | Formula / source | Healthy | Problem |
|--------|------------------|---------|---------|
| **Sink/source ratio** | total sinks ÷ total sources per currency | near 1.0 over a period | ≪1 = inflation (currency piling up), ≫1 = deflation (players can't afford items) |
| **Inflation** | units per active player climbing over weeks | flat/stable | players earn faster than they can spend; prices need sinks or rebalancing |
| **Whale concentration** | share of revenue from top N% payers | diversified | >75% from top 5% = revenue fragility, exploit risk, and unrepresentative feedback |
| **Price elasticity** | purchases vs price changes (experiment or segmented A/B) | meaningful response | no response = either price too low (leaving money) or poor value communication |
| **Sink sufficiency** | active sinks per player per session | players use sinks | no sinks = hoarding, then massive inflation once a sink opens |
| **D1/D7 cohort cross-link** | retention by acquisition cohort vs spend | new cohorts monetize similarly | a cohort with low retention + high spend = one-time whales, not a healthy base |

### Diagnose with telemetry (workflow)

When the economy or retention breaks, run this before touching balance numbers:

1. **Check you have the events.** Is every currency tracked as source AND sink with SKUs? Do you have balance-after-transaction? Purchase funnel? If not, that absence is itself the finding — instrument, then wait for data (24h dashboard lag; use "View Events" for real-time spot checks).
2. **Check logging correctness.** Logged AFTER success, not attempt? Server-side only? If a sink was never logged (e.g. repair costs omitting tracking), apparent inflation may be a measurement gap.
3. **Read the health signals above.** Pick the narrowest broken ratio first: sink/source, then concentration, then cohort cross-links.
4. **Act on the smallest lever.** One balance change (sink price, source rate) at a time, with a hypothesis and a guardrail. Re-check the same signals after the change — the data loop is the point.

Telemetry tells you the economy is broken and whether a fix worked; it does not decide what to do. The user owns the design choice. Your job is to surface what the numbers mean and flag when the data is insufficient to decide.

---

## 7. Best Practices

- Log from server, not client. Client events can be spoofed.
- Log AFTER the action succeeds, not when attempted.
- Use the event batcher for high-frequency events (kills, pickups, damage dealt).
- Keep event names stable across updates. Renaming breaks historical comparison.
- Use custom fields for dimensions you want to filter by (weapon, map, class).
- Track both sources and sinks for every currency to detect inflation.
- Implement all funnels on day 1. Adding them later means no historical baseline.
- Test with "View Events" before relying on the 24-hour dashboard.
