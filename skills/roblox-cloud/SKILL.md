---
name: roblox-cloud
description: Open Cloud REST API, API keys, webhooks, HttpService constraints, scope selection.
last_reviewed: 2026-05-27
sources:
  - https://create.roblox.com/docs/reference/cloud/open-cloud
---

# roblox-cloud

## When to Load

Load this skill when the task involves Roblox Open Cloud REST APIs, API-key authentication, webhook setup, or HttpService calls to Open Cloud endpoints. Skip it for OAuth flows (use roblox-oauth), persistent data design (use roblox-data), gameplay networking (use roblox-networking), or pure engine API lookups (use roblox-studio-mcp).

## Quick Reference

### Open Cloud REST APIs
- Base: `https://apis.roblox.com/cloud/v2/…` (v1 for legacy)
- Auth: `x-api-key: <API_KEY>` header for server-to-server
- Content-Type: `application/json` for bodies
- Pagination: read `nextPageToken`, pass it back as `pageToken` query param
- Update masks: use `updateMask` query param for partial PATCH
- Long-running ops: poll the returned Operation resource with exponential backoff
- Error codes: `INVALID_ARGUMENT` (bad input), `PERMISSION_DENIED`/`INSUFFICIENT_SCOPE` (auth), `RESOURCE_EXHAUSTED`/429 (rate limit → backoff), `UNAVAILABLE` (transient → retry)

### API Keys
- Use for: CI jobs, bots, web backends, in-experience automation (non-user)
- Each key has scoped permissions—confirm required scopes before coding
- Creator permissions AND key scopes must both allow the action
- Never store keys as plain text in experiences—use Secrets

### Webhooks
- Requires public HTTPS POST endpoint
- Return 2XX within 5 seconds; process event async
- Verify `roblox-signature` header when secret is configured
- Deduplicate by `NotificationId`—deliveries may repeat
- Reject stale timestamps

### HttpService Constraints (in-experience)
- Only certain Open Cloud endpoints are supported
- Allowed headers: `x-api-key`, `Content-Type` ONLY
- API key must come from a Secret (not plain string)
- HTTPS only; path params cannot contain `..`
- Check endpoint support before coding

### Handoffs
- OAuth / user consent → `roblox-oauth`
- Data schema / DataStore design → `roblox-data`
- Remotes / networking → `roblox-networking`
- Engine API lookup only → `roblox-studio-mcp`

### References
- `references/full.md` — complete instructions, decision rules, checklist, common mistakes, examples
- `references/` — per-topic docs: open-cloud-overview, api-patterns-errors-types-scopes-and-rate-limits, webhooks-documentation, http-service, openapi-documentation, cloud-reference-json-files
