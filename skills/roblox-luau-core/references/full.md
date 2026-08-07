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

```luau
local bounded = math.clamp(value, minimum, maximum)
local whole = numerator // denominator
```

Floating-point equality is often the wrong test for derived values. Use a tolerance selected from the domain, not one universal epsilon.

Do not normalize a zero-length vector without deciding the fallback direction. Roblox datatype math belongs in the relevant camera, physics, or building skill.

## 9. Cross-language translation traps

### JavaScript to Luau

- `===` becomes `==`; `!==` becomes `~=`.
- `null` and `undefined` do not map to two separate values; Luau uses `nil`.
- Arrow functions, optional chaining, nullish coalescing, spread syntax, and `const`/`let` are not Luau syntax.
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
- `getfenv`, `setfenv`, `loadstring`, and similar legacy markers are review prompts; check the supported Luau behavior and the containing code's purpose instead of treating a token as a verdict.
- Engine behavior and project architecture are routed to their canonical skills.
