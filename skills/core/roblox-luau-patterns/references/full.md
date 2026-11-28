# Luau Patterns: Full Reference

> Examples are illustrative. Match the project's existing conventions and verify behavior in Studio.

## 1. Pick a shape from ownership, not fashion

Start with plain functions. Add state only when something must own it. Add an object only when several independent values need the same behavior and lifecycle.

| Need | Smallest useful shape |
| --- | --- |
| Pure transformation or validation | functions in a module |
| One subsystem owns state | module with private state and a narrow API |
| Many independent values share behavior | table plus metatable |
| Framework or lifecycle already established | existing project abstraction |

A module table is already a namespace. A class named `Manager`, `Service`, or `Controller` does not create a boundary by itself. Name the owned state and public contract. Split only when lifecycle, authority, or reasons to change are genuinely different.

Use `roblox-architecture` for cross-project dependency direction and startup order.

## 2. Metatable objects

```luau
local Countdown = {}
Countdown.__index = Countdown

export type Countdown = typeof(setmetatable(
    {} :: {
        remaining: number,
        finished: boolean,
    },
    Countdown
))

function Countdown.new(seconds: number): Countdown
    return setmetatable({
        remaining = seconds,
        finished = seconds <= 0,
    }, Countdown)
end

function Countdown:step(deltaTime: number): boolean
    if self.finished then
        return true
    end
    self.remaining = math.max(0, self.remaining - deltaTime)
    self.finished = self.remaining == 0
    return self.finished
end

return Countdown
```

Rules:

- Set `__index` on the class table.
- Call constructors with `.`, methods with `:`.
- Store mutable state on `self`. Fields on the class table are shared.
- Prefer composition to metatable inheritance. Inheritance obscures fields, construction, and cleanup, and often produces weak type inference.
- Give owned resources an explicit `destroy` or equivalent lifecycle only when the object actually owns resources.
- Share exactly one metatable per type. `__eq` dispatches only when both operands carry the *same* handler — two classes with separate `__eq` handlers silently compare by raw identity. Runtime hook semantics (`__newindex` absent-key interception, `__eq` dispatch, what the table library ignores): see `roblox-luau-core` §7.

Do not wrap a single table in an object merely to imitate another language.

## 3. Module state and startup

Top-level module code runs during `require` and can yield. Keep it cheap. Expose explicit initialization only when wiring cannot happen lazily.

```luau
local Registry = {}
local byPlayer: {[Player]: string} = {}

function Registry.get(player: Player): string?
    return byPlayer[player]
end

function Registry.set(player: Player, value: string)
    byPlayer[player] = value
end

function Registry.remove(player: Player)
    byPlayer[player] = nil
end

return Registry
```

The bootstrap, not each module, should own global startup order. Avoid every module inventing `Init` and `Start` by default. If phases exist, define what each phase guarantees and fail visibly when a dependency is unavailable. Never spawn all initializers concurrently when order matters.

Player removal is not a universal save or cleanup hook. It is one lifecycle signal. The canonical persistence layer owns save/release behavior, and each subsystem owns only its own player-keyed memory and connections.

### Name what yields: the `Async` suffix

Practitioner convention informed by [Kampfkarren’s guidelines](https://raw.githubusercontent.com/Kampfkarren/kampfkarren-luau-guidelines/main/README.md), independently written here. Make possible suspension visible at the API boundary. An `Async` suffix (`loadProfileAsync`) is one useful convention; document whether the call yields or returns a promise. Respect existing naming contracts and do not rename public APIs merely for style. A suffix does not enforce behavior or remove yield restrictions.

This is a naming convention, not an async framework. It coexists with promises, and with plain coroutines and `task.*` scheduling, without needing any library (practitioner design, not an engine rule).

### Return arity: `nil` is a value, "nothing" is not

`return` and `return nil` produce different results. A function that ends with bare `return` (or falls off the end) returns *no values*; `return nil` returns *one value, nil* — and the difference is visible when forwarding or counting results.

For fixed result contracts, keep the number of returned values consistent. A `(value, errorMessage)` API should return two values on every path, such as `return nil, message` or `return value, nil`. Ordinary assignment pads missing values with nil, but forwarding multiple results or counting them exposes the difference. Variable-result APIs can be intentional; document them rather than imposing fixed arity universally.

### Return a named variable from modules

Practitioner preference: a named local export can make a module easier to search and annotate. Prefer it when that helps readability, not as a correctness rule. Anonymous returns remain valid, including established story/spec conventions. This adds no new wrapper or abstraction.

## 4. Instance visibility and ancestry

Configure before parenting when descendants, listeners, plugins, or replication should observe only a complete object.

```luau
local marker = Instance.new("Part")
marker.Name = "SpawnMarker"
marker.Anchored = true
marker.CanCollide = false
marker.Size = Vector3.new(1, 1, 1)
marker.CFrame = spawnCFrame
marker.Parent = workspace
```

This reduces exposure to partial state and unnecessary change observation. It does not solve an abstract "replication race." Some operations require ancestry or a specific parent. Parent earlier when the API contract requires it, then make partial visibility explicit.

For groups of instances, build under an unparented model and parent the completed model once. Avoid repeated full-tree searches in hot paths. Cache stable ownership references, use tags for dynamic collections, and handle streamed or destroyed instances becoming unavailable.

## 5. Signals and cleanup

The code that creates a connection owns it.

```luau
local connection: RBXScriptConnection? = nil

local function stop()
    if connection then
        connection:Disconnect()
        connection = nil
    end
end

connection = source.Changed:Connect(function(value)
    consume(value)
end)
```

Use `:Once()` for a genuinely one-shot event. Use `:Wait()` only when yielding the current thread is acceptable and cancellation or timeout is not required. For long-lived owners, collect connections, tasks, and instances behind one cleanup boundary. A cleanup library can be worthwhile when the project already uses one; one connection does not justify a dependency.

### Typed signal payloads

Engine-provided signals such as `RemoteEvent.OnServerEvent` are typed as `...any` in the API dump, so their payloads are unchecked. Custom signal classes can do better: make them generic (`Signal<T...>`) and type the payload once at the module boundary so every `.Connect` call site is checked. (Tooling-defined type surfaces such as `luau-lsp`'s exported `RBXScriptSignal<T...>` do carry payloads; the engine dump itself does not.)

```luau
type Purchased = Signal<{
    userId: number,
    productId: number,
}>

local purchased: Purchased = signal.new()

purchased:Connect(function(payload)
    -- payload.userId and payload.productId are checked here
    grantProduct(payload.userId, payload.productId)
end)
```

The useful habit is exporting the typed alias from the module that owns the signal and requiring that type at call sites, instead of re-declaring the payload shape inline each time. Without it, a typo like `productID` compiles and fails at runtime.

Disconnecting before destroying is useful when callbacks could run during teardown or captured references outlive the instance. Do not claim every destroyed instance leaks every attached connection. Verify the actual owner and references.

### Instance references

For an ordinary replicated reference, use an `ObjectValue` under a stable owner. With streaming enabled, its `Value` is `nil` until the target streams in, so callers must handle temporary absence. Attributes remain useful for lightweight configuration metadata.

<!-- temporal: 2026-08 -->

Studio beta adds instance-typed attributes (`Instance:SetAttribute("Target", otherInstance)`). Reading one back returns an `InstanceHandle`, not the instance: call `handle:Get()` (nil when the target is absent) or `handle:Wait(timeout)` (yields until it streams in). The handle exists so "attribute missing" (GetAttribute returns nil) stays distinguishable from "target not streamed in yet" (handle present, `Get()` nil). Treat this as beta until it reaches the stable engine reference, and verify current behavior before relying on it.

## 6. Task scheduling and cancellation

- `task.defer`: queue work after the current resumption cycle.
- `task.spawn`: start independent work promptly.
- `task.delay`: schedule after a duration.
- `task.cancel`: cancel a thread that is still owned and cancellable.
- `task.wait`: yield for an approximate duration, not a precise clock.

Do not use legacy `wait()`. Prefer a state-change signal when one exists; use `task.wait()` only for justified polling or cadence and give long-lived loops an explicit stop condition.

A spawned task has no automatic owner and no automatic error contract. Keep its handle when cancellation matters. Do not use spawning to hide required startup ordering or to turn an error into an unobserved background failure.

Event-driven work is preferable only when a real event represents the state change. Replacing a measured 10 Hz scan with `Heartbeat` creates a 60 Hz scan. If polling is necessary, choose cadence from responsiveness and cost, then measure it.

### Raw coroutine semantics

`task.*` covers scheduling; `coroutine.*` has its own lifecycle rules that schedulers, worker pools, and cancel-on-leave code hit directly. All points below verified against the live Luau runtime and the engine `coroutine` reference (2026-10):

- **Who owns the error.** `coroutine.resume` returns `false, errorValue` for a failure inside the coroutine (invalid arguments to `resume` can still throw) and the *caller* decides what the error means. `coroutine.wrap` returns a function that *propagates* errors into the calling code (wrap the call in `pcall` yourself). Pick by ownership, not by experience level: `resume` for schedulers that centralize failure handling, `wrap` for producer-style iteration where an error should surface at the call site.

```luau
local co = coroutine.create(function(word: string)
	local repetition = word
	while true do
		coroutine.yield(repetition)
		repetition ..= word
	end
end)

local ok, first = coroutine.resume(co, "Hi") -- first-resume args go to the body's parameters
print(ok, first)     -- true  Hi
local ok2, second = coroutine.resume(co)    -- later args become the yield() results
print(ok2, second)   -- true  HiHi
```

- **First-resume arguments are the body's parameters.** There is no pending yield to receive them; only the second and later resumes feed values to earlier `coroutine.yield` calls. Calling `wrap(...)`/`resume(co, ...)` with producer arguments on resume #2 is a classic silent bug: the body never sees them, and the yield receives them instead.
- **`coroutine.close(co)`** puts a suspended coroutine into the dead state and returns `true` (also `true` for a coroutine that already finished). For a coroutine that stopped on an *error*, it returns `false, message`. Resuming a closed coroutine fails with the ordinary `cannot resume dead coroutine`; there is no separate "closed" state. This is the manual counterpart of `task.cancel` for threads you created yourself — closing cancels the thread without treating the suspension as an error.
- A coroutine that errored reads `coroutine.status(co) == "dead"`, the same status as one that returned. `resume`'s `false` flag (or `wrap` raising) is the only signal that distinguishes an errored thread from a finished one.
- Yielding is prohibited inside metamethods regardless of the current thread; see `roblox-luau-core` §11 for the exact boundary behavior.

### `coroutine.finally`: cleanup when a thread ends

<!-- temporal: 2026-11 -->
Added to the Roblox `coroutine` reference in October 2026; the standalone Luau CLI used for the other probes here does not have it yet, so check it in Studio before relying on it. `coroutine.finally(co, callback)` registers a callback that runs once when `co` reaches a terminal state:

- `callback("finished", ...results)` when the body returned;
- `callback("error", err)` when it errored;
- `callback("cancelled")` when `coroutine.close` or `task.cancel` stopped it.

Callbacks run in reverse registration order and may yield. If one errors, the rest are skipped. Registering on a dead coroutine raises an error, and a coroutine driven through `coroutine.wrap` that ends with callbacks registered raises `cannot run finalizers from a wrapped coroutine`. When the engine resumes the thread or `task.cancel` closes it, the callbacks run on a separate thread and their errors surface as script errors. This gives a cancel-on-leave task one place to release what it holds, whichever way it ends.

```luau
-- Illustrative: release a claimed resource however the task ends.
local function runClaimed(claim: () -> (), release: () -> (), body: () -> ()): thread
    local co = coroutine.create(body)
    claim()
    coroutine.finally(co, function(status: string)
        if status == "error" then
            warn("claimed task failed")
        end
        release()
    end)
    task.spawn(co)
    return co -- task.cancel(co) also triggers release()
end

return runClaimed
```

## 7. Fallible calls without semantic collapse

`pcall` returns a transport/execution success flag followed by the function's results. A successful function may legitimately return `nil`.

```luau
local ok, value = pcall(dataStore.GetAsync, dataStore, key)
if not ok then
    return nil, `read failed: {value}`
end
return value, nil
```

Do not write a retry helper that returns only `T?`; it collapses "successful missing value" and "all attempts failed." Preserve a result shape or separate error value.

```luau
export type Attempt<T> =
    { ok: true, value: T }
    | { ok: false, error: string }
```

Retry policy is domain-specific:

- A read may be safe to repeat but still needs a bound and observable failure.
- A write, purchase grant, webhook side effect, or remote action may duplicate work.
- DataStore budgets, HTTP status, receipt retries, and session ownership have separate contracts.

Route persistence to `roblox-data`, purchases to `roblox-monetization`, web calls to `roblox-cloud`, and client requests to `roblox-networking`.

Use `xpcall` when a custom error handler or traceback is part of the diagnostic boundary. Do not add it mechanically around every function.

### Thrown vs returned failure

Luau has no exceptions-as-values; the two failure mechanisms answer different questions, and choosing the wrong one is what produces `pcall`-everything or `assert`-everything code:

- **Return the failure** when it is an expected outcome of the domain: not-found, full, invalid input, cooldown active. Test: a unit test *asserting this failure* would be reasonable. Shape it as `(boolean, string?)` or a tagged result (`Attempt<T>` above) so "success with nil" and "failed" stay distinct.
- **Throw the failure** (`error`) when the state must never be reachable: a broken invariant, an unhandled case, a misuse of the module's API. The crash is the point; the traceback is the diagnostic. `pcall` around your own module's routine failure is a smell that the module chose the wrong mechanism — and a wrapper layer that converts everything to `nil, err` destroys the distinction for callers.
- Catch at boundaries where something can actually be done: a remote handler answering the client, a request loop retrying, a connection shutting down. Validate external inputs (remotes, saves, commands) on arrival, at the edge, so inner code can rely on documented validated inputs. Preserve checks for internal invariants and changing state; boundary validation does not eliminate races.

Mechanics that matter for placement (probed 2026-10):

- The `xpcall` message handler runs **before** stack unwinding — it is the only place `debug.traceback` still shows the real error path. A `pcall` receives only the error message; the frames are gone by the time you could format them.
- `error(msg, 0)` drops the `script:line:` position prefix. Thrown values are not player-facing strings; build user-facing messages at the boundary from the ok flag, never by displaying raw error text.
- Arguments to `assert(value, buildMessage())` are evaluated eagerly even on success. In a measured hot path, build an expensive diagnostic inside `if not value then ... end`; a constant message does not have this construction cost.
- The `xpcall` handler may itself error (the call then fails with `error in error handling`) and only its first return value is used as the message.

## 8. Optional libraries

Promise, signal, cleanup, component, and remote libraries can encode useful contracts. They also add API surface, versioning, and team learning cost.

Use one when:

- the project already depends on it;
- multiple call sites need the same cancellation, cleanup, or composition semantics;
- its behavior is covered by tests and current documentation.

Do not recommend a package from name recognition alone. Verify maintenance, license, current API, and whether native Luau plus a small explicit pattern is enough. Install through the package manager already used by the project.

## Static Scan Interpretation

Static searches for `:Destroy(`, `:Disconnect(`, `Janitor`, `Maid`, or wait calls are review prompts, not proof of correct teardown or scheduling. Trace whether cleanup is reachable, whether every owned resource is covered, and whether a wait-coupled loop has a justified cadence or should respond to a real state-change event.

## 9. Review checklist

- The chosen shape is the smallest one that represents ownership.
- Public API and mutable private state are obvious.
- No circular `require` or hidden top-level yield.
- Startup order is explicit where order matters.
- Every connection, task, and created instance has an owner and endpoint.
- Successful `nil`, thrown errors, cancellation, timeout, and retry exhaustion stay distinct.
- Return arity is consistent across all branches: a function returning `(value, error)` never falls back to a bare `return`.
- Possible yields are visible in naming or documentation; existing API contracts are preserved.
- Named module exports are used where they improve readability, not enforced as a blanket style rule.
- Retried operations are safe to repeat or idempotent.
- Partial instance visibility is intentional.
- No new manager class, framework, or dependency exists only to namespace one feature.
- Security, persistence, purchases, networking, and performance are handed to their canonical skills.

## 10. Hot-path micro-optimizations

Moved from `roblox-performance`, which keeps profiling, budgets, and engine
tuning. These are code-level patterns: measure first, then apply only on paths
the profiler confirms are hot.

### Object Pooling

Pre-clone and reuse instances to avoid allocation spikes and garbage-collection
pressure on spawn-heavy paths.

```luau
local Pool = {}
Pool.__index = Pool

function Pool.new(template: Instance, initialSize: number)
    local self = setmetatable({
        _template = template,
        _available = {},
        _leases = {}, -- Instance -> token held by its current borrower
    }, Pool)

    for _ = 1, initialSize do
        local obj = template:Clone()
        obj.Parent = nil
        table.insert(self._available, obj)
    end
    return self
end

function Pool:get(): (Instance, any)
    local obj = table.remove(self._available)
    if not obj then
        obj = self._template:Clone()
    end
    local lease = {} -- a fresh token per acquisition
    self._leases[obj] = lease
    return obj, lease
end

function Pool:release(obj: Instance, lease: any): boolean
    -- Only the live lease may return obj. A nil lease must NEVER validate:
    -- for an unowned object _leases[obj] is nil, so a nil lease would
    -- compare equal and admit a duplicate pool entry.
    if lease == nil then
        return false
    end
    if self._leases[obj] ~= lease then
        return false
    end
    self._leases[obj] = nil
    obj.Parent = nil
    -- Reset state here
    table.insert(self._available, obj)
    return true
end
```

Callers must hold the token from `get` and pass it back to `release`. Membership tracking alone is not enough: a delayed callback holding only the object reference can release it after it was re-acquired, double-booking it. The per-acquisition token rejects that stale release instead.

### Throttled Updates

Instead of updating every frame, batch expensive work at fixed intervals:

```luau
-- Instead of updating every frame, batch at fixed intervals
local TICK_RATE = 1/10 -- 10 updates per second
local accumulated = 0

RunService.Heartbeat:Connect(function(dt)
    accumulated += dt
    if accumulated < TICK_RATE then return end
    accumulated -= TICK_RATE

    -- Do expensive work here (runs 10x/sec, not 60x)
    updateAllNPCs()
end)
```

### Distance-Based Relevance Filtering

Skip expensive updates for distant entities; the discovery scan itself remains
O(n):

```luau
-- This reduces expensive updates after discovery; the scan itself remains O(n).
local ACTIVATION_RANGE = 100

local function getActiveEntities(playerPosition: Vector3): {Instance}
    local active = {}
    for _, entity in allEntities do
        if (entity.Position - playerPosition).Magnitude < ACTIVATION_RANGE then
            table.insert(active, entity)
        end
    end
    return active
end
```

For large populations or frequent queries, use a real spatial index such as a
grid or spatial hash. Choose its cell size from the query radius and movement
pattern; this linear filter is not spatial partitioning.

### Lazy Loading

```luau
-- Don't load everything at once
-- Stream content as player approaches
local loaded = {}

local function ensureLoaded(zoneName: string)
    if loaded[zoneName] then return end
    loaded[zoneName] = true

    local zone = ServerStorage.Zones:FindFirstChild(zoneName)
    if zone then
        zone:Clone().Parent = workspace.ActiveZones
    end
end
```

## 11. ValueBase objects

`StringValue`, `NumberValue`, `IntValue`, `BoolValue`, `ObjectValue`, and
`CFrameValue` are typed single-value containers parented in the DataModel.
The value lives in the `.Value` property; assigning it fires the object's
`Changed` signal with the new value (not the property name).

Prefer instance attributes (`SetAttribute`/`GetAttribute`) for small static
data on an instance. Reach for a ValueBase object for legacy compatibility
or when a shared, replicated container with its own `Changed` signal is the
point.

- `StringValue`: shared strings (game state, current minigame name).
  `.Value` accepts at most 200,000 characters; longer raises
  `String too long`.
- `CFrameValue`: rarely used; stores one CFrame. Attributes already store
  CFrames, so use it only when `Changed` signaling on a replicated
  container is the requirement.

```luau
-- Server: currentGame is a StringValue in workspace
currentGame.Value = "Lobby"

-- Client: statusLabel is a TextLabel
workspace.CurrentGame.Changed:Connect(function(newName: string)
    statusLabel.Text = newName
end)
```

## 12. Spreading work across frames

Field-measured lessons from several projects about time-sliced work. Profile your own worst frame before and after every change; a budget that lowers the total can leave the peak where it was.

### Start a budgeted worker deferred

If `Enqueue` starts its worker with `task.spawn`, the worker runs at once and finishes the first job before the caller enqueues the second, so a loop of enqueues produces one job per worker run and the per-frame budget never trips. Start the worker with `task.defer` so it wakes after the caller's loop and sees the whole batch. Spread per-object setup over frames the same way, biggest jobs first.

### Clamp dt in accumulating timers

A "still for N seconds" settle check that adds raw `dt` settled every body at once after one long setup frame. Clamp `dt` (for example to 0.1 s) in every timer that accumulates. When a MicroProfiler capture won't show which work landed in a long frame, wrap the callbacks with `os.clock()` and log the frame index. Heartbeat's `deltaTime` is the time since the previous frame, so the long frame shows up in the value the next frame receives.

### A start-up budget only sees time since its own resume

When start-up systems are paced by a per-frame budget (`task.wait()` once this frame's systems pass it), work that one system pushed with `task.delay(0, ...)` resumes before the pacer next frame and stacks on top of the next system unseen. Push loads that can wait clearly past start-up (for example `task.delay(1, ...)`).

### Make the overflow path cheap and the budget check inside the step

A limiter whose overflow path rebuilt and re-queried the remaining work every step was worse than no limit (310 ms frames). So was a time budget checked only between large steps. Take a fixed amount per step, keep the remainder of the query on the operation, and check the budget inside the step. That cut worst frames from 310 to 57 ms at the price of a slower overall operation.

### Total versus peak

Count limits per worker multiply: 5 workers at 250 items each is 1,250 items a frame. A loop with no yield, or a bulk swap or reparent done all at once, ignores any limit. If a shared time budget halves a system's total but barely moves its peak, look for one atomic step and spread that; in one case only spreading the swap cut the peak from 81 to 29 ms.

### A budget can hide an infinite loop

A worker whose end condition could never be met spent exactly its 2 ms budget every frame, forever, and looked "busy". Another looped forever because a broad-phase query said "overlaps" while the exact test said "miss". When a budgeted system sits at its cap while nothing changes, count completions: a backlog that does not shrink with 0 finished is a stuck loop. Give every operation a no-progress guard that ends it after N steps with no effect and warns.

### Sliced computations need stable inputs

Spreading a graph walk over frames is only safe if nothing it caches changes between slices. A sliced walk that trusted an "entry valid while its parts still have a Parent" cache reported 3x the real result, because another system hid and restored parts between frames. Pause the mutating system during the walk, and test the sliced result against the one-frame result on the same randomized inputs before trusting it.

### Invalidate caches narrowly

A cache cleared wholesale by a frequent event is effectively always cold. One cache reset on every chunk build cost about 43 µs per check instead of 3 µs warm (556 ms total, about 155 ms after invalidating only entries near the change). Invalidate narrowly, print hit, miss and evicted counts, and make sure a measured win did not come from an earlier warm-up that filled the cache. For weak-keyed caches of Instances, see `roblox-luau-core`: entries can vanish while the Instance still exists.

```luau
-- Illustrative: a deferred, time-budgeted queue with completion counts
-- and a no-progress guard. Each job does one bounded step per call and
-- returns "done", "progress" or "idle".
type Step = () -> "done" | "progress" | "idle"

local BUDGET_SECONDS = 0.002
local MAX_IDLE_STEPS = 600

local queue: { { step: Step, idle: number } } = {}
local running = false
local completed = 0

local function worker()
    while #queue > 0 do
        local frameStart = os.clock()
        while #queue > 0 and os.clock() - frameStart < BUDGET_SECONDS do
            local job = queue[1]
            local result = job.step()
            if result == "done" then
                table.remove(queue, 1)
                completed += 1
            elseif result == "idle" then
                job.idle += 1
                if job.idle >= MAX_IDLE_STEPS then
                    warn("job made no progress; dropping it")
                    table.remove(queue, 1)
                end
            else
                job.idle = 0
            end
        end
        task.wait()
    end
    running = false
end

local function enqueue(step: Step)
    table.insert(queue, { step = step, idle = 0 })
    if not running then
        running = true
        task.defer(worker) -- deferred: sees the caller's whole batch
    end
end

local function stats(): (number, number)
    return #queue, completed
end

return { enqueue = enqueue, stats = stats }
```

### Spatial grids keyed by Vector3

Luau hashes `Vector3` table keys by value, so a grid can key cells by a floored `Vector3` and read the 27 cells around a point. Replacing a pairwise distance loop this way took 656 lights from 19 ms to about 3 ms in one project. Check the new path against the old loop, with a tolerance for float32-stored properties such as `PointLight.Brightness`. Don't key a grid by `Vector2`: those keys hash by identity.

```luau
-- Illustrative: neighbour lookup in a uniform grid.
local CELL = 16

local cells: { [Vector3]: { Vector3 } } = {}

local function cellOf(position: Vector3): Vector3
    return Vector3.new(
        math.floor(position.X / CELL),
        math.floor(position.Y / CELL),
        math.floor(position.Z / CELL)
    )
end

local function insert(position: Vector3)
    local key = cellOf(position)
    local list = cells[key]
    if not list then
        list = {}
        cells[key] = list
    end
    table.insert(list, position)
end

local function near(position: Vector3, radius: number): { Vector3 }
    local found = {}
    local center = cellOf(position)
    for dx = -1, 1 do
        for dy = -1, 1 do
            for dz = -1, 1 do
                local list = cells[center + Vector3.new(dx, dy, dz)]
                if list then
                    for _, other in list do
                        if (other - position).Magnitude <= radius then
                            table.insert(found, other)
                        end
                    end
                end
            end
        end
    end
    return found
end

return { insert = insert, near = near }
```

The 27-cell read is correct only while `radius <= CELL`.

## Community ecosystem (leads, not sources)

Top-sorted DevForum canon for language patterns. These are the posts experienced scripters still cite.

- [All about OOP](https://devforum.roblox.com/t/all-about-object-oriented-programming/8585) (2.7k likes, 2014, still the reference); [metatables and metamethods](https://devforum.roblox.com/t/all-you-need-to-know-about-metatables-and-metamethods/503259).
- [Avoiding wait() and why](https://devforum.roblox.com/t/avoiding-wait-and-why/244015): origin of the `task.*` canon.
- [Pcalls: when and how](https://devforum.roblox.com/t/pcalls-when-and-how-to-use-them/393687) (658 likes); [Promises and why](https://devforum.roblox.com/t/promises-and-why-you-should-use-them/350825) for the Promise library.
- Framework design: [Writing an FPS framework](https://devforum.roblox.com/t/writing-an-fps-framework-2020/503318) (+ part 2), the most-cited architecture walkthrough; [Server Authority: How to Begin?](https://devforum.roblox.com/t/server-authority-how-to-begin/4139185) (2025).

## Prevent work creation during teardown

Mark an owner closing before destroying entities or releasing resources that can trigger callbacks. Gameplay, death, removal, and deferred handlers must distinguish normal play from teardown and must not register new work with a cleanup owner that is already cleaning. Inspect the actual cleanup library's reentrancy contract.

Test normal completion, forced teardown with live entities, last-player departure, and shutdown. Observe callbacks rather than assuming destruction produces a particular gameplay event. Keep cleanup idempotent and reject stale scheduled work after the owner has closed.
