# roblox monetization: full reference

This guide focuses on the server-side correctness of Roblox's purchase APIs. Product catalog setup and current policy requirements change over time; use the linked Creator Hub pages as the authority for eligibility and configuration details.

## 1. Pick the product type

- **Pass:** durable ownership for an experience.
- **Developer Product:** repeatable consumable purchase.
- **Subscription:** recurring benefit with a subscription-specific lifecycle.
- **Private server or paid access:** access configuration rather than an item grant.
- **Creator Rewards and ads:** platform programs with their own eligibility and reporting rules.

Do not model all of these as one “purchase” table. Their ownership, renewal, refund, and retry behavior differ.

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

local function ownsPass(player: Player, passId: number): boolean
    local ok, owns = pcall(function()
        return MarketplaceService:UserOwnsGamePassAsync(player.UserId, passId)
    end)
    return ok and owns == true
end
```

Cache a successful result when appropriate, but provide an invalidation or refresh path for purchases made during the session. Handle API failure as “not confirmed yet,” not as a permanent denial or grant.

## 3. Centralize Developer Product receipts

Only one server callback should own `ProcessReceipt`. It must:

1. identify the product and player;
2. determine whether this receipt was already granted;
3. grant through the authoritative data service;
4. record the receipt or transaction id with the grant;
5. return `PurchaseGranted` only after durable success.

```luau
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local handlers = {
    [COIN_PRODUCT_ID] = function(player: Player)
        return EconomyService:AddCoins(player, 500)
    end,
}

MarketplaceService.ProcessReceipt = function(receiptInfo)
    local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local productHandler = handlers[receiptInfo.ProductId]
    if not productHandler then
        warn("Unhandled product", receiptInfo.ProductId)
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local transactionId = tostring(receiptInfo.PurchaseId)
    if ReceiptStore:WasGranted(transactionId) then
        return Enum.ProductPurchaseDecision.PurchaseGranted
    end

    local ok = productHandler(player)
    if not ok then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    if not ReceiptStore:RecordGrant(transactionId, player.UserId) then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end
    return Enum.ProductPurchaseDecision.PurchaseGranted
end
```

The order between granting and recording must match the project's persistence guarantees. If a grant and receipt record cannot be made atomic, make the grant idempotent so a retry cannot duplicate value.

## 4. Subscriptions and recurring benefits

Subscriptions need explicit entitlement checks and renewal handling. Keep these separate from one-time Game Pass ownership. A subscription benefit should have:

- a server-side entitlement check;
- a clear expiration or renewal state;
- behavior when the subscription API is unavailable;
- a downgrade path that does not delete unrelated player data;
- UI that describes the actual cadence and benefit.

Use the current subscription documentation for API names and platform eligibility. Do not hard-code assumptions about age, region, or payment availability.

## 5. Private servers and paid access

Private-server prompts, paid access, and item purchases solve different problems. Decide whether the player is buying access, a server instance, or an in-game entitlement. Keep access enforcement on the server and test owners, invited players, and expired or unavailable configurations.

## 6. Policy and presentation

Eligibility-sensitive products may require `PolicyService` checks. Treat a failed policy lookup conservatively for the affected feature, and update the implementation when Roblox changes the documented requirements.

Purchase UI should make the price, cadence, contents, and meaningful restrictions clear. For randomized paid content, implement the disclosure and eligibility rules in the current Roblox policy documentation before release. Do not rely on a color, rarity label, or marketing phrase as a substitute for a required disclosure.

Platform program names and payout rules change. Engagement-Based Payouts is historical/deprecated material, not a current implementation target; consult the current Creator Rewards documentation when working on platform payouts.

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
- [ ] There is one receipt callback and a product dispatch table.
- [ ] Grants are idempotent and receipt identifiers are recorded.
- [ ] Product configuration is trusted server data.
- [ ] Policy and eligibility checks use current official documentation.
- [ ] Prices, cadence, contents, and disclosures are visible before purchase.
- [ ] Failures leave the receipt retryable instead of silently acknowledging it.
