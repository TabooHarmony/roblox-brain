# roblox tooling: full reference

Tooling should make the source tree reproducible without forcing every project into the same framework. Keep the repository's chosen tools visible in its manifest and CI.

## 1. Decide what the project needs

| Need | Useful tool | Keep in mind |
| --- | --- | --- |
| file-to-Studio sync or build | Rojo | define the data-model mapping in a project file |
| third-party packages | Wally | commit the manifest and lockfile; choose realms intentionally |
| Luau linting | Selene | configure the Roblox standard and project exceptions |
| formatting | StyLua | pin the formatter and run a check in CI |
| standalone scripts | Lune | use only where its runtime libraries are appropriate |
| tool versions | Aftman or an existing manager | one source of truth for versions |
| editor navigation | luau-lsp plus a sourcemap | regenerate the map when the tree changes |

If the project already has a working toolchain, extend it before introducing another manager.

## 2. Rojo project mapping

A Rojo project file maps filesystem paths to Roblox services. Keep the mapping small and obvious.

```json
{
  "name": "ExampleGame",
  "tree": {
    "$className": "DataModel",
    "ReplicatedStorage": {
      "$path": "src/ReplicatedStorage"
    },
    "ServerScriptService": {
      "$path": "src/ServerScriptService"
    },
    "StarterPlayer": {
      "StarterPlayerScripts": {
        "$path": "src/StarterPlayer/StarterPlayerScripts"
      }
    }
  }
}
```

File suffixes communicate the Roblox instance type in the usual Rojo workflow:

- `.server.luau` maps to a server `Script`;
- `.client.luau` maps to a client `LocalScript`;
- `.luau` maps to a `ModuleScript`;
- `init.luau` can represent a module at a folder boundary.

Use the exact conventions documented by the project's Rojo version. Test both `rojo serve` for development and `rojo build` for a reproducible artifact.

## 3. Packages with Wally

A package manifest should state whether a dependency is shared, server-only, client-only, or development-only. Keep the lockfile under version control so CI resolves the same graph.

```toml
[package]
name = "team/example-game"
version = "0.1.0"
registry = "https://github.com/UpliftGames/wally-index"
realm = "shared"

[dependencies]
Promise = "evaera/promise@4.0.0"

[dev-dependencies]
TestEZ = "roblox/testez@0.4.2"
```

The names and versions above are examples, not recommendations. Verify package ownership, license, compatibility, and the project's existing conventions before adding a dependency. Do not copy a package into the repository just to avoid documenting it.

## 4. Pin the toolchain

Aftman is archived and should be treated as legacy compatibility. If an existing repository already uses `aftman.toml`, keep its versions pinned and avoid an unrelated migration during feature work. For a new project, evaluate a maintained manager such as Rokit or another toolchain that the team can support.

An existing Aftman manifest can look like this:
```toml
[tools]
rojo = "rojo-rbx/rojo@7.7.0"
wally = "UpliftGames/wally@0.3.2"
selene = "kampfkarren/selene@0.31.0"
stylua = "JohnnyMorganz/StyLua@2.5.2"
lune = "lune-org/lune@0.10.5"
```

Use versions tested by the repository. Update them deliberately, review generated lockfile changes, and record compatibility failures rather than silently floating to the newest release.

## 5. Selene

Configure the Roblox standard and keep suppressions narrow.

```toml
std = "roblox"

[rules]
unused_variable = "warn"
shadowing = "warn"

[config]
allow_defined_top = true
```

Run `selene src` locally and in CI. Prefer a named configuration or a small inline suppression with a reason over disabling a rule for the whole project.

## 6. StyLua

Formatting is a repository convention. Keep the configuration short and run the formatter in check mode in automation.

```toml
column_width = 100
indent_type = "Spaces"
indent_width = 4
quote_style = "AutoPreferDouble"
call_parentheses = "Always"
```

Use `stylua --check .` in CI and `stylua .` only as an explicit developer action. Do not mix formatter changes with a gameplay change unless the repository expects format-on-save commits.

## 7. Lune and standalone scripts

Lune is useful for file transforms, test orchestration, and small repository utilities. Keep Roblox-only code out of scripts that must run without Studio.

```luau
local fs = require("@lune/fs")
local serde = require("@lune/serde")

local manifest = serde.decode("json", fs.readFile("manifest.json"))
print(manifest.name)
```

A Lune script is not automatically a Roblox runtime script. Document which APIs it expects and make its inputs and outputs testable from CI.

## 8. Sourcemaps and editor support

If the editor needs Roblox-aware type information, generate a sourcemap from the same Rojo project file used for development. Treat the generated map as disposable build output unless the repository explicitly versions it.

Regenerate it after adding services, moving modules, or changing suffixes. A stale map can make correct code look broken and can hide incorrect paths.

## 9. CI sequence

A small pipeline can use this order:

1. install the pinned tools;
2. restore or install Wally dependencies;
3. run Selene;
4. run StyLua in check mode;
5. generate a sourcemap if luau-lsp analysis is enabled;
6. run standalone Lune tests or project tests;
7. run `rojo build` and inspect the artifact boundary.

Keep credentials out of project files and CI logs. If a build needs a Roblox API credential, inject it through the CI secret store and use the narrowest scope available.

## 10. Ignore generated output

The exact list depends on the project, but commonly generated paths include:

```gitignore
/Packages/
/.aftman/
/build/
sourcemap.json
*.rbxl
```

Do not ignore source, lockfiles, configuration, or test fixtures by accident. Check `git status` after installing tools and packages.

## Tooling checklist

- [ ] The project has one documented source-to-Studio workflow.
- [ ] Tool versions are pinned and tested.
- [ ] Dependencies have explicit realms and licenses.
- [ ] Lint and format checks run without rewriting files in CI.
- [ ] Sourcemaps and build artifacts have a clear ownership policy.
- [ ] Standalone scripts declare their runtime assumptions.
- [ ] CI produces a reproducible build or reports why it cannot.
