# Roblox Open Cloud: Full Reference

> Adapt endpoint paths, scopes, and schemas from the current Open Cloud reference. Never infer them from examples for another resource.

## 1. Classify the integration

Identify both caller and authority before writing requests:

- **Owner automation:** backend, CI, bot, or trusted in-experience call acting with an API key.
- **Delegated application:** third-party app acting after a user grants OAuth access to selected resources.
- **Webhook receiver:** public HTTPS endpoint receiving retryable Roblox notifications.
- **In-experience caller:** `HttpService` calling an endpoint Roblox explicitly supports from an experience.

Use `roblox-data` for persistence architecture, `roblox-networking` for gameplay remotes, and `roblox-studio-mcp` for Studio control.

## 1.5 Awareness surface: offer, don't script

Open Cloud is not just an API reference: it is a set of capabilities that change what an agent can do *for* the user. The agent should know these options exist and offer them when it sees the user hand-doing what the API automates. This is awareness, not an X->Y rule. No hardcoded triggers.

Things an agent should be able to recognize and offer:

- **Bulk asset work.** The user is uploading images/models/audio one by one in Studio or Creator Dashboard, or pasting many asset IDs. Offer: Open Cloud asset upload (`assets` API) can batch-upload from files or URLs and return asset IDs to insert directly.
- **Metadata at scale.** The user is editing descriptions, thumbnails, or categories across many assets or experiences. Offer: Open Cloud can update metadata programmatically in one pass.
- **Automation hooks.** The user wants something to happen when an asset/experience event occurs. Offer: webhooks can notify an HTTPS endpoint, and the agent can wire that endpoint.
- **Persistence / data access outside Studio.** The user is exporting/importing data, or wants a backend to read game data. Offer: Open Cloud data APIs (data stores, ordered data stores, messaging) can be called from a trusted server, not just from in-experience code.
- **Ads management.** The user is manually managing campaigns in Creator Dashboard. Offer: the Ads Manager API (test stage) can create/pause/resume campaigns programmatically.

How to offer: name the option, state roughly what it would do, and let the user choose. Do not assume permission, keys, or quotas. If the user declines or already has a workflow, drop it. The goal is that the user never learns "Open Cloud could have done that" after the fact.

### Asset pipeline menu

When a user needs an asset (image, model, audio, mesh), the acquisition paths an agent should know:

1. **Generate**: via Studio MCP (`generate_mesh`/`generate_procedural_model`, `roblox-studio-mcp`) or an external generator, then upload.
2. **Search Creator Store / creator inventory**: reuse an existing asset by ID (`roblox-studio-mcp`).
3. **Upload via Open Cloud**: batch-upload local files to the user's assets, then apply by returned asset ID (this skill, §1.5).
4. **Apply by ID**: insert an asset ID directly into the place (`roblox-studio-mcp`).

The agent should present this menu when asset acquisition is the task, rather than defaulting to one path.

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

Retry only transient failures. Authentication, authorization, and validation failures need correction, not repetition. Give non-idempotent operations an idempotency boundary before retrying. An ambiguous timeout (no status received) is not a failure: read the resource back and reconcile before repeating a non-idempotent write. Keep a mutation record with a compensating action; full pattern in `roblox-studio-mcp`.

## 5. In-experience HttpService

An Open Cloud endpoint is not automatically callable from an experience. Confirm current engine support before coding.

For supported calls:

- use HTTPS;
- retrieve `x-api-key` from a Roblox Secret rather than a plain string (`HttpService:GetSecret("name")`, see the secrets store below);
- send only headers supported by the engine and endpoint;
- validate path parameters and reject traversal-like input;
- keep the call server-side;
- bound retries and request volume.

Do not route a request through a client to bypass server-side restrictions.

### The secrets store

Credentials live in the experience's secrets store, not in the place file. `HttpService:GetSecret(key): Secret` returns a `Secret` value, verified against the docs (https://create.roblox.com/docs/en-us/cloud-services/secrets and the `Secret` datatype page):

- `Secret` is non-printable and non-loggable: printing it yields `Secret(<name>)`, so a leaked log line is not a leaked credential. Build the request value with `Secret:AddPrefix()` and `Secret:AddSuffix()` instead of concatenating strings.
- Secrets are available on live servers and in collaborative testing only. Local playtesting raises `Can't find secret with given key`, and a client script raises the same error, so a `GetSecret` call belongs in a server script and must be tested on a server, not in Play Solo.
- For local testing, define the value in Studio under File, Experience Settings, Security, Local Secrets.
- Add secrets in the Creator Dashboard under the game's Secrets tab, or manage them through Open Cloud. Only the game or group owner can view, create, or edit them; a game holds up to 500.
- Each secret carries an allowed domain, and the domain can be narrowed to a specific host such as `my.example.com`. Always set the narrowest domain the integration supports: an unrestricted secret is accepted by any endpoint that receives it.
- `Allow HTTP Requests` must be enabled in Studio's Security settings for any of this to run.

A true secret belongs here. A value that only needs to be hidden from players still belongs here too, but the anti-pattern to avoid is putting anything credential-shaped in `ReplicatedStorage`, a `StringValue`, or a module script, where clients can read it.

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

Cross-owner atomicity: durable acceptance and deduplication must not acknowledge an event before its work is recoverable; see `roblox-data` full reference, section Cross-owner atomicity limits.

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

## 8.6 TeleportService (in-experience)

Server-only teleports between places in the same experience or others. <!-- temporal: 2026-11 -->

**Studio testing:** `TeleportAsync` now works in Studio **Test** and **Team Test** without publishing; the destination place opens as a new test server, and the debugger, server inspection, and Device Simulator carry over. Only `TeleportAsync` is supported in tests (not `Teleport`, `TeleportPartyAsync`, or other legacy methods), and test servers differ from production:
- In **Test**, `game.PrivateServerId` and `game.JobId` are always empty. In **Team Test**, every server is private, so `PrivateServerId` is never empty, even for public-server teleports. Don't trust `PrivateServerId ~= ""` checks until you test in a published game.
- In Team Test, a reserved server's `PrivateServerId` can differ from its `ReservedServerId` (they match in production). Reuse the original `ReservedServerId` to send more players.
- `VipServerId` teleports fail in tests (Team Test servers have no owner), and `GetPlayerPlaceInstanceAsync` doesn't work.
- Tests only teleport between places that share the starting place's `GameId`.

- `TeleportService:TeleportAsync(placeId, players, teleportOptions?)` is the current method for every teleport (different place, specific server, reserved server); `Teleport`, `TeleportToPlaceInstance`, and `TeleportToPrivateServer` are legacy. Server scripts only; route client requests through a `RemoteEvent`. Max 50 players per call; a group must teleport within one experience.
- Yields and can throw: always wrap in `pcall` and retry failures (official guidance recommends retries, especially for reserved-server teleports). A teleport can also fail after the call returns without throwing; handle that in `TeleportService.TeleportInitFailed` (player, `Enum.TeleportResult`, errorMessage, placeId, teleportOptions). There is no `TeleportFailed` event.
- Options come from `Instance.new("TeleportOptions")`; there is no `CreateTeleportOptions`:
  - `SetTeleportData(data)`: non-secure payload, visible to the client; never send secrets.
  - Routing fields (set at most one; setting more than one errors):
    - `ReservedServerId = guid` for a developer-created reserved server. Generate the GUID on the server with `HttpService:GenerateGUID(false)`. The first teleport with a new ID creates the server; reusing the ID routes later teleports to it.
    - `VipServerId = privateServerId` for a player-purchased VIP (private) server. Use the target server's `game.PrivateServerId`, from any place in the same experience.
    - `ServerInstanceId = jobId` for a specific public server.
  - **Deprecated:** `ShouldReserveServer`, `ReservedServerAccessCode`, and `TeleportService:ReserveServerAsync()` remain only for backward compatibility. Don't write new code with them. See "Migrate from access codes" below.
- Read data on arrival: server `player:GetJoinData().TeleportData`; client `TeleportService:GetLocalPlayerTeleportData()`.

```luau
-- Server: teleport a player with data
local opts = Instance.new("TeleportOptions")
opts:SetTeleportData({ round = 3 })
local ok, err = pcall(function()
    TeleportService:TeleportAsync(PLACE_ID, { player }, opts)
end)
if not ok then warn("teleport failed:", err) end

-- Client on arrival
local data = TeleportService:GetLocalPlayerTeleportData()
if data then print("round:", data.round) end
```

### Reserved servers: create, reuse, and identify

Create the reserved server by teleporting with a fresh GUID, and persist the GUID if other servers or later sessions must send players to the same server. Key it by whatever identifies the session (lobby ID, party ID) in a DataStore, or in a MemoryStore for short-lived matches.

```luau
-- Server: create (first teleport) or rejoin (same ID) a reserved server
local HttpService = game:GetService("HttpService")
local TeleportService = game:GetService("TeleportService")

local reservedServerId = HttpService:GenerateGUID(false) -- or the stored ID to rejoin
local opts = Instance.new("TeleportOptions")
opts.ReservedServerId = reservedServerId

local ok, result = pcall(TeleportService.TeleportAsync, TeleportService, PLACE_ID, players, opts)
if ok and result then
	-- result.PrivateServerId matches game.PrivateServerId on the destination.
	-- result.ReservedServerAccessCode is only filled for legacy access-code teleports.
end
```

The destination instance is private: only players you teleport in arrive. On arrival, `game.PrivateServerId` equals the `ReservedServerId` you supplied and stays constant across every instance of that reserved server, while `game.JobId` changes per running instance. Identify the server type through DataModel properties, not fields invented on `GetJoinData()`:

```luau
-- Server script inside the reserved server
local inReservedServer = game.PrivateServerId ~= ""
-- A developer-created reserved server has no owning user;
-- a purchased private (VIP) server has a non-zero game.PrivateServerOwnerId.
local developerReserved = inReservedServer and game.PrivateServerOwnerId == 0
if inReservedServer and developerReserved then
	-- restricted admission: verify the player against server-held state
	-- (see the opaque-ticket pattern below), never from client claims.
end
```

To keep a VIP-server party together when moving to another place in the same experience, set `opts.VipServerId = game.PrivateServerId`.

**Migrate from access codes:** replace `ReserveServerAsync()` + `ReservedServerAccessCode` (or `ShouldReserveServer = true`) with a server-generated GUID in `ReservedServerId`, store the GUID wherever you stored access codes, and update every `TeleportOptions` that set the old fields.

A standard public server reports `PrivateServerId = ""`. A purchased private server reports a non-empty `PrivateServerId` with a non-zero `PrivateServerOwnerId`, which is how the cases stay distinguishable. Treat any non-empty `PrivateServerId` as restricted admission and verify the player's right to be there from server-held state.

### Secure teleport handoff (opaque ticket)

`SetTeleportData` payloads are client-readable, so the payload must never carry authority: no grant amounts, no role strings, no unlocked flags. The verified pattern is an opaque key plus a server-side record:

1. The source server generates an unguessable identifier (for example `HttpService:GenerateGUID(false)`).
2. Write a per-player ticket record containing the expected UserId, destination PlaceId, intended reservation/match identity, and authoritative round state, with a short TTL. A party needs independently claimable admission per member, not one globally consumed ticket.
3. Only the opaque id goes into `SetTeleportData({ ticket = id })`.
4. On arrival, the destination server reads the id from `player:GetJoinData().TeleportData`, reads the record from MemoryStore, verifies the player's UserId is admitted, and consumes it. Unknown, expired, or non-admitted ids fail closed: kick or return the player to the lobby.

Claim through `UpdateAsync`: validate the bound user and destination, then write a claimed-state record with an idempotent claim identifier. Returning `nil` from the transform cancels the update; it does not delete the ticket. Keep the transform side-effect-free because it can run again. Confirm the returned stored claim belongs to this attempt before admitting; an error or unknown outcome is not permission. Retain the claim until TTL expiry so a replay is recognized. A readable ticket is not an authorization proof.

### Failure ladder: pcall throw vs TeleportInitFailed

Distinguish the two failure surfaces and size retries to the cause, not to a fixed schedule:

- **Call failure caught by `pcall`**: classify the error. Do not retry invalid arguments or authorization mistakes blindly; retry only documented transient failures, bounded by a deadline and player/session state.
- **`TeleportService.TeleportInitFailed(player, teleportResult, errorMessage, placeId, teleportOptions)`** fires per player after initiation, so a group teleport can partially succeed: some arrive, some land here. Branch on the result enum:
  - `Enum.TeleportResult.Flooded`: too many recent teleport requests. Back off rather than hot-retry. `GameFull` is the distinct destination-capacity result.
  - `Enum.TeleportResult.Failure` and other retryable results: bounded retry with backoff.
  - Non-retryable results (for example `Enum.TeleportResult.Unauthorized` with a bad reserved-server code): do not retry; surface to the player.
- **Straggler policy**: when half a party arrives and half lands in `TeleportInitFailed`, the arriving server holds the match open (or re-teleports stragglers through the reserved access code) instead of starting with a broken group. Decide the wait timeout in product terms, then implement it explicitly.

Keep retry counts and backoff intervals as configuration, not guessed constants: measure real failure rates in a published place before tuning.

### Teleports and the durable session

A teleport moves the player to a server that will re-acquire their profile. The outgoing server must flush durable work *before* the teleport freezes local gameplay, not from `PlayerRemoving` after the connection is gone:

1. Stop granting progress the moment the teleport is accepted.
2. Use the save wrapper's documented final-save/release lifecycle before `TeleportAsync` when implementing an explicit handoff. Verify completion and failure reporting; calling `EndSession` alone is not a generic proof of durability. Do not start the teleport on an unconfirmed save. The destination still needs bounded acquisition/recovery, not an assumption of instant ownership.
3. `pcall` the teleport. If the call throws, the player is still connected and local: re-acquire the profile on this server, or disconnect the player cleanly with data already saved — never leave a released lock behind a live session.
4. If `TeleportInitFailed` fires, the player remains in the source server unless another attempt succeeds. Keep gameplay frozen; re-acquire ownership before resuming, or disconnect cleanly. A released profile cannot remain writable just because the player is still connected.

Cross-reference: session ownership protocol in `roblox-data` §4; ticket records use the MemoryStore patterns in `roblox-server-data`.

## 8.7 BadgeService (in-experience)

Server-side badge awarding and lookup. Awarding succeeds only when: caller is a server script, the place belongs to the badge's experience, the player is connected, the badge is enabled, and the player does not already have it (award-once per user).

- `BadgeService:AwardBadgeAsync(userId, badgeId)` → boolean; yields, so wrap in `pcall`. `AwardBadge` is deprecated; do not use it. Rate limit: `50 + 35 × player count` awards per minute.
- `BadgeService:GetBadgeInfoAsync(badgeId)` → dictionary (`Name`, `Description`, `IsEnabled`, `IconImageId`); yields. Check `IsEnabled` before awarding.
- Ownership checks: `UserHasBadgeAsync(userId, badgeId)` for one badge; `CheckUserBadgesAsync(userId, badgeIds)` for batches. `GetUserBadgesAsync` is not deprecated but serves batch (≤100) lookups with award dates. BadgeService exposes no events; call `AwardBadgeAsync` directly; there is nothing to poll and no `BadgeAwarded` event.
- Studio: only disabled badges can be awarded there for testing; awarding an enabled badge in Studio returns true without awarding.

```luau
-- Server: award a kill-streak badge
local function onKillStreak(player, BADGE_ID)
    local info = BadgeService:GetBadgeInfoAsync(BADGE_ID)
    if not info.IsEnabled then return end
    if BadgeService:UserHasBadgeAsync(player.UserId, BADGE_ID) then return end
    local ok, awarded = pcall(BadgeService.AwardBadgeAsync, BadgeService, player.UserId, BADGE_ID)
    if ok and awarded then print(player.Name, "earned the badge") end
end
```

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
