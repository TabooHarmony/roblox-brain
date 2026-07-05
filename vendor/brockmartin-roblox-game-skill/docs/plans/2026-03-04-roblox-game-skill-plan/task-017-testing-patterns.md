# Task 017: Write testing-patterns.md

**depends-on:** 001
**phase:** 3 - Specialized References
**files:** `references/testing-patterns.md`

## Description

Write a testing reference covering TestEZ, module testing, MCP-powered testing, and CI/CD integration.

## What To Do

1. **Overview** — When to load (writing tests, setting up testing, CI/CD)
2. **TestEZ Framework** — Installation (Wally), test file conventions, describe/it/expect syntax, beforeEach/afterEach, test suites
3. **Unit Testing ModuleScripts** — Testing pure logic modules, mocking Roblox services, dependency injection for testability
4. **Integration Testing** — Testing interactions between modules, testing RemoteEvent flows, testing DataStore operations
5. **MCP-Powered Testing** — Using MCP playtest tools to run the game, capture console output, verify behavior, automated smoke tests
6. **Manual Testing Workflows** — Playtesting checklist, multi-player testing (Studio test server), edge case testing
7. **Mocking Roblox Services** — Creating test doubles for Players, DataStoreService, MarketplaceService, common mock patterns
8. **Test Organization** — Where to put tests, naming conventions, test-to-module mapping
9. **CI/CD Integration** — Running tests with Lune/Lemur in CI, GitHub Actions setup, automated linting + formatting + testing pipeline
10. **Best Practices** — Test critical paths (data save/load, purchases, combat), keep tests fast, test server-side validation logic
11. **Anti-Patterns** — Testing only in Studio manually, no tests for monetization code, untestable tightly-coupled modules

Include TestEZ example code for testing a currency module.

## Verification

- File exists at `references/testing-patterns.md`
- TestEZ syntax and setup documented
- Mocking patterns for Roblox services included
- CI/CD pipeline example included
- MCP testing workflow documented
