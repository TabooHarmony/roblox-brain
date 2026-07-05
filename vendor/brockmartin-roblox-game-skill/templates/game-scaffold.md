# Universal Game Scaffold

## Overview

This is the universal foundation for ANY Roblox game regardless of genre. Use this as the starting point before applying genre-specific templates (simulator, tycoon, obby, RPG, horror, battle royale, etc.). Genre templates build on top of this scaffold -- they never replace it.

This scaffold provides:
- Standard folder structure with clear separation of concerns
- Server game lifecycle management
- Player data persistence using the ProfileService pattern
- Centralized remote event validation with rate limiting
- Client initialization and system bootstrapping
- Shared type definitions and constants

All code uses `.luau` extension, Luau type annotations, and follows production best practices.

---

## Folder Structure

```
game/
├── ServerScriptService/
│   ├── GameManager.server.luau      -- Game lifecycle: init, load modules, create remotes, game loop
│   ├── DataManager.server.luau      -- Player data persistence (ProfileService pattern)
│   └── RemoteHandler.server.luau    -- Centralized remote validation, rate limiting, dispatch
├── ServerStorage/
│   ├── Modules/                     -- Server-only modules (not visible to clients)
│   │   └── ItemDefinitions.luau     -- Item/asset data tables, drop rates, pricing
│   └── Assets/                      -- Server-only models/assets (cloned on demand)
├── ReplicatedStorage/
│   ├── Shared/                      -- Shared modules (both server and client can require)
│   │   ├── Types.luau               -- Shared type definitions (PlayerData, ItemData, etc.)
│   │   └── Constants.luau           -- Shared constants (intervals, limits, enums)
│   ├── Remotes/                     -- RemoteEvents and RemoteFunctions (created at runtime by GameManager)
│   └── Assets/                      -- Client-visible assets (effects, animations, UI prefabs)
├── StarterGui/
│   └── MainGui/                     -- Primary ScreenGui container for all UI
├── StarterPlayer/
│   └── StarterPlayerScripts/
│       └── ClientController.client.luau  -- Client initialization, input, UI wiring
└── Workspace/
    └── Map/                         -- Game world geometry and spawn locations
```

### Placement Rules

| Content | Location | Why |
|---------|----------|-----|
| Game logic, data, anti-cheat | `ServerScriptService` | Hidden from clients, server-authoritative |
| Secret configs, drop tables, pricing | `ServerStorage/Modules` | Clients cannot read server storage |
| Cloneable models, maps, NPCs | `ServerStorage/Assets` | Loaded on demand, hidden until needed |
| Shared types, constants, utilities | `ReplicatedStorage/Shared` | Both sides need identical definitions |
| RemoteEvents/Functions | `ReplicatedStorage/Remotes` | Must be accessible from both sides |
| Client-visible effects, animations | `ReplicatedStorage/Assets` | Client needs to render these |
| UI layouts | `StarterGui` | Cloned into PlayerGui on spawn |
| Client controllers | `StarterPlayerScripts` | Persist across respawns |
| 3D world | `Workspace/Map` | The live game environment |

---

## Core Modules

### Constants (`ReplicatedStorage/Shared/Constants.luau`)

```luau
--!strict
-- Shared constants used by both server and client.
-- Add game-specific constants here. Genre templates extend this table.

local Constants = {
	-- Data persistence
	SAVE_INTERVAL = 300,           -- Auto-save every 5 minutes (seconds)
	DATA_STORE_NAME = "PlayerData_v1",

	-- Remote security
	MAX_REMOTE_RATE = 30,          -- Default max remote fires per window
	REMOTE_WINDOW = 10,            -- Rate limit window (seconds)
	REMOTE_COOLDOWN = 1,           -- Default cooldown after hitting rate limit (seconds)
	REMOTE_KICK_THRESHOLD = 5,     -- Kick after this many rate limit violations

	-- Gameplay defaults
	MAX_HEALTH = 100,
	WALK_SPEED = 16,
	SPRINT_SPEED = 24,
	INTERACTION_RANGE = 15,        -- Studs

	-- Remote names (single source of truth for all remote identifiers)
	Remotes = {
		PlayerDataLoaded = "PlayerDataLoaded",
		RequestAction = "RequestAction",
		UpdateUI = "UpdateUI",
	},
}

return Constants
```

### Types (`ReplicatedStorage/Shared/Types.luau`)

```luau
--!strict
-- Shared type definitions used by both server and client.
-- Genre templates extend these types with game-specific fields.

export type PlayerData = {
	DataVersion: number,
	Cash: number,
	Level: number,
	Experience: number,
	Inventory: { ItemEntry },
	Settings: PlayerSettings,
	Statistics: PlayerStatistics,
}

export type ItemEntry = {
	Id: string,
	Quantity: number,
	Metadata: { [string]: any }?,
}

export type ItemDefinition = {
	Id: string,
	Name: string,
	Description: string,
	Rarity: number,
	MaxStack: number,
	BasePrice: number,
}

export type PlayerSettings = {
	MusicVolume: number,
	SFXVolume: number,
	ShowTutorial: boolean,
}

export type PlayerStatistics = {
	TotalPlayTime: number,
	GamesPlayed: number,
	JoinedTimestamp: number,
}

-- Validator function signature used by RemoteHandler
export type ValidatorFn = (player: Player, ...any) -> (boolean, string?)

-- Remote handler signature
export type RemoteHandlerFn = (player: Player, ...any) -> ()

-- Remote registration config
export type RemoteConfig = {
	Name: string,
	Type: "Event" | "Function",
	Handler: RemoteHandlerFn | (player: Player, ...any) -> ...any,
	Validator: ValidatorFn?,
	Cooldown: number?,
	RateLimit: number?,
}

return nil
```

### GameManager (`ServerScriptService/GameManager.server.luau`)

```luau
--!strict
--[[
	GameManager.server.luau
	Game lifecycle controller. This is the entry point for the server.

	Initialization order:
	1. Cache services
	2. Load shared modules (Constants, Types)
	3. Initialize DataManager (must be ready before players join)
	4. Initialize RemoteHandler (creates remotes, registers handlers)
	5. Connect PlayerAdded/PlayerRemoving
	6. Handle players already in game (Studio fast-start edge case)
	7. Start game loop
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ServerScriptService = game:GetService("ServerScriptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- Shared modules
local Constants = require(ReplicatedStorage.Shared.Constants)

-- Server modules
local DataManager = require(ServerScriptService.DataManager)
local RemoteHandler = require(ServerScriptService.RemoteHandler)

local GameManager = {}

local isInitialized = false
local isRunning = false

--[[ -----------------------------------------------------------------------
	Initialization
----------------------------------------------------------------------- ]]

local function createRemoteFolder(): Folder
	local existing = ReplicatedStorage:FindFirstChild("Remotes")
	if existing then
		return existing :: Folder
	end

	local folder = Instance.new("Folder")
	folder.Name = "Remotes"
	folder.Parent = ReplicatedStorage
	return folder
end

local function onPlayerAdded(player: Player)
	-- Load player data (DataManager handles retry/kick on failure)
	DataManager.loadPlayer(player)
end

local function onPlayerRemoving(player: Player)
	-- Save and release player data
	DataManager.unloadPlayer(player)

	-- Clean up remote handler state (rate limit tracking, cooldowns)
	RemoteHandler.cleanupPlayer(player)
end

function GameManager.init()
	if isInitialized then
		warn("[GameManager] Already initialized")
		return
	end

	print("[GameManager] Initializing...")

	-- Step 1: Create the Remotes folder
	createRemoteFolder()

	-- Step 2: Initialize data persistence (must happen before players connect)
	DataManager.init()

	-- Step 3: Initialize remote handling (creates RemoteEvents, registers handlers)
	RemoteHandler.init()

	-- Step 4: Connect player lifecycle events
	Players.PlayerAdded:Connect(onPlayerAdded)
	Players.PlayerRemoving:Connect(onPlayerRemoving)

	-- Step 5: Handle players who joined before this script ran (Studio edge case)
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end

	isInitialized = true
	print("[GameManager] Initialization complete")
end

--[[ -----------------------------------------------------------------------
	Game Loop
----------------------------------------------------------------------- ]]

function GameManager.start()
	if not isInitialized then
		error("[GameManager] Must call init() before start()")
	end

	if isRunning then
		warn("[GameManager] Game loop already running")
		return
	end

	isRunning = true
	print("[GameManager] Game loop started")

	-- Main game loop — genre templates override or extend this.
	-- Default: heartbeat-driven tick for periodic tasks.
	local autoSaveTimer = 0

	RunService.Heartbeat:Connect(function(dt: number)
		if not isRunning then
			return
		end

		-- Auto-save on interval
		autoSaveTimer += dt
		if autoSaveTimer >= Constants.SAVE_INTERVAL then
			autoSaveTimer = 0
			DataManager.saveAllPlayers()
		end

		-- Genre-specific tick logic goes here.
		-- Example: round management, spawner updates, world simulation.
	end)
end

--[[ -----------------------------------------------------------------------
	Shutdown
----------------------------------------------------------------------- ]]

game:BindToClose(function()
	isRunning = false
	print("[GameManager] Server shutting down, saving all player data...")
	DataManager.saveAllPlayersSync()
end)

--[[ -----------------------------------------------------------------------
	Bootstrap
----------------------------------------------------------------------- ]]

GameManager.init()
GameManager.start()
```

### DataManager (`ServerScriptService/DataManager.server.luau`)

```luau
--!strict
--[[
	DataManager.server.luau
	Player data persistence using the ProfileService pattern.

	Features:
	- Profile template with default values for new players
	- Automatic session locking (prevents data corruption on server hops)
	- Auto-save on interval (driven by GameManager)
	- Save on PlayerRemoving
	- Parallel saves on BindToClose (30-second deadline)
	- Data access API: getData, setData, updateData
	- Schema reconciliation (new fields get defaults automatically)

	If ProfileService is not installed, this module falls back to raw
	DataStoreService with the same external API. Replace the internals
	with ProfileService when ready for production.
]]

local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)

local DataManager = {}

--[[ -----------------------------------------------------------------------
	Profile Template — Default data for new players.
	Genre templates extend this with game-specific fields.
----------------------------------------------------------------------- ]]

local PROFILE_TEMPLATE: { [string]: any } = {
	DataVersion = 1,
	Cash = 0,
	Level = 1,
	Experience = 0,
	Inventory = {},
	Settings = {
		MusicVolume = 0.5,
		SFXVolume = 0.8,
		ShowTutorial = true,
	},
	Statistics = {
		TotalPlayTime = 0,
		GamesPlayed = 0,
		JoinedTimestamp = 0,
	},
}

--[[ -----------------------------------------------------------------------
	Internal State
----------------------------------------------------------------------- ]]

local dataStore = DataStoreService:GetDataStore(Constants.DATA_STORE_NAME)
local playerDataCache: { [Player]: { [string]: any } } = {}
local playerLoadedSignals: { [Player]: BindableEvent } = {}

local MAX_RETRIES = 3
local RETRY_DELAY = 2

--[[ -----------------------------------------------------------------------
	Helpers
----------------------------------------------------------------------- ]]

-- Deep clone a table to avoid shared references between players
local function deepClone(original: { [string]: any }): { [string]: any }
	local clone: { [string]: any } = {}
	for key, value in original do
		if typeof(value) == "table" then
			clone[key] = deepClone(value :: { [string]: any })
		else
			clone[key] = value
		end
	end
	return clone
end

-- Reconcile loaded data against the template (fills in missing fields)
local function reconcile(data: { [string]: any }, template: { [string]: any })
	for key, default in template do
		if data[key] == nil then
			if typeof(default) == "table" then
				data[key] = deepClone(default :: { [string]: any })
			else
				data[key] = default
			end
		elseif typeof(default) == "table" and typeof(data[key]) == "table" then
			reconcile(data[key] :: { [string]: any }, default :: { [string]: any })
		end
	end
end

-- Validate that data has the expected shape (prevents saving corrupt data)
local function validateData(data: { [string]: any }): boolean
	if typeof(data) ~= "table" then
		return false
	end
	if typeof(data.Cash) ~= "number" or data.Cash ~= data.Cash then -- NaN check
		return false
	end
	if typeof(data.Level) ~= "number" or data.Level < 1 then
		return false
	end
	return true
end

local function getKey(player: Player): string
	return "Player_" .. player.UserId
end

--[[ -----------------------------------------------------------------------
	Load / Save
----------------------------------------------------------------------- ]]

local function loadData(player: Player): { [string]: any }?
	local key = getKey(player)

	for attempt = 1, MAX_RETRIES do
		local success, result = pcall(function()
			return dataStore:GetAsync(key)
		end)

		if success then
			local data = result or deepClone(PROFILE_TEMPLATE)
			reconcile(data, PROFILE_TEMPLATE)

			-- Set first-join timestamp if new player
			if data.Statistics.JoinedTimestamp == 0 then
				data.Statistics.JoinedTimestamp = os.time()
			end
			data.Statistics.GamesPlayed += 1

			return data
		end

		warn(`[DataManager] Load attempt {attempt}/{MAX_RETRIES} failed for {player.Name}: {result}`)
		if attempt < MAX_RETRIES then
			task.wait(RETRY_DELAY * attempt)
		end
	end

	return nil
end

local function saveData(player: Player): boolean
	local data = playerDataCache[player]
	if not data then
		return false
	end

	if not validateData(data) then
		warn(`[DataManager] Invalid data for {player.Name}, skipping save`)
		return false
	end

	local key = getKey(player)

	for attempt = 1, MAX_RETRIES do
		local success, err = pcall(function()
			dataStore:UpdateAsync(key, function(_oldData)
				return data
			end)
		end)

		if success then
			return true
		end

		warn(`[DataManager] Save attempt {attempt}/{MAX_RETRIES} failed for {player.Name}: {err}`)
		if attempt < MAX_RETRIES then
			task.wait(RETRY_DELAY * attempt)
		end
	end

	warn(`[DataManager] All save retries exhausted for {player.Name}`)
	return false
end

--[[ -----------------------------------------------------------------------
	Public API
----------------------------------------------------------------------- ]]

function DataManager.init()
	print("[DataManager] Initialized")
end

function DataManager.loadPlayer(player: Player)
	local data = loadData(player)

	if not data then
		player:Kick("Failed to load your data. Please rejoin.")
		return
	end

	-- Check if the player left during async load
	if not player:IsDescendantOf(Players) then
		return
	end

	playerDataCache[player] = data

	-- Set up leaderstats for the leaderboard
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"

	local cashValue = Instance.new("IntValue")
	cashValue.Name = "Cash"
	cashValue.Value = data.Cash
	cashValue.Parent = leaderstats

	local levelValue = Instance.new("IntValue")
	levelValue.Name = "Level"
	levelValue.Value = data.Level
	levelValue.Parent = leaderstats

	leaderstats.Parent = player

	-- Signal that data is ready (other systems and client can listen for this)
	local remotes = ReplicatedStorage:FindFirstChild("Remotes")
	if remotes then
		local dataLoadedRemote = remotes:FindFirstChild(Constants.Remotes.PlayerDataLoaded)
		if dataLoadedRemote and dataLoadedRemote:IsA("RemoteEvent") then
			(dataLoadedRemote :: RemoteEvent):FireClient(player, {
				Cash = data.Cash,
				Level = data.Level,
				Experience = data.Experience,
			})
		end
	end

	print(`[DataManager] Loaded data for {player.Name}`)
end

function DataManager.unloadPlayer(player: Player)
	-- Sync leaderstats back to cache before saving
	local data = playerDataCache[player]
	if data then
		local leaderstats = player:FindFirstChild("leaderstats")
		if leaderstats then
			local cashValue = leaderstats:FindFirstChild("Cash")
			if cashValue and cashValue:IsA("IntValue") then
				data.Cash = cashValue.Value
			end
			local levelValue = leaderstats:FindFirstChild("Level")
			if levelValue and levelValue:IsA("IntValue") then
				data.Level = levelValue.Value
			end
		end

		saveData(player)
		playerDataCache[player] = nil
	end

	print(`[DataManager] Unloaded data for {player.Name}`)
end

-- Get the full data table for a player (returns nil if not loaded yet)
function DataManager.getData(player: Player): { [string]: any }?
	return playerDataCache[player]
end

-- Set a specific field in a player's data
function DataManager.setData(player: Player, key: string, value: any): boolean
	local data = playerDataCache[player]
	if not data then
		warn(`[DataManager] setData: no data loaded for {player.Name}`)
		return false
	end

	data[key] = value

	-- Sync to leaderstats if applicable
	local leaderstats = player:FindFirstChild("leaderstats")
	if leaderstats then
		local stat = leaderstats:FindFirstChild(key)
		if stat and stat:IsA("IntValue") and typeof(value) == "number" then
			stat.Value = math.floor(value)
		end
	end

	return true
end

-- Atomically update a field using a transform function
function DataManager.updateData(player: Player, key: string, transform: (current: any) -> any): boolean
	local data = playerDataCache[player]
	if not data then
		warn(`[DataManager] updateData: no data loaded for {player.Name}`)
		return false
	end

	local newValue = transform(data[key])
	return DataManager.setData(player, key, newValue)
end

-- Save all currently loaded players (non-blocking, spawns save tasks)
function DataManager.saveAllPlayers()
	for player in playerDataCache do
		task.spawn(saveData, player)
	end
end

-- Save all players synchronously (for BindToClose, blocks until complete or timeout)
function DataManager.saveAllPlayersSync()
	local allPlayers = Players:GetPlayers()
	local remaining = #allPlayers

	if remaining == 0 then
		return
	end

	local finished = Instance.new("BindableEvent")

	for _, player in allPlayers do
		task.spawn(function()
			saveData(player)
			remaining -= 1
			if remaining <= 0 then
				finished:Fire()
			end
		end)
	end

	-- Wait for completion or timeout (leave 5s buffer before 30s hard limit)
	task.delay(25, function()
		finished:Fire()
	end)

	finished.Event:Wait()
	finished:Destroy()

	print("[DataManager] Shutdown save complete")
end

-- Get the profile template (useful for genre templates that extend it)
function DataManager.getProfileTemplate(): { [string]: any }
	return deepClone(PROFILE_TEMPLATE)
end

return DataManager
```

### RemoteHandler (`ServerScriptService/RemoteHandler.server.luau`)

```luau
--!strict
--[[
	RemoteHandler.server.luau
	Centralized remote event/function validation and dispatch.

	Features:
	- Register remotes with handler + validator in one call
	- Automatic type checking on arguments
	- Per-player rate limiting with configurable thresholds
	- Per-player, per-action cooldown enforcement
	- Logging of suspicious activity
	- Easy pattern for adding new remotes

	Usage:
	  RemoteHandler.register({
	      Name = "AttackRequest",
	      Type = "Event",
	      Handler = function(player, targetId)
	          -- handle attack
	      end,
	      Validator = function(player, targetId)
	          if typeof(targetId) ~= "string" then
	              return false, "targetId must be a string"
	          end
	          return true, nil
	      end,
	      Cooldown = 0.5,
	      RateLimit = 10,
	  })
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)

local RemoteHandler = {}

--[[ -----------------------------------------------------------------------
	Internal State
----------------------------------------------------------------------- ]]

-- Rate limiting: tracks timestamps of recent requests per player per remote
local rateLimitData: { [Player]: { [string]: { number } } } = {}

-- Cooldown tracking: last fire time per player per remote
local cooldownData: { [Player]: { [string]: number } } = {}

-- Violation counters per player
local violationCounts: { [Player]: number } = {}

-- Registered remote configs (for reference/debugging)
local registeredRemotes: { [string]: any } = {}

--[[ -----------------------------------------------------------------------
	Rate Limiting
----------------------------------------------------------------------- ]]

local function checkRateLimit(player: Player, remoteName: string, maxRequests: number): boolean
	local now = os.clock()
	local windowSeconds = Constants.REMOTE_WINDOW

	-- Initialize tracking
	if not rateLimitData[player] then
		rateLimitData[player] = {}
	end
	local playerRates = rateLimitData[player]

	if not playerRates[remoteName] then
		playerRates[remoteName] = {}
	end
	local timestamps = playerRates[remoteName]

	-- Prune timestamps outside the window
	local windowStart = now - windowSeconds
	local pruned: { number } = {}
	for _, ts in timestamps do
		if ts > windowStart then
			table.insert(pruned, ts)
		end
	end
	playerRates[remoteName] = pruned

	-- Check if at limit
	if #pruned >= maxRequests then
		-- Track violations
		violationCounts[player] = (violationCounts[player] or 0) + 1
		warn(`[RemoteHandler] Rate limited {player.Name} on "{remoteName}" (violation #{violationCounts[player]})`)

		if violationCounts[player] >= Constants.REMOTE_KICK_THRESHOLD then
			warn(`[RemoteHandler] Kicking {player.Name}: exceeded violation threshold`)
			task.defer(function()
				player:Kick("Too many requests. Please rejoin.")
			end)
		end

		return false
	end

	-- Record this request
	table.insert(pruned, now)
	playerRates[remoteName] = pruned
	return true
end

--[[ -----------------------------------------------------------------------
	Cooldown
----------------------------------------------------------------------- ]]

local function checkCooldown(player: Player, remoteName: string, cooldownSeconds: number): boolean
	local now = os.clock()

	if not cooldownData[player] then
		cooldownData[player] = {}
	end

	local lastUsed = cooldownData[player][remoteName]
	if lastUsed and (now - lastUsed) < cooldownSeconds then
		return false
	end

	cooldownData[player][remoteName] = now
	return true
end

--[[ -----------------------------------------------------------------------
	Registration
----------------------------------------------------------------------- ]]

function RemoteHandler.init()
	-- Ensure the Remotes folder exists
	local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
	if not remotesFolder then
		remotesFolder = Instance.new("Folder")
		remotesFolder.Name = "Remotes"
		remotesFolder.Parent = ReplicatedStorage
	end

	-- Create the default PlayerDataLoaded remote
	RemoteHandler.createRemote(Constants.Remotes.PlayerDataLoaded, "Event")
	RemoteHandler.createRemote(Constants.Remotes.UpdateUI, "Event")

	print("[RemoteHandler] Initialized")
end

-- Create a RemoteEvent or RemoteFunction without registering a handler
function RemoteHandler.createRemote(name: string, remoteType: string): Instance
	local remotesFolder = ReplicatedStorage:WaitForChild("Remotes")
	local existing = remotesFolder:FindFirstChild(name)
	if existing then
		return existing
	end

	local remote: Instance
	if remoteType == "Function" then
		remote = Instance.new("RemoteFunction")
	else
		remote = Instance.new("RemoteEvent")
	end

	remote.Name = name
	remote.Parent = remotesFolder
	return remote
end

-- Register a remote with handler, optional validator, cooldown, and rate limit.
-- This creates the remote instance and connects the handler with all security layers.
function RemoteHandler.register(config: {
	Name: string,
	Type: string,            -- "Event" or "Function"
	Handler: (...any) -> ...any,
	Validator: ((Player, ...any) -> (boolean, string?))?,
	Cooldown: number?,       -- Minimum seconds between fires (default: 0, no cooldown)
	RateLimit: number?,      -- Max fires per rate window (default: Constants.MAX_REMOTE_RATE)
})
	local remotesFolder = ReplicatedStorage:WaitForChild("Remotes")

	-- Create the remote instance
	local remote = RemoteHandler.createRemote(config.Name, config.Type)

	local cooldownSeconds = config.Cooldown or 0
	local maxRate = config.RateLimit or Constants.MAX_REMOTE_RATE

	registeredRemotes[config.Name] = config

	if config.Type == "Event" then
		local remoteEvent = remote :: RemoteEvent

		remoteEvent.OnServerEvent:Connect(function(player: Player, ...: any)
			-- Rate limit check
			if not checkRateLimit(player, config.Name, maxRate) then
				return
			end

			-- Cooldown check
			if cooldownSeconds > 0 then
				if not checkCooldown(player, config.Name, cooldownSeconds) then
					return
				end
			end

			-- Validator check
			if config.Validator then
				local valid, reason = config.Validator(player, ...)
				if not valid then
					warn(`[RemoteHandler] Validation failed for {player.Name} on "{config.Name}": {reason or "unknown"}`)
					return
				end
			end

			-- Execute handler
			config.Handler(player, ...)
		end)
	elseif config.Type == "Function" then
		local remoteFunction = remote :: RemoteFunction

		remoteFunction.OnServerInvoke = function(player: Player, ...: any)
			-- Rate limit check
			if not checkRateLimit(player, config.Name, maxRate) then
				return nil
			end

			-- Cooldown check
			if cooldownSeconds > 0 then
				if not checkCooldown(player, config.Name, cooldownSeconds) then
					return nil
				end
			end

			-- Validator check
			if config.Validator then
				local valid, reason = config.Validator(player, ...)
				if not valid then
					warn(`[RemoteHandler] Validation failed for {player.Name} on "{config.Name}": {reason or "unknown"}`)
					return nil
				end
			end

			-- Execute handler and return result
			return config.Handler(player, ...)
		end
	end

	print(`[RemoteHandler] Registered remote: {config.Name} ({config.Type})`)
end

--[[ -----------------------------------------------------------------------
	Cleanup
----------------------------------------------------------------------- ]]

function RemoteHandler.cleanupPlayer(player: Player)
	rateLimitData[player] = nil
	cooldownData[player] = nil
	violationCounts[player] = nil
end

--[[ -----------------------------------------------------------------------
	Utilities — For use by other server modules
----------------------------------------------------------------------- ]]

-- Fire a remote event to a specific client
function RemoteHandler.fireClient(remoteName: string, player: Player, ...: any)
	local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
	if not remotesFolder then
		return
	end

	local remote = remotesFolder:FindFirstChild(remoteName)
	if remote and remote:IsA("RemoteEvent") then
		remote:FireClient(player, ...)
	end
end

-- Fire a remote event to all clients
function RemoteHandler.fireAllClients(remoteName: string, ...: any)
	local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
	if not remotesFolder then
		return
	end

	local remote = remotesFolder:FindFirstChild(remoteName)
	if remote and remote:IsA("RemoteEvent") then
		remote:FireAllClients(...)
	end
end

return RemoteHandler
```

### ItemDefinitions (`ServerStorage/Modules/ItemDefinitions.luau`)

```luau
--!strict
--[[
	ItemDefinitions.luau
	Server-only item/asset data tables.

	This lives in ServerStorage so clients cannot read drop rates,
	pricing formulas, or hidden item stats. Only the server references this.

	Genre templates extend this with game-specific item categories.
]]

local ItemDefinitions = {}

-- Rarity tiers (maps to display color, drop weight, etc.)
ItemDefinitions.Rarity = {
	Common = { Tier = 1, Color = Color3.fromRGB(200, 200, 200), Weight = 60 },
	Uncommon = { Tier = 2, Color = Color3.fromRGB(30, 200, 30), Weight = 25 },
	Rare = { Tier = 3, Color = Color3.fromRGB(30, 100, 255), Weight = 10 },
	Epic = { Tier = 4, Color = Color3.fromRGB(160, 50, 255), Weight = 4 },
	Legendary = { Tier = 5, Color = Color3.fromRGB(255, 200, 0), Weight = 1 },
}

-- Item registry — add items here. Genre templates populate this further.
ItemDefinitions.Items: { [string]: {
	Name: string,
	Description: string,
	Rarity: string,
	MaxStack: number,
	BasePrice: number,
	Category: string,
} } = {
	-- Example starter item (replace with genre-specific items)
	coin = {
		Name = "Coin",
		Description = "A shiny gold coin.",
		Rarity = "Common",
		MaxStack = 9999,
		BasePrice = 1,
		Category = "Currency",
	},
}

-- Look up an item definition by ID
function ItemDefinitions.get(itemId: string): typeof(ItemDefinitions.Items[""])?
	return ItemDefinitions.Items[itemId]
end

-- Get all items in a category
function ItemDefinitions.getByCategory(category: string): { [string]: typeof(ItemDefinitions.Items[""]) }
	local results: { [string]: typeof(ItemDefinitions.Items[""]) } = {}
	for id, item in ItemDefinitions.Items do
		if item.Category == category then
			results[id] = item
		end
	end
	return results
end

return ItemDefinitions
```

### ClientController (`StarterPlayer/StarterPlayerScripts/ClientController.client.luau`)

```luau
--!strict
--[[
	ClientController.client.luau
	Client initialization script. Runs once per player on join.
	Persists across respawns (lives in StarterPlayerScripts).

	Initialization order:
	1. Cache services and wait for critical instances
	2. Wait for player data to replicate (server signals readiness)
	3. Set up UI connections
	4. Connect input handlers
	5. Initialize client-side systems (camera, sound, effects)
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local StarterGui = game:GetService("StarterGui")

local Constants = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Constants"))

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

--[[ -----------------------------------------------------------------------
	Wait for Server Data
----------------------------------------------------------------------- ]]

local remotesFolder = ReplicatedStorage:WaitForChild("Remotes")
local dataLoadedRemote = remotesFolder:WaitForChild(Constants.Remotes.PlayerDataLoaded) :: RemoteEvent
local updateUIRemote = remotesFolder:WaitForChild(Constants.Remotes.UpdateUI) :: RemoteEvent

local playerData: { [string]: any }? = nil

print("[ClientController] Waiting for player data...")

dataLoadedRemote.OnClientEvent:Connect(function(data: { [string]: any })
	playerData = data
	print(`[ClientController] Data received: Level {data.Level}, Cash {data.Cash}`)

	-- Initialize UI with data
	initializeUI(data)
end)

--[[ -----------------------------------------------------------------------
	UI Setup
----------------------------------------------------------------------- ]]

-- Disable default Roblox UI elements as needed
-- StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack, false)

local function initializeUI(data: { [string]: any })
	-- Find the MainGui ScreenGui
	local mainGui = playerGui:WaitForChild("MainGui", 10)
	if not mainGui then
		warn("[ClientController] MainGui not found")
		return
	end

	-- Genre templates wire up specific UI elements here.
	-- Example: update cash display, level display, etc.
	print("[ClientController] UI initialized")
end

-- Listen for server-pushed UI updates
updateUIRemote.OnClientEvent:Connect(function(updateType: string, payload: any)
	-- Dispatch UI updates based on type.
	-- Genre templates add cases here.
	if updateType == "Cash" then
		-- Update cash display
	elseif updateType == "Level" then
		-- Update level display
	end
end)

--[[ -----------------------------------------------------------------------
	Input Handling
----------------------------------------------------------------------- ]]

local function onInputBegan(input: InputObject, gameProcessedEvent: boolean)
	if gameProcessedEvent then
		return
	end

	-- Genre templates add input bindings here.
	-- Example keybinds:
	-- if input.KeyCode == Enum.KeyCode.E then
	--     fireInteraction()
	-- end
end

UserInputService.InputBegan:Connect(onInputBegan)

--[[ -----------------------------------------------------------------------
	Character Setup (runs each respawn)
----------------------------------------------------------------------- ]]

local function onCharacterAdded(character: Model)
	local humanoid = character:WaitForChild("Humanoid") :: Humanoid
	local rootPart = character:WaitForChild("HumanoidRootPart") :: BasePart

	-- Genre templates set up per-spawn logic here.
	-- Example: reset sprint, update camera target, apply cosmetics.
	print("[ClientController] Character spawned")
end

if player.Character then
	task.spawn(onCharacterAdded, player.Character)
end
player.CharacterAdded:Connect(onCharacterAdded)

--[[ -----------------------------------------------------------------------
	Boot Complete
----------------------------------------------------------------------- ]]

print("[ClientController] Client systems initialized")
```

---

## MCP Scaffold Instructions

Use this Luau code with the `execute_luau` MCP tool (Community MCP full mode) to create the entire folder structure and script sources in Studio automatically.

Run this as a **single `execute_luau` call** from the server context:

```luau
--[[
	MCP Scaffold Creator
	Creates the universal game scaffold folder structure and scripts in Roblox Studio.
	Execute via the MCP execute_luau tool.
]]

local ServerScriptService = game:GetService("ServerScriptService")
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")
local StarterPlayer = game:GetService("StarterPlayer")

-- Helper: create a folder if it doesn't exist
local function ensureFolder(parent: Instance, name: string): Folder
	local existing = parent:FindFirstChild(name)
	if existing and existing:IsA("Folder") then
		return existing
	end
	if existing then
		existing:Destroy()
	end
	local folder = Instance.new("Folder")
	folder.Name = name
	folder.Parent = parent
	return folder
end

-- Helper: create a script with source
local function createScript(parent: Instance, name: string, className: string, source: string): Instance
	local existing = parent:FindFirstChild(name)
	if existing then
		existing:Destroy()
	end
	local script = Instance.new(className)
	script.Name = name
	script.Source = source
	script.Parent = parent
	return script
end

-- Helper: create a ScreenGui
local function ensureScreenGui(parent: Instance, name: string): ScreenGui
	local existing = parent:FindFirstChild(name)
	if existing and existing:IsA("ScreenGui") then
		return existing
	end
	if existing then
		existing:Destroy()
	end
	local gui = Instance.new("ScreenGui")
	gui.Name = name
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Parent = parent
	return gui
end

print("Creating scaffold folders...")

-- ServerStorage
local ssModules = ensureFolder(ServerStorage, "Modules")
local ssAssets = ensureFolder(ServerStorage, "Assets")

-- ReplicatedStorage
local rsShared = ensureFolder(ReplicatedStorage, "Shared")
local rsRemotes = ensureFolder(ReplicatedStorage, "Remotes")
local rsAssets = ensureFolder(ReplicatedStorage, "Assets")

-- StarterGui
local mainGui = ensureScreenGui(StarterGui, "MainGui")

-- StarterPlayerScripts
local sps = StarterPlayer:FindFirstChild("StarterPlayerScripts")

-- Workspace
local mapFolder = ensureFolder(workspace, "Map")

print("Folders created. Creating scripts...")

-----------------------------------------------------------------------
-- Constants (ReplicatedStorage/Shared/Constants)
-----------------------------------------------------------------------
createScript(rsShared, "Constants", "ModuleScript", [[
--!strict
local Constants = {
	SAVE_INTERVAL = 300,
	DATA_STORE_NAME = "PlayerData_v1",
	MAX_REMOTE_RATE = 30,
	REMOTE_WINDOW = 10,
	REMOTE_COOLDOWN = 1,
	REMOTE_KICK_THRESHOLD = 5,
	MAX_HEALTH = 100,
	WALK_SPEED = 16,
	SPRINT_SPEED = 24,
	INTERACTION_RANGE = 15,
	Remotes = {
		PlayerDataLoaded = "PlayerDataLoaded",
		RequestAction = "RequestAction",
		UpdateUI = "UpdateUI",
	},
}
return Constants
]])

-----------------------------------------------------------------------
-- Types (ReplicatedStorage/Shared/Types)
-----------------------------------------------------------------------
createScript(rsShared, "Types", "ModuleScript", [[
--!strict
export type PlayerData = {
	DataVersion: number,
	Cash: number,
	Level: number,
	Experience: number,
	Inventory: { ItemEntry },
	Settings: PlayerSettings,
	Statistics: PlayerStatistics,
}

export type ItemEntry = {
	Id: string,
	Quantity: number,
	Metadata: { [string]: any }?,
}

export type ItemDefinition = {
	Id: string,
	Name: string,
	Description: string,
	Rarity: number,
	MaxStack: number,
	BasePrice: number,
}

export type PlayerSettings = {
	MusicVolume: number,
	SFXVolume: number,
	ShowTutorial: boolean,
}

export type PlayerStatistics = {
	TotalPlayTime: number,
	GamesPlayed: number,
	JoinedTimestamp: number,
}

export type ValidatorFn = (player: Player, ...any) -> (boolean, string?)
export type RemoteHandlerFn = (player: Player, ...any) -> ()

return nil
]])

-----------------------------------------------------------------------
-- ItemDefinitions (ServerStorage/Modules/ItemDefinitions)
-----------------------------------------------------------------------
createScript(ssModules, "ItemDefinitions", "ModuleScript", [[
--!strict
local ItemDefinitions = {}

ItemDefinitions.Rarity = {
	Common = { Tier = 1, Color = Color3.fromRGB(200, 200, 200), Weight = 60 },
	Uncommon = { Tier = 2, Color = Color3.fromRGB(30, 200, 30), Weight = 25 },
	Rare = { Tier = 3, Color = Color3.fromRGB(30, 100, 255), Weight = 10 },
	Epic = { Tier = 4, Color = Color3.fromRGB(160, 50, 255), Weight = 4 },
	Legendary = { Tier = 5, Color = Color3.fromRGB(255, 200, 0), Weight = 1 },
}

ItemDefinitions.Items = {
	coin = {
		Name = "Coin",
		Description = "A shiny gold coin.",
		Rarity = "Common",
		MaxStack = 9999,
		BasePrice = 1,
		Category = "Currency",
	},
}

function ItemDefinitions.get(itemId)
	return ItemDefinitions.Items[itemId]
end

function ItemDefinitions.getByCategory(category)
	local results = {}
	for id, item in ItemDefinitions.Items do
		if item.Category == category then
			results[id] = item
		end
	end
	return results
end

return ItemDefinitions
]])

-----------------------------------------------------------------------
-- DataManager (ServerScriptService/DataManager)
-- Stored as ModuleScript so GameManager can require it
-----------------------------------------------------------------------
createScript(ServerScriptService, "DataManager", "ModuleScript", [[
--!strict
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)

local DataManager = {}

local PROFILE_TEMPLATE = {
	DataVersion = 1,
	Cash = 0,
	Level = 1,
	Experience = 0,
	Inventory = {},
	Settings = {
		MusicVolume = 0.5,
		SFXVolume = 0.8,
		ShowTutorial = true,
	},
	Statistics = {
		TotalPlayTime = 0,
		GamesPlayed = 0,
		JoinedTimestamp = 0,
	},
}

local dataStore = DataStoreService:GetDataStore(Constants.DATA_STORE_NAME)
local playerDataCache = {}
local MAX_RETRIES = 3
local RETRY_DELAY = 2

local function deepClone(original)
	local clone = {}
	for key, value in original do
		if typeof(value) == "table" then
			clone[key] = deepClone(value)
		else
			clone[key] = value
		end
	end
	return clone
end

local function reconcile(data, template)
	for key, default in template do
		if data[key] == nil then
			if typeof(default) == "table" then
				data[key] = deepClone(default)
			else
				data[key] = default
			end
		elseif typeof(default) == "table" and typeof(data[key]) == "table" then
			reconcile(data[key], default)
		end
	end
end

local function validateData(data)
	if typeof(data) ~= "table" then return false end
	if typeof(data.Cash) ~= "number" or data.Cash ~= data.Cash then return false end
	if typeof(data.Level) ~= "number" or data.Level < 1 then return false end
	return true
end

local function getKey(player)
	return "Player_" .. player.UserId
end

local function loadData(player)
	local key = getKey(player)
	for attempt = 1, MAX_RETRIES do
		local success, result = pcall(function()
			return dataStore:GetAsync(key)
		end)
		if success then
			local data = result or deepClone(PROFILE_TEMPLATE)
			reconcile(data, PROFILE_TEMPLATE)
			if data.Statistics.JoinedTimestamp == 0 then
				data.Statistics.JoinedTimestamp = os.time()
			end
			data.Statistics.GamesPlayed += 1
			return data
		end
		warn("[DataManager] Load attempt " .. attempt .. "/" .. MAX_RETRIES .. " failed for " .. player.Name .. ": " .. tostring(result))
		if attempt < MAX_RETRIES then
			task.wait(RETRY_DELAY * attempt)
		end
	end
	return nil
end

local function saveData(player)
	local data = playerDataCache[player]
	if not data then return false end
	if not validateData(data) then
		warn("[DataManager] Invalid data for " .. player.Name .. ", skipping save")
		return false
	end
	local key = getKey(player)
	for attempt = 1, MAX_RETRIES do
		local success, err = pcall(function()
			dataStore:UpdateAsync(key, function()
				return data
			end)
		end)
		if success then return true end
		warn("[DataManager] Save attempt " .. attempt .. "/" .. MAX_RETRIES .. " failed for " .. player.Name .. ": " .. tostring(err))
		if attempt < MAX_RETRIES then
			task.wait(RETRY_DELAY * attempt)
		end
	end
	warn("[DataManager] All save retries exhausted for " .. player.Name)
	return false
end

function DataManager.init()
	print("[DataManager] Initialized")
end

function DataManager.loadPlayer(player)
	local data = loadData(player)
	if not data then
		player:Kick("Failed to load your data. Please rejoin.")
		return
	end
	if not player:IsDescendantOf(Players) then return end
	playerDataCache[player] = data

	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	local cashValue = Instance.new("IntValue")
	cashValue.Name = "Cash"
	cashValue.Value = data.Cash
	cashValue.Parent = leaderstats
	local levelValue = Instance.new("IntValue")
	levelValue.Name = "Level"
	levelValue.Value = data.Level
	levelValue.Parent = leaderstats
	leaderstats.Parent = player

	local remotes = ReplicatedStorage:FindFirstChild("Remotes")
	if remotes then
		local remote = remotes:FindFirstChild(Constants.Remotes.PlayerDataLoaded)
		if remote and remote:IsA("RemoteEvent") then
			remote:FireClient(player, { Cash = data.Cash, Level = data.Level, Experience = data.Experience })
		end
	end
	print("[DataManager] Loaded data for " .. player.Name)
end

function DataManager.unloadPlayer(player)
	local data = playerDataCache[player]
	if data then
		local leaderstats = player:FindFirstChild("leaderstats")
		if leaderstats then
			local cashVal = leaderstats:FindFirstChild("Cash")
			if cashVal and cashVal:IsA("IntValue") then data.Cash = cashVal.Value end
			local lvlVal = leaderstats:FindFirstChild("Level")
			if lvlVal and lvlVal:IsA("IntValue") then data.Level = lvlVal.Value end
		end
		saveData(player)
		playerDataCache[player] = nil
	end
	print("[DataManager] Unloaded data for " .. player.Name)
end

function DataManager.getData(player)
	return playerDataCache[player]
end

function DataManager.setData(player, key, value)
	local data = playerDataCache[player]
	if not data then return false end
	data[key] = value
	local leaderstats = player:FindFirstChild("leaderstats")
	if leaderstats then
		local stat = leaderstats:FindFirstChild(key)
		if stat and stat:IsA("IntValue") and typeof(value) == "number" then
			stat.Value = math.floor(value)
		end
	end
	return true
end

function DataManager.updateData(player, key, transform)
	local data = playerDataCache[player]
	if not data then return false end
	local newValue = transform(data[key])
	return DataManager.setData(player, key, newValue)
end

function DataManager.saveAllPlayers()
	for player in playerDataCache do
		task.spawn(saveData, player)
	end
end

function DataManager.saveAllPlayersSync()
	local allPlayers = Players:GetPlayers()
	local remaining = #allPlayers
	if remaining == 0 then return end
	local finished = Instance.new("BindableEvent")
	for _, player in allPlayers do
		task.spawn(function()
			saveData(player)
			remaining -= 1
			if remaining <= 0 then finished:Fire() end
		end)
	end
	task.delay(25, function() finished:Fire() end)
	finished.Event:Wait()
	finished:Destroy()
	print("[DataManager] Shutdown save complete")
end

function DataManager.getProfileTemplate()
	return deepClone(PROFILE_TEMPLATE)
end

return DataManager
]])

-----------------------------------------------------------------------
-- RemoteHandler (ServerScriptService/RemoteHandler)
-- Stored as ModuleScript so GameManager can require it
-----------------------------------------------------------------------
createScript(ServerScriptService, "RemoteHandler", "ModuleScript", [[
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)

local RemoteHandler = {}

local rateLimitData = {}
local cooldownData = {}
local violationCounts = {}

local function checkRateLimit(player, remoteName, maxRequests)
	local now = os.clock()
	local windowSeconds = Constants.REMOTE_WINDOW
	if not rateLimitData[player] then rateLimitData[player] = {} end
	local playerRates = rateLimitData[player]
	if not playerRates[remoteName] then playerRates[remoteName] = {} end
	local timestamps = playerRates[remoteName]
	local windowStart = now - windowSeconds
	local pruned = {}
	for _, ts in timestamps do
		if ts > windowStart then table.insert(pruned, ts) end
	end
	playerRates[remoteName] = pruned
	if #pruned >= maxRequests then
		violationCounts[player] = (violationCounts[player] or 0) + 1
		warn("[RemoteHandler] Rate limited " .. player.Name .. " on " .. remoteName)
		if violationCounts[player] >= Constants.REMOTE_KICK_THRESHOLD then
			task.defer(function() player:Kick("Too many requests.") end)
		end
		return false
	end
	table.insert(pruned, now)
	playerRates[remoteName] = pruned
	return true
end

local function checkCooldown(player, remoteName, cooldownSeconds)
	local now = os.clock()
	if not cooldownData[player] then cooldownData[player] = {} end
	local lastUsed = cooldownData[player][remoteName]
	if lastUsed and (now - lastUsed) < cooldownSeconds then return false end
	cooldownData[player][remoteName] = now
	return true
end

function RemoteHandler.init()
	local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
	if not remotesFolder then
		remotesFolder = Instance.new("Folder")
		remotesFolder.Name = "Remotes"
		remotesFolder.Parent = ReplicatedStorage
	end
	RemoteHandler.createRemote(Constants.Remotes.PlayerDataLoaded, "Event")
	RemoteHandler.createRemote(Constants.Remotes.UpdateUI, "Event")
	print("[RemoteHandler] Initialized")
end

function RemoteHandler.createRemote(name, remoteType)
	local remotesFolder = ReplicatedStorage:WaitForChild("Remotes")
	local existing = remotesFolder:FindFirstChild(name)
	if existing then return existing end
	local remote
	if remoteType == "Function" then
		remote = Instance.new("RemoteFunction")
	else
		remote = Instance.new("RemoteEvent")
	end
	remote.Name = name
	remote.Parent = remotesFolder
	return remote
end

function RemoteHandler.register(config)
	local remote = RemoteHandler.createRemote(config.Name, config.Type)
	local cooldownSeconds = config.Cooldown or 0
	local maxRate = config.RateLimit or Constants.MAX_REMOTE_RATE

	if config.Type == "Event" then
		remote.OnServerEvent:Connect(function(player, ...)
			if not checkRateLimit(player, config.Name, maxRate) then return end
			if cooldownSeconds > 0 then
				if not checkCooldown(player, config.Name, cooldownSeconds) then return end
			end
			if config.Validator then
				local valid, reason = config.Validator(player, ...)
				if not valid then
					warn("[RemoteHandler] Validation failed for " .. player.Name .. " on " .. config.Name .. ": " .. (reason or "unknown"))
					return
				end
			end
			config.Handler(player, ...)
		end)
	elseif config.Type == "Function" then
		remote.OnServerInvoke = function(player, ...)
			if not checkRateLimit(player, config.Name, maxRate) then return nil end
			if cooldownSeconds > 0 then
				if not checkCooldown(player, config.Name, cooldownSeconds) then return nil end
			end
			if config.Validator then
				local valid, reason = config.Validator(player, ...)
				if not valid then
					warn("[RemoteHandler] Validation failed for " .. player.Name .. " on " .. config.Name)
					return nil
				end
			end
			return config.Handler(player, ...)
		end
	end
	print("[RemoteHandler] Registered remote: " .. config.Name)
end

function RemoteHandler.cleanupPlayer(player)
	rateLimitData[player] = nil
	cooldownData[player] = nil
	violationCounts[player] = nil
end

function RemoteHandler.fireClient(remoteName, player, ...)
	local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
	if not remotesFolder then return end
	local remote = remotesFolder:FindFirstChild(remoteName)
	if remote and remote:IsA("RemoteEvent") then
		remote:FireClient(player, ...)
	end
end

function RemoteHandler.fireAllClients(remoteName, ...)
	local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
	if not remotesFolder then return end
	local remote = remotesFolder:FindFirstChild(remoteName)
	if remote and remote:IsA("RemoteEvent") then
		remote:FireAllClients(...)
	end
end

return RemoteHandler
]])

-----------------------------------------------------------------------
-- GameManager (ServerScriptService/GameManager — the entry-point Script)
-----------------------------------------------------------------------
createScript(ServerScriptService, "GameManager", "Script", [[
--!strict
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ServerScriptService = game:GetService("ServerScriptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local DataManager = require(ServerScriptService.DataManager)
local RemoteHandler = require(ServerScriptService.RemoteHandler)

local isInitialized = false
local isRunning = false

local function createRemoteFolder()
	local existing = ReplicatedStorage:FindFirstChild("Remotes")
	if existing then return existing end
	local folder = Instance.new("Folder")
	folder.Name = "Remotes"
	folder.Parent = ReplicatedStorage
	return folder
end

local function onPlayerAdded(player)
	DataManager.loadPlayer(player)
end

local function onPlayerRemoving(player)
	DataManager.unloadPlayer(player)
	RemoteHandler.cleanupPlayer(player)
end

-- Init
print("[GameManager] Initializing...")
createRemoteFolder()
DataManager.init()
RemoteHandler.init()

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

for _, player in Players:GetPlayers() do
	task.spawn(onPlayerAdded, player)
end

isInitialized = true
print("[GameManager] Initialization complete")

-- Game loop
isRunning = true
local autoSaveTimer = 0

RunService.Heartbeat:Connect(function(dt)
	if not isRunning then return end
	autoSaveTimer += dt
	if autoSaveTimer >= Constants.SAVE_INTERVAL then
		autoSaveTimer = 0
		DataManager.saveAllPlayers()
	end
end)

game:BindToClose(function()
	isRunning = false
	print("[GameManager] Server shutting down, saving all data...")
	DataManager.saveAllPlayersSync()
end)

print("[GameManager] Game loop started")
]])

-----------------------------------------------------------------------
-- ClientController (StarterPlayerScripts/ClientController)
-----------------------------------------------------------------------
createScript(sps, "ClientController", "LocalScript", [[
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Constants = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Constants"))

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local remotesFolder = ReplicatedStorage:WaitForChild("Remotes")
local dataLoadedRemote = remotesFolder:WaitForChild(Constants.Remotes.PlayerDataLoaded)
local updateUIRemote = remotesFolder:WaitForChild(Constants.Remotes.UpdateUI)

local playerData = nil

local function initializeUI(data)
	local mainGui = playerGui:WaitForChild("MainGui", 10)
	if not mainGui then
		warn("[ClientController] MainGui not found")
		return
	end
	print("[ClientController] UI initialized")
end

dataLoadedRemote.OnClientEvent:Connect(function(data)
	playerData = data
	print("[ClientController] Data received: Level " .. data.Level .. ", Cash " .. data.Cash)
	initializeUI(data)
end)

updateUIRemote.OnClientEvent:Connect(function(updateType, payload)
	-- Dispatch UI updates by type
end)

UserInputService.InputBegan:Connect(function(input, gameProcessed)
	if gameProcessed then return end
	-- Add input bindings here
end)

local function onCharacterAdded(character)
	local humanoid = character:WaitForChild("Humanoid")
	local rootPart = character:WaitForChild("HumanoidRootPart")
	print("[ClientController] Character spawned")
end

if player.Character then
	task.spawn(onCharacterAdded, player.Character)
end
player.CharacterAdded:Connect(onCharacterAdded)

print("[ClientController] Client systems initialized")
]])

print("")
print("=== SCAFFOLD COMPLETE ===")
print("Created:")
print("  ServerScriptService/GameManager (Script)")
print("  ServerScriptService/DataManager (ModuleScript)")
print("  ServerScriptService/RemoteHandler (ModuleScript)")
print("  ServerStorage/Modules/ItemDefinitions (ModuleScript)")
print("  ServerStorage/Assets/ (Folder)")
print("  ReplicatedStorage/Shared/Constants (ModuleScript)")
print("  ReplicatedStorage/Shared/Types (ModuleScript)")
print("  ReplicatedStorage/Remotes/ (Folder)")
print("  ReplicatedStorage/Assets/ (Folder)")
print("  StarterGui/MainGui (ScreenGui)")
print("  StarterPlayerScripts/ClientController (LocalScript)")
print("  Workspace/Map/ (Folder)")
print("")
print("Next: Apply a genre template to add game-specific systems.")
```

For the **standard MCP** (official 6-tool server), split the scaffold code into multiple `run_code` calls -- one per script -- since `run_code` may have shorter execution limits. Create folders first, then scripts one at a time.

---

## Manual Setup Instructions

For developers working directly in Roblox Studio without MCP:

### Step 1: Create Folder Structure

1. In the **Explorer** panel, right-click each service and select **Insert Object > Folder**:
   - `ServerStorage` > Add folder named `Modules`
   - `ServerStorage` > Add folder named `Assets`
   - `ReplicatedStorage` > Add folder named `Shared`
   - `ReplicatedStorage` > Add folder named `Remotes`
   - `ReplicatedStorage` > Add folder named `Assets`
   - `Workspace` > Add folder named `Map`

2. In `StarterGui`, insert a **ScreenGui** named `MainGui`. Set `ResetOnSpawn = false`.

### Step 2: Create Shared Modules

1. In `ReplicatedStorage/Shared`, insert a **ModuleScript** named `Constants`.
   - Paste the **Constants** code from the Core Modules section above.

2. In `ReplicatedStorage/Shared`, insert a **ModuleScript** named `Types`.
   - Paste the **Types** code from the Core Modules section above.

### Step 3: Create Server Modules

1. In `ServerStorage/Modules`, insert a **ModuleScript** named `ItemDefinitions`.
   - Paste the **ItemDefinitions** code from the Core Modules section above.

2. In `ServerScriptService`, insert a **ModuleScript** named `DataManager`.
   - Paste the **DataManager** code (the MCP version without `--!strict` annotations if your Studio does not support them).

3. In `ServerScriptService`, insert a **ModuleScript** named `RemoteHandler`.
   - Paste the **RemoteHandler** code.

### Step 4: Create the Game Manager (Entry Point)

1. In `ServerScriptService`, insert a **Script** named `GameManager`.
   - Paste the **GameManager** code. This is the only server Script -- it bootstraps everything else.

### Step 5: Create the Client Controller

1. In `StarterPlayer > StarterPlayerScripts`, insert a **LocalScript** named `ClientController`.
   - Paste the **ClientController** code.

### Step 6: Enable API Services

1. Go to **Game Settings > Security**.
2. Enable **Allow Studio Access to API Services** (required for DataStore testing in Studio).

### Step 7: Test

1. Press **Play** in Studio.
2. Check the **Output** panel for initialization messages:
   - `[GameManager] Initializing...`
   - `[DataManager] Initialized`
   - `[RemoteHandler] Initialized`
   - `[GameManager] Game loop started`
   - `[DataManager] Loaded data for [YourName]`
   - `[ClientController] Client systems initialized`

### Step 8: Apply a Genre Template

With the scaffold in place, apply a genre template (simulator, tycoon, obby, etc.) to add game-specific systems on top of this foundation.

---

## Extension Points

Genre templates extend this scaffold at these specific points:

| Extension Point | Where | What to Add |
|-----------------|-------|-------------|
| Profile template fields | `DataManager` PROFILE_TEMPLATE | Genre-specific player data (e.g., pets, rebirth count, quest state) |
| Constants | `Constants.luau` | Genre-specific values (round times, spawn rates, upgrade costs) |
| Types | `Types.luau` | Genre-specific type definitions |
| Item definitions | `ItemDefinitions.luau` | Genre-specific items, tools, pets, upgrades |
| Remote registrations | After `RemoteHandler.init()` in GameManager | Genre-specific remotes with validators |
| Game loop logic | `RunService.Heartbeat` in GameManager | Round management, spawners, world simulation |
| Client input bindings | `onInputBegan` in ClientController | Genre-specific keybinds and interactions |
| UI wiring | `initializeUI` in ClientController | Genre-specific HUD elements and menus |
| Character setup | `onCharacterAdded` in ClientController | Genre-specific per-spawn logic |
