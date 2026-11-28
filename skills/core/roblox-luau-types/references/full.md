# Luau Type System: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## Decision Rules

- Use `--!strict` for new or actively maintained code
- Prefer inference-preserving designs over annotation-heavy designs when inferred shape stays precise
- Annotate where it clarifies intent, stabilizes contracts, constrains `self`, or prevents widening to `any`
- Prefer explicit exported aliases at module boundaries for stable contracts
- Use generics when input/output relationships matter; never replace with `any`
- Use tagged unions + refinements for multi-case structured values
- Casts (`::`) are a precision tool, not a bypass: narrow overly generic inference, don't hide errors

## Philosophy

The type system exists to **catch bugs at analysis time** without affecting runtime. The goal is not "annotate everything" but "let the type checker help you." Key principles:

1. **Inference first.** If the type checker already knows the type, don't annotate it. Redundant annotations add noise and can become stale.
2. **Annotate boundaries.** Function parameters, return types, and exported module surfaces benefit from explicit types. Internal locals usually don't.
3. **Preserve relationships.** A generic `<T>` that carries a type through a transform is more valuable than `any` that erases it.
4. **Narrow, don't cast.** Use `typeof()`, `IsA()`, and conditional checks to narrow types. Use `::` only when you genuinely know more than the checker.
5. **Sealed vs unsealed matters.** An explicitly annotated table is sealed (no new fields). An unannotated local table stays unsealed while it is being built; it seals on annotation, on being returned from a function, or when its declaring scope exits — not on being passed to a function.

## Strictness Modes

```luau
--!strict    -- Full type checking. Errors on unresolved types. Use for new code.
--!nonstrict -- Permissive checking for transitional code; project settings may select it.
--!nocheck   -- Disables type checking entirely. Only for generated code or legacy.
```

**Solver rollout:** Roblox began general release of the New Type Solver on November 20, 2025. Nocheck and nonstrict projects migrated automatically at that point, while existing strict projects remained opt-in. Roblox also documented strict-mode compatibility, performance, memory, and correctness issues. Check the current project's Scripting settings and file directives instead of assuming one universal solver or mode.

## Basic Type Annotations

```luau
-- Variable annotations
local name: string = "Alice"
local health: number = 100
local isAlive: boolean = true
local data: any = nil -- opt out of type checking

-- Function parameter and return types
local function add(a: number, b: number): number
    return a + b
end

-- Optional parameters
local function greet(name: string, title: string?): string
    if title then
        return `{title} {name}`
    end
    return name
end
```

## Table Types

```luau
-- Array type
local scores: { number } = { 100, 95, 87 }

-- Dictionary type (indexer)
local config: { [string]: boolean } = {
    shadows = true,
    particles = false,
}

-- Record type (concrete fields)
type PlayerData = {
    name: string,
    level: number,
    inventory: { string },
    stats: {
        health: number,
        mana: number,
    },
}
```

### Sealed vs Unsealed Tables

```luau
-- UNSEALED: unannotated local tables accumulate fields
local config = {}
config.debug = true    -- fine, table is unsealed
config.version = "1.0" -- fine, still accumulating

-- SEALED: once annotated or returned, no new fields allowed
local settings: { debug: boolean } = { debug = true }
settings.version = "1.0" -- ERROR: 'version' not in type

-- Practical implication: build tables fully before annotating
local data = {
    name = "Alice",
    level = 10,
}
-- data is unsealed here, you can still add fields
data.guild = "Warriors"

-- Passing it to a typed function does NOT seal it (width subtyping allows
-- extra properties at the call site); it seals on annotation, on return
-- from a function, or when its declaring scope exits.
```

### Indexer values that can be absent

Practitioner design informed by [Kampfkarren’s guidelines](https://raw.githubusercontent.com/Kampfkarren/kampfkarren-luau-guidelines/main/README.md), written independently. The same source informs static requires and literal-union guidance below; these are design recommendations, not universal style requirements.

Indexing a dictionary with a key that has no value returns `nil` at runtime, but an indexer typed `{ [K]: V }` presents every read as a plain `V` — the type checker never sees the `nil`, so a missing key slips through and errors at runtime. Whenever any key may be absent (per-player counters, caches, records read back from storage), type the value `V?` so the checker forces a nil check:

```luau
local points: { [Player]: number? } = {}

local function addPoints(player: Player, amount: number)
    local current = points[player]
    if current == nil then
        points[player] = amount
    else
        points[player] = current + amount
    end
end
```

With `{ [Player]: number }` instead, `current` reads as `number` and `current + amount` type-checks even though it errors for a player with no entry yet (verified with `luau-analyze` under `--!strict`, 2026-10). Reserve the non-optional indexer `{ [K]: V }` for tables where every key you will ever index is guaranteed present.

## Union and Intersection Types

```luau
-- Union type: value can be one of several types
local id: string | number = "abc123"
id = 42 -- also valid

-- Optional is shorthand for T | nil
local nickname: string? = nil -- equivalent to string | nil

-- Tagged unions for state machines (discriminated unions)
type Loading = { kind: "loading" }
type Ready<T> = { kind: "ready", value: T }
type Failed = { kind: "failed", message: string }
type State<T> = Loading | Ready<T> | Failed

local function readValue(state: State<number>): number?
    if state.kind == "ready" then
        return state.value -- narrowed to Ready<number>
    end
    return nil
end
```

## Type Narrowing and Guards

```luau
-- typeof narrows types (Roblox-aware, preferred over type())
local function process(value: string | number)
    if typeof(value) == "string" then
        -- value is narrowed to string here
        print(string.upper(value))
    else
        -- value is narrowed to number here
        print(value * 2)
    end
end

-- Instance type checking with :IsA()
local function handlePart(instance: Instance)
    if instance:IsA("BasePart") then
        -- instance is narrowed to BasePart
        instance.Anchored = true
        instance.BrickColor = BrickColor.new("Bright red")
    end
end

-- assert for non-nil narrowing
local function getPlayerData(player: Player): PlayerData
    local leaderstats = player:FindFirstChild("leaderstats")
    assert(leaderstats, "Player missing leaderstats")
    -- leaderstats is now narrowed to non-nil
    return parseStats(leaderstats)
end
```

### Refinements are claims about a place, and the fragile one is a table field

A refinement attaches to a specific storage location — a local binding or a table field expression — and survives only as long as no intervening code invalidates it. Reassigning a narrowed local kills its refinement immediately (verified: the use after `v = nil` is a type error under the current checker). What varies between solver versions is how aggressively field refinements (`t.value ~= nil`) are invalidated by writes through other paths; treating "any intervening call may have written the field" as true is the safe assumption even when the checker in front of you still accepts the code.

The robust idiom, for both reasons: copy the field to a local and narrow the local.

```luau
-- Fragile: refinement on t.value, and other code may write t.value
if t.value ~= nil then
    process(t.value)
end

-- Robust: the local cannot be written behind the checker's back,
-- and reassignment of the local is visible to the checker
local value = t.value
if value ~= nil then
    process(value)
end
```

Copy before logic that may call anything; a local copy is insulated from later replacement of the original field. A captured mutable local can still be rebound by a closure, and copying a table reference does not freeze its contents.

### Reading type errors: the report line is where types meet, not where the bug is

A type error is reported at the point where an incompatible value is *used or assigned*, but the wrong value was usually produced one or two hops upstream. Probed: a function whose body returns a string under a `number` return annotation is flagged at the `return` — the source — not at the downstream use. Follow the value back to where it was created instead of annotating the report line into silence.

Related, and equally verified: `any` at a boundary silences every check downstream. A function returning `any` can return a string, and every consumer — including `local n: number = get()` — type-checks cleanly while the bad value flows on. When you see a suspicious value that the checker "let through," look for an `any` between its origin and the failure point; fixing the annotation at that hop restores checking for everything after it.

## Generics

```luau
-- Generic function: preserves element type through transforms
local function first<T>(list: { T }): T?
    return list[1]
end

local name = first({ "Alice", "Bob" }) -- inferred as string?
local num = first({ 1, 2, 3 })         -- inferred as number?

-- Generic type alias
type Result<T> = {
    success: boolean,
    value: T?,
    error: string?,
}

-- Generic class-like pattern
type Stack<T> = {
    items: { T },
    push: (self: Stack<T>, value: T) -> (),
    pop: (self: Stack<T>) -> T?,
    peek: (self: Stack<T>) -> T?,
}
```

### When to Use Generics

- **Yes:** When a function transforms input and the output type depends on the input type
- **Yes:** When a container holds items of a specific type that callers should know about
- **Yes:** When you want to preserve type relationships across a chain of operations
- **No:** When the type is always the same (just use the concrete type)
- **No:** When you'd end up with `<any>` everywhere (you've lost the benefit)

## Type Exports

```luau
-- In a ModuleScript, export types for other modules to use
export type WeaponData = {
    name: string,
    damage: number,
    rarity: "Common" | "Rare" | "Epic" | "Legendary",
    durability: number,
}

-- Consumers import with require
local Types = require(game.ReplicatedStorage.Types)

local function createWeapon(name: string, damage: number): Types.WeaponData
    return {
        name = name,
        damage = damage,
        rarity = "Common",
        durability = 100,
    }
end
```

### Export Philosophy

- Export named aliases for every type that crosses a module boundary
- Keep implementation types internal (don't export helper types only used inside)
- Choose signatures that let callers infer types cleanly without needing to import the alias
- A well-typed module surface acts as documentation

### Static requires: the type information lives in the path

Keep `require` targets statically resolvable by the project’s analyzer. With Roblox-aware tooling and the correct sourcemap, a path such as `require(ReplicatedStorage.Packages.React)` lets the analyzer resolve module types. Computed loader paths can lose that information:

```luau
-- static: the checker resolves the module and all its exported types
local React = require(ReplicatedStorage.Packages.React)

-- dynamic: values become any (and error outright in strict mode)
local modules = {}
for _, moduleScript in Modules:GetChildren() do
    modules[moduleScript.Name] = require(moduleScript)
end
```

With the loop version, every value read out of `modules` is `any`: no autocomplete, no exported types, and any mistake in how a module is used surfaces at runtime instead of at analysis (verified with `luau-analyze` under `--!strict`, 2026-10: a `require` whose argument is not a static path reports "Unknown require: unsupported path"). If a module collection is genuinely needed, list the requires explicitly and build the registry from static requires — the few extra lines preserve the entire type chain.

The same rule protects the consumer side: when one module re-exports another, require the original statically and pass the value through, rather than re-requiring through a computed path.

### String-union enums: catch invalid values statically

For a game-owned closed vocabulary, a string-literal union makes invalid values detectable statically. A `never` assignment checks that all alternatives were handled. This does not replace Roblox engine enums or a project’s already well-typed representation:

```luau
type Phase = "lobby" | "running" | "intermission"

local function phaseLabel(phase: Phase): string
    if phase == "lobby" then
        return "Waiting"
    elseif phase == "running" then
        return "In progress"
    elseif phase == "intermission" then
        return "Between rounds"
    else
        local impossible: never = phase
        return impossible -- type error here if a Phase value was not matched above
    end
end
```

Adding another alternative, or removing the intermission branch, leaves a non-`never` value at the final assignment and produces a type error. Check this with the project’s analyzer and solver; the assignment deliberately turns an unhandled case into a static diagnostic.

Avoid an enum factory that erases literal information into `any` or broad `string` types. A typed table or existing library can also preserve useful static contracts; inspect its actual types rather than rejecting it by category. Runtime-extensible registries need a separate validation contract.

## Common Roblox Types

```luau
-- Instance hierarchy types
local part: Part = Instance.new("Part")
local player: Player = game.Players.LocalPlayer
local character: Model = player.Character or player.CharacterAdded:Wait()
local humanoid: Humanoid = character:FindFirstChildWhichIsA("Humanoid") :: Humanoid

-- Value types (NOT instances; value types / structs)
local position: Vector3 = Vector3.new(10, 5, 0)
local rotation: CFrame = CFrame.new(0, 10, 0) * CFrame.Angles(0, math.rad(90), 0)
local color: Color3 = Color3.fromRGB(255, 0, 0)
local udim2: UDim2 = UDim2.new(0.5, 0, 0.5, 0)

-- Enum types
local material: Enum.Material = Enum.Material.Grass
```

## Typing Object-Like Modules

```luau
--!strict

local Counter = {}
Counter.__index = Counter

type CounterData = { value: number }
export type Counter = typeof(setmetatable({} :: CounterData, Counter))

function Counter.new(initialValue: number): Counter
    return setmetatable({ value = initialValue }, Counter)
end

-- Explicit self annotation when : syntax doesn't infer precisely enough
function Counter.increment(self: Counter, amount: number): number
    self.value += amount
    return self.value
end

return Counter
```

### When to Use Explicit `self`

- When the type checker can't infer `self` precisely through `:` syntax
- When you need `self` to be a specific subtype in an inheritance chain
- When the method is defined with `.` but called with `:` (rare, avoid if possible)
- In type definitions (function signatures in type aliases always need explicit self)

## New Solver Type Features

<!-- temporal: 2026-09 -->
Everything in this section requires the **new type solver**. The old solver cannot resolve these constructs: do not delete them, rewrite them into old-solver idioms, or report them as missing in a project still running the old solver. Roblox generalized the new solver on November 20, 2025 (see Strictness Modes above): `nocheck`/`nonstrict` projects were migrated automatically, while strict projects stay on the old solver until they opt in. Opt in per experience with the Workspace property `UseNewLuauTypeSolver` (Scripting category, set to `Enabled`); the Studio beta-feature toggle was removed on January 7, 2026. The separate `LuauTypeCheckMode` property sets the default strictness mode, not the solver. Check which solver a project uses, or set the property explicitly, before editing these features.

### keyof and rawkeyof

Built-in type functions on table types. `keyof<T>` returns the keys of `T` as a union of singleton types; `rawkeyof<T>` ignores metatables.

```luau
local config = { health = 10, range = 20, team = "red" }
type ConfigKey = keyof<typeof(config)> -- "health" | "range" | "team"

local function read(key: ConfigKey) -- callers can only pass real keys
end
```

### setmetatable<T, M>

The new solver promotes `setmetatable` to a type constructor: `setmetatable<T, M>` builds the table type `T` carrying metatable `M`, without routing through `typeof(setmetatable(...))`.

```luau
local Mt = {}
Mt.__index = Mt

type Object = setmetatable<{ value: number }, { __index: typeof(Mt) }>

function Mt.new(value: number): Object
    return setmetatable({ value = value }, Mt)
end
```

The old-solver idiom `typeof(setmetatable({} :: T, Mt))` still works under the new solver; `setmetatable<T, M>` is the clearer form there. In old-solver projects keep the `typeof` idiom, because `setmetatable<T, M>` in type position does not resolve.

### User-defined type functions

Functions that run during analysis and compute a type from types. Declared with `type function`; called with angle brackets like built-ins.

```luau
type function keyofLike(ty: type)
    if not ty:is("table") then
        error("keyofLike expects a table type")
    end
    local union = nil
    for key in ty:properties() do
        union = if union then types.unionof(union, key) else key
    end
    return if union then union else types.singleton(nil)
end

type Keys = keyofLike<{ name: string, level: number }> -- "name" | "level"
```

- Runs at analysis time only: no runtime presence, no runtime cost, and no access to runtime functions or script locals.
- The environment is sandboxed and restricted: the `types` library (constructors and inspectors such as `types.unionof`, `types.singleton`, `types.newtable`, `tabletype:properties()`, `setreadproperty`/`readproperty`) plus `assert`, `error`, `print`, `next`, `ipairs`, `pairs`, `select`, `unpack`, `getmetatable`, `setmetatable`, `rawget`, `rawset`, `rawlen`, `raweq`, `tonumber`, `tostring`, `type`, `typeof`, and the `math`, `table`, `string`, `bit32`, `utf8`, and `buffer` libraries. Nothing else is available.
- `error()` inside a type function surfaces as a type error at the call site.
- Status: shipped upstream (luau.org/types/type-functions) and usable on Roblox under the new solver; Roblox staff have confirmed experiences can be published with them, but editor tooling inside type-function bodies is still maturing.

### read table members

The new solver tracks read and write types per property. Prefix a member with `read` to make it read-only:

```luau
local function describe(box: { read part: Instance })
    print(box.part.Name)
    -- box.part = Instance.new("Part") -- type error: read-only
end
```

Reads are allowed and writes are type errors, so callers can pass a narrower table (a `{ part: Part }` where `{ read part: Instance }` is expected). Functions defined with `function T.name()` syntax are inferred as read-only members. The read/write split is also visible to user-defined type functions: `ty:properties()` returns `{ [key]: { read: type?, write: type? } }`.

## Function Attributes

### @deprecated

Marks a named function or property as deprecated. The linter warns at every call site and the LSP shows the entry in a distinct style in autocomplete. Both optional string parameters customize the warning: `use` names the replacement, `reason` explains.

```luau
@deprecated local function oldApi()
end

@[deprecated { use = "newApi()", reason = "oldApi miscounts negative values" }]
local function olderApi()
end
```

| Form | Warning |
| --- | --- |
| `@deprecated` | `Function 'oldApi' is deprecated.` |
| `use = "newApi()"` | adds `use 'newApi()' instead.` |
| member function | `Member 'class.func' is deprecated` |

Attributes apply to functions only and are not user-definable. Status: documented upstream at luau.org/attributes and parsed by Studio since release 669; upstream release 0.668 fixed propagation to anonymous functions under the new solver. Treat actual Studio warning behavior as still settling; do not claim it errors or blocks anything.

### Native codegen (--!native / @native)

Roblox-only compiler feature: server-side scripts compile to machine code instead of bytecode. Covered in full in `roblox-luau-core`; the type-relevant facts:

- `--!native` at the top of a Script enables it for all functions in the script (top-level scope only if deemed profitable). `@native` above an individual function enables it per function.
- Enable `--!optimize 2` alongside: `--!native` benefits from aggressive optimization, and the pairing is the common performance idiom.
- Annotate hot parameters (`v: Vector3`, not `v`): codegen specializes on type annotations, and wrong or missing hints add runtime checks or drop the function back to the interpreter.
- Server scoping: documented for server-side scripts. Do not add `--!native` to client scripts expecting the same benefit.
- Roblox publishes no official speedup number; measure with the Script Profiler instead of claiming a ratio.

## Pitfalls reported on the DevForum (2026)

Each item below is labeled with how far it was checked. Items marked "local check" were reproduced with the standalone `luau-analyze` (2026-11; new solver by default, `--solver=old` for the old one), which can differ from the version shipped in Studio.

### A path that falls off the end returns nothing, not `nil`

Reported on the DevForum (2026-10-17, [thread](https://devforum.roblox.com/t/sudden-return-type-error/4939413/2)); local check: both solvers flag it. A function typed to return an optional value must say `return nil` on its empty path. Falling off the end returns zero values, and the checker reports `Not all codepaths in this function return '...'`.

```luau
--!strict
local function pickHandler(enabled: boolean): (() -> ())?
    if enabled then
        return function() end
    end
    return nil -- required: falling off the end is "no values"
end

return pickHandler
```

### A solver rollout can surface an error that was already there

Reported on the DevForum (2026-10-17, [thread](https://devforum.roblox.com/t/sudden-return-type-error/4939413/10)). A type error that appears "suddenly" in unchanged code can come from the solver switching, not from a runtime change: `Workspace.UseNewLuauTypeSolver` is a `RolloutState`, and its `Default` value follows the engine-wide rollout ([Workspace reference](https://create.roblox.com/docs/reference/engine/classes/Workspace)). Check which solver is active, then reduce the failure to a standalone snippet and test it under both solvers before treating it as a bug in your logic. Runtime behavior does not change with the solver.

### Array literals of strings may widen to `string`

Reported on the DevForum (2026-07-02 and 2026-07-06, [thread](https://devforum.roblox.com/t/how-to-make-array-return-a-union-type/4549941/33)). Local check: the old solver widens `{ "apple", "banana" }` to `{ string }`, so assigning an element to `"apple" | "banana"` fails. The standalone new solver accepted the same assignment. Don't rely on either: declare the union once and annotate the array with it, or assert each element as the thread suggests (`"apple" :: "apple"`). Pick one source of truth so the values aren't listed twice. A small fixed list like this needs no `type function`; reserve type functions for types derived from larger structures.

```luau
--!strict
export type Fruit = "apple" | "banana" | "cherry"

local FRUITS: { Fruit } = { "apple", "banana", "cherry" }

local function isFruit(value: string): boolean
    return table.find(FRUITS, value :: any) ~= nil
end

return { FRUITS = FRUITS, isFruit = isFruit }
```

### `self` through inherited `:` methods

Reported on the DevForum (2026-08-13, [thread](https://devforum.roblox.com/t/type-does-not-have-key-error-after-applying-table-inheritance/4808799/3)); open, not reproduced here. A method that type-checks alone can fail with "type does not have key" once metatable inheritance is added, because the checker may not resolve `self` through `:`-defined methods on the inherited table. Write the class with an explicit data type and an annotated `self` (see [Typing Object-Like Modules](#typing-object-like-modules)), or prefer composition. To report it, make a minimal strict-mode script that separates the method syntax from the inheritance.

## Common Mistakes

- Using `keyof`, `setmetatable<T, M>`, type functions, or `read` members in an old-solver project and "fixing" the resulting errors by deleting them; they need the new solver (`UseNewLuauTypeSolver`)
- Assuming upstream-only Luau features are live in the Roblox VM without checking deployment status

- Leaving variables unannotated in `--!nonstrict` → unintentional `any` propagation
- Replacing useful generic relationships with `any` or overly broad unions
- Sealing a table too early with an annotation, then expecting to add fields later
- Expecting `:` method definitions to automatically share precise `self` type across the class
- Leaving an optional-return function to fall off the end instead of `return nil`
- Using `::` to force unrelated conversions instead of fixing underlying type design
- Building unions without a discriminant, making downstream refinement difficult
- Indexer dictionaries typed `{ [K]: V }` while missing keys are indexed at runtime; type the value `V?` where absence is expected (see Table Types)
- Annotating untrusted remote/DataStore payloads as already validated, or casting `unknown` to the desired type without runtime checks. Accept `unknown`, validate and narrow it, then pass the checked value onward.
- Narrowing a table field and holding the refinement across calls that may write the field; copy the field to a local and narrow the local instead
- Using intersections between incompatible primitives (`string & number`)
- Annotating every local variable (noise that hides the important annotations)
- Exporting internal helper types that clutter the module's public surface
- Building enums with `makeEnum`-style libraries or lookup tables when a string-literal union would catch invalid values at analysis time

## Solver Migration Rules

- Never delete or "modernize away" new-solver syntax (`keyof`, `setmetatable<T, M>`, `type function`, `read` members) because a toolchain or collaborator reports it as unknown; see [New Solver Type Features](#new-solver-type-features) for the opt-in.
- Do not add new-solver syntax to a project that has not opted in; the old solver will reject or mangle it.

## Quality Checklist

- [ ] File has appropriate strictness mode (`--!strict` for maintained code)
- [ ] Function parameters and return types annotated at module boundaries
- [ ] Internal locals rely on inference where the inferred type is precise
- [ ] Generics preserve type relationships (no `any` escape hatches)
- [ ] Tagged unions have a discriminant field for narrowing
- [ ] Exported types are named, focused, and documented
- [ ] Casts (`::`) are justified (narrowing, not hiding errors)
- [ ] No sealed table violations (fields added after annotation)
- [ ] New-solver features are only used where the new solver is enabled
- [ ] Time-sensitive claims (solver rollout, attributes, Studio behavior) carry a `<!-- temporal: YYYY-MM -->` marker
