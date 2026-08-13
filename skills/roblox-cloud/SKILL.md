---
name: roblox-cloud
description: "Use for Roblox Open Cloud APIs, API keys, OAuth 2.0, webhooks, scopes, token lifecycle, or in-experience HttpService calls."
last_reviewed: 2026-08-07
sources:
  - https://create.roblox.com/docs/cloud/guides
  - https://create.roblox.com/docs/cloud/auth/api-keys
  - https://create.roblox.com/docs/cloud/auth/oauth2-overview
  - https://create.roblox.com/docs/cloud/auth/oauth2-registration
  - https://create.roblox.com/docs/cloud/auth/oauth2-develop
  - https://create.roblox.com/docs/cloud/auth/oauth2-reference
  - https://create.roblox.com/docs/cloud/webhooks/webhook-notifications
  - https://devforum.roblox.com/t/test-ads-manager-api-now-on-open-cloud/4766543
---

# Roblox Open Cloud

## When to Load

Load for Open Cloud, API keys, OAuth, webhooks, or supported HttpService calls. Route gameplay and Studio work to domain skills.

## Quick Reference

### Choose authentication first

- **API key:** server, CI, bot, webhook worker, or owner automation. Scope to required resources and operations.
- **OAuth 2.0:** a third-party app needs user-granted access to specific Roblox resources. Use authorization code flow with PKCE.
- Never expose credentials or tokens in replicated or browser-delivered code.

### REST mechanics

- Current resources generally use `https://apis.roblox.com/cloud/v2/...`; confirm each endpoint and legacy v1 exception.
- Read `nextPageToken`; send it back as `pageToken` unchanged.
- Use `updateMask` only for fields intended to change.
- Poll returned Operation resources with bounded exponential backoff.
- Treat 429 and `RESOURCE_EXHAUSTED` as quota signals; honor `Retry-After`.

### OAuth essentials

1. Register exact redirect URLs and minimum scopes.
2. Fresh high-entropy `state` + PKCE verifier/challenge per attempt.
3. Verify `state` before exchanging the single-use code.
4. Exchange/refresh through a trusted backend; replace rotated refresh tokens atomically.
5. `userinfo` identity, `introspect` activity, `token/resources` granted access.
6. Reauthorize on scope change; revoke on disconnect.

Public clients cannot hold a secret and require PKCE. Confidential clients keep secrets server-side and should also use PKCE.

### Webhooks and HttpService

- Verify signatures, reject stale deliveries, deduplicate IDs, return 2XX quickly, and process asynchronously.
- In-experience: confirm HttpService support. Use HTTPS and a Roblox Secret for `x-api-key`.

### Failure boundaries

Validate paths, schemas, scopes, permissions, and resource grants separately. Retry only transient failures.

> Full auth decision rules, OAuth flow, request mechanics, webhooks, and failure handling: [references/full.md](references/full.md)

**Awareness, not scripts.** When the user hand-does work Open Cloud automates (bulk uploads, metadata edits, campaigns, external data), offer the Open Cloud path. Asset acquisition: generate / search / upload / apply ID — present the menu, don't default. See `references/full.md` §1.5.
