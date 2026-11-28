# Roblox Testing: Full Reference

How to make Roblox code testable, and how to run tests at each layer: pure Luau outside Studio, the native engine test framework inside a playtest, multi-client playtests, and CI. Engine facts were checked against the Roblox creator docs on 2026-11-27. Workflow advice marked "observed" comes from real projects and isn't documented engine behavior. All code is illustrative: adapt names and paths to your project.

Related skills: `roblox-tooling` (Rojo, Lune, Wally, CI setup), `roblox-studio-mcp` (driving Studio), `roblox-networking` (what to test at the remote boundary), `roblox-data` (save tests), `roblox-publish-checklist` (release gates), `roblox-cloud` (Open Cloud keys).

## 1. Pick the layer

| Layer | Runs where | Good for | Can't see |
|---|---|---|---|
| Pure Luau (Lune, Jest Lua in a runner) | Your machine, CI | Rules, math, economy, parsers, state machines, encoders | Engine services, replication, physics |
| Native engine tests (`TestService`) | Studio playtest (Play, Play Here, Run) or a Team Test server | Code that needs the real DataModel, physics, and scripts | Live servers, other clients' screens |
| Multi-client playtest (`StudioTestService`, Server & Clients) | Studio, up to 8 simulated clients | Join/leave, lobbies, matchmaking, replication, remotes | Real devices, real latency (unless simulated) |
| Open Cloud Luau Execution | A Roblox server for a published place version | CI checks against the real engine without Studio | Running server or local scripts, physics |
| Two real accounts | Live dev universe | Final multiplayer claims, purchases, teleports | Nothing hidden, but it's slow and manual |

Push as much logic as possible into the pure layer: it's fast, deterministic, and runs on every commit. Use the engine layers for the seams.

## 2. Write code you can test

**Pure modules.** Put rules in ModuleScripts that take plain values and return plain values: no `game:GetService`, no `task.wait`, no `os.time()` inside. Pass time, randomness, and state in.

```luau
-- Illustrative: a pure cooldown rule, testable anywhere.
local Cooldown = {}

export type State = { readyAt: number }

function Cooldown.tryUse(state: State, now: number, duration: number): (boolean, State)
	if now < state.readyAt then
		return false, state
	end
	return true, { readyAt = now + duration }
end

return Cooldown
```

**Dependency injection.** When a module needs an engine service, pass it in (or a table with the same methods). Production passes the real service; tests pass a fake.

```luau
-- Illustrative: the store is injected, so tests can use an in-memory fake.
type Store = {
	GetAsync: (self: Store, key: string) -> any,
	SetAsync: (self: Store, key: string, value: any) -> (),
}

local function makeFakeStore(): Store
	local data: { [string]: any } = {}
	local fake = {}
	function fake:GetAsync(key: string): any
		return data[key]
	end
	function fake:SetAsync(key: string, value: any)
		data[key] = value
	end
	return (fake :: any) :: Store
end

local function grantCoins(store: Store, userId: number, amount: number): number
	local key = "player_" .. tostring(userId)
	local balance = (store:GetAsync(key) or 0) + amount
	store:SetAsync(key, balance)
	return balance
end

return { makeFakeStore = makeFakeStore, grantCoins = grantCoins }
```

Real DataStores use `UpdateAsync` for this; the point is the seam, not the save pattern (`roblox-data`).

**Shared rules on both sides.** When client and server both run a rule (weapon state, hitboxes, cooldowns), one pure module serves both. A test of that module covers prediction and validation at once (`roblox-networking` §3b).

**Make clocks and randomness inputs.** Pass `now` into functions instead of calling `os.clock()` inside them, and pass a `Random` object instead of using `math.random`. Then a test can fix the seed and the time.

```luau
-- Illustrative: seeded rolls are reproducible in tests.
local function rollRarity(rng: Random, weights: { [string]: number }): string
	local total = 0
	for _, w in weights do
		total += w
	end
	local pick = rng:NextNumber() * total
	for name, w in weights do
		pick -= w
		if pick <= 0 then
			return name
		end
	end
	return next(weights) :: string
end

return rollRarity
```

Iteration order over a dictionary isn't guaranteed. For a deterministic roll, sort the keys or store weights as an array.

**Test the contract, not the implementation.** Assert what callers rely on (inputs to outputs, errors, events fired), not private fields or call counts. Refactors then don't break tests that should still pass.

## 3. Native engine tests: TestService (official)

<!-- temporal: 2026-11 -->

Roblox's engine test framework runs Luau tests inside a playtest, against the same scripts, physics, and replication players get.

### Where it runs

`TestService.Enabled` is `true` only while playtesting in Studio (**Play**, **Play Here**, or **Run**) and on a Team Test server.

- It's `false` in Edit mode (including the command bar while editing) and in live servers.
- While it's `false`, `RegisterTest`, `RegisterSuite`, `RunTestsAsync`, `ListTests`, and `ResetTestRegistry` throw.
- Tests can't run in a published experience.

So guard any script that registers tests and might also ship:

```luau
local TestService = game:GetService("TestService")
if not TestService.Enabled then
	return -- not a playtest
end
```

### Registering tests

- `TestService:RegisterTest(name, callback, options?)` registers a test in the `Default` suite and returns its `TestCase`.
- `TestService:RegisterSuite(name, options?)` returns a `TestSuite`, and `suite:RegisterTest(...)` adds tests to it. Tests in a suite inherit its tags and timeout.
- Calling `RegisterSuite` again with the same name and no options (or an empty table) returns the existing suite, so several scripts can add to one suite. Different options throw.
- `options`:
  - `Tags`: an array of strings.
  - `TimeoutSec`: 0 to 86400, default 30; 0 means no per-test timeout.
- Each test name must be unique within its suite. Empty names, duplicate names, bad tags, and out-of-range timeouts throw.
- The callback receives `(test: TestCase, context: TestExecutionContext)` and may yield.

### Checking values

- `test:Check(actual, expected, message?)` records a failure on mismatch and keeps running.
- `test:Require(actual, expected, message?)` does the same check, but stops the test on mismatch. Use it when the rest of the test can't continue (a part it needs is missing).
- Equality rules:
  - Different types never match.
  - Tables compare deeply unless they have `__eq`.
  - NaN never equals itself.
  - Instances match only by identity.
- Checks made after a test has finished are ignored. So a check inside a spawned thread that outlives the test doesn't count.
- `context:Skip(reason?)` stops the test and records it as `Skipped`, for example a touch test on a device without touch. The test is reported as failed instead if a check already failed, or if the callback catches the skip with `pcall` and throws a different error.

### Timeouts

A test that runs past its `TimeoutSec` is reported `TimedOut`.

- If it's yielding when time runs out, it stops there, but threads it spawned keep running.
- If it's running without yielding, it's reported timed out when it finishes.
- The place's script timeout still stops a test that never yields.

### Running and reading results

`TestService:RunTestsAsync(filter?)` runs tests one at a time, in registration order, and yields until the last finishes.

- **Filter fields** (all optional; a test runs only if it matches every field you set):
  - `TestId`: an exact match.
  - `Suite`: the suite name.
  - `NamePattern`: plain, case-sensitive substring; not a Lua pattern.
  - `IncludeTags`: any of these tags.
- Unknown fields, wrong types, and empty `TestId`, `Suite`, or `IncludeTags` throw.
- **One run at a time.** Starting a second run throws. Tests registered during a run wait for the next one.
- It prints a summary to Output and returns a `TestRunResult`.

**`TestRunResult`:**

- Counts: `Passed`, `Failed` (includes `TimedOut`), `Skipped`, `Total`.
- `Duration`, and `Summary` (for display; don't parse it).
- `GetTests()` returns a `TestResult` per test.
- `Status` is an `Enum.TestRunStatus`: `Pass`, `Fail`, `NoTests`, or `Skipped`. Compare it against `Enum.TestRunStatus.Pass` rather than listing failure values, because statuses may be added. Treat `NoTests` as a failure in CI, since a filter typo otherwise passes silently.

**`TestResult`:**

- `Status` (`Enum.TestCaseStatus`: `Pass`, `Fail`, `TimedOut`, `Skipped`).
- `FailedChecks`, `PassedChecks`, `SkipReason`, `UncaughtError`, `Duration`.
- `TestId`, `TestName`, `SuiteName`, `GetTestTags()`.
- `GetFailures()` returns up to the first 1,000 `TestFailure`s.

**`TestFailure`:**

- `Line`, `Matcher` (`"equal"`), and `Message` (default "Values are not equal").
- `StackTrace` (always empty for now).
- `GetActual()` and `GetExpected()` return display copies.
- `GetSource()` returns the script, or nil.

**`TestCase`:** `SuiteName`, `TestName`, `TimeoutSec`, `GetTestTags()`, and `TestId`. Treat `TestId` as opaque: read it from the object instead of building it from names.

Other members:

- `ListTests()` returns every registered `TestCase` in order.
- `ResetTestRegistry()` clears tests and suites; it throws during a run.
- `TestRegistryChanged` fires at most once per Heartbeat after registrations.

### A complete runner

```luau
-- Illustrative: ServerScriptService/Tests/RunAll.server.luau
local ServerScriptService = game:GetService("ServerScriptService")
local TestService = game:GetService("TestService")

if not TestService.Enabled then
	return
end

local Cooldown = require(ServerScriptService.Shared.Cooldown)

local rules = TestService:RegisterSuite("Rules", { Tags = { "unit" }, TimeoutSec = 5 })

rules:RegisterTest("cooldown blocks early use", function(test)
	local ok, state = Cooldown.tryUse({ readyAt = 10 }, 9, 2)
	test:Check(ok, false, "used before readyAt")
	test:Check(state.readyAt, 10)
end)

rules:RegisterTest("cooldown allows use and resets", function(test)
	local ok, state = Cooldown.tryUse({ readyAt = 0 }, 5, 2)
	test:Require(ok, true)
	test:Check(state, { readyAt = 7 }) -- tables compare deeply
end)

local world = TestService:RegisterSuite("World", { Tags = { "smoke" } })

world:RegisterTest("a SpawnLocation exists", function(test)
	local spawnLocation = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
	test:Check(spawnLocation ~= nil, true, "the place needs a SpawnLocation")
end)

task.defer(function()
	local result = TestService:RunTestsAsync()
	if result.Status ~= Enum.TestRunStatus.Pass then
		for _, r in result:GetTests() do
			if r.Status == Enum.TestCaseStatus.Fail or r.Status == Enum.TestCaseStatus.TimedOut then
				warn(r.TestId, r.UncaughtError)
				for _, failure in r:GetFailures() do
					warn(`  line {failure.Line}: {failure.Message}`)
				end
			end
		end
	end
end)
```

`task.defer` lets other scripts finish registering their tests before the run starts. For a strict order, run from one runner script that requires every test module.

### Engine-test habits

- **Guard with `Enabled`, every time.** Keep test scripts in a folder that your release build excludes, too: belt and braces.
- **Clean up.** Destroy parts and disconnect connections a test created, or later tests see its leftovers.
- **Wait on conditions, not fixed sleeps.** Poll a condition with a deadline (`while not cond() and os.clock() < deadline do task.wait() end`), then `Check` the condition.
- **Tag by cost.** `unit` for fast rule checks, `smoke` for world sanity, `slow` for physics or network waits, so a quick run can use `IncludeTags = { "unit", "smoke" }`.

## 4. Pure-Luau frameworks outside the engine

| Tool | What it is | Notes |
|---|---|---|
| Lune | A standalone Luau runtime with file, process, and `roblox` libraries | Runs pure modules and place-file scripts in CI with no Studio. Quirks: `roblox-tooling` §1g |
| Jest Lua | A Lua port of Jest (`describe`, `it`, `expect`), maintained under jsdotlua | Rich matchers, mocks, and snapshots. Runs in Roblox or a runner |
| TestEZ | Roblox's older BDD framework (`describe`, `it`, `expect`) | Archived. Keep it where a project already uses it; prefer the native framework or Jest Lua for new work |

A minimal Lune test needs no framework: require the module through a `.luaurc` alias, assert, and exit non-zero on failure.

```luau
-- Illustrative: tests/cooldown.spec.luau, run with `lune run tests/cooldown.spec`
local Cooldown = require("../src/shared/Cooldown")

local failures = 0
local function check(name: string, actual: any, expected: any)
	if actual ~= expected then
		failures += 1
		print(`FAIL {name}: expected {tostring(expected)}, got {tostring(actual)}`)
	end
end

local ok = Cooldown.tryUse({ readyAt = 10 }, 9, 2)
check("blocks early use", ok, false)

local ok2, state = Cooldown.tryUse({ readyAt = 0 }, 5, 2)
check("allows use", ok2, true)
check("resets readyAt", state.readyAt, 7)

if failures > 0 then
	error(`{failures} test(s) failed`)
end
print("all passed")
```

Lune's `require` resolves paths relative to the script. Packages that call `game:GetService` won't run there without shims, so keep engine code out of the pure layer.

## 5. Running tests from an agent

**Studio MCP.** Roblox's built-in Studio MCP server can start and stop play and run Luau. Its `execute_luau` targets a DataModel type of Edit, Client, or Server.

- Engine tests need a running playtest. Start play, run the runner on the Server DataModel, and read the printed summary or return the counts.
- Edit-mode execution can't run `TestService` (it's disabled there), but it can `require` pure modules.
- Studio caches `require` results in Edit mode, so require a clone to pick up edits (`roblox-tooling` §1g).

**Built-in `rbx-unit-test` skill.** Studio's Assistant ships a unit-test skill. It:

- detects Jest Lua or TestEZ in the project and falls back to a built-in harness;
- writes tests against the module's contract, with stubs for its dependencies;
- runs them in Play.

Load it when the host offers it, and follow the project's existing framework.

**Read live state before trusting a pass.** A sync tool can stop applying edits silently, so a green run may be testing old code. Before a measured run, read back a value you just changed from the running peer (`roblox-tooling` §1g).

## 6. CI with Open Cloud Luau Execution (official)

Roblox's file-based workflow docs suggest running tests from CI through **Luau Execution**: you send a script, and Roblox runs it on a server loaded with a place version.

- **Endpoint:** `POST https://apis.roblox.com/cloud/v2/universes/{universeId}/places/{placeId}/luau-execution-session-tasks`. Add `/versions/{versionId}` before the task path to pin a version.
- **Scopes:** `universe.place.luau-execution-session:write` to create a task. Reading the task and its logs needs read access.
- **Inside a task:**
  - Physics doesn't run, and server and local scripts don't start automatically. Your script must require and run what it tests.
  - DataModel changes aren't persisted, **but DataStore APIs act on real cloud data**, so point tests at a test universe or fakes.
- **Limits:** a script up to 4 MB, runtime up to 5 minutes, return values up to 4 MB as JSON, and logs up to 450 KB.

Whether `TestService.Enabled` is true inside a task isn't documented. Check it at runtime, and fall back to a framework or plain asserts.

```luau
-- Illustrative task body: return machine-readable counts to CI.
local ServerScriptService = game:GetService("ServerScriptService")
local Cooldown = require(ServerScriptService.Shared.Cooldown)

local results = { passed = 0, failed = 0, failures = {} :: { string } }

local function check(name: string, actual: any, expected: any)
	if actual == expected then
		results.passed += 1
	else
		results.failed += 1
		table.insert(results.failures, `{name}: expected {tostring(expected)}, got {tostring(actual)}`)
	end
end

local ok = Cooldown.tryUse({ readyAt = 10 }, 9, 2)
check("cooldown blocks early use", ok, false)

return results
```

The CI job:

1. Builds the place, publishes it to a test universe (or uploads a version).
2. Creates the task with the script.
3. Polls the task until it finishes.
4. Fails the build unless `failed == 0` and `passed > 0`.

Gate on parsed counts, not exit codes or log text (`roblox-tooling` §9). Keep the API key in CI secrets with only the scopes above (`roblox-cloud`).

## 7. Multi-client playtests

**Server & Clients mode.** Studio's Test tab can start a server with up to 8 clients. One or two clients cover most checks. Team Test shares collaborator client logs.

**`StudioTestService`** (Studio-only) scripts multi-client tests from a plugin:

- `ExecuteMultiplayerTestAsync(numPlayers, args)` starts a server with up to 8 simulated clients and yields until the test ends. It's plugin-only, can't be called from inside a running test, and only one session can run per Studio instance.
- The server reads `GetTestArgs()`, can `AddPlayers(n)` mid-test, and ends with `EndTest(value)`. That value is what `ExecuteMultiplayerTestAsync` returns.
- Clients call `CanLeaveTest()` and `LeaveTest()` to simulate disconnects. `GetTestArgs` has a known issue on client LocalScripts.
- `ExecutePlayModeAsync(args)` and `ExecuteRunModeAsync(args)` start single-session tests.

Use it for lobby, matchmaking, and join/leave flows. Studio's MCP `start_stop_play` covers a single Play client.

**Input and devices.**

- `UserInputService:CreateVirtualInput()` returns a `VirtualInput` for scripted input in Studio.
- The Device Simulator (`StudioDeviceSimulatorService`) switches device profiles.
- Both are Studio-only.

**Network conditions.** Test prediction and timers under simulated latency and jitter (Studio's network simulator), not only at zero ping (`roblox-networking` §3b).

## 8. What to test, by risk

**Remotes and gameplay (observed).**

- **Test through the real client sender.** Server tests that call the handler directly passed while the real path was broken. In one case a removed config field silently gated the client code that sent hits. In another, the server dropped packets whose slot argument was out of range because a new weapon reused that field. When you remove a config field, grep everything it gates.
- **Walk every early return.** When a bug survives a fix, read live state first: both sides stuck at the same value means the server refused before spending. Then walk every early return on the server path for that packet, including range checks.
- **Fire tools repeatedly.** Bugs that appear on the second or third activation (can't refire, double fire, breaks after the third shot) recurred across sessions. Fire each tool 5 or more times, including after reload and swap, and log every server-side rejection with its reason.
- **Test from the timer's last frame.** Cooldown and reload boundaries break there, not on a fresh weapon (`roblox-networking` §3b).
- **Fuzz entity ids and numbers.** Send NaN, infinity, negatives, fractions, and dead ids to every remote that takes ids or numbers.

**Saves (`roblox-data`).**

- Repeat a grant with the same grant id. It must return the existing result.
- Claim offline earnings, rejoin inside the minimum absence, and expect zero.
- Interrupt a save mid-grant (kill the server or leave) and check what the next load sees.
- Encode and decode every replicated blob with an unknown template or a missing field.

**Purchases (`roblox-monetization`).**

- Each offer's label matches its grant; displayed odds sum to 100% and match the server table.
- There's exactly one `ProcessReceipt` assignment.
- Pass free trials: trial start, session end, crash-and-rejoin within the hour, and purchase during the trial.

**Multiplayer claims (observed).** For friendly fire, party payouts, and spawn protection, run two real accounts on two machines against the dev universe. Add a temporary server-side damage and death log, so every claim comes from the server log rather than one screen.

- Engine messages such as asset load failures don't reach custom error telemetry, so also read each client's F9 log.
- Restore test saves afterward, and remember that test activity lands in dev leaderboards.

## 9. QA checklist before a release

- [ ] Pure tests pass in CI (Lune or a framework), gated on parsed counts.
- [ ] Engine suite passes in a Studio playtest, and `NoTests` counts as failure.
- [ ] Every remote changed in this release was exercised through the real client path.
- [ ] Tools fired 5+ times, including after reload and swap. Zero unexplained server rejections in the log.
- [ ] Fresh-profile first session, leave, and rejoin; every reward claimed once.
- [ ] Two-client check for any shared or competitive state.
- [ ] Phone-size viewport and touch input checked, using the Device Simulator at minimum.
- [ ] Latency and jitter simulated for prediction-heavy features.
- [ ] Test scripts excluded from the release build, or guarded by `TestService.Enabled`.
- [ ] The serving build matches the tested commit (`roblox-publish-checklist`).

## Sources

Official (reviewed 2026-11-27):

- [TestService](https://create.roblox.com/docs/reference/engine/classes/TestService), [TestCase](https://create.roblox.com/docs/reference/engine/classes/TestCase), [TestSuite](https://create.roblox.com/docs/reference/engine/classes/TestSuite), [TestRunResult](https://create.roblox.com/docs/reference/engine/classes/TestRunResult), [TestResult](https://create.roblox.com/docs/reference/engine/classes/TestResult), [TestFailure](https://create.roblox.com/docs/reference/engine/classes/TestFailure), [TestExecutionContext](https://create.roblox.com/docs/reference/engine/classes/TestExecutionContext)
- [TestCaseStatus](https://create.roblox.com/docs/reference/engine/enums/TestCaseStatus), [TestRunStatus](https://create.roblox.com/docs/reference/engine/enums/TestRunStatus)
- [StudioTestService](https://create.roblox.com/docs/reference/engine/classes/StudioTestService), [Testing modes](https://create.roblox.com/docs/studio/testing-modes), [File-based workflows](https://create.roblox.com/docs/projects/file-based-workflows)

Frameworks: [Lune](https://lune-org.github.io/docs/), [Jest Lua](https://raw.githubusercontent.com/jsdotlua/jest-lua/main/README.md), [TestEZ](https://raw.githubusercontent.com/Roblox/testez/master/README.md).
