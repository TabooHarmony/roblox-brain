--[[
    ProcessReceipt + ProfileStore Integration
    Source: madstudioroblox.github.io/ProfileStore/devproducts/ (Apache 2.0)
    
    This is the robust "PurchaseId caching" approach that yields the ProcessReceipt
    callback until the purchase is confirmed saved to DataStore. Prevents item loss
    on server crashes.
    
    ADAPT THIS: Replace ProductFunctions entries with your actual products.
    The PurchaseIdCheckAsync and processReceipt functions are copy-paste ready.
]]

local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

-- Reference to your loaded profiles table (from your ProfileStore setup)
local Profiles: {[Player]: typeof(PlayerStore:StartSessionAsync())} = {}

-- How many purchase IDs to cache per player (FIFO eviction)
local PURCHASE_ID_CACHE_SIZE = 100

-------------------------------------------------------------------------------
-- Product handlers: one function per Developer Product ID
-- Each receives (receiptInfo, player, profile). Mutate profile.Data directly.
-- Do NOT call profile:Save() here — PurchaseIdCheckAsync handles persistence.
-------------------------------------------------------------------------------

local ProductFunctions = {}

ProductFunctions[456456] = function(_receipt, _player, profile)
    profile.Data.Cash += 100
end

ProductFunctions[789789] = function(_receipt, _player, profile)
    table.insert(profile.Data.Inventory, "SpeedBoost")
end

-------------------------------------------------------------------------------
-- PurchaseIdCheckAsync: yields until purchase is confirmed saved to DataStore.
-- Returns PurchaseGranted only after DataStore persistence is verified.
-- Returns NotProcessedYet if profile releases before save confirms.
-------------------------------------------------------------------------------

function PurchaseIdCheckAsync(
    profile,
    purchase_id: string,
    grant_product: () -> ()
): Enum.ProductPurchaseDecision

    if profile:IsActive() ~= true then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local purchase_id_cache = profile.Data.PurchaseIdCache
    if purchase_id_cache == nil then
        purchase_id_cache = {}
        profile.Data.PurchaseIdCache = purchase_id_cache
    end

    -- Already granted in a previous session (idempotency check)
    if table.find(purchase_id_cache, purchase_id) ~= nil then
        return Enum.ProductPurchaseDecision.PurchaseGranted
    end

    -- Grant the product and record the PurchaseId atomically
    local success, result = pcall(grant_product)
    if success ~= true then
        warn(`[ProcessReceipt] Grant failed: {result}`)
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- FIFO eviction: keep cache bounded
    while #purchase_id_cache >= PURCHASE_ID_CACHE_SIZE do
        table.remove(purchase_id_cache, 1)
    end
    table.insert(purchase_id_cache, purchase_id)

    -- Yield until we confirm the PurchaseId was saved to DataStore
    -- profile.LastSavedData updates after each successful DataStore write
    while profile:IsActive() == true do
        local last_saved_cache = profile.LastSavedData
            and profile.LastSavedData.PurchaseIdCache

        if last_saved_cache and table.find(last_saved_cache, purchase_id) then
            return Enum.ProductPurchaseDecision.PurchaseGranted
        end

        -- Wait for next save cycle
        profile.OnAfterSave:Wait()
    end

    return Enum.ProductPurchaseDecision.NotProcessedYet
end

-------------------------------------------------------------------------------
-- processReceipt: the single callback assigned to MarketplaceService.
-- Waits for profile to load, then delegates to PurchaseIdCheckAsync.
-------------------------------------------------------------------------------

local function processReceipt(receiptInfo): Enum.ProductPurchaseDecision
    local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- Wait for profile to load (player may have just joined)
    local profile = Profiles[player]
    while profile == nil and player:IsDescendantOf(Players) do
        task.wait()
        profile = Profiles[player]
    end

    if profile == nil then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- Look up the handler for this product
    local handler = ProductFunctions[receiptInfo.ProductId]
    if handler == nil then
        warn(`[ProcessReceipt] No handler for ProductId {receiptInfo.ProductId}`)
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- Yield until purchase is confirmed saved
    return PurchaseIdCheckAsync(profile, receiptInfo.PurchaseId, function()
        handler(receiptInfo, player, profile)
    end)
end

-- Assign the callback (only ONE script may do this)
MarketplaceService.ProcessReceipt = processReceipt
