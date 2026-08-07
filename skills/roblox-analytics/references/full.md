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

## 6. Static Artifact Review

When reviewing a static `.rbxl` or `.rbxm`, scan script call sites, funnel-shaped names, and UI or interaction boundaries to propose candidate instrumentation. Treat the result as a routing aid only:

- a present call site does not prove that the event fires on the successful server-side transition;
- a missing call site does not prove that live instrumentation is absent, because code may be generated, external, or outside the inspected artifact;
- class, name, and string counts do not establish funnel quality, retention, conversion, or economy health;
- validate the chosen events with a runtime scenario and Creator Hub's event view before using them for decisions.

## 7. Best Practices

- Log from server, not client. Client events can be spoofed.
- Log AFTER the action succeeds, not when attempted.
- Use the event batcher for high-frequency events (kills, pickups, damage dealt).
- Keep event names stable across updates. Renaming breaks historical comparison.
- Use custom fields for dimensions you want to filter by (weapon, map, class).
- Track both sources and sinks for every currency to detect inflation.
- Implement all funnels on day 1. Adding them later means no historical baseline.
- Test with "View Events" before relying on the 24-hour dashboard.
