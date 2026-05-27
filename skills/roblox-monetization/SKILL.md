---
name: roblox-monetization
description: ProcessReceipt correctness, prompt APIs, purchase reconciliation, session-lock interaction.
last_reviewed: 2026-05-26
---

<!-- Source: brockmartin/roblox-game-skill (MIT) -->

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

## Quick Reference

**Load Full Reference below only when you need specific API implementations or pricing formulas.**

Key rules:
- GamePasses: one-time purchase, check with UserOwnsGamePassAsync on join + cache.
- Developer Products: consumable, ProcessReceipt is the ONLY place to grant items.
- ProcessReceipt contract: grant item THEN return PurchaseGranted. If grant fails, return NotProcessedYet. Never return PurchaseGranted before granting.
- All purchase logic is SERVER-SIDE. Client only prompts.
- PromptGamePassPurchase / PromptProductPurchase from client, handle on server.
- TOS: odds disclosure MANDATORY for random items. Games get removed without it.
- TOS: no real-world trading, no misleading purchase UI, no pay-to-win that ruins gameplay.
- DevEx: dual-rate system. New Rate $0.0038/R$ (earned after Sept 5, 2025). Old Rate $0.0035/R$ (earned before). Must clear Old Rate balance first before New Rate kicks in.
- Premium Payouts: engagement-based, detect with player.MembershipType.
- Subscriptions: recurring monthly revenue via PromptSubscriptionPurchase. Tiered benefits.
- Private Servers: monetizable via PromptCreatePrivateServer / PromptPurchasePrivateServer.
- Paid Access: one-time Robux or local currency fee via PromptPurchaseExperience. Common for closed betas.
- Immersive Ads: AdService image/portal/video ad units. Earn via ad views, separate from Rewarded Video Ads.
- PolicyService: must-check for compliance (age/region restrictions on subscriptions, random items, ads).
- Commerce Products: sell physical merchandise through Roblox.
- Creator Store: sell plugins ($4.99+) and models ($2.99+) for USD. 30-day escrow hold.
- Never store purchase state only in DataStore without session locking (use ProfileStore).

---

## Full Reference

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

## 5. Rewarded Video Ads

Players opt-in to watching a short video ad in exchange for an in-game reward. Revenue per completed view. API is via `AdService` - use mcp-roblox-docs for current method signatures (API has changed during beta).

### Placement Best Practices

- **Between rounds** - natural break, player is already waiting
- **In lobby / waiting area** - low-stakes moment, nothing else to do
- **After death (optional revive)** - high motivation, clear value proposition
- **Daily bonus multiplier** - "Watch ad to double your daily reward"

**Avoid:** mid-gameplay interruptions, mandatory ads, ads that block progression.

### Reward Value

- Target 3-10 Robux equivalent value per completed view
- Too low: players won't bother. Too high: undermines paid products.
- Implement a server-side cooldown (5+ minutes) to prevent spam

---

## 6. Subscriptions

Subscriptions provide recurring monthly revenue. Players pay a monthly Robux fee and receive ongoing benefits. This creates predictable income and higher lifetime value per player.

### Core API

| Method / Event | Purpose |
|---|---|
| `MarketplaceService:PromptSubscriptionPurchase(player, subscriptionId)` | Show the subscription purchase prompt |
| `MarketplaceService.PromptSubscriptionPurchaseFinished` | Fires when the subscription purchase prompt closes (does NOT confirm purchase - use UserHasSubscriptionAsync to verify) |
| `MarketplaceService:GetSubscriptionProductInfoAsync(subscriptionId)` | Get subscription tier details (price, name, description) |
| `MarketplaceService:UserHasSubscriptionAsync(userId, subscriptionId)` | Check if a player has an active subscription |

### Subscription Configuration

Subscriptions are configured in the **Creator Dashboard > Monetization > Subscriptions**. Each subscription has:

- **Name** - Displayed to the player
- **Description** - What benefits they receive
- **Price** - Monthly Robux cost (25 R$ minimum)
- **Benefits** - Defined by your game; granted server-side

### Implementation (Server Script)

```luau
-- ServerScriptService/SubscriptionService.lua
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local SUBSCRIPTIONS = {
	["premium_monthly"] = {
		id = 123456789,
		name = "Premium Monthly",
		grant = function(player: Player)
			player:SetAttribute("Subscriber", true)
			player:SetAttribute("MonthlyBonus", 500)
		end,
		revoke = function(player: Player)
			player:SetAttribute("Subscriber", false)
			player:SetAttribute("MonthlyBonus", 0)
		end,
	},
}

-- Grant on join if subscription is active
local function onPlayerAdded(player: Player)
	for key, sub in SUBSCRIPTIONS do
		local success, hasSub = pcall(function()
			return MarketplaceService:UserHasSubscriptionAsync(player.UserId, sub.id)
		end)
		if success and hasSub then
			sub.grant(player)
		end
	end
end

-- Handle prompt close (NOTE: this does NOT confirm purchase succeeded)
-- Use UserHasSubscriptionAsync to verify actual subscription status
MarketplaceService.PromptSubscriptionPurchaseFinished:Connect(function(player: Player, subscriptionId: string, didTryPurchasing: boolean)
	if not didTryPurchasing then return end
	-- Player attempted purchase - verify it actually went through
	for key, sub in SUBSCRIPTIONS do
		if sub.id == subscriptionId then
			local success, hasSub = pcall(function()
				return MarketplaceService:UserHasSubscriptionAsync(player.UserId, sub.id)
			end)
			if success and hasSub then
				sub.grant(player)
			end
			break
		end
	end
end)

for _, player in Players:GetPlayers() do
	task.spawn(onPlayerAdded, player)
end
Players.PlayerAdded:Connect(onPlayerAdded)
```

### Subscription Design Best Practices

- **Tiered value:** Offer 2-3 tiers (Bronze/Silver/Gold or Basic/Pro/Ultimate) at increasing prices
- **Clear benefits:** List exact benefits in the subscription description. "2x coins" is better than "exclusive rewards"
- **Recurring currency:** Give a daily or monthly currency stipend that incentivizes logging in
- **Exclusive content:** Cosmetics, titles, frames, and emotes that are permanently unlocked for subscribers
- **Non-disruptive:** Free players should still enjoy the full game loop. Subscribers get bonuses, not exclusive gameplay
- **Cancellation:** Use `UserHasSubscriptionAsync` on player join to detect lapsed subscriptions and revoke benefits. The prompt event only fires when the UI closes, not on actual cancellation.

---

## 7. Private Servers

Private servers let players pay a monthly Robux fee for a dedicated server instance they control. Players can invite friends, play in private, host events, or farm resources without interference.

### Core API

| Method / Event | Purpose |
|---|---|
| `MarketplaceService:PromptCreatePrivateServer(player, placeId)` | Show the create/purchase prompt for a new private server |
| `MarketplaceService:PromptPurchasePrivateServer(player, privateServerId)` | Show the renewal prompt for an existing private server |
| `MarketplaceService.PrivateServerPurchaseFinished` | Fires when a private server is purchased or renewed |

### Setup

1. Navigate to your experience in Creator Dashboard
2. Go to **Monetization > Private Servers**
3. Set the monthly price in Robux (min 10 R$, can change every 60 days)
4. Configure any server-specific settings

### Notes

- **Price changes** are limited to once every 60 days. Plan pricing carefully.
- **Revenue:** You earn 50% of the subscription fee (Roblox takes the other 50%).
- **Permissions:** Private server owners can configure who can join via the server's settings page.
- **VipServer:** The legacy `VipServer` API is deprecated. Use the new Private Server APIs.

### Common Use Cases

- **Competitive practice:** Teams/guilds rent a server to practice strategies
- **Roleplay communities:** Persistent worlds for friend groups
- **Resource farming:** Dedicated server for grinding without competition
- **Content creators:** Record/stream without interference from other players
- **Classes/events:** Educators or event hosts run private sessions

---

## 8. Paid Access (Entry Fee)

Paid access charges a one-time fee - in Robux or local currency - for entry to your experience. Commonly used for closed betas, premium experiences, or content packs.

### Core API

| Method / Event | Purpose |
|---|---|
| `MarketplaceService:PromptPurchaseExperience(player)` | Prompt the player to purchase access |
| `MarketplaceService.PromptPurchaseExperienceFinished` | Fires when the prompt closes |
| `MarketplaceService:UserOwnsGamePassAsync` | Check if the player has purchased access (uses a hidden GamePass) |

### Implementation

```luau
-- Server: Check access on join
local MarketplaceService = game:GetService("MarketplaceService")

-- Roblox assigns a hidden GamePass ID when you enable paid access
-- Check it with UserOwnsGamePassAsync on PlayerAdded
local ACCESS_PASS_ID = 123456789  -- Replace with your experience's ID

local function onPlayerAdded(player: Player)
	local success, hasAccess = pcall(function()
		return MarketplaceService:UserOwnsGamePassAsync(player.UserId, ACCESS_PASS_ID)
	end)

	if success and hasAccess then
		-- Player has purchased access, let them in
	else
		-- Player has not purchased access
		-- Teleport them to the purchase experience or show a purchase prompt
	end
end
```

```luau
-- Client: Prompt purchase
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local function promptPurchase()
	MarketplaceService:PromptPurchaseExperience(Players.LocalPlayer)
end

MarketplaceService.PromptPurchaseExperienceFinished:Connect(function(player: Player, wasPurchased: boolean)
	if wasPurchased then
		-- Player purchased access, teleport to the main experience
	end
end)
```

### Types

| Type | Priced In | Payout |
|------|-----------|--------|
| **Robux** | Robux (one-time) | Standard Robux payout |
| **Local Currency** | User's local currency (fallback USD) | USD payout |

### Use Cases

- **Closed beta:** Let most engaged users test early
- **Standalone experiences:** One-time purchase games (premium content packs)
- **Ticket/event access:** Temporary access for limited-time events

---

## 9. Immersive Ads

Immersive ads allow Roblox to serve advertiser content inside your experience. You earn revenue from ad views. Separate from Rewarded Video Ads (which are player-initiated opt-in).

### Ad Formats

| Format | Description | Placement |
|--------|-------------|-----------|
| **Image Ad** | Static image displayed on an AdPanel or AdPortal | On a surface, billboard, or screen in your experience |
| **Portal Ad** | Interactive portal that teleports to another experience | Ground-level portal the player can walk through |
| **Video Ad** | Video player ad unit | On a screen or surface |
| **Branded Ad** | Custom branded content integrated into the experience | Sponsored items, branded environments |

### Core API

| API | Purpose |
|---|---|
| `AdService` | Service for managing ad units |
| `AdPortal` | Instance class for portal ad units |
| `AdGui` | Instance class for image/video ad units placed in 3D space |

### Placement Best Practices

- **Natural integration:** Place ads where real-world billboards or screens would exist (stadium walls, shop windows, city buildings)
- **Non-intrusive:** Ads should not block gameplay, navigation, or UI
- **Contextual:** An ad for a racing game fits on a billboard in your racing game's loading area
- **No interaction required:** Players should not be required to watch or interact with ads to progress
- **Respect PolicyService:** Check `PolicyService:GetPolicyInfoForPlayerAsync()` to ensure ads are shown only to eligible users (age/region restrictions)

---

## 10. Commerce Products and Creator Store

### Commerce Products

Commerce Products allow you to sell **physical goods** (merchandise) through Roblox. Configured in the Creator Dashboard under **Monetization > Commerce Products**.

- Requires seller onboarding and eligibility verification
- Products are synced to Roblox for purchase
- Supports fulfillment tracking

### Creator Store (Plugins and Models)

Sell development assets to other creators:

| Asset Type | Minimum Price | Revenue Share |
|------------|---------------|---------------|
| **Plugin** | $4.99 USD | Taxes and payment processing fees only |
| **Model** | $2.99 USD | Taxes and payment processing fees only |

**Escrow hold:** Roblox holds your share of each sale for **30 days** from the date of purchase.

### Marketplace (Catalog) Commissions

When users purchase your catalog items (accessories, clothes) within your experience via the avatar inspect menu or avatar editor service, you earn a commission on each sale.

---

## 11. PolicyService Compliance

Roblox requires you to use `PolicyService` to restrict certain monetization features based on the player's age, location, and platform.

### When to Check PolicyService

- **Subscriptions / Commerce Products:** Only show purchase options to eligible users
- **Paid random items (loot boxes, gacha):** Must block for users in restricted regions
- **Immersive ads:** Only show ad units to eligible users
- **Paid item trading:** Must check eligibility

### Implementation

```luau
-- ServerScriptService/PolicyServiceCheck.lua
local PolicyService = game:GetService("PolicyService")
local Players = game:GetService("Players")

local function isEligibleForRandomItems(player: Player): boolean
	local success, policyInfo = pcall(function()
		return PolicyService:GetPolicyInfoForPlayerAsync(player)
	end)

	if not success then
		-- On failure, default to restricting the feature
		return false
	end

	return policyInfo.IsPriceFixEnabled  -- Example: check relevant policy flag
end

-- Usage: hide loot boxes if the player is not eligible
local function updateShopUI(player: Player)
	if isEligibleForRandomItems(player) then
		-- Show loot boxes in the shop
	else
		-- Hide loot boxes or show a "not available in your region" message
	end
end

Players.PlayerAdded:Connect(function(player: Player)
	player:GetPropertyChangedSignal("MembershipType"):Connect(function()
		updateShopUI(player)
	end)
	updateShopUI(player)
end)
```

### Recommended Approach

- **Fail closed:** If `PolicyService:GetPolicyInfoForPlayerAsync()` errors, default to restricting the feature
- **Cache results per-player** to avoid repeated API calls
- **Re-check on locale change** if you support in-session region switching

---

## 12. Pricing Strategy

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

## 13. DevEx Math

### Dual Exchange Rate System

As of September 5, 2025, Roblox operates a dual-rate DevEx system based on when Robux was earned:

| Rate | Value | Applies To |
|------|-------|------------|
| **New Rate** | $0.0038/R$ | Robux earned **on or after** 10 AM PT on September 5, 2025 |
| **Old Rate** | $0.0035/R$ | Robux earned **before** 10 AM PT on September 5, 2025 |

### Cash-Out Ordering Rules

- **Must clear Old Rate first:** You must cash out **all** Old Rate Robux before you can cash out any New Rate Robux.
- **Spending does not help:** Spending Robux on the platform (items, experiences, etc.) does **not** reduce your Old Rate balance. Spending is deducted from your total balance but does not count toward clearing Old Rate first.
- **Group funds:** If you receive payment from a Group that earned Robux before the cutoff, those Robux also cash out at the Old Rate. Your Old Rate balance may increase from Group payouts.

### Example Conversion

| Balance Type | Amount | Rate | USD Value |
|-------------|--------|------|-----------|
| Old Rate | 30,000 R$ | $0.0035 | $105 |
| New Rate | 30,000 R$ | $0.0038 | $114 |
| Mixed (clear Old Rate first) | 30,000 Old + 30,000 New | Dual | $105 + $114 = $219 |

### Minimum Cashout

- **30,000 Robux** minimum per cash-out request.
- Funds are reviewed on a per-request basis. First-time cashouts require creating a DevEx portal account via email invite.
- Eligibility requirements and service requirements are defined in the [DevEx Terms of Use](https://en.help.roblox.com/hc/en-us/articles/205499100-Developer-Exchange-DevEx-Program-Frequently-Asked-Questions).

> **Upcoming (June 2026):** US creators 18+ will get a higher rate of ~$0.0054/Robux (42% increase). Requires identity verification.

### Revenue Projection Formulas

```
Daily Revenue (Robux) = DAU x Conversion Rate x Average Purchase (Robux)

Monthly Revenue (Robux) = Daily Revenue x 30

Monthly Revenue (USD) = Monthly Revenue (Robux) x 0.0038
```

**Example projections at different scales (New Rate):**

| DAU | Conversion Rate | Avg Purchase | Daily Robux | Monthly USD |
|---|---|---|---|---|
| 100 | 2% | 100 R$ | 200 | $23 |
| 1,000 | 2% | 100 R$ | 2,000 | $228 |
| 10,000 | 3% | 150 R$ | 45,000 | $5,130 |
| 100,000 | 3% | 150 R$ | 450,000 | $51,300 |

> **Important:** If your revenue includes Old Rate Robux, the USD value will be lower until the Old Rate balance is cleared. For mixed balances, calculate separately and sum.

**Typical conversion rates on Roblox:** 1-5% of DAU makes a purchase on any given day. Well-optimized games with strong shop design reach the higher end.

**Premium Payout addition:** Premium Payouts add roughly 10-30% on top of direct purchase revenue depending on your Premium player ratio and engagement quality.

### Break-Even Calculations

```
Hours spent developing = X
Hourly rate target = $Y/hr
Required total earnings = X * Y
Required Robux = (X * Y) / 0.0038
Required paying players = Required Robux / Average Purchase
```

---

## 14. Roblox TOS Compliance (MANDATORY)

These are not suggestions. Violating them gets your game taken down.

### Odds Disclosure (enforced, games get removed)

**Any item sold with a randomized element MUST display the exact drop chance percentages in-game.** This applies to:
- Loot boxes / mystery boxes
- Random pet hatching
- Gacha pulls
- Any "chance" mechanic tied to a purchase

If a pet has a 0.1% drop rate, the player must see "0.1%" before they buy. Not "rare," not "legendary," not a color code. The exact number.

Games have been taken down for violating this. Roblox enforces it.

```luau
-- Example: display odds on a loot box GUI
local oddsLabel = script.Parent.OddsLabel
oddsLabel.Text = "Drop rates: Common 60% | Uncommon 25% | Rare 10% | Epic 4% | Legendary 1%"
```

### Presenting Products (Guidelines)

Roblox requires monetization products to be presented in a way that is **transparent, honest, and user-friendly**:

**Discounts must be genuine and fair:**
- A discount is not genuine if an item is always "on sale" for the same amount.
- A discount is not fair if it's only offered for a very short time, pressuring users.

**No misleading urgency:**
- Don't claim an item is almost out of stock or only available for a short time if it isn't true.
- Don't use a countdown timer that isn't accurate or automatically restarts.

**Language recommendations:**
| Avoid | Use Instead |
|-------|-------------|
| "GET IT NOW" | "View Item" |
| "LAST CHANCE, ACT NOW" | "See Price" |
| "BUY BEFORE IT'S GONE!" | "Open Shop" |

### Other TOS Rules That Affect Monetization

- **No gambling mechanics.** Do not implement anything that resembles gambling (betting Robux, coin flips, roulette). Roblox bans these.
- **No off-platform sales.** Do not direct players to buy Robux or items outside of Roblox's systems.
- **No misleading product descriptions.** GamePass and DevProduct descriptions must exactly match what the player receives.
- **No purchased advantages in experiences marked as "All Ages."** Stricter rules apply for experiences targeting younger audiences.
- **Refund policy.** If a player reports not receiving an item, investigate and honor legitimate claims. Roblox can reverse charges.
- **PolicyService integration required.** Use `PolicyService:GetPolicyInfoForPlayerAsync()` to restrict subscriptions, commerce products, paid random items, and immersive ads based on user eligibility.

> **Recommendation:** Download and read the full [Roblox Community Standards](https://en.help.roblox.com/hc/en-us/articles/203313410-Roblox-Community-Standards) and [Terms of Use](https://en.help.roblox.com/hc/en-us/articles/115004647846-Roblox-Terms-of-Use). Feed them to the AI as context when working on monetization features.

---

## 15. Ethical Monetization

Roblox's audience skews young (a significant portion is under 16). This carries a responsibility to monetize fairly. Roblox also actively enforces policies against predatory practices.

### Do

- **Provide genuine value** for every purchase. The player should feel good about what they got.
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

## 16. Best Practices

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

## 17. Anti-Patterns

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
