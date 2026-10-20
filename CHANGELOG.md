# Changelog

## Unreleased

- Optional, main-only manually approved live API smoke workflow (not executed during development).
- GitHub documentation reflects the successful PyPI v0.1.0 publication.

## 0.1.0 — 2026-10-20

- Add synchronous HTTPX client, reusable session, context manager and explicit/env Server key.
- Cover current conditions, solar/geomagnetic series, ten statistics metrics, alerts/scales and public metadata.
- Preserve JSON nulls, timestamp strings, attribution, unknown fields and raw response body.
- Add structured errors, redaction, redirect refusal and bounded GET retries without quota sleep.
- Add offline examples/tests, API comparison evidence, type checking and build/install CI.
- Published on PyPI after owner approval, licensed under PolyForm Noncommercial1.0.0; clean installation, exact hashes and both attestations verified.

### Release review fixes

- Sanitize all HTTPX request failures; decoding errors cannot expose the request or cause chain.
- Narrow retries and return immediately when a server asks to wait or reports no quota.
- Tolerate oversized rate headers, validate alert object containers and detect URL-safe key patterns.
- Restrict sdist docs to public API contract/schema; verify the minimum HTTPX in CI.
- Document complete branch-specific installation and Windows activation.

### License adoption

- Adopt unmodified PolyForm Noncommercial License 1.0.0, including institutional permissions.
- Add IonoFlux Required Notice and SPDX/PEP639 license-file declarations.
- Verify official text integrity, notice preservation and metadata in wheel/sdist; add 14 regression cases.
- Separate adopted SDK licensing from unapproved API terms and external publishing gates.
