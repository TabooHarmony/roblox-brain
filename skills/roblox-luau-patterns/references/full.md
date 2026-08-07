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

This reduces exposure to partial state and unnecessary change observation. It does not solve an abstract “replication race.” Some operations require ancestry or a specific parent. Parent earlier when the API contract requires it, then make partial visibility explicit.

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

## 7. Fallible calls without semantic collapse

`pcall` returns a transport/execution success flag followed by the function's results. A successful function may legitimately return `nil`.

```luau
local ok, value = pcall(dataStore.GetAsync, dataStore, key)
if not ok then
    return nil, `read failed: {value}`
end
return value, nil
```

Do not write a retry helper that returns only `T?`; it collapses “successful missing value” and “all attempts failed.” Preserve a result shape or separate error value.

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
- Retried operations are safe to repeat or idempotent.
- Partial instance visibility is intentional.
- No new manager class, framework, or dependency exists only to namespace one feature.
- Security, persistence, purchases, networking, and performance are handed to their canonical skills.
