# roblox-oauth — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Extended content from the original SKILL.md. See the slimmed SKILL.md for the quick reference.

---

## When to Load (Expanded)

Use this skill when the task is mainly about Roblox OAuth 2.0 delegated authorization for Open Cloud:

- Registering or configuring an OAuth app in Creator Dashboard.
- Choosing between confidential and public client implementations.
- Building the authorization code flow, especially with PKCE.
- Constructing authorization URLs and handling redirect callbacks.
- Exchanging authorization codes, refreshing tokens, introspecting tokens, or revoking sessions.
- Picking the minimum OAuth scopes for a user-authorized integration.
- Validating which resources a token can access after user consent.
- Setting up localhost or sample-app-style development for OAuth testing.
- Debugging OAuth-specific errors, redirect mismatches, token misuse, or scope failures.

Do not use this skill when the task is mainly about:

- General Open Cloud request construction, API keys, webhooks, or non-OAuth cloud automation.
- In-experience scripting architecture, remotes, replication, or gameplay code.
- DataStore or MemoryStore design.

## Decision Rules

- Use this skill if the integration needs user-granted or creator-granted delegated access rather than server-owned API keys.
- Prefer authorization code flow with PKCE for all clients and require PKCE for public clients.
- Treat browser and mobile apps as public clients that cannot safely hold a client secret.
- Treat apps with a secure backend as confidential clients and keep the client secret server-side only.
- Request the minimum scopes needed for the app's actual function.
- Add `openid` when the app needs an ID token, and add `profile` only when it truly needs profile claims.
- If the task shifts to endpoint selection, request shaping, rate limits, or webhooks rather than OAuth mechanics, hand off to `roblox-cloud`.
- If the task shifts to in-experience runtime architecture or persistence design, hand off to the appropriate Roblox skill.
- If a request mixes OAuth with out-of-scope architecture, answer only the OAuth portion and explicitly exclude the rest.

## Instructions

1. Confirm the OAuth use case:
   - User- or creator-delegated access to Open Cloud resources.
   - App type: confidential or public.
   - Whether identity is needed in addition to API access.
2. Register or review the app configuration:
   - Ensure the developer is ID verified if they need to register and publish apps.
   - Record the client ID.
   - Store the client secret immediately and securely if the app is confidential, because Roblox only shows it once.
   - Add only the necessary scopes.
   - Add exact redirect URLs for production and local development.
3. Design the flow before coding:
   - Use authorization code flow.
   - Use PKCE for all clients; it is mandatory for public clients.
   - Generate a fresh high-entropy `state` per authorization attempt.
   - Generate a fresh `code_verifier` and `code_challenge` per authorization attempt.
   - Use `nonce` when OIDC identity binding is relevant.
4. Build the authorization request correctly:
   - Send users to `https://apis.roblox.com/oauth/v1/authorize`.
   - Include `client_id`, `redirect_uri`, `scope`, and `response_type=code`.
   - Include `code_challenge` and `code_challenge_method=S256` for PKCE.
   - Do not expose a confidential client secret in browser or mobile code.
5. Handle the callback defensively:
   - Verify the returned `state` before using the `code`.
   - Handle both success (`code`) and failure (`error`, `error_description`) query parameters.
   - Treat the authorization code as short-lived and single-use.
6. Exchange the code for tokens at `POST /oauth/v1/token`:
   - Use `application/x-www-form-urlencoded`.
   - Send the code, client ID, grant type, and either `code_verifier` or confidential-client credentials.
   - Store refresh tokens only on trusted server-side systems.
7. Manage token lifecycle explicitly:
   - Access tokens last about 15 minutes.
   - Refresh tokens last about 90 days and are single-use for refresh.
   - Replace the stored refresh token atomically after every successful refresh response.
   - Revoke sessions with `POST /oauth/v1/token/revoke` when disconnecting an app.
8. Validate what the token can actually do:
   - Use `GET /oauth/v1/userinfo` for identity claims.
   - Use `POST /oauth/v1/token/resources` when the app must confirm resource-level access granted by the user.
   - Use `POST /oauth/v1/token/introspect` only for token activity and claims; it is not a substitute for resource authorization checks.
9. Keep scope and risk tight:
   - Match scopes to actual endpoints and resource ownership needs.
   - Treat medium, high, and critical endpoint categories as a least-privilege warning signal during design and review.
   - Avoid expanding the skill into general Open Cloud endpoint implementation.
10. Keep the response inside scope:
   - Focus on app registration, auth flow design, tokens, scopes, local development, and OAuth-specific errors.
   - Do not drift into API-key-first cloud integrations, gameplay architecture, or data-service design.

## Using References

This skill keeps its complete guidance in this `references/full.md` file. Use the official OAuth 2.0 overview listed in `SKILL.md` for current endpoint, scope, redirect, and app-registration details. Do not infer that topic-specific local reference files exist unless they are present in this skill directory.

## Checklist

- The task actually requires delegated OAuth access, not API-key-based automation.
- The client is classified correctly as confidential or public.
- PKCE is included, or the design is rejected if a public client tries to skip it.
- Redirect URLs are exact matches and valid for the intended environment.
- Requested scopes are minimal and match the integration's real behavior.
- `openid` is included only when identity data or an ID token is needed.
- `state` is generated, stored, and verified on callback.
- The authorization code is exchanged promptly and only once.
- Access and refresh token storage stays off untrusted clients.
- Refresh token rotation is handled by replacing the stored refresh token after refresh.
- The app uses `userinfo`, `introspect`, and `token/resources` for their distinct purposes.
- The guidance stays out of general Open Cloud request mechanics, gameplay scripting, and data architecture.

## Common Mistakes

- Using API keys and OAuth interchangeably instead of choosing the auth model first.
- Shipping a confidential client secret in frontend or mobile code.
- Skipping PKCE, especially for public clients.
- Forgetting to verify `state` on the callback.
- Assuming a refresh token can be reused multiple times after a successful refresh.
- Forgetting that authorization codes expire quickly and are single-use.
- Requesting `profile` without `openid`.
- Requesting broad scopes during development instead of the minimum required set.
- Assuming token introspection proves resource ownership or consented resource coverage.
- Adding or changing scopes without reauthorizing users.
- Treating non-OAuth Open Cloud issues as part of this skill instead of handing them to `roblox-cloud`.

## Examples

### Public web or mobile app

- Use authorization code flow with PKCE.
- Keep all secrets off the client.
- Verify `state`, exchange the code on a trusted backend when possible, and store refresh tokens securely.

### Confidential server app

- Register the app, store the secret once, and still use PKCE.
- Use the server to exchange codes, refresh tokens, and call Open Cloud with bearer tokens.

### Local development

- Register the exact callback URL your app serves, such as `http://localhost:<port>/redirect` for local testing.
- Store client ID and secret in environment variables.
- Test the full login, callback, token exchange, refresh, and logout or revoke path before requesting more scopes or review.
