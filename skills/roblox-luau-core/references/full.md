# Luau Core Language


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## When to Load

Load this skill when the task involves:

- General Luau syntax, variables, operators, or control flow
- Table operations (arrays, dictionaries, iteration, manipulation)
- String patterns and string library usage
- Math operations and helpers
- Scope, closures, and variable lifetime
- Common idioms and their pitfalls
- Porting code from JavaScript/Python/other languages to Luau
- Understanding sharp edges (1-based indexing, nil semantics, truthiness)

**Hand off to other skills when:**

- Type annotations, generics, inference, strictness modes → `roblox-luau-types`
- OOP patterns, async/promises, module architecture, service patterns → `roblox-luau-patterns`
- Roblox engine APIs, services, networking, data storage → `roblox-*` domain skills

## Decision Rules

- Stay within pure Luau syntax, semantics, and standard library
- Treat Luau as Lua 5.1 + Luau extensions. Do NOT assume Lua 5.2+ features
- Prefer `local` variables and `local function` by default
- Keep control flow direct: `if`/`elseif`/`else`, loops, `break`, `continue` over clever boolean tricks
- Use Luau-specific syntax when it improves correctness/readability (if-expressions, compound assignment, generalized iteration)
- Prefer built-in library functions over handwritten helpers
- When unsure whether something is a language question or an engine question, answer only the pure Luau portion

## Key Rules

- Luau is NOT Lua 5.1. Has: generics, `continue`, `+=`, string interpolation (backticks), floor division `//`
- Arrays are 1-based. `#tbl` for length. Generalized iteration: `for k, v in tbl do`
- Always use `task.wait/spawn/delay` (never deprecated `wait/spawn/delay`)
- Prefer backtick interpolation over `..` concatenation
- Local function order: callees above callers (no hoisting). Forward-declare for mutual recursion.
- Only `nil` and `false` are falsy. `0`, `""`, and `{}` are truthy.

---

## Luau Extensions (not in Lua 5.1)

```luau
-- Compound assignment operators
score += 10
score -= 5
score *= 2

-- continue keyword (skips to next iteration)
for i = 1, 10 do
    if i % 2 == 0 then continue end
    print(i)
end

-- Generalized iteration (preferred over ipairs/pairs)
for index, item in items do print(index, item) end
for key, value in stats do print(key, value) end
```

## Tables

Tables are the only compound data structure. They serve as arrays, dictionaries, objects, and namespaces.

```luau
-- Dictionary (string keys)
-- NOTE: name = "Alice" is shorthand for ["name"] = "Alice".
-- Luau tables are NOT JSON objects. Keys are strings, not identifiers.
local player = {
    name = "Alice",
    health = 100,
    inventory = {},
}
print(player.name)       --> "Alice"
print(player["health"])  --> 100

-- Dynamic keys REQUIRE bracket notation
local fieldName = "health"
print(player[fieldName]) --> 100

-- Arrays are 1-based, NOT 0-based
local items = { "sword", "shield", "potion" }
print(items[1]) --> "sword"
print(#items)   --> 3 (length operator)
```

### Table Operations

```luau
-- table.insert: append to array
local queue = {}
table.insert(queue, "task1")
table.insert(queue, "task2")
-- queue = {"task1", "task2"}

-- table.insert at index: insert at position (shifts others right)
table.insert(queue, 1, "urgent")
-- queue = {"urgent", "task1", "task2"}

-- table.remove: remove by index (shifts others left), returns removed value
local removed = table.remove(queue, 1) --> "urgent"

-- table.remove without index removes last element
local last = table.remove(queue) --> "task2"

-- table.find: search for value in array (returns index or nil)
local fruits = { "apple", "banana", "cherry" }
local index = table.find(fruits, "banana") --> 2
local missing = table.find(fruits, "grape") --> nil

-- table.sort: in-place sort
local numbers = { 5, 3, 8, 1, 9 }
table.sort(numbers) -- ascending by default
-- numbers = {1, 3, 5, 8, 9}

-- Custom sort comparator
local players = {
    { name = "Alice", score = 150 },
    { name = "Bob", score = 200 },
    { name = "Charlie", score = 100 },
}
table.sort(players, function(a, b)
    return a.score > b.score -- descending by score
end)

-- table.concat: join array elements into string
local parts = { "Hello", "world", "!" }
print(table.concat(parts, " ")) --> "Hello world !"

-- table.freeze / table.isfrozen (Luau extension - immutable tables)
local CONFIG = table.freeze({
    MAX_PLAYERS = 50,
    ROUND_TIME = 300,
    MAP_SIZE = 500,
})
-- CONFIG.MAX_PLAYERS = 100 --> ERROR: attempt to modify a frozen table

-- table.clone (Luau extension - shallow copy)
local original = { 1, 2, 3, sub = { 4, 5 } }
local copy = table.clone(original)
copy[1] = 99
print(original[1]) --> 1 (not affected)
-- NOTE: sub-tables are still shared references (shallow copy)

-- table.move (copy elements between tables or within a table)
local src = { 10, 20, 30, 40, 50 }
local dst = {}
table.move(src, 2, 4, 1, dst) -- copy src[2..4] into dst starting at dst[1]
-- dst = {20, 30, 40}

-- table.clear (Luau extension - remove all keys, keep table reference)
local t = { 1, 2, 3 }
table.clear(t) -- t is now empty but same reference

-- Deep copy utility (not built-in - write your own)
local function deepCopy<T>(original: T): T
    if typeof(original) ~= "table" then
        return original
    end
    local copy = table.clone(original :: any)
    for key, value in copy do
        if typeof(value) == "table" then
            copy[key] = deepCopy(value)
        end
    end
    return copy :: T
end
```

## String Interpolation

```luau
-- ALWAYS prefer backtick interpolation over .. concatenation
local name = "Alice"
local level = 42
local message = `{name} reached level {level}!`

-- Expressions in interpolation
local price = 19.99
local tax = 0.08
print(`Total: ${price * (1 + tax)}`)

-- string.split (Luau extension)
local parts = string.split("a,b,c", ",")
```

## String Patterns

Luau uses **Lua patterns**, which are NOT regular expressions. They are simpler and more limited.

```luau
-- Character classes
-- %a  letters          %A  non-letters
-- %d  digits           %D  non-digits
-- %l  lowercase        %L  non-lowercase
-- %u  uppercase        %U  non-uppercase
-- %w  alphanumeric     %W  non-alphanumeric
-- %s  whitespace       %S  non-whitespace
-- %p  punctuation      %P  non-punctuation
-- .   any character
-- %%  literal %

-- Quantifiers
-- *   0 or more (greedy)
-- +   1 or more (greedy)
-- -   0 or more (lazy)
-- ?   0 or 1

-- string.match: extract matches
local year, month, day = string.match("2026-03-04", "(%d+)-(%d+)-(%d+)")
print(year, month, day) --> "2026" "03" "04"

-- string.gmatch: iterate over all matches
local text = "score=100, level=42, health=75"
for key, value in string.gmatch(text, "(%w+)=(%d+)") do
    print(key, value)
end

-- string.gsub: replace matches
local cleaned = string.gsub("Hello   World", "%s+", " ")
print(cleaned) --> "Hello World"

-- Escaping pattern characters: use % before special chars
-- Special chars: ( ) . % + - * ? [ ] ^ $
local escaped = string.gsub("file.txt", "%.", "_")
print(escaped) --> "file_txt"

-- Anchors
-- ^ matches start of string
-- $ matches end of string
local isEmail = string.match("user@example.com", "^%w+@%w+%.%w+$") ~= nil
```

## Luau-Specific Math Extensions

```luau
local intDiv = 10 // 3   --> 3 (floor division, Luau extension)
print(math.clamp(15, 0, 10))  --> 10 (Luau extension)
print(math.sign(-7))          --> -1 (Luau extension)
print(math.round(3.5))        --> 4 (Luau extension)

-- For better randomness, use Random.new()
local rng = Random.new()
print(rng:NextNumber())         --> [0, 1) float
print(rng:NextInteger(1, 100))  --> [1, 100] integer
```

### Math Helpers

```luau
-- Clamping values
local health = math.clamp(currentHealth, 0, MAX_HEALTH)

-- Linear interpolation
local function lerp(a: number, b: number, t: number): number
    return a + (b - a) * t
end

-- Mapping a value from one range to another
local function map(value: number, inMin: number, inMax: number, outMin: number, outMax: number): number
    return outMin + (outMax - outMin) * ((value - inMin) / (inMax - inMin))
end

-- Distance between two Vector3s
local distance = (posA - posB).Magnitude

-- Normalized direction
local direction = (target - origin).Unit

-- Rounding to decimal places
local function roundTo(value: number, places: number): number
    local factor = 10 ^ places
    return math.round(value * factor) / factor
end
print(roundTo(3.14159, 2)) --> 3.14
```

## Common Idioms

### Ternary with and/or

Luau has no ternary operator. Use `and`/`or` chains for single-value conditions:

```luau
-- Basic ternary: condition and truthy_value or falsy_value
local status = (health > 0 and "alive" or "dead")
local label = (isAdmin and "Admin" or "User")
local color = (isActive and Color3.new(0, 1, 0) or Color3.new(1, 0, 0))

-- With function calls
local displayName = (player.DisplayName ~= "" and player.DisplayName or player.Name)

-- Nested (use sparingly - readability drops fast)
local tier = (score >= 90 and "S" or score >= 70 and "A" or score >= 50 and "B" or "C")

-- CAVEAT: if the truthy value is nil or false, the expression breaks:
-- (condition and nil or "fallback") returns "fallback" even when condition is true
-- In that case, use a proper if/else block or Luau's if-expression:
local result = if condition then valueA else valueB
```

---

## Sharp Edges

### 1-Based Indexing

Luau arrays are 1-indexed. The first element is `array[1]`, not `array[0]`.

```luau
local items = { "first", "second", "third" }
print(items[1]) --> "first"
print(items[0]) --> nil (NOT an error, just nil)

-- Off-by-one errors are common when porting from other languages
for i = 1, #items do -- correct: 1 to length
    print(items[i])
end
```

### The `#` Operator and Nil Gaps

The `#` (length) operator is only reliable for **contiguous arrays** with no nil gaps.

```luau
-- Reliable: contiguous array
local a = { 1, 2, 3, 4, 5 }
print(#a) --> 5 (correct)

-- UNRELIABLE: array with nil gap
local b = { 1, 2, nil, 4, 5 }
print(#b) --> could be 2 or 5 (undefined behavior!)

-- The length operator finds ANY valid boundary where t[n] ~= nil and t[n+1] == nil
-- With gaps, multiple boundaries exist, and the result is unpredictable

-- SAFE: if you need to handle sparse data, use a dictionary with explicit count
local sparse: { [number]: string } = {}
local count = 0
sparse[1] = "a"
count += 1
sparse[5] = "e"
count += 1
-- Use count, not #sparse
```

### Nil in Tables

```luau
-- Setting a table value to nil REMOVES the key
local t = { a = 1, b = 2, c = 3 }
t.b = nil
-- t is now { a = 1, c = 3 } - "b" key no longer exists

-- This means you cannot store nil as a meaningful value in a table
-- Use a sentinel value instead if you need to distinguish "absent" from "nil"
local NONE = newproxy(false) -- unique sentinel
local cache = {}
cache["key"] = NONE -- means "we checked, value is absent"
-- cache["other"] is nil, meaning "we haven't checked yet"

-- nil in arrays causes gaps (see # operator issue above)
local list = { 1, 2, 3 }
list[2] = nil -- creates a gap - DO NOT DO THIS
-- Use table.remove(list, 2) instead to shift elements down
```

### Equality and Type Coercion

```luau
-- Luau does NOT coerce types in comparisons (unlike JavaScript)
print(0 == "0")    --> false
print(1 == true)   --> false
print("" == false) --> false

-- Only nil and false are falsy
-- 0, "", and empty tables are TRUTHY
if 0 then print("0 is truthy") end         --> prints
if "" then print("empty string is truthy") end --> prints
if {} then print("empty table is truthy") end  --> prints

-- This means you cannot use `if value then` to check for empty strings or zero
-- Be explicit:
if value ~= nil and value ~= "" then end
if value ~= nil and value ~= 0 then end
```

### Table Reference Semantics

```luau
-- Tables are passed and assigned by REFERENCE, not by value
local original = { 1, 2, 3 }
local alias = original
alias[1] = 99
print(original[1]) --> 99 (both point to the same table)

-- To get an independent copy, use table.clone (shallow) or a deep copy function
local copy = table.clone(original)
copy[1] = 0
print(original[1]) --> 99 (unaffected)

-- But nested tables are still shared in a shallow clone
local nested = { data = { 1, 2, 3 } }
local shallowCopy = table.clone(nested)
shallowCopy.data[1] = 99
print(nested.data[1]) --> 99 (shared reference!)
-- Use a deep copy for nested structures
```

### Scope and Closures

```luau
-- Common loop closure bug
local functions = {}
for i = 1, 5 do
    functions[i] = function()
        return i
    end
end
-- In Luau, each loop iteration creates a new 'i' variable,
-- so this actually works correctly (unlike some other languages)
print(functions[1]()) --> 1
print(functions[5]()) --> 5

-- But watch out with while loops - the variable is shared
local fns = {}
local i = 1
while i <= 5 do
    fns[i] = function()
        return i
    end
    i += 1
end
print(fns[1]()) --> 6 (all functions share the same 'i' which is now 6)

-- Fix: capture the value in a local
local fns2 = {}
local j = 1
while j <= 5 do
    local captured = j
    fns2[j] = function()
        return captured
    end
    j += 1
end
print(fns2[1]()) --> 1 (correct)
```

### Local Function Declaration Order

Luau has no hoisting - a `local function` is invisible to code above its declaration.

```luau
-- BAD: helperB is nil when functionA runs
local function functionA()
    helperB() -- ERROR: attempt to call a nil value
end

local function helperB()
    print("helper")
end

-- GOOD: callee declared before caller
local function helperB()
    print("helper")
end

local function functionA()
    helperB() -- works
end
```

For mutual recursion (A calls B, B calls A), use a forward declaration:

```luau
local functionB  -- forward declaration (declares variable, no assignment)

local function functionA(x: number)
    if x <= 0 then return end
    functionB(x - 1)
end

function functionB(x: number) -- no 'local' here (already declared above)
    if x <= 0 then return end
    functionA(x - 1)
end
```

**Rule:** Callees above callers, always. If a `local function` is called by code above its definition, that is a runtime nil-error bug.

### Metatables: Powerful but Error-Prone

```luau
-- Common mistake: forgetting __index
local MyClass = {}
-- Missing: MyClass.__index = MyClass

function MyClass.new()
    return setmetatable({}, MyClass)
end

function MyClass:doSomething()
    print("doing something")
end

local obj = MyClass.new()
obj:doSomething() --> ERROR: attempt to call a nil value
-- Because __index is not set, method lookup fails

-- Common mistake: modifying the metatable instead of the instance
function MyClass:setName(name: string)
    -- BAD: this sets it on the class table, shared by all instances!
    MyClass.name = name

    -- GOOD: set on the instance
    self.name = name
end
```

### Reserved Keywords as Identifiers

Luau reserves certain words for the language syntax. These cannot be used as identifiers:

```
and, break, do, else, elseif, end, false, for, function, if, in,
local, nil, not, or, repeat, return, then, true, until, while,
continue (Luau-specific)
```

```luau
-- BAD: keyword used as parameter name - syntax error
local function onComplete(return: number) end  -- ERROR
local function process(continue: boolean) end   -- ERROR

-- GOOD: renamed to avoid reserved keyword
local function onComplete(result: number) end
local function process(shouldContinue: boolean) end
```

---

## JS → Luau Translation Table

AI models trained on JavaScript commonly generate patterns that don't exist in Luau. This table covers the most frequent mistakes.

| JavaScript | Luau | Notes |
|------------|------|-------|
| `arr.map(fn)` | `table.create(#arr)` + for loop, or use a utility | No built-in map/filter/reduce on tables |
| `arr.filter(fn)` | Loop with `table.insert` into new table | No built-in filter |
| `arr.find(fn)` | Loop with early return | No built-in find |
| `arr.includes(x)` | `table.find(arr, x) ~= nil` | Returns index or nil |
| `arr.push(x)` | `table.insert(arr, x)` | |
| `arr.pop()` | `table.remove(arr)` | Removes and returns last element |
| `arr.splice(i, n)` | `table.remove(arr, i)` in a loop | No splice equivalent |
| `arr.length` or `arr.length` | `#arr` | `#` operator, not a property |
| `obj.keys(x)` | No direct equivalent - use `for k in x do` | |
| `obj.values(x)` | `for _, v in x do` | |
| `Object.assign(a, b)` | `for k, v in b do a[k] = v end` | No spread operator |
| `const x = ...` | `local x = ...` | No const/let/var |
| `let x = ...` | `local x = ...` | |
| `function(x) { return x }` | `function(x) return x end` | No arrow functions |
| `(x) => x * 2` | `function(x) return x * 2 end` | No arrow functions |
| `x === y` | `x == y` | No `===` in Luau, `==` is strict |
| `x !== y` | `x ~= y` | Not `!=` |
| `null` | `nil` | No null/undefined distinction |
| `typeof x` | `typeof(x)` for Roblox types, `type(x)` for Luau types | Parentheses required |
| `console.log(x)` | `print(x)` | |
| `x ?? y` | `x or y` | Luau `or` returns the value, not a boolean |
| `x?.y` | `x and x.y` | No optional chaining |
| `{...obj}` | Manual table copy with loop | No spread operator |
| `[...arr]` | Manual copy with loop or `table.move` | No spread operator |
| `new Map()` | Regular table `{}` | Luau tables are dictionaries by default |
| `new Set()` | `{[value] = true}` pattern | Use table as set |
| `Promise.all(arr)` | `Promise.all(arr)` | Same if using evaera/Promise |
| `async/await` | `coroutine` or Promise chains | No async/await syntax |
| `try/catch` | `pcall(fn)` or `xpcall(fn, handler)` | No try/catch |
| `throw error` | `error("message")` | |
| `class Foo { }` | `local Foo = {} Foo.__index = Foo` | Prototype-based OOP |
| `new Foo()` | `setmetatable({}, Foo)` | |
| `import x from "y"` | `local x = require(y)` | No ES modules |
| `export default` | `return module` | Module returns its public API |
| `str1 + str2` | `` `{str1}{str2}` `` | Use backtick interpolation, NOT `..` |
| `"hello " + name` | `` `hello {name}` `` | Backticks are the Luau way |

### Type-Specific Confusion

| JavaScript | Luau | Why AI Gets It Wrong |
|------------|------|---------------------|
| `0 == ""` → `true` | `0 == ""` → `false` | Luau has no type coercion in `==` |
| `"" == false` → `true` | `"" == false` → `false` | Only `nil` and `false` are falsy |
| `if (0)` → falsy | `if 0 then` → truthy | `0`, `""`, `{}` are all truthy in Luau |
| `x = null` → typeof `object` | `x = nil` → type `nil` | No null/undefined split |
| `Array.isArray(x)` | `type(x) == "table"` | No Array type distinction |
| `x.push()` on string | N/A - strings are not indexable | No string methods, use `string.*` library |

---

## Common Mistakes

- Treating `0` or `""` as falsy — only `false` and `nil` are falsy in Luau
- `a and b or c` ternary fails when `b` can be `false` or `nil`
- Assuming zero-based arrays — Luau arrays are one-based
- Mixing `:` and `.` syntax (defining with `:`, calling with `.`)
- Relying on dictionary iteration order
- Missing args become `nil`, extra args are silently ignored
- Using globals where locals/closures fit
- Overusing metatables for simple data containers
- Assuming `goto`, bitwise operators, or integer semantics exist in Luau
- Using `..` concatenation instead of backtick interpolation

## Quality Checklist

- [ ] Valid Luau syntax (not Lua 5.2+, not JavaScript)
- [ ] All variables declared with `local`
- [ ] Simplest correct control-flow construct used
- [ ] Tables used intentionally (array vs dictionary vs metatable-backed)
- [ ] Iteration matches data shape (generalized `for k, v in tbl do`)
- [ ] Standard library preferred over custom helpers
- [ ] String building uses backtick interpolation
- [ ] No nil gaps in arrays
- [ ] Callees declared above callers
- [ ] No reserved keywords used as identifiers
