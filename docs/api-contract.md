# API contract and verification evidence

Checked 2026-10-20 KST. Service source at `hongjunna/iono-flux` commit `473a89a`; relevant tracked API files had no local changes. Sources: `backend/app/api/v1/routes/{data,overview}.py`, `backend/app/schemas/common.py`, `backend/app/api/deps.py`, `backend/app/services/{space_weather,data_status}.py`. No server source was changed. This is a contract snapshot, not a service deployment-version claim.

Public schema: https://ionoflux.runvia.app/openapi.json. Its server URL is https://ionoflux.runvia.app. [Captured v0.1 subset](openapi-v0.1.json) contains the original selected operations and transitive schemas, without private data or authenticated responses. The SDK base URL appends `/v1`.

## Comparison and known gaps

Endpoint methods, parameter names/types/enums/default values/ranges and modeled response fields for the supported surface agree between source and public OpenAPI. OpenAPI only describes generic dicts for scales/sources/status and for nested current-summary objects: the SDK preserves arbitrary JSON rather than guessing stricter models. Server-generated schema examples are illustrative, not authenticated live fixtures. Unknown/additive fields are retained.

**Mismatch in prose:** the shared OpenAPI `start` parameter says default end minus 7 days for all series/statistics, but implementation uses flux/sunspots/Ap/statistics 30 days, X-ray 6 hours, wind 1 day and Kp 7 days. The SDK omits unspecified times and lets the server decide. `1mo` is implemented as a 30-day time_bucket, not a calendar month. We have not changed the API or its schema text.

Unauthenticated GET checks (no API key, no forged Origin/Referer):

| Request | Result | What was verified |
|---|---|---|
| `/openapi.json` | 200 | Public schema, server URL and security scheme |
| `/v1/sources` | 200 | `sources` object and `collectors` array; provider license/name/url/datasets |
| `/v1/data-status` | 200 | `generated_at`, datasets array, coverage/retention/freshness; spot_archive object |
| `/v1/space-weather/current` | 401 | JSON `detail` instructing account creation and X-API-Key header |
| `https://pypi.org/pypi/ionoflux/json` | 404 | No project JSON found; **not** availability/ownership confirmation |

These were the only operational API probes during the initial investigation, before the separately authorized nine-call acceptance. At the initial investigation, authenticated success was untested. The subsequent release review performed nine bounded live calls (see release-review.md); revoked/Web/expired keys, quota exhaustion and server errors remain uninduced. Mock tests cover the source/schema contract, not real authorization or data quality. No key was available during that initial investigation; the later acceptance used an owner-supplied temporary Server key without creating one. Public responses were inspected locally; real response datasets were not copied into this repository. HTTP 403/404/422/429/5xx handling below is grounded in source/HTTP contract, not induced in production.

## Supported operations

All HTTP methods are GET. Protected routes use `X-API-Key` (OpenAPI APIKeyHeader). All parameters below are optional unless marked required. `start`/`end` accept date-time, `interval` is raw/1m/5m/1h/3h/1d/7d/1mo (default raw), `limit` integer1..10000 (default5000) for all six series.

| Endpoint | SDK method | Extra parameters / actual default range | JSON response |
|---|---|---|---|
| `/v1/space-weather/current` | `space_weather.current()` | none | Current object |
| `/v1/solar/flux` | `solar.flux()` | 30 days | Series |
| `/v1/solar/sunspots` | `solar.sunspots()` | source null/swpc/silso (effective swpc); 30 days | Series |
| `/v1/solar/xray` | `solar.xray()` | band long/short, default long; 6 hours | Series |
| `/v1/solar/wind` | `solar.wind()` | parameter speed/density/bt/bz, default speed; 1 day | Series |
| `/v1/geomagnetic/kp` | `geomagnetic.kp()` | source null/swpc/gfz (effective swpc), include_forecast bool default true; 7 days | Series + forecast nullable array |
| `/v1/geomagnetic/ap` | `geomagnetic.ap()` | 30 days | Series |
| `/v1/statistics/{metric}` | `statistics(metric)` | required metric; start/end/source; 30 days | Statistics |
| `/v1/alerts` | `alerts.list()` | since null → last7days, repeatable category, limit1..500 default50 | Alert array |
| `/v1/alerts/scales` | `alerts.scales()` | none | fetched_at, attribution, scales object |
| `/v1/sources` | `sources()` | public/no key | sources object, collectors array |
| `/v1/data-status` | `data.status()` | public/no key | generated_at, datasets, spot_archive |
| `/v1/data-status/{dataset}` | `data.status(dataset)` | required dataset; public/no key | dataset string, rows array |

The SDK does not add pagination, inference, API writes or a generic arbitrary-path request method. New resources can share the internal bounded GET transport. Public data-status detail may show newest rows from datasets outside the dedicated v0.1 series scope; that is metadata/latest-record inspection; use the v0.1.3 observation and ionosphere calls for query-shaped data.

## v0.1.3 additions: ionosphere, propagation and observations

Checked 2026-10-21 KST against service source `backend/app/api/v1/routes/{ionosphere,propagation,observations}.py` and the live public OpenAPI. Every parameter name, type, enum, default and range below matched between the two; no server source was changed. All ten operations are GET with `X-API-Key` (CallerDep), so the SDK requires a key and consumes ordinary quota per call. No authenticated live request was made for this version; behavior is covered by mocked tests only.

| Endpoint | SDK method | Parameters (server default) | Response object |
|---|---|---|---|
| `/v1/ionosphere/tec` | `ionosphere.tec()` | time (latest; nearest map ±15 min), lat −90..90 + lon −180..180 together, format json/geojson | Grid: time/source/attribution/units/grid + lon/lat/tec/anomaly arrays, or a GeoJSON FeatureCollection. Point: time/latitude/longitude/tec_tecu/fof2_mhz/hmf2_km/attribution |
| `/v1/ionosphere/muf` | `ionosphere.muf()` | as tec, hop_km 0..4000 (3000), source model/ionosonde (model) | Model grid/point like tec with muf/fof2 (+m3000f2, hop_km). Ionosonde: time/window_minutes/attribution/stations[] |
| `/v1/ionosphere/stations` | `ionosphere.stations()` | max_age_hours 1..48 (6) | attribution, stations[] (code/name/latitude/longitude/time/fof2_mhz/muf3000_mhz/m3000f2/hmf2_km/foe_mhz/tec_tecu/confidence) |
| `/v1/propagation/path` | `propagation.path(from_, to, frequency)` | from/to 2..200 chars, frequency 1.8..54, datetime (now, ≤72 h ahead), mode, power >0..100000 (100), tx_gain/rx_gain −20..30 (2.15), noise (rural), path auto/short/long | frequency_mhz, datetime, path, prediction, details, bands[], observed (null unless about now), drivers, model, attribution[] |
| `/v1/propagation/forecast` | `propagation.forecast(from_, to)` | start (current hour), hours 1..72 (24), same link options | path, mode, power_w, path_type, hours[] (time/muf_mhz/best_band/best_reliability/recommended_frequencies_mhz/confidence/ionosphere_basis/kp/bands), model |
| `/v1/propagation/conditions` | `propagation.conditions(location=None)` | location 2..200 chars (global), datetime | datetime/ionosphere_basis/confidence/drivers plus local per-band status, or global day/night open_fraction per band |
| `/v1/observations/live` | `observations.live()` | minutes 1..60 (15), band, mode ≤16 chars, source pskreporter/wsprnet, bbox `minLon,minLat,maxLon,maxLat`, limit 1..5000 (2000) | grid-square paths plus notes/attribution |
| `/v1/observations/paths` | `observations.paths(from_, to)` | radius_km 50..1500 (500), hours >0..6 (1), band | from/to, radius_km, hours, a_to_b/b_to_a (total_spots, bands, recent), notes, attribution |
| `/v1/observations/bands` | `observations.bands(location=None)` | radius_km 50..3000 (1000), role rx/tx (rx), minutes 5..60 (15), mode | area/coordinates/radius_km/role/minutes/bands[]/notes/attribution |
| `/v1/observations/callsign/{callsign}` | `observations.callsign(callsign)` | role tx/rx (tx), hours >0..48 (24), limit 1..1000 (300) | callsign/role/hours/generated_at/space_weather plus reports/notes/attribution |

Enums: mode ft8/ft4/wspr/cw/ssb/am/rtty/psk31 (propagation, lower case); noise city/residential/rural/quiet; band 160m/80m/60m/40m/30m/20m/17m/15m/12m/10m/6m. Observation `mode` is free text compared by the server. Locations are `lat,lon`, Maidenhead locators or place names; place names are geocoded by the server (OpenStreetMap Nominatim, ODbL attribution added to propagation responses).

SDK behavior: arguments are checked locally with the server ranges above and raise `ValueError` without a request. The SDK sends its signature defaults explicitly (as with the v0.1 series calls), except optional times and locations, which are omitted so the server decides. `lat`/`lon` must be passed together; the server silently returns the full grid for one coordinate. `muf(source="ionosonde")` rejects lat/lon, geojson and a non-default hop_km because the server ignores them for measured values. Callsigns follow the server pattern and are percent-encoded as one path segment; a callsign containing `/` (portable suffix) cannot match the server's single-segment route and is expected to return 404. Responses are preserved as JSON without new runtime models, like the v0.1 surface.

Model versus observation: model TEC/MUF and every propagation result come from NOAA GloTEC NmF2/hmF2 with the IonoFlux simplified ITU-R P.533 path model (`model` field lists limitations; future times use same-UT persistence with a storm correction, and `ionosphere_basis` may fall back to climatology). Ionosonde MUF and stations are GIRO measurements within a time window. Observations are PSK Reporter / WSPRnet reception reports: proof of one-way propagation at that moment, never proof of a closed band, and SNR values are not comparable across receivers.

Provider terms (from public `/v1/sources`, 2026-10-21): GloTEC public domain (U.S. Government work); GIRO data policy requires acknowledgement; PSK Reporter free public feed with attribution; WSPRnet via WSPR.live free for research/projects with freely accessible results and **no commercial use**. Keep each response's `attribution` and check current terms in `sources()`. Query scope is bounded by the server (live ≤60 min, paths ≤6 h, callsign ≤48 h, newest rows only); the SDK adds no pagination, bulk export or historical spot download.

## Types, units and semantic distinctions

Series fields: metric/description/unit/source/interval strings; attribution `{key: str, name: str|null, url: str|null, license: str|null}`; start/end ISO8601 datetime strings; last_updated datetime|null; latest DataPoint|null; data DataPoint array. DataPoint: time datetime, value number|null, optional nullable min/max/count. Nullable response fields and unknown fields survive unchanged. `latest` is the latest available observation and need not lie inside the requested range. `last_updated` is collection success time, distinct from observation time. Null measurements are filtered out by the source query, so absence of a row is also possible; missing samples are not filled or synthesized.

Current: generated_at datetime, solar/geomagnetic/ionosphere objects, noaa_scales object|null, alerts_last_24h integer, freshness array. Solar sfi/sunspot_number may be null or `{value,time,source}`; xray may be null or `{flux,class,time}`; wind has speed/density/bt/bz values or null plus a latest time (not necessarily each component's own time). Geomagnetic kp adds g_scale. Do not infer that the wind component times all match or that all current-summary fields have source/unit metadata: use series and sources for explicit attribution.

Statistics: metric/unit/source strings, start/end datetime, count integer; min/max/mean/median/stddev/first/last/change numbers|null; first_time/last_time datetime|null. Empty results have count0 and nullable statistics. It has **no attribution field in the current contract**; call sources() for the provider terms rather than inventing one.

Alert: id/source/product_id/category/title/message strings; issue_time datetime; message_code/serial/noaa_scale nullable strings. category is ALERT/WARNING/WATCH/SUMMARY/CANCEL/OTHER/ES_OPENING. ES_OPENING can be an IonoFlux detection rather than an upstream NOAA alert. Scales includes current/previous_24h/day_1/day_2/day_3 entries under scales, preserving provider payload keys and strings.

| Statistics metric | Unit | Allowed sources (first default) |
|---|---|---|
| sfi | sfu | swpc |
| ssn | count | swpc, silso |
| kp | index | swpc, gfz |
| ap | nT | gfz |
| xray_long / xray_short | W/m^2 | primary |
| solar_wind_speed | km/s | swpc-rtsw |
| solar_wind_density | p/cm^3 | swpc-rtsw |
| imf_bt / imf_bz | nT | swpc-rtsw |

Kp series/statistics use status==observed. The optional Kp `forecast` is separate and includes time/kp/status/noaa_scale; preserve estimated/predicted status and never label it an observation. NOAA scales includes forecasts/probabilities. TEC/MUF and path products distinguish model and measurement as described in the v0.1.3 section; no ML prediction claim is made by this SDK. SILSO and other source choices can change values/timestamps and carry different terms: see sources().

Dataset enum: sfi, ssn, xray, solar_wind, kp, ap, tec, ionosonde, stations, pskreporter, wsprnet, activity, alerts, places. Summary dataset fields include key/category/table/sources/collectors/records/approximate/last_24h/total_collected/first_time/last_time/retention_days/last_success_at/stale. Nullable counts/coverage are not zero. retention_days null indicates no reported policy, **not guaranteed permanent storage**. Large counts may be approximate. Summary is cached120seconds. Detail returns at most30 newest rows; raw PSK detail limits the source query to1hour, WSPR/activity to1day. Retention/coverage is dynamic: the observed metadata reported raw PSK/WSPR retention30days while most solar/geomagnetic values reported null retention policy. Check current metadata rather than hard-coding a coverage promise.

Time-series queries include both start and end; maximum range3660days. Newest limit points/buckets are selected then returned ascending. No cursor/has_more contract exists and reaching limit may mean truncation. SDK accepts only aware datetime and converts to UTC, intentionally stricter than the server's naive-as-UTC helper. If only one bound is supplied, exact now/default range checks remain server-side. `1mo` fixed30days; no automatic splitting because boundary overlap and quota need a separate tested policy.

## Authentication, errors and limits

Protected routes require a Server key for ordinary Python usage; keyless access allowed for the website/internal paths is not a public SDK entitlement. Do not spoof browser Origin to avoid authentication. Existing Server key issuance requires service_url; SDK does not change issuance policy. Public sources/data-status routes have no CallerDep and are requested without any SDK key.

401 invalid/missing key; 403 revoked/expired/Web-without-Origin or incompatible origin/service configuration; 422 input validation/invalid source/dataset; 404 unknown resource/path; 429 daily quota; scales can return503 if not yet collected. Other infrastructure failures can return non-JSON errors. FastAPI validation detail can be an array, although the common ErrorResponse advertises string detail. SDK preserves its explanation as sanitized text, avoiding a falsely strict string-body decoder. APIError covers unmapped status codes.

Quota headers X-RateLimit-Limit/Remaining are integers. X-RateLimit-Reset is seconds until the next UTC midnight. On exceeded daily quota Retry-After is the same remaining seconds; never interpret it as epoch. Header presence is not guaranteed for failures before quota consumption or infrastructure errors. No-key metadata may have none. SDK stores Retry-After as string to avoid guessing unexpected proxy formats. Missing/malformed numeric quota fields become None.

Redirects are refused, HTTPS roots only, trust_env disabled. Only selected transient connection/read/remote-protocol failures and HTTP502/503/504 retry with bounded count/backoff; responses with Retry-After or remaining quota0 do not retry. Pool/local protocol/decoding failures do not retry; no429 auto-retry or daily sleep. Returned metadata excludes request objects and arbitrary response headers. Application/raw transport debug logging remains the caller's responsibility.

References: [HTTPX transports](https://www.python-httpx.org/advanced/transports/), [PyPA metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [Python support status](https://devguide.python.org/versions/). These informed transport testing, packaging and CI choices; implementation behavior above is grounded in the service source/schema.

Release review 2026-10-20: refetched public OpenAPI; all 13 selected GET operations parameters/responses/security and all referenced schemas match this snapshot exactly. This confirms public specification agreement, not authenticated response success. Oversized numeric quota fields (>20digits) are treated as missing; Retry-After remains a string.
