# Changelog

## 0.1.3 — 2026-10-21

- New `client.ionosphere`: `tec()`, `muf()` (model or ionosonde source) and `stations()`.
- New `client.propagation`: `path()`, `forecast()` and `conditions()` for HF path predictions and band conditions.
- New `client.observations`: `live()`, `paths()`, `bands()` and `callsign()` for PSK Reporter / WSPRnet reception reports.
- New exported literal types `Band`, `PropagationMode` and `NoiseEnvironment`. Arguments outside server ranges raise `ValueError` before any request.
- Publishing workflows no longer read the `PYPI_PUBLISH_ENABLED` / `TESTPYPI_PUBLISH_ENABLED` variables.
- Existing methods, retry/redirect/redaction behavior, UTM tags, PolyForm Noncommercial 1.0.0 and NOTICE are unchanged.

## 0.1.2 — 2026-10-21

- Missing-key `ConfigurationError` now links the official key page: `Get an API key: https://ionoflux.runvia.app/account`. Public metadata calls still need no key.
- Every request carries fixed usage-statistics tags `utm_source=python`, `utm_medium=sdk` and `utm_content=<SDK version>`; caller parameters are preserved and no key/user/host data is added.
- `User-Agent` now reports the actual package version (`ionoflux-python/0.1.2`) instead of the stale `0.1.0` value.
- New reviewed release manifest `.github/release/0.1.2.json`; v0.1.0/v0.1.1 tags and artifacts stay immutable.

## 0.1.1 — 2026-10-20

- Replace pre-release/Pending Publisher guidance with official SDK installation and Server-key quickstarts in English and Korean.
- Use absolute HTTPS documentation/license links for GitHub and PyPI, and the official service-hosted PNG logo with descriptive alt text.
- Clarify supported APIs, unsupported async/pandas/TEC/MUF features and historical v0.1.0 verification versus follow-up work.
- Refresh package URLs, version metadata and reviewed release checksums; preserve public client behavior, PolyForm Noncommercial 1.0.0 and NOTICE.
- Keep v0.1.0 tags/artifacts immutable and protected Trusted Publishing/manual approval gates unchanged.

## 0.1.0 — 2026-10-20

- Add synchronous HTTPX client, reusable session, context manager and explicit/env Server key.
- Cover current conditions, solar/geomagnetic series, ten statistics metrics, alerts/scales and public metadata.
- Preserve JSON nulls, timestamp strings, attribution, unknown fields and raw response body.
- Add structured errors, redaction, redirect refusal and bounded GET retries without quota sleep.
- Add offline examples/tests, API comparison evidence, type checking and build/install CI.
- Published on PyPI after owner approval; clean installation, artifact hashes and both attestations verified.

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
