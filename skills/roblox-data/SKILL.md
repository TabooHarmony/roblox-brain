---
name: roblox-data
description: "Use when implementing player data persistence with DataStore or ProfileStore, session locking, schemas, migrations, or save and load flows."
last_reviewed: 2026-05-21
sources:
  - https://raw.githubusercontent.com/brockmartin/roblox-game-skill/main/references/datastore-persistence.md
---

# Roblox Data Persistence Reference

## When to Load

Load when implementing player data persistence with DataStore or ProfileStore, including session locking, schemas, migrations, and save/load flows. Use `roblox-server-data` for leaderboards, MessagingService, and shared world state.

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
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
