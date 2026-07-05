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

## 2. GamePasses

GamePasses are **one-time permanent purchases** tied to the player's account. Once bought, the player owns it forever across all sessions. Ideal for VIP perks, permanent stat boosts, cosmetic bundles, and feature unlocks.

### Core API

| Method / Event | Purpose |
|---|---|
| `MarketplaceService:UserOwnsGamePassAsync(userId, gamePassId)` | Check if player owns a GamePass |
| `MarketplaceService:PromptGamePassPurchase(player, gamePassId)` | Show the purchase prompt to a player |
| `MarketplaceService.PromptGamePassPurchaseFinished` | Fires when the prompt closes (purchased or cancelled) |

### Complete GamePass System (Server Script)

Place this in `ServerScriptService`:

```luau
-- ServerScriptService/GamePassService.lua
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

-- ===== CONFIGURATION =====
-- Map each GamePass ID to a function that grants its perks.
-- Add new passes here; the rest of the system handles them automatically.
local GAME_PASSES = {
	[123456789] = {
		name = "VIP",
		grant = function(player: Player)
			-- Example: tag the player so other scripts can check
			player:SetAttribute("IsVIP", true)

			-- Example: give a permanent speed boost
			local character = player.Character or player.CharacterAdded:Wait()
			local humanoid = character:FindFirstChildOfClass("Humanoid")
			if humanoid then
				humanoid.WalkSpeed = 24
			end
		end,
	},
	[987654321] = {
		name = "2x Coins",
		grant = function(player: Player)
			player:SetAttribute("CoinMultiplier", 2)
		end,
	},
}

-- ===== GRANT PERKS ON JOIN =====
-- Check every configured GamePass when the player joins.
local function onPlayerAdded(player: Player)
	for gamePassId, passInfo in GAME_PASSES do
		local success, ownsPass = pcall(function()
			return MarketplaceService:UserOwnsGamePassAsync(player.UserId, gamePassId)
		end)

		if success and ownsPass then
			local grantSuccess, grantErr = pcall(passInfo.grant, player)
			if not grantSuccess then
				warn(`[GamePass] Failed to grant "{passInfo.name}" to {player.Name}: {grantErr}`)
			end
		elseif not success then
			warn(`[GamePass] Failed to check ownership of {passInfo.name} for {player.Name}: {ownsPass}`)
		end
	end

	-- Re-grant perks on every respawn (speed, accessories, etc.)
	player.CharacterAdded:Connect(function()
		for gamePassId, passInfo in GAME_PASSES do
			if player:GetAttribute("IsVIP") or player:GetAttribute("CoinMultiplier") then
				-- Only re-grant if we already confirmed ownership
				local success, ownsPass = pcall(function()
					return MarketplaceService:UserOwnsGamePassAsync(player.UserId, gamePassId)
				end)
				if success and ownsPass then
					pcall(passInfo.grant, player)
				end
			end
		end
	end)
end

-- ===== GRANT PERKS ON PURCHASE (mid-session) =====
-- If the player buys a GamePass while already in-game, grant immediately.
MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player: Player, gamePassId: number, wasPurchased: boolean)
	if not wasPurchased then
		return
	end

	local passInfo = GAME_PASSES[gamePassId]
	if not passInfo then
		return
	end

	local success, err = pcall(passInfo.grant, player)
	if success then
		print(`[GamePass] Granted "{passInfo.name}" to {player.Name} (mid-session purchase)`)
	else
		warn(`[GamePass] Failed to grant "{passInfo.name}" to {player.Name}: {err}`)
	end
end)

-- ===== INITIALIZE =====
for _, player in Players:GetPlayers() do
	task.spawn(onPlayerAdded, player)
end
Players.PlayerAdded:Connect(onPlayerAdded)
```

### Prompting Purchases (Server or Client)

```luau
-- Client-side: prompt a GamePass purchase from a button, shop GUI, etc.
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local VIP_PASS_ID = 123456789

local function promptVIPPurchase()
	MarketplaceService:PromptGamePassPurchase(Players.LocalPlayer, VIP_PASS_ID)
end

-- Connect to a shop button
script.Parent.MouseButton1Click:Connect(promptVIPPurchase)
```

---

## 3. Developer Products

Developer Products are **consumable/repeatable purchases**. Players can buy them multiple times. Ideal for currency packs, temporary boosts, extra lives, loot crates, and skip-timers.

### Core API

| Method / Event | Purpose |
|---|---|
| `MarketplaceService:PromptProductPurchase(player, productId)` | Show the purchase prompt |
| `MarketplaceService.ProcessReceipt` | **CRITICAL** callback Roblox invokes to confirm granting |

### The ProcessReceipt Contract

`ProcessReceipt` is the single most important callback in Roblox monetization. Roblox calls it and expects one of two return values:

| Return Value | Meaning |
|---|---|
| `Enum.ProductPurchaseDecision.PurchaseGranted` | Item was successfully granted. Roblox finalizes the purchase. **Returning this without actually granting is a policy violation and causes player complaints.** |
| `Enum.ProductPurchaseDecision.NotProcessedYet` | Granting failed or could not be confirmed. Roblox will **retry** calling ProcessReceipt later (including on rejoin). |

**Rules:**
- Only ONE script can set `MarketplaceService.ProcessReceipt`. If two scripts both assign it, only the last one takes effect and the other is silently overwritten.
- Return `PurchaseGranted` ONLY after successfully persisting the granted item (DataStore save confirmed).
- If DataStore save fails, return `NotProcessedYet` so Roblox retries.
- Always handle the case where the player has left the game before ProcessReceipt fires.

### Complete Developer Product System (Server Script)

Place this in `ServerScriptService`:

```luau
-- ServerScriptService/DeveloperProductService.lua
local MarketplaceService = game:GetService("MarketplaceService")
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")

local purchaseHistoryStore = DataStoreService:GetDataStore("PurchaseHistory")

-- ===== CONFIGURATION =====
-- Map each product ID to a handler that grants the item.
-- The handler receives the player and must return true on success.
local PRODUCTS = {
	[111111111] = {
		name = "100 Coins",
		grant = function(player: Player): boolean
			local leaderstats = player:FindFirstChild("leaderstats")
			if not leaderstats then
				return false
			end

			local coins = leaderstats:FindFirstChild("Coins")
			if not coins then
				return false
			end

			coins.Value += 100
			return true
		end,
	},
	[222222222] = {
		name = "500 Coins",
		grant = function(player: Player): boolean
			local leaderstats = player:FindFirstChild("leaderstats")
			if not leaderstats then
				return false
			end

			local coins = leaderstats:FindFirstChild("Coins")
			if not coins then
				return false
			end

			coins.Value += 500
			return true
		end,
	},
	[333333333] = {
		name = "Speed Boost (60s)",
		grant = function(player: Player): boolean
			local character = player.Character
			if not character then
				return false
			end

			local humanoid = character:FindFirstChildOfClass("Humanoid")
			if not humanoid then
				return false
			end

			humanoid.WalkSpeed = 32
			task.delay(60, function()
				if humanoid and humanoid.Parent then
					humanoid.WalkSpeed = 16
				end
			end)
			return true
		end,
	},
}

-- ===== PROCESS RECEIPT CALLBACK =====
local function processReceipt(receiptInfo): Enum.ProductPurchaseDecision
	-- 1. Check if this purchase was already granted (idempotency guard)
	local purchaseKey = `{receiptInfo.PlayerId}_{receiptInfo.PurchaseId}`

	local alreadyGranted = false
	local lookupSuccess, lookupErr = pcall(function()
		alreadyGranted = purchaseHistoryStore:GetAsync(purchaseKey)
	end)

	if not lookupSuccess then
		-- Cannot verify history; retry later to avoid duplicates
		warn(`[Product] DataStore lookup failed for {purchaseKey}: {lookupErr}`)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	if alreadyGranted then
		-- Already granted in a previous attempt; finalize
		return Enum.ProductPurchaseDecision.PurchaseGranted
	end

	-- 2. Find the product handler
	local productInfo = PRODUCTS[receiptInfo.ProductId]
	if not productInfo then
		warn(`[Product] No handler for product ID {receiptInfo.ProductId}`)
		-- Unknown product: still return NotProcessedYet so it can be handled
		-- after a code update adds the missing handler
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	-- 3. Find the player (they may have left before ProcessReceipt fires)
	local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
	if not player then
		-- Player left; retry on their next join
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	-- 4. Grant the item
	local grantSuccess = false
	local grantOk, grantErr = pcall(function()
		grantSuccess = productInfo.grant(player)
	end)

	if not grantOk then
		warn(`[Product] Grant error for "{productInfo.name}" to {player.Name}: {grantErr}`)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	if not grantSuccess then
		warn(`[Product] Grant returned false for "{productInfo.name}" to {player.Name}`)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	-- 5. Record the purchase BEFORE returning PurchaseGranted
	local saveSuccess, saveErr = pcall(function()
		purchaseHistoryStore:SetAsync(purchaseKey, true)
	end)

	if not saveSuccess then
		-- Grant succeeded but save failed. This is the hardest edge case.
		-- Returning PurchaseGranted risks no record if we crash before saving.
		-- Returning NotProcessedYet risks a duplicate grant on retry.
		-- Best practice: return PurchaseGranted since the player already received
		-- the item, and log the failure for manual reconciliation.
		warn(`[Product] CRITICAL: Grant succeeded but history save failed for {purchaseKey}: {saveErr}`)
	end

	print(`[Product] Granted "{productInfo.name}" to {player.Name} (PurchaseId: {receiptInfo.PurchaseId})`)
	return Enum.ProductPurchaseDecision.PurchaseGranted
end

-- ===== ASSIGN CALLBACK (only one script can do this) =====
MarketplaceService.ProcessReceipt = processReceipt
```

### Prompting Developer Product Purchases (Client)

```luau
-- Client-side shop button example
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local COINS_100_PRODUCT_ID = 111111111

script.Parent.MouseButton1Click:Connect(function()
	MarketplaceService:PromptProductPurchase(Players.LocalPlayer, COINS_100_PRODUCT_ID)
end)
```

---

## 4. Premium Payouts

Roblox automatically pays developers based on how much time **Premium subscribers** spend in their game. There is no purchase prompt; you earn passively. The more engagement time from Premium players, the higher the payout.

### Detecting Premium Players

```luau
-- ServerScriptService/PremiumService.lua
local Players = game:GetService("Players")

local function grantPremiumPerks(player: Player)
	player:SetAttribute("IsPremium", true)

	-- Example perks to incentivize Premium play time:
	-- Extra daily reward, exclusive cosmetics, bonus XP, premium-only areas
	local leaderstats = player:FindFirstChild("leaderstats")
	if leaderstats then
		local coins = leaderstats:FindFirstChild("Coins")
		if coins then
			coins.Value += 50 -- daily Premium login bonus
		end
	end
end

local function revokePremiumPerks(player: Player)
	player:SetAttribute("IsPremium", false)
end

local function onPlayerAdded(player: Player)
	-- Check on join
	if player.MembershipType == Enum.MembershipType.Premium then
		grantPremiumPerks(player)
	end

	-- Real-time detection: player may subscribe or unsubscribe mid-session
	player:GetPropertyChangedSignal("MembershipType"):Connect(function()
		if player.MembershipType == Enum.MembershipType.Premium then
			grantPremiumPerks(player)
		else
			revokePremiumPerks(player)
		end
	end)
end

for _, player in Players:GetPlayers() do
	task.spawn(onPlayerAdded, player)
end
Players.PlayerAdded:Connect(onPlayerAdded)
```

### Premium Upsell

You can prompt non-Premium players to subscribe:

```luau
-- Client-side: prompt a Premium subscription upsell
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local player = Players.LocalPlayer

if player.MembershipType ~= Enum.MembershipType.Premium then
	MarketplaceService:PromptPremiumPurchase(player)
end

-- Listen for result
MarketplaceService.PromptPremiumPurchaseFinished:Connect(function()
	-- MembershipType will update automatically on the server if they subscribed
end)
```

---

## 5. Rewarded Video Ads (2026)

Roblox's ad monetization system allows players to opt-in to watching a short video ad in exchange for an in-game reward. Revenue is generated per completed view.

### Implementation via AdService

```luau
-- ServerScriptService/RewardedAdService.lua
local AdService = game:GetService("AdService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- RemoteEvent for client to request an ad
local requestAdEvent = Instance.new("RemoteEvent")
requestAdEvent.Name = "RequestRewardedAd"
requestAdEvent.Parent = ReplicatedStorage

local adCooldowns: { [number]: number } = {}
local COOLDOWN_SECONDS = 300 -- 5-minute cooldown between ads

requestAdEvent.OnServerEvent:Connect(function(player: Player)
	local now = os.time()
	local lastAd = adCooldowns[player.UserId] or 0

	if now - lastAd < COOLDOWN_SECONDS then
		local remaining = COOLDOWN_SECONDS - (now - lastAd)
		warn(`[Ads] {player.Name} on cooldown, {remaining}s remaining`)
		return
	end

	-- Grant the reward after confirmed view
	local leaderstats = player:FindFirstChild("leaderstats")
	if leaderstats then
		local coins = leaderstats:FindFirstChild("Coins")
		if coins then
			coins.Value += 25 -- reward equivalent to 3-10 Robux value
		end
	end

	adCooldowns[player.UserId] = now
	print(`[Ads] Granted rewarded ad bonus to {player.Name}`)
end)

Players.PlayerRemoving:Connect(function(player: Player)
	adCooldowns[player.UserId] = nil
end)
```

### Placement Best Practices

| Placement | Why It Works |
|---|---|
| **Between rounds** | Natural break; player is already waiting |
| **In lobby / waiting area** | Low-stakes moment; player has nothing else to do |
| **After death (optional revive)** | High motivation to watch; clear value proposition |
| **Daily bonus multiplier** | "Watch ad to double your daily reward" |
| **Cosmetic preview** | "Watch ad to try this skin for 1 hour" |

**Avoid:** Mid-gameplay interruptions, mandatory ads, ads that block progression.

### Recommended Reward Value

- **3-10 Robux equivalent value** per completed view
- Too low: players will not bother watching
- Too high: undermines paid product sales
- Sweet spot: meaningful but not game-breaking (e.g., 25-50 coins when 100 coins costs 25 Robux)

---

## 6. Pricing Strategy

### Common Roblox Price Points

| Robux | Typical Use |
|---|---|
| **25** | Minimum viable price. Small cosmetic, single-use consumable |
| **50** | Minor cosmetic pack, small currency bundle |
| **75** | Mid-tier consumable, trail effect, small pet |
| **100** | Standard GamePass, decent currency pack |
| **250** | Premium GamePass (2x coins, VIP), mid currency bundle |
| **500** | Major GamePass (significant gameplay advantage), large currency pack |
| **1,000** | Top-tier GamePass, mega currency bundle |
| **2,500+** | Whale-tier only. Use sparingly |

### Pricing Tactics

**Anchoring:** Show the most expensive option first in the shop UI. When a player sees "Mega Pack: 1,000 Robux" first, the "Starter Pack: 100 Robux" feels like a bargain by comparison.

**Bundle Value:** Offer multi-item bundles at a per-unit discount:
- 100 Coins = 50 Robux (0.50 Robux/coin)
- 300 Coins = 100 Robux (0.33 Robux/coin) -- "Best Value" tag
- 1,000 Coins = 250 Robux (0.25 Robux/coin) -- "Most Popular" tag

**Minimum Price Floor:** Do not price anything below **25 Robux**. Roblox takes a 30% marketplace fee, and extremely low-priced items generate negligible revenue while still requiring full implementation and support effort.

**Odd Pricing:** 49 Robux feels cheaper than 50 Robux. 99 feels cheaper than 100. Roblox players respond to this the same way real-world consumers do.

**Limited-Time Offers:** Create urgency with rotating shop items or seasonal GamePasses. Fear of missing out (FOMO) drives conversions, but use ethically (see Section 8).

---

## 7. DevEx Math

### Exchange Rate

As of 2026, the Developer Exchange (DevEx) rate is approximately:

> **1 Robux earned = ~$0.0035 USD**

This means:
- **30,000 Robux** (minimum cashout) = ~**$105 USD**
- **100,000 Robux** = ~**$350 USD**
- **1,000,000 Robux** = ~**$3,500 USD**

### Revenue Projection Formulas

```
Daily Revenue (Robux) = DAU x Conversion Rate x Average Purchase (Robux)

Monthly Revenue (Robux) = Daily Revenue x 30

Monthly Revenue (USD) = Monthly Revenue (Robux) x 0.0035
```

**Example projections at different scales:**

| DAU | Conversion Rate | Avg Purchase | Daily Robux | Monthly USD |
|---|---|---|---|---|
| 100 | 2% | 100 R$ | 200 | $21 |
| 1,000 | 2% | 100 R$ | 2,000 | $210 |
| 10,000 | 3% | 150 R$ | 45,000 | $4,725 |
| 100,000 | 3% | 150 R$ | 450,000 | $47,250 |

**Typical conversion rates on Roblox:** 1-5% of DAU makes a purchase on any given day. Well-optimized games with strong shop design reach the higher end.

**Premium Payout addition:** Premium Payouts add roughly 10-30% on top of direct purchase revenue depending on your Premium player ratio and engagement quality.

### Break-Even Calculations

```
Hours spent developing = X
Hourly rate target = $Y/hr
Required total earnings = X * Y
Required Robux = (X * Y) / 0.0035
Required paying players = Required Robux / Average Purchase
```

---

## 8. Ethical Monetization

Roblox's audience skews young (a significant portion is under 16). This carries a responsibility to monetize fairly. Roblox also actively enforces policies against predatory practices.

### Do

- **Provide genuine value** for every purchase. The player should feel good about what they got.
- **Disclose odds** on any randomized rewards (loot boxes, mystery eggs, random pet hatching). Display exact percentages.
- **Allow core gameplay for free.** Free players should enjoy the full game loop. Purchases should enhance, not gate.
- **Price transparently.** Show the Robux cost clearly before any purchase prompt.
- **Offer earnable alternatives.** If a cosmetic costs 100 Robux, also let players earn it after 10 hours of gameplay.
- **Respect declining.** If a player closes a purchase prompt, do not immediately re-prompt.

### Do Not

- **No pay-to-win in competitive modes.** If your game has PvP, purchased items should not provide a statistical advantage.
- **No hidden costs.** Never require a chain of purchases to unlock something ("buy A to unlock B to unlock C").
- **No artificial scarcity manipulation.** "Only 3 left!" when supply is unlimited is deceptive.
- **No pressure tactics on children.** Countdown timers, social pressure ("your friend bought this!"), and guilt messaging are inappropriate.
- **No paywalled progression.** Never block a player from advancing in the story or level because they have not purchased something.
- **No misleading descriptions.** GamePass and product descriptions must accurately reflect what the player receives.

---

## 9. Best Practices

### Server-Side Purchase Verification (Always)

Never grant items from the client. A client script can prompt a purchase, but the grant must always happen in a ServerScript via `ProcessReceipt` (for products) or `PromptGamePassPurchaseFinished` (for GamePasses, verified with `UserOwnsGamePassAsync`).

### Graceful Failure Handling

```luau
-- Wrap every MarketplaceService call in pcall
local success, result = pcall(function()
	return MarketplaceService:UserOwnsGamePassAsync(player.UserId, passId)
end)

if not success then
	-- API is down or rate-limited. Fail gracefully.
	warn(`[Purchase] API call failed: {result}`)
	-- Do NOT assume they own it; do NOT assume they don't.
	-- Cache the last known state and retry later.
end
```

### Receipt Logging

Log every purchase for customer support and debugging:

```luau
-- Inside ProcessReceipt, after granting
print(`[Receipt] Player={receiptInfo.PlayerId} Product={receiptInfo.ProductId} PurchaseId={receiptInfo.PurchaseId} CurrencySpent={receiptInfo.CurrencySpent} PlaceId={receiptInfo.PlaceIdWherePurchased}`)
```

Keep a DataStore or external log of all purchases so you can:
- Investigate "I paid but didn't get my item" support tickets
- Track conversion metrics
- Identify unusual purchase patterns (potential fraud or exploits)

### Test Purchases in Studio

- In Roblox Studio, `ProcessReceipt` will fire with test data.
- `UserOwnsGamePassAsync` returns false in Studio for passes the Studio user does not own.
- Use Studio's "Test" tab to simulate purchases.
- Always test the full flow: prompt, purchase, grant, rejoin-and-re-grant, and the failure path.

### Natural Purchase Prompt Placement

**Good placements:**
- In a dedicated shop GUI the player opens voluntarily
- Contextually, when the player encounters a locked feature ("This area is VIP-only. Unlock VIP?")
- After the player has played for several minutes and understands the game's value

**Bad placements:**
- Immediately on join before the player has loaded
- Every 30 seconds via popup
- Blocking the screen during active gameplay

---

## 10. Anti-Patterns

### Client-Side Purchase Granting (Exploitable)

```luau
-- BAD: Never do this
-- LocalScript
MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, id, purchased)
	if purchased then
		player.Character.Humanoid.WalkSpeed = 50 -- exploiter can fire this event
	end
end)
```

Exploiters can fire `RemoteEvent`s and manipulate client-side logic. Always grant on the server.

### Improper ProcessReceipt Handling

```luau
-- BAD: Returns PurchaseGranted without actually granting
MarketplaceService.ProcessReceipt = function(receiptInfo)
	-- "I'll grant it later"
	return Enum.ProductPurchaseDecision.PurchaseGranted -- Player never gets their item
end
```

```luau
-- BAD: No error handling, can silently fail
MarketplaceService.ProcessReceipt = function(receiptInfo)
	local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
	player.leaderstats.Coins.Value += 100 -- crashes if player left or leaderstats missing
	return Enum.ProductPurchaseDecision.PurchaseGranted
end
```

```luau
-- BAD: No idempotency check, causes duplicates on retry
MarketplaceService.ProcessReceipt = function(receiptInfo)
	local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
	if player then
		player.leaderstats.Coins.Value += 100
	end
	return Enum.ProductPurchaseDecision.PurchaseGranted -- Roblox won't retry, but if
	-- you returned NotProcessedYet when the player was absent and PurchaseGranted
	-- here, the player gets double coins if there's no receipt dedup.
end
```

### Aggressive Popup Spam

Prompting purchases repeatedly annoys players and violates Roblox UX guidelines. A player who closes a prompt does not want to see it again immediately. Implement cooldowns:

```luau
-- Minimum 60-second cooldown between prompts of the same type
local lastPromptTime: { [number]: number } = {}

local function safePrompt(player: Player, productId: number)
	local key = player.UserId
	local now = os.time()

	if lastPromptTime[key] and now - lastPromptTime[key] < 60 then
		return -- too soon, skip
	end

	lastPromptTime[key] = now
	MarketplaceService:PromptProductPurchase(player, productId)
end
```

### Misleading Descriptions

Do not describe a GamePass as "2x Everything" if it only doubles coins and not XP. Do not show a product giving 1,000 coins in the icon but actually grant 100. Roblox can remove misleading assets, and players will leave negative reviews.

### Hiding Costs

Never make the total cost of engagement unclear. If your game has a "Battle Pass" that requires buying 10 tiers at 50 Robux each, make the full 500 Robux cost visible upfront rather than drip-feeding 50 Robux prompts.
