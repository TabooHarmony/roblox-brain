# Luau Type System — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## Decision Rules

- Use `--!strict` for new or actively maintained code
- Prefer inference-preserving designs over annotation-heavy designs when inferred shape stays precise
- Annotate where it clarifies intent, stabilizes contracts, constrains `self`, or prevents widening to `any`
- Prefer explicit exported aliases at module boundaries for stable contracts
- Use generics when input/output relationships matter; never replace with `any`
- Use tagged unions + refinements for multi-case structured values
- Casts (`::`) are a precision tool, not a bypass — narrow overly generic inference, don't hide errors

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
--!nonstrict -- Default mode. Warns but allows unresolved types. Good for transitional code.
--!nocheck   -- Disables type checking entirely. Only for generated code or legacy.
```

**2025-2026 Update:** The New Type Solver (GA Nov 2025) is faster and more accurate. `--!nonstrict` is now the default for all scripts. Prefer `--!strict` for anything you actively maintain.

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

-- Value types (NOT instances — value types / structs)
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

## Common Mistakes

- Leaving variables unannotated in `--!nonstrict` → unintentional `any` propagation
- Replacing useful generic relationships with `any` or overly broad unions
- Sealing a table too early with an annotation, then expecting to add fields later
- Expecting `:` method definitions to automatically share precise `self` type across the class
- Using `::` to force unrelated conversions instead of fixing underlying type design
- Building unions without a discriminant, making downstream refinement difficult
- Using intersections between incompatible primitives (`string & number`)
- Annotating every local variable (noise that hides the important annotations)
- Exporting internal helper types that clutter the module's public surface

## Quality Checklist

- [ ] File has appropriate strictness mode (`--!strict` for maintained code)
- [ ] Function parameters and return types annotated at module boundaries
- [ ] Internal locals rely on inference where the inferred type is precise
- [ ] Generics preserve type relationships (no `any` escape hatches)
- [ ] Tagged unions have a discriminant field for narrowing
- [ ] Exported types are named, focused, and documented
- [ ] Casts (`::`) are justified (narrowing, not hiding errors)
- [ ] No sealed table violations (fields added after annotation)
