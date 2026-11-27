# Roblox Performance: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Detailed performance targets, profiling guides, optimization patterns, and platform-specific guidance.

## Starting Performance Targets

These are investigation thresholds, not Roblox platform limits. Replace them
with measurements from representative devices and your experience's workload.

### Server
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| Heartbeat time | < 16ms (60Hz) | > 33ms (below 30Hz) |
| Script time | < 10ms/frame | > 20ms |
| Memory | stable baseline | sustained growth |
| Network out | measured baseline | congestion or latency |
| DataStore budget | query `GetRequestBudgetForRequestType()` | low budget per request type |

### Client
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| FPS (desktop) | 60 | < 30 |
| FPS (mobile) | 45 | < 30 |
| Memory | stable device-tier baseline | sustained growth or OS termination |
| Load time | < 10s to playable | > 20s |
| Input latency | < 100ms | > 200ms |

## Profiling Tools

### MicroProfiler (Ctrl+F6)
Per-frame breakdown of time spent in scripts, physics, rendering. The primary tool for finding what's actually slow.

- Server: View → MicroProfiler
- Client: Ctrl+F6 toggles the profiler; Ctrl+Alt+F6 opens its detailed timeline
- Look for: long bars in "Script" category, physics spikes, render thread stalls

Frame time converts to FPS by dividing 1,000 ms by frame time. These are the documented reference points (Roblox MicroProfiler docs):

| Average frame time | Frames per second |
|--------------------|-------------------|
| 33.33 ms | 30 FPS |
| 16.67 ms | 60 FPS |
| 8.33 ms | 120 FPS |
| 4.17 ms | 240 FPS |

A high average is not the only failure mode: the docs stress **consistent** frame times, so a 16 ms average hiding periodic 40 ms spikes still reads as stutter to a player. Read the per-frame bars, not just the average.

### Custom labels in the MicroProfiler

The MicroProfiler is far more useful when hot paths carry their own labels. The `debug` library provides [debug.profilebegin](https://create.roblox.com/docs/en-us/reference/engine/libraries/debug) (opens a custom MicroProfiler label), `debug.profileend` (closes the most recent one), and `debug.setmemorycategory` (names a thread's memory usage in the Developer Console). They are cheap but not free, so gate them behind a flag that defaults off and wrap the calls so enabling is a one-line change:

```luau
local PROFILING = false -- flip during performance sessions

local function begin(label: string)
    if PROFILING then debug.profilebegin(label) end
end
local function finish()
    if PROFILING then debug.profileend() end
end
```

Pair `begin`/`finish` around each measured region (per-system updates, expensive queries, serialization), and set a memory category per long-lived thread so memory grouped under one script separates in the console. Labels must be balanced: every `profilebegin` needs exactly one `profileend`, on the same thread.

### Developer Console (F9)
- **Stats**: Memory, network, render stats
- **Server Stats** (game owner): Server-side metrics
- **Script Performance**: Per-script CPU time

### Script Profiler (Ctrl+Alt+F5)
- Per-script CPU usage and heap allocations
- Identifies which scripts are hot

### MicroProfiler search and Assistant analysis (2026-11)

On the desktop client, the MicroProfiler **Detailed** view has a search box (Ctrl+F; F3/Enter next, Shift+F3 previous) that dims non-matching labels and highlights frames containing a match, which is the fastest way to find your own `debug.profilebegin` label in a long capture. Studio's Assistant, and agents connected through the Studio MCP server, can read a **paused** capture and report likely bottlenecks. Treat that report as a lead and confirm it with an A/B run. The full tag list lives in the LibMP `ALL-SCOPES` document linked from the MicroProfiler docs page. <!-- temporal: 2026-11 -->

### Server memory pressure: `DataModel.ServerLowMemoryWarning`

`DataModel.ServerLowMemoryWarning` fires on the server when Roblox detects memory pressure. The docs call it a best-effort chance to drop nonessential memory, say it can fire more than once while pressure lasts, and say it guarantees neither a shutdown nor its avoidance. Make the handler idempotent and cheap:

```luau
-- Illustrative: free caches you can rebuild; never allocate heavily here.
local caches: { [string]: { [any]: any } } = {}

game.ServerLowMemoryWarning:Connect(function()
    for _, cache in caches do
        table.clear(cache) -- idempotent: safe to run on every firing
    end
end)
```

If heartbeat stays low after optimization, the performance docs point to Extended Services for Compute for reserving more server CPU. <!-- temporal: 2026-11 -->

### Load (join) time

The docs give the join order: `ReplicatedFirst` (loading screen) replicates first, then the rest of the DataModel (all of `ReplicatedStorage`, and with streaming only the area near spawn), then the avatar loads. There is no built-in load-time tool; a stopwatch is enough for a baseline. Documented causes: streaming disabled, bulky `ReplicatedStorage` (free models add hidden bulk), heavy `ReplicatedFirst`, `ContentProvider:PreloadAsync` over large sets (preloading all of Workspace, or waiting on `RequestQueueSize`), and expensive startup LocalScripts. Preload only loading-screen images, key menu art and spawn-area assets, offer a Skip button for long preloads, and defer UI panels until first opened. An unexpected jump in load time can be an obfuscated free-model script generating thousands of instances.

### Graphics quality levels (2026-11)

The engine scales rendering quality per device; even at the lowest level, draw distance is at least 500 studs. Preview levels in Studio with Studio Settings → Rendering → **Editor Quality Level**. The docs now advise **against** changing visual effects from scripts based on `UserGameSettings.SavedQualityLevel`, because it fights the engine's automatic scaling. If you need your own budgets for debris, effects or physics (which the engine's scaling does not reduce), key them to measured frame time rather than the saved quality slider. <!-- temporal: 2026-11 -->

## Measuring correctly in Studio (field-measured)

These process lessons were measured across several projects. Numbers are examples, not targets.

- **Studio throttles an unfocused playtest client.** Measured cap: about 15 FPS (idle frame p50 near 66.7 ms), even when the window looks foregrounded. Total frame time from an unattended or agent-driven session is meaningless. Detect the cap from inside the game by counting simulation steps per drawn frame (about 4 when capped, about 1 when focused), void captures whose idle p50 is not near 16.7 ms, and compare per-action CPU instead: client-target Script Profiler, `Stats.RenderCPUFrameTime`, `SceneDrawcallCount`, `SceneTriangleCount`. Show the window-focus state and graphics level in any debug HUD. Don't steal window focus on someone else's machine without permission.
- **Studio solo mixes server and client in one process.** Before chasing a label, run a local server with one client (Test tab, or an MCP multiplayer playtest) and profile each process. In one run this showed server p99 18 ms against client p99 46-51 ms, which settled where to look.
- **The Studio playtest server can tick at about 20 Hz.** Per-frame costs measured there hold about three times the work of a 60 Hz live frame. Report per-second cost next to per-frame cost and re-measure on a live server before raising counts.
- **Studio require time is mostly compile time.** Live clients receive bytecode, so a large data module that took 234-518 ms in Studio took about 40 ms on phones, while a UI build was slower on phones than in Studio. Rank startup costs from live-device timings, section by section.
- **`Stats:GetTotalMemoryUsageMb()` in Studio includes the editor** (2+ GB). It says nothing about phones.
- **Check stat units on a live client before charting.** Measured: `Stats.RenderCPUFrameTime` and `RenderGPUFrameTime` read in seconds (0.0085 = 8.5 ms), while `PhysicsStepTimeMs` is milliseconds; `RenderGPUFrameTime` reads about 0 in Studio. The reference pages don't state the render units, so confirm before trusting a pipeline.
- **`Stats.PhysicsStepTimeMs` is smoothed.** After a burst it ramped from 2 to 43 over about 2.5 s while frames were already 100-120 ms. Time physics yourself from `RunService.PreSimulation` to `PostSimulation`. On the server it reads near 0 when the costly bodies are client-simulated, so log the client too.
- **Labels only see their own scopes.** To localize an unexplained stall, timestamp each frame stage (`PreRender`, `PreAnimation`, `PreSimulation`, `PostSimulation`, `Heartbeat`) and log `gcinfo()` and total memory beside frame time. A gap between stages with flat memory rules out Luau allocation; a one-frame jump of tens of MB points at script work. Set the timestamp before anything that can throw, read logs and probes before stopping the playtest, and keep logging past the trigger: the worst frame can come seconds later.
- **Split a big label before trusting a saving.** Ten verified "removed real work" fixes moved p99 only from 91 to 76 ms in one project. Measure sub-labels, and check that diagnostics (a per-frame debug scan) are not running inside a measured label.
- **A "last slow frame" label explains that frame, not a low average.** Fixing a 54 ms label changed nothing in an A/B because it was a single attach frame. If a tuning knob changes nothing about the worst frame across a whole sweep, the worst frame comes from elsewhere.
- **Keep harness work out of the measured window.** Screenshots, large instance scans and target-picking walks (one scan of about 450k parts made 250-320 ms server frames) read as feature cost. After marking a capture, wait a couple of Heartbeats on both peers before acting. Verify what a test actually hit; a ray can hit foliage instead of the wall you meant.
- **Benchmark in the reporter's state.** A fix that won on a fresh-map bench did nothing for the player who reported lag: their state (hundreds of settled debris pieces) cost 3x the bench. Eliminate causes with identical scripted input, one switch per variant, then confirm in the live session at the reporter's position. Per-item cost also rose under load (0.1 ms quiet vs 0.3-0.4 ms mid-event).
- **A/B the harness assumption before building a harder harness.** A server-driven bench cannot see client-only fixes (lazy work during a wind-up), so measure those through the real client path.
- **Time what the player sees.** For action latency, detect the visible result (for example a ray from the camera through the expected change every Heartbeat) instead of timing when the work ends. This exposed a newest-first queue serving the first request last. A per-frame ms budget also makes latency scale with frame time, so slow devices lose twice.
- **Studio has no real round trip.** Effects that wait for the server look instant in Studio and late on phones. `Player:GetNetworkPing()` returns round-trip time. Add per-leg timing (server reply, effect arriving, effect shown) and run network-dependent features once under a Studio network profile before calling them done.
- **For "clean up performance" requests, total each system's ms per frame across idle, action and heavy scenarios** on separate server and client. The biggest waste found was idle polling. Price a cache by switching it off: one warm-up spent 150-520 ms to save 15-100 ms. At 60 FPS, frame time minus labels is mostly vsync wait.
- **Engine-internal instances.** A running peer holds tens of thousands of instances in hidden services; a large `Stats.InstanceCount` jump with no visible arrivals can be engine work, not a missing root in your probe.

## Field-measured costs and patterns

Measured in Studio on PC unless noted; reproduce on your own target devices.

| Pattern | Measured | Practice |
|---------|----------|----------|
| Parent many new Parts one by one into Workspace | 1,657 Parts: 12.3 ms vs 0.6 ms into a detached Folder plus one attach | Build under an unparented Folder in time-budgeted slices (about 3 ms a frame), attach once, remove with one `Folder:Destroy()` |
| Per-frame work capped by count | 523 ms of work fell to 19 ms after a time cap plus a grid | Cap by elapsed `os.clock()` time (for example 4 ms), because each operation gets dearer as the world grows |
| `FindFirstChildWhichIsA`/`FindFirstChildOfClass` per Part in one big folder | 13k parts: 198 ms on that check alone | They scan children linearly. Memoise per parent within one loop; bench on realistic folder sizes |
| Property reads vs spatial queries | `part.Parent` ~0.10 us; Instance-keyed insert ~0.11 us; `GetPartBoundsInBox` 6-15 us | Engine calls dominate loops, and `--!native` won't help them. Cache facts an anchored part never changes in a weak-keyed table (about 40% cut once) |
| New Part vs pooled Part | ~37 us vs ~7 us | Pool hot spawns |
| Clone+parent under physics load | ~30 us quiet vs ~500 us with thousands of moving parts | Benchmark spawns under the feature's real physics load; avoid copying parts at the moment of a big physics event |
| Lazy acceleration structure | BVH raycast 0.13 ms warm, 2-13 ms building on first shot | Build indexes at load or bake time, not on first gameplay use |
| "All X as data" helper on lazy data | 1,415 ms and 68 MB requiring 1,601 modules; 1.4 ms filtering first | Filter before forcing lazy loads |
| Lazy load inside one action | Worst frame 87-96 ms down to 34-47 ms | Do lazy work during the action's wind-up on a per-frame budget. If a lazy load sits in a replicated handler, hold that and later events (keep order) until it finishes, with a cap that forces completion |
| Loop walks every item to find actionable ones | ~1.5 ms a frame on ~2,700 items that could never act | Keep a separate actionable set, updated where its condition changes. A recheck over an unchanged world can rest after a clean pass if every event that could change the answer wakes it |
| Destroy a 145k-part map in one call | 2.5 s frame; 2 s build slices froze the server 4-7 s | Destroy and build in ~30 ms slices with `task.wait()` between; drive the loading bar from real built progress (a replicated attribute) |
| Reset a data-built map | Full rebuild 8.8 s server / 12.9 s client; dirty-only 0.3 s | Find changed chunks before wiping state that tracks untouched originals; rebuild only those |
| Grid look via `Texture` on six faces vs `MaterialVariant` | 1,600 parts: 139 vs 25 draw calls, 31,981 vs 16,177 triangles | Use a greyscale `MaterialVariant` ColorMap tinted by `Part.Color`; build on a lattice matching the tile size so lines meet |
| Part memory | ~3.3 KB per Part regardless of collision flags | Turning off collision does not make a dense map cheaper; bake far chunks (see below) |
| Destroying runtime meshes on a large map | ~12.5k meshes from `CreateMeshPartAsync`: destroying 30 caused delayed (~16 s) stalls of 1-17 s; unparent-and-hold caused none (Studio solo) | On large runtime-mesh maps, retire baked meshes by unparenting and keeping a reference; profile destruction on a full-size map. When a stall comes after a delay with nothing in your labels, suspect engine background work |

**Runtime baking.** `AssetService:CreateDataModelContentAsync` can bake far chunks into cheaper meshes with the same look; one measured layout kept Parts within about 40-60 studs and baked meshes beyond. See `roblox-building` for the mesh APIs.

**Scriptless interactive props.** Many props need no script, connection or loop each. Keep their state as replicated data (a hit counter, a dead tag), let one server system at a fixed rate (for example 20 Hz) stand up what is due, and let one client system visit only props that are moving and move them in one `workspace:BulkMoveTo`. Measured with 18 targets: 1.4 microseconds per idle tick and 0.22% of server time under 20 shots a second.

**Dirty-mark systems for cosmetics.** For skins, paint or outfits on many models, change hooks only mark affected models (entity added, a late mesh arriving inside it, equipped item changed), and one scheduled system repaints only marked models. Route every model through one apply function that resets each part to its base first, then applies layers in order, so idle frames cost nothing and reskins start clean.

**Sum the budgets.** Separately reasonable per-system budgets can add up past the frame. Keep a table of every system's budget and its measured p99.

## What Luau actually charges for (hot-loop cost model)

The Scripts table above lists fixes; this section explains why they work so agents can generalize
instead of cargo-culting. Everything here traces to [luau.org/performance](https://luau.org/performance)
(the "How we make Luau fast" page) — ordering claims only; no absolute cycle counts are published.

**Imports, not locals, kill global reads.** The compiler resolves global chains like `math.max` at
*load time* ("imports") when the script's environment is pure, so `math.max(x, 1)` in a hot loop is
already a constant-index fetch. `local max = math.max` buys nothing here — the Luau docs call
caching method/library locals unproductive and discourage it. The habit that *does* matter:
mutable globals cannot use the same load-time import assumption; their accesses can still be inline-cached. Keep per-script mutable state in locals or module-locals for clear ownership.

**Environment impurity disables imports.** Calling `getfenv`, `setfenv`, or `loadstring` marks the affected environment *impure*, disabling import optimizations for functions using it
— even read-only `getfenv` use, per the docs. `roblox-luau-core` flags these as isolation hazards;
the performance reason to avoid them is that they deoptimize the whole module's global access and
also disable `--!optimize 2` inlining entirely. Avoiding them is not style; it is keeping the
compiler's optimizations armed.

**Lookup shape matters; there is no universal cost ladder.** Luau inline-caches constant-key field access (`t.field` and constant `t["field"]`) when table shapes are stable. Direct fields avoid metatable lookup. Method calls have their own optimizations; do not replace engine `object:Method()` calls with cached functions mechanically. Builtin fastcalls are a separate case: `string.byte(s)` can use a fastcall whereas `s:byte()` cannot. Measure the actual workload before turning these mechanisms into a speed ranking.

**Dead habits from Lua 5.1 training data:**
- Hoisting `#list` out of `for i = 1, #list` — the loop bound is evaluated *once* at loop entry; the
  hoist is noise. `#t` is also O(logN) worst case with cached length in Luau, not the Lua O(N) walk.
- Hand unrolling loops — the compiler unrolls compile-time-bounded loops (`for i = 1, 4`) under
  `--!optimize 2` with its own profitability heuristics, and inlines local functions the same way.
  Hand unrolling fights the compiler and hurts readability; revisit whenever the optimization level
  or build flags change.
- `local f = math.floor` at module top — pure folklore in a clean environment (see imports above).

**Allocation is a different cost axis, and the allocating frame is not the stalling frame.** Luau's
GC is incremental and runs "assists" interleaved with script execution; a high allocation rate in one
system shows up later as collector time attributed elsewhere, plus a periodic *atomic* step that can
pause on the order of tens of milliseconds when it must traverse large recently-mutated structures
(large weak tables and many active coroutines are the documented aggravators). So when the profiler
shows GC cost rather than your function, hunt the allocation source, not the frame with the spike:

```luau
-- Illustrative: the consumer may read these views only until the next update.
local results = {} -- retained across updates, not recreated every frame
local function updateViews(entities)
    for i, entity in entities do
        local view = results[i]
        if view == nil then
            view = {} -- allocate once per active slot, not once per frame
            results[i] = view
        end
        view.pos = entity.Position
        view.hp = entity.Health
    end
    for i = #entities + 1, #results do
        results[i] = nil -- discard inactive slots
    end
    return results
end
```

Every slot has its own table; assigning one scratch table to every slot aliases all rows. This example changes the ownership contract: consumers must not retain views as immutable historical snapshots.

The safety precondition for reuse (pools, scratch buffers, `table.clear`): nothing may retain the
recycled object past the iteration. `table.create(n)` preallocates storage for known-size arrays;
`table.clear` empties without freeing capacity. Closures and string concatenation are the other
allocation sources: Luau caches closures with only immutable upvalues, but a closure with a mutated
upvalue allocates per creation, and `s .. x` in a loop is a string object per iteration — use
`table.concat` (the Scripts table row).

**Measure, don't recite.** Every micro-optimization above costs readability. The MicroProfiler and
Script Profiler (this skill's primary tools) decide whether any of it applies; an unmeasured hoist is
cargo cult. For verifying that a change actually removed GC work rather than moving it, watch the
Developer Console memory graph across a fixed-duration stress play session, and compare the
MicroProfiler's GC/atomic bars before and after — not a single-frame snapshot.

## Parallel Luau mechanics: Actors, messages, SharedTable

Parallel Luau is a worker model, not a switch that makes an existing script faster. An `Actor`
provides an isolation boundary for scripts that can run concurrently. The useful shape is usually:

1. the serial coordinator gathers small, immutable inputs;
2. workers perform expensive math, visibility tests, or simulation calculations;
3. workers return raw results;
4. the coordinator synchronizes and applies Roblox instance changes.

Actors can run in different Luau VMs; do not rely on a one-Actor-to-one-VM mapping or on module-level state being shared across Actors. Communicate explicitly instead. Scripts under the same Actor execute sequentially relative to each other — parallelism comes
from multiple Actors. `require()` cannot be called inside a desynchronized parallel phase; require
modules in a serial context first.

**Thread-safety tiers.** API members carry thread-safety tags in the reference pages: `Unsafe`
(read/write or call forbidden in parallel — the default when untagged), `Read Parallel` (readable,
not writable), `Local Safe` (usable within the owning Actor only), `Safe`. Parallel code that touches
an Unsafe member is auto-detected and prevented by the engine. Before writing a parallel path, check
the tags of every member it touches; "usually it works" is not a design.

```luau
local bindable = script.Parent:WaitForChild("Work")

bindable.Event:ConnectParallel(function(input)
    local result = expensivePureCalculation(input)

    -- DataModel writes and other restricted operations belong back in serial.
    task.synchronize()
    script.Parent.Result.Value = result
end)
```

The code above is illustrative. Keep the parallel section free of instance writes unless the current
API explicitly permits the operation. Avoid moving a large mutable object graph between the
coordinator and workers. Actor setup, synchronization, and contention can cost more than the work
being offloaded.

**Actor messaging (`Actor:SendMessage` / `BindToMessage` / `BindToMessageParallel`).** Messaging is
asynchronous: the sender never blocks. `SendMessage(topic, ...)` targets exactly one Actor; that
Actor may have multiple callbacks bound to one topic. Only executing scripts that are *descendants of the Actor* can bind. A module required by such a script can run in its Actor context; the module's storage location alone does not determine the caller context. `BindToMessage`
invokes the callback in a serial context, `BindToMessageParallel` in a parallel one. Arguments are
**passed by copy across the VM boundary** (ordinary message values are transferred across execution contexts): large tables are fully
copied on every send, and functions cannot be sent at all because they belong to a specific VM. So
message payloads must be plain data, Instance references, or SharedTable handles.

**SharedTable: shared by reference, with atomics.** Sending a SharedTable through a message (or
sharing one via `SharedTableRegistry`) does not copy it — updates by one Actor are immediately
visible to all. Key/value restrictions (verified on the datatype page): keys must be strings or
non-negative integers < 2³²; values may be booleans, numbers, vectors, strings, serializable
datatypes, or nested SharedTables — **not Instances or functions** (both error on write). For
read-modify-write without a serial phase, use the atomic primitives:

```luau
-- Counter-style state: prefer increment — docs note it is much faster than update
local oldValue = SharedTable.increment(stats, "damageDealt", 1) -- errors if key missing/non-number

-- Compound read-modify-write: update may call f MORE THAN ONCE under contention;
-- f must be pure (no side effects, no captures you mutate), or retried runs double-apply.
SharedTable.update(stats, "bestLap", function(best)
    if lapTime < best then return lapTime end
    return best
end)

-- Read-then-write through the element syntax is NOT atomic; another actor's write interleaves:
local v = stats["x"]; stats["x"] = v .. ",x" -- the exact interleaving hazard the docs call out
```

**Snapshots: `clone` vs `cloneAndFreeze`.** A shallow `SharedTable.clone` is atomic and cheap
(structural sharing — nested SharedTables stay shared), so it yields a consistent snapshot of one
table even while others mutate it. A deep clone is **not** atomic as a whole: each nested table is
snapshotted at a different instant, so a concurrently-mutated graph can clone inconsistently.
`cloneAndFreeze` produces a read-only clone (writes error); frozen snapshots are the right way to
hand workers a stable view of config or level data. SharedTable writes are distinct from DataModel writes. Before touching instances, check each member's thread-safety tag; synchronize for restricted operations. SharedTable is a data channel, not permission to bypass engine thread-safety restrictions.

**When not to bother.** A message-per-frame pattern reintroduces the coordination cost you
parallelized to avoid; batch per tick. Prefer more, logically-cohesive Actors over few overloaded
ones (the docs recommend granularity for load balancing), but keep a unit of logic in one Actor.
The practical rule is unchanged: profile first, isolate a pure or read-heavy calculation, compare
against the serial version, and keep the parallel path only if the MicroProfiler shows a real win on
target hardware.

## Common Performance Issues

### Scripts

| Problem | Symptom | Fix |
|---------|---------|-----|
| Heartbeat loop over many instances | Server frame time spike | Event-driven or batch with yielding |
| Repeated workspace lookups | Unnecessary overhead | Cache references in variables |
| Table allocation in hot paths | GC pressure, frame spikes | Reuse preallocated tables |
| String concatenation in loops | O(n²) allocation | `table.concat()` |
| Signal over-subscription | Many listeners on one event | Batch or partition |
| Unthrottled RenderStepped | Client FPS drop | Only use for camera/input, throttle everything else |
| require() in loops | Repeated module resolution | Cache module reference outside loop |

### Memory

| Problem | Symptom | Fix |
|---------|---------|-----|
| Undisconnected events | Memory grows over time | Trove/Maid pattern, disconnect on cleanup |
| Orphaned instances | Memory never freed | Destroy() instances, nil references |
| Large tables never cleared | Lua GC can't collect | Set to nil or use weak tables |
| Excessive cloning | Memory spikes on spawn | Object pooling |
| Oversized images | High texture memory | Match resolution to on-screen size: at most 512x512 for large on-screen images, under 256x256 for minor ones, trim sheets for 3D reuse (docs) |

Source for the image sizing guidance: https://create.roblox.com/docs/en-us/performance-optimization/improve (trim sheets, resolution-vs-screen-size rule). Uploaded images are transcoded by the platform, so "use a compressed format" is not a lever you control: the lever is resolution and reuse.

#### Player/Character objects are NOT auto-destroyed

`PlayerRemoving` and `CharacterRemoving` fire, but the engine does not destroy the Player or Character instances. If you hold attributes, connections, or references on them, that memory stays on the server for the life of the process, a slow leak that grows with every join/leave and eventually crashes long-lived servers.

The pattern: disconnect/destroy each player's resources in those events, and destroy the instance when you are done with it. Defer the destroy (the removal event may still run cleanup) and wrap in `pcall` so cleanup can't error mid-list.

```luau
local Players = game:GetService("Players")

local function destroyDeferred(instance: Instance)
    task.defer(pcall, instance.Destroy, instance)
end

local function onCharacterRemoving(character: Model)
    -- disconnect character-owned connections, clear attributes
    destroyDeferred(character)
end

Players.PlayerAdded:Connect(function(player)
    player.CharacterRemoving:Connect(onCharacterRemoving)
end)

Players.PlayerRemoving:Connect(function(player)
    -- disconnect player-owned connections, clear attributes
    destroyDeferred(player)
    -- player is about to leave; no need to keep the object alive
end)
```

Notes:
- The same leak exists on the client (e.g. Player/character references from LocalScripts); clean up there too.
- `Workspace.PlayerCharacterDestroyBehavior` (`Default`, `Enabled`, `Disabled`; set in Studio, not by scripts): `Enabled` makes the engine call `Destroy()` on a player's old character when it is replaced (for example on respawn) and on the `Player` object when the player leaves. `Default` follows the engine's current default, which can change between releases, so set `Enabled` explicitly if you rely on it. Explicit cleanup of your own connections and tables is still needed and harmless. <!-- temporal: 2026-11 -->

### Rendering

| Problem | Symptom | Fix |
|---------|---------|-----|
| High draw calls | Low FPS when looking at dense areas | Reduce *unique* meshes and materials, not raw part count. The engine instances identical meshes with the same `MeshContent` and identical `SurfaceAppearance`/`TextureContent` (or material) into one draw call; decals, textures and particles batch poorly (performance docs, "Draw calls"). Field-measured in one project: about 20.8k anchored Parts drew in about 31 draw calls, while the same build converted to about 331 unique meshes took about 295. MeshParts are not an automatic fix; measure draw calls (Render Stats, Shift+F2) and frame time before and after any conversion |
| Transparent part stacking | Overdraw, GPU bound | Reduce layers, use CanvasGroup for UI |
| Excessive particles | Mobile FPS death | Cap ParticleEmitter.Rate, reduce on mobile |
| Too many dynamic lights | Frame time spike | Documented guidance is simply "use fewer dynamic lights"; the 4-6 per area figure is a practitioner heuristic, not an engine limit. Measure before enforcing |
| Post-processing stacking | GPU overhead | One BloomEffect, one ColorCorrection max |

### Network

| Problem | Symptom | Fix |
|---------|---------|-----|
| Frequent RemoteEvent fires | Bandwidth spike | Batch updates into one event per tick. The 10-20/sec throttle figure is a practitioner heuristic: pick the rate from measured bandwidth and gameplay tolerance, not a rule |
| Large payloads | Lag spike on fire | Send IDs not full objects, compress data |
| Replicating unnecessary instances | Join time slow | Keep Workspace lean, use ServerStorage |
| Unthrottled property changes | Network saturation | Batch property changes, use attributes |

### Replay / Delta State Recording

A replay system stores compact per-delta state changes rather than full frames: record only the authoritative fields that change each tick (CFrame, velocity, health, anim), delta/dict-encode against the prior frame, then compress (e.g. ZStd) and chunk the stream for storage. Store an integrity hash (e.g. HMAC-SHA256) so chunks can't be tampered with, and version the protocol so older replays stay decodeable as the format evolves. Reconstruction happens at playback on the client, keeping the stored footprint near the delta+compression size rather than raw per-frame snapshots. [Community lead: "ReplayCore" by lathienvu7, https://devforum.roblox.com/t/replaycore-a-modern-open-source-replay-system-for-roblox/4803450; label as practitioner design and verify specifics before adoption.]

## Optimization Patterns

Code-level micro-optimizations (object pooling, throttled updates,
distance-based relevance filtering, lazy loading) now live in
`roblox-luau-patterns` §10. Apply them only where the profiler shows cost.
The engine-side counterparts stay in this skill: StreamingEnabled tuning and
detect-platform guidance are under Mobile-Specific Optimization below.

## Mobile-Specific Optimization

Optimize for representative low-end mobile devices, not universal object caps:

- **Geometry**: Profile visible parts and triangles; use StreamingEnabled where appropriate.
- **Textures**: Match resolution to on-screen size and inspect texture memory.
- **Particles**: Measure active particle cost and reduce rate/lifetime on constrained devices.
- **UI**: Profile hierarchy and `CanvasGroup` use; CanvasGroup itself has rendering cost.
- **Shadows**: Profile lighting and shadow settings on each target tier.
- **Streaming**: Tune radii in Studio against pop-in, memory, and bandwidth.

### StreamingEnabled

StreamingEnabled is **on by default** for new places. Scoping is container-based: streaming applies exclusively to descendants of `Workspace`. Instances in `ReplicatedStorage`, `ReplicatedFirst`, etc. never stream.

With `ModelStreamingBehavior = Improved` (recommended), a Model streams in only when one of its BasePart descendants is eligible, and the model's non-BasePart descendants (Folders, Scripts, ValueObjects) stream in alongside it. A Model with no BasePart descendants replicates at join and is exempt from streaming out. In Legacy mode (default), non-BasePart descendants replicate at join and only BaseParts stream in/out.

When instances stream out, they are **parented to nil** (not destroyed). Luau references persist if they stream back in. Removal signals fire, but local-only property changes may be lost.

Configuration:
- `StreamingTargetRadius`: maximum target distance; Studio default is 1024 studs.
- `StreamingMinRadius`: highest-priority radius; Studio default is 64 studs.
- `StreamingIntegrityMode`: behavior when a player enters an incompletely streamed region.

Game scripts can't set these: they carry the `PluginOrOpenCloud` capability, so only Studio, plugins, and Open Cloud Luau execution sessions can change them. Tune them in Studio from measurements on
representative devices; do not assume a smaller radius is automatically better. <!-- temporal: 2026-11 -->

**Gotcha**: `workspace:FindFirstChild("DistantPart")` returns nil if the part is streamed out. Use `WaitForChild` with timeout, or design systems that don't depend on distant parts existing on the client.

**Remotes and streamed instances.** A remote signal and the instance it references travel independently: the signal can arrive before the instance, or the instance may never stream in, and an instance path sent as a string has the same problem. Address world objects by a stable id (attribute or number) and resolve it on arrival with a nil check, pre-fetch with `Player:RequestStreamAroundAsync()` on the server before firing, or skip the work for clients that lack the instance.

**Client copies.** Locally cloning a server instance into Workspace makes a client-only copy that no longer gets property updates; locally reparenting from `ReplicatedStorage` into Workspace can make it eligible to stream out; a client `Destroy()` of a server object only removes it locally, and it streams back with its original state. Client physics, including server-authority prediction, runs only in streamed areas, even for locally created instances; add a replication focus near anything that must keep simulating.

### Predictive Streaming (2026-07)

`Workspace.PredictiveStreamingMode` is set in Studio (or from a plugin or Open Cloud Luau execution, per its `PluginOrOpenCloud` capability); runtime game scripts can't change it. `Default` currently behaves like `Disabled`; `Enabled` lets the engine prefetch likely destinations for streaming-enabled experiences.

Spawn prefetching creates small temporary streaming foci at possible respawn locations after a player dies. CFrame return optimization keeps the area a player just left streamed in for a likely near-term return. Predictions are additive and temporary, so remeasure memory and bandwidth on representative devices. Predictive streaming leaves your own `RequestStreamAroundAsync` pre-fetches and `AddReplicationFocus` foci in place. Watch the effect in the **Network Stats** overlay (Shift+F3 live, Shift+Ctrl+F3 in a Studio playtest).

### Frustum streaming (2026-10)

`Player.FrustumStreaming` (`Enum.FrustumStreamingMode`: `Default` = `Disabled`, `Disabled`, `Automatic`, `Enabled`) adds the player's camera frustum to the streamed area, beyond the normal radius, for scopes, racing and free cameras. It is per player and **server-only**: a client that needs it fires a remote, and the server validates the request and sets the property. `Automatic` turns it on for a narrow field of view, high speed while looking where you move, or a camera far from the replication focus, after a short activation delay; set `Enabled` during an equip animation if the scope must be ready when it opens. It is additive (radius, frustum and replication foci are unioned), so it raises memory and possibly CPU, and normal quotas still apply. Stream-out: with `Opportunistic`, content that leaves the view and lies outside the radius and foci lingers 1.5 s; with `LowMemory`, it stays until memory runs low. <!-- temporal: 2026-11 -->

```luau
-- Illustrative server Script: scope requests from the client.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local scopeEvent = ReplicatedStorage:WaitForChild("ScopeEvent") :: RemoteEvent

Players.PlayerAdded:Connect(function(player)
    player.FrustumStreaming = Enum.FrustumStreamingMode.Automatic
end)

scopeEvent.OnServerEvent:Connect(function(player, wantsScope)
    if typeof(wantsScope) ~= "boolean" then
        return
    end
    -- Also check that the player actually has a scoped weapon equipped.
    player.FrustumStreaming = if wantsScope
        then Enum.FrustumStreamingMode.Enabled
        else Enum.FrustumStreamingMode.Automatic
end)
```

### SLIM level of detail (2026-11)

SLIM (Scalable Lightweight Interactive Models) cloud-transcodes models into composite meshes with multiple detail levels, so distant and streamed-out models stay visible with fewer draw calls, triangles and memory. Requirements: `StreamingEnabled`, a place **saved to Roblox** (not a local file), and Team Create on. Set `Model.LevelOfDetail = Enum.ModelLevelOfDetail.SLIM` on models of **static** parts and meshes; runtime-modified or animated models, and models containing a `Humanoid`, are not supported. `Workspace.EnableSLIMAvatars` (set in Properties; not scriptable) renders standard or advanced R15 player avatars as animated SLIM stand-ins and can swap them even inside the streaming radius; R6 avatars and NPCs are excluded, and avatars must be transcoded once before they show (rejoin after a minute or two). Debug with the Developer Console's DebugVisualizations → `SlimTintMode` (`LOD`, `DataModelState`; Studio also has `TranscoderStatus`). Known issues from the docs: unions can render wrong in SLIM (split them into their own model), coplanar faces z-fight (move them 0.01 studs apart), and UVs are regenerated so default-material tiling can shift. Studio's AI skill `rbx-convert-to-streaming` can convert a non-streaming game, including setting SLIM; back up the place first. <!-- temporal: 2026-11 -->

### Transparent batching of web-backed calls

Some web-backed APIs batch concurrent calls into fewer HTTP requests automatically. Per the scripting docs, these currently include `MarketplaceService:GetProductInfoAsync` (Product, GamePass and Bundle info types), `MarketplaceService:UserOwnsGamePassAsync`, `AvatarEditorService:GetItemDetailsAsync` and `AssetService:GetBundleDetailsAsync`. Batching only happens when calls start close together, so start them concurrently with `task.spawn` (each in `pcall`) instead of awaiting one at a time, and don't hand-roll batching on top. <!-- temporal: 2026-11 -->

### Detect Platform

```luau
local UserInputService = game:GetService("UserInputService")

local isMobile = UserInputService.TouchEnabled
    and not UserInputService.KeyboardEnabled

if isMobile then
    -- StreamingEnabled is set in Studio (ReadOnly from scripts).
    -- Reduce particle counts, disable expensive effects
end
```

## Performance Budget Template

Illustrative allocation for a 60 FPS target. Replace every number with measured
project budgets before enforcing it:

```
SERVER BUDGET (per Heartbeat frame, 16ms total):
  Physics:     4ms
  Scripts:     8ms
  Replication: 2ms
  Overhead:    2ms

CLIENT BUDGET (per render frame, 16ms for 60fps):
  Render:      8ms
  Scripts:     4ms
  Physics:     2ms
  UI:          1ms
  Overhead:    1ms

MEMORY BUDGET:
  Set per tested device tier; watch sustained growth and OS termination.

NETWORK BUDGET:
  Set from measured gameplay traffic and latency; rate-limit per action semantics.
```

## Community ecosystem (leads, not sources)

- [Connections can memory leak Instances](https://devforum.roblox.com/t/psa-connections-can-memory-leak-instances/90082): the RBXScriptSignal leak PSA every reviewer cites; [GC and memory leaks](https://devforum.roblox.com/t/garbage-collection-and-memory-leaks-in-roblox-what-you-should-know/374954).
- [How to actually improve performance](https://devforum.roblox.com/t/improved-how-to-actually-improve-performance-in-your-games/1221842) (measure-first canon); [6000+ FPS game](https://devforum.roblox.com/t/creating-the-most-optimized-roblox-game-runs-at-6000-fps/1736424) extreme case.
- [Luau Bytecode EXPLAINED](https://devforum.roblox.com/t/luau-bytecode-explained-how-to-read-debug-and-optimize-like-a-hacker/3941941) (2025) and [Illegal Luau optimizations](https://devforum.roblox.com/t/%E2%96%A8-how-2-make-roblox-engineers-cry-illegal-luau-optimizations-and-how-to-use-them/4128934) (2025): compiler-level perf literacy.
- [Dynamic culling system](https://devforum.roblox.com/t/advanced-modular-dynamic-culling-system/4322958) (2026); [DistanceFade](https://devforum.roblox.com/t/distancefade-a-transparency-falloff-effect-for-your-games/3136828); [greedy meshing](https://devforum.roblox.com/t/consume-everything-how-greedy-meshing-works/452717).
