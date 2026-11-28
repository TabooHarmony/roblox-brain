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

Test existing ownership on join, a trial start and its session end, a crash and rejoin within the hour (the trial continues) versus a normal leave, purchase during a trial, purchase/cancel in-session, a query failure, repeated refresh, character respawn, player leave during the query, and two passes contributing to one benefit. Centralization removes duplicate plumbing, not product-specific rules or server validation. Repeated trials through alternate accounts were raised in the [free trials thread](https://devforum.roblox.com/t/introducing-pass-free-trials/4995943) (2026-11-25): never tie irreversible rewards to a trial-time ownership check.

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

## 8a. Built-in Shop, outside-the-game sales, and refunds (official)

<!-- temporal: 2026-11 -->

**The Roblox Shop.** `MarketplaceService:OpenShop(player)` opens the personalized in-game Shop overlay.

- Call it from a server Script, or from a LocalScript for the local player only, in response to a user action.
- Configure it in Creator Hub > Monetization > Shop:
  - Passes are always listed.
  - Developer products can be Listed or Unlisted. Unlisted products can still be bought through your own flows.
- Hide the menu entry with `StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.ExperienceShop, false)`. A global Shop button exists and is off by default.
- Standard earnings apply.
- Pass free trials start from the Shop's Try button. There's no API to start a trial from your own UI (staff reply, [free trials thread](https://devforum.roblox.com/t/introducing-pass-free-trials/4995943), 2026-11-18). Don't invent one; the trial rules are in §2a.

**Selling outside the game.** Listed developer products and passes can appear on Home, in search, and on the page after a Robux purchase. The buyer may not be in your game when they pay.

- Roblox continuously checks that `ProcessReceipt` grants correctly. A flagged product loses only its outside-the-game eligibility, and a Creator Hub banner and report lead to "Mark as fixed".
- Never grant from `PromptProductPurchaseFinished`. A receipt handler only fires while the user is on a server, so grant on their next join through the receipt path (§3).
- Developer product icons: at most 512×512, with important detail inside the circle crop. Prices range from 1 to 1 billion Robux.
- Passes can only be prompted in their own game.

**Refunds.** The **Transaction Refunded** webhook covers developer products, passes, private servers, and paid access. It doesn't cover subscriptions, which have their own **Subscription Refunded** trigger.

- Roblox revokes passes and avatar items automatically.
- Developer product benefits are yours to remove. Key the reversal on the transaction id, and make it idempotent.
- Setup details: `roblox-cloud` §8.9.

## 8b. Offer integrity (measured across reviewed kits)

Teardowns of 59 simulator games and kits found the same defects again and again. Audit for them before every release:

- **More than one script assigning `ProcessReceipt`.** Only the last assignment wins. Grep the whole place for every assignment and every product id, keep one receipt router keyed by product id, and never reuse one id for two products.
- **Client-granted rewards.** Watch for code that grants on the client's purchase-success signal, or spin rewards chosen on the client. Choose every random reward on the server. Opening animations wait for the server's result, then build the reel around the actual pull.
- **Labels that disagree with grants.** Examples: "+300 storage" added 30, a "2x cash" flag was ignored by the server multiplier, and a "FREE" button opened a purchase prompt. Keep one server-backed product definition that drives the offer text, price, handler, and grant, and test each purchase end to end against its label.
- **Displayed odds that disagree with the roll.** One kit showed 40/60/80% while it rolled 25/33/50%, weights summed to 102%, and "guaranteed in 12" had no server pity counter. Generate displayed odds from the server table, and assert in a test that they sum to 100% and match each weight.
- **Off-sale passes still shown.** A shop built from local data keeps showing passes that are off sale, and Roblox then refuses the prompt. Read live `IsForSale` and price with `GetProductInfo`, and hide off-sale items. Developer products can't be deleted, so retire them off sale and never re-create one under the same name.

**Policy coverage (official).**

- Random items bought with a currency that players can also buy with Robux are paid random items. That includes keys, rerolls, and spin tickets. Show every outcome's actual odds before the spend.
- Where `ArePaidRandomItemsRestricted` is true, apply the restricted treatment to both purchase paths. If the policy lookup fails, refuse the paid path.
- Containers earned only through play need no odds disclosure. Keep opening them working everywhere, and replace only the buy row with a note.
- If paid items can be traded, also gate trading on `IsPaidItemTradingAllowed`.

**Gifting.** Never take the recipient's UserId from the client with the purchase.

- Store the chosen recipient on the server, keyed to the buyer, before you prompt. Read it back in the receipt handler.
- Validate that the recipient exists and is eligible.
- Record the grant against the receipt.
- Keep a pending-gift record so offline recipients get the gift when they next join.

**Paid effects outside the save.** A receipt grant must not yield, prompt, or wait on the player.

- For timed effects (a server boost, a revive), have the grant queue a durable delivery record in the profile.
- Mark the record started when the effect begins, and completed or refunded when it ends.
- After a crash, the record refunds instead of replaying.

**Server-wide paid effects.** Of the 59 reviewed games, 23 sold one. The pro-social form is a timed luck or XP boost (often 15 minutes) that helps everyone in the server and names the buyer. Avoid selling disruption to other players, such as a paid "nuke" or a lethal hazard, and keep paid effects out of competitive rounds (`roblox-player-psychology`).

**Prompt placement (measured in one game).** Prompts that opened when a player tried something, such as equipping a locked item at a stand, were closed by reflex. Over three days, 647 prompts closed a median 1.7 s after opening, with no sales. Open a Robux prompt only from a deliberate priced button, and give the "try" action a preview. Log the time from prompt to close per placement.

Where offers appeared across the same 59 reviews (counts overlap, and prevalence isn't conversion):

| Offer | Games |
|---|---|
| Physical in-world shop or pad | 47 |
| Paid skip, rebirth, or instant-finish family | 34 |
| Limited or countdown indicator | 25 |
| Paid server-wide effect | 23 |
| Paid gifting | 14 |
| Prompt when the player can't afford something | 12 |
| Join, timer, or return offers | 10 |

The stronger triggers followed a milestone, such as a starter pack after the first big deposit or a double-cash offer after the second rebirth. Shortfall prompts carry dark-pattern risk.

**Social rewards.**

- `AvatarEditorService:PromptSetFavorite` can't prove that a player favorited the game. Pay a favorite reward once ever.
- Games can't read likes.
- For group-join rewards, re-check a negative `IsInGroup` with `GroupService:GetGroupsAsync(userId)`. Server lookups were observed to cache for about a minute.
- Gate these rewards on account age, and rate-limit the remote.

**Environments.** A developer product can only be bought in the universe that owns it (observed), so keep one generated id module per universe. Managed regional pricing was refused on a dev universe (`InvalidManagedPricing`), so offers there sell at list price. Add a test that fails when offer-config prices and catalog prices disagree.

**Price tests.** Create a second "slot" product at the test price that grants exactly like the original.

- Assign arms with a stable hash of the test id and UserId.
- Keep past buyers in the control arm.
- Read prices with `GetProductInfo`, and show a placeholder until it answers.
- Roblox Experiments can drive the split instead (`roblox-growth-design`).

## 8c. Rewarded video (official)

Rewarded video is a full-screen ad of 6–30 s that grants a reward. Roblox's playbook recommends:

- **Opt-in.** Show the reward first, then offer opt in, skip, or pay.
- **Moments of need.** Use natural breaks: after a defeat, at the end of a level, on wait screens.
- **Length.** Aim for 15–30 s for in-game ads.
- **Rewards.** Meaningful, consumable, repeatable: boosters, currency, extra lives.

Types: Join with Reward (before entering), the Rewarded Video Billboard template, and in-game prompts in the HUD or menus.

- Protect purchase revenue by hiding ads from likely spenders.
- Estimate earnings in Creator Hub > Ads > Eligibility.
- Test the effect on retention and spend with an experiment.

Self-audit before launch:

- Is the prompt visible soon after its trigger?
- Is there more than one reward type?
- Is the frequency cap at least 2–3 prompts per session?
- Are the rewards consumable?
- Is the prompt near the core loop?

## 8d. Earnings, DevEx, and tax (official)

<!-- temporal: 2026-11 -->

- **Standard DevEx rate:** 0.0038 USD per Earned Robux ($114 per 30,000). It was 0.0035 before September 5, 2025.
- **U.S. 18+ rate: 0.0054**, effective June 8, 2026. It applies to developer products, passes, subscriptions, and private servers bought by age-verified U.S. adults.
  - Player characters must be R15 (standard or advanced) or a qualifying custom form for 100% of active playtime, with R15 animation packs.
  - Any R6 at any point disqualifies the game, so set Avatar Settings to R15 Only. Games without a visible character count as nonhuman, and NPCs are exempt.
  - A background compliance check enforces this. Group payouts respect the rate.
- **Tax:** DevEx payments are royalties.
  - U.S. creators without a valid W-9 face 24% backup withholding.
  - Non-U.S. creators file W-8BEN or W-8BEN-E and see 0–30% withholding on payments tied to U.S. sales, depending on treaty, or 24% backup withholding if their tax information is invalid.
  - Payouts arrive net through Tipalti. Forms 1099-MISC, 1099-NEC, and 1042-S are downloadable.
  - This isn't tax advice; consult a professional.

Sources for §8a–8d: [Shop](https://create.roblox.com/docs/production/monetization/shop), [Developer products](https://create.roblox.com/docs/production/monetization/developer-products), [Webhook notifications](https://create.roblox.com/docs/cloud/webhooks/webhook-notifications), [Rewarded video playbook](https://create.roblox.com/docs/production/promotion/rewarded-video-playbook), [Developer Exchange](https://create.roblox.com/docs/production/monetization/developer-exchange), [U.S. 18+ DevEx rate](https://create.roblox.com/docs/production/monetization/18-plus-devex-rate), [Tax information](https://create.roblox.com/docs/production/monetization/tax-information), [Paid random items](https://create.roblox.com/docs/production/monetization/paid-random-items).

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
