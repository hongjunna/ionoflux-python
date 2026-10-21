# IonoFlux Python SDK v0.1.2

- **Key page link in missing-key errors.** Calling an authenticated endpoint without `IONOFLUX_API_KEY`/`api_key` now raises `ConfigurationError: Set IONOFLUX_API_KEY or api_key to a Server API key. Get an API key: https://ionoflux.runvia.app/account`. `sources()` and `data.status()` still work without a key.
- **SDK usage tags.** Every request carries fixed `utm_source=python`, `utm_medium=sdk` and `utm_content=<SDK version>` query parameters so IonoFlux can count SDK traffic. They never contain key, user, host or environment data; method parameters are unchanged. See the [UTM specification (Korean)](https://github.com/hongjunna/ionoflux-python/blob/main/docs/usage-tags.ko.md).
- **Correct User-Agent.** `ionoflux-python/0.1.2` instead of the stale `0.1.0`.

Public method signatures, retry/redirect/redaction behavior, PolyForm Noncommercial 1.0.0 and NOTICE are unchanged. v0.1.0/v0.1.1 tags and artifacts remain immutable.

## Validation — 2026-10-21 KST

- Local: offline tests (new cases for the error link, UTM tags on authenticated/public calls, parameter preservation and User-Agent version), Ruff lint/format, mypy, Twine, artifact/license/credential-pattern checks and clean wheel/sdist installs.
- Server compatibility: the backend ignores undeclared query parameters (public `/v1/sources` with UTM tags returned 200) and nginx has no proxy cache keyed by query string. No authenticated live API request was made.
- Reviewed hashes: see [release artifacts](release-artifacts.md).
