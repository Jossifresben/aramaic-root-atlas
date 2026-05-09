# API Stability & Deprecation Policy

> Living contract for downstream consumers of the Aramaic Root Atlas
> public JSON API. Last updated 2026-05-09.

## What this document promises

- **Versioned URLs are stable within a major version.** Once an endpoint
  ships under `/api/v1/X`, its response shape and parameter contract
  will not change in a way that breaks correctly-written clients,
  except as described under "Breaking changes" below.
- **Deprecation notice is at least 12 months.** When an endpoint, field,
  or parameter is scheduled for removal, the deprecation is announced in
  the [CHANGELOG](../CHANGELOG.md) and surfaced in the OpenAPI spec
  (`deprecated: true`) at least 12 months before removal.
- **Major versions exist to break things.** A new `/api/v2/` URL space
  signals that breaking changes have landed; v1 continues to work
  alongside v2 for at least 12 months after v2 ships.
- **Rate limits are documented.** See "Rate limits" below. Headers on
  every response let clients adapt without trial-and-error.

## What this document does **not** promise

- **Performance.** No latency or throughput SLA. The Atlas runs on a
  single Render Pro instance and may experience brief slowdowns during
  redeploys.
- **Uptime.** No SLA. Solo-maintained academic tool. See
  [docs/SUCCESSION.md](SUCCESSION.md) for continuity planning.
- **Underlying data immutability.** The corpus, glosses, cognates, and
  extraction outputs may change between releases. Each release is a
  separate Zenodo deposit with its own DOI; cite the version DOI to pin
  the data your analysis depends on. See [CHANGELOG](../CHANGELOG.md)
  "Data Changes" sections.
- **Backwards compatibility on `/api/X` (no version prefix).** The
  unversioned legacy paths exist for compatibility with pre-v3.0.3
  consumers, but new fields, parameters, and response-shape changes
  may land there without notice. **Use `/api/v1/X`.**

## Versioned base URLs

| Version | Base URL | Status | Notes |
|---|---|---|---|
| **v1** | `https://aramaic-root-atlas.onrender.com/api/v1/` | **Recommended** | Stable contract; 12-month deprecation notice for breaking changes |
| Legacy | `https://aramaic-root-atlas.onrender.com/api/`     | Compatibility | No stability contract; may change. Aliased to v1 today, but not guaranteed |

Every endpoint listed in [/api-docs](https://aramaic-root-atlas.onrender.com/api-docs)
is reachable under both bases. Examples:

```
# Recommended
GET https://aramaic-root-atlas.onrender.com/api/v1/roots?q=SH-L-M

# Legacy (works today, no contract)
GET https://aramaic-root-atlas.onrender.com/api/roots?q=SH-L-M
```

## Breaking changes — what counts

The following are **breaking** and require a major version bump (e.g.
v1 → v2) and 12-month deprecation:

- Removing an endpoint or HTTP method
- Removing a top-level field from a response body
- Renaming a top-level field
- Changing the type of a field (e.g. number → string)
- Tightening a parameter's accepted format (rejecting input that v1
  accepted)
- Changing the meaning of a status code

The following are **not** breaking and may land in any release:

- Adding new endpoints
- Adding optional fields to a response
- Adding optional parameters
- Adding new enum values
- Loosening parameter validation
- Performance improvements
- Bug fixes (including changing wrong output to correct output, when the
  wrong output was clearly wrong)

## Deprecation process

When something is deprecated, we:

1. Mark it `deprecated: true` in the OpenAPI spec at `/static/swagger.json`.
2. Add a `Deprecation` HTTP response header with the date of removal in
   IMF-fixdate format (RFC 9745).
3. Add a CHANGELOG entry under the next release.
4. Wait **at least 12 months** before removing.
5. After removal, requests to the removed surface return `410 Gone` with
   a body pointing to the replacement.

## Rate limits

| Limit | Window | Scope |
|---|---|---|
| **600 requests** | per minute | per IP address |
| **60 requests**  | per second | per IP address |

Response headers on every API response:

| Header | Meaning |
|---|---|
| `X-RateLimit-Limit`     | Limit for the window that just elapsed (e.g. `60`) |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset`     | Unix timestamp when the current window resets |
| `Retry-After`           | Seconds to wait before retrying (set on 429) |

Exceeding the limit returns `429 Too Many Requests`. Clients should
respect `Retry-After` and back off — don't busy-loop.

If you need higher limits for legitimate research workloads
(institutional bulk download, reproduction of cited analyses), please
[open a GitHub issue](https://github.com/Jossifresben/aramaic-root-atlas/issues).

## Authentication

Currently **none.** All endpoints are public. Future authenticated tiers
(for higher rate limits) may be introduced via API tokens; if so, they
will follow the OAuth 2.0 Bearer Token convention and be opt-in (the
unauthenticated public endpoints will continue to work).

## CORS

All endpoints respond with `Access-Control-Allow-Origin: *`. Browser-based
clients on any origin can call the API directly.

## Server errors

| Status | Meaning |
|---|---|
| `200`  | OK |
| `400`  | Bad request — malformed parameter; body includes `{"error": "..."}` |
| `404`  | Endpoint or resource not found |
| `429`  | Rate limit exceeded |
| `5xx`  | Server bug; please open an issue with the request you sent |

## Versioned-URL exception list

The following paths are **not** versioned because they're not data API
endpoints:

- `/api-docs` — the Swagger UI itself (HTML). Always at this path.
- `/static/swagger.json` — the OpenAPI spec. Always at this path.

## Client SDK / code generation

The OpenAPI spec at `/static/swagger.json` (3.0.3 schema) supports code
generation via standard tools (`openapi-generator`, `swagger-codegen`,
etc.). Generated clients should target the `/api/v1/` base URL.

## Citing API responses in publications

If a paper depends on a specific API response, cite the **versioned
Zenodo deposit DOI** (e.g. `10.5281/zenodo.20089274` for v3.0) so the
exact data version that produced the response is preserved. The concept
DOI `10.5281/zenodo.19358625` always resolves to the latest version,
which may differ from the one your analysis used.

---

*Questions or proposals?* Open an issue at
https://github.com/Jossifresben/aramaic-root-atlas/issues.
