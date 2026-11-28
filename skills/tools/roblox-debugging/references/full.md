# Roblox Debugging: Full Reference

> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

This is a method for finding and fixing bugs in Roblox games, for people and for coding agents. Tool mechanics for Studio MCP bridges are in `roblox-studio-mcp`; when someone else's Studio is involved, follow `roblox-collaboration-mode` before touching it. Roblox's own `rbx-debug`, `rbx-perf-profiling` and `rbx-network-simulator` skills (in Studio's Assistant and the official MCP server) cover the current tool procedures; load them when available.

## 1. The loop

1. **Check you are looking at the right thing.** Right place, right Studio window, right version, current code.
2. **Reproduce.** Write down the exact steps, device, input type, player count, server type and the state the player was in.
3. **Read the code path** that runs for those steps and list candidate causes, most likely first.
4. **Isolate.** Cut the search space in half each time: client or server, one player or several, Studio or live, fresh state or a long session.
5. **Observe** with the cheapest tool that answers the question (logs, a logpoint, a breakpoint, a profiler).
6. **Fix one cause.** Change as little as possible.
7. **Verify** on the same steps, by looking, on the real client path, and with two clients if anything is shared.
8. **Report** what changed, how it was verified, and what wasn't.

Skipping step 1 or step 7 is where most wasted time comes from.

## 2. Before anything: right place, right build

Many "the fix didn't work" reports are not bugs in the fix.

- **Wrong place.** Multi-place games (lobby, match, tutorial) and several open Studio windows make it easy to test or edit the wrong one. Confirm the place name or id before editing or testing, and on MCP bridges pass the target id on every call (`roblox-studio-mcp`).
- **Stale code.** Check the running code is the code you changed:
  - Rojo or Script Sync not connected, or connected to a different project.
  - A playtest started before the sync landed.
  - In edit mode, Studio caches `require` results for the session, so a builder that requires a re-synced module gets the old table; `require(module:Clone())` returns the new one (measured in one project).
  - A published live server still runs the old version until servers restart or migrate.
- **Leftover debug state.** Admin modes, forced roles, slowed time, frozen cameras, network simulation and device simulation all change behavior. Record what you turned on and remove it before judging.
- **Stale processes.** Leftover Studio windows from an earlier local-server test kept simulating and skewed a performance capture unnoticed in one project. List running Studio processes before measuring.

A quick way to prove freshness: add a one-line version marker (a constant printed at startup, or an attribute set by the new code) and check it in the session you test.

```luau
-- ModuleScript: bump BUILD_TAG when you change the module, then look for it in Output.
local BUILD_TAG = "inventory-fix-3"
print(`[Inventory] loaded {BUILD_TAG}`)
workspace:SetAttribute("InventoryBuild", BUILD_TAG)
```

## 3. Reproduce

- Capture the **real state**, not a fresh one. A change that moved weapon cooldowns broke refire only after a weapon was stowed and drawn again; tests that started fresh never hit it (observed in one project). Script the real sequence a player goes through.
- Note the **input type and device**: touch, gamepad and mouse take different paths, and phones run slower (`roblox-input`, `roblox-gui`).
- Note **who and how many**: a bug that needs a second player, a late joiner or a teleport won't appear solo. In one project a late joiner added about 20 seconds into a session was the closest Studio case to a live join.
- Note **where**: Studio, a published test place, or live. Studio playtests run the client and server on one machine with near-zero latency.
- If you can't reproduce it, don't guess a fix. Add targeted logging around the suspect path, ship it, and read it after the bug happens again.

## 4. Read before you run

Reading the code is often faster than any playtest.

- Trace the exact path: input → client handler → remote → server validation → state change → replication → client display.
- List candidate causes and what each predicts. Pick the observation that tells them apart.
- **Feel bugs** (floaty debris, jitter, things that "plop") are usually found by reading. In one project about 15 scripted playtests failed to reproduce a hand-feel bug, while reading the support logic found the cause in minutes (edge and corner contacts counted as support). Playtest only to answer a question the code can't.
- When the owner already says a system feels weak, build the fix rather than gathering evidence of how weak it is.

## 5. Isolate

| Question | How to split it |
| :-- | :-- |
| Client or server? | Read both Output streams (Studio shows server and client output; the Developer Console has separate Client and Server logs). Check whether the server state is right and only the display is wrong, or the reverse. |
| One player or several? | Repeat with two clients (Server & Clients mode, or an MCP multiplayer playtest). Replication, ownership and remotes only show up there. |
| Studio or live? | Studio has no real latency; add it with the Network Simulator (section 8). Check live with the Developer Console and Error Report (section 9). |
| Fresh or long session? | Some bugs need time (a leak, a counter overflow, state after a round). Keep a passive logger running for the whole session. |
| This change or older? | Toggle the change behind a flag (section 7) and compare in the same session. |
| Content or code? | Swap in a known-good asset or a plain part; asset privacy can make textures and meshes blank (`roblox-studio-mcp`). |

## 6. Observe: tools and when to use them

### Output, Developer Console and log files

- **Output** shows prints, warnings and errors from Studio, playtests and plugins; filter it to the context you need.
- **Developer Console** (F9, or `/console` in chat) works in playtests and live servers: client and server logs, memory, network and more. Use it on a phone or a live server where Studio isn't attached.
- **Log files** are on disk; on Windows under `%LOCALAPPDATA%\Roblox\logs`. Studio's own logs showed `Script timeout` during a "crash" in one project, which pointed at a stalled single-process solo playtest rather than a bug in the feature.
- **Command Bar** runs Luau in the current context, including during a running game.

### Structured logging with Logger

<!-- temporal: 2026-11 --> `LogService:GetLogger(name)` returns a named `Logger`, and `Logger:GetLogger(name)` makes nested ones (`Combat.Damage`). `Info`, `Warn`, `Error`, `Output` and `Log` take a message with `{key}` placeholders plus a context table. Messages go to Output, the Developer Console and `LogService.MessageOut`, tagged with the logger's full path, and appear in `GetLogHistory`. A logger's `MessageOut` fires on it and every ancestor, so one listener on `Combat` sees all combat logs.

```luau
local LogService = game:GetService("LogService")

local combatLog = LogService:GetLogger("Combat")
local damageLog = combatLog:GetLogger("Damage")

local function applyDamage(attacker: Player, target: Model, amount: number)
	damageLog:Info("{attacker} hit {target} for {amount}", {
		attacker = attacker.Name,
		target = target.Name,
		amount = amount,
	})
end

return applyDamage
```

- Keep a reference to each logger; once all references are released it is reclaimed and calling it errors. The number of live loggers and the path length are bounded.
- `LogService:Error` logs and then throws a structured error table (`message`, `template`, `context`, `stack`); catch it with `pcall`.
- `GetLogHistory` returns recent entries; `GetLogHistoryAsync` reads another participant's or the server's history during a Team Test, up to 512 entries.
- The docs warn that logger events and message contents can be unreliable or truncated: **never drive game logic from logs**. They are for people and tools.

### Print discipline

- Print **summary lines**, not floods: one line per phase or every few seconds, with a stable prefix you can filter on. Pulling every per-second line from one 80-second run cost more agent context than the rest of a multi-run sweep in one project.
- Log the inputs that decide a branch, not only "got here".
- Log `os.clock()` around anything you time, including screenshots: a capture stalled one playtest about 0.4 s and landed seconds after the code that posed the camera, so it read like a feature stall.
- Remove or gate noisy logs before shipping; leave cheap threshold logs (for example "frame over 50 ms in X") in suspect paths.

### Breakpoints and the Script Debugger

- **Standard breakpoints** pause a script at a line; inspect the **Watch** window (variables in scope, plus your own expressions under **My Watches**), the **Call Stack** and Output, then **Step Into**, **Step Over** or **Step Out**.
- **Conditional breakpoints** pause only when an expression is true (`hp <= 0`); use them inside loops and hot paths.
- **Logpoints** log a message without pausing (a red diamond). They are the cleanest "did this run, and with what?" check, and they don't need a code change.
- Each breakpoint has a **context**: Client, Server or Edit (plugins). A breakpoint set only for the server never fires in a LocalScript's path. Check the context first when a breakpoint "doesn't hit".
- Disable rather than delete breakpoints you will need again; deleting loses the condition and log message.
- Pausing a server in a multiplayer test freezes every client's view of it; prefer logpoints there.

### Isolating with the smallest unit

Test the smallest unit that answers the question. Call the module function live with a placed stand-in target instead of playing a whole match to reach a state; every playtest costs time. To confirm an edit landed, read back the script source in the edit DataModel rather than starting a playtest.

When scripting repeated test hits on a destructible target, aim each strike at a random point across its face and count only strikes whose ray actually hit the target. A fixed ray from a fixed position goes through the first hole and hits whatever is behind (one test logged 1 hit in 40 s).

## 7. Compare changes in one session

To A/B a change without restarting, put it behind a flag both peers read, and flip it between runs.

```luau
-- Shared ModuleScript: a debug flag both client and server read.
-- The server sets the attribute; the client follows it. Illustrative.
local RunService = game:GetService("RunService")

local Flags = { NewKnockback = false }

if RunService:IsClient() then
	local function sync()
		Flags.NewKnockback = workspace:GetAttribute("Flag_NewKnockback") == true
	end
	workspace:GetAttributeChangedSignal("Flag_NewKnockback"):Connect(sync)
	sync()
else
	Flags.NewKnockback = workspace:GetAttribute("Flag_NewKnockback") == true
	workspace:GetAttributeChangedSignal("Flag_NewKnockback"):Connect(function()
		Flags.NewKnockback = workspace:GetAttribute("Flag_NewKnockback") == true
	end)
end

return Flags
```

- Run off, on, off, on, and save each run's result as it ends; re-arming a probe wiped earlier runs in one project.
- Wrap a module's public functions at runtime (from a server or client evaluation) to time them without a restart.
- For live experiments use Roblox's config and experiment tools instead (`rbx-configs-experimentation`, `roblox-analytics`).

## 8. Performance bugs

Measure; don't guess. Full method in `roblox-performance` and Roblox's `rbx-perf-profiling` skill.

- **Script Profiler** (in the Developer Console) records CPU time of running scripts on the Client (default) or Server, at 1 kHz (default) or 10 kHz, for 1, 5 or 10 minutes or manually. It only records functions that use CPU; threads that sleep or wait don't show. Use it for "which script is expensive".
- **MicroProfiler** shows timing for every engine task in each frame. Press **Ctrl+Alt+F6** (⌘⌥F6) to open it and **Ctrl+P** (⌘P) to pause into detailed mode; **Ctrl+Shift+F5** shows the Performance Summary. Bars of similar height mean a cost every frame; occasional tall bars mean spikes. Label your own code with `debug.profilebegin("Name")` and `debug.profileend()` so it shows up by name.
- **Capture windows are short.** In one project an MCP MicroProfiler capture held only about 12 frames (about 0.75 s) in a busy session. Schedule the repro with `task.delay`, take the capture as the very next call, and check which frames it caught. A capture also stalled the game when it finished, so don't take percentiles from a session that includes one.
- **Re-running a repro on an area already affected is not a repro.** Reset the state between runs.
- **Boot noise.** Client timings within about 20 s of joining included the client's own startup (16.7 s vs 0.35 s once settled, in one project). Wait for boot to settle before timing.
- **Network Simulator** (beta) adds inbound and outbound latency, jitter and packet loss to playtests; presets include Ideal Fiber (the default adds 8 ms each way, so zero every field for a true baseline). Use it for rubber-banding, desync and "only laggy players see it" bugs. Zero it before handing Studio back; values carried into the next playtest in one project.
- **Passive logger in a long session.** When you can't take focus on someone's machine, a small client logger that prints one line every few seconds (frame-time percentiles, slow-frame gaps, draw calls) runs for the whole session without touching input. A lag source that appears only after 20 minutes can't be cleared by a log from the first minute.

```luau
-- LocalScript: prints frame-time percentiles every 5 s. Illustrative.
local RunService = game:GetService("RunService")

local samples: { number } = {}
local lastReport = os.clock()

RunService.Heartbeat:Connect(function(dt: number)
	table.insert(samples, dt * 1000)
	local now = os.clock()
	if now - lastReport < 5 or #samples < 10 then
		return
	end
	lastReport = now
	table.sort(samples)
	local function pct(p: number): number
		return samples[math.max(1, math.floor(#samples * p))]
	end
	print(string.format("[FrameLog] p50=%.1fms p95=%.1fms max=%.1fms n=%d", pct(0.5), pct(0.95), samples[#samples], #samples))
	table.clear(samples)
end)
```

- **Solo Play is one process.** Edit, server and client share one process in a solo playtest, so heavy server work can stall everything. Test heavy server work in a multiplayer playtest, which splits server and client like live.

## 9. Bugs that only happen live

- **Error Report.** Creator Dashboard > your game > **Monitoring > Error Report** shows near-real-time Luau errors and warnings for server and client, with filters for date range, place, severity, platform, OS, and "new errors since" a version, plus version annotations on the chart. Check it before and after every update (`roblox-publish-checklist`).
- **Error Reporting Open Cloud API.** <!-- temporal: 2026-11 --> With an API key scoped `universe.analytics:read` (and `:write` for rules), you can fetch error details (message, stack trace, severity, client or server, platform, first-seen version) by message hash. Get hashes from the `ErrorCount` metric broken down by `MessageHash`. Rules (regular expressions) group or ignore noisy messages, and Roblox suggests some you can dismiss. Each endpoint allows 60 requests per minute per key (`roblox-cloud`).
- **Developer Console on a live server** (F9) shows server logs to people with permission.
- **Live-only differences:** real latency, real devices, streaming, many players, long sessions, published asset permissions, and other servers (MessagingService, MemoryStore). Reproduce each in Studio where possible (Network Simulator, Device Simulator, multi-client tests) before changing code.
- **Teleports.** Studio playtest automation can follow teleports to other places in the same experience and read the destination server's output (`roblox-studio-mcp`).

## 10. Fix

- Fix the cause you proved, not every candidate.
- Keep the change small enough to explain in one sentence.
- If the fix touches a shared path, list everything else on that path and check it: one sound change asked for one weapon also changed every approved blast in one project, and only reading the diff against the roster showed it.
- Don't leave diagnostic flags, forced states or extra logging on by accident.

## 11. Verify

A fix isn't done until it's seen working.

- **Same steps, same state.** Re-run the exact reproduction, including the real player state that triggered it.
- **Look at it.** For anything visual or felt, look at the result in the game. A log line saying a function ran is not proof that the player sees the right thing.
- **Real client path.** Tests that skip the client fire path can pass while one runtime error breaks the game: in one project a nil index early in a client action meant every shot that hit the map was never sent to the server and lost its sound and effects, while server-side tests passed. Run one action of each affected kind through the real client and read the client error log grouped by message.
- **Two clients for anything shared:** replication, remotes, ownership, private UI, chat. Note each client's own player identity next to each observation.
- **Each input type** the bug or fix touches (touch, gamepad, mouse), and the smallest phone for UI.
- **Separate kinds of evidence.** Layout inspection, a direct handler call, simulated input and real hardware input prove different things. A handler call doesn't test hit testing; a misplaced simulated tap doesn't prove a broken button.
- **Captures can lie.** Screenshots miss short effects, some world UI and core UI, and come back black or stale when Studio isn't rendering (`roblox-studio-mcp`). Check state too before reporting something missing.

## 12. Report honestly

- Say what was verified, how, and in which context (solo or multiplayer, device, input).
- Say what wasn't verified and why (no second client, display off, no device).
- Never write "fixed" from intention, from code review alone, or from a test that couldn't have shown the bug.
- Include the evidence: the log lines, the before and after, the reproduction steps.

## 13. Common pains

| Symptom | Usual cause | Check |
| :-- | :-- | :-- |
| "Fixed it, still broken" | Wrong place, stale build, cached require, old live servers | Version marker (section 2) |
| Works solo, breaks with friends | Replication, ownership, a client-only assumption | Two-client test |
| Works in Studio, breaks live | Latency, devices, streaming, permissions | Network and Device Simulator, Error Report |
| Breakpoint never hits | Wrong context (Client/Server/Edit), code not running, stale build | Logpoint first, check context |
| Bug only after a while | Leak, state carried across rounds, counters | Passive logger across the session |
| Lag "sometimes" | Spikes, not steady cost | MicroProfiler, look for tall bars |
| Agent says "can't reproduce" after many runs | Scripted scenario that can never show the bug | Read the code path first |
| Numbers look wrong in a shared Studio | Someone else is playing in the same session | Look for input you didn't send (`roblox-collaboration-mode`) |

## 14. When Studio itself misbehaves

These were reported on the DevForum and may be fixed by now; treat them as things to try, not engine facts.

- **"Failed to fetch place info"** when opening or creating places (reported from 2026-09-04): users reported that logging out of Studio, ending it in Task Manager and logging back in worked for some (https://devforum.roblox.com/t/we-could-not-open-the-place-95206881-failed-to-fetch-place-info/4850252).
- **MCP reports Studio unreachable after an update:** Roblox staff said a restart (once, sometimes twice) cleared a one-time issue tied to a June 2026 Studio update (https://devforum.roblox.com/t/assistant-updates-multiple-chats-and-chat-history/4668130).
- **Transform handles stopped appearing** (2026-10-11): one user fixed it by reinstalling Studio from a fresh installer (https://devforum.roblox.com/t/tool-handles-no-longer-appear/4926020).
- **Team Create "the server has shut down"** (2026-06-26): users suggested clearing the cache and restoring a recent version from version history; back up before trying recovery (https://devforum.roblox.com/t/team-create-the-server-has-shut-down/4702235).

## 15. Checklist

- [ ] Right place, version and fresh code confirmed.
- [ ] Reproduction steps written, with device, input, players and state.
- [ ] Code path read and candidate causes listed.
- [ ] Client vs server and solo vs multiplayer split done.
- [ ] Cause proved with a log, logpoint, breakpoint or profile.
- [ ] One cause fixed; shared-path neighbours checked.
- [ ] Verified by looking, on the real client path, with two clients where shared.
- [ ] Debug state removed; Studio handed back clean.
- [ ] Report says what was and wasn't verified.
