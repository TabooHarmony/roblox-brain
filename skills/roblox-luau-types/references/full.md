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
5. **Sealed vs unsealed matters.** An annotated table is sealed (no new fields). An unannotated local table accumulates fields until it leaves scope or gets returned.

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

-- But once you pass it to a typed function or return it, it seals
```

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

## Common Mistakes

- Using `keyof`, `setmetatable<T, M>`, type functions, or `read` members in an old-solver project and "fixing" the resulting errors by deleting them; they need the new solver (`UseNewLuauTypeSolver`)
- Assuming upstream-only Luau features are live in the Roblox VM without checking deployment status

- Leaving variables unannotated in `--!nonstrict` → unintentional `any` propagation
- Replacing useful generic relationships with `any` or overly broad unions
- Sealing a table too early with an annotation, then expecting to add fields later
- Expecting `:` method definitions to automatically share precise `self` type across the class
- Using `::` to force unrelated conversions instead of fixing underlying type design
- Building unions without a discriminant, making downstream refinement difficult
- Using intersections between incompatible primitives (`string & number`)
- Annotating every local variable (noise that hides the important annotations)
- Exporting internal helper types that clutter the module's public surface

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
