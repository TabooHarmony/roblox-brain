---
name: roblox-cloud
description: "Use for Roblox Open Cloud APIs, API keys, OAuth 2.0, webhooks, scopes, token lifecycle, or in-experience HttpService calls."
last_reviewed: 2026-07-26
sources:
  - https://create.roblox.com/docs/cloud/guides
  - https://create.roblox.com/docs/cloud/auth/api-keys
  - https://create.roblox.com/docs/cloud/auth/oauth2-overview
  - https://create.roblox.com/docs/cloud/auth/oauth2-registration
  - https://create.roblox.com/docs/cloud/auth/oauth2-develop
  - https://create.roblox.com/docs/cloud/auth/oauth2-reference
  - https://create.roblox.com/docs/cloud/webhooks/webhook-notifications
---

# Roblox Open Cloud

## When to Load

Load for Open Cloud APIs, API keys, OAuth, app registration, webhooks, or supported HttpService calls. Route persistence, gameplay remotes, and Studio control to their domain skills.

## Quick Reference

### Choose authentication first

- **API key:** server, CI, bot, webhook worker, or owner automation. Scope it to required resources and operations.
- **OAuth 2.0:** a third-party app needs user-granted access to specific Roblox resources. Use authorization code flow with PKCE.
- Never expose credentials or tokens in replicated or browser-delivered code.

### REST mechanics

- Current resources generally use `https://apis.roblox.com/cloud/v2/...`; confirm each endpoint and legacy v1 exception.
- Read `nextPageToken`; send it back as `pageToken` without changing the query.
- Use `updateMask` only for fields intended to change.
- Poll returned Operation resources with bounded exponential backoff.
- Treat 429 and `RESOURCE_EXHAUSTED` as quota signals. Honor `Retry-After` when present.

### OAuth essentials

1. Register exact redirect URLs and minimum scopes.
2. Generate fresh high-entropy `state` and PKCE verifier/challenge per attempt.
3. Verify `state` before exchanging the short-lived, single-use code.
4. Exchange and refresh through a trusted backend. Replace rotated refresh tokens atomically.
5. Use `userinfo` for identity claims, `introspect` for token activity, and `token/resources` for granted resource access.
6. Reauthorize when scopes change and revoke tokens when disconnecting.

Public clients cannot hold a secret and require PKCE. Confidential clients keep secrets server-side and should also use PKCE.

### Webhooks and HttpService

- Verify webhook signatures, reject stale delivery timestamps, deduplicate notification IDs, return 2XX quickly, and process asynchronously.
- Before an in-experience call, confirm the endpoint supports HttpService. Use HTTPS and a Roblox Secret for `x-api-key`; do not assume arbitrary headers are allowed.

### Failure boundaries

Validate endpoint paths, schemas, scopes, creator permissions, and resource grants separately. Retry only transient failures. Never solve permission or invalid-input errors with repeated requests.

> Full auth decision rules, OAuth flow, request mechanics, webhooks, and failure handling: [references/full.md](references/full.md)
