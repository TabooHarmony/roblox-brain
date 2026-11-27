# roblox monetization: full reference

> Code examples are illustrative. Adapt them to your project and verify in Studio before production use.

This guide focuses on the server-side correctness of Roblox's purchase APIs. Product catalog setup and current policy requirements change over time; use the linked Creator Hub pages as the authority for eligibility and configuration details.

## 1. Pick the product type

- **Pass:** durable ownership for an experience.
- **Developer Product:** repeatable consumable purchase.
- **Subscription:** recurring benefit with a subscription-specific lifecycle.
- **Private server or paid access:** access configuration rather than an item grant.
- **Creator Rewards and ads:** platform programs with their own eligibility and reporting rules.

Do not model all of these as one "purchase" table. Their ownership, renewal, refund, and retry behavior differ.

## 2. Keep prompting separate from granting

The client owns the presentation and can request a prompt. The server owns the entitlement. A button click or `PromptProductPurchaseFinished` event is never proof of a Developer Product grant.

```luau
-- LocalScript: presentation only
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

buyButton.Activated:Connect(function()
    MarketplaceService:PromptProductPurchase(Players.LocalPlayer, PRODUCT_ID)
end)
```

For a Game Pass, the server can check ownership before enabling a durable feature.

```luau
local MarketplaceService = game:GetService("MarketplaceService")

local function ownsPass(player: Player, passId: number): (boolean?, string?)
    local ok, owns = pcall(function()
        return MarketplaceService:UserOwnsGamePassAsync(player.UserId, passId)
    end)
    if not ok then
        return nil, tostring(owns) -- unknown; do not cache as non-ownership
    end
    return owns == true, nil
end
```

Call this every time access matters (join, spawn, when the benefit is used) instead of caching a `true` for the session or saving it: Roblox caches the result internally, so repeated calls are cheap, and the answer turns `false` when a free trial ends or a purchase is refunded. Handle API failure as "not confirmed yet": deny for now and re-check next time, never a permanent denial or grant.

## 2a. Centralized Game Pass benefits

Operator/design pattern, grounded in the official [passes flow](https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/production/monetization/passes.md): one server owner maintains a pass-ID→benefit registry and the corresponding confirmed entitlement state. Features ask this owner for access rather than each implementing a purchase listener. Keep this registry distinct from repeatable Developer Product grants.

- On `Players.PlayerAdded`, check configured pass ownership with `UserOwnsGamePassAsync` and reconcile benefits. Also cover players already present when the owner starts; prevent duplicate initialization. A failed request means unknown, not “does not own.” Never persist that failure as a negative entitlement.
- Connect `MarketplaceService.PromptGamePassPurchaseFinished` once on the server. For a registered pass and successful purchase, invalidate your application’s stale negative cache and run the same benefit reconciliation used on join. The engine updates its ownership-query cache when this event fires. Server event results reflect the final purchase outcome; LocalScript results must not authorize benefits.
- A benefit setter should be idempotent: “VIP access enabled” or “this pass contributes multiplier X,” not “add X again whenever a callback runs.” Compose multiple benefits from their sources instead of stacking them every respawn or refresh. Reapply character-specific presentation through the existing character lifecycle without duplicating the entitlement grant.
- An external purchase during an existing session can take several minutes to propagate through the engine ownership cache. Define a bounded refresh path; reconnecting starts a new ownership check. Do not promise that an application cache invalidation bypasses Roblox’s cache.
- Validate configured IDs and keep unknown passes from authorizing arbitrary benefits. Remove per-player caches at departure and ignore stale asynchronous results for a player/session that has ended. Keep subscriptions and paid consumables on their own lifecycle paths.

### Pass free trials (from December 2, 2026)

<!-- temporal: 2026-11 --> Creators can enable a one-session **free trial** per pass (Creator Hub > Monetization > Shop > Free Trials, or the Open Cloud game passes API; new passes have trials off by default). Players who don't own the pass see **Try** in Shop; each player gets one trial per pass, one active trial at a time. The trial lasts one game session (it survives a rejoin within an hour after a system error), and a **Buy** button appears before it ends. In Studio playtests, trials last one hour.

What breaks in old pass code:
- Starting a trial fires `PromptGamePassPurchaseFinished` with `purchaseSuccess = true`, and `UserOwnsGamePassAsync` returns `true` during the trial. No event fires when the trial ends; ownership checks simply return `false` again.
- So **any permanent grant on "owns pass" is now exploitable**: one-time bonus currency, inventory items, maxed upgrades, or unlock flags written to the DataStore. A player in a trial should get exactly what a buyer gets, and only while the trial lasts.
- Fix: apply pass benefits from a live ownership check and don't save them. For anything permanent, call `MarketplaceService:GetPassOwnershipAsync(player, passId)` and grant only when `.Owned` is `true` (bought). `.Active` is `true` for owners and active trials (it matches `UserOwnsGamePassAsync`); `StartTime`/`EndTime` are present while a trial is active. On the client it can only query the local player.
- Gifting flows: a trialing player looks like an owner to `UserOwnsGamePassAsync`, so check the recipient's `Owned` instead.

```luau
-- Server: permanent rewards only for purchased passes, not trials
local function grantPermanentRewardIfOwned(player: Player, passId: number)
	local ok, ownership = pcall(MarketplaceService.GetPassOwnershipAsync, MarketplaceService, player, passId)
	if not ok then
		warn("pass ownership check failed:", ownership) -- unknown: retry later, never grant
		return
	end
	if ownership.Owned then
		-- grant permanent items, currency, or saved data (idempotently)
	elseif ownership.Active then
		-- free trial: temporary, unsaved benefits only
	end
end
```

Test existing ownership on join, a trial start and its session end, purchase during a trial, purchase/cancel in-session, a query failure, repeated refresh, character respawn, player leave during the query, and two passes contributing to one benefit. Centralization removes duplicate plumbing, not product-specific rules or server validation.

## 3. Centralize Developer Product receipts

Use one server-owned Developer Product receipt path. The example below uses `ProcessReceipt`; alternatively, [`BindReceiptHandler`](https://create.roblox.com/docs/reference/engine/classes/MarketplaceService#BindReceiptHandler) accepts `Enum.ReceiptType.DeveloperProduct` with an optional product-ID filter. Whichever path owns the receipt must:

1. identify the product and player;
2. determine whether this receipt was already granted;
3. grant through the authoritative data service;
4. record the receipt or transaction id with the grant;
5. acknowledge the receipt only after durable success.

For `ProcessReceipt`, return `Enum.ProductPurchaseDecision` values as below. For `BindReceiptHandler`, return `Enum.ReceiptDecision` values.

```luau
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local productGrants = {
    [COIN_PRODUCT_ID] = { coins = 500 },
}

MarketplaceService.ProcessReceipt = function(receiptInfo)
    local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local productGrant = productGrants[receiptInfo.ProductId]
    if not productGrant then
        warn("Unhandled product", receiptInfo.ProductId)
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local transactionId = tostring(receiptInfo.PurchaseId)
    local granted = ReceiptStore:ApplyGrantOnce(
        transactionId,
        player.UserId,
        productGrant
    )
    if not granted then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end
    return Enum.ProductPurchaseDecision.PurchaseGranted
end
```

`ApplyGrantOnce` is a project-specific persistence boundary. It must make the
transaction ID and entitlement mutation one durable, idempotent operation, and
must treat an already-granted ID as success. Do not implement it as "grant,
then separately record": a crash or failed record between those operations can
duplicate value on retry.

Cross-owner atomicity: atomic receipt recording for one profile is not an atomic exchange between two profiles; for trading or gifting across profiles, see `roblox-data` full reference, section Cross-owner atomicity limits.

With `BindReceiptHandler`, filtered handlers claim their configured product IDs; a catch-all handles remaining products. A matching bound handler takes precedence over `ProcessReceipt`; unmatched receipts can fall through to it. Duplicate registrations for the same receipt type/product combination or catch-all fail. Keep routing ownership explicit during migration instead of registering competing callbacks. Retain the returned `RBXScriptConnection` for intentional teardown, not routine disconnection while receipts remain outstanding.

When wrapping a grant/save operation inside your receipt handler, `pcall` success means that operation did not throw, not that its domain result confirms a successful grant. Inspect both the protected-call flag and the returned domain result before acknowledging. `ProcessReceipt` has no timer-driven retry; bound receipts remain unresolved for a later delivery opportunity. Do not promise the two APIs have identical delivery timing.

## 3a. Receipt failure tests

For every receipt implementation, force these cases in a test place:

- the player is absent;
- the product is unknown or its handler is missing;
- the grant succeeds but recording the transaction fails;
- the same transaction is delivered twice;
- the server shuts down between grant and acknowledgement.

Receipt failures can be silent in normal play: the player paid and nothing arrived. Treat the durable idempotency record as load-bearing. Do not acknowledge an unknown product or a grant that was not durably recorded, and verify duplicate delivery returns success without granting twice.

## 4. Subscriptions and recurring benefits

Subscriptions need explicit entitlement checks and renewal handling. Keep these separate from one-time Game Pass ownership. A subscription benefit should have:

- a server-side entitlement check;
- a clear expiration or renewal state;
- behavior when the subscription API is unavailable;
- a downgrade path that does not delete unrelated player data;
- UI that describes the actual cadence and benefit.

Use the current subscription documentation for platform eligibility. Do not hard-code assumptions about age, region, or payment availability.

### Subscription status reconciliation

Query `MarketplaceService:GetUserSubscriptionStatusAsync(player, subscriptionId)` on the server at join. The result separates `IsSubscribed` (active entitlement) from `IsRenewing` (whether it will renew); cancellation of renewal is not immediate loss of a paid current term.

Even a successful query returns `IsSubscribed = false` while an initial payment is processing **or has failed**. Do not equate that response with a confirmed cancellation, and never grant a new paid benefit before active status is confirmed. Operator guidance: show pending status after purchase, reconcile again through the documented status event and bounded retries, and make any grace policy for previously confirmed benefits explicit rather than extending access indefinitely.

Listen to **`Players.UserSubscriptionStatusChanged(player, subscriptionId)`**, then query the current status again. It is not a `MarketplaceService.SubscriptionStatusChanged` event carrying a trusted new-status argument. Prompt closure is not payment confirmation.

This event is server-only and is recognized after the subscription purchase modal closes; an external purchase during play may need the documented prompt/refresh flow. Do not assume it is a push notification for every external billing change.

Apply/revoke through one benefit reconciler, with separate ownership for permanent pass benefits and temporary subscription benefits. A failed lookup is unknown: surface and retry within a bounded policy rather than deleting unrelated data or treating it as confirmed expiry. On replacing a pass with a subscription, preserve legacy passholders’ permanent benefits. If a plan grants currency once per paid period, use the documented payment/history contract and a durable period-specific deduplication record; do not grant again on every status check.

## 5. Private servers and paid access

Private-server prompts, paid access, and item purchases solve different problems. Decide whether the player is buying access, a server instance, or an in-game entitlement. Keep access enforcement on the server and test owners, invited players, and expired or unavailable configurations.

## 6. Policy and presentation

Eligibility-sensitive products may require `PolicyService` checks. Treat a failed policy lookup conservatively for the affected feature, and update the implementation when Roblox changes the documented requirements.

Purchase UI should make the price, cadence, contents, and meaningful restrictions clear. For randomized paid content, the current policy documentation requires outcome and numerical-odds disclosure before purchase, and classifies broad item types as paid random items, including probability modifiers such as luck boosts and pity systems. Do not rely on a color, rarity label, or marketing phrase as a substitute for a required disclosure.

When `ArePaidRandomItemsRestricted` is true for a user, Roblox lists several treatments: an unpaid earnable path to the item, a disclosed non-random sequence, guaranteed direct purchase of specific outcomes, hiding the paid-random feature, blocking that purchase with a message, or removing the user from the affected part of the game. Present the options and their trade-offs instead of defaulting to the most disruptive one. Do not unilaterally hide or remove a feature when a less disruptive documented option fits the game.

If the restriction applies, odds disclosure alone is not one of the listed treatments. Ask which documented option suits the game. If the requested purchase flow conflicts with the restriction, explain that once and keep working on unaffected parts; do not silently disable the feature or treat an unverified policy check as a pass.

Platform program names and payout rules change. Engagement-Based Payouts is historical/deprecated material, not a current implementation target; consult the current Creator Rewards documentation when working on platform payouts.

### Dynamic prices and transfer arbitrage

With Managed Pricing, fetch displayed product/pass prices at runtime from a client script using `MarketplaceService:GetProductInfoAsync` (and the matching `Enum.InfoType`); do not hard-code the default price in custom UI. Handle lookup failure as unavailable pricing rather than inventing an amount. Test with Creator Dashboard’s Dynamic Price Check and disable its test configuration afterward. Official source: [regional pricing](https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/production/monetization/regional-pricing.md).

For transferable paid items, price differences create a separate trading/gifting risk. Use `GetUsersPriceLevelsAsync` to inform the server’s transfer policy; map results by user ID and handle missing/failed results explicitly. Fetch at join and do not carry price-level caches across sessions. These levels do not replace item ownership checks, and a price-difference threshold is a design choice, not universal Roblox policy.

### Robux transfers are a distinct receipt flow

Official [Robux transfers](https://create.roblox.com/docs/production/monetization/robux-transfers) use server-only `MarketplaceService:PromptRobuxTransferAsync(sender, receiverUserId, amount)` with Roblox-controlled confirmation and eligibility. Use the actual requesting player as sender; validate the recipient, finite positive integer amount, supported bounds, authorization and prompt frequency before calling. Do not confuse a transfer request ID with settlement. As documented when reviewed, the supported transaction range is 10–500 Robux; check current documentation before shipping. <!-- temporal: 2026-10 -->

Transfers are a Roblox Plus subscriber feature. The current documented split is 10% to the game and 90% to the recipient; game earnings are DevEx-eligible and Roblox takes no transfer fee. Model reward economics against the appropriate sent/received amount, not a presumed 100% recipient payout. <!-- temporal: 2026-10 -->

Register separate `BindReceiptHandler` handlers for `Enum.ReceiptType.RobuxTransferSender` and `Enum.ReceiptType.RobuxTransferReceiver`. Correlate using `TransferRequestId`; use the receipt’s unique `PurchaseId` for durable duplicate protection and distinguish receipt side/user so sender and receiver processing cannot suppress each other. Return `Enum.ReceiptDecision.Processed` only after any promised persistent benefit is committed; otherwise keep it `NotProcessedYet`. Do not use `Enum.ProductPurchaseDecision` for bound handlers.

Receipts can settle after receiver approval and arrive on whichever server the relevant user is currently in, or on their next join if offline. Handle receipts without depending on the originating server’s in-memory request table. Sender `CurrencySpent` is sent amount; receiver `CurrencySpent` is received amount, so they are not interchangeable. Platform eligibility and limits remain Roblox-owned: do not fabricate age/subscription approval or direct Robux payouts.

## 7. Creator Rewards

Creator Rewards is a platform program rather than an in-experience purchase API. As documented on 2026-07-13, it has two parts:

- **Daily Engagement Rewards:** 5 Robux when an Active Spender spends at least 10 minutes in the experience during a day and the experience is one of the first three they launch that day.
- **Audience Expansion Rewards:** a 35% revenue share on the first $100 of qualifying purchases by an attributed New User or Reactivated User during their first 60 days, subject to the experience's 10-minute, attribution, and average-100-DAU-for-60-days conditions.

Creator Rewards data is surfaced in Creator Dashboard and has a 60-day holding period. There is no server callback that grants the reward to a player and no purchase receipt to process. Do not make Creator Rewards the source of truth for coins, products, or player entitlements.

Treat the program terms as changeable policy. Do not automate engagement, manipulate teleports, encourage alternate accounts, or design an idle loop solely to manufacture reward activity. Review the current eligibility, anti-fraud, and DevEx terms before making a business or content decision.

## 8. Economy design

Monetization changes the economy even when the product is cosmetic:

- faucets increase supply;
- sinks remove supply;
- multipliers change time-to-earn;
- tradeable rewards can create secondary markets;
- limited offers can concentrate demand and support load.

Model the ordinary player path before choosing prices. Track purchases and grants separately so an analytics event cannot become the source of truth for inventory.

## 9. Testing matrix

Test in a non-production place with representative data:

- prompt cancelled;
- ownership API errors;
- unknown product id;
- player leaves before receipt processing;
- receipt callback called twice;
- grant succeeds but receipt recording fails;
- save or shutdown begins during a grant;
- subscription entitlement changes;
- policy lookup denies or cannot determine eligibility.
- Creator Rewards eligibility and dashboard reporting reviewed when the experience is relying on it.

Keep test product IDs and test entitlements out of production configuration.

## Monetization checklist

- [ ] Prompting is client-side, granting is server-side.
- [ ] Receipt routing has one owner per product/type; passes share a benefit reconciler.
- [ ] Grants are idempotent and receipt identifiers are recorded.
- [ ] Product configuration is trusted server data.
- [ ] Policy and eligibility checks use current official documentation.
- [ ] Prices, cadence, contents, and disclosures are visible before purchase.
- [ ] Failures leave the receipt retryable instead of silently acknowledging it.

## Catalog eligibility and deferred fulfilment

### Separate catalog and purchase states

Define display, selection, acquisition, purchase, ownership, and equip eligibility separately. An earn-only reward can remain visible with its actual acquisition path while the server rejects an invalid purchase. Test card creation, retained selection, action labels, ownership changes, and equipping together; a hidden card cannot exercise its existing acquisition-button code.

### Isolate optional diagnostics

Optional telemetry must not break an authoritative grant, trigger a duplicate grant, or cause an owed entitlement to disappear. Keep grant/idempotency state inside its established durable transaction boundary and isolate diagnostic failures from that result. Inject a telemetry failure into the purchase test; a successful counter test does not verify grant safety.

### Settle delayed entitlements deliberately

Model reserved, started, confirmed-delivered, cancelled, and recoverable states for paid effects. Identify operations bought with saved credits as well as those with receipt IDs; retries and duplicate callbacks must find the same authoritative operation.

Define the effect-delivery boundary and the recovery policy for a started operation whose outcome is unknown. Do not promise exactly-once world execution when effect delivery and persistence cannot commit atomically. Do not refund merely because the buyer leaves if an already-running effect can still complete. Do not mark an effect delivered after shutdown cancellation prevented it from running.

Test disconnect before and after start, explicit cancellation, duplicate completion, crash-left saved state, rejoin recovery, and shutdown ordering. Verify the actual owed entitlement after each case through the real save validator and grant owner; see `roblox-data`. Keep fulfilment of the game's owed item or credit distinct from a platform payment refund.
