# Horror Genre Template

## 1. Genre Overview

**Core Experience Loop:** Explore --> Tension Builds --> Scare --> Survive

Horror games on Roblox succeed when atmosphere dominates every design decision. The player should feel uneasy before anything dangerous actually happens. Sound design, lighting, and pacing are more important than complex mechanics.

**Design Pillars:**
- **Atmosphere is everything.** Darkness, fog, ambient drones, and environmental storytelling create dread without a single jumpscare.
- **Vulnerability drives tension.** The player must feel underpowered — limited light, no weapons, restricted movement.
- **Pacing controls fear.** Long stretches of quiet make sudden events devastating. Never spam scares.
- **Mystery sustains engagement.** Unanswered questions ("What happened here?") pull players deeper than action alone.

**Reference Games:**
- **Doors** — Procedural rooms, distinct monster behaviors, learn-or-die pattern recognition.
- **The Mimic** — Narrative-driven chapters, Japanese horror aesthetics, puzzle-gated progression.
- **Apeirophobia** — Liminal spaces, environmental horror, backrooms-inspired level design.
- **Identity Fraud** — Maze exploration, NPC imposters, social deduction elements.

---

## 2. Architecture Blueprint

```
StarterPlayerScripts/
  HorrorClient/
    AtmosphereController.luau      -- Lighting/fog transitions on the client
    FlashlightController.luau      -- Toggle, battery UI, light attachment
    JumpscareController.luau       -- Camera takeover, sound stingers, screen flash
    SoundController.luau           -- Ambient loops, positional audio, stingers
    UIController.luau              -- Battery meter, inventory, interaction prompts

ServerScriptService/
  HorrorServer/
    MonsterAI.luau                 -- State machine: Dormant/Patrol/Alert/Chase/Kill
    EventSequencer.luau            -- Proximity/progress-triggered scripted events
    DoorKeySystem.luau             -- Locked doors, key items, inventory tracking
    ProgressionManager.luau        -- Room/level advancement, difficulty scaling
    GameManager.luau               -- Round lifecycle, player spawning, win/loss

ReplicatedStorage/
  HorrorShared/
    Config.luau                    -- Tuning constants (speeds, timers, thresholds)
    Types.luau                     -- Type definitions for shared data
    Remotes/                       -- RemoteEvents and RemoteFunctions
      AtmosphereRemote.luau
      JumpscareRemote.luau
      FlashlightRemote.luau
      MonsterRemote.luau
```

**Key Modules:**

| Module | Responsibility | Runs On |
|---|---|---|
| AtmosphereManager | Dynamic lighting, fog, color correction transitions | Client |
| MonsterAI | Enemy state machine, pathfinding, line of sight | Server |
| EventSequencer | Trigger scripted horror events by proximity/progress | Server |
| JumpscareSystem | Camera control, scare visuals, sound stingers | Client |
| SoundManager | Ambient loops, positional audio, dynamic mixing | Client |
| FlashlightSystem | Light attachment, battery drain, toggle, pickups | Client + Server |
| DoorKeySystem | Locked doors, key inventory, unlock logic | Server |

---

## 3. Core Systems

### 3.1 Atmosphere System

Dynamically controls Lighting properties to shift mood between safe and dangerous states. Uses TweenService for smooth transitions.

```luau
-- AtmosphereController.luau (StarterPlayerScripts)

local Lighting = game:GetService("Lighting")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local AtmosphereController = {}

-- Preset definitions for different mood states
local PRESETS = {
	Safe = {
		Ambient = Color3.fromRGB(80, 80, 90),
		OutdoorAmbient = Color3.fromRGB(80, 80, 90),
		Brightness = 1.2,
		FogEnd = 500,
		FogColor = Color3.fromRGB(30, 30, 40),
		ColorCorrection = {
			Brightness = 0,
			Contrast = 0.05,
			Saturation = -0.1,
			TintColor = Color3.fromRGB(255, 245, 240),
		},
		Atmosphere = {
			Density = 0.15,
			Offset = 0,
			Color = Color3.fromRGB(60, 60, 70),
			Decay = Color3.fromRGB(40, 40, 50),
			Glare = 0,
			Haze = 2,
		},
	},

	Uneasy = {
		Ambient = Color3.fromRGB(40, 40, 55),
		OutdoorAmbient = Color3.fromRGB(40, 40, 55),
		Brightness = 0.6,
		FogEnd = 250,
		FogColor = Color3.fromRGB(15, 15, 25),
		ColorCorrection = {
			Brightness = -0.05,
			Contrast = 0.15,
			Saturation = -0.3,
			TintColor = Color3.fromRGB(220, 220, 240),
		},
		Atmosphere = {
			Density = 0.25,
			Offset = 0,
			Color = Color3.fromRGB(40, 40, 55),
			Decay = Color3.fromRGB(25, 25, 35),
			Glare = 0,
			Haze = 4,
		},
	},

	Danger = {
		Ambient = Color3.fromRGB(15, 10, 20),
		OutdoorAmbient = Color3.fromRGB(15, 10, 20),
		Brightness = 0.1,
		FogEnd = 80,
		FogColor = Color3.fromRGB(5, 5, 10),
		ColorCorrection = {
			Brightness = -0.12,
			Contrast = 0.3,
			Saturation = -0.5,
			TintColor = Color3.fromRGB(200, 180, 200),
		},
		Atmosphere = {
			Density = 0.45,
			Offset = 0,
			Color = Color3.fromRGB(20, 15, 25),
			Decay = Color3.fromRGB(10, 10, 15),
			Glare = 0,
			Haze = 8,
		},
	},

	Panic = {
		Ambient = Color3.fromRGB(5, 0, 0),
		OutdoorAmbient = Color3.fromRGB(5, 0, 0),
		Brightness = 0.02,
		FogEnd = 40,
		FogColor = Color3.fromRGB(2, 0, 0),
		ColorCorrection = {
			Brightness = -0.2,
			Contrast = 0.4,
			Saturation = -0.7,
			TintColor = Color3.fromRGB(180, 140, 140),
		},
		Atmosphere = {
			Density = 0.6,
			Offset = 0,
			Color = Color3.fromRGB(10, 5, 5),
			Decay = Color3.fromRGB(5, 0, 0),
			Glare = 0,
			Haze = 10,
		},
	},
}

local DEFAULT_TWEEN_DURATION = 3.0
local activeTweens: { Tween } = {}
local colorCorrection: ColorCorrectionEffect? = nil
local atmosphereInstance: Atmosphere? = nil
local currentPreset: string = "Safe"

-- Initialize or find existing post-processing instances
function AtmosphereController.Init()
	-- ColorCorrectionEffect
	colorCorrection = Lighting:FindFirstChildOfClass("ColorCorrectionEffect")
	if not colorCorrection then
		colorCorrection = Instance.new("ColorCorrectionEffect")
		colorCorrection.Name = "HorrorColorCorrection"
		colorCorrection.Parent = Lighting
	end

	-- Atmosphere instance
	atmosphereInstance = Lighting:FindFirstChildOfClass("Atmosphere")
	if not atmosphereInstance then
		atmosphereInstance = Instance.new("Atmosphere")
		atmosphereInstance.Name = "HorrorAtmosphere"
		atmosphereInstance.Parent = Lighting
	end

	-- Apply safe preset immediately on load
	AtmosphereController.SetPreset("Safe", 0)
end

-- Cancel all active tweens to avoid conflicts
local function cancelActiveTweens()
	for _, tween in activeTweens do
		tween:Cancel()
	end
	table.clear(activeTweens)
end

-- Tween a single instance's properties
local function tweenProperties(instance: Instance, properties: { [string]: any }, duration: number)
	local tweenInfo = TweenInfo.new(duration, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)
	local tween = TweenService:Create(instance, tweenInfo, properties)
	table.insert(activeTweens, tween)
	tween:Play()
end

-- Transition to a named preset over a given duration
function AtmosphereController.SetPreset(presetName: string, duration: number?)
	local preset = PRESETS[presetName]
	if not preset then
		warn(`[Atmosphere] Unknown preset: {presetName}`)
		return
	end

	local tweenDuration = duration or DEFAULT_TWEEN_DURATION
	cancelActiveTweens()
	currentPreset = presetName

	-- Tween Lighting properties
	tweenProperties(Lighting, {
		Ambient = preset.Ambient,
		OutdoorAmbient = preset.OutdoorAmbient,
		Brightness = preset.Brightness,
		FogEnd = preset.FogEnd,
		FogColor = preset.FogColor,
	}, tweenDuration)

	-- Tween ColorCorrection
	if colorCorrection then
		tweenProperties(colorCorrection, {
			Brightness = preset.ColorCorrection.Brightness,
			Contrast = preset.ColorCorrection.Contrast,
			Saturation = preset.ColorCorrection.Saturation,
			TintColor = preset.ColorCorrection.TintColor,
		}, tweenDuration)
	end

	-- Tween Atmosphere instance
	if atmosphereInstance then
		tweenProperties(atmosphereInstance, {
			Density = preset.Atmosphere.Density,
			Offset = preset.Atmosphere.Offset,
			Color = preset.Atmosphere.Color,
			Decay = preset.Atmosphere.Decay,
			Glare = preset.Atmosphere.Glare,
			Haze = preset.Atmosphere.Haze,
		}, tweenDuration)
	end
end

-- Get the current active preset name
function AtmosphereController.GetCurrentPreset(): string
	return currentPreset
end

-- Flicker effect: rapid toggling between two presets
function AtmosphereController.Flicker(flickerCount: number, intervalSeconds: number)
	task.spawn(function()
		local originalPreset = currentPreset
		for i = 1, flickerCount do
			AtmosphereController.SetPreset("Panic", 0.05)
			task.wait(intervalSeconds * 0.3)
			AtmosphereController.SetPreset(originalPreset, 0.05)
			task.wait(intervalSeconds * 0.7)
		end
	end)
end

-- Listen for server-driven atmosphere changes
function AtmosphereController.ConnectRemotes()
	local remotes = ReplicatedStorage:WaitForChild("HorrorShared"):WaitForChild("Remotes")
	local atmosphereRemote = remotes:WaitForChild("AtmosphereRemote") :: RemoteEvent

	atmosphereRemote.OnClientEvent:Connect(function(presetName: string, duration: number?)
		AtmosphereController.SetPreset(presetName, duration)
	end)
end

return AtmosphereController
```

### 3.2 Monster/Enemy AI State Machine

Server-authoritative enemy AI using a finite state machine with five states: Dormant, Patrol, Alert, Chase, and Kill.

```luau
-- MonsterAI.luau (ServerScriptService)

local Players = game:GetService("Players")
local PathfindingService = game:GetService("PathfindingService")
local RunService = game:GetService("RunService")

local MonsterAI = {}
MonsterAI.__index = MonsterAI

export type MonsterState = "Dormant" | "Patrol" | "Alert" | "Chase" | "Kill"

export type MonsterConfig = {
	PatrolSpeed: number,        -- Studs/sec during patrol (e.g. 10)
	ChaseSpeed: number,         -- Must exceed player WalkSpeed (e.g. 22, player is 16)
	SightRange: number,         -- Max raycast distance in studs (e.g. 60)
	SightAngle: number,         -- Field of view half-angle in degrees (e.g. 55)
	HearingRange: number,       -- Distance to detect running players (e.g. 30)
	AlertDuration: number,      -- Seconds spent investigating before returning (e.g. 8)
	SearchTimeout: number,      -- How long to search a hiding spot before giving up (e.g. 12)
	KillRange: number,          -- Distance to trigger kill (e.g. 5)
	PatrolWaypoints: { Vector3 },
}

local DEFAULT_CONFIG: MonsterConfig = {
	PatrolSpeed = 10,
	ChaseSpeed = 22,
	SightRange = 60,
	SightAngle = 55,
	HearingRange = 30,
	AlertDuration = 8,
	SearchTimeout = 12,
	KillRange = 5,
	PatrolWaypoints = {},
}

-- Hiding spots tagged with CollectionService tag "HidingSpot"
local CollectionService = game:GetService("CollectionService")

function MonsterAI.new(model: Model, config: MonsterConfig?)
	local self = setmetatable({}, MonsterAI)

	self.Model = model
	self.Humanoid = model:FindFirstChildOfClass("Humanoid") :: Humanoid
	self.RootPart = model:FindFirstChild("HumanoidRootPart") :: BasePart
	self.Config = config or DEFAULT_CONFIG
	self.State = "Dormant" :: MonsterState
	self.Target = nil :: Player?
	self.LastKnownPosition = nil :: Vector3?
	self.AlertTimer = 0
	self.SearchTimer = 0
	self.CurrentWaypointIndex = 1
	self.Active = false
	self.Path = PathfindingService:CreatePath({
		AgentRadius = 3,
		AgentHeight = 6,
		AgentCanJump = false,
		AgentCanClimb = false,
	})

	return self
end

-- Activate the monster AI loop
function MonsterAI:Start()
	self.Active = true
	self:SetState("Patrol")

	task.spawn(function()
		while self.Active do
			self:Update()
			task.wait(0.1) -- 10 Hz tick rate for AI
		end
	end)
end

-- Deactivate the monster
function MonsterAI:Stop()
	self.Active = false
	self.Humanoid.WalkSpeed = 0
end

-- Transition to a new state
function MonsterAI:SetState(newState: MonsterState)
	if self.State == newState then
		return
	end

	local oldState = self.State
	self.State = newState

	-- State entry logic
	if newState == "Dormant" then
		self.Humanoid.WalkSpeed = 0
		self.Target = nil
	elseif newState == "Patrol" then
		self.Humanoid.WalkSpeed = self.Config.PatrolSpeed
		self.Target = nil
		self.AlertTimer = 0
	elseif newState == "Alert" then
		self.Humanoid.WalkSpeed = self.Config.PatrolSpeed * 0.7
		self.AlertTimer = self.Config.AlertDuration
	elseif newState == "Chase" then
		self.Humanoid.WalkSpeed = self.Config.ChaseSpeed
	elseif newState == "Kill" then
		self.Humanoid.WalkSpeed = 0
	end

	-- Fire event for client-side reactions (animation, sound, atmosphere)
	local remotes = game.ReplicatedStorage:FindFirstChild("HorrorShared")
	if remotes then
		local monsterRemote = remotes.Remotes:FindFirstChild("MonsterRemote") :: RemoteEvent?
		if monsterRemote then
			monsterRemote:FireAllClients(self.Model.Name, newState, oldState)
		end
	end
end

-- Main update tick dispatches to per-state handlers
function MonsterAI:Update()
	local handler = self["_Update_" .. self.State]
	if handler then
		handler(self)
	end
end

-- DORMANT: Do nothing. Activated externally by EventSequencer.
function MonsterAI:_Update_Dormant()
	-- No-op. Awaiting activation trigger.
end

-- PATROL: Follow waypoints, scan for players.
function MonsterAI:_Update_Patrol()
	local waypoints = self.Config.PatrolWaypoints
	if #waypoints == 0 then
		return
	end

	-- Move toward current waypoint
	local targetWaypoint = waypoints[self.CurrentWaypointIndex]
	local distToWaypoint = (self.RootPart.Position - targetWaypoint).Magnitude

	if distToWaypoint < 5 then
		self.CurrentWaypointIndex = (self.CurrentWaypointIndex % #waypoints) + 1
		targetWaypoint = waypoints[self.CurrentWaypointIndex]
	end

	self:NavigateTo(targetWaypoint)

	-- Check for visible or audible players
	local detectedPlayer = self:DetectPlayer()
	if detectedPlayer then
		self.Target = detectedPlayer
		self.LastKnownPosition = self:GetPlayerPosition(detectedPlayer)
		self:SetState("Chase")
	end
end

-- ALERT: Investigate last known position, then return to patrol.
function MonsterAI:_Update_Alert()
	self.AlertTimer -= 0.1

	if self.LastKnownPosition then
		local dist = (self.RootPart.Position - self.LastKnownPosition).Magnitude
		if dist < 5 then
			self.LastKnownPosition = nil -- Reached investigation point
		else
			self:NavigateTo(self.LastKnownPosition)
		end
	end

	-- Check if player is visible again during search
	local detectedPlayer = self:DetectPlayer()
	if detectedPlayer then
		self.Target = detectedPlayer
		self.LastKnownPosition = self:GetPlayerPosition(detectedPlayer)
		self:SetState("Chase")
		return
	end

	-- Give up after alert duration expires
	if self.AlertTimer <= 0 then
		self:SetState("Patrol")
	end
end

-- CHASE: Pursue target. If target hides, switch to searching. If lost, go to Alert.
function MonsterAI:_Update_Chase()
	if not self.Target or not self.Target.Character then
		self:SetState("Alert")
		return
	end

	local playerPos = self:GetPlayerPosition(self.Target)
	if not playerPos then
		self:SetState("Alert")
		return
	end

	-- Check if player is in a hiding spot
	if self:IsPlayerHiding(self.Target) then
		self.LastKnownPosition = playerPos
		self.SearchTimer = self.Config.SearchTimeout
		self:SearchHidingSpots()
		return
	end

	-- Check kill range
	local distToPlayer = (self.RootPart.Position - playerPos).Magnitude
	if distToPlayer <= self.Config.KillRange then
		self:SetState("Kill")
		self:ExecuteKill(self.Target)
		return
	end

	-- Check if we still have line of sight
	if self:HasLineOfSight(playerPos) then
		self.LastKnownPosition = playerPos
		self:NavigateTo(playerPos)
	else
		-- Lost sight — go to last known position
		self.LastKnownPosition = playerPos
		self:SetState("Alert")
	end
end

-- KILL: Execute kill sequence on the target player.
function MonsterAI:_Update_Kill()
	-- Kill state is handled by ExecuteKill; after a delay, return to Patrol.
end

-- Execute the kill: trigger jumpscare, then respawn the player
function MonsterAI:ExecuteKill(player: Player)
	local remotes = game.ReplicatedStorage:FindFirstChild("HorrorShared")
	if remotes then
		local jumpscareRemote = remotes.Remotes:FindFirstChild("JumpscareRemote") :: RemoteEvent?
		if jumpscareRemote then
			jumpscareRemote:FireClient(player, self.Model.Name)
		end
	end

	-- Wait for jumpscare to play, then kill
	task.delay(1.5, function()
		local character = player.Character
		if character then
			local humanoid = character:FindFirstChildOfClass("Humanoid")
			if humanoid then
				humanoid.Health = 0
			end
		end

		-- Return to patrol after kill
		task.delay(2, function()
			self:SetState("Patrol")
		end)
	end)
end

-- Navigate to a world position using PathfindingService
function MonsterAI:NavigateTo(position: Vector3)
	local success, errorMessage = pcall(function()
		self.Path:ComputeAsync(self.RootPart.Position, position)
	end)

	if success and self.Path.Status == Enum.PathStatus.Success then
		local waypoints = self.Path:GetWaypoints()
		for _, waypoint in waypoints do
			if not self.Active then
				break
			end
			self.Humanoid:MoveTo(waypoint.Position)
			local reached = self.Humanoid.MoveToFinished:Wait()
			if not reached then
				break
			end
		end
	else
		-- Fallback: move directly toward position
		self.Humanoid:MoveTo(position)
	end
end

-- Detect nearest visible or audible player
function MonsterAI:DetectPlayer(): Player?
	local nearest: Player? = nil
	local nearestDist = math.huge

	for _, player in Players:GetPlayers() do
		local playerPos = self:GetPlayerPosition(player)
		if not playerPos then
			continue
		end

		-- Skip players who are hiding
		if self:IsPlayerHiding(player) then
			continue
		end

		local dist = (self.RootPart.Position - playerPos).Magnitude

		-- Check hearing range (running players are louder)
		local isRunning = self:IsPlayerRunning(player)
		local effectiveHearingRange = if isRunning then self.Config.HearingRange * 1.5 else self.Config.HearingRange

		local detected = false

		if dist <= effectiveHearingRange then
			detected = true
		elseif dist <= self.Config.SightRange and self:IsInFieldOfView(playerPos) and self:HasLineOfSight(playerPos) then
			detected = true
		end

		if detected and dist < nearestDist then
			nearest = player
			nearestDist = dist
		end
	end

	return nearest
end

-- Raycast-based line of sight check
function MonsterAI:HasLineOfSight(targetPosition: Vector3): boolean
	local origin = self.RootPart.Position + Vector3.new(0, 2, 0) -- Eye height
	local direction = targetPosition - origin

	local rayParams = RaycastParams.new()
	rayParams.FilterDescendantsInstances = { self.Model }
	rayParams.FilterType = Enum.RaycastFilterType.Exclude

	local result = workspace:Raycast(origin, direction, rayParams)

	if not result then
		return true -- Nothing blocking, target is in open air
	end

	-- Check if the hit part belongs to a player character
	local hitModel = result.Instance:FindFirstAncestorOfClass("Model")
	if hitModel then
		local hitPlayer = Players:GetPlayerFromCharacter(hitModel)
		if hitPlayer then
			return true -- Hit the player, so we have line of sight
		end
	end

	return false
end

-- Check if target is within the monster's field of view cone
function MonsterAI:IsInFieldOfView(targetPosition: Vector3): boolean
	local toTarget = (targetPosition - self.RootPart.Position).Unit
	local forward = self.RootPart.CFrame.LookVector
	local dotProduct = forward:Dot(toTarget)
	local angleRad = math.acos(math.clamp(dotProduct, -1, 1))
	local angleDeg = math.deg(angleRad)

	return angleDeg <= self.Config.SightAngle
end

-- Check if a player is inside a hiding spot
function MonsterAI:IsPlayerHiding(player: Player): boolean
	local character = player.Character
	if not character then
		return false
	end

	local playerRoot = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not playerRoot then
		return false
	end

	for _, spot in CollectionService:GetTagged("HidingSpot") do
		if spot:IsA("BasePart") then
			local dist = (playerRoot.Position - spot.Position).Magnitude
			if dist < 6 then
				return true
			end
		end
	end

	return false
end

-- Search nearby hiding spots when a player disappears
function MonsterAI:SearchHidingSpots()
	task.spawn(function()
		local hidingSpots = CollectionService:GetTagged("HidingSpot")
		local nearbySpots: { BasePart } = {}

		for _, spot in hidingSpots do
			if spot:IsA("BasePart") then
				local dist = (self.RootPart.Position - spot.Position).Magnitude
				if dist < 40 then
					table.insert(nearbySpots, spot)
				end
			end
		end

		-- Visit each nearby hiding spot
		for _, spot in nearbySpots do
			if not self.Active or self.SearchTimer <= 0 then
				break
			end

			self:NavigateTo(spot.Position)
			task.wait(2) -- Pause at each spot
			self.SearchTimer -= 2

			-- Check if the player is still hiding here
			if self.Target and not self:IsPlayerHiding(self.Target) then
				-- Player left hiding — resume chase
				self:SetState("Chase")
				return
			end
		end

		-- Gave up searching — return to patrol
		self:SetState("Patrol")
	end)
end

-- Helper: get a player's HumanoidRootPart position
function MonsterAI:GetPlayerPosition(player: Player): Vector3?
	local character = player.Character
	if not character then
		return nil
	end

	local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not rootPart then
		return nil
	end

	return rootPart.Position
end

-- Helper: check if a player is sprinting
function MonsterAI:IsPlayerRunning(player: Player): boolean
	local character = player.Character
	if not character then
		return false
	end

	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if not humanoid then
		return false
	end

	return humanoid.MoveDirection.Magnitude > 0.5 and humanoid.WalkSpeed > 16
end

return MonsterAI
```

### 3.3 Event Sequencer

Triggers scripted horror events based on player proximity or game progress. Events include light flickers, door slams, shadow appearances, and environmental changes.

```luau
-- EventSequencer.luau (ServerScriptService)

local Players = game:GetService("Players")
local CollectionService = game:GetService("CollectionService")

local EventSequencer = {}
EventSequencer.__index = EventSequencer

export type EventAction = {
	Type: "Flicker" | "DoorSlam" | "ShadowAppear" | "SoundPlay" | "AtmosphereChange" | "Custom",
	Delay: number,          -- Seconds to wait before executing this action
	Target: string?,        -- Name/tag of the target object
	Params: { [string]: any }?,
}

export type EventTrigger = {
	Name: string,
	TriggerPart: BasePart,          -- Invisible part the player must enter
	TriggerOnce: boolean,           -- If true, only fires the first time
	Actions: { EventAction },
	Fired: boolean,
}

function EventSequencer.new()
	local self = setmetatable({}, EventSequencer)
	self.Triggers = {} :: { EventTrigger }
	self.Connections = {} :: { RBXScriptConnection }
	return self
end

-- Register all parts tagged "HorrorTrigger" in the workspace
function EventSequencer:Init()
	for _, part in CollectionService:GetTagged("HorrorTrigger") do
		if part:IsA("BasePart") then
			self:RegisterTrigger(part)
		end
	end
end

-- Create a trigger from a tagged part. Configuration is read from Attributes.
function EventSequencer:RegisterTrigger(part: BasePart)
	local actionsModule = part:FindFirstChild("Actions") :: ModuleScript?
	if not actionsModule then
		warn(`[EventSequencer] Trigger "{part.Name}" has no Actions ModuleScript`)
		return
	end

	local actions = require(actionsModule) :: { EventAction }

	local trigger: EventTrigger = {
		Name = part.Name,
		TriggerPart = part,
		TriggerOnce = part:GetAttribute("TriggerOnce") or true,
		Actions = actions,
		Fired = false,
	}

	table.insert(self.Triggers, trigger)

	-- Connect touch detection
	local connection = part.Touched:Connect(function(hit: BasePart)
		local character = hit:FindFirstAncestorOfClass("Model")
		if not character then
			return
		end

		local player = Players:GetPlayerFromCharacter(character)
		if not player then
			return
		end

		if trigger.Fired and trigger.TriggerOnce then
			return
		end

		trigger.Fired = true
		self:ExecuteSequence(trigger, player)
	end)

	table.insert(self.Connections, connection)
end

-- Execute a sequence of actions with delays
function EventSequencer:ExecuteSequence(trigger: EventTrigger, triggeringPlayer: Player)
	task.spawn(function()
		for _, action in trigger.Actions do
			task.wait(action.Delay)
			self:ExecuteAction(action, triggeringPlayer)
		end
	end)
end

-- Dispatch an individual action
function EventSequencer:ExecuteAction(action: EventAction, player: Player)
	if action.Type == "Flicker" then
		self:DoFlicker(action, player)
	elseif action.Type == "DoorSlam" then
		self:DoDoorSlam(action)
	elseif action.Type == "ShadowAppear" then
		self:DoShadowAppear(action, player)
	elseif action.Type == "SoundPlay" then
		self:DoSoundPlay(action, player)
	elseif action.Type == "AtmosphereChange" then
		self:DoAtmosphereChange(action)
	elseif action.Type == "Custom" then
		self:DoCustom(action, player)
	end
end

function EventSequencer:DoFlicker(action: EventAction, player: Player)
	local remotes = game.ReplicatedStorage.HorrorShared.Remotes
	local atmosphereRemote = remotes:FindFirstChild("AtmosphereRemote") :: RemoteEvent?
	if not atmosphereRemote then
		return
	end

	local count = if action.Params then (action.Params.Count or 5) else 5
	local interval = if action.Params then (action.Params.Interval or 0.15) else 0.15

	-- Flicker is client-side; fire to the triggering player or all players
	for i = 1, count do
		atmosphereRemote:FireClient(player, "Panic", 0.05)
		task.wait(interval * 0.3)
		atmosphereRemote:FireClient(player, "Uneasy", 0.05)
		task.wait(interval * 0.7)
	end
end

function EventSequencer:DoDoorSlam(action: EventAction)
	local targetName = action.Target
	if not targetName then
		return
	end

	local doors = CollectionService:GetTagged(targetName)
	for _, door in doors do
		if door:IsA("Model") and door:FindFirstChild("DoorPart") then
			local hinge = door:FindFirstChild("HingeConstraint")
			if hinge and hinge:IsA("HingeConstraint") then
				hinge.AngularVelocity = 15
				task.delay(0.5, function()
					hinge.AngularVelocity = 0
				end)
			end
		end
	end
end

function EventSequencer:DoShadowAppear(action: EventAction, player: Player)
	local shadowTemplate = game.ReplicatedStorage:FindFirstChild("ShadowFigure")
	if not shadowTemplate then
		return
	end

	local character = player.Character
	if not character or not character:FindFirstChild("HumanoidRootPart") then
		return
	end

	local playerPos = character.HumanoidRootPart.Position
	local lookDir = character.HumanoidRootPart.CFrame.LookVector
	local spawnPos = playerPos + lookDir * (action.Params and action.Params.Distance or 30)

	local shadow = shadowTemplate:Clone()
	shadow:PivotTo(CFrame.new(spawnPos, playerPos))
	shadow.Parent = workspace

	local duration = action.Params and action.Params.Duration or 3
	task.delay(duration, function()
		shadow:Destroy()
	end)
end

function EventSequencer:DoSoundPlay(action: EventAction, player: Player)
	if not action.Params or not action.Params.SoundId then
		return
	end

	local sound = Instance.new("Sound")
	sound.SoundId = action.Params.SoundId
	sound.Volume = action.Params.Volume or 1
	sound.PlayOnRemove = false

	local character = player.Character
	if character and character:FindFirstChild("HumanoidRootPart") then
		sound.Parent = character.HumanoidRootPart
	else
		sound.Parent = workspace
	end

	sound:Play()
	sound.Ended:Once(function()
		sound:Destroy()
	end)
end

function EventSequencer:DoAtmosphereChange(action: EventAction)
	local remotes = game.ReplicatedStorage.HorrorShared.Remotes
	local atmosphereRemote = remotes:FindFirstChild("AtmosphereRemote") :: RemoteEvent?
	if not atmosphereRemote then
		return
	end

	local preset = action.Params and action.Params.Preset or "Danger"
	local duration = action.Params and action.Params.Duration or 3
	atmosphereRemote:FireAllClients(preset, duration)
end

function EventSequencer:DoCustom(action: EventAction, player: Player)
	if action.Params and action.Params.Callback then
		local callbackModule = game.ServerScriptService:FindFirstChild(action.Params.Callback)
		if callbackModule and callbackModule:IsA("ModuleScript") then
			local callback = require(callbackModule)
			if typeof(callback) == "function" then
				callback(player, action.Params)
			end
		end
	end
end

-- Cleanup
function EventSequencer:Destroy()
	for _, conn in self.Connections do
		conn:Disconnect()
	end
	table.clear(self.Connections)
	table.clear(self.Triggers)
end

return EventSequencer
```

### 3.4 Jumpscare System

Client-side system that seizes camera control, displays a scare visual, plays a sound stinger, and flashes the screen.

```luau
-- JumpscareController.luau (StarterPlayerScripts)

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local SoundService = game:GetService("SoundService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LocalPlayer = Players.LocalPlayer
local Camera = workspace.CurrentCamera

local JumpscareController = {}

local COOLDOWN_SECONDS = 5
local lastJumpscareTime = 0
local isPlaying = false

-- Configuration per monster type
local JUMPSCARE_DATA: { [string]: { ImageId: string?, ModelName: string?, SoundId: string, Duration: number } } = {
	DefaultMonster = {
		ImageId = nil,
		ModelName = "JumpscareModel_Default",
		SoundId = "rbxassetid://REPLACE_WITH_STINGER_ID",
		Duration = 1.2,
	},
}

function JumpscareController.Init()
	local remotes = ReplicatedStorage:WaitForChild("HorrorShared"):WaitForChild("Remotes")
	local jumpscareRemote = remotes:WaitForChild("JumpscareRemote") :: RemoteEvent

	jumpscareRemote.OnClientEvent:Connect(function(monsterName: string)
		JumpscareController.Play(monsterName)
	end)
end

function JumpscareController.Play(monsterName: string)
	-- Enforce cooldown
	local now = tick()
	if isPlaying or (now - lastJumpscareTime) < COOLDOWN_SECONDS then
		return
	end

	isPlaying = true
	lastJumpscareTime = now

	local data = JUMPSCARE_DATA[monsterName] or JUMPSCARE_DATA.DefaultMonster
	local playerGui = LocalPlayer:WaitForChild("PlayerGui")

	-- 1. Create full-screen overlay
	local screenGui = Instance.new("ScreenGui")
	screenGui.Name = "JumpscareOverlay"
	screenGui.IgnoreGuiInset = true
	screenGui.DisplayOrder = 100

	-- Flash frame (white flash on impact)
	local flashFrame = Instance.new("Frame")
	flashFrame.Name = "Flash"
	flashFrame.Size = UDim2.fromScale(1, 1)
	flashFrame.BackgroundColor3 = Color3.new(1, 1, 1)
	flashFrame.BackgroundTransparency = 1
	flashFrame.ZIndex = 10
	flashFrame.Parent = screenGui

	-- Scare image (if using an image-based jumpscare)
	if data.ImageId then
		local scareImage = Instance.new("ImageLabel")
		scareImage.Name = "ScareImage"
		scareImage.Size = UDim2.fromScale(1, 1)
		scareImage.Image = data.ImageId
		scareImage.ScaleType = Enum.ScaleType.Stretch
		scareImage.BackgroundTransparency = 1
		scareImage.ImageTransparency = 1
		scareImage.ZIndex = 5
		scareImage.Parent = screenGui
	end

	screenGui.Parent = playerGui

	-- 2. Take camera control
	local originalCameraType = Camera.CameraType
	Camera.CameraType = Enum.CameraType.Scriptable

	-- Position camera facing the scare model (if using 3D model)
	local scareModel: Model? = nil
	if data.ModelName then
		local template = ReplicatedStorage:FindFirstChild(data.ModelName)
		if template then
			scareModel = template:Clone()
			local character = LocalPlayer.Character
			if character and character:FindFirstChild("HumanoidRootPart") then
				local rootCF = character.HumanoidRootPart.CFrame
				local spawnCF = rootCF * CFrame.new(0, 0, -4) -- 4 studs in front
				scareModel:PivotTo(spawnCF)
				scareModel.Parent = workspace

				Camera.CFrame = rootCF * CFrame.new(0, 1.5, 0) -- Eye level, looking forward
			end
		end
	end

	-- 3. Play stinger sound at high volume
	local stinger = Instance.new("Sound")
	stinger.SoundId = data.SoundId
	stinger.Volume = 2.5
	stinger.PlaybackSpeed = 1
	stinger.Parent = SoundService
	stinger:Play()

	-- 4. Screen flash
	task.spawn(function()
		local flashIn = TweenService:Create(flashFrame, TweenInfo.new(0.05), { BackgroundTransparency = 0 })
		flashIn:Play()
		flashIn.Completed:Wait()

		local flashOut = TweenService:Create(flashFrame, TweenInfo.new(0.3), { BackgroundTransparency = 1 })
		flashOut:Play()
	end)

	-- 5. Fade in scare image
	if data.ImageId then
		local scareImage = screenGui:FindFirstChild("ScareImage") :: ImageLabel?
		if scareImage then
			local fadeIn = TweenService:Create(scareImage, TweenInfo.new(0.05), { ImageTransparency = 0 })
			fadeIn:Play()
		end
	end

	-- 6. Camera shake during scare
	task.spawn(function()
		local elapsed = 0
		while elapsed < data.Duration do
			local shakeOffset = Vector3.new(
				math.random() * 0.4 - 0.2,
				math.random() * 0.4 - 0.2,
				0
			)
			Camera.CFrame = Camera.CFrame * CFrame.new(shakeOffset)
			local dt = task.wait()
			elapsed += dt
		end
	end)

	-- 7. Wait for duration, then release
	task.wait(data.Duration)

	-- Cleanup
	if scareModel then
		scareModel:Destroy()
	end

	Camera.CameraType = originalCameraType
	stinger:Destroy()
	screenGui:Destroy()

	isPlaying = false
end

return JumpscareController
```

### 3.5 Flashlight System

Toggleable flashlight with battery drain, recharge pickups, and visual feedback.

```luau
-- FlashlightController.luau (StarterPlayerScripts)

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local CollectionService = game:GetService("CollectionService")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LocalPlayer = Players.LocalPlayer

local FlashlightController = {}

local MAX_BATTERY = 100
local DRAIN_RATE = 2         -- Battery units per second while on
local PICKUP_RECHARGE = 40   -- Battery units restored per pickup
local TOGGLE_KEY = Enum.KeyCode.F

local battery = MAX_BATTERY
local isOn = false
local spotLight: SpotLight? = nil
local pointLight: PointLight? = nil
local lightPart: BasePart? = nil
local heartbeatConnection: RBXScriptConnection? = nil

function FlashlightController.Init()
	-- Wait for character
	local character = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
	FlashlightController.SetupLights(character)

	-- Reconnect on respawn
	LocalPlayer.CharacterAdded:Connect(function(newCharacter)
		FlashlightController.SetupLights(newCharacter)
		battery = MAX_BATTERY
		isOn = false
	end)

	-- Toggle input
	UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if gameProcessed then
			return
		end
		if input.KeyCode == TOGGLE_KEY then
			FlashlightController.Toggle()
		end
	end)

	-- Battery drain loop
	heartbeatConnection = RunService.Heartbeat:Connect(function(dt)
		if isOn then
			battery = math.max(0, battery - DRAIN_RATE * dt)
			if battery <= 0 then
				FlashlightController.TurnOff()
			end
			FlashlightController.UpdateUI()
		end
	end)

	-- Battery pickup detection
	for _, pickup in CollectionService:GetTagged("BatteryPickup") do
		FlashlightController.ConnectPickup(pickup)
	end

	CollectionService:GetInstanceAddedSignal("BatteryPickup"):Connect(function(pickup)
		FlashlightController.ConnectPickup(pickup)
	end)
end

function FlashlightController.SetupLights(character: Model)
	local rootPart = character:WaitForChild("HumanoidRootPart") :: BasePart
	local head = character:WaitForChild("Head") :: BasePart

	-- Clean up existing lights
	if lightPart then
		lightPart:Destroy()
	end

	-- Attach an invisible part to the character for the light source
	lightPart = Instance.new("Part")
	lightPart.Name = "FlashlightMount"
	lightPart.Size = Vector3.new(0.1, 0.1, 0.1)
	lightPart.Transparency = 1
	lightPart.CanCollide = false
	lightPart.Massless = true
	lightPart.Parent = character

	local weld = Instance.new("WeldConstraint")
	weld.Part0 = head
	weld.Part1 = lightPart
	weld.Parent = lightPart
	lightPart.CFrame = head.CFrame * CFrame.new(0, 0, -0.5)

	-- SpotLight: main directional beam
	spotLight = Instance.new("SpotLight")
	spotLight.Brightness = 3
	spotLight.Range = 45
	spotLight.Angle = 40
	spotLight.Face = Enum.NormalId.Front
	spotLight.Color = Color3.fromRGB(255, 245, 220)
	spotLight.Enabled = false
	spotLight.Parent = lightPart

	-- PointLight: subtle ambient glow around the player
	pointLight = Instance.new("PointLight")
	pointLight.Brightness = 0.5
	pointLight.Range = 12
	pointLight.Color = Color3.fromRGB(255, 245, 220)
	pointLight.Enabled = false
	pointLight.Parent = lightPart
end

function FlashlightController.Toggle()
	if isOn then
		FlashlightController.TurnOff()
	else
		FlashlightController.TurnOn()
	end
end

function FlashlightController.TurnOn()
	if battery <= 0 then
		return
	end

	isOn = true
	if spotLight then
		spotLight.Enabled = true
	end
	if pointLight then
		pointLight.Enabled = true
	end
end

function FlashlightController.TurnOff()
	isOn = false
	if spotLight then
		spotLight.Enabled = false
	end
	if pointLight then
		pointLight.Enabled = false
	end
end

function FlashlightController.GetBattery(): number
	return battery
end

function FlashlightController.GetMaxBattery(): number
	return MAX_BATTERY
end

function FlashlightController.IsOn(): boolean
	return isOn
end

function FlashlightController.ConnectPickup(pickup: Instance)
	if not pickup:IsA("BasePart") then
		return
	end

	pickup.Touched:Connect(function(hit)
		local character = hit:FindFirstAncestorOfClass("Model")
		if not character then
			return
		end

		local player = Players:GetPlayerFromCharacter(character)
		if player ~= LocalPlayer then
			return
		end

		battery = math.min(MAX_BATTERY, battery + PICKUP_RECHARGE)
		FlashlightController.UpdateUI()
		pickup:Destroy()
	end)
end

function FlashlightController.UpdateUI()
	local playerGui = LocalPlayer:FindFirstChild("PlayerGui")
	if not playerGui then
		return
	end

	local batteryGui = playerGui:FindFirstChild("BatteryUI")
	if not batteryGui then
		batteryGui = FlashlightController.CreateBatteryUI()
	end

	local fill = batteryGui:FindFirstChild("BatteryFill", true) :: Frame?
	if fill then
		local pct = battery / MAX_BATTERY
		fill.Size = UDim2.new(pct, 0, 1, 0)

		-- Color: green → yellow → red
		if pct > 0.5 then
			fill.BackgroundColor3 = Color3.fromRGB(80, 200, 80)
		elseif pct > 0.2 then
			fill.BackgroundColor3 = Color3.fromRGB(220, 200, 50)
		else
			fill.BackgroundColor3 = Color3.fromRGB(220, 50, 50)
		end
	end
end

function FlashlightController.CreateBatteryUI(): ScreenGui
	local playerGui = LocalPlayer:WaitForChild("PlayerGui")

	local gui = Instance.new("ScreenGui")
	gui.Name = "BatteryUI"
	gui.ResetOnSpawn = false

	local frame = Instance.new("Frame")
	frame.Name = "BatteryFrame"
	frame.Size = UDim2.new(0, 120, 0, 20)
	frame.Position = UDim2.new(0, 20, 1, -40)
	frame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
	frame.BorderSizePixel = 1
	frame.BorderColor3 = Color3.fromRGB(150, 150, 150)
	frame.Parent = gui

	local fill = Instance.new("Frame")
	fill.Name = "BatteryFill"
	fill.Size = UDim2.new(1, 0, 1, 0)
	fill.BackgroundColor3 = Color3.fromRGB(80, 200, 80)
	fill.BorderSizePixel = 0
	fill.Parent = frame

	gui.Parent = playerGui
	return gui
end

return FlashlightController
```

### 3.6 Door/Key System

Server-authoritative system for locked doors that require key items to open. Tracks per-player key inventory.

```luau
-- DoorKeySystem.luau (ServerScriptService)

local Players = game:GetService("Players")
local CollectionService = game:GetService("CollectionService")

local DoorKeySystem = {}

-- Per-player inventory: { [Player]: { [keyId]: true } }
local playerKeys: { [Player]: { [string]: boolean } } = {}

function DoorKeySystem.Init()
	-- Setup player tracking
	Players.PlayerAdded:Connect(function(player)
		playerKeys[player] = {}
	end)

	Players.PlayerRemoving:Connect(function(player)
		playerKeys[player] = nil
	end)

	-- Initialize existing players
	for _, player in Players:GetPlayers() do
		playerKeys[player] = {}
	end

	-- Connect key pickups
	for _, pickup in CollectionService:GetTagged("KeyPickup") do
		DoorKeySystem.ConnectKeyPickup(pickup)
	end

	CollectionService:GetInstanceAddedSignal("KeyPickup"):Connect(function(pickup)
		DoorKeySystem.ConnectKeyPickup(pickup)
	end)

	-- Connect locked doors
	for _, door in CollectionService:GetTagged("LockedDoor") do
		DoorKeySystem.ConnectLockedDoor(door)
	end
end

function DoorKeySystem.ConnectKeyPickup(pickup: Instance)
	if not pickup:IsA("BasePart") then
		return
	end

	local keyId = pickup:GetAttribute("KeyId") :: string?
	if not keyId then
		warn(`[DoorKeySystem] KeyPickup "{pickup.Name}" missing KeyId attribute`)
		return
	end

	pickup.Touched:Connect(function(hit)
		local character = hit:FindFirstAncestorOfClass("Model")
		if not character then
			return
		end

		local player = Players:GetPlayerFromCharacter(character)
		if not player or not playerKeys[player] then
			return
		end

		if playerKeys[player][keyId] then
			return -- Already has this key
		end

		playerKeys[player][keyId] = true
		pickup:Destroy()

		-- Notify client (for UI/sound feedback)
		local remotes = game.ReplicatedStorage:FindFirstChild("HorrorShared")
		if remotes then
			local keyRemote = remotes.Remotes:FindFirstChild("KeyPickupRemote") :: RemoteEvent?
			if keyRemote then
				keyRemote:FireClient(player, keyId)
			end
		end
	end)
end

function DoorKeySystem.ConnectLockedDoor(door: Instance)
	local promptPart = if door:IsA("Model") then door:FindFirstChild("PromptPart") else door
	if not promptPart or not promptPart:IsA("BasePart") then
		return
	end

	local requiredKeyId = door:GetAttribute("RequiredKeyId") :: string?
	if not requiredKeyId then
		warn(`[DoorKeySystem] LockedDoor "{door.Name}" missing RequiredKeyId attribute`)
		return
	end

	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Unlock"
	prompt.ObjectText = "Locked Door"
	prompt.HoldDuration = 0.5
	prompt.MaxActivationDistance = 8
	prompt.Parent = promptPart

	local unlocked = false

	prompt.Triggered:Connect(function(player: Player)
		if unlocked then
			return
		end

		if not playerKeys[player] or not playerKeys[player][requiredKeyId] then
			-- Player does not have the key — notify client
			local remotes = game.ReplicatedStorage:FindFirstChild("HorrorShared")
			if remotes then
				local lockRemote = remotes.Remotes:FindFirstChild("DoorLockedRemote") :: RemoteEvent?
				if lockRemote then
					lockRemote:FireClient(player, door.Name, requiredKeyId)
				end
			end
			return
		end

		-- Unlock the door
		unlocked = true
		prompt:Destroy()

		-- Open animation: tween or hinge
		if door:IsA("Model") then
			local doorPart = door:FindFirstChild("DoorPart") :: BasePart?
			if doorPart then
				local TweenService = game:GetService("TweenService")
				local openCF = doorPart.CFrame * CFrame.Angles(0, math.rad(90), 0)
				local tween = TweenService:Create(doorPart, TweenInfo.new(0.8, Enum.EasingStyle.Quad), {
					CFrame = openCF,
				})
				tween:Play()
			end
		end
	end)
end

-- Query: does a player have a specific key?
function DoorKeySystem.PlayerHasKey(player: Player, keyId: string): boolean
	return playerKeys[player] ~= nil and playerKeys[player][keyId] == true
end

-- Grant a key programmatically (e.g., from a puzzle completion)
function DoorKeySystem.GiveKey(player: Player, keyId: string)
	if not playerKeys[player] then
		playerKeys[player] = {}
	end
	playerKeys[player][keyId] = true
end

return DoorKeySystem
```

---

## 4. Progression Design

### Room/Level Structure

```
Level 1: "The Arrival"
  - Tutorial area, teach flashlight, crouch, interact
  - Single monster encounter (scripted, not AI-driven)
  - 1 key, 1 locked door
  - Bright-ish ambient, long fog distance

Level 2: "The Basement"
  - Tighter corridors, reduced visibility
  - AI monster begins patrol (slow speed, small patrol area)
  - 2 keys, puzzle to reveal one key
  - Battery pickups become necessary

Level 3: "The Ward"
  - Multiple rooms, multiple patrol routes
  - Faster monster, wider detection radius
  - Hiding spots introduced
  - Narrative journals reveal backstory

Level 4: "The Core"
  - Near-total darkness, very short fog distance
  - Multiple monsters with different behaviors
  - Minimal battery pickups
  - Chase sequences with scripted route collapses

Level 5: "Escape"
  - Boss encounter or extended chase
  - Timed escape sequence
  - Ending branches based on collected items/choices
```

### Difficulty Scaling

| Factor | Early Levels | Mid Levels | Late Levels |
|---|---|---|---|
| Ambient Light | 0.8 - 1.2 | 0.3 - 0.6 | 0.02 - 0.1 |
| Fog Distance | 300 - 500 | 120 - 250 | 40 - 80 |
| Monster Speed | 8 - 10 | 14 - 18 | 20 - 24 |
| Sight Range | 30 - 40 | 50 - 60 | 70 - 90 |
| Battery Drain | 1/sec | 2/sec | 3/sec |
| Battery Pickups | Abundant | Moderate | Scarce |
| Hiding Spots | Many | Some | Few |

### Narrative Delivery

- **Journals/Notes:** Collectible TextLabels on SurfaceGuis attached to paper models. Each reveals a fragment of the story.
- **Environmental storytelling:** Bloodstains, overturned furniture, barricaded doors, scratches on walls.
- **Audio logs:** Short voice clips triggered by proximity to key objects.
- **Multiple endings:** Track player choices (who they save, what items they collect, whether they read all journals). Fire different ending cutscenes based on accumulated flags.

---

## 5. Monetization Strategy

### DevProducts (Repeatable Purchases)

| Product | Price (Robux) | Description |
|---|---|---|
| Extra Life | 25 | Revive on the spot instead of restarting the level |
| Battery Pack | 10 | Instantly refill flashlight battery to 100% |
| Monster Repellent | 50 | Monsters ignore you for 30 seconds |

### GamePasses (One-Time Purchases)

| GamePass | Price (Robux) | Description |
|---|---|---|
| Bonus Chapter | 149 | Unlock an additional story chapter after the main game |
| Upgraded Flashlight | 99 | Brighter beam, slower battery drain (1.5x range, 0.6x drain) |
| Night Vision Mode | 199 | Toggle-able green-tinted vision boost (slight ambient increase) |
| All Skins Pack | 129 | Exclusive character skins (glowing eyes, tattered outfit, etc.) |
| Skip Level | 49 | Skip to the next level if stuck |

### Ethical Guidelines

- Never lock core progression behind purchases. All levels must be completable without spending.
- Extra lives are a convenience, not a requirement. Tune difficulty so free players can succeed with skill.
- Clearly label all purchases. No deceptive pricing or hidden costs.

---

## 6. Performance Considerations

### Lighting Performance

- **Limit active lights.** Dynamic PointLights and SpotLights are expensive. Keep total active light count under 8 per player's visible area.
- **Pre-bake static lighting.** Use SurfaceLight for environmental set dressing that does not need to change at runtime.
- **Disable lights by distance.** Lights beyond 100 studs from the camera should be disabled via a client-side distance check.
- **Flashlight optimization.** Only one SpotLight per player. Disable the SpotLight entirely when the flashlight is off rather than setting Brightness to 0.

### Fog and Draw Distance

- **Use fog to hide draw distance.** Set FogEnd to a value that hides unloaded geometry. Players accept short visibility as a horror mechanic.
- **StreamingEnabled.** Enable workspace streaming with a modest StreamingMinRadius (64-128) and StreamingTargetRadius (256). Horror corridors load fast due to small visible areas.

### Particles and Effects

- **Minimize particle emitters.** Dust particles and fog effects look great but cost frames. Limit to 2-3 active ParticleEmitters visible at once.
- **Use Decals over MeshParts for blood/grime.** Decals are cheaper to render than additional geometry.

### Monster AI

- **Tick rate.** Run AI updates at 10 Hz (task.wait(0.1)), not every frame. Pathfinding is expensive.
- **Limit pathfinding calls.** Cache the computed path and only recompute when the target moves more than 10 studs from the last computed destination.
- **Despawn distant monsters.** If no player is within 200 studs of a monster, pause its AI loop entirely.

### General

- **Anchor static parts.** Every unanchored part costs physics simulation. Anchor all environmental geometry.
- **Merge small parts.** Use Union operations or MeshParts for complex static decorations instead of dozens of individual Parts.
- **Profile regularly.** Use the MicroProfiler (Ctrl+F6) to identify frame time spikes from lighting, physics, or script execution.

---

## 7. Launch Checklist

### Scare Design

- [ ] Jumpscare timing is earned, not random. Each scare follows a buildup of tension.
- [ ] No two jumpscares fire within 30 seconds of each other (cooldown enforced).
- [ ] At least 3 "fake scares" (tension with no payoff) per level to keep players on edge.
- [ ] Monster encounters feel dangerous but escapable. Players who pay attention survive.

### Sound Design

- [ ] Ambient drone loops seamlessly with no audible seam.
- [ ] Quiet-to-loud dynamic range is extreme. Ambient at 0.2-0.4 volume, stingers at 2.0-3.0.
- [ ] Positional audio for monster footsteps (use Sound parented to monster's HumanoidRootPart).
- [ ] Environmental sounds (dripping water, creaking wood, distant screams) placed throughout levels.
- [ ] Heartbeat sound triggers when monster is within hearing range.

### Playtesting

- [ ] Watch at least 10 first-time players. Note where they get confused, bored, or desensitized.
- [ ] Verify every hiding spot works — monster searches then gives up reliably.
- [ ] Confirm flashlight battery drain feels fair. Players should run out occasionally, not constantly.
- [ ] Test on low-end devices (mobile, older PCs). Ensure fog hides pop-in and frame rate stays above 30.
- [ ] Verify all key/door combinations work. No softlocks where a key is unreachable.

### Atmosphere

- [ ] Each level has a distinct color palette and fog density.
- [ ] Atmosphere transitions are smooth (no jarring snaps between presets).
- [ ] "Safe rooms" exist where the player can catch their breath — critical for pacing.
- [ ] Darkness is the primary fear tool, not gore or graphic content (Roblox-appropriate).

### Technical

- [ ] All remote events are validated server-side. Clients cannot grant themselves keys or skip levels.
- [ ] Monster kill detection is server-authoritative. Clients cannot avoid death by exploiting.
- [ ] StreamingEnabled is on with appropriate radius values.
- [ ] No memory leaks: all cloned instances (shadows, sounds, UI) are destroyed after use.
- [ ] Battery pickups and key items replicate correctly in multiplayer.

### Polish

- [ ] Main menu with atmospheric background and eerie music.
- [ ] Loading screen with lore text or tips.
- [ ] Death screen with "Try Again" and optional revive purchase.
- [ ] End-of-game stats: time survived, keys found, deaths, jumpscares triggered.
- [ ] Badges for completing each level, speed runs, and no-death runs.
