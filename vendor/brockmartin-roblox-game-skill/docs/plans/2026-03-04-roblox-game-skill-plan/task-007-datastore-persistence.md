# Task 007: Write datastore-persistence.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/datastore-persistence.md`

## Description

Write a comprehensive reference for data persistence in Roblox covering raw DataStoreService, ProfileService, session locking, and data migration patterns.

## What To Do

1. **Overview** — When to load (saving/loading player data, data architecture questions)
2. **DataStoreService Basics** — GetDataStore, GetAsync, SetAsync, UpdateAsync, RemoveAsync. When to use each. Include code for basic save/load
3. **Leaderstats Pattern** — Standard leaderstats folder setup, connecting to DataStore for persistence, auto-save on interval and PlayerRemoving
4. **ProfileService** — What it is, why to use it over raw DataStore, installation (Wally or manual), session locking explained, basic setup code, profile template definition
5. **Session Locking** — Why it's critical (prevents data duplication/loss when player rapidly server-hops), how ProfileService handles it, manual implementation for raw DataStore
6. **Data Schema Design** — Structuring player data tables, versioning data schemas, default values, nested data
7. **Data Migration** — Handling schema changes across game updates, backwards compatibility, migration scripts
8. **OrderedDataStore** — Global leaderboards, ranking systems, pagination
9. **Cross-Server Data** — MessagingService for real-time cross-server communication, GlobalDataStore patterns
10. **Best Practices** — Auto-save intervals (5 min recommended), save on PlayerRemoving, handle BindToClose for server shutdown, retry failed saves, data validation before save
11. **Anti-Patterns** — Saving too frequently (rate limits), not handling DataStore errors, storing Instance references, exceeding 4MB data limit
12. **Sharp Edges** — DataStore rate limits (60 + numPlayers * 10 per minute), eventual consistency, BindToClose timeout (30 seconds), data loss from improper session handling

## Verification

- File exists at `references/datastore-persistence.md`
- Covers both raw DataStoreService and ProfileService
- Session locking explained with code
- Data migration pattern included
- Rate limits and sharp edges documented
