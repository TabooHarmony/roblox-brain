# roblox sharp edges: full reference

This is a pre-ship review list. The examples are intentionally small; they show the failure boundary, not a full framework.

## 1. Mutable data needs one owner

A player can move between servers while the old server is still saving. Without session ownership, the last writer wins and progress can disappear. Use a well-understood profile wrapper or implement a lock, heartbeat, release, and stale-owner policy together. Do not mix raw writes with a wrapper that already owns the profile.

## 2. Client values are proposals

A client can fire a remote without clicking the expected button. It can also change every local value. Never accept client-supplied currency, damage, price, ownership, or reward as fact. Recompute the result from server state and trusted definitions.

## 3. Receipts must be repeat-safe

Developer product processing can be retried. The grant operation must be idempotent, and the receipt should be acknowledged only after the server has recorded the grant successfully. If the player is unavailable or the write fails, return the not-yet-processed decision so Roblox can retry.

```luau
MarketplaceService.ProcessReceipt = function(receipt)
    local receiptKey = tostring(receipt.PurchaseId)
    if ReceiptStore:Has(receiptKey) then
        return Enum.ProductPurchaseDecision.PurchaseGranted
    end

    local player = Players:GetPlayerByUserId(receipt.PlayerId)
    if not player then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local ok = GrantService:GrantProduct(player, receipt.ProductId, receiptKey)
    if not ok then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end
    return Enum.ProductPurchaseDecision.PurchaseGranted
end
```

The store and grant service in this example are project-owned abstractions. Do not install a second receipt callback in another script.

## 4. Connections have owners

Every `Connect` should have a lifetime. A player connection belongs to that player; a round connection belongs to the round; a UI connection belongs to the screen. Disconnect explicitly or destroy an owning instance that reliably cleans up its descendants.

```luau
local connections = {}
connections[#connections + 1] = player.CharacterAdded:Connect(onCharacter)
connections[#connections + 1] = remote.OnServerEvent:Connect(onRequest)

local function cleanup()
    for _, connection in connections do
        connection:Disconnect()
    end
    table.clear(connections)
end
```

Do not keep player keys in tables after `PlayerRemoving`. Weak tables can help with auxiliary caches, but they are not a substitute for lifecycle cleanup.

## 5. Rate limits do not replace validation

- Reject NaN and infinity before range checks. A comparison-only guard can accept NaN because both `<` and `>` return false.

A cooldown prevents a flood from consuming unlimited work. It does not make an invalid request valid. Apply both a request budget and domain checks. For expensive operations, queue or reject work before creating instances or making service calls.

## 6. Shutdown is a deadline

`BindToClose` is not an unlimited maintenance window. Track pending saves, cap retries, and avoid starting new gameplay work during shutdown. A server that waits forever is no safer than one that exits immediately.

## 7. Scale before detail

Large decorative models, particle rates, shadows, and per-frame loops multiply across players and devices. Profile a representative scene on a low-end target. Prefer streaming, batching, pooling, and event-driven updates over a large fixed object budget.

## 8. Module loading can yield

A module that waits for instances or starts work at top level makes every caller wait. Keep module loading declarative. Move connections and loops to an explicit `Init` or `Start` phase. This also makes circular dependencies easier to detect.

## 9. Table length is not a count with holes

The `#` operator is not a reliable count for a table with missing numeric keys. If a collection can contain holes, maintain an explicit count or iterate with `pairs` and count what you need. Do not remove an array entry by assigning `nil` when order matters; use `table.remove` or a deliberate swap-delete operation.

## 10. Use the task scheduler APIs

For new code, use `task.wait`, `task.defer`, and `task.spawn` instead of the older global scheduling functions. Still keep ownership and cancellation in mind: spawning work does not make it safe to outlive its player or round.

## 11. Bound instance waits

An unconditional `WaitForChild` can hang a boot path forever when content is missing. Use a timeout at trust boundaries and report the missing dependency with enough context to fix it.

```luau
local folder = ReplicatedStorage:WaitForChild("Shared", 10)
if not folder then
    error("Shared folder was not replicated before startup deadline")
end
```

Do not put arbitrary short timeouts on dependencies that legitimately load later. Decide whether the caller should wait, retry, or fail closed.

## 12. Luau patterns are not regular expressions

Luau string patterns use `%d`, `%a`, and `.-` for common cases. They do not implement the full regular-expression syntax used by JavaScript or PCRE. Test the pattern against both valid and invalid inputs, and prefer explicit parsing for security-sensitive formats.

## 13. Declaration order matters

A local function is not hoisted like a function declaration in some other languages. Define a local function before code that calls it, or forward-declare the variable and assign the function later.

```luau
local step: () -> ()

local function run()
    step()
end

step = function()
    print("step")
end
```

## Pre-ship questions

- Can a client create value without the server checking it?
- Can two servers write the same mutable profile?
- Can a receipt be retried without a duplicate grant?
- Does every connection and task have an owner lifetime?
- Can a missing instance or service make startup hang forever?
- Does shutdown finish within a bounded deadline?
- Have high-volume effects been profiled on a representative low-end device?
