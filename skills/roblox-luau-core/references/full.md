# Luau Core Language: Full Reference

This reference covers the language. Roblox engine behavior belongs in the domain skills.

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

Missing arguments are `nil`; extra arguments can be ignored. A function that requires arity or non-nil inputs must validate or express that contract through types and call structure.

Loop variables in a numeric or generic `for` have iteration-local behavior. Variables mutated outside the loop are shared by closures. Capture the intended value in a new local when ownership is unclear.

### `const` bindings

<!-- temporal: 2026-03 -->
`const` was added in Luau 0.711 (March 2026) and is newer than most models' training cutoffs. Older tooling and lint stubs may reject it; the keyword is valid ([release notes](https://github.com/luau-lang/luau/releases/tag/0.711), [RFC](https://github.com/luau-lang/rfcs/blob/master/docs/const-keyword.md)).

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

## 8. Numeric behavior

Luau provides ordinary arithmetic, compound assignment such as `+=`, and floor division `//`. Be explicit around division by zero, negative values, clamping, and units.

`NaN` propagates through arithmetic and is unequal to everything including itself. Range guards written as `if v < min or v > max` silently accept NaN because both comparisons are false. Guard with `v ~= v`.

Floor division `//` truncates toward negative infinity (`-7 // 2 == -4`). `0/0` is NaN.

### buffer library

- Fixed-size binary data without table overhead: `buffer.create(size)`, then read/write typed values at offsets.
- Offsets are 0-based, sizes in bytes. Out-of-range access errors; the buffer does not grow.
- Reads/writes take explicit width and endianness (`readu8`/`readi16`/`readf32` family). No platform-dependent sizing.
- Do not use `buffer.readinteger`/`buffer.writeinteger`: they appear in some type definitions but are not in the released runtime.

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

## 10. Review checklist

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
- Engine behavior and project architecture are routed to their canonical skills.
