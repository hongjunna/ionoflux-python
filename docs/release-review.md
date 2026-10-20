# v0.1.0 final code review and real API acceptance

> Historical v0.1.0 development evidence. The initial release was subsequently published and verified on 2026-10-20; see [the immutable release record](https://github.com/hongjunna/ionoflux-python/releases/tag/python-v0.1.0). Statements below describe the review-time state, not current publication status. This v0.1.1 documentation patch performs no new live API acceptance.

2026-10-20 KST. Reviewed PR #4 at ed4fa19, then added focused regression fixes on the same branch. No merge, package upload, service deployment, DB operation, account/key-policy change or administrator request was performed. The owner initially deferred the license decision at that review, then explicitly adopted unmodified PolyForm Noncommercial1.0.0 in a subsequent request. LICENSE/NOTICE/SPDX now implement that approval; API terms, merge and uploads remain separately unapproved.

## Findings and resolutions

| Priority | Finding at the reviewed head | Resolution / evidence |
|---|---|---|
| P1 | HTTPX DecodingError/other RequestError could escape with an attached authenticated request and unsanitized error text | Catch RequestError, return a sanitized SDK error outside the exception handler with no chained request exception; regression includes a real invalid-gzip decoder failure |
| P2 | Oversized numeric quota header raised ValueError, masking a successful response or structured429 | Parse only ASCII decimal values up to20digits; malformed/oversized values become None, leaving Retry-After/status intact |
| P2 | Local protocol/pool/configuration failures retried; 503 Retry-After or Remaining0 could be ignored | Only selected connection/read/remote-protocol failures retry; do not retry5xx when server wait/quota headers advise against it. Never retry429 |
| P2 | Artifact key regex omitted URL-safe '-'/'_' emitted by the real key generator; sdist included internal development documents | URL-safe key regression and archive path guards; sdist doc allowlist now contains only API contract/schema, not development plan/review/verification/handoff |
| P2 | Alert list accepted scalar elements despite advertised list-of-objects return type | Validate container elements and raise ResponseError without guessing domain models |
| P3 | README lacked complete checkout/venv steps for an unmerged branch; minimum declared HTTPX was not exercised | Add English/Korean macOS/Linux/Windows installation instructions and CI Python3.11/HTTPX0.27.0 job |

The focused pre-fix regressions recorded17failures/2passes; fixes then passed all97offline cases. Original failure output is retained outside the repository, not in distribution files. See the PR's final check run for the exact final commit and matrix result; source changes require that run to pass before merge.

## Real Server API acceptance — nine sequential GET requests

Executed2026-10-20 15:19KST using the patched working tree. The environment variable was absent; the supplied temporary Server test key was entered via echo-disabled stdin, held only in process memory and never placed in commands, source files, env files, request URLs or raw output. The key is not reproduced in this report. No key rotation/revocation API was called; the owner plans to revoke the temporary key after use.

`max_retries=0`, timeout10seconds, sequential requests, hard maximum10. Exactly9requests were made:6authenticated data routes and3public metadata routes (no key sent to public routes). Every request returned200, every field/type validation passed, no retries, and no401/403/429 occurred. No further operational requests were made after this test. The stop policy would have halted immediately on any API error; no quota-exhaustion, revoked-key or invalid-key condition was deliberately induced.

| # | SDK call | HTTP | Validation |
|---|---|---|---|
| 1 | space_weather.current() | 200 | Authentication success; generated_at UTC, nested condition objects, nullable scales/freshness |
| 2 | solar.flux(interval='1d', limit=2) | 200 | sfi/sfu, source/attribution, range/update/latest/points types and UTC |
| 3 | geomagnetic.kp(limit=2) | 200 | kp/index, source/attribution, nullable point fields and separate forecast timestamps/status |
| 4 | statistics('sfi', explicit2day UTC range) | 200 | Count, numeric-or-null statistics, UTC range and nullable first/last times |
| 5 | alerts.list(limit=2) | 200 | List-of-objects, UTC issue_time, string/nullable alert fields |
| 6 | alerts.scales() | 200 | fetched_at UTC, attribution and scales object |
| 7 | sources() | 200 | Provider catalog, license/name/url field types and collector array |
| 8 | data.status() | 200 | Dataset/source lists, UTC-or-null coverage/freshness and retention-or-null |
| 9 | data.status('sfi') | 200 | Dataset key and newest-record rows with UTC/source fields |

For every success, decoded raw_body equaled data: original timestamps, nulls, numbers, units and attribution are preserved rather than normalized or filled. Real nullable values satisfy the nullable predicates; this is not exhaustive testing of all possible missing-data combinations. Six protected responses had numeric quota headers; the three public responses had none, consistent with source. Client context exit and explicit idempotent close yielded is_closed=True. No response body, observation values, API key or authentication header is stored here or in public logs/artifacts. Only request outcome/type-check summaries are retained.

Server source api/deps.py confirms429 Retry-After and X-RateLimit-Reset are seconds to UTC midnight; live success validates quota header presence/types, not quota exhaustion. Mock tests verify429 immediate return, repeated categories, bounded retries, redirects, null preservation and malformed errors. **Do not report real429/403 behavior as induced or live-verified.**

## OpenAPI, data compatibility and versions

The public OpenAPI was refetched during review. All13supported GET operations' parameters, responses/security and all referenced component schemas match the captured subset exactly. The default server URL remains the SDK's HTTPS origin. Source-specific default-period prose discrepancies and fixed30day1mo are already documented in api-contract.md; SDK omits absent time bounds to preserve server defaults. The9live checks found no response mismatch requiring server changes. Live SFI/Kp/current/statistics acceptance does not claim live sunspots/X-ray/wind/Ap or every source parameter; those remain schema/source/mock verified.

Python>=3.11, HTTPX>=0.27,<0.29. CI covers supported3.11–3.15 and macOS/Windows3.14 plus the minimumHTTPX0.27.0. No upper Python compatibility beyond tested stable versions is claimed. Public PyPI vulnerability metadata was checked on2026-10-20 for HTTPX0.27.0/0.28.1 and installed httpcore/anyio/h11/idna/certifi/typing_extensions versions; no advisories were listed. This is only the index metadata check at that time, not a complete transitive security audit. Dependencies are range-bounded, not a frozen runtime environment; known-advisory checks cannot guarantee absence of vulnerabilities. No extra runtime dependencies were introduced by the review.

## Public repository and artifact exposure review

Inspected every reachable existing commit's tracked blobs/messages, PR/issue text and all three existing CI run logs using service/GitHub/AWS token and private-key patterns without printing matches. No credential-pattern finding was detected; this is a scoped automated/manual review, not proof of universal secret absence. Historical Git author metadata includes a personal email and handoff/CI logs include temporary filesystem paths. These are privacy/minimization considerations, not observed authentication credentials; values are not copied here. New commits use the owner's GitHub noreply address. The current SDK internal handoff document is removed; prior history is not rewritten. Historical privacy cleanup, if desired by the owner, requires a separate coordinated history policy.

HTTPX INFO logging with a mock authenticated request was captured and did not contain the key. The SDK emits no credential log; custom transports, external debug hooks and application logging of raw authenticated requests remain caller-controlled and cannot be universally sanitized by the SDK. Redirects remain disabled, arbitrary-origin request methods are not public, environment proxies/netrc are disabled, HTTPS root is enforced and keys are never query parameters. Success raw bodies are preserved and can contain arbitrary service data, so consumers must not blindly publish them.

Wheel contains only ionoflux package/type marker and standard dist-info. Sdist includes code/tests/examples/build checks/public API contract and schema; internal development/review/handoff material is excluded. Artifact inspection rejects unsafe paths, private-key/service-key patterns and unexpected metadata. Both formats target metadata2.4, independently fixing #5's Twine incompatibility. Windows fixture/example reads use explicitUTF-8, independently fixing #5's platform failure. Tests must pass on actual Windows; local success alone is insufficient.

## Decision

No known remaining code blocker after the fixes **provided the latest CI passes**. The PR may be merged after final user approval; this review does not merge it. The code-license choice is now resolved. External release still requires package-name/ownership/accounts2FA/Trusted Publisher preparation and separate TestPyPI/PyPI authorization. No upload/name reservation has occurred. See release-preparation.md and issue#3; follow-up feature APIs remain issue#2.

The owner subsequently adopted PolyForm Noncommercial1.0.0 and its institutional permissions unchanged. LICENSE/NOTICE/SPDX now apply that approval. The API terms and attribution-policy proposal remain unapproved; no upload is authorized. See licensing-review.ko.md for the standard notice/UI-attribution distinction and broad institutional permission caveat.
