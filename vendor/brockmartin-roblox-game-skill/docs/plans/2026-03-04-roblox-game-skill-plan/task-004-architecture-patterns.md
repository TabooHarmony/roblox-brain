# Task 004: Write architecture-patterns.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/architecture-patterns.md`

## Description

Write a comprehensive reference for Roblox game architecture — how to structure games, organize scripts, use services, and implement client-server communication patterns.

## What To Do

1. **Overview** — When to load this reference (starting a new game, organizing code, architecture questions)
2. **Core Concepts** — The Roblox data model, client vs server execution, replication model
3. **Service Hierarchy** — What each service is for (ServerScriptService, ServerStorage, ReplicatedStorage, ReplicatedFirst, StarterGui, StarterPlayer, StarterPack, Workspace) with clear rules on what goes where and why
4. **Script Types and Placement** — Script (server), LocalScript (client), ModuleScript (shared), placement rules for each
5. **Client-Server Communication** — RemoteEvents (one-way async), RemoteFunctions (two-way sync), BindableEvents (same-side), when to use each, folder organization for remotes
6. **Module Script Architecture** — Structuring game logic into reusable modules, require patterns, avoiding circular dependencies, lazy loading
7. **Framework Patterns** — Knit-style Services (server) + Controllers (client), Single Script Architecture (SSA), pros/cons of each
8. **Folder Organization Conventions** — Standard folder layouts for small/medium/large games, naming conventions
9. **Best Practices** — Separation of concerns, single responsibility modules, minimal cross-module coupling
10. **Anti-Patterns** — God scripts, circular requires, putting server logic in ReplicatedStorage, using Workspace for script storage

Include Luau code examples for each communication pattern and architecture style.

## Verification

- File exists at `references/architecture-patterns.md`
- Covers all Roblox services with clear "what goes here" guidance
- RemoteEvent/RemoteFunction patterns include security considerations
- At least 2 architecture patterns (Knit-style, SSA) with pros/cons
- Code examples demonstrate proper module structure
