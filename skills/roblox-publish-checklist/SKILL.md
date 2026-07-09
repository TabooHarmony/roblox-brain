---
name: roblox-publish-checklist
description: "Use before publishing or updating a Roblox game to check data, security, performance, monetization, mobile, metadata, social, and analytics."
last_reviewed: 2026-05-27
sources: [original]
---

## When to Load

Load when preparing to publish or update a Roblox game. Provides a structured checklist covering data persistence, security, performance, monetization, mobile, gameplay, metadata, social, and analytics. Use to catch blockers before going live.

## Quick Reference

### 1. Data & Persistence
DataStore save/load ✓ · Session locking (ProfileStore) ✓ · BindToClose ✓ · Data migration plan ✓ · Disconnect-during-save edge case ✓ · No parallel save race conditions ✓

### 2. Security
All remotes validated server-side (types, ranges, ownership) ✓ · No secrets in ReplicatedStorage/StarterPlayer ✓ · Rate limiting on remotes ✓ · Logic server-side only (currency, inventory, damage) ✓ · ProcessReceipt: grant THEN PurchaseGranted ✓ · Anti-cheat basics (speed, teleport, inventory) ✓

### 3. Performance
Mobile tested ✓ · Part count reasonable ✓ · No memory leaks (events disconnected) ✓ · MicroProfiler: no scripts >1ms/frame ✓ · StreamingEnabled if large map ✓ · Signal cleanup ✓

### 4. Monetization
GamePasses idempotent on rejoin ✓ · DevProducts deliver correctly ✓ · Premium payout configured ✓ · Prices competitive ✓ · No pay-to-win ✓

### 5. Mobile
Touch controls work ✓ · UI uses Scale not Offset ✓ · ContextActionService ✓ · Small screen tested ✓ · Orientation handled ✓ · Low-end device tested ✓

### 6. Gameplay
Core loop 10+ min test ✓ · Edge cases: disconnect during trade, death during cutscene, rapid pressing, rejoin mid-game ✓ · Tutorial/FTUE ✓ · Difficulty curve ✓ · Fun check ✓

### 7. Metadata
Icon 512x512 ✓ · 3+ thumbnails ✓ · Description ✓ · Genre ✓ · Max players ✓ · Badges ✓ · Rating ✓

### 8. Social
Private servers ✓ · Party/chat/friend ✓ · Report/block safe ✓ · Tags correct ✓ · Team assignment ✓

### 9. Analytics
Events: join/leave, purchases, completions, session length, errors ✓ · Funnel tracking ✓ · Dashboard configured ✓

### Output Format
1. READY / NOT READY  2. Critical blockers  3. Warnings  4. Pass count/%  5. Failed items + fixes

📖 Full reference: `references/full.md`
