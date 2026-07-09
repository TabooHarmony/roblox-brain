---
name: roblox-oauth
description: "Use when implementing Roblox OAuth 2.0 for Open Cloud, including app registration, PKCE, token exchange, refresh, revocation, or scopes."
last_reviewed: 2026-05-27
sources:
  - https://create.roblox.com/docs/cloud/auth/oauth2-overview
---

# roblox-oauth

## When to Load

Load this skill when the task centers on Roblox OAuth 2.0 delegated authorization for Open Cloud — app registration, authorization code flow with PKCE, token exchange/refresh/revocation, scope selection, or OAuth-specific error debugging. Skip it for API-key automation, in-experience scripting, or general Open Cloud endpoint work (use `roblox-cloud` instead).

## Quick Reference

### Flow Selection
- **Auth Code + PKCE** — required for public clients (browser/mobile), recommended for all.
- **Confidential** — backend holds `client_secret`; never expose in frontend code.
- **Public** — no secret; PKCE mandatory.

### PKCE Essentials
- Generate `code_verifier` (43–128 char random) + `code_challenge` (SHA-256, base64url).
- Send `code_challenge` + `code_challenge_method=S256` in authorize; send `code_verifier` in token exchange.
- One verifier per authorization attempt.

### Authorization URL
`GET https://apis.roblox.com/oauth/v1/authorize`
Params: `client_id`, `redirect_uri`, `scope`, `response_type=code`, `code_challenge`, `code_challenge_method=S256`, `state`, optional `nonce`.

### Token Exchange
`POST /oauth/v1/token` — `application/x-www-form-urlencoded`
Params: `grant_type=authorization_code`, `code`, `client_id`, `code_verifier` (public) or `client_secret` (confidential).

### Token Lifecycle
- **Auth code** — seconds, single-use; exchange immediately.
- **Access token** — ~15 min; use as Bearer.
- **Refresh token** — ~90 days; single-use per refresh. Replace stored token atomically after each refresh.
- **Revoke**: `POST /oauth/v1/token/revoke` on disconnect.

### Scope Selection
- Minimum scopes matching actual endpoint needs.
- `openid` → ID token; `profile` only if profile claims needed.
- Medium/high/critical risk = least-privilege review signal.
- Changing scopes requires reauthorization.

### Validation Endpoints
- `GET /oauth/v1/userinfo` — identity claims.
- `POST /oauth/v1/token/introspect` — token activity (not resource auth).
- `POST /oauth/v1/token/resources` — resource-level access.

### Key Rules
- Verify `state` before using returned code.
- Refresh tokens: server-side only.
- PKCE even for confidential clients.
- Don't mix API keys and OAuth.
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
