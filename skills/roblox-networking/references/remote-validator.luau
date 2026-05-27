--[[
    RemoteValidator — Production-ready server-side validation module
    Source: roblox-brain/skills/roblox-networking
    
    Drop this into ServerScriptService/Modules/. Require it in every remote handler.
    Covers: type checking, range validation, cooldowns, existence checks, distance,
    authorization, and cleanup.
    
    ADAPT THIS: Add game-specific checks (e.g. team validation, game state checks).
    The core patterns (validateArgs, checkCooldown, withinRange) are universal.
]]

local Players = game:GetService("Players")

local RemoteValidator = {}

-------------------------------------------------------------------------------
-- Type Checking
-- Validates that arguments match expected types.
-------------------------------------------------------------------------------

type TypeSpec = string | (value: any) -> boolean

function RemoteValidator.checkType(value: any, expected: TypeSpec): boolean
    if typeof(expected) == "function" then
        return expected(value)
    end
    return typeof(value) == expected
end

function RemoteValidator.validateArgs(
    args: { any },
    schema: { { name: string, type: TypeSpec, optional: boolean? } }
): (boolean, string?)
    for i, spec in schema do
        local value = args[i]

        if value == nil then
            if not spec.optional then
                return false, `Missing required argument: {spec.name}`
            end
            continue
        end

        if not RemoteValidator.checkType(value, spec.type) then
            return false, `Invalid type for {spec.name}: expected {tostring(spec.type)}, got {typeof(value)}`
        end
    end

    -- Reject extra arguments not declared in schema
    if #args > #schema then
        return false, `Too many arguments: expected {#schema}, got {#args}`
    end

    return true, nil
end

-------------------------------------------------------------------------------
-- Range Checking
-- Validates that numeric values fall within acceptable bounds.
-------------------------------------------------------------------------------

function RemoteValidator.checkRange(value: number, min: number, max: number): boolean
    return typeof(value) == "number"
        and value == value -- NaN check
        and value >= min
        and value <= max
end

function RemoteValidator.checkIntegerRange(value: number, min: number, max: number): boolean
    return RemoteValidator.checkRange(value, min, max)
        and math.floor(value) == value
end

-------------------------------------------------------------------------------
-- Cooldown Tracking
-- Per-player, per-action cooldown enforcement.
-------------------------------------------------------------------------------

local cooldowns: { [Player]: { [string]: number } } = {}

function RemoteValidator.checkCooldown(player: Player, action: string, cooldownSeconds: number): boolean
    local now = os.clock()
    local playerCooldowns = cooldowns[player]

    if not playerCooldowns then
        playerCooldowns = {}
        cooldowns[player] = playerCooldowns
    end

    local lastUsed = playerCooldowns[action]
    if lastUsed and (now - lastUsed) < cooldownSeconds then
        return false
    end

    playerCooldowns[action] = now
    return true
end

function RemoteValidator.clearPlayerCooldowns(player: Player)
    cooldowns[player] = nil
end

-------------------------------------------------------------------------------
-- Existence Checks
-- Validates that targets, objects, and instances actually exist.
-------------------------------------------------------------------------------

function RemoteValidator.playerExists(playerName: string): Player?
    return Players:FindFirstChild(playerName) :: Player?
end

function RemoteValidator.characterAlive(player: Player): boolean
    local character = player.Character
    if not character then
        return false
    end

    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if not humanoid then
        return false
    end

    return humanoid.Health > 0
end

function RemoteValidator.instanceExists(parent: Instance, name: string, className: string?): Instance?
    local child = parent:FindFirstChild(name)
    if not child then
        return nil
    end

    if className and not child:IsA(className) then
        return nil
    end

    return child
end

-------------------------------------------------------------------------------
-- Authorization
-- Checks if a player is allowed to perform an action.
-------------------------------------------------------------------------------

function RemoteValidator.playerOwnsItem(player: Player, itemId: string, inventoryFolder: Folder?): boolean
    local folder = inventoryFolder or player:FindFirstChild("Inventory") :: Folder?
    if not folder then
        return false
    end

    return folder:FindFirstChild(itemId) ~= nil
end

function RemoteValidator.playerHasAttribute(player: Player, attribute: string, expectedValue: any?): boolean
    local value = player:GetAttribute(attribute)
    if expectedValue ~= nil then
        return value == expectedValue
    end
    return value ~= nil
end

-------------------------------------------------------------------------------
-- Distance Check
-- Validates that two positions are within an acceptable range.
-------------------------------------------------------------------------------

function RemoteValidator.withinRange(posA: Vector3, posB: Vector3, maxDistance: number): boolean
    return (posA - posB).Magnitude <= maxDistance
end

function RemoteValidator.playerWithinRange(player: Player, targetPos: Vector3, maxDistance: number): boolean
    local character = player.Character
    if not character then
        return false
    end

    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then
        return false
    end

    return RemoteValidator.withinRange(root.Position, targetPos, maxDistance)
end

-------------------------------------------------------------------------------
-- Cleanup — prevent memory leaks from departed players
-------------------------------------------------------------------------------

Players.PlayerRemoving:Connect(function(player)
    RemoteValidator.clearPlayerCooldowns(player)
end)

return RemoteValidator
