# Roblox Multiplayer & Networking Reference

---

## 1. Overview

**Load this reference when:**

- Designing multiplayer game loops (rounds, lobbies, arenas)
- Implementing matchmaking or queue systems
- Building cross-server features (global chat, trading, server browsing)
- Working with TeleportService for multi-place games
- Creating team-based gameplay
- Managing player lifecycles in a multiplayer context
- Setting up private/reserved servers

This document covers player management, team systems, lobby implementation, round-based game loops, TeleportService, MessagingService, matchmaking, server instance management, and production best practices for multiplayer Roblox games.

---

## 2. Player Management

### Players Service

The `Players` service is the root of all player-related functionality. Every connected player is represented by a `Player` instance that lives as a child of `Players`.

```luau
local Players = game:GetService("Players")

-- Current player count
local count = #Players:GetPlayers()

-- Server capacity
local maxPlayers = Players.MaxPlayers

-- Iterate all connected players
for _, player in Players:GetPlayers() do
    print(player.Name, player.UserId)
end
```

### PlayerAdded / PlayerRemoving

These are the two most important events for multiplayer games. They fire on the server when a player joins or leaves.

```luau
-- ServerScriptService/PlayerManager.luau

local Players = game:GetService("Players")

local function onPlayerAdded(player: Player)
    -- Load saved data
    -- Initialize player state (score, team assignment, inventory)
    -- Grant starter gear
    -- Teleport to lobby spawn
    print(`{player.Name} joined (UserId: {player.UserId})`)
end

local function onPlayerRemoving(player: Player)
    -- Save player data (CRITICAL: do this before the player object is destroyed)
    -- Clean up any per-player state tables
    -- Notify other players
    -- Update team balance
    print(`{player.Name} leaving`)
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

-- Handle players who joined before this script ran (studio edge case)
for _, player in Players:GetPlayers() do
    task.spawn(onPlayerAdded, player)
end
```

**Critical rule:** Always handle `PlayerRemoving` to save data. The player object and its descendants are destroyed shortly after this event fires. If you yield too long (e.g., a slow DataStore call), you risk losing the save. Use `game:BindToClose()` as a fallback for server shutdowns.

### CharacterAdded / CharacterRemoving

Each player's character is a `Model` in `Workspace` that contains the `Humanoid`, body parts, and accessories. Characters are created and destroyed on respawn.

```luau
local function onCharacterAdded(character: Model)
    local humanoid = character:WaitForChild("Humanoid")
    local rootPart = character:WaitForChild("HumanoidRootPart")

    -- Set custom health
    humanoid.MaxHealth = 150
    humanoid.Health = 150

    -- Listen for death
    humanoid.Died:Connect(function()
        -- Award kill to attacker, update scoreboard, etc.
    end)
end

player.CharacterAdded:Connect(onCharacterAdded)
```

### LoadCharacter (Manual Respawning)

By default, Roblox auto-spawns characters. For round-based games, disable auto-spawn and control it manually:

```luau
-- In StarterPlayer properties: set CharacterAutoLoads = false
-- Or set it in script:
Players.CharacterAutoLoads = false

-- Spawn a specific player
player:LoadCharacter()

-- Spawn all players
for _, player in Players:GetPlayers() do
    task.spawn(function()
        player:LoadCharacter()
    end)
end
```

### Player Instance Lifecycle

Understanding the lifecycle prevents common bugs:

1. `PlayerAdded` fires -- Player instance exists, no character yet.
2. `CharacterAdded` fires -- Character model is parented to Workspace.
3. `CharacterRemoving` fires -- Character is about to be destroyed (death or manual removal).
4. `CharacterAdded` fires again -- Respawn.
5. `PlayerRemoving` fires -- Player is disconnecting. Character may or may not exist.

**Gotcha:** `player.Character` can be `nil` at any point. Always nil-check before accessing it.

---

## 3. Team Systems

### Teams Service

The `Teams` service holds `Team` objects. Teams are automatically replicated to all clients and show up in the default leaderboard.

```luau
local Teams = game:GetService("Teams")

-- Create teams programmatically (or place them in Studio under Teams)
local redTeam = Instance.new("Team")
redTeam.Name = "Red"
redTeam.TeamColor = BrickColor.new("Bright red")
redTeam.AutoAssignable = false -- Don't auto-assign players
redTeam.Parent = Teams

local blueTeam = Instance.new("Team")
blueTeam.Name = "Blue"
blueTeam.TeamColor = BrickColor.new("Bright blue")
blueTeam.AutoAssignable = false
blueTeam.Parent = Teams

local lobbyTeam = Instance.new("Team")
lobbyTeam.Name = "Lobby"
lobbyTeam.TeamColor = BrickColor.new("Medium stone grey")
lobbyTeam.AutoAssignable = true -- New players go here
lobbyTeam.Parent = Teams
```

### Assigning Players to Teams

```luau
-- Direct assignment
player.Team = redTeam

-- The player's nametag, leaderboard entry, and spawn location
-- all update automatically based on TeamColor.

-- Get all players on a team
local redPlayers = redTeam:GetPlayers()
print(`Red team has {#redPlayers} players`)
```

### Team-Based Logic

Always check teams on the **server** before applying damage or other competitive interactions:

```luau
local function canDamage(attacker: Player, victim: Player): boolean
    -- No friendly fire
    if attacker.Team == victim.Team then
        return false
    end

    -- No damaging lobby players
    if victim.Team == lobbyTeam then
        return false
    end

    return true
end

-- In a weapon hit handler (server-side)
local function onWeaponHit(attacker: Player, victimCharacter: Model)
    local victim = Players:GetPlayerFromCharacter(victimCharacter)
    if not victim then return end

    if not canDamage(attacker, victim) then return end

    local humanoid = victimCharacter:FindFirstChild("Humanoid")
    if humanoid then
        humanoid:TakeDamage(25)
    end
end
```

### Auto-Balancing Teams

```luau
local function getSmallestTeam(teamList: {Team}): Team
    local smallest = teamList[1]
    local smallestCount = #smallest:GetPlayers()

    for i = 2, #teamList do
        local count = #teamList[i]:GetPlayers()
        if count < smallestCount then
            smallest = teamList[i]
            smallestCount = count
        end
    end

    return smallest
end

-- Assign player to the team with fewer members
local function assignToBalancedTeam(player: Player)
    player.Team = getSmallestTeam({ redTeam, blueTeam })
end
```

---

## 4. Lobby System

A lobby holds players in a waiting area until enough are ready to start a round. This implementation tracks ready states, shows a ready-up GUI, enforces a minimum player threshold, and auto-starts after a timeout.

### Server-Side Lobby Manager

```luau
-- ServerScriptService/LobbyManager.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LobbyRemotes = Instance.new("Folder")
LobbyRemotes.Name = "LobbyRemotes"
LobbyRemotes.Parent = ReplicatedStorage

local ReadyUpEvent = Instance.new("RemoteEvent")
ReadyUpEvent.Name = "ReadyUp"
ReadyUpEvent.Parent = LobbyRemotes

local LobbyStatusEvent = Instance.new("RemoteEvent")
LobbyStatusEvent.Name = "LobbyStatus"
LobbyStatusEvent.Parent = LobbyRemotes

-- Configuration
local MIN_PLAYERS = 2
local MAX_WAIT_TIME = 60 -- seconds to auto-start after minimum reached
local COUNTDOWN_DURATION = 10 -- final countdown before round starts

-- State
local readyPlayers: { [Player]: boolean } = {}
local lobbyActive = true
local countdownRunning = false

local function getReadyCount(): number
    local count = 0
    for player, isReady in readyPlayers do
        -- Verify the player is still connected
        if isReady and player.Parent == Players then
            count += 1
        end
    end
    return count
end

local function getTotalPlayers(): number
    return #Players:GetPlayers()
end

local function broadcastStatus(message: string, countdown: number?)
    for _, player in Players:GetPlayers() do
        LobbyStatusEvent:FireClient(player, message, countdown, getReadyCount(), getTotalPlayers())
    end
end

local function shouldStart(): boolean
    return getTotalPlayers() >= MIN_PLAYERS and getReadyCount() >= MIN_PLAYERS
end

local function startCountdown()
    if countdownRunning then return end
    countdownRunning = true

    for i = COUNTDOWN_DURATION, 1, -1 do
        if not lobbyActive then
            countdownRunning = false
            return
        end

        -- Recheck player count (someone may have left)
        if getTotalPlayers() < MIN_PLAYERS then
            broadcastStatus("Not enough players. Waiting...", nil)
            countdownRunning = false
            return
        end

        broadcastStatus(`Round starting in {i}...`, i)
        task.wait(1)
    end

    countdownRunning = false
    lobbyActive = false
    broadcastStatus("Round starting!", 0)

    -- Signal to round manager (see Section 5)
    local RoundManager = require(script.Parent:WaitForChild("RoundManager"))
    RoundManager.startRound()
end

-- Handle ready-up toggle
ReadyUpEvent.OnServerEvent:Connect(function(player: Player)
    if not lobbyActive then return end

    readyPlayers[player] = not readyPlayers[player]
    broadcastStatus(
        if readyPlayers[player] then `{player.Name} is ready!` else `{player.Name} unreadied.`,
        nil
    )

    if shouldStart() and not countdownRunning then
        task.spawn(startCountdown)
    end
end)

-- Clean up when players leave
Players.PlayerRemoving:Connect(function(player: Player)
    readyPlayers[player] = nil

    if lobbyActive then
        broadcastStatus(`{player.Name} left the lobby.`, nil)
    end
end)

-- Auto-start timer: once minimum players are present, start a background timer
task.spawn(function()
    local waitElapsed = 0
    while lobbyActive do
        task.wait(1)
        if getTotalPlayers() >= MIN_PLAYERS then
            waitElapsed += 1
            if waitElapsed >= MAX_WAIT_TIME and not countdownRunning then
                -- Force all present players to ready
                for _, player in Players:GetPlayers() do
                    readyPlayers[player] = true
                end
                task.spawn(startCountdown)
            end
        else
            waitElapsed = 0
        end
    end
end)

-- Public API for reset
local LobbyManager = {}

function LobbyManager.reset()
    readyPlayers = {}
    lobbyActive = true
    countdownRunning = false
    broadcastStatus("Lobby open. Ready up!", nil)
end

return LobbyManager
```

### Client-Side Ready-Up GUI

```luau
-- StarterPlayerScripts/LobbyGui.client.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local lobbyRemotes = ReplicatedStorage:WaitForChild("LobbyRemotes")
local readyUpEvent = lobbyRemotes:WaitForChild("ReadyUp")
local lobbyStatusEvent = lobbyRemotes:WaitForChild("LobbyStatus")

-- Build GUI
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "LobbyGui"
screenGui.ResetOnSpawn = false
screenGui.Parent = playerGui

local frame = Instance.new("Frame")
frame.Size = UDim2.fromScale(0.3, 0.15)
frame.Position = UDim2.fromScale(0.35, 0.8)
frame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
frame.BackgroundTransparency = 0.3
frame.Parent = screenGui

local uiCorner = Instance.new("UICorner")
uiCorner.CornerRadius = UDim.new(0, 12)
uiCorner.Parent = frame

local statusLabel = Instance.new("TextLabel")
statusLabel.Size = UDim2.fromScale(1, 0.5)
statusLabel.BackgroundTransparency = 1
statusLabel.TextColor3 = Color3.new(1, 1, 1)
statusLabel.TextScaled = true
statusLabel.Text = "Waiting for players..."
statusLabel.Parent = frame

local readyButton = Instance.new("TextButton")
readyButton.Size = UDim2.fromScale(0.6, 0.4)
readyButton.Position = UDim2.fromScale(0.2, 0.55)
readyButton.BackgroundColor3 = Color3.fromRGB(0, 170, 0)
readyButton.TextColor3 = Color3.new(1, 1, 1)
readyButton.TextScaled = true
readyButton.Text = "Ready Up"
readyButton.Parent = frame

local readyCorner = Instance.new("UICorner")
readyCorner.CornerRadius = UDim.new(0, 8)
readyCorner.Parent = readyButton

local isReady = false

readyButton.Activated:Connect(function()
    isReady = not isReady
    readyButton.Text = if isReady then "Unready" else "Ready Up"
    readyButton.BackgroundColor3 = if isReady
        then Color3.fromRGB(170, 0, 0)
        else Color3.fromRGB(0, 170, 0)
    readyUpEvent:FireServer()
end)

lobbyStatusEvent.OnClientEvent:Connect(function(message: string, countdown: number?, readyCount: number, totalCount: number)
    statusLabel.Text = `{message}\nReady: {readyCount}/{totalCount}`

    if countdown and countdown == 0 then
        screenGui.Enabled = false
    end
end)
```

---

## 5. Round-Based Games

### Round Lifecycle State Machine

A production round system follows a clear state machine:

```
Intermission --> Countdown --> Playing --> Results --> Intermission
```

Each state has entry/exit logic, and the system must handle players joining and leaving at any point.

### Complete Round Manager Implementation

```luau
-- ServerScriptService/RoundManager.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local Teams = game:GetService("Teams")

-- Remotes
local RoundRemotes = Instance.new("Folder")
RoundRemotes.Name = "RoundRemotes"
RoundRemotes.Parent = ReplicatedStorage

local RoundStateEvent = Instance.new("RemoteEvent")
RoundStateEvent.Name = "RoundState"
RoundStateEvent.Parent = RoundRemotes

local ScoreUpdateEvent = Instance.new("RemoteEvent")
ScoreUpdateEvent.Name = "ScoreUpdate"
ScoreUpdateEvent.Parent = RoundRemotes

-- Configuration
local INTERMISSION_TIME = 15
local COUNTDOWN_TIME = 5
local ROUND_TIME = 120 -- 2 minutes per round
local RESULTS_TIME = 10
local SCORE_TO_WIN = 10

-- Map pool (models stored in ServerStorage/Maps/)
local MAP_NAMES = { "Desert", "Forest", "City" }

-- State
export type RoundState = "Intermission" | "Countdown" | "Playing" | "Results"

local currentState: RoundState = "Intermission"
local currentMap: Model? = nil
local currentMapName: string = ""
local roundNumber = 0
local mapRotationIndex = 0
local playerScores: { [Player]: number } = {}
local roundParticipants: { Player } = {}

-- Teams (assumed created elsewhere or created here)
local redTeam = Teams:FindFirstChild("Red")
local blueTeam = Teams:FindFirstChild("Blue")
local lobbyTeam = Teams:FindFirstChild("Lobby")

local RoundManager = {}

-- Utility: broadcast state to all clients
local function broadcastState(state: RoundState, data: { [string]: any }?)
    for _, player in Players:GetPlayers() do
        RoundStateEvent:FireClient(player, state, data or {})
    end
end

-- Utility: broadcast scores
local function broadcastScores()
    local scores = {}
    for player, score in playerScores do
        if player.Parent == Players then
            scores[player.Name] = score
        end
    end
    for _, player in Players:GetPlayers() do
        ScoreUpdateEvent:FireClient(player, scores)
    end
end

-- Map Selection: sequential rotation (can be changed to random)
local function selectNextMap(): string
    mapRotationIndex = (mapRotationIndex % #MAP_NAMES) + 1
    return MAP_NAMES[mapRotationIndex]
end

-- Load map into workspace
local function loadMap(mapName: string): Model?
    local mapsFolder = ServerStorage:FindFirstChild("Maps")
    if not mapsFolder then
        warn("Maps folder not found in ServerStorage")
        return nil
    end

    local mapTemplate = mapsFolder:FindFirstChild(mapName)
    if not mapTemplate then
        warn(`Map "{mapName}" not found`)
        return nil
    end

    local mapClone = mapTemplate:Clone()
    mapClone.Name = "ActiveMap"
    mapClone.Parent = workspace
    return mapClone
end

-- Remove current map
local function unloadMap()
    if currentMap then
        currentMap:Destroy()
        currentMap = nil
    end
end

-- Get spawn points from the active map
local function getSpawnPoints(teamName: string): { BasePart }
    if not currentMap then return {} end

    local spawns = {}
    local spawnFolder = currentMap:FindFirstChild(teamName .. "Spawns")
    if spawnFolder then
        for _, spawn in spawnFolder:GetChildren() do
            if spawn:IsA("BasePart") then
                table.insert(spawns, spawn)
            end
        end
    end
    return spawns
end

-- Teleport player to a spawn point
local function teleportToSpawn(player: Player, spawnPoints: { BasePart })
    if #spawnPoints == 0 then return end
    if not player.Character then return end

    local rootPart = player.Character:FindFirstChild("HumanoidRootPart")
    if not rootPart then return end

    local spawn = spawnPoints[math.random(1, #spawnPoints)]
    rootPart.CFrame = spawn.CFrame + Vector3.new(0, 5, 0)
end

-- Teleport player back to lobby
local function teleportToLobby(player: Player)
    local lobbySpawn = workspace:FindFirstChild("LobbySpawn")
    if not lobbySpawn or not player.Character then return end

    local rootPart = player.Character:FindFirstChild("HumanoidRootPart")
    if rootPart then
        rootPart.CFrame = lobbySpawn.CFrame + Vector3.new(0, 5, 0)
    end
end

-- Assign players to balanced teams
local function assignTeams()
    local players = Players:GetPlayers()
    roundParticipants = {}

    -- Shuffle for fairness
    for i = #players, 2, -1 do
        local j = math.random(1, i)
        players[i], players[j] = players[j], players[i]
    end

    for i, player in players do
        if i % 2 == 1 then
            player.Team = redTeam
        else
            player.Team = blueTeam
        end
        playerScores[player] = 0
        table.insert(roundParticipants, player)
    end
end

-- Register a kill/score
function RoundManager.addScore(player: Player, points: number)
    if currentState ~= "Playing" then return end
    if not playerScores[player] then return end

    playerScores[player] += points
    broadcastScores()
end

-- Determine winner
local function determineWinner(): (string, Player?)
    local topPlayer: Player? = nil
    local topScore = 0

    -- Individual scores
    for player, score in playerScores do
        if player.Parent == Players and score > topScore then
            topScore = score
            topPlayer = player
        end
    end

    -- Team scores
    local redScore, blueScore = 0, 0
    for player, score in playerScores do
        if player.Parent ~= Players then continue end
        if player.Team == redTeam then
            redScore += score
        elseif player.Team == blueTeam then
            blueScore += score
        end
    end

    local winningTeam = "Tie"
    if redScore > blueScore then
        winningTeam = "Red"
    elseif blueScore > redScore then
        winningTeam = "Blue"
    end

    return winningTeam, topPlayer
end

-- Check if a player reached the score limit
local function checkScoreLimit(): boolean
    for _, score in playerScores do
        if score >= SCORE_TO_WIN then
            return true
        end
    end
    return false
end

-- State: Intermission
local function stateIntermission()
    currentState = "Intermission"
    roundNumber += 1

    -- Move all players to lobby team
    for _, player in Players:GetPlayers() do
        player.Team = lobbyTeam
        task.spawn(function()
            player:LoadCharacter()
            task.wait(0.5)
            teleportToLobby(player)
        end)
    end

    unloadMap()
    currentMapName = selectNextMap()
    broadcastState("Intermission", { duration = INTERMISSION_TIME, nextMap = currentMapName, round = roundNumber })

    for i = INTERMISSION_TIME, 1, -1 do
        broadcastState("Intermission", { timeLeft = i, nextMap = currentMapName, round = roundNumber })
        task.wait(1)
    end
end

-- State: Countdown
local function stateCountdown()
    currentState = "Countdown"

    -- Load map
    currentMap = loadMap(currentMapName)

    -- Assign teams and reset scores
    assignTeams()

    -- Spawn characters at team spawn points
    for _, player in roundParticipants do
        if player.Parent ~= Players then continue end

        task.spawn(function()
            player:LoadCharacter()
            task.wait(0.5) -- brief wait for character to load

            local teamName = if player.Team == redTeam then "Red" else "Blue"
            teleportToSpawn(player, getSpawnPoints(teamName))
        end)
    end

    -- Freeze players during countdown (disable movement)
    -- This is optional but improves feel
    for i = COUNTDOWN_TIME, 1, -1 do
        broadcastState("Countdown", { timeLeft = i })
        task.wait(1)
    end
end

-- State: Playing
local function statePlaying()
    currentState = "Playing"
    playerScores = {}
    for _, player in roundParticipants do
        if player.Parent == Players then
            playerScores[player] = 0
        end
    end

    broadcastState("Playing", { duration = ROUND_TIME })
    broadcastScores()

    -- Round timer with early exit on score limit
    for i = ROUND_TIME, 1, -1 do
        if currentState ~= "Playing" then break end

        if checkScoreLimit() then
            break
        end

        broadcastState("Playing", { timeLeft = i })
        task.wait(1)
    end
end

-- State: Results
local function stateResults()
    currentState = "Results"

    local winningTeam, topPlayer = determineWinner()
    local topPlayerName = if topPlayer then topPlayer.Name else "Nobody"

    broadcastState("Results", {
        winningTeam = winningTeam,
        topPlayer = topPlayerName,
        duration = RESULTS_TIME,
    })

    task.wait(RESULTS_TIME)
end

-- Handle player death during a round (respawn at team spawn)
local function onCharacterDied(player: Player)
    if currentState ~= "Playing" then return end

    task.wait(3) -- respawn delay
    if player.Parent ~= Players then return end
    if currentState ~= "Playing" then return end

    player:LoadCharacter()
    task.wait(0.5)

    local teamName = if player.Team == redTeam then "Red" else "Blue"
    teleportToSpawn(player, getSpawnPoints(teamName))
end

-- Wire up character death tracking
Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        local humanoid = character:WaitForChild("Humanoid")
        humanoid.Died:Connect(function()
            onCharacterDied(player)
        end)
    end)
end)

-- Clean up player from round on disconnect
Players.PlayerRemoving:Connect(function(player)
    playerScores[player] = nil
    local idx = table.find(roundParticipants, player)
    if idx then
        table.remove(roundParticipants, idx)
    end
end)

-- Main game loop
function RoundManager.startRound()
    while true do
        stateIntermission()
        stateCountdown()
        statePlaying()
        stateResults()
    end
end

-- Start automatically or called from LobbyManager
return RoundManager
```

### Client-Side Round HUD

```luau
-- StarterPlayerScripts/RoundHud.client.luau

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local roundRemotes = ReplicatedStorage:WaitForChild("RoundRemotes")
local roundStateEvent = roundRemotes:WaitForChild("RoundState")
local scoreUpdateEvent = roundRemotes:WaitForChild("ScoreUpdate")

-- Build HUD (top-center status bar)
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "RoundHud"
screenGui.ResetOnSpawn = false
screenGui.Parent = playerGui

local statusLabel = Instance.new("TextLabel")
statusLabel.Size = UDim2.fromScale(0.4, 0.06)
statusLabel.Position = UDim2.fromScale(0.3, 0.02)
statusLabel.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
statusLabel.BackgroundTransparency = 0.4
statusLabel.TextColor3 = Color3.new(1, 1, 1)
statusLabel.TextScaled = true
statusLabel.Font = Enum.Font.GothamBold
statusLabel.Parent = screenGui

local uiCorner = Instance.new("UICorner")
uiCorner.CornerRadius = UDim.new(0, 8)
uiCorner.Parent = statusLabel

roundStateEvent.OnClientEvent:Connect(function(state: string, data: { [string]: any })
    if state == "Intermission" then
        local timeLeft = data.timeLeft or data.duration
        statusLabel.Text = `INTERMISSION | Next: {data.nextMap or "?"} | {timeLeft}s`
        statusLabel.BackgroundColor3 = Color3.fromRGB(40, 40, 100)
    elseif state == "Countdown" then
        statusLabel.Text = `GET READY! {data.timeLeft}`
        statusLabel.BackgroundColor3 = Color3.fromRGB(200, 150, 0)
    elseif state == "Playing" then
        statusLabel.Text = `ROUND | {data.timeLeft or data.duration}s`
        statusLabel.BackgroundColor3 = Color3.fromRGB(0, 120, 0)
    elseif state == "Results" then
        statusLabel.Text = `{data.winningTeam} wins! MVP: {data.topPlayer}`
        statusLabel.BackgroundColor3 = Color3.fromRGB(150, 50, 0)
    end
end)

scoreUpdateEvent.OnClientEvent:Connect(function(scores: { [string]: number })
    -- Update a scoreboard UI (implementation depends on your UI framework)
end)
```

---

## 6. TeleportService

TeleportService handles moving players between places (separate experiences within a universe) or between servers of the same place.

### Multi-Place Architecture

A typical multi-place setup:

```
Universe (Experience)
  |-- Hub/Lobby Place (start place)
  |-- Arena Place
  |-- Minigame Place A
  |-- Minigame Place B
```

Each place has its own PlaceId. Players start at the start place and are teleported to sub-places.

### TeleportAsync

```luau
local TeleportService = game:GetService("TeleportService")
local Players = game:GetService("Players")

local ARENA_PLACE_ID = 123456789 -- Replace with your actual PlaceId

-- Teleport a single player
local function teleportPlayer(player: Player)
    local success, result = pcall(function()
        return TeleportService:TeleportAsync(ARENA_PLACE_ID, { player })
    end)

    if not success then
        warn(`Teleport failed for {player.Name}: {result}`)
    end
end

-- Teleport a group of players together (they land on the same server)
local function teleportGroup(players: { Player })
    local success, result = pcall(function()
        return TeleportService:TeleportAsync(ARENA_PLACE_ID, players)
    end)

    if not success then
        warn(`Group teleport failed: {result}`)
    end
end
```

### TeleportOptions and Data Passing

`TeleportOptions` lets you configure the teleport and pass data between places.

```luau
local function teleportWithData(players: { Player }, matchData: { [string]: any })
    local teleportOptions = Instance.new("TeleportOptions")

    -- Pass data that all players in this teleport can read on arrival
    teleportOptions:SetTeleportData({
        matchId = matchData.matchId,
        gameMode = matchData.gameMode,
        teams = matchData.teams,
    })

    -- Optionally target a reserved server
    if matchData.reservedCode then
        teleportOptions.ReservedServerAccessCode = matchData.reservedCode
    end

    local success, result = pcall(function()
        return TeleportService:TeleportAsync(ARENA_PLACE_ID, players, teleportOptions)
    end)

    if not success then
        warn(`Teleport with data failed: {result}`)
    end
end
```

### Reading Teleport Data on Arrival

```luau
-- In the destination place's server script
local TeleportService = game:GetService("TeleportService")
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player: Player)
    local joinData = player:GetJoinData()
    local teleportData = joinData.TeleportData

    if teleportData then
        print(`Player {player.Name} arrived with match ID: {teleportData.matchId}`)
        print(`Game mode: {teleportData.gameMode}`)
        -- Use this data to set up the match
    end
end)
```

### ReservedServer for Private Matches

Reserved servers are free, programmatically-created private servers. They are essential for matchmaking.

```luau
local TeleportService = game:GetService("TeleportService")

local ARENA_PLACE_ID = 123456789

-- Step 1: Reserve a server (returns an access code)
local success, accessCode = pcall(function()
    return TeleportService:ReserveServer(ARENA_PLACE_ID)
end)

if not success then
    warn(`Failed to reserve server: {accessCode}`)
    return
end

-- Step 2: Teleport players to the reserved server
local teleportOptions = Instance.new("TeleportOptions")
teleportOptions.ReservedServerAccessCode = accessCode
teleportOptions:SetTeleportData({
    matchId = "MATCH_001",
    gameMode = "Deathmatch",
})

local success2, err = pcall(function()
    TeleportService:TeleportAsync(ARENA_PLACE_ID, playersToTeleport, teleportOptions)
end)

if not success2 then
    warn(`Teleport to reserved server failed: {err}`)
end
```

### Teleport Error Handling

Teleports can fail for many reasons (rate limits, player in another teleport, server full). Always handle failures.

```luau
local TeleportService = game:GetService("TeleportService")

-- Listen for teleport failures (fires on the client)
-- Server-side retry pattern:
local MAX_RETRIES = 3
local RETRY_DELAY = 2

local function teleportWithRetry(placeId: number, players: { Player }, options: TeleportOptions?)
    for attempt = 1, MAX_RETRIES do
        local success, result = pcall(function()
            return TeleportService:TeleportAsync(placeId, players, options)
        end)

        if success then
            return true
        end

        warn(`Teleport attempt {attempt}/{MAX_RETRIES} failed: {result}`)

        if attempt < MAX_RETRIES then
            task.wait(RETRY_DELAY)

            -- Remove disconnected players before retry
            local validPlayers = {}
            for _, player in players do
                if player.Parent then
                    table.insert(validPlayers, player)
                end
            end
            players = validPlayers

            if #players == 0 then
                return false
            end
        end
    end

    warn("All teleport retries exhausted")
    return false
end
```

### TeleportInitFailed (Client-Side)

```luau
-- StarterPlayerScripts/TeleportHandler.client.luau

local TeleportService = game:GetService("TeleportService")

TeleportService.TeleportInitFailed:Connect(function(player, teleportResult, errorMessage)
    warn(`Teleport failed: {teleportResult} - {errorMessage}`)
    -- Show error UI to the player
end)
```

---

## 7. MessagingService

MessagingService provides cross-server publish/subscribe messaging. Messages sent from one server can be received by all other servers in the same experience.

### Basic Pub/Sub

```luau
local MessagingService = game:GetService("MessagingService")

local TOPIC = "GlobalAnnouncements"

-- Subscribe to a topic (do this once on server startup)
local success, subscription = pcall(function()
    return MessagingService:SubscribeAsync(TOPIC, function(message)
        -- message.Data contains the published data
        -- message.Sent is the Unix timestamp when it was published
        local data = message.Data
        print(`[Global] {data.text} (from server {data.serverId})`)

        -- Broadcast to all players on this server
        for _, player in game:GetService("Players"):GetPlayers() do
            -- Fire a remote to show announcement UI
        end
    end)
end)

if not success then
    warn(`Failed to subscribe to {TOPIC}: {subscription}`)
end

-- Publish a message (all subscribed servers receive it, including this one)
local function announce(text: string)
    local success, err = pcall(function()
        MessagingService:PublishAsync(TOPIC, {
            text = text,
            serverId = game.JobId,
            timestamp = os.time(),
        })
    end)

    if not success then
        warn(`Failed to publish to {TOPIC}: {err}`)
    end
end
```

### Rate Limits

MessagingService has strict rate limits. Exceeding them causes errors.

| Limit | Value |
|---|---|
| **PublishAsync** | 150 + 60 * numPlayers messages per minute |
| **SubscribeAsync** | 5 + 2 * numPlayers subscriptions per minute |
| **Message size** | 1 KB per message |
| **Messages received** | (150 + 60 * numPlayers) * numSubscriptions per minute |

For a server with 20 players: 150 + 60 * 20 = **1,350 publishes per minute**.

### Use Case: Global Server List

```luau
-- ServerScriptService/ServerList.luau

local MessagingService = game:GetService("MessagingService")
local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")

local HEARTBEAT_TOPIC = "ServerHeartbeat"
local HEARTBEAT_INTERVAL = 30 -- seconds

-- Subscribe to heartbeats from other servers
local serverList: { [string]: { playerCount: number, maxPlayers: number, lastSeen: number } } = {}

pcall(function()
    MessagingService:SubscribeAsync(HEARTBEAT_TOPIC, function(message)
        local data = message.Data
        serverList[data.jobId] = {
            playerCount = data.playerCount,
            maxPlayers = data.maxPlayers,
            lastSeen = os.time(),
        }
    end)
end)

-- Broadcast this server's info periodically
task.spawn(function()
    while true do
        pcall(function()
            MessagingService:PublishAsync(HEARTBEAT_TOPIC, {
                jobId = game.JobId,
                playerCount = #Players:GetPlayers(),
                maxPlayers = Players.MaxPlayers,
            })
        end)
        task.wait(HEARTBEAT_INTERVAL)
    end
end)

-- Prune stale servers
task.spawn(function()
    while true do
        task.wait(60)
        local now = os.time()
        for jobId, info in serverList do
            if now - info.lastSeen > 90 then
                serverList[jobId] = nil
            end
        end
    end
end)
```

### Use Case: Cross-Server Global Events

```luau
-- Trigger a global event (e.g., double XP, boss spawn, holiday event)
local EVENTS_TOPIC = "GlobalEvents"

-- Publisher (admin server or admin command)
local function triggerGlobalEvent(eventName: string, duration: number)
    pcall(function()
        MessagingService:PublishAsync(EVENTS_TOPIC, {
            event = eventName,
            startTime = os.time(),
            duration = duration,
        })
    end)
end

-- Subscriber (every server)
pcall(function()
    MessagingService:SubscribeAsync(EVENTS_TOPIC, function(message)
        local data = message.Data
        if data.event == "DoubleXP" then
            -- Set a global multiplier
            _G.XPMultiplier = 2
            task.delay(data.duration, function()
                _G.XPMultiplier = 1
            end)
        end
    end)
end)
```

---

## 8. Matchmaking

Roblox does not provide a built-in matchmaking service. You must build one using DataStores, TeleportService, and optionally MessagingService.

### Concepts

- **Skill-Based Matching:** Track player skill (ELO, MMR, rank) in a DataStore. Match players with similar ratings.
- **Queue System:** Players join a queue. When enough players are queued, create a reserved server and teleport them.
- **Party Queuing:** Groups of friends queue together as a unit.

### ELO/MMR Tracking

```luau
-- ServerScriptService/Modules/EloSystem.luau

local DataStoreService = game:GetService("DataStoreService")
local eloStore = DataStoreService:GetDataStore("PlayerElo")

local EloSystem = {}

local DEFAULT_ELO = 1000
local K_FACTOR = 32

function EloSystem.getElo(userId: number): number
    local success, elo = pcall(function()
        return eloStore:GetAsync(`elo_{userId}`)
    end)
    return if success and elo then elo else DEFAULT_ELO
end

function EloSystem.saveElo(userId: number, elo: number)
    pcall(function()
        eloStore:SetAsync(`elo_{userId}`, math.floor(elo))
    end)
end

function EloSystem.calculateNewElo(winnerElo: number, loserElo: number): (number, number)
    local expectedWinner = 1 / (1 + 10 ^ ((loserElo - winnerElo) / 400))
    local expectedLoser = 1 - expectedWinner

    local newWinnerElo = winnerElo + K_FACTOR * (1 - expectedWinner)
    local newLoserElo = loserElo + K_FACTOR * (0 - expectedLoser)

    return math.floor(newWinnerElo), math.max(0, math.floor(newLoserElo))
end

return EloSystem
```

### Queue System with Reserved Servers

```luau
-- ServerScriptService/MatchmakingQueue.luau

local TeleportService = game:GetService("TeleportService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EloSystem = require(script.Parent.Modules.EloSystem)

local ARENA_PLACE_ID = 123456789
local MATCH_SIZE = 2 -- 1v1
local ELO_RANGE = 200 -- max ELO difference for matching
local ELO_RANGE_EXPAND_INTERVAL = 15 -- expand range every 15 seconds
local ELO_RANGE_EXPAND_AMOUNT = 50

-- Remotes
local QueueRemote = Instance.new("RemoteEvent")
QueueRemote.Name = "QueueRemote"
QueueRemote.Parent = ReplicatedStorage

local QueueStatusRemote = Instance.new("RemoteEvent")
QueueStatusRemote.Name = "QueueStatus"
QueueStatusRemote.Parent = ReplicatedStorage

-- Queue state
type QueueEntry = {
    player: Player,
    elo: number,
    joinedAt: number,
}

local queue: { QueueEntry } = {}

local function removeFromQueue(player: Player)
    for i = #queue, 1, -1 do
        if queue[i].player == player then
            table.remove(queue, i)
            return
        end
    end
end

local function isInQueue(player: Player): boolean
    for _, entry in queue do
        if entry.player == player then
            return true
        end
    end
    return false
end

local function findMatch(entry: QueueEntry): QueueEntry?
    local now = os.time()
    local waitTime = now - entry.joinedAt
    local expandedRange = ELO_RANGE + math.floor(waitTime / ELO_RANGE_EXPAND_INTERVAL) * ELO_RANGE_EXPAND_AMOUNT

    for _, other in queue do
        if other.player == entry.player then continue end
        if math.abs(entry.elo - other.elo) <= expandedRange then
            return other
        end
    end
    return nil
end

local function createMatch(players: { Player })
    -- Reserve a server
    local success, accessCode = pcall(function()
        return TeleportService:ReserveServer(ARENA_PLACE_ID)
    end)

    if not success then
        warn(`Failed to reserve server: {accessCode}`)
        for _, player in players do
            QueueStatusRemote:FireClient(player, "Error", "Failed to create match. Please try again.")
        end
        return
    end

    -- Build match data
    local matchData = {
        matchId = game:GetService("HttpService"):GenerateGUID(false),
        players = {},
    }
    for _, player in players do
        table.insert(matchData.players, { userId = player.UserId, name = player.Name })
    end

    -- Teleport
    local teleportOptions = Instance.new("TeleportOptions")
    teleportOptions.ReservedServerAccessCode = accessCode
    teleportOptions:SetTeleportData(matchData)

    for _, player in players do
        QueueStatusRemote:FireClient(player, "MatchFound", "Teleporting to arena...")
    end

    local teleportSuccess, err = pcall(function()
        TeleportService:TeleportAsync(ARENA_PLACE_ID, players, teleportOptions)
    end)

    if not teleportSuccess then
        warn(`Match teleport failed: {err}`)
    end
end

-- Queue processing loop
task.spawn(function()
    while true do
        task.wait(1)

        -- Clean disconnected players
        for i = #queue, 1, -1 do
            if queue[i].player.Parent ~= Players then
                table.remove(queue, i)
            end
        end

        -- Attempt to find matches
        local matched: { [Player]: boolean } = {}

        for _, entry in queue do
            if matched[entry.player] then continue end

            local opponent = findMatch(entry)
            if opponent and not matched[opponent.player] then
                matched[entry.player] = true
                matched[opponent.player] = true

                -- Remove both from queue and create match
                removeFromQueue(entry.player)
                removeFromQueue(opponent.player)
                task.spawn(createMatch, { entry.player, opponent.player })
            end
        end
    end
end)

-- Handle queue join/leave
QueueRemote.OnServerEvent:Connect(function(player: Player, action: string)
    if action == "join" then
        if isInQueue(player) then return end

        local elo = EloSystem.getElo(player.UserId)
        table.insert(queue, {
            player = player,
            elo = elo,
            joinedAt = os.time(),
        })
        QueueStatusRemote:FireClient(player, "Queued", `Searching... (ELO: {elo})`)

    elseif action == "leave" then
        removeFromQueue(player)
        QueueStatusRemote:FireClient(player, "Left", "Removed from queue.")
    end
end)

-- Auto-remove on disconnect
Players.PlayerRemoving:Connect(function(player)
    removeFromQueue(player)
end)
```

---

## 9. Instance Management

### Server Types

| Type | Cost | Creation | Use Case |
|---|---|---|---|
| **Public Server** | Free | Automatic (Roblox fills them) | Default gameplay |
| **Reserved Server** | Free | `TeleportService:ReserveServer()` | Matchmaking, private matches, instanced dungeons |
| **Private Server (VIP)** | Paid (Robux, set by developer) | Player purchases via game page | Player-owned private spaces |

### Reserved Servers

Reserved servers are the backbone of custom matchmaking. They are created on demand, receive an access code, and only players with that code can join.

```luau
-- Create a reserved server
local accessCode = TeleportService:ReserveServer(placeId)

-- This code can be:
-- 1. Used immediately to teleport players
-- 2. Stored in a DataStore for later use (e.g., persistent worlds)
-- 3. Shared via MessagingService so other servers can direct players to it
```

### Server Capacity

```luau
local Players = game:GetService("Players")

-- Maximum players for this server (set in Game Settings)
print(Players.MaxPlayers) -- e.g., 50

-- Preferred player count (Roblox matchmaker target)
-- Set via Game Settings > Places > Max Players
-- For reserved servers, the limit is the place's MaxPlayers setting
```

### Detecting Server Type

```luau
-- On the destination server:
local privateServerId = game.PrivateServerId
local privateServerOwnerId = game.PrivateServerOwnerId

if privateServerId ~= "" and privateServerOwnerId == 0 then
    print("This is a Reserved Server (matchmaking)")
elseif privateServerId ~= "" and privateServerOwnerId ~= 0 then
    print(`This is a VIP/Private Server owned by UserId {privateServerOwnerId}`)
else
    print("This is a public server")
end
```

---

## 10. Best Practices

### Handle Disconnects Gracefully

```luau
-- Save data BEFORE teleporting (data can be lost during server hops)
local function safeTeleport(player: Player, placeId: number, options: TeleportOptions?)
    -- Save all player data first
    local DataManager = require(script.Parent.Modules.DataManager)
    DataManager.savePlayerData(player)

    -- Small delay to ensure save completes
    task.wait(0.5)

    -- Then teleport
    pcall(function()
        TeleportService:TeleportAsync(placeId, { player }, options)
    end)
end
```

### Auto-Save During Rounds

```luau
-- Periodic auto-save to prevent data loss from crashes
local AUTO_SAVE_INTERVAL = 120 -- every 2 minutes

task.spawn(function()
    while true do
        task.wait(AUTO_SAVE_INTERVAL)
        for _, player in Players:GetPlayers() do
            task.spawn(function()
                pcall(function()
                    DataManager.savePlayerData(player)
                end)
            end)
        end
    end
end)
```

### Validate Player Counts

```luau
-- Before starting a round, verify enough players are still connected
local function validatePlayerCount(minimum: number): boolean
    local count = #Players:GetPlayers()
    if count < minimum then
        warn(`Not enough players to start: {count}/{minimum}`)
        return false
    end
    return true
end
```

### Anti-AFK System

```luau
-- ServerScriptService/AntiAfk.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local AFK_TIMEOUT = 300 -- 5 minutes
local AFK_WARNING = 240 -- warn at 4 minutes

local AfkPingRemote = Instance.new("RemoteEvent")
AfkPingRemote.Name = "AfkPing"
AfkPingRemote.Parent = ReplicatedStorage

local AfkWarningRemote = Instance.new("RemoteEvent")
AfkWarningRemote.Name = "AfkWarning"
AfkWarningRemote.Parent = ReplicatedStorage

local lastActivity: { [Player]: number } = {}

-- Client pings on any input (mouse move, key press, touch)
AfkPingRemote.OnServerEvent:Connect(function(player: Player)
    lastActivity[player] = os.time()
end)

Players.PlayerAdded:Connect(function(player)
    lastActivity[player] = os.time()
end)

Players.PlayerRemoving:Connect(function(player)
    lastActivity[player] = nil
end)

-- Check loop
task.spawn(function()
    while true do
        task.wait(10)
        local now = os.time()
        for player, lastTime in lastActivity do
            if player.Parent ~= Players then continue end

            local idle = now - lastTime
            if idle >= AFK_TIMEOUT then
                player:Kick("You were kicked for being AFK.")
                lastActivity[player] = nil
            elseif idle >= AFK_WARNING then
                AfkWarningRemote:FireClient(player, AFK_TIMEOUT - idle)
            end
        end
    end
end)
```

**Client-side AFK ping:**

```luau
-- StarterPlayerScripts/AfkPing.client.luau

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local afkPing = ReplicatedStorage:WaitForChild("AfkPing")

local PING_THROTTLE = 10 -- only ping every 10 seconds max
local lastPing = 0

UserInputService.InputBegan:Connect(function()
    local now = os.clock()
    if now - lastPing >= PING_THROTTLE then
        lastPing = now
        afkPing:FireServer()
    end
end)
```

### Handle Mid-Round Joins

```luau
-- When a player joins during an active round, decide what to do:
Players.PlayerAdded:Connect(function(player)
    if currentState == "Playing" then
        -- Option A: Add them as a spectator
        player.Team = lobbyTeam
        -- Show spectator UI

        -- Option B: Add them to the round (if team-based, pick smaller team)
        -- player.Team = getSmallestTeam({ redTeam, blueTeam })
        -- player:LoadCharacter()
        -- teleportToSpawn(player, getSpawnPoints(player.Team.Name))
        -- playerScores[player] = 0

    elseif currentState == "Intermission" then
        -- Normal join, they'll be included in the next round
        player.Team = lobbyTeam
        player:LoadCharacter()
    end
end)
```

### BindToClose for Server Shutdowns

```luau
-- Ensure data saves even when Roblox shuts down the server
game:BindToClose(function()
    for _, player in Players:GetPlayers() do
        task.spawn(function()
            pcall(function()
                DataManager.savePlayerData(player)
            end)
        end)
    end

    -- Give DataStore calls time to complete
    task.wait(3)
end)
```

---

## 11. Anti-Patterns

### Not Handling Teleport Failures

```luau
-- BAD: Fire and forget
TeleportService:TeleportAsync(placeId, { player })

-- GOOD: Wrap in pcall, retry on failure
local success, err = pcall(function()
    TeleportService:TeleportAsync(placeId, { player })
end)
if not success then
    warn(`Teleport failed: {err}`)
    -- Retry or notify player
end
```

### Losing Data During Server Hop

```luau
-- BAD: Teleport without saving
QueueRemote.OnServerEvent:Connect(function(player, action)
    if action == "join" then
        TeleportService:TeleportAsync(arenaPlaceId, { player })
    end
end)

-- GOOD: Save then teleport
QueueRemote.OnServerEvent:Connect(function(player, action)
    if action == "join" then
        DataManager.savePlayerData(player)
        task.wait(0.5)
        pcall(function()
            TeleportService:TeleportAsync(arenaPlaceId, { player })
        end)
    end
end)
```

### Unbalanced Teams

```luau
-- BAD: Random or first-come assignment
player.Team = if math.random() > 0.5 then redTeam else blueTeam

-- GOOD: Always assign to the smallest team
player.Team = getSmallestTeam({ redTeam, blueTeam })
```

### No Reconnection / Rejoin Support

If your game involves long sessions (RPGs, survival), consider allowing rejoins:

```luau
-- Store the reserved server access code in a DataStore keyed by UserId
-- When a player reconnects, check if they have an active session:

local function checkActiveSession(player: Player): string?
    local success, code = pcall(function()
        return sessionStore:GetAsync(`session_{player.UserId}`)
    end)
    if success and code then
        return code -- reserved server access code
    end
    return nil
end

Players.PlayerAdded:Connect(function(player)
    local activeCode = checkActiveSession(player)
    if activeCode then
        -- Offer to rejoin
        -- If accepted:
        local options = Instance.new("TeleportOptions")
        options.ReservedServerAccessCode = activeCode
        pcall(function()
            TeleportService:TeleportAsync(ARENA_PLACE_ID, { player }, options)
        end)
    end
end)
```

### Not Cleaning Up State on Player Leave

```luau
-- BAD: State tables grow forever
Players.PlayerRemoving:Connect(function(player)
    -- Nothing cleaned up
end)

-- GOOD: Remove player from all state tables
Players.PlayerRemoving:Connect(function(player)
    playerScores[player] = nil
    readyPlayers[player] = nil
    lastActivity[player] = nil

    local idx = table.find(roundParticipants, player)
    if idx then
        table.remove(roundParticipants, idx)
    end

    removeFromQueue(player)
end)
```

### Trusting Client for Match-Critical Logic

```luau
-- BAD: Client tells server the score
ScoreRemote.OnServerEvent:Connect(function(player, score)
    playerScores[player] = score -- Exploiter sends 999999
end)

-- GOOD: Server tracks all scoring
-- Only the server increments scores based on validated game events
-- (e.g., server detects a kill via Humanoid.Died and awards points)
```

---

## Quick Reference: Service Summary

| Service | Purpose | Key Methods/Events |
|---|---|---|
| **Players** | Player management | `PlayerAdded`, `PlayerRemoving`, `GetPlayers()`, `MaxPlayers` |
| **Teams** | Team assignment | `Team.AutoAssignable`, `Team:GetPlayers()`, `player.Team` |
| **TeleportService** | Cross-place movement | `TeleportAsync`, `ReserveServer`, `TeleportOptions` |
| **MessagingService** | Cross-server messaging | `PublishAsync`, `SubscribeAsync` |
| **DataStoreService** | Persistent data (ELO, sessions) | `GetAsync`, `SetAsync`, `UpdateAsync` |
