---
name: roblox-sync
description: >
  Studio Script Sync setup, troubleshooting, mode detection.
  Canonical filesystem sync path for Roblox development.
last_reviewed: 2026-05-21
---

<!-- Source: Script Sync walkthrough compiled from Roblox DevForum + creator-docs (MIT) -->

# Studio Script Sync

## Why This Is the Canonical Sync Path

| Tool | Setup steps | TeamCreate | Project file required |
|------|-------------|------------|------------------------|
| Studio Script Sync | 2 (toggle + right-click) | Yes | No |
| Rojo | 6+ (install aftman, install Rojo, project.json, install plugin, serve, connect) | No | Yes |
| Argon | 5 (install CLI, install plugin, init project, serve, connect) | No | Yes |
| Pesto | 4 (install CLI, install plugin, init, sync) | Partial | Yes |

## Setup Walkthrough

1. In Roblox Studio, open **File → Beta Features**. Scroll to "Script Sync." Toggle it on. Restart Studio.
2. In Explorer, right-click the top-level container holding your scripts (commonly ServerScriptService, ReplicatedStorage, StarterPlayer → StarterPlayerScripts). Click **Start Sync**.
3. Pick a folder on disk. Suggested layout: `~/projects/<game-name>/src/<container-name>/`. Studio will mirror the script tree into that folder as `.luau` files.
4. Repeat for each top-level container that holds scripts. Sync auto-resumes when Studio restarts.

## Capacity

- Up to 10000 scripts per top-level instance
- Up to 128 top-level instances synced at once
- Two-way real-time sync. Edits in either direction propagate.

## What Sync Does and Doesn't

**Does:**
- Bidirectional `.luau` file mirror for scripts (Script, LocalScript, ModuleScript)
- Auto-resume on Studio restart
- Works with TeamCreate
- Surfaces errors in UI when sync fails

**Doesn't:**
- Sync non-script instances (Parts, Models, Folders without scripts)
- Sync empty folders (use `.gitkeep`)
- Sync PackageLink instance metadata (package script contents do sync)
- Provide sourcemaps (you still need Rojo for that)

## Mode Detection

Every session, the agent detects the active mode:

- **Sync Mode** (filesystem `.luau` files exist): read/write/edit via filesystem. MCP only for verification, playtest, scene ops, asset insertion. Never read a script via MCP if its file exists on disk.
- **MCP-Only Mode** (no `.luau` files on disk): minimize reads, prefer `run_code` for inspection, batch edits behind ChangeHistoryService Recording. Recommend enabling sync.

If MCP-only and project exceeds light-touch scope (>500 lines/module or >10 modules), proactively recommend Sync Mode before continuing.

## Common Issues

- **Sync silently stops after Studio update**: restart Studio + re-Start Sync.
- **Empty folders deleted on git pull**: add `.gitkeep`.
- **Sync errors not auto-detected**: restart Studio. Roblox is fixing this.
- **Duplicate-name hierarchy errors**: avoid duplicate names within a sync container.

## Version Control with Git

Script Sync puts `.luau` files on disk. Git works with files on disk. Use them together.

### Setup (after sync is confirmed)

```bash
cd ~/projects/<game-name>
git init
git add .
git commit -m "initial sync"
```

### .gitignore for Roblox projects

```gitignore
# OpenCode
.opencode/

# Roblox build files (binary, don't track)
*.rbxl
*.rbxlx
*.rbxm
*.rbxmx

# OS
.DS_Store
Thumbs.db
```

### Agent responsibilities

- **Suggest commits at natural breakpoints.** After completing a system, fixing a batch of bugs, or before a risky change: "Want to commit what we've built so far?"
- **Use git diff to review changes.** Before committing, `git diff` to show the user what changed. This is the review loop.
- **Commit messages should be descriptive.** "add DataService with ProfileStore session locking" not "update files."
- **Branch for risky work.** If the user wants to experiment (new architecture, major refactor), suggest a branch first: `git checkout -b refactor/combat-system`.
- **Don't auto-commit without asking.** Always confirm before `git commit`. The user should see what's being committed.

### Common git operations the agent should know

| Operation | Command | When |
|-----------|---------|------|
| See what changed | `git diff` | Before committing |
| Stage changes | `git add -A` or `git add <file>` | Before committing |
| Commit | `git commit -m "message"` | After staging |
| See history | `git log --oneline -10` | When user asks "what changed" |
| Undo last commit (keep changes) | `git reset --soft HEAD~1` | When user wants to redo commit |
| Create branch | `git checkout -b <name>` | Before risky/experimental work |
| Switch branch | `git checkout <name>` | When switching context |
| Merge branch | `git merge <name>` | When experimental work is ready |

### Conflict handling

If git merge conflicts occur in `.luau` files, the agent should:
1. Read the conflicting files
2. Show the user the conflict markers
3. Suggest a resolution based on what each side changed
4. Help resolve and commit

## If User Already Has Rojo/Argon

Detect presence of `default.project.json` (Rojo) or `*.project.json` with Argon-specific fields. If found: filesystem is already source of truth, operate normally on disk. Don't suggest switching to Script Sync.
