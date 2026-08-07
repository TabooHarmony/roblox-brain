# Roblox Architecture: Full Reference

Architecture is the ownership and dependency model that makes changes safe. Folders and class names are evidence of that model only when they clarify a real boundary.

## 1. Define the feature before the hierarchy

For a behavior, answer:

1. Which state is authoritative?
2. Which code may mutate it?
3. Which operations are public, and who calls them?
4. Which instances, connections, tasks, and cached values does it own?
5. Does it cross a client/server, persistence, purchase, or external-service boundary?
6. When does it start, and how does it stop?

If those answers fit in one small module or script, keep them there. A service/controller pair is not automatically more architectural than two scripts. Add boundaries because ownership differs, not because a template has folders to fill.

## 2. Runtime location is a trust and execution decision

| Location | Typical role | Important consequence |
| --- | --- | --- |
| `ServerScriptService` | server rules and orchestration | not replicated to clients |
| `ServerStorage` | server-only templates and assets | unavailable to clients |
| `ReplicatedStorage` | shared definitions, modules, and remotes | readable by clients |
| `StarterPlayerScripts` | per-player client behavior | cloned and run for each player |
| `StarterGui` | UI templates | cloned into each player's GUI |
| `Workspace` | live world instances | replicated according to engine behavior |

Replicated code is not a secret store. Do not put credentials, private reward logic, hidden detection thresholds, or authoritative mutable state in replicated locations and assume clients cannot inspect it.

A shared module may hold types, immutable identifiers, pure calculations, or presentation-safe configuration. The server still owns decisions that grant value, change persistent state, charge a purchase, or affect other players.

## 3. Prefer feature cohesion over ceremonial layers

A small feature can keep related code together while respecting runtime boundaries:

```text
ReplicatedStorage/Features/Inventory/
├── Types.luau
└── Remotes/
ServerScriptService/Features/Inventory/
├── Inventory.luau
└── Inventory.server.luau
StarterPlayer/StarterPlayerScripts/Features/Inventory/
├── InventoryView.luau
└── Inventory.client.luau
```

This is an example, not a required tree. A flat layout is better when the project is small. A top-level server/shared/client layout is better when that is already consistent. Do not reorganize a working repository solely to match this specimen.

The important properties are:

- one obvious server owner for authoritative mutation;
- client code owns input and presentation, not grants;
- shared code is safe to replicate;
- one feature change does not require hunting through unrelated generic manager folders.

## 4. Module contracts

A useful module contract states its owned state, public operations, caller side, failure modes, and lifecycle.

```luau
local Inventory = {}
local quantities: {[Player]: {[string]: number}} = {}

function Inventory.getCount(player: Player, itemId: string): number
    local playerItems = quantities[player]
    return if playerItems then playerItems[itemId] or 0 else 0
end

function Inventory.remove(player: Player, itemId: string, amount: number): boolean
    if amount < 1 then
        return false
    end
    local playerItems = quantities[player]
    local current = if playerItems then playerItems[itemId] else nil
    if current == nil or current < amount then
        return false
    end
    playerItems[itemId] = current - amount
    return true
end

function Inventory.release(player: Player)
    quantities[player] = nil
end

return Inventory
```

This does not need a class, dependency container, base service, or lifecycle interface. Add one only when repeated concrete behavior pays for it.

Keep top-level module code cheap and non-yielding. Hidden work during `require` makes ordering, failure, and cycles hard to diagnose. Circular requires indicate ownership or dependency direction is unclear; do not solve them with delayed globals.

## 5. Dependency direction

Use a direct module call when one owner needs a stable operation from another. The dependency remains visible and searchable.

Use a signal when:

- the publisher should not know independent observers;
- zero, one, or several observers are legitimate;
- delayed notification is acceptable;
- the signal has an owner and cleanup contract.

Do not introduce a global event bus merely to erase dependency arrows. It replaces compile-time/searchable relationships with string names, runtime ordering, and hidden consumers.

Avoid bidirectional feature dependencies. Move a narrow pure contract downward, let one side own orchestration, or emit an event from the authoritative owner. Shared folders should not become dumping grounds for anything imported twice.

## 6. Startup only when startup exists

Many modules need no initialization. Requiring them and calling their operations is enough.

When startup order matters, one small bootstrap should make it explicit:

```luau
local DataOwner = require(script.Parent.DataOwner)
local Match = require(script.Parent.Match)

local ok, problem = DataOwner.start()
if not ok then
    error(`Data startup failed: {problem}`)
end

Match.start(DataOwner)
```

Sequential calls preserve order and surface failure. Do not wrap every `Start` in `task.spawn`; that discards ordering and creates unowned background failures. Run independent startup concurrently only when independence is proven and failures are still collected.

Avoid universal two-phase `Init`/`Start` contracts. They add ceremony and can leave modules half-initialized. If phases are necessary, state exactly what each phase guarantees, validate dependency availability, and prevent public operations before readiness.

Top-level scripts can wire small features directly. A framework is not required to make startup explicit.

If a client dependency arrives through replication, use a bounded
`WaitForChild` and handle timeout explicitly. An unbounded wait converts a
missing instance or placement mistake into a silent startup hang.

## 7. Client/server APIs

A client request is untrusted input, not a command. The server validates the request against current server-owned state before side effects.

For each client-to-server remote, define:

- payload types and size limits;
- finite number and range checks;
- current-state preconditions;
- player ownership or permission;
- replay and duplicate semantics;
- abusive-frequency controls based on operation cost;
- success, denial, timeout, and reconciliation behavior.

Client prediction may improve responsiveness, but it must reconcile with the authoritative result. Never accept client-supplied damage, price, ownership, reward, inventory, or privileged destination as truth.

Load `roblox-networking` and `roblox-security` for executable patterns. Load `roblox-monetization` for purchase ownership and `roblox-data` for persistence ownership.

## 8. One canonical side-effect owner

Some operations tolerate only one owner:

- profile load, save, migration, and session release;
- purchase receipt processing and durable grants;
- authoritative currency or inventory mutation;
- cross-server message deduplication;
- external webhook side effects.

Feature modules may request these operations. They should not each implement their own save loop, receipt callback, retry policy, or shutdown handler. Duplicate owners create overwrite races and ambiguous recovery.

Player removal is a signal, not a universal persistence architecture. The canonical data owner defines leave, crash, teleport, and shutdown behavior. Other features release only the memory and resources they own.

## 9. Split and merge criteria

Split a module when at least one is true:

- authority changes, such as client presentation versus server decision;
- state has a separate lifecycle or persistence contract;
- a pure calculation can be tested without Roblox wiring;
- dependencies and reasons to change are genuinely unrelated;
- resource ownership becomes clearer after the split.

Merge or delete a boundary when:

- it only forwards calls without policy or translation;
- its name is generic but its state belongs to one feature;
- an interface has one implementation and no independent contract;
- two modules mutate the same state;
- boilerplate exceeds the behavior it protects.

Do not build speculative plugin systems or factories for one implementation.

## 10. Architecture review

Check the real call and data flow, not just folder names.

- Every authoritative state mutation has one canonical owner.
- Shared code and instances are safe for clients to read.
- Runtime location matches execution and trust requirements.
- Public module APIs are narrow and failure behavior is explicit.
- No circular require, hidden top-level yield, or accidental concurrent startup.
- Direct dependencies remain visible; signals have a real decoupling reason.
- Connections, tasks, instances, and player-keyed caches have cleanup owners.
- Persistence and purchase callbacks are not duplicated across features.
- Tests can isolate pure behavior where doing so is useful.
- No service/controller/manager/framework layer exists only for symmetry.
- The structure is the smallest one that a new contributor can trace end to end.

## 11. Learn from noisy RBXMs without cargo-culting

A Roblox model or place is evidence, not an authority. A large file, a name such as `Best`, `Working`, or `Template`, or a claim that it came from a successful game does not establish that its architecture is good.

When using a corpus of `.rbxm` or `.rbxl` files:

1. Preserve the original archive and record hashes before changing anything.
2. Parse instances and script source statically. Never execute source from an untrusted model during analysis.
3. Deduplicate exact files and near-identical variants before counting patterns.
4. Route artifacts into separate high-signal, component, review, and quarantine sets. Quarantine is a copy-safety decision, not proof of malware or uselessness, and it must not silently exclude artifacts from pattern study: shipped, successful games routinely trigger risk signals through anti-exploit tooling. Study quarantined code for structure while keeping it out of anything copied.
5. Infer a pattern only when it recurs across independent artifacts and survives a code-quality review. Rich trees and lots of code are signals for study, not quality labels.
6. Extract the abstraction, boundary, invariant, and failure behavior. Do not copy source, asset IDs, hidden loaders, or project-specific names into a new game.
7. Test the resulting guidance against a held-out project and the relevant runtime requirements. Static files contain no retention, conversion, crash, or live performance evidence.

Useful recurring structures to inspect are feature ownership, explicit server/client boundaries, narrow remote contracts, canonical persistence owners, layout-driven UI, and cleanup ownership. Treat dynamic code, numeric asset requires, obfuscation-like code, duplicate variants, and self-described unfinished files as review triggers.
