# Roblox Tooling Ecosystem — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## Decision Rules

- Use Rojo for any project with more than a few scripts; Studio-only development has no version history
- Use Wally for dependencies; never commit `/Packages/` to Git
- Use `aftman.toml` to pin tool versions across the team
- Run Selene + StyLua in CI to enforce code quality automatically
- Generate sourcemaps for luau-lsp to provide accurate IntelliSense
- Always commit `wally.lock` for reproducible installs

## Philosophy

The modern Roblox dev stack moves code from Studio to the filesystem. This enables:

1. **Version control.** Git tracks every change. Rollbacks, branches, PRs all work.
2. **Collaboration.** Multiple developers can work on the same project with standard merge workflows.
3. **Automation.** Linting, formatting, type checking, and testing run in CI.
4. **Reproducibility.** `aftman.toml` + `wally.lock` = identical toolchain for everyone.

Studio becomes a visual editor and playtester. Code lives on disk.

---

## Core Toolchain

Managed via [Aftman](https://github.com/nicbarker/aftman) (toolchain manager):

| Tool | Purpose | Install |
|------|---------|---------|
| [Rojo](https://rojo.space) | Syncs filesystem code to Roblox Studio | `aftman install` |
| [Wally](https://wally.run) | Package manager for Luau libraries | `aftman install` |
| [Selene](https://kampfkarren.github.io/selene/) | Static analysis and linting | `aftman install` |
| [StyLua](https://github.com/JohnnyMorganz/StyLua) | Opinionated code formatter | `aftman install` |
| [Lune](https://github.com/lune-org/lune) | Standalone Luau runtime for scripts/CI | `aftman install` |
| [luau-lsp](https://github.com/JohnnyMorganz/luau-lsp) | Language server for editor IntelliSense | binary download |

### Aftman Configuration

```toml
# aftman.toml
[tools]
rojo = "rojo-rbx/rojo@7.4.4"
wally = "UpliftGames/wally@0.3.2"
selene = "kampfkarren/selene@0.27.1"
stylua = "JohnnyMorganz/StyLua@2.0.2"
lune = "lune-org/lune@0.8.0"
```

---

## Rojo: Filesystem Sync

Rojo maps local directories to Roblox services using a `default.project.json` file.

### File Naming Conventions

Rojo determines the Roblox class based on file suffixes:

| Suffix | Roblox Class | Example |
|--------|--------------|---------|
| `*.server.luau` | Script (server) | `Game.server.luau` |
| `*.client.luau` | LocalScript (client) | `Input.client.luau` |
| `*.luau` | ModuleScript | `Utils.luau` |
| `init.luau` | Folder becomes ModuleScript | `Combat/init.luau` |
| `*.model.json` | Rojo model file | `Tree.model.json` |

### Project File

```json
{
  "name": "MyGame",
  "tree": {
    "$path": "src",
    "ReplicatedStorage": {
      "$className": "ReplicatedStorage",
      "Shared": {
        "$path": "shared"
      }
    },
    "ServerScriptService": {
      "$className": "ServerScriptService",
      "$path": "server"
    },
    "StarterPlayer": {
      "StarterPlayerScripts": {
        "$className": "StarterPlayerScripts",
        "$path": "client"
      }
    }
  }
}
```

### Key Commands

```bash
rojo serve                            # Start live sync server
rojo build -o game.rbxl              # Build binary place file
rojo sourcemap default.project.json -o sourcemap.json  # For LSP support
```

---

## Wally: Package Management

Wally manages Luau library dependencies using **realms** to determine where code is accessible.

### Realms

| Realm | Destination | Use for |
|-------|-------------|---------|
| `shared` | ReplicatedStorage | Code used by both server and client |
| `server` | ServerScriptService | Server-only libraries |
| `dev` | Dev dependencies | Testing frameworks, linters |

### Configuration

```toml
# wally.toml
[package]
name = "my-game"
version = "0.1.0"
registry = "https://github.com/UpliftGames/wally-index"
realm = "shared"

[dependencies]
Promise = "evaera/promise@4.0.0"
ProfileService = "loleris/profileservice@1.4.2"
Trove = "sleitnick/trove@0.5.1"
Signal = "sleitnick/signal@1.2.1"

[dev-dependencies]
TestEZ = "roblox/testez@0.4.1"
```

### Popular Packages

| Package | Purpose |
|---------|---------|
| `evaera/promise` | Async control flow with Promises |
| `sleitnick/knit` | Lightweight game framework |
| `loleris/profileservice` | DataStore wrapper with session locking |
| `sleitnick/trove` | Cleanup/lifecycle management |
| `sleitnick/signal` | Typed custom signals |
| `sleitnick/comm` | Typed client-server remotes |
| `roblox/testez` | BDD-style testing framework |

---

## Selene: Linter

Catches bugs and style issues. Requires `std = "roblox"` in config to recognize Roblox globals.

### Configuration

```toml
# selene.toml
std = "roblox"

[rules]
unused_variable = "warn"
shadowing = "warn"
incorrect_standard_library_use = "error"
```

### Commands

```bash
selene src/                    # Lint all source files
selene --no-color src/         # Lint without color (for CI)
```

### Inline Suppression

```luau
-- selene: allow(unused_variable)
local _unused = computeSomething()
```

---

## StyLua: Formatter

Ensures consistent code style across the team.

### Configuration

```toml
# stylua.toml
column_width = 120
line_endings = "Unix"
indent_type = "Spaces"
indent_width = 4
quote_style = "AutoPreferDouble"
call_parentheses = "Always"
```

### Commands

```bash
stylua src/                    # Format all source files
stylua --check src/            # Check formatting (for CI, exits 1 if not formatted)
```

### Inline Ignore

```luau
-- stylua: ignore
local x = {a=1,b=2,c=3}
```

---

## luau-lsp: Editor IntelliSense

Provides type checking, autocompletion, and diagnostics in editors.

### Sourcemap Generation

luau-lsp needs a sourcemap to understand the Roblox instance hierarchy:

```bash
rojo sourcemap default.project.json -o sourcemap.json
```

### VS Code Setup

Install the `luau-lsp` extension. In `.vscode/settings.json`:

```json
{
  "luau-lsp.sourcemap.enabled": true,
  "luau-lsp.sourcemap.autogenerate": true,
  "luau-lsp.sourcemap.rojoProjectFile": "default.project.json",
  "luau-lsp.fflags.enableByDefault": true
}
```

### Roblox Studio Companion Plugin

Optional: the [Luau Language Server Companion](https://www.roblox.com/library/10913122509) sends the Studio DataModel to the language server for non-Rojo projects.

---

## Lune: Standalone Luau Runtime

Runs Luau scripts outside Studio for automation, CI, and tooling.

### Built-in Libraries

```luau
local fs = require("@lune/fs")
local net = require("@lune/net")
local process = require("@lune/process")
local serde = require("@lune/serde")
```

### Example: Simple Test Runner

```luau
-- run-tests.luau
local function runTest(name, testFn)
    local success, err = pcall(testFn)
    if success then
        print("PASS: " .. name)
    else
        warn("FAIL: " .. name .. ": " .. err)
    end
end

runTest("addition", function()
    assert(1 + 1 == 2)
end)
```

---

## .gitignore Essentials

Never commit these:

```gitignore
# Build artifacts
*.rbxl
*.rbxlx

# Wally packages (install, don't commit)
/Packages/

# Sourcemap (regenerated)
sourcemap.json

# Aftman binaries
/.aftman/

# Rojo build output
/build/
```

---

## CI/CD Pipeline

A standard GitHub Actions pipeline should:

1. **Lint** with Selene
2. **Format check** with StyLua
3. **Type check** with `luau-lsp analyze`
4. **Test** with Lune or TestEZ
5. **Build** a `.rbxl` artifact

```yaml
name: CI
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Aftman
        run: |
          curl -LsSf https://raw.githubusercontent.com/nicbarker/aftman/main/install.sh | sh
          echo "$HOME/.aftman/bin" >> $GITHUB_PATH

      - name: Install tools
        run: aftman install

      - name: Lint
        run: selene --no-color src/

      - name: Format check
        run: stylua --check src/

      - name: Type check
        run: |
          rojo sourcemap default.project.json -o sourcemap.json
          luau-lsp analyze --settings .luaurc src/

      - name: Test
        run: lune run tests/run.luau

      - name: Build
        run: rojo build -o build/game.rbxl

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: game-build
          path: build/game.rbxl
```

---

## VS Code Recommended Setup

Install these extensions:

- **luau-lsp** — Type checking, IntelliSense, diagnostics
- **Rojo** — Live sync to Studio
- **Selene** — Inline linting
- **StyLua** — Format on save

Enable in `.vscode/settings.json`:

```json
{
  "luau-lsp.sourcemap.enabled": true,
  "luau-lsp.sourcemap.autogenerate": true,
  "editor.formatOnSave": true,
  "[luau]": {
    "editor.defaultFormatter": "JohnnyMorganz.stylua"
  }
}
```

---

## Common Pitfalls

1. **Committing `/Packages/`.** Bloats the repo and creates noisy diffs. Let Wally install them.
2. **Not committing `wally.lock`.** Without it, different developers may get different package versions.
3. **Missing `selene.toml` with `std = "roblox"`.** Selene won't recognize Roblox globals and will flag false positives.
4. **Stale sourcemap.** Regenerate after adding/removing instances in Studio: `rojo sourcemap ...`
5. **Running `rojo serve` without Studio plugin.** The Rojo Studio plugin must be installed and connected.
6. **Using `init.server.luau` or `init.client.luau`.** Rojo doesn't support these — only `init.luau` (ModuleScript).
7. **Not pinning tool versions in `aftman.toml`.** Different team members get different tool versions.
8. **Forgetting `luau-lsp` binary in CI.** It's not a Wally package; download it separately or via Aftman.

## Quality Checklist

- [ ] `aftman.toml` exists with pinned tool versions
- [ ] `default.project.json` maps all source directories correctly
- [ ] `wally.toml` declares all dependencies; `wally.lock` is committed
- [ ] `selene.toml` has `std = "roblox"`
- [ ] `.gitignore` excludes `/Packages/`, `*.rbxl`, `sourcemap.json`
- [ ] CI runs lint, format check, type check, and tests
- [ ] `rojo sourcemap` is generated for luau-lsp
- [ ] VS Code extensions installed: luau-lsp, Rojo, Selene, StyLua
