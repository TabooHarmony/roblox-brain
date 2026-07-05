# Genre Template: Battle Royale

## 1. Genre Overview

**Core Loop:** Drop --> Loot --> Survive --> Fight --> Win

Players deploy from a high point above the map, choose a landing spot, scavenge for weapons
and items, and fight to be the last player (or squad) standing while a shrinking safe zone
forces encounters.

**Key Pillars:**
- **Tension Curve** — Early game is looting and positioning; mid game is rotating to safe zone;
  late game is intense close-quarters combat.
- **Fair Starts** — Everyone drops with nothing. No permanent power advantages.
- **Emergent Gameplay** — Random loot placement and zone movement ensure no two matches feel the same.
- **High Stakes** — One life per match. Elimination is permanent (spectate or return to lobby).

**Roblox Examples:**
- BIG Paintball (arena variant with respawns, but loot/loadout loop applies)
- Arsenal (fast-paced weapon rotation, arena BR hybrid)
- Island Royale (classic BR format on Roblox)

**Typical Match Flow:**
1. Players gather in lobby while queue fills (30-60s)
2. Countdown begins once minimum player count reached
3. All players teleport to drop vehicle/sky platform
4. Free-fall with parachute to choose landing spot
5. Loot weapons, armor, consumables from spawn points
6. Storm/zone begins shrinking on a timer
7. Players eliminate each other; eliminated players spectate
8. Last player/squad alive wins
9. XP/rewards distributed, return to lobby

---

## 2. Architecture Blueprint

```
ServerScriptService/
  BattleRoyale/
    MatchManager.lua          -- State machine, round lifecycle
    StormSystem.lua           -- Zone shrink logic, damage ticks
    LootSpawner.lua           -- Item distribution across map
    EliminationTracker.lua    -- Kill feed, placements, stats
    DropSystem.lua            -- Sky deploy, parachute, landing
    SpectatorSystem.lua       -- Camera follow on elimination
    WeaponManager.lua         -- Weapon stats, rarity scaling
    InventoryManager.lua      -- Per-match inventory (not persistent)
    AntiCheat.lua             -- Server-side hit validation

ReplicatedStorage/
  BattleRoyale/
    Config.lua                -- Match settings, zone timings, loot tables
    WeaponDefs.lua            -- Weapon definitions and rarity stats
    Remotes/                  -- Folder of RemoteEvents/RemoteFunctions
      MatchState.lua          -- Replicate match phase to clients
      ZoneUpdate.lua          -- Broadcast zone position/radius
      KillFeed.lua            -- Broadcast eliminations
      SpectatorTarget.lua     -- Spectator camera target changes
      DropInput.lua           -- Player deploy/parachute input

StarterPlayerScripts/
  BattleRoyale/
    HUDController.lua         -- Health, kill count, alive count, zone timer
    MinimapController.lua     -- Minimap with zone overlay
    SpectatorController.lua   -- Spectator camera input
    DropController.lua        -- Parachute input and camera during drop
    LootPickupUI.lua          -- Proximity prompts for item pickup

StarterGui/
  BattleRoyaleHUD/
    KillFeed.gui              -- Kill feed overlay
    Minimap.gui               -- Minimap with storm circle
    MatchInfo.gui             -- Alive count, placement, zone timer
    Inventory.gui             -- Current loadout display
    VictoryScreen.gui         -- Winner announcement
    SpectatorHUD.gui          -- Spectating player info
```

**Module Responsibilities:**

| Module | Responsibility | Runs On |
|---|---|---|
| MatchManager | State machine, phase transitions, win detection | Server |
| StormSystem | Zone center, radius, shrink schedule, damage ticks | Server |
| LootSpawner | Place weapons/items at spawn points on match start | Server |
| EliminationTracker | Kill credit, placement tracking, kill feed broadcasts | Server |
| DropSystem | Sky teleport, free-fall physics, parachute deploy | Server + Client |
| SpectatorSystem | Camera assignment on elimination, player cycling | Server + Client |
| WeaponManager | Damage calculation, rarity stat scaling, hit validation | Server |
| InventoryManager | Per-match loadout, pickup/drop, ammo tracking | Server |

---

## 3. Core Systems (Luau Code)

### 3.1 Match Lifecycle State Machine

The match flows through discrete phases. A single `MatchState` value drives all systems.

```
Lobby --> Waiting --> Countdown --> Deploying --> InProgress --> Victory --> Cleanup --> Lobby
```

```luau
--!strict
-- ServerScriptService/BattleRoyale/MatchManager.lua

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local Config = require(ReplicatedStorage.BattleRoyale.Config)
local StormSystem = require(script.Parent.StormSystem)
local LootSpawner = require(script.Parent.LootSpawner)
local EliminationTracker = require(script.Parent.EliminationTracker)
local DropSystem = require(script.Parent.DropSystem)
local SpectatorSystem = require(script.Parent.SpectatorSystem)

local MatchStateRemote = ReplicatedStorage.BattleRoyale.Remotes.MatchState

export type MatchPhase =
	"Lobby"
	| "Waiting"
	| "Countdown"
	| "Deploying"
	| "InProgress"
	| "Victory"
	| "Cleanup"

local MatchManager = {}
MatchManager.__index = MatchManager

function MatchManager.new()
	local self = setmetatable({}, MatchManager)
	self._phase = "Lobby" :: MatchPhase
	self._alivePlayers = {} :: { [Player]: boolean }
	self._matchStartTime = 0
	self._countdownRemaining = Config.COUNTDOWN_DURATION
	self._winner = nil :: Player?
	return self
end

function MatchManager:GetPhase(): MatchPhase
	return self._phase
end

function MatchManager:GetAlivePlayers(): { Player }
	local alive = {}
	for player, isAlive in self._alivePlayers do
		if isAlive and player.Parent then
			table.insert(alive, player)
		end
	end
	return alive
end

function MatchManager:GetAliveCount(): number
	return #self:GetAlivePlayers()
end

function MatchManager:_setPhase(newPhase: MatchPhase)
	local oldPhase = self._phase
	self._phase = newPhase
	print(`[MatchManager] Phase: {oldPhase} -> {newPhase}`)
	MatchStateRemote:FireAllClients(newPhase)
end

function MatchManager:_transitionTo(phase: MatchPhase)
	local handlers: { [MatchPhase]: () -> () } = {
		Lobby = function()
			self:_setPhase("Lobby")
			-- Reset all systems
			self._alivePlayers = {}
			self._winner = nil
			EliminationTracker:Reset()
			SpectatorSystem:Reset()
		end,

		Waiting = function()
			self:_setPhase("Waiting")
			-- Wait for minimum players
			while self._phase == "Waiting" do
				local playerCount = #Players:GetPlayers()
				if playerCount >= Config.MIN_PLAYERS then
					self:_transitionTo("Countdown")
					return
				end
				task.wait(1)
			end
		end,

		Countdown = function()
			self:_setPhase("Countdown")
			self._countdownRemaining = Config.COUNTDOWN_DURATION

			for i = Config.COUNTDOWN_DURATION, 1, -1 do
				if self._phase ~= "Countdown" then return end
				self._countdownRemaining = i
				MatchStateRemote:FireAllClients("Countdown", i)

				-- If players drop below minimum during countdown, abort
				if #Players:GetPlayers() < Config.MIN_PLAYERS then
					self:_transitionTo("Waiting")
					return
				end
				task.wait(1)
			end

			self:_transitionTo("Deploying")
		end,

		Deploying = function()
			self:_setPhase("Deploying")

			-- Register all current players as alive
			for _, player in Players:GetPlayers() do
				self._alivePlayers[player] = true
			end

			-- Spawn loot across the map before players land
			LootSpawner:SpawnAllLoot()

			-- Teleport players to sky and begin drop sequence
			DropSystem:DeployAllPlayers(self:GetAlivePlayers())

			-- Wait for deploy phase duration (players are free-falling)
			task.wait(Config.DEPLOY_DURATION)

			self:_transitionTo("InProgress")
		end,

		InProgress = function()
			self:_setPhase("InProgress")
			self._matchStartTime = os.clock()

			-- Start the storm system
			StormSystem:Start()

			-- Main match loop: check for winner
			while self._phase == "InProgress" do
				local aliveCount = self:GetAliveCount()

				if aliveCount <= 1 then
					local alivePlayers = self:GetAlivePlayers()
					if #alivePlayers == 1 then
						self._winner = alivePlayers[1]
					end
					self:_transitionTo("Victory")
					return
				end

				-- Tick storm system
				StormSystem:Tick()

				task.wait(0.5)
			end
		end,

		Victory = function()
			self:_setPhase("Victory")

			-- Announce winner
			if self._winner then
				MatchStateRemote:FireAllClients("Victory", self._winner.Name)
				print(`[MatchManager] Winner: {self._winner.Name}`)
			else
				MatchStateRemote:FireAllClients("Victory", nil)
				print("[MatchManager] No winner (draw or all eliminated)")
			end

			-- Award XP / rewards here
			EliminationTracker:FinalizeResults(self._winner)

			-- Show victory screen for a few seconds
			task.wait(Config.VICTORY_SCREEN_DURATION)
			self:_transitionTo("Cleanup")
		end,

		Cleanup = function()
			self:_setPhase("Cleanup")

			-- Stop storm
			StormSystem:Stop()

			-- Despawn remaining loot
			LootSpawner:DespawnAllLoot()

			-- Reset drop system
			DropSystem:Reset()

			-- Teleport remaining players back to lobby spawn
			for _, player in Players:GetPlayers() do
				local lobbySpawn = workspace.LobbySpawn
				if player.Character and lobbySpawn then
					player.Character:PivotTo(lobbySpawn.CFrame + Vector3.new(0, 5, 0))
				end
			end

			task.wait(Config.CLEANUP_DURATION)
			self:_transitionTo("Lobby")
		end,
	}

	local handler = handlers[phase]
	if handler then
		handler()
	else
		warn(`[MatchManager] Unknown phase: {phase}`)
	end
end

function MatchManager:EliminatePlayer(player: Player, killer: Player?)
	if not self._alivePlayers[player] then return end

	self._alivePlayers[player] = false
	local placement = self:GetAliveCount() + 1

	EliminationTracker:RecordElimination(player, killer, placement)
	SpectatorSystem:BeginSpectating(player, self:GetAlivePlayers())

	print(`[MatchManager] {player.Name} eliminated (#{placement}). {self:GetAliveCount()} remain.`)
end

-- Handle player disconnect during match
function MatchManager:OnPlayerRemoving(player: Player)
	if self._alivePlayers[player] then
		self._alivePlayers[player] = nil
		EliminationTracker:RecordDisconnect(player, self:GetAliveCount() + 1)
	end
end

function MatchManager:Start()
	-- Listen for player disconnects
	Players.PlayerRemoving:Connect(function(player)
		self:OnPlayerRemoving(player)
	end)

	-- Begin the match cycle
	while true do
		self:_transitionTo("Lobby")
		task.wait(Config.LOBBY_INTERMISSION)
		self:_transitionTo("Waiting")
		-- Waiting will chain into Countdown -> Deploying -> InProgress -> Victory -> Cleanup -> Lobby
		task.wait(1)
	end
end

return MatchManager
```

**Config module (referenced above):**

```luau
--!strict
-- ReplicatedStorage/BattleRoyale/Config.lua

local Config = {
	-- Player counts
	MIN_PLAYERS = 4,
	MAX_PLAYERS = 50,

	-- Phase durations (seconds)
	LOBBY_INTERMISSION = 10,
	COUNTDOWN_DURATION = 10,
	DEPLOY_DURATION = 15,
	VICTORY_SCREEN_DURATION = 8,
	CLEANUP_DURATION = 5,

	-- Storm / Zone
	ZONE_INITIAL_RADIUS = 500,      -- studs
	ZONE_DAMAGE_PER_TICK = 5,
	ZONE_TICK_INTERVAL = 1.0,       -- seconds between damage ticks
	ZONE_PHASES = {
		{ waitTime = 60, shrinkTime = 30, radiusFraction = 0.6 },
		{ waitTime = 45, shrinkTime = 25, radiusFraction = 0.35 },
		{ waitTime = 30, shrinkTime = 20, radiusFraction = 0.15 },
		{ waitTime = 20, shrinkTime = 15, radiusFraction = 0.05 },
		{ waitTime = 10, shrinkTime = 10, radiusFraction = 0.0 },
	},

	-- Loot
	LOOT_SPAWN_TAG = "LootSpawn",
	RARITY_WEIGHTS = {
		Common = 40,
		Uncommon = 30,
		Rare = 18,
		Epic = 9,
		Legendary = 3,
	},

	-- Drop system
	DROP_HEIGHT = 500,               -- studs above map center
	PARACHUTE_DEPLOY_HEIGHT = 100,   -- auto-deploy parachute below this
	FALL_SPEED = 80,                 -- studs/sec during free fall
	PARACHUTE_SPEED = 30,            -- studs/sec with parachute

	-- Spectator
	SPECTATOR_CYCLE_COOLDOWN = 0.5,  -- seconds between switching targets
}

return Config
```

---

### 3.2 Shrinking Zone / Storm System

The zone is a circle on the XZ plane. Each phase picks a new smaller circle inside the
current safe area. The zone interpolates from current to target over the shrink duration.
Players outside take periodic damage.

```luau
--!strict
-- ServerScriptService/BattleRoyale/StormSystem.lua

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local Config = require(ReplicatedStorage.BattleRoyale.Config)
local ZoneUpdateRemote = ReplicatedStorage.BattleRoyale.Remotes.ZoneUpdate

local StormSystem = {}
StormSystem.__index = StormSystem

export type ZoneState = {
	centerX: number,
	centerZ: number,
	radius: number,
}

function StormSystem.new()
	local self = setmetatable({}, StormSystem)

	-- Current visible zone (what players see and what deals damage)
	self._currentZone = {
		centerX = 0,
		centerZ = 0,
		radius = Config.ZONE_INITIAL_RADIUS,
	} :: ZoneState

	-- Target zone the current zone is shrinking toward
	self._targetZone = {
		centerX = 0,
		centerZ = 0,
		radius = Config.ZONE_INITIAL_RADIUS,
	} :: ZoneState

	self._phaseIndex = 0
	self._isShrinking = false
	self._running = false
	self._damageTickAccumulator = 0

	-- Map bounds (set based on your map dimensions)
	self._mapCenterX = 0
	self._mapCenterZ = 0

	return self
end

-- Check if a world position is inside the current safe zone
function StormSystem:IsInsideZone(position: Vector3): boolean
	local dx = position.X - self._currentZone.centerX
	local dz = position.Z - self._currentZone.centerZ
	local distSquared = dx * dx + dz * dz
	return distSquared <= self._currentZone.radius * self._currentZone.radius
end

-- Pick a random point inside the current zone for the next smaller zone center
function StormSystem:_pickNextCenter(currentZone: ZoneState, nextRadius: number): (number, number)
	-- The new center must be placed so the new circle fits inside the old one
	local maxOffset = math.max(0, currentZone.radius - nextRadius)

	if maxOffset <= 0 then
		return currentZone.centerX, currentZone.centerZ
	end

	local angle = math.random() * 2 * math.pi
	local distance = math.random() * maxOffset
	local newCenterX = currentZone.centerX + math.cos(angle) * distance
	local newCenterZ = currentZone.centerZ + math.sin(angle) * distance

	return newCenterX, newCenterZ
end

-- Broadcast current zone state to all clients (for minimap rendering)
function StormSystem:_broadcastZone()
	ZoneUpdateRemote:FireAllClients(
		self._currentZone.centerX,
		self._currentZone.centerZ,
		self._currentZone.radius,
		self._targetZone.centerX,
		self._targetZone.centerZ,
		self._targetZone.radius,
		self._isShrinking
	)
end

-- Apply damage to all players outside the safe zone
function StormSystem:_applyStormDamage()
	for _, player in Players:GetPlayers() do
		local character = player.Character
		if not character then continue end

		local humanoid = character:FindFirstChildOfClass("Humanoid")
		local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
		if not humanoid or not rootPart then continue end
		if humanoid.Health <= 0 then continue end

		if not self:IsInsideZone(rootPart.Position) then
			-- Scale damage by phase for increasing urgency
			local damageMultiplier = math.max(1, self._phaseIndex)
			local damage = Config.ZONE_DAMAGE_PER_TICK * damageMultiplier
			humanoid:TakeDamage(damage)
		end
	end
end

-- Run a single shrink phase: wait, then interpolate zone to target
function StormSystem:_runPhase(phaseConfig: { waitTime: number, shrinkTime: number, radiusFraction: number })
	local nextRadius = Config.ZONE_INITIAL_RADIUS * phaseConfig.radiusFraction
	local nextCenterX, nextCenterZ = self:_pickNextCenter(self._currentZone, nextRadius)

	self._targetZone = {
		centerX = nextCenterX,
		centerZ = nextCenterZ,
		radius = nextRadius,
	}

	-- Phase 1: Wait period (zone is static, target is shown on minimap)
	self._isShrinking = false
	self:_broadcastZone()
	print(`[StormSystem] Phase {self._phaseIndex}: waiting {phaseConfig.waitTime}s before shrink`)

	local waitElapsed = 0
	while waitElapsed < phaseConfig.waitTime and self._running do
		task.wait(1)
		waitElapsed += 1
	end

	if not self._running then return end

	-- Phase 2: Shrink period (interpolate current zone toward target)
	self._isShrinking = true
	self:_broadcastZone()
	print(`[StormSystem] Phase {self._phaseIndex}: shrinking over {phaseConfig.shrinkTime}s`)

	local startZone: ZoneState = {
		centerX = self._currentZone.centerX,
		centerZ = self._currentZone.centerZ,
		radius = self._currentZone.radius,
	}

	local shrinkElapsed = 0
	while shrinkElapsed < phaseConfig.shrinkTime and self._running do
		local dt = task.wait()
		shrinkElapsed += dt

		local alpha = math.clamp(shrinkElapsed / phaseConfig.shrinkTime, 0, 1)
		-- Smooth ease-in-out interpolation
		local smoothAlpha = alpha * alpha * (3 - 2 * alpha)

		self._currentZone.centerX = startZone.centerX + (self._targetZone.centerX - startZone.centerX) * smoothAlpha
		self._currentZone.centerZ = startZone.centerZ + (self._targetZone.centerZ - startZone.centerZ) * smoothAlpha
		self._currentZone.radius = startZone.radius + (self._targetZone.radius - startZone.radius) * smoothAlpha

		self:_broadcastZone()
	end

	-- Snap to target at end of shrink
	self._currentZone.centerX = self._targetZone.centerX
	self._currentZone.centerZ = self._targetZone.centerZ
	self._currentZone.radius = self._targetZone.radius
	self._isShrinking = false
	self:_broadcastZone()
end

-- Called every match tick from MatchManager
function StormSystem:Tick()
	if not self._running then return end

	self._damageTickAccumulator += 0.5 -- called every 0.5s from MatchManager
	if self._damageTickAccumulator >= Config.ZONE_TICK_INTERVAL then
		self._damageTickAccumulator -= Config.ZONE_TICK_INTERVAL
		self:_applyStormDamage()
	end
end

function StormSystem:Start()
	self._running = true
	self._phaseIndex = 0
	self._damageTickAccumulator = 0

	-- Reset zone to full size
	self._currentZone = {
		centerX = self._mapCenterX,
		centerZ = self._mapCenterZ,
		radius = Config.ZONE_INITIAL_RADIUS,
	}
	self._targetZone = {
		centerX = self._mapCenterX,
		centerZ = self._mapCenterZ,
		radius = Config.ZONE_INITIAL_RADIUS,
	}

	self:_broadcastZone()

	-- Run zone phases in sequence on a separate thread
	task.spawn(function()
		for i, phaseConfig in Config.ZONE_PHASES do
			if not self._running then break end
			self._phaseIndex = i
			self:_runPhase(phaseConfig)
		end

		-- After all phases: zone is fully closed, max damage
		print("[StormSystem] All phases complete. Zone fully closed.")
	end)
end

function StormSystem:Stop()
	self._running = false
end

return StormSystem
```

**Client-side minimap zone rendering (outline):**

```luau
--!strict
-- StarterPlayerScripts/BattleRoyale/MinimapController.lua (zone portion)

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ZoneUpdateRemote = ReplicatedStorage.BattleRoyale.Remotes.ZoneUpdate

-- References to minimap UI circles (Frame objects with UICorner for circle shape)
local minimapFrame = script.Parent:WaitForChild("Minimap")
local currentZoneIndicator = minimapFrame:WaitForChild("CurrentZone")   -- ImageLabel, circle
local targetZoneIndicator = minimapFrame:WaitForChild("TargetZone")     -- ImageLabel, circle, dashed

local MINIMAP_SCALE = 0.5  -- studs-to-pixels ratio for your minimap

local function worldToMinimap(worldX: number, worldZ: number): (number, number)
	-- Convert world XZ to minimap pixel position relative to minimap center
	local minimapCenterX = minimapFrame.AbsoluteSize.X / 2
	local minimapCenterY = minimapFrame.AbsoluteSize.Y / 2
	return minimapCenterX + worldX * MINIMAP_SCALE, minimapCenterY + worldZ * MINIMAP_SCALE
end

local function updateZoneCircle(indicator: GuiObject, centerX: number, centerZ: number, radius: number)
	local px, py = worldToMinimap(centerX, centerZ)
	local pixelRadius = radius * MINIMAP_SCALE
	local diameter = pixelRadius * 2

	indicator.Position = UDim2.fromOffset(px - pixelRadius, py - pixelRadius)
	indicator.Size = UDim2.fromOffset(diameter, diameter)
end

ZoneUpdateRemote.OnClientEvent:Connect(function(
	curCenterX: number, curCenterZ: number, curRadius: number,
	tgtCenterX: number, tgtCenterZ: number, tgtRadius: number,
	isShrinking: boolean
)
	updateZoneCircle(currentZoneIndicator, curCenterX, curCenterZ, curRadius)
	updateZoneCircle(targetZoneIndicator, tgtCenterX, tgtCenterZ, tgtRadius)

	-- Show target zone indicator only when zone will shrink next
	targetZoneIndicator.Visible = (tgtRadius < curRadius)

	-- Visual feedback: change zone border color when shrinking
	if isShrinking then
		currentZoneIndicator.ImageColor3 = Color3.fromRGB(255, 80, 80)  -- red when moving
	else
		currentZoneIndicator.ImageColor3 = Color3.fromRGB(80, 160, 255) -- blue when static
	end
end)
```

---

### 3.3 Loot Spawning

```luau
--!strict
-- ServerScriptService/BattleRoyale/LootSpawner.lua

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local Config = require(ReplicatedStorage.BattleRoyale.Config)
local WeaponDefs = require(ReplicatedStorage.BattleRoyale.WeaponDefs)

local LootSpawner = {}

local spawnedLoot: { Instance } = {}

-- Select a rarity tier using weighted random
function LootSpawner:_rollRarity(): string
	local totalWeight = 0
	for _, weight in Config.RARITY_WEIGHTS do
		totalWeight += weight
	end

	local roll = math.random() * totalWeight
	local cumulative = 0
	for rarity, weight in Config.RARITY_WEIGHTS do
		cumulative += weight
		if roll <= cumulative then
			return rarity
		end
	end
	return "Common"
end

-- Pick a random weapon definition of the given rarity
function LootSpawner:_pickWeapon(rarity: string): string?
	local candidates = {}
	for weaponName, def in WeaponDefs do
		if def.rarity == rarity then
			table.insert(candidates, weaponName)
		end
	end
	if #candidates == 0 then return nil end
	return candidates[math.random(#candidates)]
end

function LootSpawner:SpawnAllLoot()
	self:DespawnAllLoot()

	local spawnPoints = CollectionService:GetTagged(Config.LOOT_SPAWN_TAG)
	print(`[LootSpawner] Spawning loot at {#spawnPoints} points`)

	for _, spawnPoint in spawnPoints do
		if not spawnPoint:IsA("BasePart") then continue end

		local rarity = self:_rollRarity()
		local weaponName = self:_pickWeapon(rarity)
		if not weaponName then continue end

		-- Clone weapon model from ServerStorage
		local weaponTemplate = ServerStorage:FindFirstChild("Weapons")
			and ServerStorage.Weapons:FindFirstChild(weaponName)
		if not weaponTemplate then continue end

		local lootItem = weaponTemplate:Clone()
		lootItem:PivotTo(spawnPoint.CFrame + Vector3.new(0, 1, 0))

		-- Attach metadata
		local rarityValue = Instance.new("StringValue")
		rarityValue.Name = "Rarity"
		rarityValue.Value = rarity
		rarityValue.Parent = lootItem

		-- Add proximity prompt for pickup
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Pick Up"
		prompt.ObjectText = `{weaponName} ({rarity})`
		prompt.HoldDuration = 0.15
		prompt.MaxActivationDistance = 8
		prompt.Parent = lootItem.PrimaryPart or lootItem:FindFirstChildWhichIsA("BasePart")

		lootItem.Parent = workspace.LootFolder

		table.insert(spawnedLoot, lootItem)
	end

	print(`[LootSpawner] Spawned {#spawnedLoot} items`)
end

function LootSpawner:DespawnAllLoot()
	for _, item in spawnedLoot do
		if item.Parent then
			item:Destroy()
		end
	end
	table.clear(spawnedLoot)
end

return LootSpawner
```

**Weapon definitions with rarity stat scaling:**

```luau
--!strict
-- ReplicatedStorage/BattleRoyale/WeaponDefs.lua

export type WeaponDef = {
	rarity: string,
	baseDamage: number,
	fireRate: number,     -- rounds per second
	magSize: number,
	reloadTime: number,   -- seconds
	range: number,        -- max effective range in studs
	weaponType: string,   -- "AR" | "Shotgun" | "SMG" | "Sniper" | "Pistol"
}

-- Rarity multipliers applied to base damage
local RARITY_DAMAGE_SCALE = {
	Common = 1.0,
	Uncommon = 1.15,
	Rare = 1.3,
	Epic = 1.5,
	Legendary = 1.75,
}

local WeaponDefs: { [string]: WeaponDef } = {
	-- Assault Rifles
	AssaultRifle_Common     = { rarity = "Common",    baseDamage = 18, fireRate = 5.5, magSize = 30, reloadTime = 2.2, range = 200, weaponType = "AR" },
	AssaultRifle_Uncommon   = { rarity = "Uncommon",  baseDamage = 21, fireRate = 5.5, magSize = 30, reloadTime = 2.0, range = 200, weaponType = "AR" },
	AssaultRifle_Rare       = { rarity = "Rare",      baseDamage = 23, fireRate = 5.5, magSize = 30, reloadTime = 1.8, range = 200, weaponType = "AR" },
	AssaultRifle_Epic       = { rarity = "Epic",      baseDamage = 27, fireRate = 6.0, magSize = 35, reloadTime = 1.6, range = 220, weaponType = "AR" },
	AssaultRifle_Legendary  = { rarity = "Legendary", baseDamage = 32, fireRate = 6.0, magSize = 35, reloadTime = 1.4, range = 240, weaponType = "AR" },

	-- Shotguns
	Shotgun_Common    = { rarity = "Common",    baseDamage = 70,  fireRate = 1.0, magSize = 5,  reloadTime = 4.5, range = 30,  weaponType = "Shotgun" },
	Shotgun_Rare      = { rarity = "Rare",      baseDamage = 85,  fireRate = 1.0, magSize = 5,  reloadTime = 4.0, range = 35,  weaponType = "Shotgun" },
	Shotgun_Legendary = { rarity = "Legendary", baseDamage = 110, fireRate = 1.1, magSize = 6,  reloadTime = 3.5, range = 40,  weaponType = "Shotgun" },

	-- SMGs
	SMG_Common   = { rarity = "Common",   baseDamage = 12, fireRate = 10.0, magSize = 25, reloadTime = 1.8, range = 80,  weaponType = "SMG" },
	SMG_Uncommon = { rarity = "Uncommon", baseDamage = 14, fireRate = 10.0, magSize = 30, reloadTime = 1.6, range = 90,  weaponType = "SMG" },
	SMG_Epic     = { rarity = "Epic",     baseDamage = 18, fireRate = 11.0, magSize = 35, reloadTime = 1.4, range = 100, weaponType = "SMG" },

	-- Snipers
	Sniper_Rare      = { rarity = "Rare",      baseDamage = 90,  fireRate = 0.5, magSize = 5, reloadTime = 3.0, range = 500, weaponType = "Sniper" },
	Sniper_Epic      = { rarity = "Epic",      baseDamage = 105, fireRate = 0.5, magSize = 5, reloadTime = 2.8, range = 550, weaponType = "Sniper" },
	Sniper_Legendary = { rarity = "Legendary", baseDamage = 130, fireRate = 0.5, magSize = 5, reloadTime = 2.5, range = 600, weaponType = "Sniper" },

	-- Pistols
	Pistol_Common   = { rarity = "Common",   baseDamage = 22, fireRate = 3.5, magSize = 12, reloadTime = 1.5, range = 120, weaponType = "Pistol" },
	Pistol_Uncommon = { rarity = "Uncommon", baseDamage = 25, fireRate = 3.5, magSize = 15, reloadTime = 1.4, range = 130, weaponType = "Pistol" },
}

return WeaponDefs
```

---

### 3.4 Elimination Tracking

```luau
--!strict
-- ServerScriptService/BattleRoyale/EliminationTracker.lua

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local KillFeedRemote = ReplicatedStorage.BattleRoyale.Remotes.KillFeed

export type EliminationRecord = {
	victim: string,
	killer: string?,
	placement: number,
	timestamp: number,
}

local EliminationTracker = {}

local killCounts: { [Player]: number } = {}
local placements: { [Player]: number } = {}
local eliminations: { EliminationRecord } = {}

function EliminationTracker:Reset()
	table.clear(killCounts)
	table.clear(placements)
	table.clear(eliminations)
end

function EliminationTracker:RecordElimination(victim: Player, killer: Player?, placement: number)
	-- Track placement
	placements[victim] = placement

	-- Track kill count
	if killer and killer ~= victim then
		killCounts[killer] = (killCounts[killer] or 0) + 1
	end

	-- Log the elimination
	local record: EliminationRecord = {
		victim = victim.Name,
		killer = if killer and killer ~= victim then killer.Name else nil,
		placement = placement,
		timestamp = os.clock(),
	}
	table.insert(eliminations, record)

	-- Broadcast kill feed to all clients
	local killerName = record.killer or "The Storm"
	KillFeedRemote:FireAllClients(killerName, victim.Name, placement)

	-- Drop victim's inventory at their death location
	self:_dropInventory(victim)
end

function EliminationTracker:RecordDisconnect(player: Player, placement: number)
	placements[player] = placement

	local record: EliminationRecord = {
		victim = player.Name,
		killer = nil,
		placement = placement,
		timestamp = os.clock(),
	}
	table.insert(eliminations, record)

	KillFeedRemote:FireAllClients("Disconnect", player.Name, placement)
end

function EliminationTracker:GetKillCount(player: Player): number
	return killCounts[player] or 0
end

function EliminationTracker:GetPlacement(player: Player): number?
	return placements[player]
end

function EliminationTracker:_dropInventory(player: Player)
	-- Clone the player's held tools/weapons to the ground at their death position
	local character = player.Character
	if not character then return end

	local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not rootPart then return end

	local dropPosition = rootPart.CFrame

	-- Move backpack tools to workspace as loot
	for _, tool in player.Backpack:GetChildren() do
		if tool:IsA("Tool") then
			tool.Parent = workspace.LootFolder
			local handle = tool:FindFirstChild("Handle") :: BasePart?
			if handle then
				handle.CFrame = dropPosition * CFrame.new(
					math.random(-3, 3), 1, math.random(-3, 3)
				)
			end
		end
	end
end

function EliminationTracker:FinalizeResults(winner: Player?)
	print("[EliminationTracker] Match Results:")
	if winner then
		placements[winner] = 1
		print(`  1st: {winner.Name} ({self:GetKillCount(winner)} kills)`)
	end

	-- Sort and print top placements
	local sorted: { { player: string, placement: number } } = {}
	for player, placement in placements do
		table.insert(sorted, { player = player.Name, placement = placement })
	end
	table.sort(sorted, function(a, b) return a.placement < b.placement end)

	for _, entry in sorted do
		print(`  #{entry.placement}: {entry.player}`)
	end

	-- TODO: Award XP based on placement and kills
	-- XP formula example: base XP + (kills * 50) + (placement bonus)
end

return EliminationTracker
```

---

### 3.5 Spectator System

```luau
--!strict
-- ServerScriptService/BattleRoyale/SpectatorSystem.lua

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SpectatorTargetRemote = ReplicatedStorage.BattleRoyale.Remotes.SpectatorTarget

local SpectatorSystem = {}

-- Map of spectating player -> currently watched player
local spectatorTargets: { [Player]: Player } = {}
-- Map of spectating player -> index in alive list (for cycling)
local spectatorIndex: { [Player]: number } = {}

function SpectatorSystem:Reset()
	table.clear(spectatorTargets)
	table.clear(spectatorIndex)
end

function SpectatorSystem:BeginSpectating(eliminated: Player, alivePlayers: { Player })
	if #alivePlayers == 0 then return end

	-- Pick first alive player as initial target
	local targetIndex = 1

	-- Prefer the player's killer if they're still alive
	spectatorIndex[eliminated] = targetIndex
	spectatorTargets[eliminated] = alivePlayers[targetIndex]

	-- Tell the eliminated player's client to enter spectator mode
	SpectatorTargetRemote:FireClient(
		eliminated,
		"StartSpectating",
		alivePlayers[targetIndex]
	)
end

function SpectatorSystem:CycleTarget(spectator: Player, direction: number, alivePlayers: { Player })
	if #alivePlayers == 0 then return end
	if not spectatorIndex[spectator] then return end

	local currentIdx = spectatorIndex[spectator]
	local newIdx = ((currentIdx - 1 + direction) % #alivePlayers) + 1

	spectatorIndex[spectator] = newIdx
	spectatorTargets[spectator] = alivePlayers[newIdx]

	SpectatorTargetRemote:FireClient(
		spectator,
		"SwitchTarget",
		alivePlayers[newIdx]
	)
end

function SpectatorSystem:GetTarget(spectator: Player): Player?
	return spectatorTargets[spectator]
end

return SpectatorSystem
```

**Client-side spectator camera controller:**

```luau
--!strict
-- StarterPlayerScripts/BattleRoyale/SpectatorController.lua

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")

local SpectatorTargetRemote = ReplicatedStorage.BattleRoyale.Remotes.SpectatorTarget
local Config = require(ReplicatedStorage.BattleRoyale.Config)

local camera = workspace.CurrentCamera
local isSpectating = false
local currentTarget: Player? = nil
local cameraOffset = Vector3.new(0, 8, 12)
local renderConnection: RBXScriptConnection? = nil

local function followTarget()
	if not currentTarget then return end
	local character = currentTarget.Character
	if not character then return end
	local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not rootPart then return end

	camera.CameraType = Enum.CameraType.Scriptable
	local targetCF = CFrame.new(rootPart.Position + cameraOffset, rootPart.Position)
	camera.CFrame = camera.CFrame:Lerp(targetCF, 0.1)
end

local function startSpectating(target: Player)
	isSpectating = true
	currentTarget = target

	-- Disconnect any existing render loop
	if renderConnection then
		renderConnection:Disconnect()
	end

	renderConnection = RunService.RenderStepped:Connect(followTarget)
end

local function stopSpectating()
	isSpectating = false
	currentTarget = nil
	if renderConnection then
		renderConnection:Disconnect()
		renderConnection = nil
	end
	camera.CameraType = Enum.CameraType.Custom
end

SpectatorTargetRemote.OnClientEvent:Connect(function(action: string, target: Player?)
	if action == "StartSpectating" and target then
		startSpectating(target)
	elseif action == "SwitchTarget" and target then
		currentTarget = target
	elseif action == "StopSpectating" then
		stopSpectating()
	end
end)

-- Cycle targets with left/right arrow or Q/E keys
local lastCycleTime = 0
UserInputService.InputBegan:Connect(function(input, gameProcessed)
	if gameProcessed or not isSpectating then return end
	if os.clock() - lastCycleTime < Config.SPECTATOR_CYCLE_COOLDOWN then return end

	local direction = 0
	if input.KeyCode == Enum.KeyCode.E or input.KeyCode == Enum.KeyCode.Right then
		direction = 1
	elseif input.KeyCode == Enum.KeyCode.Q or input.KeyCode == Enum.KeyCode.Left then
		direction = -1
	end

	if direction ~= 0 then
		lastCycleTime = os.clock()
		-- Fire to server to get next valid target
		ReplicatedStorage.BattleRoyale.Remotes.SpectatorTarget:FireServer("CycleTarget", direction)
	end
end)
```

---

### 3.6 Drop / Spawn System

```luau
--!strict
-- ServerScriptService/BattleRoyale/DropSystem.lua

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.BattleRoyale.Config)
local DropRemote = ReplicatedStorage.BattleRoyale.Remotes.DropInput

local DropSystem = {}

local deployedPlayers: { [Player]: boolean } = {}

function DropSystem:DeployAllPlayers(players: { Player })
	table.clear(deployedPlayers)

	-- Determine map center for the drop position
	local mapCenter = Vector3.new(0, Config.DROP_HEIGHT, 0)

	for i, player in players do
		if not player.Character then continue end

		local humanoid = player.Character:FindFirstChildOfClass("Humanoid")
		local rootPart = player.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
		if not humanoid or not rootPart then continue end

		-- Spread players along a line in the sky
		local offset = Vector3.new((i - #players / 2) * 6, 0, 0)
		local spawnCF = CFrame.new(mapCenter + offset)
		player.Character:PivotTo(spawnCF)

		-- Disable default movement during drop
		humanoid.PlatformStand = true

		deployedPlayers[player] = true

		-- Notify client to begin free-fall camera
		DropRemote:FireClient(player, "BeginDrop", spawnCF.Position)
	end

	-- Server-side drop physics (simplified: move characters downward)
	task.spawn(function()
		while true do
			local anyDropping = false
			for player, isDropping in deployedPlayers do
				if not isDropping then continue end
				if not player.Character then continue end

				local rootPart = player.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
				if not rootPart then continue end

				local height = rootPart.Position.Y
				local speed: number

				if height > Config.PARACHUTE_DEPLOY_HEIGHT then
					speed = Config.FALL_SPEED
				else
					speed = Config.PARACHUTE_SPEED
					-- Notify client to deploy parachute visual (once)
				end

				-- Ground check: stop drop when near ground
				local rayResult = workspace:Raycast(
					rootPart.Position,
					Vector3.new(0, -5, 0),
					RaycastParams.new()
				)
				if rayResult or height <= 5 then
					-- Player has landed
					local humanoid = player.Character:FindFirstChildOfClass("Humanoid")
					if humanoid then
						humanoid.PlatformStand = false
					end
					deployedPlayers[player] = false
					DropRemote:FireClient(player, "Landed")
					continue
				end

				-- Move downward
				rootPart.CFrame = rootPart.CFrame - Vector3.new(0, speed * 0.03, 0)
				anyDropping = true
			end

			if not anyDropping then break end
			task.wait()
		end
	end)
end

-- Allow client to send lateral movement input during drop
DropRemote.OnServerEvent:Connect(function(player, action, direction: Vector3?)
	if action ~= "MoveInput" then return end
	if not deployedPlayers[player] then return end
	if not direction then return end

	local rootPart = player.Character and player.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not rootPart then return end

	-- Clamp lateral movement speed
	local lateralSpeed = 40
	local clampedDir = Vector3.new(
		math.clamp(direction.X, -1, 1),
		0,
		math.clamp(direction.Z, -1, 1)
	).Unit * lateralSpeed * 0.03

	rootPart.CFrame = rootPart.CFrame + clampedDir
end)

function DropSystem:Reset()
	table.clear(deployedPlayers)
end

return DropSystem
```

---

## 4. Progression Design

Battle royale progression must never grant permanent power advantages. All combat is
skill-based with equal access to loot on the ground.

### XP and Leveling

| Action | XP Reward |
|---|---|
| Survive to top 50% | +50 XP |
| Survive to top 25% | +100 XP |
| Survive to top 10% | +200 XP |
| Victory Royale (1st) | +500 XP |
| Per elimination | +50 XP |
| Damage dealt (per 100) | +10 XP |
| Match completed | +25 XP |

### Cosmetic Unlocks

- **Level milestones** unlock free cosmetic items (skins, emotes, trails).
- **Seasonal ranks** (Bronze/Silver/Gold/Diamond/Champion) based on placement consistency.
- **Lifetime stats** tracked: total wins, total kills, K/D ratio, matches played.

### Battle Pass Integration

Each season (6-8 weeks) offers a battle pass with 100 tiers:
- **Free track:** ~25 free rewards spread across tiers (basic skins, sprays, small currency).
- **Premium track:** unlocked via Robux purchase, adds rewards at every tier.
- Progression is XP-based, not pay-to-skip (or offer limited tier-buy for late joiners).

---

## 5. Monetization Strategy

**Core principle:** No pay-to-win. All purchasable items are cosmetic only.

### Revenue Streams

| Product | Pricing (Robux) | Type |
|---|---|---|
| Battle Pass (seasonal) | 499-799 | Seasonal content |
| Character Skins | 100-500 | Cosmetic |
| Weapon Skins | 50-250 | Cosmetic (visual only) |
| Emotes / Dances | 75-200 | Cosmetic |
| Glider / Parachute Skins | 100-300 | Cosmetic |
| Drop Trail Effects | 50-150 | Cosmetic |

### Gamepass Ideas

| Gamepass | Price | Benefit |
|---|---|---|
| VIP | 499 | 2x XP, exclusive lobby area, VIP badge |
| Stat Tracker | 199 | Detailed match stats, heatmaps, leaderboard access |
| Emote Pack | 299 | Bundle of 10 emotes |

### Anti-P2W Safeguards

- Weapon skins never modify stats (damage, fire rate, accuracy stay identical).
- No purchasable weapons, ammo, or armor.
- XP boosts are acceptable but must not gate gameplay content.
- Matchmaking never considers spend amount.

---

## 6. Performance Considerations

### Many Players in One Server

- **Server tick budget:** Target 30Hz server heartbeat. Profile with `debug.profilebegin()`.
- **Player cap:** Start with 30-50 players. Stress test before going higher.
- **Character replication:** Use `StreamingEnabled = true` to only replicate nearby characters.
- **StreamingIntegrity:** Set to `Enum.StreamingIntegrity.Minimum` for BR maps.
- **StreamingTargetRadius:** 256-512 studs depending on map size.

### Weapon / Projectile Optimization

```luau
-- Use raycasts for hitscan weapons, NOT physical Part projectiles
local function fireHitscan(origin: Vector3, direction: Vector3, maxRange: number): RaycastResult?
    local params = RaycastParams.new()
    params.FilterType = Enum.RaycastFilterType.Exclude
    params.FilterDescendantsInstances = { player.Character }

    return workspace:Raycast(origin, direction.Unit * maxRange, params)
end
-- For visual bullet trails, use Beams or tweened Attachments (client-side only)
```

- **Hitscan weapons:** One `workspace:Raycast()` per shot. Cheap and accurate.
- **Projectile weapons (rockets, grenades):** Simulate trajectory with math on server,
  use client-side visual parts that get cleaned up.
- **Never create physical Part projectiles** for every bullet. This kills server performance.

### Map Optimization

- **Part count:** Keep under 10,000 unique parts. Use MeshParts over Unions.
- **Texture budget:** Reuse materials. Use Roblox PBR materials where possible.
- **LOD:** Place distant scenery as low-poly Decals or MeshParts with minimal collision.
- **Destroy loot items** immediately on pickup (do not just hide them).
- **Workspace cleanup:** Remove dead player ragdolls after 5 seconds.

### Distant Player Rendering

```luau
-- Reduce render fidelity for distant players on the client
RunService.Heartbeat:Connect(function()
    local myPos = localPlayer.Character and localPlayer.Character.PrimaryPart
    if not myPos then return end

    for _, otherPlayer in Players:GetPlayers() do
        if otherPlayer == localPlayer then continue end
        local otherChar = otherPlayer.Character
        if not otherChar then continue end

        local dist = (otherChar:GetPivot().Position - myPos.Position).Magnitude
        -- Beyond 200 studs: hide accessories, simplify rendering
        for _, accessory in otherChar:GetChildren() do
            if accessory:IsA("Accessory") then
                accessory:FindFirstChildWhichIsA("BasePart").LocalTransparencyModifier =
                    if dist > 200 then 1 else 0
            end
        end
    end
end)
```

### Network Optimization

- Batch zone updates: broadcast once per second, not every frame.
- Kill feed uses `FireAllClients` sparingly (only on elimination events).
- Loot pickups: use ProximityPrompt server validation, do not replicate all loot state every frame.

---

## 7. Launch Checklist

### Zone / Storm Balance
- [ ] Zone timing tested with minimum player count (does final zone close before match drags)
- [ ] Zone timing tested with maximum player count (enough time to loot and rotate)
- [ ] Zone damage per phase escalates appropriately (early = warning, late = lethal)
- [ ] Zone center randomization stays within map bounds
- [ ] Zone visual indicator is clear on minimap at all phases

### Loot Distribution
- [ ] Every landing area has at least 2-3 loot spawn points
- [ ] Rarity distribution tested over 100+ matches (Legendary < 5% of drops)
- [ ] No "dead zones" where players land with zero loot access
- [ ] High-tier loot areas balanced by higher risk (more exposed, central)
- [ ] Weapon balance: no single weapon dominates all ranges

### Player Count
- [ ] Minimum player count starts a match correctly (tested with 4 players)
- [ ] Maximum player count does not cause server lag (profiled at 50 players)
- [ ] Server FPS stays above 25 at max player count
- [ ] Lobby handles players joining mid-countdown gracefully
- [ ] Players disconnecting mid-match do not break match state

### Spectator Mode
- [ ] Eliminated player camera transitions smoothly to spectator view
- [ ] Cycling between alive players works with Q/E keys
- [ ] Spectator cannot interact with game world (no input leaks)
- [ ] Spectator UI shows target player name, health, kill count
- [ ] Spectating ends and returns to lobby on match end

### Progression and Rewards
- [ ] XP awarded correctly based on placement and kills
- [ ] Battle pass tiers increment with XP
- [ ] Cosmetic items apply correctly in lobby and in-match
- [ ] Leaderboard updates after each match

### Security
- [ ] All damage calculations are server-authoritative
- [ ] Loot pickup validated server-side (proximity check, item exists, not already taken)
- [ ] Remote events rate-limited (especially weapon fire and movement)
- [ ] Kill credit cannot be spoofed via client
- [ ] Zone damage cannot be bypassed by client exploits
- [ ] Inventory manipulation impossible from client (server owns inventory state)

### Mobile and Performance
- [ ] Touch controls for drop, aiming, looting tested on mobile
- [ ] Frame rate acceptable on low-end devices with StreamingEnabled
- [ ] UI scales correctly on small screens
- [ ] Part count under budget at all match phases

### Pre-Launch Stress Test
- [ ] Run 10+ full matches with target player count
- [ ] Monitor server memory (should not climb across matches -- check for leaks)
- [ ] Verify cleanup phase removes all loot, resets all systems
- [ ] Test rapid back-to-back matches (no state bleed between rounds)
