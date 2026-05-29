---
name: roblox-data
description: DataStores, ProfileStore, session locking, data persistence patterns.
last_reviewed: 2026-05-21
---

<!-- Source: brockmartin/roblox-game-skill (MIT) -->

# Roblox Data Persistence Reference

## 1. Overview

Data persistence in Roblox means saving player progress so it survives across sessions. Every time a player joins, the server loads their data from the cloud; every time they leave (or periodically), it saves back.

**When data flows:**

```
Player Joins  -->  Server loads from DataStore  -->  Populate in-game objects
Player Plays  -->  Data lives in server memory   -->  Auto-save on interval
Player Leaves -->  Server saves to DataStore     -->  Data persists for next session
```

**Data architecture decisions:**

| Approach | Best For | Complexity |
|----------|----------|------------|
| Raw DataStoreService | Simple games, prototypes | Low |
| **ProfileStore** | **Production games (USE THIS)** | Medium |
| Custom wrapper | Specific advanced requirements | High |

> **Use ProfileStore for any game that will ship.** Raw DataStore examples in sections 2-3 exist to explain the underlying system. Do NOT implement manual auto-save, session locking, BindToClose handlers, or retry logic - ProfileStore handles all of this automatically. Section 4 is the production pattern.

**Prerequisite:** Enable API Services in Roblox Studio under **Game Settings > Security > Enable Studio Access to API Services**. Without this, DataStore calls will fail in Studio testing.

---

## Quick Reference

**Load Full Reference below only when you need specific implementation examples or migration patterns.**

Key rules:
- ALWAYS use ProfileStore for player data. Never raw DataStoreService for mutable player state.
- Session locking prevents data corruption from multi-server joins. ProfileStore handles this.
- BindToClose is MANDATORY. Flush all pending saves on server shutdown.
- Schema: use a default template table. New fields get default values automatically.
- Access pattern: `profile.Data.fieldName`. Mutate directly, ProfileStore auto-saves.
- Release profile on PlayerRemoving: `profile:Release()`
- OrderedDataStore for leaderboards only (separate from player data).
- Data migration: version field in schema, migrate on load if version < current.
- Never store Instances or functions in DataStores. Serialize to primitives.
- Cross-server: MessagingService for real-time, GlobalDataStore for shared state.
