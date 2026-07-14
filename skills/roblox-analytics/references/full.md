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
    customFields = {
        [Enum.AnalyticsCustomFieldKeys.CustomField01] = { value = "Zombie" },
        [Enum.AnalyticsCustomFieldKeys.CustomField02] = { value = "Sword" },
        [Enum.AnalyticsCustomFieldKeys.CustomField03] = { value = "Wave5" },
    }
})
```

### Economy Events

Track virtual currency flow. Enables revenue analysis, inflation detection, economy health.

```luau
-- Player EARNED currency (source)
AnalyticsService:LogEconomyEvent(
    player,
    Enum.AnalyticsEconomyFlowType.Source, -- Source = earned/gained
    "Coins",                               -- Currency name (max 10 types)
    50,                                    -- Amount
    player.leaderstats.Coins.Value + 50,   -- Balance AFTER transaction
    Enum.AnalyticsEconomyTransactionType.Gameplay.Name, -- Transaction type
    "QuestReward_Daily",                   -- Item SKU (what triggered it)
    {
        customFields = {
            [Enum.AnalyticsCustomFieldKeys.CustomField01] = { value = "Quest_001" },
        }
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

Transaction types: `Gameplay`, `ContextualPurchase`, `InAppPurchase`, `Shop`, `TimedReward`, `Trade`.

### Funnel Events

Track step-by-step progression through a flow. Max 10 funnels, 100 steps each.

```luau
-- Onboarding funnel: track where players drop off
AnalyticsService:LogFunnelStepEvent(player, "Onboarding", "1", "WelcomeScreen")
-- ... player progresses ...
AnalyticsService:LogFunnelStepEvent(player, "Onboarding", "2", "PickCharacter")
-- ... player progresses ...
AnalyticsService:LogFunnelStepEvent(player, "Onboarding", "3", "FirstBattle")
-- ... player progresses ...
AnalyticsService:LogFunnelStepEvent(player, "Onboarding", "4", "CompleteTutorial")

-- Shop conversion funnel
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", "1", "OpenedShop")
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", "2", "ViewedItem")
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", "3", "ClickedBuy")
AnalyticsService:LogFunnelStepEvent(player, "ShopPurchase", "4", "ConfirmedPurchase")
```

Steps MUST fire in order for the same player in the same session. Skipping step 2 and firing step 3 breaks the funnel visualization.

---

## 2. Rate Limits and Batching

| Constraint | Limit |
|-----------|-------|
| Total AnalyticsService calls/minute | 120 + (20 × CCU) |
| Custom event names | 100 |
| Economy resource types | 10 |
| Funnels | 10 |
| Steps per funnel | 100 |
| Custom fields per event | 3 |
| Unique values per custom field | 8,000 (then grouped as "Other") |

### Batching Strategy

For high-frequency events (kills, item pickups), batch on the server:

```luau
-- ServerScriptService/Analytics/EventBatcher.luau

local AnalyticsService = game:GetService("AnalyticsService")

local EventBatcher = {}
local batches: { [Player]: { [string]: number } } = {}

-- Accumulate events, flush periodically
function EventBatcher:increment(player: Player, eventName: string, amount: number?)
    if not batches[player] then
        batches[player] = {}
    end
    local current = batches[player][eventName] or 0
    batches[player][eventName] = current + (amount or 1)
end

function EventBatcher:flush()
    for player, events in batches do
        if not player:IsDescendantOf(game.Players) then
            batches[player] = nil
            continue
        end
        for eventName, value in events do
            local success, err = pcall(function()
                AnalyticsService:LogCustomEvent(player, eventName, value)
            end)
            if not success then warn("Analytics event failed:", err) end
        end
    end
    batches = {}
end

-- Flush every 30 seconds
task.spawn(function()
    while true do
        task.wait(30)
        EventBatcher:flush()
    end
end)

-- Flush on player leaving (capture final counts)
game.Players.PlayerRemoving:Connect(function(player)
    if batches[player] then
        for eventName, value in batches[player] do
            AnalyticsService:LogCustomEvent(player, eventName, value)
        end
        batches[player] = nil
    end
end)

return EventBatcher
```

For a maintained batching module with failure retention, see [`references/event-batcher.luau`](references/event-batcher.luau).

---

## 3. Event Taxonomy (Recommended)

Use consistent naming. Custom fields for breakdown, not separate event names.

### DO: Use custom fields for variants

```luau
-- ONE event, broken down by weapon type via custom field
AnalyticsService:LogCustomEvent(player, "EnemyKill", 1, {
    customFields = {
        [Enum.AnalyticsCustomFieldKeys.CustomField01] = { value = weaponType },
        [Enum.AnalyticsCustomFieldKeys.CustomField02] = { value = enemyType },
    }
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
- Firing funnel steps out of order (breaks the visualization)
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

## 6. Best Practices

- Log from server, not client. Client events can be spoofed.
- Log AFTER the action succeeds, not when attempted.
- Use the event batcher for high-frequency events (kills, pickups, damage dealt).
- Keep event names stable across updates. Renaming breaks historical comparison.
- Use custom fields for dimensions you want to filter by (weapon, map, class).
- Track both sources and sinks for every currency to detect inflation.
- Implement all funnels on day 1. Adding them later means no historical baseline.
- Test with "View Events" before relying on the 24-hour dashboard.
