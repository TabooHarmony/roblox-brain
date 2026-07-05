# Task 014: Write tooling-ecosystem.md

**depends-on:** 001
**phase:** 3 - Specialized References
**files:** `references/tooling-ecosystem.md`

## Description

Write a tooling reference covering Rojo, Wally, Selene, StyLua, Git workflows, and external development tooling.

## What To Do

1. **Overview** — When to load (setting up Rojo, external tooling, CI/CD, package management)
2. **Rojo** — What it is (filesystem sync to Studio), setup/installation, project.json configuration, file naming conventions (.server.luau, .client.luau, .luau), syncing workflow, two-way sync
3. **Wally** — Package manager for Roblox, wally.toml configuration, installing packages, common packages (Promise, ProfileService, Knit, TestEZ), publishing packages
4. **Selene** — Luau linter, configuration (selene.toml), Roblox-specific lints, custom rules, CI integration
5. **StyLua** — Luau formatter, configuration (stylua.toml), format-on-save setup, CI integration
6. **Git Workflows** — Version control for Roblox projects via Rojo, branching strategies, .gitignore for Roblox projects, collaborative development
7. **VS Code Setup** — Extensions (Luau LSP, Rojo, Selene), settings.json configuration, debugging setup
8. **CI/CD** — GitHub Actions for linting/formatting, automated testing with TestEZ + Lemur/Lune, deployment workflows
9. **Rojo Project Templates** — Starter project structures for solo dev and team projects
10. **Best Practices** — Use external tooling for professional projects, automate code quality checks, version control everything
11. **Anti-Patterns** — Editing only in Studio without version control, manual code formatting, no linting

## Verification

- File exists at `references/tooling-ecosystem.md`
- Rojo setup includes project.json examples
- Wally includes common package list
- Git workflow includes .gitignore template
- CI/CD pipeline example included
