# Roblox Performance Optimization Reference

## 1. Overview

Load this reference when:

- A game runs slowly or hitches during play (frame drops, lag spikes).
- Optimizing for mobile devices or low-end hardware.
- Conducting a performance audit before release or after adding major features.
- Players report high memory usage, disconnects, or long load times.
- Scaling a game to support more concurrent players.

Performance optimization is not a one-time task. It should be revisited after every significant content addition and tested across the full range of target devices.

---

## 2. Performance Targets

| Metric | Desktop | Mobile |
|---|---|---|
| Frame Rate | 60 fps | 30 fps minimum |
| Memory Budget | ~1 GB | ~500 MB |
| Network | Minimize remote frequency | Same, with smaller payloads |
| Load Time | Under 10 seconds | Under 15 seconds |

**Key principles:**

- Always measure against the *lowest-spec target device*, not your development machine.
- Frame budget at 60 fps is ~16.6 ms per frame. At 30 fps it is ~33.3 ms.
- Network: keep RemoteEvent calls under 50 per second per client. Prefer batching.

---

## 3. Part Count Optimization

### Limits

- **Per model:** aim for a maximum of ~500 parts.
- **Total scene:** keep the visible scene under 10,000 parts.
- Fewer parts means less physics simulation, less rendering overhead, and faster replication.

### MeshParts Over Unions

- `UnionOperation` recalculates collision geometry at runtime and is more expensive.
- Export unions as MeshParts in Studio (right-click > Export Selection) and re-import.
- MeshParts use a fixed collision fidelity that is cheaper to compute.

### StreamingEnabled

For large maps, enable `Workspace.StreamingEnabled`:

- `StreamingTargetRadius` — the radius (in studs) the engine tries to keep loaded around the player. Start at 256 and tune.
- `StreamingMinRadius` — the minimum guaranteed radius. Set to ~64 to ensure nearby content is always present.
- `StreamingPauseMode` controls what happens when content is not yet loaded (Default, Disabled, ClientPhysicsPause).
- Mark critical models with `ModelStreamingMode = Persistent` so they are never streamed out.

### Anchoring

- **Anchor every static part.** Unanchored parts enter the physics solver even if they are not moving, consuming CPU every frame.
- Use `BasePart.Anchored = true` for terrain decorations, buildings, props, and anything that should not move.

---

## 4. Script Optimization

### Consolidated Heartbeat

Never scatter `RunService.Heartbeat:Connect(...)` across dozens of scripts. Consolidate into a single manager.

```lua
-- HeartbeatManager (single Script in ServerScriptService or a ModuleScript)
local RunService = game:GetService("RunService")

local HeartbeatManager = {}
HeartbeatManager._callbacks = {} :: { [string]: (dt: number) -> () }

function HeartbeatManager:Register(id: string, callback: (dt: number) -> ())
	self._callbacks[id] = callback
end

function HeartbeatManager:Unregister(id: string)
	self._callbacks[id] = nil
end

RunService.Heartbeat:Connect(function(dt: number)
	for _, callback in self._callbacks do
		callback(dt)
	end
end)

return HeartbeatManager
```

Usage from other modules:

```lua
local HeartbeatManager = require(path.to.HeartbeatManager)

HeartbeatManager:Register("EnemyAI", function(dt: number)
	-- update all enemies
end)

-- When no longer needed:
HeartbeatManager:Unregister("EnemyAI")
```

### Cache GetService Calls

```lua
-- GOOD: cache at the top of the script
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

-- BAD: calling GetService repeatedly
RunService.Heartbeat:Connect(function()
	local players = game:GetService("Players"):GetPlayers() -- wasteful
end)
```

### Avoid FindFirstChild in Tight Loops

```lua
-- BAD: searching the hierarchy every frame
RunService.Heartbeat:Connect(function()
	local hrp = workspace:FindFirstChild("Player1"):FindFirstChild("HumanoidRootPart")
end)

-- GOOD: cache the reference once
local hrp = character:WaitForChild("HumanoidRootPart")
RunService.Heartbeat:Connect(function()
	if hrp and hrp.Parent then
		-- use cached reference
	end
end)
```

### Table Pre-allocation

```lua
-- Pre-allocate a table with 100 slots
local results = table.create(100)
for i = 1, 100 do
	results[i] = computeValue(i)
end
```

### String Concatenation

```lua
-- BAD: creates a new string object every iteration
local result = ""
for i = 1, 1000 do
	result = result .. tostring(i) .. ","
end

-- GOOD: build a table, join once
local parts = table.create(1000)
for i = 1, 1000 do
	parts[i] = tostring(i)
end
local result = table.concat(parts, ",")
```

---

## 5. Memory Management

### Disconnect Events

Every `:Connect()` call returns a `RBXScriptConnection`. Store it and disconnect when done.

```lua
-- Event Cleanup Pattern
local Cleaner = {}
Cleaner.__index = Cleaner

function Cleaner.new()
	local self = setmetatable({}, Cleaner)
	self._connections = {} :: { RBXScriptConnection }
	self._instances = {} :: { Instance }
	return self
end

function Cleaner:Add(connection: RBXScriptConnection)
	table.insert(self._connections, connection)
	return connection
end

function Cleaner:AddInstance(instance: Instance)
	table.insert(self._instances, instance)
	return instance
end

function Cleaner:Clean()
	for _, conn in self._connections do
		if conn.Connected then
			conn:Disconnect()
		end
	end
	table.clear(self._connections)

	for _, inst in self._instances do
		inst:Destroy()
	end
	table.clear(self._instances)
end

return Cleaner
```

Usage:

```lua
local Cleaner = require(path.to.Cleaner)
local cleaner = Cleaner.new()

cleaner:Add(workspace.ChildAdded:Connect(function(child)
	print(child.Name, "added")
end))

cleaner:Add(Players.PlayerRemoving:Connect(function(player)
	print(player.Name, "left")
end))

-- When this system shuts down or the player leaves:
cleaner:Clean()
```

### Destroy Instances Properly

- Always call `:Destroy()` rather than setting `Parent = nil`. `:Destroy()` locks the instance, disconnects all events on it, and marks it for garbage collection.
- Setting `Parent = nil` keeps the instance alive if anything still references it.

### Avoid Reference Cycles

```lua
-- BAD: mutual references prevent garbage collection
local a = {}
local b = {}
a.ref = b
b.ref = a
-- Neither a nor b can be collected until both references are broken
```

Break references explicitly when done: `a.ref = nil; b.ref = nil`.

### Instance.Destroying

Use `Instance.Destroying` to run cleanup when an instance is about to be destroyed:

```lua
local part = Instance.new("Part")
part.Destroying:Connect(function()
	-- clean up related data, disconnect connections, etc.
end)
```

### Debris Service

For timed cleanup of temporary instances (projectiles, effects):

```lua
local Debris = game:GetService("Debris")
local bullet = Instance.new("Part")
bullet.Parent = workspace
Debris:AddItem(bullet, 5) -- destroyed after 5 seconds
```

---

## 6. Network Optimization

### Minimize RemoteEvent Data Size

- Send only what changed, not full state.
- Use numeric IDs instead of long string keys when possible.
- Avoid sending Instance references when a name or ID suffices.

### Batch Related Remotes

```lua
-- BAD: three separate remote calls
remoteHealth:FireClient(player, health)
remoteAmmo:FireClient(player, ammo)
remoteStamina:FireClient(player, stamina)

-- GOOD: one call with a table
remotePlayerState:FireClient(player, {
	health = health,
	ammo = ammo,
	stamina = stamina,
})
```

### UnreliableRemoteEvent

For high-frequency, non-critical data such as position or rotation updates, use `UnreliableRemoteEvent`. Dropped packets are acceptable because the next update will correct the state.

```lua
-- In ReplicatedStorage, create an UnreliableRemoteEvent named "PositionSync"
local posSync = ReplicatedStorage:WaitForChild("PositionSync")

-- Server: fire frequently without guaranteeing delivery
RunService.Heartbeat:Connect(function()
	for _, player in Players:GetPlayers() do
		posSync:FireClient(player, npcPositions)
	end
end)
```

### Compress Large Data

- Strip unnecessary keys before sending.
- Use short key names (`hp` instead of `hitPoints`).
- Consider delta compression: send only values that changed since the last update.

### Reduce Replication

- Set visual-only properties on the client (particle colors, UI tweens).
- Properties changed on the server replicate to all clients automatically, which consumes bandwidth.

---

## 7. Rendering Optimization

### Level of Detail (LOD)

Create multiple versions of a model at different detail levels and swap based on distance:

```lua
local function setLOD(model: Model, playerPosition: Vector3)
	local distance = (model:GetPivot().Position - playerPosition).Magnitude
	if distance < 100 then
		-- show high-detail version
	elseif distance < 300 then
		-- show medium-detail version
	else
		-- show low-detail version or hide
	end
end
```

Roblox also has built-in `MeshPart.RenderFidelity` (Automatic, Performance, Precise) which controls mesh LOD.

### Draw Distance Limits

- Use `BasePart.CastShadow = false` on distant or small parts.
- Disable unnecessary `SurfaceLight`, `PointLight`, `SpotLight` on distant objects.
- With StreamingEnabled, the engine handles draw distance automatically.

### Particle Count Budgets

| Property | Recommended Max |
|---|---|
| Particles per emitter (`Rate`) | ~200 |
| Total active emitters in view | ~20 |
| Beam segments (`Segments`) | 10-20 |
| Trail `MaxLength` | Keep short for mobile |

- Set `ParticleEmitter.Enabled = false` when off-screen or far away.
- Use fewer, larger particles instead of many small ones.

### Texture Resolution

| Use Case | Max Resolution |
|---|---|
| General props, walls, floors | 512x512 |
| Hero assets (player characters, key items) | 1024x1024 |
| UI icons, decals | 256x256 to 512x512 |
| Sky/environment | 1024x1024 |

- Use `Decal` over `Texture` when the surface only needs one face covered. Decals are simpler to render.
- Compress textures before uploading. Avoid PNG when JPEG quality is acceptable.

---

## 8. Mobile-Specific Optimization

### Part Counts

- Target 30-50% fewer parts than desktop. If the desktop budget is 10K parts, aim for 5-7K on mobile.
- Use `UserInputService:GetPlatform()` or screen size to detect mobile and reduce detail.

### Simplified Particle Effects

- Halve the `Rate` of particle emitters on mobile.
- Reduce `Lifetime` to keep fewer active particles.
- Disable non-essential emitters entirely.

### Touch-Optimized UI

- Minimum touch target size: **44x44 points** (following Apple HIG).
- Add padding between interactive elements.
- Use `GuiObject.Active = true` to ensure touch events register.
- Avoid hover-dependent UI (mobile has no hover state).

### Reduced Draw Distance

```lua
if UserInputService.TouchEnabled then
	workspace.StreamingTargetRadius = 128 -- lower than desktop
	workspace.StreamingMinRadius = 48
end
```

### Memory-Efficient Assets

- Use lower-resolution textures on mobile (256x256 where desktop uses 512x512).
- Reduce mesh polygon counts for mobile LOD models.
- Monitor memory with `Stats():GetTotalMemoryUsageMb()` and warn/act if approaching 500 MB.

### Test on Low-End Devices

- Test on devices with 2-3 GB RAM (older iPads, budget Android phones).
- Use the Roblox mobile emulator in Studio, but always verify on real hardware.
- Check for thermal throttling during extended play sessions.

---

## 9. Profiling Tools

### MicroProfiler (Ctrl+F6 in Studio)

The MicroProfiler displays a real-time flame graph of what the engine is doing each frame.

**How to read it:**

1. Press `Ctrl+F6` to open. Press `Ctrl+P` to pause and inspect a frame.
2. Each horizontal bar is a task. Width represents time spent.
3. Look for bars that are unusually wide — these are your hot frames.
4. Common labels to watch:
   - `Heartbeat` — your Heartbeat scripts. If wide, your per-frame logic is too heavy.
   - `Physics` — collision and simulation. Reduce unanchored parts.
   - `Render/Perform` — GPU-bound. Reduce draw calls, textures, particles.
   - `Replication` — network overhead. Reduce remote calls and replicated property changes.
5. Click a bar to see details: script name, line number, time in microseconds.
6. Use the `microprofiler` dump (`Ctrl+F6` > `Dump`) to save a `.html` file for offline analysis.

### F9 Developer Console

- Press `F9` in-game or in Studio to open.
- **Log** tab: errors, warnings, print output.
- **Memory** tab: breakdown by category (Instances, PhysicsParts, Sounds, Scripts, Signals, etc.).
- **Stats** tab: FPS, ping, data send/receive rates.
- **Server Stats** (in-game): server heartbeat time, physics step time.

### Stats Service (Programmatic)

```lua
local Stats = game:GetService("Stats")

-- Total memory in MB
local totalMemory = Stats:GetTotalMemoryUsageMb()

-- Specific categories
local instanceMemory = Stats:GetMemoryUsageMbForTag(Enum.DeveloperMemoryTag.Instances)
local scriptMemory = Stats:GetMemoryUsageMbForTag(Enum.DeveloperMemoryTag.LuaHeap)

print(string.format("Total: %.1f MB | Instances: %.1f MB | Lua: %.1f MB",
	totalMemory, instanceMemory, scriptMemory))
```

---

## 10. Best Practices

### Profile Before Optimizing

Never guess where the bottleneck is. Use the MicroProfiler and memory stats to find the actual hot path before changing code.

### Optimize Hot Paths First

Focus effort on code that runs every frame (Heartbeat, RenderStepped) or on every player action. Code that runs once at startup is rarely worth optimizing.

### Spatial Queries Over Brute Force

```lua
-- BAD: loop over every part in workspace
for _, part in workspace:GetDescendants() do
	if (part.Position - origin).Magnitude < 50 then
		-- ...
	end
end

-- GOOD: spatial query
local params = OverlapParams.new()
params.FilterType = Enum.RaycastFilterType.Include
params.FilterDescendantsInstances = { workspace.Enemies }

local parts = workspace:GetPartBoundsInBox(
	CFrame.new(origin),
	Vector3.new(100, 100, 100), -- 50-stud radius box
	params
)
```

### Object Pooling

Reuse instances instead of creating and destroying them repeatedly.

```lua
-- Object Pool Pattern
local ObjectPool = {}
ObjectPool.__index = ObjectPool

function ObjectPool.new(template: Instance, initialSize: number)
	local self = setmetatable({}, ObjectPool)
	self._template = template
	self._available = table.create(initialSize)
	self._active = {} :: { [Instance]: boolean }

	-- Pre-populate
	for i = 1, initialSize do
		local clone = template:Clone()
		clone.Parent = nil
		table.insert(self._available, clone)
	end

	return self
end

function ObjectPool:Get(): Instance
	local obj: Instance
	if #self._available > 0 then
		obj = table.remove(self._available)
	else
		obj = self._template:Clone()
	end

	self._active[obj] = true
	return obj
end

function ObjectPool:Return(obj: Instance)
	if not self._active[obj] then
		return
	end

	self._active[obj] = nil
	obj.Parent = nil

	-- Reset state as needed (position, visibility, etc.)
	if obj:IsA("BasePart") then
		obj.CFrame = CFrame.new(0, -1000, 0) -- move off-screen
		obj.Anchored = true
		obj.Velocity = Vector3.zero
	end

	table.insert(self._available, obj)
end

function ObjectPool:ReturnAll()
	for obj in self._active do
		self:Return(obj)
	end
end

function ObjectPool:Destroy()
	for obj in self._active do
		obj:Destroy()
	end
	for _, obj in self._available do
		obj:Destroy()
	end
	table.clear(self._active)
	table.clear(self._available)
end

return ObjectPool
```

Usage:

```lua
local ObjectPool = require(path.to.ObjectPool)
local bulletTemplate = ReplicatedStorage.Assets.Bullet
local bulletPool = ObjectPool.new(bulletTemplate, 50)

-- Spawn a bullet
local bullet = bulletPool:Get()
bullet.CFrame = firePoint
bullet.Parent = workspace

-- Return when done
bulletPool:Return(bullet)
```

### Lazy-Load Distant Content

Do not load all assets at game start. Use StreamingEnabled or manually load content as the player approaches.

```lua
local function onPlayerMoved(position: Vector3)
	for _, zone in zones do
		local distance = (zone.center - position).Magnitude
		if distance < zone.loadRadius and not zone.loaded then
			zone:Load()
		elseif distance > zone.unloadRadius and zone.loaded then
			zone:Unload()
		end
	end
end
```

---

## 11. Anti-Patterns

### Premature Optimization

Optimizing code that is not a bottleneck wastes development time and often makes code harder to read. Always profile first.

### Creating/Destroying Instances in Heartbeat

```lua
-- ANTI-PATTERN: creating parts every frame
RunService.Heartbeat:Connect(function()
	local part = Instance.new("Part") -- allocation every frame
	part.Parent = workspace
	task.delay(1, function()
		part:Destroy()
	end)
end)

-- FIX: use an object pool (see section 10)
```

### Large Uncompressed Data Over Remotes

```lua
-- ANTI-PATTERN: sending entire inventory every update
remote:FireClient(player, fullInventoryTable) -- could be thousands of entries

-- FIX: send only changes
remote:FireClient(player, { added = { itemId }, removed = { oldItemId } })
```

### Not Testing on Mobile

A game that runs at 60 fps on a gaming PC may run at 10 fps on a phone. Always test on actual mobile hardware, not just the Studio emulator.

### Ignoring Memory Leaks

Common leak sources:

- Event connections that are never disconnected.
- Instances removed from the hierarchy but still referenced in a table.
- Closures capturing large upvalues that outlive their usefulness.
- Module-level tables that grow indefinitely without cleanup.

Detect leaks by monitoring `Stats:GetTotalMemoryUsageMb()` over time. If memory grows continuously during gameplay without stabilizing, there is a leak.

```lua
-- Simple memory monitor
local lastMemory = 0
task.spawn(function()
	while true do
		local current = game:GetService("Stats"):GetTotalMemoryUsageMb()
		local delta = current - lastMemory
		if delta > 10 then
			warn(string.format("Memory spike: +%.1f MB (total: %.1f MB)", delta, current))
		end
		lastMemory = current
		task.wait(10)
	end
end)
```
