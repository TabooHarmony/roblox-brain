# Task 032: Write code-review.md Workflow

**depends-on:** 001
**phase:** 5 - Workflows
**files:** `workflows/code-review.md`

## Description

Write the code quality review workflow.

## What To Do

1. **Step 1: Project Scan** — MCP: get_project_structure + get_file_tree for overview. Offline: Ask user to describe structure
2. **Step 2: Organization Review** — Check: scripts in correct locations, proper use of services, clean folder structure, module naming conventions
3. **Step 3: Code Quality Scan** — MCP: grep_scripts for anti-patterns. Check for:
   - Deprecated APIs (wait(), spawn(), delay())
   - Global variable usage
   - Missing type annotations on public functions
   - Inconsistent naming conventions
   - Dead code / unreachable code
   - Duplicate code across scripts
4. **Step 4: Architecture Review** — Check module boundaries, dependency direction, circular requires, separation of concerns
5. **Step 5: Security Quick-Check** — Quick scan for unvalidated remotes, client-trusted logic (refer to security-audit for deep review)
6. **Step 6: Performance Quick-Check** — Quick scan for common perf issues (refer to performance-audit for deep review)
7. **Step 7: Quality Report** — Rate overall quality (A-F), list findings by severity, provide specific fix for each finding
8. **Step 8: Refactoring Suggestions** — If significant issues found, suggest refactoring priorities

## Verification

- File exists at `workflows/code-review.md`
- Covers organization, quality, architecture, security, performance
- Specific anti-patterns to search for listed
- Produces rated quality report
- MCP and offline paths documented
