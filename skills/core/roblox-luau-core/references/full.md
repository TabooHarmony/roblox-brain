# Luau Core Language: Full Reference

This reference covers the language plus the Roblox-facing facts agents need most often: engine deprecations, sandbox deltas from Lua 5.1, the native codegen directives, and Roblox naming conventions. Deeper engine behavior belongs in the domain skills.

## 1. Values, truthiness, and equality

Only `false` and `nil` are falsy. Zero, empty strings, and empty tables are truthy.

```luau
if 0 then
    print("runs")
end

print(0 == "0") -- false
print(1 == true) -- false
```

Equality does not coerce between numbers, strings, and booleans. Inequality is `~=`. Use explicit empty or zero checks when those values are invalid.

The common fallback expression `value or defaultValue` replaces both `nil` and `false`. If `false` is valid, test for `nil` explicitly.

```luau
local result = if value == nil then defaultValue else value
```

Prefer Luau's `if` expression when the true branch could be `false` or `nil`. The older `condition and trueValue or falseValue` idiom cannot preserve a falsy true value.

## 2. Tables are several shapes, not one promise

A table can represent a sequence, dictionary, record, set, object, or module. Choose one shape intentionally.

```luau
local sequence = { "first", "second" }
local record = { name = "Ada", score = 10 }
local dictionary: {[number]: string} = {}
dictionary[userId] = "Ada"
local set: {[string]: boolean} = { admin = true }
```

Array conventions are 1-based. The length operator is useful for a contiguous sequence. Once a numeric-keyed table has nil gaps, do not rely on `#table` as a count or boundary.

Assigning `nil` removes a key. Use `table.remove(sequence, index)` when removing from the middle of a sequence and preserving contiguity matters.

Dot syntax is literal field syntax. Dynamic keys require brackets:

```luau
local field = "score"
print(record[field])
```

Dictionary iteration order is unspecified. Sort explicit keys or values before emitting stable output.

### `__newindex` fires only for keys the table does not have

An assignment goes through `__newindex` only when the key is absent from the raw table. Once a key exists — including after a single `rawset` inside the hook — later writes bypass the hook while that raw key remains present (verified against the Luau runtime, 2026-10):

```luau
local log = {}
local t = setmetatable({}, { __newindex = function(tbl, key, value)
	table.insert(log, key)
	rawset(tbl, key, value) -- the write itself must not re-enter the hook
end })
t.a = 1 -- hook runs
t.a = 2 -- raw write: key now exists, hook does NOT run
```

Two consequences:

- Inside `__newindex`, write with `rawset` or to a separate table. A plain `tbl[key] = value` on an absent key re-enters the hook recursively.
- A hook that must observe *every* write cannot let the exposed table ever hold the data. Keep the exposed table permanently empty and store the value elsewhere (`store[key] = value` inside the hook); every write then hits the hook because no raw key ever becomes present.

### Datatype table keys: Vector3 by value, Vector2 by identity

`Vector3` is the VM's native vector value type, so `t[Vector3.new(1, 2, 3)]` and a later `t[Vector3.new(1, 2, 3)]` hit the same entry. That makes a floored `Vector3` a cheap spatial-grid key (see `roblox-luau-patterns`). Field-measured in Studio: `Vector2` keys hash by identity, so `t[Vector2.new(1, 2)] = 5` followed by `t[Vector2.new(1, 2)]` reads `nil` with no error, and linters do not warn. Treat other userdata datatypes (`CFrame`, `Color3`, `UDim2`) the same way until you have checked them. For 2D grid cells use `Vector3.new(x, 0, z)` or a string key.

## 3. Reference and copy semantics

Tables are references. Assignment aliases the same table.

```luau
local original = { score = 10, nested = { enabled = true } }
local alias = original
alias.score = 20
print(original.score) -- 20
```

`table.clone` creates a shallow copy. Nested tables remain shared.

```luau
local copy = table.clone(original)
copy.score = 30
copy.nested.enabled = false -- also changes original.nested.enabled
```

Do not add a generic recursive deep-copy helper without defining how it handles metatables, cycles, shared subgraphs, Instances, and unsupported keys. Copy only the data shape the caller owns.

`table.freeze` prevents writes to that table, not recursively to all nested tables. Treat it as one boundary, not deep immutability.

Freezing an already frozen table raises an error (`table is already frozen`; checked with the standalone Luau CLI). When the call runs at module require time, for example several config entries that share one frozen list, the whole requiring script dies even though static checks pass. Freeze a shared table once where it is created, or guard with `table.isfrozen(t)`.

### Weak tables and Instance keys

A metatable's `__mode` makes keys (`"k"`), values (`"v"`) or both (`"kv"`) weak, so the collector can reclaim an object referenced only from that table; collection is nondeterministic. For Instances, collection applies to the Luau reference, not the object: the engine keeps instance data outside the VM, so an instance still in the data model does **not** keep its Luau reference alive. The docs warn not to use a weak table to track whether an Instance still exists ([metatables](https://create.roblox.com/docs/luau/metatables#use-weak-tables)). In one project a weak-keyed "fallen parts" set read 0 entries while every part was still in the world.

- Use weak Instance-keyed tables only as caches where a lost entry is a harmless miss.
- For sets you must keep, use a plain table and remove entries on `Instance.Destroying` or `AncestryChanged`; for tagged instances use `CollectionService` signals.

```luau
-- Illustrative: a strong set that cleans itself up.
local tracked: { [Instance]: true } = {}

local function track(instance: Instance)
    if tracked[instance] then
        return
    end
    tracked[instance] = true
    instance.Destroying:Once(function()
        tracked[instance] = nil
    end)
end
```

### Immutable updates via path copying

Practitioner design, informed by [Kampfkarren’s guidelines](https://raw.githubusercontent.com/Kampfkarren/kampfkarren-luau-guidelines/main/README.md); independently written here. For tree-shaped immutable state, clone each table along the changed path instead of deep-copying unrelated branches:

```luau
local settings = { audio = { volume = 0.8 }, video = { shadows = true } }
local updated = table.clone(settings)
updated.audio = table.clone(settings.audio)
updated.audio.volume = 0.4 -- settings.audio.volume remains 0.8
```

Unchanged branches retain identity and can be shared only while they remain immutable. Cloning cost depends on the sizes of the tables copied, not just path depth. This is not a replacement for independent mutable snapshots: aliases and cycles need an explicit ownership policy. Existing deep-copy requirements for mutable player defaults still apply; see `roblox-data`.

## 4. Iteration and mutation

Generalized iteration is valid Luau:

```luau
for index, value in sequence do
    print(index, value)
end

for key, value in dictionary do
    print(key, value)
end
```

Use numeric loops when index range is the contract. Avoid removing sequence elements while iterating forward because indices shift. Iterate backward, record removals, or build a filtered result.

```luau
for index = #sequence, 1, -1 do
    if shouldRemove(sequence[index]) then
        table.remove(sequence, index)
    end
end
```

`table.find` searches array values and returns an index or nil. It does not search dictionary keys or apply a predicate. `table.sort` mutates the sequence and its comparator must define a consistent strict order.

## 5. Scope, functions, and multiple values

A local name is visible from its declaration onward. Code above a local declaration does not capture that later local.

A `repeat … until` condition can see locals declared inside its body; those locals do not escape the loop. The body runs at least once, and the loop stops when the condition is **true**, unlike `while`. Source: [control structures](https://create.roblox.com/docs/luau/control-structures).

```luau
local second

local function first(value: number)
    if value > 0 then
        second(value - 1)
    end
end

function second(value: number)
    if value > 0 then
        first(value - 1)
    end
end
```

Forward declaration is appropriate for mutual recursion. Otherwise place a callee before its callers.

Functions can return multiple values. Context can keep or discard them:

```luau
local function divide(a: number, b: number): (number?, string?)
    if b == 0 then
        return nil, "division by zero"
    end
    return a / b, nil
end

local quotient, problem = divide(6, 2)
```

Parentheses and table constructors affect multiple-value expansion. When this matters, assign the values explicitly rather than relying on terse expression behavior.

A call expands to all its values only as the **last** argument or list item; anywhere else it is cut to its first value (`select("#", g(), 3)` is 2 for a two-value `g`, `select("#", 3, g())` is 3). Passing a multi-return helper into the middle of an argument list shifts every later argument. In one project a player arrived as a `Vector3` and the server errored on every use, unnoticed because the callee was untyped. Unpack into locals first, annotate the callee, and read the server error log after one use, not only the client's.

```luau
local function sizeAndCenter(): (Vector3, Vector3)
    return Vector3.one, Vector3.zero
end

local function place(size: Vector3, center: Vector3, owner: Player?) end

local size, center = sizeAndCenter()
place(size, center, nil) -- explicit; place(sizeAndCenter(), nil) would drop center
```

### A line that starts with `(` continues the previous statement

Luau has no statement terminator, so `part:Destroy()` followed by a line `(boxes :: any)[i] = nil` parses as calling the result of the previous line. The same happens after an assignment such as `x.Parent = folder`. Never start a line with `(`: assign through a local first, or reorder the statements.

```luau
local function clear(boxes: { BasePart }, i: number)
    boxes[i]:Destroy()
    local list = boxes :: any -- cast through a local instead of a leading "("
    list[i] = nil
end
```

Missing arguments are `nil`; extra arguments can be ignored. A function that requires arity or non-nil inputs must validate or express that contract through types and call structure.

Loop variables in a numeric or generic `for` have iteration-local behavior. Variables mutated outside the loop are shared by closures. Capture the intended value in a new local when ownership is unclear.

### `const` bindings

<!-- temporal: 2026-03 -->
`const` was added in Luau 0.711 (March 2026). Older tooling and lint stubs may reject it; the keyword is valid ([release notes](https://github.com/luau-lang/luau/releases/tag/0.711), [RFC](https://github.com/luau-lang/rfcs/blob/master/docs/const-keyword.md)).

```luau
const maxRetries = 3
-- maxRetries = 5 -- rejected at compile time: constant rebinding

const config = { speed = 16 } -- the binding is frozen, not the table
config.speed = 20 -- allowed; use table.freeze for value immutability
```

A `const` binding freezes the name, not the value; it applies to the binding like `local`, and the table itself stays mutable unless frozen. It is a contextual keyword, valid only where `local` is. `const` must be initialized at declaration. Prefer `const` for module-level values and constants that must never be rebound; it lets the typechecker and tools treat the symbol as stable.

## 6. Method syntax

A colon adds an implicit first argument named `self`.

```luau
function object:move(amount)
    self.position += amount
end

object:move(2)
-- equivalent call shape: object.move(object, 2)
```

A dot does not add `self`. Define and call a function consistently. Constructors and module functions usually use dot syntax; instance methods usually use colon syntax.

Metatable object design and lifecycle belong in `roblox-luau-patterns`.

## 7. Strings and patterns

### Literal search, splitting, and byte-oriented operations

Use existing [standard library](https://luau.org/library) functions before inventing parsing helpers:

- `string.find(text, needle, 1, true)` performs literal search. Without the fourth argument, punctuation in the needle may act as pattern syntax. Prefer literal search for user-supplied search text.
- `string.split(text, separator)` uses a literal separator, not a pattern; the default separator is comma. An empty separator splits **bytes**, not Unicode characters.
- `string.reverse` reverses bytes and can corrupt UTF-8. `string.lower`/`upper` handle ASCII case, not international case folding. Do not use these as Unicode-aware display or name normalization.
- `string.format` supports field width/precision, e.g. `%.2f`; it is not locale-aware number formatting.
- `string.pack`/`unpack` provide binary strings; `packsize` reports a fixed format's size. Use an explicit layout and byte order rather than assuming host sizes. Prefer the existing `buffer` guidance when mutable binary storage is needed.


Backtick interpolation and `..` concatenation are both valid:

```luau
local message = `{name} reached {score}`
local path = prefix .. "/" .. suffix
```

Use the clearer form. When assembling many pieces in a loop, collect fragments in a sequence and call `table.concat` once if measurements show allocation matters.

Luau uses Lua-style string patterns, not regular expressions. Do not paste regex syntax and assume equivalent behavior.

Common classes include `%a` letters, `%d` digits, `%w` alphanumeric, and `%s` whitespace. Uppercase forms negate a class. Pattern magic characters must be escaped according to Lua pattern rules.

```luau
local year, month, day = string.match("2026-07-26", "^(%d+)-(%d+)-(%d+)$")
local compact = string.gsub("too   wide", "%s+", " ")
for word in string.gmatch("one two", "%S+") do
    print(word)
end
```

A plausible-looking email regex translated into a Lua pattern is not robust email validation. Validate only the format the product actually needs.

### Equality dispatch with `__eq`

The `__eq` hook is consulted only when both operands carry the *same* handler function (sharing one metatable is a simple way to ensure this). With a handler present, `x == x` also reaches the handler — Luau does not short-circuit self-comparison once `__eq` exists. When the two operands have different `__eq` handlers, Luau calls neither and falls back to raw identity; a handler on only one side is likewise ignored. All of this is live Luau behavior (probed 2026-10), not Lua 5.1 semantics:

```luau
local Vec = {}
Vec.__index = Vec
Vec.__eq = function(a, b)
	if rawequal(a, b) then -- identity check must not recursively invoke __eq
		return true
	end
	return a.x == b.x and a.y == b.y
end
```

The handler's return is coerced to a boolean: any non-nil/non-false value counts as equal, `nil`/`false` as unequal. Consequences:

- Two classes that each define their own `__eq` cannot ever compare equal across types — the cross-type comparison silently ignores both handlers. Share one metatable per type.
- Put an identity check at the top of expensive handlers; it runs even for `x == x`.
- `rawequal(a, b)` never dispatches `__eq`; use it for identity checks that must not run user code.

### Library operations ignore metamethods

`#` honors `__len`; `rawlen`, `ipairs`, `pairs`, `table.insert`, and `table.concat` operate on raw storage. Generalized `for ... in t` is different: it can call `__iter`. Do not assume a custom iterator changes how `pairs` or the table library sees a proxy. A proxy whose elements live only behind `__index` iterates as empty and concatenates to `""`; `table.insert(proxy, v)` writes raw storage and skips `__newindex` (all probed 2026-10). Consequences:

- A read-only view or tracking proxy must keep the real data in a raw field (or the backing table) and iterate *that*; iterating the proxy itself finds nothing.
- `rawlen(t)` is the deliberate raw-length read; keep `__len` off tables that are also used as sequences, or length checks in library calls will disagree with `#`.
- There is no `__pairs` dispatch in Luau; `pairs` cannot be redirected.

## 8. Numeric behavior

Luau provides ordinary arithmetic, compound assignment such as `+=`, and floor division `//`. Be explicit around division by zero, negative values, clamping, and units.

`NaN` propagates through arithmetic and is unequal to everything including itself. Range guards written as `if v < min or v > max` silently accept NaN because both comparisons are false. Guard with `v ~= v`.

Floor division `//` truncates toward negative infinity (`-7 // 2 == -4`). `0/0` is NaN.

### buffer library

- Fixed-size binary data without table overhead: `buffer.create(size)`, then read/write typed values at offsets.
- Offsets are 0-based, sizes in bytes. Out-of-range access errors; the buffer does not grow.
- The function name selects width and numeric representation (`readu8`/`readi16`/`readf32` family); byte order is fixed, not a selectable argument.
- Multibyte numeric reads/writes are little-endian; signed integers use two's complement ([luau.org/library](https://luau.org/library)); matters whenever buffer contents cross to an external format.
- `buffer.readinteger`/`buffer.writeinteger` are 64-bit integer APIs behind the upstream `LuauIntegerLibrary` flag ([runtime source](https://raw.githubusercontent.com/luau-lang/luau/master/VM/src/lbuflib.cpp)). They are present in the local standalone CLI used for these probes, but are not listed in the Roblox buffer reference checked in 2026-10. Do not infer Roblox availability from a standalone CLI or from missing web documentation; verify the target runtime before using them.

- **Vector read/write** (added to the Roblox buffer reference by 2026-11): `buffer.readvectorf32x3(b, offset)` and `buffer.writevectorf32x3(b, offset, v)` move a whole `Vector3` as three `f32` values (12 bytes). The `x2` forms read or write 8 bytes: `readvectorf32x2` returns a vector with Z set to 0, and `writevectorf32x2` writes only X and Y. Values are stored as `f32`, so expect float rounding on the way back. <!-- temporal: 2026-11 -->

```luau
local POSITION = 0 -- 12 bytes
local FACING = 12 -- 8 bytes (X, Y only)

local b = buffer.create(20)
buffer.writevectorf32x3(b, POSITION, Vector3.new(10, 4, -2))
buffer.writevectorf32x2(b, FACING, Vector3.new(0.6, 0.8, 0))
local position = buffer.readvectorf32x3(b, POSITION)
local facing = buffer.readvectorf32x2(b, FACING) -- Z reads as 0
```

Two failure modes behave oppositely — this is the part agents get wrong:

- **Out-of-bounds access errors loudly** (`buffer access out of bounds`): bad offset arithmetic is caught at the call.
- **A wrong-width read can silently succeed if it stays in bounds.** `readu16` on a slot written as `u32` returns the low bytes, not a schema-mismatch error. `f32` also rounds: a `writef32`/`readf32` roundtrip of `0.1` does not compare equal to the original double. Choose `f32` or `f64` for the required precision; neither makes arbitrary decimal values exact. Out-of-range integer *writes* are also silent, taking the value's least significant bits (`writeu8(b, 0, 300)` stores 44).

Decision rule: all offset and width arithmetic lives inside `get`/`set` helpers keyed by field name; no call site ever computes an offset or picks a width inline.

```luau
local bounded = math.clamp(value, minimum, maximum)
local whole = numerator // denominator
```

Floating-point equality is often the wrong test for derived values. Use a tolerance selected from the domain, not one universal epsilon.

Do not normalize a zero-length vector without deciding the fallback direction. Roblox datatype math belongs in the relevant camera, physics, or building skill.

### math library quick map

One-line semantics; full reference at [luau.org/library](https://luau.org/library). Angles are radians; use `math.rad`/`math.deg` to convert.

- `math.abs`, `math.floor`, `math.ceil`, `math.sqrt` (NaN on negative input), `math.exp`, `math.log(n, base?)` (base defaults to e; NaN on negative, `-inf` on 0), `math.log10(n)`.
- Trig: `math.sin`/`math.cos`/`math.tan` take radians; `math.asin`/`math.acos` return NaN outside `[-1, 1]`; `math.atan2(y, x)` resolves the quadrant from both signs (range `[-pi, pi]`) and is the correct angle from a displacement, not `math.atan(y/x)` which loses quadrant. Hyperbolic: `sinh`, `cosh`, `tanh`. `math.atan(n)` returns `[-pi/2, pi/2]`.
- `math.round` rounds to nearest, halfway away from zero; `math.floor`/`math.ceil` bound it. `math.fmod(x, y)` truncates toward zero and returns NaN when y is 0, unlike `x % y` which follows the sign of y. `math.modf(n)` returns integer and fractional parts, both with the input's sign. `math.frexp`/`math.ldexp` split/rebuild a significand and binary exponent.
- `math.clamp(n, min, max)` errors when `min > max`. `math.sign(n)` is `-1`/`1`/`0` (0 for NaN too). `math.max`/`math.min` require at least one argument and error otherwise.
- `math.random()` returns `[0, 1]`; `math.random(n)` returns `[1, n]`; `math.random(min, max)` returns `[min, max]`. Arguments are truncated to integers, so `math.random(1.5)` always returns 1. `math.randomseed(seed)` reseeds the generator for a deterministic sequence.
- `math.isnan`, `math.isinf`, `math.isfinite` classify problem values without `x ~= x` tricks.
- `math.noise(x, y?, z?)` is 3D Perlin noise, roughly `[-1, 1]`, inputs defaulting to 0. Smooth; use for procedural terrain and variation, not as a hash. For whole-terrain generation prefer a dedicated terrain or noise skill.
- Luau adds `math.lerp(a, b, t)` (`a + (b - a) * t`; at exactly `t == 1` returns `b`) and `math.map(x, inMin, inMax, outMin, outMax)` (linear range remap); neither exists in plain Lua 5.x.

### EncodingService

Roblox's engine service for Base64, hashing, and compression: `game:GetService("EncodingService")`. It operates on `buffer` values (use `buffer.fromstring`/`buffer.tostring` to convert), not strings, except the string hash. Docs: [EncodingService](https://create.roblox.com/docs/reference/engine/classes/EncodingService). <!-- temporal: 2026-08 -->

- `EncodingService:Base64Encode(input: buffer): buffer` and `:Base64Decode(input: buffer): buffer` (decode throws on invalid input).
- `EncodingService:ComputeBufferHash(input: buffer, algorithm: HashAlgorithm): buffer` and `:ComputeStringHash(input: string, algorithm: HashAlgorithm): string`. These are fast hashes (the `HashAlgorithm` enum), not password hashes or key derivation; use server-validated tokens or an external KDF for credential purposes.
- `EncodingService:CompressBuffer(input, CompressionAlgorithm, compressionLevel?)`: Zstd levels -7 to 22; higher compresses more, costs more time.
- `EncodingService:DecompressBuffer(input, CompressionAlgorithm)` throws when the size header is missing/corrupt or exceeds 1GB. For untrusted compressed data (e.g. from a client RemoteEvent), call `:GetDecompressedBufferSize(input, algorithm)` first; when it returns nil, refuse to decompress. Cap sizes by input source: compression amplification is a DoS vector.
- This is the engine alternative to hand-rolled Base64 or `HttpService:JSONEncode` misuse for binary payloads. For JSON, still use `HttpService`; EncodingService is for bytes.


## 9. Cross-language translation traps

### JavaScript to Luau

- `===` becomes `==`; `!==` becomes `~=`.
- `null` and `undefined` do not map to two separate values; Luau uses `nil`.
- Arrow functions, optional chaining, nullish coalescing, and spread syntax are not Luau syntax. JS `const`/`let` are unrelated to Luau's `const` keyword (a binding-freezing declaration added in 0.711) and there is no `let` at all.
- Array `.map`, `.filter`, `.find(predicate)`, `.push`, and `.length` are not methods on Luau tables.
- Object property enumeration order is not a portable dictionary-order contract.
- `try/catch` is not syntax; fallible execution uses `pcall` or `xpcall`, with domain-specific recovery.
- `async/await` is not syntax. Scheduling and Promise libraries belong in `roblox-luau-patterns`.

### Python to Luau

- Sequences conventionally start at 1, not 0.
- `None`, `True`, `False`, `elif`, list comprehensions, decorators, and exception syntax do not translate directly.
- Dictionaries, lists, objects, and sets can all be represented with tables, but their invariants must be stated.
- Tuple-like multiple returns are language behavior, not a single tuple object.
- Indentation does not delimit blocks; `then`, `do`, and `end` do.

Translate the data model and control flow, not token by token.

## 10. Deprecated and inherited APIs

Roblox deprecation is a spectrum. **Deprecated** here means the API carries an official Deprecated tag (creator docs show it struck through). **Discouraged** means it works today, has no tag, but Roblox documents a reason to avoid it. Both get replacements; only the first group will ever show deprecation tooling.

<!-- temporal: 2026-09 -->
Verify current tags against the class pages before quoting them in reviews; Roblox adds tags over time and legacy globals live in [Roblox globals](https://create.roblox.com/docs/reference/engine/globals/RobloxGlobals).

### Officially deprecated (tagged)

| Deprecated | Replacement | Notes |
| --- | --- | --- |
| `wait(seconds)` | `task.wait(seconds)` | Old global throttles to ~29 ms minimum and returns `(elapsed, gameTime)`; `task.wait` resumes on the next Heartbeat step without throttling. |
| `spawn(f)` | `task.spawn(f)` | Old global throttles the first resumption and passes extra args; `task.spawn` runs immediately. |
| `delay(t, f)` | `task.delay(t, f)` | Same throttling issues as `spawn`. |
| `:connect` / `:wait` (lowercase) | `:Connect` / `:Wait` | Legacy lowercase aliases on `RBXScriptSignal`; PascalCase names are canonical and get new behavior. |
| `BodyPosition` | `AlignPosition` | Legacy `BodyMover` family, all deprecated. |
| `BodyGyro` | `AlignOrientation` | |
| `BodyVelocity` | `LinearVelocity` | |
| `BodyForce`, `BodyThrust` | `VectorForce` | |
| `BodyAngularVelocity` | `AngularVelocity` (or `Torque`) | |
| `RocketPropulsion` | `LineForce` / `AlignPosition` + `AlignOrientation` | |
| `Humanoid:LoadAnimation` | `Animator:LoadAnimation` | Create the `Animator` on the server; calling the deprecated method from a client can create a client-only `Animator` that never replicates. Same applies to `AnimationController:LoadAnimation`. |
| `Part.Velocity` / `Part.RotVelocity` | `AssemblyLinearVelocity` / `AssemblyAngularVelocity` | Assembly-level physics; per-part behavior was inconsistent for non-root parts. Use `BasePart:GetVelocityAtPosition()` for a specific point. |
| `Model:SetPrimaryPartCFrame` | `PVInstance:PivotTo` | `GetPrimaryPartCFrame` → `PVInstance:GetPivot`. `PivotTo` needs no `PrimaryPart` and preserves offsets. |

Roblox's own deprecated-to-modern quick reference (creator docs `reference/engine/llms.txt`) confirms the mover and task rows above.

### Functional but discouraged (no official tag)

| API | Why discouraged | Use instead |
| --- | --- | --- |
| `tick()` | Not officially deprecated, but can be off by up to one second and returns inconsistent results across time zones and operating systems (Roblox's own docs say this). | `os.time()` (Unix seconds), `os.clock()` (benchmarks), global `time()` (session time), `workspace:GetServerTimeNow()` (synced), `DateTime` for timestamps. |
| `Instance.new(class, parent)` | Works, but the docs mark the parent argument as not recommended: parenting first makes every later property write replicate and re-run listeners. | Create, set properties, then assign `.Parent` last. Setting parent in the constructor is acceptable only when no properties are set afterwards or the parent is not yet replicated. |

Treat "deprecated" and "discouraged" as distinct when editing code: rewrite deprecated calls, and flag discouraged ones only when the surrounding code is already being touched.

## 11. Luau sandbox versus Lua 5.1

Luau starts from Lua 5.1 and subtracts. When porting Lua code or answering "why is X missing," these removals are intentional sandbox design, not bugs (sources: [luau.org/sandbox](https://luau.org/sandbox), [Luau globals](https://create.roblox.com/docs/reference/engine/globals/LuaGlobals)).

| Removed or reduced | Detail |
| --- | --- |
| `io` library | Removed entirely (file and process access). |
| `package` library | Removed entirely (native module loading). |
| `dofile` / `loadfile` | Removed (filesystem access). |
| `string.dump` | Removed; bytecode access is unsafe to validate. `loadstring` accepts source only, never bytecode. |
| `debug` library | Removed to a large extent; only `debug.traceback` and `debug.info` remain. |
| `os` | Reduced to `os.clock`, `os.date`, `os.difftime`, `os.time`. No `os.execute`, `os.exit`, `os.getenv`, `os.rename`, `os.remove`, `os.tmpname`. |
| `collectgarbage` | Only `"count"` works; other options are rejected because GC manipulation breaks isolation. `collectgarbage()` is effectively a weaker `gcinfo()` and deprecated in Roblox. |
| `newproxy` | Accepts `nil`/`false` (bare userdata) or `true` (empty metatable); the generator-function form is gone. |
| Builtin globals | Libraries, the string metatable, and the builtin globals table are read-only; monkey-patching `string` or `_G` builtin tables fails. Each script gets its own globals table that reads through to the builtins, so per-script globals still work. |
| `getfenv` / `setfenv` | Still present (legacy code relies on them) but costly to isolation: they can inject globals into callers on the stack. Avoid in new code; `debug.info`/upvalues and module returns cover the legitimate cases. |
| Yield restrictions | A `coroutine.yield` attempted inside a metamethod raises `attempt to yield across metamethod/C-call boundary` (probed 2026-10). An uncaught error terminates the coroutine. A `pcall` inside the metamethod can catch the error and let execution continue, but cannot make the yield succeed. `pcall`/`xpcall` themselves are the C-function boundaries you *can* yield across from ordinary code. If an `__index` hook needs data that requires waiting, make the wait explicit at the call site instead of yielding inside the hook. |

## 12. The vector library

Luau's native `vector` type underlies `Vector3`-style math. In Roblox, the library is the 3-wide VM type that `Vector3` interoperates with; the library itself is small ([luau.org/library](https://luau.org/library)).

```luau
local v = vector.create(1, 2, 3)
local m = vector.magnitude(v)
local n = vector.normalize(v)
local d = vector.dot(v, n)
local c = vector.cross(v, n)
local a = vector.angle(v, n)
local l = vector.lerp(v, n, 0.5)
-- componentwise: vector.floor / ceil / abs / sign / clamp / min / max
-- constants: vector.zero, vector.one
```

- Components are `x`/`y`/`z` (case-insensitive access); vectors are immutable, so there is no component write.
- Operator support: `+`, `-`, `*`, `/`, unary minus, and indexing are built into the VM, which is why vector math is fast under `--!native`.
- `vector.lerp(vec1, vec2, alpha)` linearly interpolates component-wise between the two vectors; `alpha` is not clamped to `[0, 1]` (values outside extrapolate). Do not confuse this Luau library function with Roblox's engine `Vector3` datatype, which uses the method form `Vector3:Lerp(goal, alpha)`.
- 4-wide mode (`LUA_VECTOR_SIZE`) exists for other embedders, not for Roblox, which is 3-wide.

## 13. Naming conventions

Roblox's official Lua style guide ([roblox.github.io/lua-style-guide](https://roblox.github.io/lua-style-guide/), verified 2026-09) sets the house conventions for Luau code:

| Construct | Convention | Example |
| --- | --- | --- |
| Classes, enum-like objects, module publics | `PascalCase` | `DataLoader`, `RobuxShop` |
| Locals, member values, functions | `camelCase` | `currentRound`, `beginVote()` |
| Local constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES = 5` |
| Private members | underscore-prefixed camelCase | `_connection` |
| Acronyms inside a name | Only capitalize the first letter | `aJsonVariable`, `MakeHttpCall` |
| Abbreviation as a set | Keep it fully capitalized | `anRGBValue`, `GetXYZ` |
| All words | Spell words out; avoid abbreviations | `label`, not `lbl` |

The acronym rule has two cases: an acronym like `JSON` or `HTTP` becomes `Json`/`Http` mid-name, while a set abbreviation like `RGB` or `XYZ` stays uppercase because it stands for full words. Spell-out is a readability rule, not a length limit; prefer the clearer name even when it is longer.

## 14. Native codegen (--!native / @native)

Roblox compiler feature: supported Luau compiles to machine code instead of VM bytecode. Best for numeric, table, and `buffer` heavy code with few library or API calls. Sources: [native code generation](https://create.roblox.com/docs/luau/native-code-gen), [Luau comments](https://create.roblox.com/docs/luau/comments). <!-- temporal: 2026-09 -->

```luau
--!native
--!optimize 2

local function kernel(v: Vector3, n: number): number
    local sum = 0
    for i = 1, n do
        sum += v.X * i
    end
    return sum
end
```

- **Scoping: server scripts and Android clients.** As of 2026-11 the docs say native code generation runs for server-side scripts and for client-side scripts on Android devices only; on other clients `--!native` has no effect, so benchmark client gains on an Android device. <!-- temporal: 2026-11 -->
- `--!native` on a Script compiles all of its functions (and the top-level scope only if deemed profitable). `@native` above an individual function narrows it to that function.
- **Pair with `--!optimize 2`.** Level 2 enables optimizations that harm debuggability (Studio test default is 1, live games default to 2); the pairing is the standard native idiom.
- **Instruction ceilings** (hit = Output window error, fix by splitting functions):
  - 64K instructions in a single code block (`exceeded single code block instruction limit`)
  - 32K internal blocks in one function (`exceeded function code block limit`)
  - 1M instructions per script (`exceeded total module instruction limit`)
  - A memory limit for natively compiled code, separate from the 1M instruction ceiling; the docs warn that a natively compiled module consuming near a million instructions "takes up a lot of memory and you may exceed the memory limit."
- **No official speedup number is published.** Roblox says only that it can improve execution speed for some server scripts. Never quote a benchmark ratio as official; measure with the Script Profiler (native functions are marked) and `debug.dumpcodesize()`.
- Deoptimizers that drop functions back to the interpreter: `getfenv`/`setfenv`, builtin calls with non-numeric arguments, and passing values that violate annotated parameter types. Annotate hot parameters (especially `Vector3`) so codegen can specialize.

## 15. Review checklist

- Syntax is Luau, not JavaScript, Python, or a different Lua version.
- Only `false` and `nil` are treated as falsy.
- Valid `false` values survive fallback logic.
- Sequences are contiguous when `#`, insertion, or removal relies on that shape.
- Dictionary behavior does not depend on iteration order.
- Table aliases and shallow copies are intentional.
- Dynamic keys use bracket syntax.
- Local declaration order and closure capture are correct.
- Method definition and call syntax agree.
- Multiple return values preserve success, absence, and error states.
- String patterns are Lua patterns, not unverified regex translations.
- Removed globals (`io`, `package`, `string.dump`, absent `os` members) are treated as sandbox design, not ported from Lua 5.1 assumptions.
- Deprecated APIs use their replacements; discouraged APIs are flagged with reasons, not called silently.
- Names follow the Roblox style guide: PascalCase types/publics, camelCase locals, `LOUD_SNAKE_CASE` constants (often written UPPER_SNAKE_CASE elsewhere), first-letter-only acronyms, spelled-out words.
- Engine behavior and project architecture are routed to their canonical skills.
