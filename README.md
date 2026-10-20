# IonoFlux Python SDK

Official synchronous Python client for [IonoFlux](https://ionoflux.runvia.app). Python 3.11+; version 0.1.0 is under development and **has not been published**.

[한국어](README.ko.md) · [API contract and verification limits](docs/api-contract.md) · [Development plan](docs/development-plan.md)

## Install

The target distribution and import name is `ionoflux`:

```sh
# After an approved PyPI release (not available from this project yet):
pip install ionoflux
```

Until then, clone this repository, create a virtual environment and run:

```sh
python -m pip install -e '.[dev]'
```

No PyPI search result and a 404 from its JSON API do **not** establish ownership or availability. `ionoflux-sdk` remains the alternative distribution name. Do not install an unverified namesake. License selection and publishing remain pending [issue #3](https://github.com/hongjunna/ionoflux-python/issues/3).

## Quickstart

Sign in at https://ionoflux.runvia.app/account and create a **Server** API key. Python runs outside the browser: a Web key can return 403. The current account flow requires a service URL even for Server keys; notebooks/batches without a website need an appropriate service URL under the existing policy. The SDK cannot issue keys or bypass that requirement.

```sh
export IONOFLUX_API_KEY='your-server-key'
```

```python
from ionoflux import Client

with Client() as client:
    current = client.space_weather.current()
    print(current.data)  # Original JSON fields, including nulls and timestamp strings
    print(current.rate_limit.remaining)
```

Explicit `Client(api_key="...")` overrides the environment. No key is required for `sources()` or `data.status()`. Keep keys out of source control, browsers and shared notebook outputs.

```python
from datetime import UTC, datetime
from ionoflux import Client, RateLimitError

with Client(timeout=10.0, max_retries=1) as client:
    try:
        series = client.solar.flux(
            start=datetime(2026, 10, 1, tzinfo=UTC),
            end=datetime(2026, 10, 2, tzinfo=UTC),
            interval="1h",
            limit=100,
        )
        print(series.data["unit"], series.data["attribution"])
        print(series.data["data"])
    except RateLimitError as error:
        print(error.retry_after, error.rate_limit.reset_seconds)
        # Return control to your application; no automatic daily-quota sleep.
```

## Supported calls

All return `APIResponse[T]`: `.data` (JSON dict, or list of dicts for alerts), `.raw_body` (original bytes), `.status_code`, `.headers` (quota/content-type only), `.rate_limit`. Nested JSON values are flexible (`Any`), not runtime-validated domain models; additive server fields survive. Timestamps remain ISO 8601 strings for lossless JSON; request datetimes must be aware and are converted to UTC. No automatic DataFrame conversion.

| Call | Options beyond shared time-series arguments |
|---|---|
| `client.space_weather.current()` | Current indicators and freshness |
| `client.solar.flux(...)` | SFI |
| `client.solar.sunspots(...)` | `source="swpc"` or `"silso"` |
| `client.solar.xray(...)` | `band="long"` or `"short"` |
| `client.solar.wind(...)` | `parameter="speed"`, `"density"`, `"bt"`, `"bz"` |
| `client.geomagnetic.kp(...)` | `source="swpc"` or `"gfz"`, `include_forecast=True` |
| `client.geomagnetic.ap(...)` | Ap |
| `client.statistics(metric, ...)` | `start`, `end`, metric-specific `source`; 10 metrics in contract |
| `client.alerts.list(...)` | `since`, repeatable `category` list, `limit=50` (1..500) |
| `client.alerts.scales()` | R/S/G levels and outlook |
| `client.sources()` | Public provider catalog and collector freshness |
| `client.data.status(dataset=None)` | Public summary or latest records of a dataset |

Shared time-series arguments: `start=None`, `end=None`, `interval="raw"`, `limit=5000` (1..10000). Omitting dates preserves endpoint-specific **server defaults**. The API keeps the newest limited points then returns them ascending. No cursor or automatic full-history download. `1mo` is a fixed **30-day** bucket. Requests with explicit start and end are limited to 3660 days; query allowance does not imply historical availability. Consult `data.status()` for retention and actual coverage.

## Errors, networking and security

`AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `ValidationError` (422), `RateLimitError` (429), `ServerError` (5xx) and `RedirectError` (3xx) extend `APIError`. Exceptions carry `status_code`, redacted textual `detail`, `rate_limit` and `retry_after`; no HTTP request object. Other failures use `TransportError`, `ResponseError` or `ConfigurationError`. Locally invalid method arguments raise `ValueError`.

Only GET is implemented. At most 0..3 retries (default 1) apply to transport errors and HTTP 502/503/504; 401/403/404/422/429/500 are never retried. Backoff is 0.25, 0.5, 1 seconds (maximum aggregate sleep 1.75 seconds). Retry-After is exposed, never used to trigger a long wait. HTTPX `timeout` is a finite positive per-operation timeout, **not a total wall-clock deadline**. Every retry may count against the API quota. `X-RateLimit-Reset` is seconds remaining until UTC midnight, not an epoch timestamp. `Retry-After` remains its original string; unknown/malformed numeric quota headers become `None`.

The default API root is `https://ionoflux.runvia.app/v1`; a custom `base_url` must be HTTPS, end in `/v1`, and contain no credentials, query or fragment. Redirects are never followed. Environment proxies and netrc credentials are disabled (`trust_env=False`). Session/transport lifetime is owned by `Client`; call `close()` or use `with`. The SDK does not log credentials, send them to public metadata routes or put them in URLs. Custom HTTP transports and application-level HTTP debug logging are trusted caller code; do not log raw request headers. Raw success bodies can contain arbitrary server data: treat them as sensitive application data when sharing.

## Development and release status

```sh
python -m pytest
ruff check .
ruff format --check .
mypy
python -m build
python -m twine check dist/*
python scripts/check_artifacts.py
python examples/offline.py
```

Tests block network connections and use HTTPX MockTransport. CI runs Python 3.11–3.15 on Linux and 3.14 on Windows/macOS, then builds and installs wheel/sdist in separate clean environments. No workflow publishes packages. Authenticated production responses are **not yet smoke-tested**; source/OpenAPI/example-fixture agreement is not production acceptance. [Follow-up #2](https://github.com/hongjunna/ionoflux-python/issues/2) covers TEC/MUF, propagation, stations and WSPR/PSK. [Release #3](https://github.com/hongjunna/ionoflux-python/issues/3) tracks license, name/ownership, safe test key and separately authorized TestPyPI/PyPI publishing. Service tracker: [iono-flux#44](https://github.com/hongjunna/iono-flux/issues/44).

The SDK license is undecided; `LICENSE` is an explicit pending-decision notice, not an open-source grant. Provider data licenses are separate: preserve API attribution and inspect source-specific conditions (including noncommercial restrictions).
