# Roblox Tooling Ecosystem Reference

## 1. Overview

**Load this reference when:** setting up Rojo for filesystem-based development, configuring external tooling (linting, formatting, testing), building CI/CD pipelines, managing packages with Wally, or onboarding a team to professional Roblox workflows.

The modern Roblox development stack moves work out of Studio and into the filesystem, enabling version control, code review, automated testing, and all the practices expected in professional software engineering. The core toolchain is:

| Tool       | Purpose                        | Install Via        |
| ---------- | ------------------------------ | ------------------ |
| **Rojo**   | Filesystem <-> Studio sync     | Aftman / Cargo     |
| **Wally**  | Package manager                | Aftman / Cargo     |
| **Selene** | Luau linter                    | Aftman / Cargo     |
| **StyLua** | Luau/Lua formatter             | Aftman / Cargo     |
| **Lune**   | Luau runtime outside Roblox    | Aftman / Cargo     |
| **Aftman** | Toolchain manager (installs all above) | Cargo       |

---

## 2. Rojo

Rojo syncs a filesystem project into Roblox Studio (and back). It is the foundation of all external tooling workflows.

### Installation

```bash
# Option A — Aftman (recommended toolchain manager)
cargo install aftman          # one-time
aftman init                   # creates aftman.toml in project root
aftman add rojo-rbx/rojo      # pins a specific version

# Option B — Cargo directly
cargo install rojo

# Option C — GitHub releases / Foreman (legacy)
# Download binary from https://github.com/rojo-rbx/rojo/releases
```

After installing via Aftman, the `aftman.toml` in your project root looks like:

```toml
[tools]
rojo = "rojo-rbx/rojo@7.4.4"
wally = "UpliftGames/wally@0.3.2"
selene = "Kampfkarren/selene@0.27.1"
stylua = "JohnnyMorganz/StyLua@0.20.0"
lune = "lune-org/lune@0.8.9"
```

### File Naming Conventions

Rojo determines the Roblox class of each file by its suffix:

| File Name Pattern         | Roblox Class      | Example                         |
| ------------------------- | ----------------- | ------------------------------- |
| `*.server.luau`           | `Script`          | `main.server.luau`              |
| `*.client.luau`           | `LocalScript`     | `controller.client.luau`        |
| `*.luau` (no prefix)      | `ModuleScript`    | `Utils.luau`                    |
| `init.luau`               | Folder becomes a `ModuleScript` | `MyModule/init.luau` |
| `init.server.luau`        | Folder becomes a `Script`       | `GameService/init.server.luau` |
| `init.client.luau`        | Folder becomes a `LocalScript`  | `HUD/init.client.luau`         |
| `init.meta.json`          | Sets properties on the folder   | `MyFolder/init.meta.json`      |
| `*.model.json`            | Rojo model file   | `part.model.json`               |

> **Note:** `.lua` also works, but `.luau` is the modern standard and enables better LSP support.

### project.json — Complete Example

```json
{
  "name": "MyGame",
  "tree": {
    "$className": "DataModel",

    "ServerScriptService": {
      "$className": "ServerScriptService",
      "Server": {
        "$path": "src/server"
      }
    },

    "ServerStorage": {
      "$className": "ServerStorage",
      "Storage": {
        "$path": "src/server-storage"
      }
    },

    "ReplicatedStorage": {
      "$className": "ReplicatedStorage",
      "Shared": {
        "$path": "src/shared"
      },
      "Packages": {
        "$path": "Packages"
      }
    },

    "StarterPlayer": {
      "$className": "StarterPlayer",
      "StarterPlayerScripts": {
        "$className": "StarterPlayerScripts",
        "Client": {
          "$path": "src/client"
        }
      },
      "StarterCharacterScripts": {
        "$className": "StarterCharacterScripts",
        "Character": {
          "$path": "src/character"
        }
      }
    },

    "StarterGui": {
      "$className": "StarterGui",
      "UI": {
        "$path": "src/ui"
      }
    },

    "Workspace": {
      "$className": "Workspace",
      "$properties": {
        "FilteringEnabled": true
      }
    },

    "Lighting": {
      "$className": "Lighting",
      "$properties": {
        "Technology": "Future"
      }
    },

    "SoundService": {
      "$className": "SoundService"
    },

    "HttpService": {
      "$className": "HttpService",
      "$properties": {
        "HttpEnabled": true
      }
    }
  }
}
```

### Common Commands

```bash
# Initialize a new project
rojo init my-game

# Start the live sync server (default port 34872)
rojo serve

# Serve a specific project file
rojo serve default.project.json

# Build a .rbxlx place file from the project
rojo build -o game.rbxlx

# Build a .rbxl (binary format)
rojo build -o game.rbxl

# Build a model file
rojo build -o model.rbxm
```

### Two-Way Sync

Rojo supports two-way sync via the Studio plugin. When connected:

- Changes made on the filesystem are pushed into Studio in real time.
- Changes made inside Studio (e.g., moving parts, editing properties) can be pulled back to the filesystem when using `*.model.json` files or `init.meta.json`.
- Script content changes in Studio are synced back to `.luau` files.

> **Caveat:** Two-way sync for non-script instances is limited. For level design, most teams use a `.rbxlx` place file committed to Git and build/serve on top of it.

---

## 3. Wally — Package Manager

Wally is the community-standard package manager for Roblox, maintained by Uplift Games.

### wally.toml — Complete Example

```toml
[package]
name = "yourname/my-game"
version = "0.1.0"
registry = "https://github.com/UpliftGames/wally-index"
realm = "shared"
license = "MIT"
description = "My awesome Roblox game"
authors = ["Your Name <you@example.com>"]

[dependencies]
Promise = "evaera/promise@4.0.0"
Knit = "sleitnick/knit@1.6.0"
Signal = "sleitnick/signal@2.0.0"
Trove = "sleitnick/trove@1.1.0"
TableUtil = "sleitnick/table-util@1.2.0"
Timer = "sleitnick/timer@1.1.0"
Component = "sleitnick/component@2.4.0"
ProfileService = "madstudioroblox/profileservice@1.2.0"

[server-dependencies]
DataStoreService = "sleitnick/datastore-service@0.1.0"

[dev-dependencies]
TestEZ = "roblox/testez@0.4.1"
```

### Realms

Wally uses **realms** to control where packages end up:

| Realm      | Destination             | Visible To          |
| ---------- | ----------------------- | ------------------- |
| `shared`   | `ReplicatedStorage`     | Server + Client     |
| `server`   | `ServerScriptService`   | Server only         |
| `dev`      | `ReplicatedStorage`     | Development only    |

### Common Commands

```bash
# Install all dependencies listed in wally.toml
wally install

# Search for a package
wally search promise

# Add a specific package (edits wally.toml)
# Note: manual editing of wally.toml is common

# Login for publishing
wally login

# Publish your own package
wally publish
```

After `wally install`, packages appear in a `Packages/` directory. Your `project.json` should map this directory into `ReplicatedStorage` (or another appropriate service).

### Popular Packages

| Package              | Author           | Purpose                                      |
| -------------------- | ---------------- | -------------------------------------------- |
| `evaera/promise`     | evaera           | Promise implementation for Luau              |
| `sleitnick/knit`     | sleitnick        | Lightweight service/controller framework     |
| `sleitnick/signal`   | sleitnick        | Custom signal (event) implementation         |
| `sleitnick/trove`    | sleitnick        | Cleanup/maid utility                         |
| `sleitnick/component`| sleitnick        | Component pattern for CollectionService tags |
| `madstudioroblox/profileservice` | madstudio | Robust DataStore wrapper             |
| `roblox/testez`      | Roblox           | BDD-style testing framework                  |
| `evaera/cmdr`        | evaera           | In-game admin command framework              |
| `stravant/goodsignal`| stravant         | Optimized signal implementation              |
| `sleitnick/table-util`| sleitnick       | Table utility functions                      |

### Publishing Your Own Packages

1. Set up your `wally.toml` with a unique `name` field: `"your-username/package-name"`.
2. Ensure `version` follows semver.
3. Include an `init.luau` at the package root that exports your module.
4. Run `wally login` to authenticate via GitHub.
5. Run `wally publish` to push to the Wally registry.

### Wally Package Sourcemap

After running `wally install`, generate a sourcemap so the Luau LSP can resolve package types:

```bash
rojo sourcemap default.project.json -o sourcemap.json
```

Some LSP configurations pick this up automatically.

---

## 4. Selene — Luau Linter

Selene is a static analysis tool for Lua and Luau. It catches bugs, style issues, and potential errors before runtime.

### Installation

```bash
aftman add Kampfkarren/selene
# or
cargo install selene
```

### selene.toml — Complete Example

```toml
std = "roblox"

[rules]
# Error-level rules (will fail CI)
unused_variable = "warn"
shadowing = "warn"
unscoped_variables = "deny"
incorrect_standard_library_use = "warn"
divide_by_zero = "warn"
undefined_variable = "deny"
deprecated = "warn"
global_usage = "warn"
if_same_then_else = "warn"
ifs_same_cond = "warn"
multiple_statements = "warn"
parenthese_conditions = "warn"
type_check_inside_call = "warn"
mismatched_arg_count = "warn"
empty_if = "warn"
empty_loop = "warn"
almost_swapped = "warn"
bad_string_escape = "deny"
compare_nan = "deny"
constant_table_comparison = "warn"
high_cyclomatic_complexity = "warn"
manual_table_clone = "warn"
mixed_table = "warn"
must_use = "warn"
roblox_incorrect_color3_new_bounds = "warn"
roblox_incorrect_roact_usage = "warn"
roblox_suspicious_udim2_new = "warn"
suspicious_reverse_loop = "warn"

[config]
high_cyclomatic_complexity = { maximum_complexity = 20 }
```

### Standard Library

The `std = "roblox"` setting tells Selene about all Roblox globals (`game`, `workspace`, `Instance`, etc.). Without it, every Roblox API call would trigger `undefined_variable`.

To generate a more precise standard library from your project's types:

```bash
selene generate-roblox-std
```

This creates a `roblox.yml` file with up-to-date API definitions.

### Common Commands

```bash
# Lint the entire src directory
selene src/

# Lint with specific config
selene --config selene.toml src/

# Generate Roblox standard library
selene generate-roblox-std

# Quiet output (only errors)
selene src/ --display-style quiet
```

### Inline Suppression

```lua
-- selene: allow(unused_variable)
local temporaryDebugValue = 42

local function example()
    -- selene: allow(shadowing)
    local x = 10
end
```

---

## 5. StyLua — Luau Formatter

StyLua is an opinionated code formatter for Lua and Luau, inspired by Prettier.

### Installation

```bash
aftman add JohnnyMorganz/StyLua
# or
cargo install stylua
```

### stylua.toml — Complete Example

```toml
column_width = 120
line_endings = "Unix"
indent_type = "Tabs"
indent_width = 4
quote_style = "AutoPreferDouble"
call_parentheses = "Always"
collapse_simple_statement = "Never"

[sort_requires]
enabled = true
```

### Common Commands

```bash
# Format all Luau files in src/
stylua src/

# Check formatting without modifying (for CI)
stylua --check src/

# Format a single file
stylua src/server/PlayerService.luau

# Verify config
stylua --config-path stylua.toml --check src/
```

### VS Code Format-on-Save

Add to your `.vscode/settings.json`:

```json
{
  "[luau]": {
    "editor.defaultFormatter": "JohnnyMorganz.stylua",
    "editor.formatOnSave": true
  }
}
```

### Ignoring Sections

```lua
-- stylua: ignore
local uglyButNecessaryMatrix = {
    { 1, 0, 0, 0 },
    { 0, 1, 0, 0 },
    { 0, 0, 1, 0 },
    { 0, 0, 0, 1 },
}
```

---

## 6. Git Workflows

### .gitignore — Complete Template

```gitignore
# Roblox place/model files (built from source via Rojo)
*.rbxlx
*.rbxl
*.rbxm
*.rbxmx

# If you use a base place file, un-ignore it:
# !base.rbxlx

# Wally packages (installed from registry, not committed)
/Packages/

# Wally lock file (optional: some teams commit this for reproducibility)
# wally.lock

# Rojo sourcemap (auto-generated)
sourcemap.json

# Selene generated std
roblox.yml

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
!.vscode/settings.json
!.vscode/extensions.json

# Aftman binaries
~/.aftman/

# Build output
/build/
/dist/
```

### Branching Strategy

```
main (production — what's live in the game)
├── develop (integration branch)
│   ├── feature/combat-system
│   ├── feature/inventory-ui
│   ├── fix/respawn-bug
│   └── chore/update-packages
└── release/v1.2.0
```

- **Feature branches** for new gameplay systems.
- **Fix branches** for bug fixes.
- **Release branches** when preparing a deployment.
- Merge to `develop` via pull request with CI checks passing.
- Merge `develop` to `main` for releases.

### Team Create + Git Coexistence

For teams that use both Team Create (for level design) and Git (for code):

1. **Code** lives in the filesystem, synced via Rojo. Developers write code in VS Code and see changes in Studio via `rojo serve`.
2. **Level design / maps** are authored directly in Studio via Team Create.
3. To capture Studio changes in Git, periodically export the place file (`File > Save As > .rbxlx`) and commit it. Rojo builds on top of this base place.
4. Use a `base.rbxlx` that you DO commit (un-ignore in `.gitignore`) for non-code assets.

```bash
# Build flow with a base place file
rojo build default.project.json --output game.rbxlx --base base.rbxlx
```

---

## 7. VS Code Setup

### Recommended Extensions

| Extension                  | ID                                 | Purpose                        |
| -------------------------- | ---------------------------------- | ------------------------------ |
| **Luau LSP**               | `JohnnyMorganz.luau-lsp`           | Autocomplete, type checking, go-to-definition |
| **Rojo**                   | `evaera.vscode-rojo`               | Rojo integration in VS Code    |
| **Selene**                 | `Kampfkarren.selene-vscode`        | Inline lint warnings           |
| **StyLua**                 | `JohnnyMorganz.stylua`             | Format-on-save                 |
| **Roblox LSP** (alt)       | `Nightrains.robloxlsp`            | Alternative LSP (older)        |

### .vscode/settings.json

```json
{
  "luau-lsp.sourcemap.enabled": true,
  "luau-lsp.sourcemap.rojoProjectFile": "default.project.json",
  "luau-lsp.sourcemap.autogenerate": true,
  "luau-lsp.types.roblox": true,
  "luau-lsp.diagnostics.enabled": true,
  "luau-lsp.completion.enabled": true,
  "luau-lsp.hover.enabled": true,

  "[luau]": {
    "editor.defaultFormatter": "JohnnyMorganz.stylua",
    "editor.formatOnSave": true,
    "editor.tabSize": 4,
    "editor.insertSpaces": false
  },

  "files.associations": {
    "*.luau": "luau",
    "*.lua": "luau"
  },

  "files.exclude": {
    "Packages/": true,
    "sourcemap.json": true
  }
}
```

### .vscode/extensions.json

```json
{
  "recommendations": [
    "JohnnyMorganz.luau-lsp",
    "evaera.vscode-rojo",
    "Kampfkarren.selene-vscode",
    "JohnnyMorganz.stylua"
  ]
}
```

### Debugging Tips

- **Luau LSP shows red squiggles on Roblox APIs:** Ensure `luau-lsp.types.roblox` is `true` and the sourcemap is being generated. Run `rojo sourcemap default.project.json -o sourcemap.json` manually if auto-generation fails.
- **Packages not resolving:** After `wally install`, regenerate the sourcemap. The LSP reads `sourcemap.json` to understand the full tree.
- **Type errors on third-party packages:** Some Wally packages lack type annotations. Use `-- luau-lsp ignore` or add type stubs.
- **Rojo plugin not connecting:** Ensure `rojo serve` is running and Studio has the Rojo plugin installed (install via the Rojo VS Code extension or Roblox plugin marketplace).

---

## 8. CI/CD — GitHub Actions

### Complete Workflow — `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint (Selene)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Aftman
        uses: ok-nick/setup-aftman@v0.4.2

      - name: Generate Roblox standard library
        run: selene generate-roblox-std

      - name: Run Selene
        run: selene src/

  format:
    name: Format Check (StyLua)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Aftman
        uses: ok-nick/setup-aftman@v0.4.2

      - name: Check formatting
        run: stylua --check src/

  analyze:
    name: Type Check (Luau LSP)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Aftman
        uses: ok-nick/setup-aftman@v0.4.2

      - name: Install packages
        run: wally install

      - name: Generate sourcemap
        run: rojo sourcemap default.project.json -o sourcemap.json

      - name: Run Luau analysis
        run: luau-lsp analyze --sourcemap sourcemap.json --defs=globalTypes.d.luau src/

  test:
    name: Tests (Lune)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Aftman
        uses: ok-nick/setup-aftman@v0.4.2

      - name: Run tests
        run: lune run tests/run

  build:
    name: Build Check
    runs-on: ubuntu-latest
    needs: [lint, format, test]
    steps:
      - uses: actions/checkout@v4

      - name: Install Aftman
        uses: ok-nick/setup-aftman@v0.4.2

      - name: Install packages
        run: wally install

      - name: Build place file
        run: rojo build default.project.json -o build.rbxl

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: game-build
          path: build.rbxl
          retention-days: 7
```

### CI Commands Summary

```bash
# Lint — exit code 1 on any warning/error
selene src/

# Format check — exit code 1 if any file is unformatted
stylua --check src/

# Build check — exit code 1 if project.json is invalid
rojo build default.project.json -o /dev/null

# Run tests via Lune
lune run tests/run
```

---

## 9. Lune Runtime

Lune is a standalone Luau runtime for running scripts outside of Roblox. It is ideal for testing, build scripts, code generation, and tooling.

### Installation

```bash
aftman add lune-org/lune
# or
cargo install lune
```

### Basic Usage

```bash
# Run a Luau script
lune run script-name           # runs script-name.luau from current dir or .lune/

# Run from a specific path
lune run path/to/script.luau
```

### Built-in Libraries

Lune provides globals that replace Roblox services for external scripting:

```lua
-- .lune/example.luau
local fs = require("@lune/fs")
local net = require("@lune/net")
local process = require("@lune/process")
local stdio = require("@lune/stdio")
local task = require("@lune/task")

-- Read a file
local content = fs.readFile("src/shared/Config.luau")
print("File length:", #content)

-- HTTP request
local response = net.request("https://api.example.com/data")
print("Status:", response.statusCode)

-- Run a shell command
local result = process.spawn("rojo", { "sourcemap", "default.project.json", "-o", "sourcemap.json" })
print("Exit code:", result.code)

-- Prompt user
local answer = stdio.prompt("confirm", "Run tests?")
if answer then
    print("Running tests...")
end
```

### Test Runner Example

```lua
-- tests/run.luau (executed via `lune run tests/run`)
local fs = require("@lune/fs")
local process = require("@lune/process")

local passed = 0
local failed = 0

local function runTest(name: string, testFn: () -> ())
    local success, err = pcall(testFn)
    if success then
        passed += 1
        print(`  PASS: {name}`)
    else
        failed += 1
        print(`  FAIL: {name} — {err}`)
    end
end

local function assertEqual(actual: any, expected: any, message: string?)
    if actual ~= expected then
        error(message or `Expected {expected}, got {actual}`)
    end
end

-- Example tests
runTest("math works", function()
    assertEqual(2 + 2, 4)
end)

runTest("string concat", function()
    assertEqual("hello" .. " " .. "world", "hello world")
end)

print(`\nResults: {passed} passed, {failed} failed`)

if failed > 0 then
    process.exit(1)
end
```

### Lune for Build Scripts

```lua
-- .lune/build.luau
local process = require("@lune/process")
local fs = require("@lune/fs")

-- Install packages
print("Installing packages...")
local wally = process.spawn("wally", { "install" })
assert(wally.code == 0, "wally install failed")

-- Generate sourcemap
print("Generating sourcemap...")
local sourcemap = process.spawn("rojo", { "sourcemap", "default.project.json", "-o", "sourcemap.json" })
assert(sourcemap.code == 0, "sourcemap generation failed")

-- Build
print("Building place file...")
if not fs.isDir("build") then
    fs.writeDir("build")
end

local build = process.spawn("rojo", { "build", "default.project.json", "-o", "build/game.rbxl" })
assert(build.code == 0, "rojo build failed")

print("Build complete: build/game.rbxl")
```

---

## 10. Rojo Project Templates

### Solo Developer — Minimal Structure

```
my-game/
├── aftman.toml
├── default.project.json
├── wally.toml
├── selene.toml
├── stylua.toml
├── .gitignore
├── Packages/                  (git-ignored, populated by wally install)
├── src/
│   ├── server/
│   │   ├── Services/
│   │   │   ├── DataService.server.luau
│   │   │   └── GameService.server.luau
│   │   └── init.server.luau   (bootstrap — requires and starts services)
│   ├── client/
│   │   ├── Controllers/
│   │   │   ├── InputController.client.luau
│   │   │   └── UIController.client.luau
│   │   └── init.client.luau   (bootstrap — requires and starts controllers)
│   └── shared/
│       ├── Constants.luau
│       ├── Types.luau
│       └── Utils.luau
└── tests/
    └── run.luau
```

### Team Project — Full Structure

```
my-game/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .vscode/
│   ├── settings.json
│   └── extensions.json
├── aftman.toml
├── default.project.json
├── wally.toml
├── wally.lock
├── selene.toml
├── stylua.toml
├── .gitignore
├── .luaurc                    (Luau configuration for aliases)
├── Packages/                  (git-ignored)
├── src/
│   ├── server/
│   │   ├── Services/
│   │   │   ├── DataService/
│   │   │   │   ├── init.luau
│   │   │   │   ├── DataSchema.luau
│   │   │   │   └── Migrations.luau
│   │   │   ├── CombatService/
│   │   │   │   ├── init.luau
│   │   │   │   ├── DamageCalculator.luau
│   │   │   │   └── HitDetection.luau
│   │   │   └── MatchmakingService/
│   │   │       └── init.luau
│   │   ├── Components/
│   │   │   ├── Loot.luau
│   │   │   └── NPC.luau
│   │   └── init.server.luau
│   ├── client/
│   │   ├── Controllers/
│   │   │   ├── InputController.luau
│   │   │   ├── CameraController.luau
│   │   │   └── UIController.luau
│   │   ├── Components/
│   │   │   ├── Billboard.luau
│   │   │   └── Interactable.luau
│   │   ├── UI/
│   │   │   ├── Screens/
│   │   │   │   ├── HUD.luau
│   │   │   │   ├── Inventory.luau
│   │   │   │   └── Settings.luau
│   │   │   └── Components/
│   │   │       ├── Button.luau
│   │   │       └── Tooltip.luau
│   │   └── init.client.luau
│   ├── character/
│   │   ├── Animate.client.luau
│   │   └── Health.client.luau
│   ├── shared/
│   │   ├── Constants.luau
│   │   ├── Types.luau
│   │   ├── Enums.luau
│   │   ├── Utils/
│   │   │   ├── Math.luau
│   │   │   ├── String.luau
│   │   │   └── Table.luau
│   │   └── Network/
│   │       ├── Remotes.luau
│   │       └── Middleware.luau
│   ├── server-storage/
│   │   ├── Maps/
│   │   └── Assets/
│   └── ui/
│       └── Widgets/
├── tests/
│   ├── run.luau
│   ├── server/
│   │   └── DataService.spec.luau
│   └── shared/
│       └── Utils.spec.luau
├── .lune/
│   ├── build.luau
│   └── deploy.luau
├── assets/                    (raw assets: PSD, blend files, etc.)
└── docs/
    └── architecture.md
```

### .luaurc for Path Aliases

```json
{
  "aliases": {
    "Packages": "Packages",
    "Shared": "src/shared",
    "Server": "src/server",
    "Client": "src/client"
  }
}
```

---

## 11. Best Practices

### Use External Tooling for Any Serious Project

- Even solo developers benefit from Rojo + Git. You get version history, the ability to roll back mistakes, and a professional code editor.
- The initial setup cost (30 minutes) pays for itself the first time you accidentally delete a script in Studio.

### Automate Quality Checks

- Run `selene` and `stylua --check` in CI on every pull request. This prevents lint regressions and formatting inconsistencies from ever reaching production.
- Add type checking via `luau-lsp analyze` in CI to catch type errors before they become runtime bugs.

### Version Control Everything

- All game code belongs in Git. No exceptions.
- Commit `wally.lock` for reproducible builds (so every team member and CI gets the same package versions).
- Commit `aftman.toml` so every contributor uses the same tool versions.
- Tag releases with semver (`v1.0.0`, `v1.1.0`) so you can always identify what's deployed.

### Lock Tool Versions

- Use Aftman to pin exact versions of Rojo, Wally, Selene, StyLua, and Lune. This prevents "works on my machine" issues.

### Structure Code by Domain

- Organize `src/server/Services/` by game system, not by script type.
- Each service folder should be self-contained with its own `init.luau`.
- Shared types and constants go in `src/shared/` where both server and client can access them.

### Write Tests

- Use Lune for unit tests on pure logic (math, data transformations, state machines).
- Use TestEZ for integration tests that run inside Studio.
- Even minimal test coverage on critical systems (data saving, economy) prevents costly bugs.

---

## 12. Anti-Patterns

### Studio-Only Development Without Backups

**Problem:** All code lives exclusively inside a Roblox place file. If the file corrupts, Studio crashes, or you accidentally delete a script, the work is gone. Roblox auto-saves are not a reliable backup strategy.

**Fix:** Use Rojo to keep code on the filesystem and commit to Git. Even a basic `git init` + `git commit` cycle provides infinite undo.

### Manual Formatting

**Problem:** Every developer uses different indentation, quote styles, and line lengths. Code reviews waste time on style nitpicks. Merges produce unnecessary diff noise.

**Fix:** Add `stylua.toml` to the project, enable format-on-save, and run `stylua --check` in CI. Formatting becomes invisible and automatic.

### No Linting

**Problem:** Typos in variable names, unused variables, and incorrect API usage are only caught at runtime (if at all). Developers waste time debugging errors that a linter would catch instantly.

**Fix:** Add `selene.toml` with `std = "roblox"` and run it in CI. Start with default rules and tighten over time.

### Committing Packages/ to Git

**Problem:** The `Packages/` directory contains third-party code installed by Wally. Committing it bloats the repository, creates noisy diffs on updates, and duplicates what the registry already provides.

**Fix:** Add `Packages/` to `.gitignore`. Run `wally install` as part of your setup and CI scripts. Commit `wally.lock` for reproducibility.

### Committing Build Artifacts

**Problem:** `.rbxl` and `.rbxlx` files are large binaries that change on every build. Committing them inflates repository size and makes Git operations slow.

**Fix:** Add `*.rbxl` and `*.rbxlx` to `.gitignore`. Build from source in CI. If you need a base place file for non-code assets, commit exactly one `base.rbxlx` and keep it updated intentionally.

### Not Using Type Annotations

**Problem:** Luau has a powerful type system, but many developers ignore it. Without types, refactoring is risky, autocomplete is limited, and bugs slip through.

**Fix:** Annotate function signatures, especially on public module APIs. Use `--!strict` at the top of critical modules. Run `luau-lsp analyze` in CI.

### Ignoring Wally Lock Files

**Problem:** Without committing `wally.lock`, different developers (and CI) may resolve to different package versions, causing subtle and hard-to-diagnose inconsistencies.

**Fix:** Commit `wally.lock`. Run `wally install` (which respects the lock file) rather than manually editing versions.

### Monolithic Scripts

**Problem:** A single 2,000-line server script that handles combat, data, matchmaking, and UI updates. Impossible to test, review, or maintain.

**Fix:** Split into focused services/modules. Each module should do one thing. Use `init.luau` folders to group related files. Aim for files under 300 lines.
