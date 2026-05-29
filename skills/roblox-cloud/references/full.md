# roblox-cloud — Full Reference

## When to Use

Use this skill when the task is mainly about Roblox Open Cloud or HTTP-based integration work outside normal gameplay scripting:

- Building CI, bots, web backends, scripts, or internal tools that call Roblox web APIs.
- Choosing API keys for non-user automation and checking the required scopes for an endpoint.
- Constructing request URLs, bodies, filters, headers, pagination, update masks, or long-running operation polling.
- Handling Open Cloud errors, quota limits, retries, and rate-limit headers.
- Deciding whether an endpoint is usable from HttpService inside an experience.
- Receiving Roblox webhooks on Discord, Slack, or a custom HTTPS endpoint.
- Reading openapi.json, cloud.docs.json, or service-specific JSON files to generate clients or inspect endpoint metadata.

Do not use this skill when the task is mainly about:

- OAuth app registration, authorization flows, token exchange, refresh handling, or delegated user consent.
- DataStore or MemoryStore schema design, save architecture, or cross-server data strategy.
- Gameplay remotes, replication, or general Roblox engine scripting.

## Decision Rules

- Use this skill if the core question is how to call or integrate with Roblox from HTTP.
- Prefer API keys when the caller is a server, CI job, bot, webhook worker, or in-experience automation that does not need end-user consent.
- Hand off to roblox-oauth when the integration needs user-granted access, OAuth registration, refresh tokens, or per-user delegated authorization.
- Hand off to roblox-data when the question becomes about persistent schema, contention, caching, or store-system design instead of request mechanics.
- Hand off to roblox-networking for gameplay networking, remotes, or trust-boundary questions.
- Hand off to roblox-api if the task is only an engine API lookup rather than a cloud integration.
- Use the machine-readable artifacts when you need exact path templates, schemas, scopes, rate limits, or HttpService usability metadata.
- If a request mixes cloud integration with out-of-scope architecture, answer only the Open Cloud portion and explicitly exclude the rest.

## Instructions

1. Classify the caller and integration surface:
   - External backend, CLI, CI, or automation worker.
   - Webhook receiver.
   - In-experience HttpService.
2. Choose authentication at the boundary:
   - Default to API keys for non-user automation.
   - If the task needs user-specific delegated access, stop and switch to roblox-oauth.
3. Confirm the endpoint before coding:
   - Base URL and path template.
   - Path and query parameters.
   - Required request body schema.
   - Required scopes.
   - Rate limits.
   - Whether HttpService is supported if the call originates in-experience.
4. Build requests using the documented patterns:
   - Insert path parameters exactly.
   - Keep pagination queries stable across pages.
   - Add Content-Type: application/json for JSON bodies.
   - Send x-api-key for API-key-authenticated requests.
   - Use updateMask only for fields you intend to patch.
5. Handle Open Cloud response mechanics explicitly:
   - Read nextPageToken for pagination.
   - Poll Operation resources with backoff for long-running calls.
   - Parse Open Cloud JSON types correctly, especially timestamps, durations, bytes, field masks, and decimals.
6. Handle failure paths as part of the integration:
   - INVALID_ARGUMENT: verify IDs, filters, headers, and body shape.
   - PERMISSION_DENIED or INSUFFICIENT_SCOPE: verify scopes and resource access.
   - RESOURCE_EXHAUSTED or HTTP 429: honor retry-after when present, otherwise use exponential backoff.
   - UNAVAILABLE and similar transient failures: retry with backoff, not tight loops.
7. For webhooks, design for secure, idempotent receipt:
   - Require a public HTTPS POST endpoint.
   - Return 2XX within 5 seconds.
   - Verify roblox-signature when a secret is configured.
   - Deduplicate by NotificationId.
   - Treat deliveries as retryable and potentially duplicated.
8. For HttpService, apply the extra platform constraints:
   - Only supported Open Cloud endpoints are callable.
   - Only x-api-key and content-type headers are allowed.
   - x-api-key must come from a Secret.
   - HTTPS only.
   - Path parameters cannot contain ..
9. Keep the answer inside scope:
   - Focus on cloud requests, auth choice, webhooks, HttpService, rate limits, and tooling artifacts.
   - Do not drift into OAuth implementation details, gameplay networking, or in-experience data architecture.

## Using References

- Open references/open-cloud-overview.md first when you need the high-level model for Open Cloud versus legacy or in-experience calls.
- Open references/cloud-guides.md when the task matches a known workflow and you need the best guide starting point.
- Open references/api-patterns-errors-types-scopes-and-rate-limits.md for request construction, pagination, field masks, errors, scopes, and retry behavior.
- Open references/webhooks-documentation.md for trigger support, payload shape, signature verification, and delivery expectations.
- Open references/http-service.md when requests originate from a Roblox experience and endpoint support must be validated.
- Open references/openapi-documentation.md when you need to inspect or generate against the unified OpenAPI description.
- Open references/cloud-reference-json-files.md when you need to mine local JSON artifacts directly for operation IDs, schemas, scopes, or engine-usability metadata.

## Checklist

- The integration surface is identified as external automation, webhook receiver, or in-experience HttpService.
- API key usage is chosen only for non-OAuth automation, and OAuth work is handed off when required.
- Endpoint path, body schema, scopes, and rate limits are confirmed before implementation.
- Pagination, filtering, and updateMask behavior are understood for the chosen endpoint.
- Long-running operations are polled instead of assumed synchronous.
- Error handling covers invalid input, permission failures, and quota exhaustion.
- Retry logic uses retry-after or exponential backoff.
- Webhooks are treated as idempotent, signed, and time-bounded.
- HttpService calls are checked for endpoint support and header limitations.
- The response stays out of OAuth implementation, data architecture, gameplay networking, and general engine scripting.

## Common Mistakes

- Implementing OAuth flows here instead of switching to roblox-oauth.
- Assuming every Open Cloud endpoint is callable from HttpService.
- Sending unsupported headers from HttpService or storing the API key as plain text instead of a Secret.
- Forgetting that API-key scopes and creator permissions both matter.
- Changing filter parameters while paginating and then hitting 400 errors.
- Ignoring Operation polling and assuming async endpoints finish immediately.
- Retrying 429s or 503s in a tight loop instead of backing off.
- Treating webhook delivery as exactly once and skipping deduplication.
- Letting webhook handlers do slow work before returning a 2XX response.
- Expanding a cloud-integration question into save-schema, gameplay, or remote-security design.

## Examples

### External automation with an API key

- Use an API key for a CI job that publishes a place, updates a universe, or lists inventory items.
- Confirm the endpoint scope, build the request URL, and inspect rate-limit headers for safe batching.

### In-experience Open Cloud call

- Before writing HttpService:RequestAsync, confirm the endpoint is supported for engine use.
- Put the API key in Secrets, send only x-api-key and content-type, and handle 429s with backoff.

### Webhook receiver

- Configure a public HTTPS endpoint.
- Verify roblox-signature, reject stale timestamps, deduplicate by NotificationId, return 2XX quickly, and process the event asynchronously.
