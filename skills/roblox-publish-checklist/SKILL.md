---
name: roblox-publish-checklist
description: "Pre-publish verification gauntlet for Roblox games"
last_reviewed: 2026-05-27
---

# /publish-checklist - Pre-Publish Verification

You are verifying a Roblox game is ready to publish. Work through every category below. For each item, check it and note PASS/FAIL/SKIP with a brief explanation.

---

## 1. Data & Persistence

- [ ] **DataStore save/load tested** - Player data saves on leave and loads on rejoin correctly
- [ ] **Session locking verified** - Using ProfileStore or equivalent; no concurrent data corruption
- [ ] **BindToClose implemented** - Server saves data before shutdown (game close, server hop)
- [ ] **Data migration plan** - If updating an existing game, schema migration handles old data formats
- [ ] **Edge case: disconnect during save** - Data not lost if player disconnects mid-save
- [ ] **Edge case: multiple DataStore calls** - No race conditions from parallel saves

---

## 2. Security

- [ ] **All remotes validated server-side** - Every RemoteEvent/RemoteFunction checks argument types, ranges, and ownership
- [ ] **No sensitive data exposed** - ReplicatedStorage, StarterPlayer have no server-only logic or secrets
- [ ] **Rate limiting on all remotes** - Per-player throttling prevents flooding/exploitation
- [ ] **No client-trusted game logic** - Currency, inventory, damage, positions calculated server-side only
- [ ] **ProcessReceipt handled correctly** - Grant item THEN return PurchaseGranted; NotProcessedYet on failure
- [ ] **Anti-cheat basics** - Speed checks, teleport detection, inventory validation

---

## 3. Performance

- [ ] **Mobile tested** - Game runs on mobile devices without crashes or severe lag
- [ ] **Part count within limits** - Workspace part count reasonable for target devices
- [ ] **No memory leaks** - Events disconnected on cleanup, no orphaned instances accumulating
- [ ] **MicroProfiler reviewed** - No scripts consistently over budget (>1ms per frame)
- [ ] **StreamingEnabled considered** - If large map, StreamingEnabled is enabled and tested
- [ ] **Signal cleanup** - No undisconnected BindableEvent/RemoteEvent connections leaking

---

## 4. Monetization

- [ ] **GamePasses work correctly** - Purchasing grants the correct benefit, idempotent on rejoin
- [ ] **DevProducts grant properly** - Consumables delivered, ProcessReceipt handles edge cases
- [ ] **Premium benefits functional** - Premium payout optimized, exclusive perks work
- [ ] **Prices reviewed** - Competitive with similar games, clear value proposition
- [ ] **No pay-to-win concerns** - Free players have reasonable experience
- [ ] **Premium Payouts enabled** - Game is eligible and configured for Premium Payouts

---

## 5. Mobile Compatibility

- [ ] **Touch controls work** - All interactions accessible via tap
- [ ] **UI scales properly** - Using Scale not Offset for UI elements; tested on small screens
- [ ] **ContextActionService for input** - Game actions bound properly for mobile
- [ ] **Small screen tested** - UI doesn't overlap, buttons are tappable, text is readable
- [ ] **Landscape and portrait** - Orientation handled if applicable
- [ ] **Performance on low-end devices** - Tested on minimum spec mobile device

---

## 6. Gameplay

- [ ] **Core loop tested end-to-end** - Play for 10+ minutes, full loop works
- [ ] **Edge cases handled:**
  - [ ] Disconnect during trade/transaction
  - [ ] Death during cutscene
  - [ ] Player leaves during multiplayer event
  - [ ] Rapid button pressing
  - [ ] Backfill/rejoin during active game
- [ ] **Tutorial/FTUE works** - New player can learn the game without confusion
- [ ] **Difficulty curve** - Early game engaging, progression feels rewarding
- [ ] **Fun check** - Core loop is actually enjoyable to play repeatedly

---

## 7. Metadata

- [ ] **Game icon set** - 512x512, clear and representative
- [ ] **Thumbnails uploaded** - At least 3 images showing gameplay
- [ ] **Description written** - Clear, compelling, includes key features
- [ ] **Genre selected** - Correct category for discovery
- [ ] **Max players configured** - Appropriate for game type
- [ ] **Game badges** - Achievement badges set up for milestones
- [ ] **Game rating** - Age-appropriate settings configured

---

## 8. Social

- [ ] **Private servers configured** - Available and priced if applicable
- [ ] **Social features tested** - Party system, chat, friending all work
- [ ] **Report/block doesn't break game** - Reporting a player doesn't crash or corrupt game state
- [ ] **Server browser** - Game appears in search with correct tags
- [ ] **Team play** - If multiplayer, team assignment and switching work

---

## 9. Analytics

- [ ] **Key events instrumented:**
  - [ ] Player joins / leaves
  - [ ] Purchases (GamePass and DevProduct)
  - [ ] Level/zone completions
  - [ ] Session length tracking
  - [ ] Error/crash reporting
- [ ] **Basic funnel tracking** - New player → tutorial complete → first purchase → retention
- [ ] **Dashboard configured** - Analytics visible in Roblox Creator Dashboard

---

## Summary

After checking all items, output:

1. **Overall status:** READY / NOT READY
2. **Critical blockers** (must fix before publish)
3. **Warnings** (should fix, not blocking)
4. **Passed items** - Count and percentage
5. **Failed items** - List each with the fix needed

If NOT READY, provide specific fixes for every failed item before the user publishes.