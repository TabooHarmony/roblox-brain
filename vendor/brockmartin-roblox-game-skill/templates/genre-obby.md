# Obby Genre Template

---

## 1. Genre Overview

**Core Loop:** Attempt > Fail > Learn > Succeed > Next Stage

The obby (obstacle course) genre is one of Roblox's most proven formats. Players navigate a sequence of increasingly difficult platforming challenges. Death resets the player to their last checkpoint, creating a tight feedback loop that drives engagement through mastery.

**Why Obbys Work:**
- Extremely low development cost — geometry-driven, minimal scripting
- High replay value via speedrun mechanics and stage counts
- Monetization is natural (skip stage, save progress, cosmetics)
- Easy to expand — adding stages is additive, not disruptive
- Broad audience appeal across all age groups

**Reference Games:**
- **Tower of Hell** — Procedurally generated tower obby, no checkpoints, competitive timer
- **Mega Easy Obby** — 2000+ stages, casual difficulty, heavy monetization through skips
- **Escape Room Obby** — Themed worlds with puzzle-obby hybrid stages

**Typical Metrics:**
- Session length: 15-45 minutes
- D1 retention target: 30-40%
- Monetization: skip stages, checkpoint saves, cosmetics, VIP areas

---

## 2. Architecture Blueprint

```
StarterPlayer/
  StarterPlayerScripts/
    TimerClient.client.luau        -- HUD timer display and sync
    CheckpointUI.client.luau       -- Checkpoint notification popups

ServerScriptService/
  StageManager.server.luau         -- Stage progression, unlocking, completion
  CheckpointSystem.server.luau     -- Checkpoint saving, respawn logic
  ObstacleManager.server.luau      -- Obstacle behavior (kill bricks, moving platforms, etc.)
  TimerSystem.server.luau          -- Speedrun timing per stage and overall
  LeaderboardManager.server.luau   -- OrderedDataStore for fastest times

ReplicatedStorage/
  SharedTypes.luau                 -- Type definitions for stage/checkpoint data
  StageConfig.luau                 -- Stage metadata (name, theme, difficulty, order)

Workspace/
  Stages/
    Stage_1/
      Obstacles/                   -- Kill bricks, moving platforms, etc.
      Checkpoints/                 -- Checkpoint parts (named Checkpoint_1, Checkpoint_2, ...)
      StageClear/                  -- Part that triggers stage completion
    Stage_2/
    ...
```

### Key Modules

| Module | Responsibility |
|---|---|
| **StageManager** | Tracks which stage each player is on, handles unlocking the next stage upon completion, persists progress via DataStore |
| **CheckpointSystem** | Detects checkpoint touches, saves last checkpoint per player, handles respawn positioning on death |
| **ObstacleManager** | Drives all obstacle behaviors — kill bricks, moving platforms, disappearing blocks, spinners, conveyors |
| **TimerSystem** | Tracks elapsed time per stage and overall run, syncs to client for GUI display |
| **LeaderboardManager** | Reads/writes fastest completion times to OrderedDataStore, surfaces top times on in-game leaderboards |

---

## 3. Core Systems

### 3.1 Stage and Checkpoint System

This is the backbone of every obby. It handles saving progress, respawning on death, and detecting checkpoint touches.

```luau
-- ServerScriptService/CheckpointSystem.server.luau

local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local progressStore = DataStoreService:GetDataStore("ObbyProgress_v1")
local stagesFolder = workspace:WaitForChild("Stages")

-- In-memory state per player
local playerCheckpoints: { [Player]: { stage: number, checkpoint: number, spawnCFrame: CFrame } } = {}

-- Utility: get the spawn CFrame from a checkpoint part
local function getSpawnCFrame(checkpointPart: BasePart): CFrame
	return checkpointPart.CFrame + Vector3.new(0, 4, 0)
end

-- Load saved progress when a player joins
local function onPlayerAdded(player: Player)
	local savedStage = 1
	local savedCheckpoint = 0

	local success, data = pcall(function()
		return progressStore:GetAsync("player_" .. player.UserId)
	end)

	if success and data then
		savedStage = data.stage or 1
		savedCheckpoint = data.checkpoint or 0
	end

	-- Find the spawn position for the saved checkpoint
	local stageFolder = stagesFolder:FindFirstChild("Stage_" .. savedStage)
	local spawnCFrame = CFrame.new(0, 10, 0) -- fallback

	if stageFolder then
		local checkpointsFolder = stageFolder:FindFirstChild("Checkpoints")
		if checkpointsFolder and savedCheckpoint > 0 then
			local cp = checkpointsFolder:FindFirstChild("Checkpoint_" .. savedCheckpoint)
			if cp then
				spawnCFrame = getSpawnCFrame(cp)
			end
		else
			-- Spawn at stage start (first checkpoint or stage origin)
			local firstCp = checkpointsFolder and checkpointsFolder:FindFirstChild("Checkpoint_1")
			if firstCp then
				spawnCFrame = getSpawnCFrame(firstCp)
			end
		end
	end

	playerCheckpoints[player] = {
		stage = savedStage,
		checkpoint = savedCheckpoint,
		spawnCFrame = spawnCFrame,
	}

	-- Teleport player to their saved checkpoint on first spawn
	player.CharacterAdded:Connect(function(character)
		local hrp = character:WaitForChild("HumanoidRootPart")
		task.wait(0.1) -- let physics settle
		local state = playerCheckpoints[player]
		if state then
			hrp.CFrame = state.spawnCFrame
		end
	end)
end

-- Save progress when a player leaves
local function onPlayerRemoving(player: Player)
	local state = playerCheckpoints[player]
	if state then
		pcall(function()
			progressStore:SetAsync("player_" .. player.UserId, {
				stage = state.stage,
				checkpoint = state.checkpoint,
			})
		end)
	end
	playerCheckpoints[player] = nil
end

-- Connect checkpoint touch detection for all stages
local function setupCheckpoints()
	for _, stageFolder in stagesFolder:GetChildren() do
		local checkpointsFolder = stageFolder:FindFirstChild("Checkpoints")
		if not checkpointsFolder then
			continue
		end

		local stageNumber = tonumber(stageFolder.Name:match("Stage_(%d+)"))
		if not stageNumber then
			continue
		end

		for _, checkpoint: BasePart in checkpointsFolder:GetChildren() do
			local cpNumber = tonumber(checkpoint.Name:match("Checkpoint_(%d+)"))
			if not cpNumber then
				continue
			end

			checkpoint.Touched:Connect(function(hit)
				local player = Players:GetPlayerFromCharacter(hit.Parent)
				if not player then
					return
				end

				local state = playerCheckpoints[player]
				if not state then
					return
				end

				-- Only update if this checkpoint is ahead of the current one
				local isNewProgress = (stageNumber > state.stage)
					or (stageNumber == state.stage and cpNumber > state.checkpoint)

				if isNewProgress then
					state.stage = stageNumber
					state.checkpoint = cpNumber
					state.spawnCFrame = getSpawnCFrame(checkpoint)

					-- Visual feedback: change checkpoint color
					checkpoint.BrickColor = BrickColor.new("Lime green")
				end
			end)
		end
	end
end

-- Stage completion detection
local function setupStageClearTriggers()
	for _, stageFolder in stagesFolder:GetChildren() do
		local clearPart = stageFolder:FindFirstChild("StageClear")
		if not clearPart then
			continue
		end

		local stageNumber = tonumber(stageFolder.Name:match("Stage_(%d+)"))
		if not stageNumber then
			continue
		end

		clearPart.Touched:Connect(function(hit)
			local player = Players:GetPlayerFromCharacter(hit.Parent)
			if not player then
				return
			end

			local state = playerCheckpoints[player]
			if not state then
				return
			end

			if state.stage == stageNumber then
				-- Advance to next stage
				local nextStage = stageNumber + 1
				local nextFolder = stagesFolder:FindFirstChild("Stage_" .. nextStage)

				if nextFolder then
					local nextCheckpoints = nextFolder:FindFirstChild("Checkpoints")
					local firstCp = nextCheckpoints and nextCheckpoints:FindFirstChild("Checkpoint_1")
					local nextSpawn = if firstCp then getSpawnCFrame(firstCp) else CFrame.new(0, 10, 0)

					state.stage = nextStage
					state.checkpoint = 1
					state.spawnCFrame = nextSpawn

					-- Teleport player to next stage
					local character = player.Character
					if character then
						local hrp = character:FindFirstChild("HumanoidRootPart")
						if hrp then
							hrp.CFrame = nextSpawn
						end
					end
				end
			end
		end)
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)
setupCheckpoints()
setupStageClearTriggers()
```

### 3.2 Obstacle Types

All obstacle logic lives in a single server script that iterates over tagged or named parts in each stage.

```luau
-- ServerScriptService/ObstacleManager.server.luau

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")

local stagesFolder = workspace:WaitForChild("Stages")

--------------------------------------------------------------------------------
-- OBSTACLE TYPE 1: Kill Bricks
-- Touch = instant death. Player respawns at last checkpoint.
-- Tag parts with a "KillBrick" BoolValue or place them in an Obstacles folder
-- with names starting with "Kill_".
--------------------------------------------------------------------------------
local function setupKillBricks()
	for _, stageFolder in stagesFolder:GetChildren() do
		local obstacles = stageFolder:FindFirstChild("Obstacles")
		if not obstacles then
			continue
		end

		for _, part: BasePart in obstacles:GetDescendants() do
			if not part:IsA("BasePart") then
				continue
			end

			local isKillBrick = part.Name:match("^Kill_") ~= nil
				or part:FindFirstChild("KillBrick") ~= nil

			if not isKillBrick then
				continue
			end

			-- Visual styling
			part.BrickColor = BrickColor.new("Really red")
			part.Material = Enum.Material.Neon

			part.Touched:Connect(function(hit)
				local character = hit.Parent
				local humanoid = character and character:FindFirstChildOfClass("Humanoid")
				if humanoid and humanoid.Health > 0 then
					humanoid.Health = 0
				end
			end)
		end
	end
end

--------------------------------------------------------------------------------
-- OBSTACLE TYPE 2: Moving Platforms
-- Platforms that tween back and forth between two positions.
-- Each moving platform needs a child part named "TargetPosition" that marks the
-- end point. The platform's original position is the start point.
--------------------------------------------------------------------------------
local function setupMovingPlatforms()
	for _, stageFolder in stagesFolder:GetChildren() do
		local obstacles = stageFolder:FindFirstChild("Obstacles")
		if not obstacles then
			continue
		end

		for _, part: BasePart in obstacles:GetDescendants() do
			if not part:IsA("BasePart") or not part.Name:match("^Moving_") then
				continue
			end

			local targetMarker = part:FindFirstChild("TargetPosition")
			if not targetMarker or not targetMarker:IsA("BasePart") then
				continue
			end

			local startCFrame = part.CFrame
			local endCFrame = targetMarker.CFrame
			targetMarker.Transparency = 1
			targetMarker.CanCollide = false

			part.Anchored = true

			-- Duration attribute, default 3 seconds
			local duration = part:GetAttribute("TweenDuration") or 3

			local tweenInfo = TweenInfo.new(
				duration,
				Enum.EasingStyle.Sine,
				Enum.EasingDirection.InOut,
				-1,          -- repeat forever
				true,        -- reverses
				0            -- delay
			)

			local tween = TweenService:Create(part, tweenInfo, { CFrame = endCFrame })
			tween:Play()
		end
	end
end

--------------------------------------------------------------------------------
-- OBSTACLE TYPE 3: Disappearing Platforms
-- Platforms that fade out and become non-collidable after being stepped on,
-- then reappear after a delay.
-- Name parts with "Disappear_" prefix.
--------------------------------------------------------------------------------
local function setupDisappearingPlatforms()
	for _, stageFolder in stagesFolder:GetChildren() do
		local obstacles = stageFolder:FindFirstChild("Obstacles")
		if not obstacles then
			continue
		end

		for _, part: BasePart in obstacles:GetDescendants() do
			if not part:IsA("BasePart") or not part.Name:match("^Disappear_") then
				continue
			end

			part.Anchored = true
			local originalTransparency = part.Transparency
			local originalColor = part.Color

			-- Configurable timing via attributes
			local fadeDelay = part:GetAttribute("FadeDelay") or 0.5
			local disappearDuration = part:GetAttribute("DisappearDuration") or 3

			local isActive = true

			part.Touched:Connect(function(hit)
				if not isActive then
					return
				end

				local player = Players:GetPlayerFromCharacter(hit.Parent)
				if not player then
					return
				end

				isActive = false

				-- Warning flash: turn red briefly
				part.Color = Color3.fromRGB(255, 80, 80)
				task.wait(fadeDelay)

				-- Fade out
				local fadeTween = TweenService:Create(part, TweenInfo.new(0.3), {
					Transparency = 1,
				})
				fadeTween:Play()
				fadeTween.Completed:Wait()

				part.CanCollide = false

				-- Wait then reappear
				task.wait(disappearDuration)

				part.CanCollide = true
				part.Color = originalColor
				local reappearTween = TweenService:Create(part, TweenInfo.new(0.3), {
					Transparency = originalTransparency,
				})
				reappearTween:Play()
				reappearTween.Completed:Wait()

				isActive = true
			end)
		end
	end
end

--------------------------------------------------------------------------------
-- OBSTACLE TYPE 4: Spinning Obstacles
-- Parts that continuously rotate around a given axis.
-- Name parts with "Spin_" prefix.
-- Typically kill bricks that spin, so combine with KillBrick tag.
--------------------------------------------------------------------------------
local function setupSpinningObstacles()
	for _, stageFolder in stagesFolder:GetChildren() do
		local obstacles = stageFolder:FindFirstChild("Obstacles")
		if not obstacles then
			continue
		end

		for _, part: BasePart in obstacles:GetDescendants() do
			if not part:IsA("BasePart") or not part.Name:match("^Spin_") then
				continue
			end

			part.Anchored = true

			-- Rotation speed in degrees per second, configurable via attribute
			local speed = part:GetAttribute("SpinSpeed") or 90
			-- Axis: "X", "Y", or "Z" — default Y
			local axisName = part:GetAttribute("SpinAxis") or "Y"

			local axisVector: Vector3
			if axisName == "X" then
				axisVector = Vector3.new(1, 0, 0)
			elseif axisName == "Z" then
				axisVector = Vector3.new(0, 0, 1)
			else
				axisVector = Vector3.new(0, 1, 0)
			end

			RunService.Heartbeat:Connect(function(dt)
				local angleDelta = math.rad(speed * dt)
				part.CFrame = part.CFrame * CFrame.fromAxisAngle(axisVector, angleDelta)
			end)
		end
	end
end

--------------------------------------------------------------------------------
-- OBSTACLE TYPE 5: Conveyor Belts
-- Applies a velocity to players standing on the part.
-- Name parts with "Conveyor_" prefix.
--------------------------------------------------------------------------------
local function setupConveyorBelts()
	for _, stageFolder in stagesFolder:GetChildren() do
		local obstacles = stageFolder:FindFirstChild("Obstacles")
		if not obstacles then
			continue
		end

		for _, part: BasePart in obstacles:GetDescendants() do
			if not part:IsA("BasePart") or not part.Name:match("^Conveyor_") then
				continue
			end

			part.Anchored = true

			-- Direction and speed via attributes
			local conveyorSpeed = part:GetAttribute("ConveyorSpeed") or 20
			-- Direction is the part's LookVector by default
			local direction = part.CFrame.LookVector

			-- Animate surface texture to show movement direction
			local texture = Instance.new("Texture")
			texture.Face = Enum.NormalId.Top
			texture.Texture = "rbxassetid://0" -- replace with arrow texture asset ID
			texture.StudsPerTileU = 4
			texture.StudsPerTileV = 4
			texture.Parent = part

			part.Touched:Connect(function(hit)
				local character = hit.Parent
				local humanoid = character and character:FindFirstChildOfClass("Humanoid")
				if not humanoid then
					return
				end

				local hrp = character:FindFirstChild("HumanoidRootPart")
				if not hrp then
					return
				end

				-- Apply velocity using AssemblyLinearVelocity adjustment
				local existingVel = hrp.AssemblyLinearVelocity
				hrp.AssemblyLinearVelocity = Vector3.new(
					direction.X * conveyorSpeed,
					existingVel.Y,
					direction.Z * conveyorSpeed
				)
			end)
		end
	end
end

-- Initialize all obstacle systems
setupKillBricks()
setupMovingPlatforms()
setupDisappearingPlatforms()
setupSpinningObstacles()
setupConveyorBelts()
```

### 3.3 Timer / Speedrun System

```luau
-- ServerScriptService/TimerSystem.server.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- RemoteEvent for syncing timer state to client
local timerRemote = Instance.new("RemoteEvent")
timerRemote.Name = "TimerSync"
timerRemote.Parent = ReplicatedStorage

local playerTimers: { [Player]: {
	overallStart: number,
	stageStart: number,
	currentStage: number,
	stageTimes: { [number]: number },
} } = {}

local function onPlayerAdded(player: Player)
	playerTimers[player] = {
		overallStart = os.clock(),
		stageStart = os.clock(),
		currentStage = 1,
		stageTimes = {},
	}
end

local function onPlayerRemoving(player: Player)
	playerTimers[player] = nil
end

-- Called when a player completes a stage (hook into StageManager)
local function onStageCompleted(player: Player, stageNumber: number)
	local timer = playerTimers[player]
	if not timer then
		return
	end

	local stageElapsed = os.clock() - timer.stageStart
	timer.stageTimes[stageNumber] = stageElapsed

	-- Notify client of stage completion time
	timerRemote:FireClient(player, "StageComplete", {
		stage = stageNumber,
		stageTime = stageElapsed,
		overallTime = os.clock() - timer.overallStart,
	})

	-- Reset stage timer for the next stage
	timer.stageStart = os.clock()
	timer.currentStage = stageNumber + 1
end

-- Periodic sync: send current elapsed time to client every second
task.spawn(function()
	while true do
		task.wait(1)
		for player, timer in playerTimers do
			if player.Parent then
				timerRemote:FireClient(player, "TimerUpdate", {
					stageTime = os.clock() - timer.stageStart,
					overallTime = os.clock() - timer.overallStart,
					currentStage = timer.currentStage,
				})
			end
		end
	end
end)

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)
```

### 3.4 Leaderboard (Fastest Times)

```luau
-- ServerScriptService/LeaderboardManager.server.luau

local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LEADERBOARD_SIZE = 10

-- One OrderedDataStore per stage for fastest times (stored in milliseconds)
local function getStageLeaderboard(stageNumber: number)
	return DataStoreService:GetOrderedDataStore("ObbyTimes_Stage_" .. stageNumber)
end

local overallLeaderboard = DataStoreService:GetOrderedDataStore("ObbyTimes_Overall")

-- Submit a time (only saves if it beats the player's previous best)
local function submitTime(player: Player, stageNumber: number, timeSeconds: number)
	local store = getStageLeaderboard(stageNumber)
	local key = "player_" .. player.UserId
	local timeMs = math.floor(timeSeconds * 1000)

	pcall(function()
		store:UpdateAsync(key, function(oldValue)
			if oldValue == nil or timeMs < oldValue then
				return timeMs
			end
			return oldValue
		end)
	end)
end

local function submitOverallTime(player: Player, timeSeconds: number)
	local key = "player_" .. player.UserId
	local timeMs = math.floor(timeSeconds * 1000)

	pcall(function()
		overallLeaderboard:UpdateAsync(key, function(oldValue)
			if oldValue == nil or timeMs < oldValue then
				return timeMs
			end
			return oldValue
		end)
	end)
end

-- Fetch top times for a stage
local function getTopTimes(stageNumber: number): { { userId: number, timeMs: number } }
	local store = getStageLeaderboard(stageNumber)
	local results = {}

	local success, pages = pcall(function()
		return store:GetSortedAsync(true, LEADERBOARD_SIZE)
	end)

	if success and pages then
		local entries = pages:GetCurrentPage()
		for _, entry in entries do
			local odString = entry.key or ""
			local odUserId = tonumber(odString:match("player_(%d+)"))
			table.insert(results, {
				userId = odUserId,
				timeMs = entry.value,
			})
		end
	end

	return results
end
```

---

## 4. Progression Design

### Difficulty Curve

Stages should follow a clear difficulty ramp. The first 10-20 stages serve as a tutorial, teaching one mechanic at a time.

| Stage Range | Difficulty | New Mechanics Introduced |
|---|---|---|
| 1-10 | Beginner | Basic jumps, simple gaps |
| 11-25 | Easy | Kill bricks (stationary), longer jumps |
| 26-50 | Medium | Moving platforms, disappearing platforms |
| 51-80 | Hard | Spinning obstacles, conveyors, combinations |
| 81-100 | Expert | Multi-mechanic gauntlets, precision timing |
| 100+ | Master / Bonus | Secret stages, extreme difficulty |

### Themed Worlds

Group stages into themed worlds to provide visual variety and a sense of progression:

- **Grasslands (1-20)** — Bright greens, simple geometry, welcoming atmosphere
- **Lava Caves (21-40)** — Red/orange palette, fire particles, kill bricks everywhere
- **Ice Kingdom (41-60)** — Slippery surfaces (reduced friction), blue/white tones
- **Sky Islands (61-80)** — Floating platforms, wind effects, high-altitude feel
- **Space Station (81-100)** — Low gravity zones, dark backdrop with stars, neon obstacles

### Bonus and Secret Stages

- Hidden paths that branch off main stages, rewarding exploration with exclusive badges
- "Challenge rooms" accessible via a lobby portal that rotate weekly
- Timed challenge stages that only appear during events

---

## 5. Monetization Strategy

### DevProducts (Repeatable Purchases)

| Product | Price (Robux) | Description |
|---|---|---|
| Skip Stage | 25-75 | Instantly complete the current stage and move to the next |
| Extra Life Token | 10 | Respawn at exact death location instead of checkpoint (one use) |
| Speed Boost (5 min) | 50 | 1.5x WalkSpeed for 5 minutes |

### GamePasses (One-Time Purchases)

| GamePass | Price (Robux) | Description |
|---|---|---|
| Auto-Save Progress | 149-299 | Checkpoints automatically save between sessions (free players lose progress on leave) |
| 2x Speed | 199 | Permanent 1.3x WalkSpeed boost |
| Trail Effects | 99 | Unlocks a selection of trail effects behind the player |
| VIP Stages | 399 | Access to exclusive VIP-only bonus stages |
| Radio / Boombox | 149 | Play custom music while playing |

### Cosmetic Shop

- Trail effects (fire, rainbow, sparkle, etc.) sold individually as DevProducts
- Win effects (particle burst on stage completion)
- Character auras

### Revenue Optimization Tips

- Place the "Skip Stage" prompt on the death screen after 5+ deaths on the same stage
- Offer a "Stage Pack" bundle (skip 10 stages at a discount)
- Show a progress-save reminder when free players attempt to leave

---

## 6. Performance Considerations

Obbys are inherently lightweight compared to combat or open-world games. The primary concerns are:

### Physics and Part Movement

- **Anchored parts only** for all obstacles. Never use unanchored parts for platforms.
- Use `TweenService` for moving platforms instead of setting CFrame every frame. Tweens are interpolated on the client and perform better.
- For spinning obstacles that must use `RunService.Heartbeat`, keep the part count low per stage. Only spin parts in stages that have active players nearby.

### Stage Streaming

- Use `Workspace.StreamingEnabled = true`. Obbys benefit greatly from streaming because players only need to load the stage they are currently on.
- Set `ModelStreamingMode` on each stage folder to `Opportunistic` for non-adjacent stages and `Persistent` for the current and next stage.

### Memory

- Avoid excessive decal/texture usage per stage — reuse materials across stages in the same world theme.
- Keep part counts under 200 per stage for optimal performance.
- Use `MeshPart` over `Union` operations where possible (unions have higher memory cost).

### Common Pitfalls

- Do not create new `Instance` objects (like BodyVelocity) on every Touched event without cleanup. Always check if one already exists or use a debounce.
- Avoid connecting `Touched` events to parts that fire extremely rapidly (like spinning kill bricks touching the baseplate). Use collision groups to prevent obstacle-to-obstacle touches.

---

## 7. Launch Checklist

### Stage Verification

- [ ] Playtest every stage start-to-finish — confirm each one is completable
- [ ] Verify every checkpoint saves correctly (touch checkpoint, die, confirm respawn location)
- [ ] Test respawn behavior: death should teleport to last checkpoint within 1 second
- [ ] Confirm stage completion triggers correctly advance the player to the next stage
- [ ] Test the first-time player experience: joining with no save data should place the player at Stage 1

### Obstacle QA

- [ ] Kill bricks reliably trigger death on touch (no gaps in collision)
- [ ] Moving platforms move smoothly with no jitter or teleporting
- [ ] Disappearing platforms reappear correctly after their timer
- [ ] Spinning obstacles rotate at a consistent speed with no stuttering
- [ ] Conveyor belts apply velocity in the correct direction

### Progression and Data

- [ ] DataStore saves and loads correctly (test with multiple accounts)
- [ ] Stage skip DevProduct works and advances the player
- [ ] Leaderboard displays correct times and updates on new records
- [ ] Timer resets properly when starting a new stage

### Performance

- [ ] StreamingEnabled is on and configured per stage
- [ ] No memory leaks from Touched event connections (check for dangling connections)
- [ ] Test with 20+ players to verify server performance under load
- [ ] Confirm no physics glitches at stage boundaries

### Monetization

- [ ] All GamePasses grant their benefits immediately on purchase
- [ ] All DevProducts process correctly and deliver their effect
- [ ] Skip stage prompt appears at the right moment (after repeated deaths)
- [ ] VIP stages are inaccessible without the GamePass

### Polish

- [ ] Every stage has a visible checkpoint indicator (color change or particle effect on touch)
- [ ] Stage transition has a brief UI notification ("Stage 5 Complete!")
- [ ] Timer GUI is visible and updating in real time
- [ ] Background music and ambient sound are present
- [ ] Thumbnail and game icon are set and visually appealing
