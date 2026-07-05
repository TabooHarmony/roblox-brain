# Publish Checklist

A comprehensive pre-publish checklist for Roblox games. Work through each category before making the game public or pushing a major update.

---

## Data and Persistence

- [ ] **DataStore tested end-to-end** — Save, load, and verify player data across multiple play sessions. Test with both new and returning players.
- [ ] **Session locking implemented** — Prevent data corruption when a player is in multiple servers simultaneously. Use a session lock key in DataStore that is claimed on join and released on leave.
- [ ] **BindToClose handler** — `game:BindToClose()` saves all active player data before the server shuts down. Test by stopping a local server and verifying data persists.
- [ ] **DataStore error handling** — All `:GetAsync()`, `:SetAsync()`, and `:UpdateAsync()` calls are wrapped in `pcall` with retry logic and fallback behavior.
- [ ] **Data versioning** — Player data has a version number so future schema changes can migrate old data gracefully.
- [ ] **DataStore budget awareness** — Requests stay within Roblox DataStore request limits (60 + numPlayers * 10 per minute for GetAsync). No tight-loop saves.
- [ ] **OrderedDataStore for leaderboards** — If the game has leaderboards, they use OrderedDataStore and update at reasonable intervals (not every frame).
- [ ] **Backup/recovery plan** — A strategy exists for recovering player data if corruption occurs (e.g., DataStore versioning, external backups).

---

## Security

- [ ] **All remotes validated** — Every `OnServerEvent` and `OnServerInvoke` handler type-checks, range-validates, and authorizes all arguments. See the Security Audit workflow for details.
- [ ] **No exposed sensitive data** — ReplicatedStorage contains no server secrets, admin keys, or exploitable configuration. Sensitive modules live in ServerStorage or ServerScriptService.
- [ ] **Rate limiting on all remotes** — Per-player cooldowns prevent spam-firing of RemoteEvents and RemoteFunctions.
- [ ] **Server-authoritative game logic** — Currency, damage, inventory, and progression are computed on the server. The client sends intent, not results.
- [ ] **Anti-exploit measures** — Speed checks, teleport validation, and/or server-side hit detection are in place for competitive games.
- [ ] **No client-side ModuleScripts with server logic** — Modules in ReplicatedStorage or StarterPlayer do not contain logic that should be server-only.

---

## Performance

- [ ] **Mobile tested** — The game runs at 30+ FPS on a mid-range mobile device (or mobile is explicitly unsupported with device restrictions set).
- [ ] **Part count reviewed** — Total workspace BasePart count is within acceptable range for the genre. StreamingEnabled is configured if part count exceeds 10,000.
- [ ] **No memory leaks** — Event connections are disconnected when no longer needed. Per-player data is cleaned up on `PlayerRemoving`. Temporary instances are destroyed.
- [ ] **StreamingEnabled configured** — If the game has a large map, StreamingEnabled is turned on with appropriate `StreamingMinRadius` and `StreamingTargetRadius` values.
- [ ] **No deprecated API usage** — `wait()`, `spawn()`, and `delay()` are replaced with `task.wait()`, `task.spawn()`, and `task.delay()`.
- [ ] **Service calls cached** — `game:GetService()` is called once per script at the top level and stored in a local variable.
- [ ] **Network traffic reasonable** — RemoteEvents do not fire every frame. Payload sizes are minimal. `FireAllClients` is used only when all clients need the data.
- [ ] **MicroProfiler reviewed** — No single frame spike exceeds 16ms (60 FPS target) or 33ms (30 FPS target) during normal gameplay.

---

## Monetization

- [ ] **GamePasses functional** — All GamePasses can be purchased, and the benefits are granted correctly. Test with `:UserOwnsGamePassAsync()`.
- [ ] **ProcessReceipt correct** — `MarketplaceService.ProcessReceipt` is implemented, handles all Developer Products, returns `Enum.ProductPurchaseDecision.PurchaseGranted` only after the item is successfully granted, and persists the grant to DataStore before acknowledging.
- [ ] **Prices reviewed** — GamePass and DevProduct prices are reasonable for the value provided and competitive within the genre.
- [ ] **Purchase prompts work** — `MarketplaceService:PromptGamePassPurchase()` and `MarketplaceService:PromptProductPurchase()` are tested in a live (non-Studio) environment.
- [ ] **Premium benefits active** — If the game supports Roblox Premium, `Players.PlayerMembershipChanged` is handled and benefits are granted/revoked correctly.
- [ ] **No purchase-blocking bugs** — Players can purchase at any point in the game flow without errors, UI conflicts, or lost items.

---

## Mobile

- [ ] **Touch controls implemented** — All core interactions work with touch input. No interactions require hover or right-click.
- [ ] **Scale-based UI** — All UI uses `UDim2` with Scale values (not Offset) for positioning and sizing, or uses `UIAspectRatioConstraint` and `UISizeConstraint` for consistent layouts across screen sizes.
- [ ] **ContextActionService for input** — Mobile-specific input is handled through `ContextActionService` with proper touch buttons, not `UserInputService` keyboard bindings.
- [ ] **Safe area respected** — UI elements do not overlap with the Roblox top bar, chat, or device notch/home indicator areas.
- [ ] **Text is readable** — Font sizes are large enough to read on a phone screen (minimum 14pt equivalent).
- [ ] **Buttons are tappable** — Interactive UI elements are at least 44x44 pixels on mobile for comfortable touch targets.
- [ ] **Performance on mobile** — Game runs smoothly on lower-end mobile devices. Graphics quality scales appropriately.

---

## Gameplay

- [ ] **Core loop tested** — The primary gameplay loop (what players do repeatedly) works from start to finish without errors.
- [ ] **Edge cases handled** — Player death during transactions, disconnection during saves, empty inventories, maximum stack sizes, and similar edge cases are tested.
- [ ] **First-Time User Experience (FTUE) works** — A brand new player can understand the game within the first 2 minutes. Tutorial, onboarding, or intuitive design guides them.
- [ ] **Progression tested** — Early game, mid game, and late game progression work. Players do not get stuck or hit dead ends.
- [ ] **Multiplayer tested** — If multiplayer, test with 2+ players. Verify interactions, shared state, and competitive/cooperative mechanics work correctly.
- [ ] **Error recovery** — If a script errors during gameplay, the player experience degrades gracefully rather than breaking entirely.
- [ ] **AFK handling** — Players who go AFK do not break the game for others or accumulate unfair advantages.
- [ ] **Respawn works** — Character respawn is clean with no lingering state from the previous life (tools, effects, connections).

---

## Metadata

- [ ] **Game icon** — 512x512 pixel icon uploaded. Clear, recognizable, and representative of the game at small sizes.
- [ ] **Thumbnails** — At least 3 thumbnails or a video thumbnail that showcase the best parts of the game.
- [ ] **Description** — Clear, compelling description that explains what the game is, what players do, and why it is fun. Include relevant keywords for search.
- [ ] **Genre set** — Correct genre selected in Game Settings (Adventure, RPG, Simulator, etc.).
- [ ] **Max players configured** — `Players.MaxPlayers` is set appropriately for the game design and server capacity.
- [ ] **Allowed devices** — Playable devices are set correctly. If the game does not support mobile or console, restrict access rather than providing a broken experience.
- [ ] **Age rating** — Experience guidelines questionnaire is completed accurately.
- [ ] **Game updates log** — Social links or group page is set up for communicating updates to players.

---

## Social

- [ ] **Private servers** — If appropriate for the genre, private servers are enabled and priced (or free). Private server functionality works correctly.
- [ ] **Social features** — Friend invites, group integration, or social sharing features are implemented if relevant.
- [ ] **Chat filtering** — Any custom chat or text display uses `TextService:FilterStringAsync()` for all user-generated content.
- [ ] **Moderation tools** — If the game has social features, basic moderation is in place (report, mute, kick for game owners).
- [ ] **Group integration** — If the game is tied to a group, group ranks and permissions work correctly for any rank-gated features.

---

## Analytics

- [ ] **Key events instrumented** — Critical player actions are tracked with `AnalyticsService` or a custom analytics system:
  - Player join and session length.
  - First-time vs. returning player.
  - Tutorial completion rate.
  - Core loop engagement (e.g., items collected, levels completed).
  - Purchase events (what was bought, by whom).
  - Churn indicators (where players leave).
- [ ] **Funnel tracking** — Key funnels are instrumented (FTUE completion, shop visit to purchase, etc.).
- [ ] **Error logging** — Script errors are logged with context (player, location, action) for debugging in production.
- [ ] **Performance metrics** — Server FPS, memory usage, and network stats are monitored or logged.

---

## Final Verification

Before pressing "Publish":

1. Play the game from start as a new player on desktop, mobile, and console (if supported).
2. Verify all checklist items above are checked.
3. Have at least one other person playtest and provide feedback.
4. Confirm DataStore saves work in a live (non-Studio) test server.
5. Review the Developer Console (`F9`) for errors during a full play session.
