# Task 003: Write luau-mastery.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/luau-mastery.md`

## Description

Write a comprehensive Luau language reference covering the language features, type system, Roblox-specific patterns, and idiomatic code. This is the go-to reference when users ask general Luau questions.

## What To Do

Follow the standard reference structure:

1. **Overview** — When to load this reference (general Luau questions, syntax help, type system questions)
2. **Core Concepts** — Luau fundamentals: variables, functions, tables, control flow, string manipulation, math operations
3. **Type System** — Gradual typing, type annotations, generics, union types, type narrowing, type exports
4. **Roblox-Specific Patterns** — Instance creation (`Instance.new`), service access (`game:GetService`), event connections (`.Connected`, `:Connect`), property access, `task` library (task.spawn, task.wait, task.delay, task.defer)
5. **OOP Patterns** — Metatables for class-like objects, module-based classes with constructors, inheritance patterns, `self` usage
6. **Async Patterns** — Coroutines, Promises (if using Promise library), `task` library async patterns, pcall/xpcall for error handling
7. **Common Idioms** — Table manipulation (insert, remove, find, sort), string patterns, math helpers, Instance tree traversal
8. **Best Practices** — Naming conventions (PascalCase for classes, camelCase for variables), type annotations on public APIs, avoiding globals
9. **Anti-Patterns** — Using `wait()` instead of `task.wait()`, polling instead of events, global variables, string concatenation in loops (use table.concat)
10. **Sharp Edges** — Luau-specific gotchas (1-based indexing, table length operator `#` behavior with gaps, `nil` in tables)

Include production-ready Luau code examples throughout.

## Verification

- File exists at `references/luau-mastery.md`
- Contains all 10 sections listed above
- Code examples are syntactically valid Luau
- Covers type system with practical examples
- Includes both beginner and advanced content
