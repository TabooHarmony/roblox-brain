--[[
    EventBatcher — Server-side analytics batching for high-frequency events
    Source: roblox-opencode/skills/roblox-analytics (authored for this harness)
    
    Use this for events that fire many times per player per session (kills, pickups,
    damage dealt). Instead of calling AnalyticsService on every occurrence, accumulate
    counts and flush periodically.
    
    ADAPT THIS: Change FLUSH_INTERVAL to match your game's pace.
    Add custom fields to the flush call if you need breakdown dimensions.
]]

local AnalyticsService = game:GetService("AnalyticsService")
local Players = game:GetService("Players")

local FLUSH_INTERVAL = 30 -- seconds between automatic flushes

local EventBatcher = {}
local batches: { [Player]: { [string]: number } } = {}

--- Increment a counter for a player. Flushed periodically as a single event with the total value.
function EventBatcher:increment(player: Player, eventName: string, amount: number?)
    if not batches[player] then
        batches[player] = {}
    end
    local current = batches[player][eventName] or 0
    batches[player][eventName] = current + (amount or 1)
end

--- Flush all accumulated events to AnalyticsService.
function EventBatcher:flush()
    for player, events in batches do
        if not player:IsDescendantOf(Players) then
            batches[player] = nil
            continue
        end
        for eventName, value in events do
            local success, err = pcall(function()
                AnalyticsService:LogCustomEvent(player, eventName, value)
            end)
            if not success then
                warn(`[EventBatcher] Failed to log {eventName}: {err}`)
            end
        end
    end
    batches = {}
end

--- Flush a single player's events (call on PlayerRemoving).
function EventBatcher:flushPlayer(player: Player)
    local events = batches[player]
    if not events then return end

    for eventName, value in events do
        pcall(function()
            AnalyticsService:LogCustomEvent(player, eventName, value)
        end)
    end
    batches[player] = nil
end

-- Periodic flush loop
task.spawn(function()
    while true do
        task.wait(FLUSH_INTERVAL)
        EventBatcher:flush()
    end
end)

-- Flush on player leaving so final counts aren't lost
Players.PlayerRemoving:Connect(function(player)
    EventBatcher:flushPlayer(player)
end)

return EventBatcher
