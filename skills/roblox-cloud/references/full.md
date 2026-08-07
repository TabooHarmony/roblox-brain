# Roblox Open Cloud: Full Reference

> Adapt endpoint paths, scopes, and schemas from the current Open Cloud reference. Never infer them from examples for another resource.

## 1. Classify the integration

Identify both caller and authority before writing requests:

- **Owner automation:** backend, CI, bot, or trusted in-experience call acting with an API key.
- **Delegated application:** third-party app acting after a user grants OAuth access to selected resources.
- **Webhook receiver:** public HTTPS endpoint receiving retryable Roblox notifications.
- **In-experience caller:** `HttpService` calling an endpoint Roblox explicitly supports from an experience.

Use `roblox-data` for persistence architecture, `roblox-networking` for gameplay remotes, and `roblox-studio-mcp` for Studio control.

## 2. Authentication decision

### API keys

Use an API key when trusted automation acts for its owner and does not need per-user consent.

Before implementation:

1. identify the exact resource and operation;
2. confirm creator or group permission;
3. grant only the required key scopes and resources;
4. store the key in a secret manager or Roblox Secret;
5. plan rotation and revocation;
6. keep it out of source, logs, URLs, replicated storage, and client code.

A valid key does not override missing creator permission or an endpoint's resource restrictions.

### OAuth 2.0

Use OAuth when an app needs user-granted access to specific Roblox resources. Roblox supports authorization code flow and its PKCE extension.

- **Public client:** cannot safely hold a client secret. PKCE is required.
- **Confidential client:** exchanges codes through a trusted backend and keeps its client secret there. Use PKCE as defense in depth.

A user must be at least 13 to authorize OAuth apps. App registration and publishing require an ID-verified developer. Verify current quota and review requirements in Creator Dashboard.

Do not mix API-key and OAuth credentials in one request or treat them as interchangeable fallback credentials.

## 3. OAuth implementation

### Register the app

Record the client ID and store a confidential client secret when it is issued. Configure exact redirect URLs. Request only scopes needed by actual product behavior. Add `openid` when the app needs an ID token and `profile` only for profile claims.

### Start authorization

For every attempt:

1. create cryptographically random `state` and store it with the pending session;
2. create a fresh PKCE verifier and SHA-256 base64url challenge;
3. send the user to `https://apis.roblox.com/oauth/v1/authorize`;
4. include `client_id`, exact `redirect_uri`, `scope`, `response_type=code`, and PKCE fields;
5. use `nonce` when OIDC identity binding requires it.

Never put a confidential client secret in the authorization URL or frontend bundle.

### Handle the callback

Reject callbacks whose `state` does not match the pending attempt. Handle explicit OAuth errors. Treat the authorization code as short-lived and single-use, then exchange it at `POST /oauth/v1/token` using `application/x-www-form-urlencoded`.

The exchange uses the original PKCE verifier for public clients. Confidential clients authenticate from their backend. Do not log codes or token responses.

### Store and rotate tokens

Keep access and refresh tokens in trusted storage. Refresh tokens rotate: after a successful refresh, atomically replace the stored token before using the new session. Concurrent refresh attempts need one owner so an older response cannot overwrite the newest token.

Reauthorize when scopes change. Revoke tokens when the user disconnects the app or credentials are suspected compromised.

Endpoint roles are distinct:

- `userinfo`: OIDC identity claims;
- `introspect`: token activity and claims, not proof of resource authorization;
- `token/resources`: resources the user granted to the token;
- protected endpoint: final enforcement of scope, resource, and operation.

## 4. REST request mechanics

Confirm from the current reference:

- API version and path template;
- path and query parameter types;
- request and response schema;
- required scopes and resource grants;
- endpoint-specific quotas;
- whether an Operation resource is returned;
- whether the endpoint is callable from `HttpService`.

Current resources generally use `https://apis.roblox.com/cloud/v2/...`; some APIs remain on legacy surfaces. Do not rewrite a documented path to match a preferred version.

### Pagination

Read `nextPageToken` and return it as `pageToken` while preserving the other filters and ordering. A token belongs to the original query. Do not reuse it after changing filters.

### Partial updates

Use `updateMask` only for fields intended to change. Match field paths exactly to the endpoint schema. Do not send a broad mask merely because the request body contains defaults.

### Long-running operations

If an endpoint returns an Operation, poll that resource. Use bounded exponential backoff with jitter and a deadline. Surface terminal operation errors rather than reporting the initial request as success.

### Errors and retries

- `INVALID_ARGUMENT`: repair IDs, filters, masks, headers, or body shape.
- `PERMISSION_DENIED` / `INSUFFICIENT_SCOPE`: inspect creator permission, key scope, OAuth scope, and resource grant separately.
- `RESOURCE_EXHAUSTED` / HTTP 429: honor `Retry-After` when present and reduce request pressure.
- `UNAVAILABLE` and transport failures: retry within a bounded policy.

Retry only transient failures. Authentication, authorization, and validation failures need correction, not repetition. Give non-idempotent operations an idempotency boundary before retrying.

## 5. In-experience HttpService

An Open Cloud endpoint is not automatically callable from an experience. Confirm current engine support before coding.

For supported calls:

- use HTTPS;
- retrieve `x-api-key` from a Roblox Secret rather than a plain string;
- send only headers supported by the engine and endpoint;
- validate path parameters and reject traversal-like input;
- keep the call server-side;
- bound retries and request volume.

Do not route a request through a client to bypass server-side restrictions.

## 6. Webhooks

Treat delivery as at-least-once and potentially delayed:

1. expose a public HTTPS POST endpoint;
2. verify the "roblox-signature" header when a webhook secret is configured;
3. validate the delivery timestamp and reject stale requests according to the integration policy;
4. deduplicate by notification ID in durable or shared state;
5. persist or enqueue accepted work;
6. return a success response quickly;
7. process slow side effects asynchronously.

The exact signature algorithm and headers belong to the current webhook documentation. Do not invent verification from a generic webhook provider.

Deduplication must survive process restarts if repeating the side effect would be harmful. A memory-only set is insufficient for durable grants or destructive actions.

## 7. Security review

Before shipping, verify:

- no credential or token appears in source, URLs, browser bundles, replicated instances, analytics, or ordinary logs;
- redirect URLs are exact and controlled by the app owner;
- `state` is bound to one pending authorization attempt;
- PKCE verifier and challenge are fresh per attempt;
- requested scopes match user-visible behavior;
- token rotation is atomic and concurrency-safe;
- API keys are resource-scoped and revocable;
- webhook verification happens before side effects;
- retries cannot duplicate non-idempotent work;
- permission failures are not hidden by fallback credentials.

## 8. Diagnostic workflow

When a request fails, record the endpoint, request ID, status, Roblox error code, and safe response details. Never record secrets or full tokens.

Diagnose in this order:

1. correct domain, version, path, method, and content type;
2. valid credential type for this endpoint;
3. creator or group permission;
4. key scopes or OAuth scopes;
5. OAuth resource grants;
6. request schema and update mask;
7. quota and retry headers;
8. operation status for asynchronous calls.

Do not broaden scopes until the failing permission boundary is identified.

## 8.5 Ads Manager API (Open Cloud, test stage)

<!-- temporal: 2026-08 -->

Roblox announced an Ads Manager API on Open Cloud (DevForum, 2026-07-30, test stage) for programmatic campaign management: create/update/pause/resume/cancel campaigns, check delivery status, list billing accounts and creatives. It authenticates with an API key (`x-api-key`) or OAuth2 using scopes such as `ad.campaign:read`, `ad.campaign:write`, and `ad.billing:read`, and campaign creates take an `x-idempotency-key` header.

This is a marketing-surface API, not an in-experience engine API: it lives on the Open Cloud side, so the standard rules of this skill apply (least-privilege keys, no keys in game code, server-side storage). As a test-stage API it may change before Beta; verify the current surface against the official docs before building on it, and treat anything beyond campaign CRUD as unverified.

## 9. Completion checklist

- Caller and authority model are explicit.
- Authentication choice matches the use case.
- Endpoint path, schema, scopes, resources, and quotas came from current documentation.
- Secrets remain in trusted storage.
- OAuth callback, PKCE, token rotation, and revocation paths are covered when applicable.
- Pagination and long-running operations are handled.
- Retry policy is bounded and limited to safe/transient cases.
- HttpService support is confirmed for in-experience calls.
- Webhook verification, deduplication, and fast acknowledgment are covered.
- Failure reports distinguish authentication, permission, resource grant, schema, and quota errors.
