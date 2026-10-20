# Changelog

## 0.1.0 — Unreleased

- Add synchronous HTTPX client, reusable session, context manager and explicit/env Server key.
- Cover current conditions, solar/geomagnetic series, ten statistics metrics, alerts/scales and public metadata.
- Preserve JSON nulls, timestamp strings, attribution, unknown fields and raw response body.
- Add structured errors, redaction, redirect refusal and bounded GET retries without quota sleep.
- Add offline examples/tests, API comparison evidence, type checking and build/install CI.
- Release blocked on license decision, package ownership and safe authenticated acceptance; no publication yet.

### Release review fixes

- Sanitize all HTTPX request failures; decoding errors cannot expose the request or cause chain.
- Narrow retries and return immediately when a server asks to wait or reports no quota.
- Tolerate oversized rate headers, validate alert object containers and detect URL-safe key patterns.
- Restrict sdist docs to public API contract/schema; verify the minimum HTTPX in CI.
- Document complete branch-specific installation and Windows activation.
