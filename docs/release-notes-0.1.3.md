# IonoFlux Python SDK v0.1.3

New resources for the ionosphere, HF propagation and observed reception reports. All require a Server API key.

- **Ionosphere.** `client.ionosphere.tec()`, `client.ionosphere.muf()` and `client.ionosphere.stations()`: NOAA GloTEC TEC/MUF maps or point values (JSON or GeoJSON), measured ionosonde MUF and GIRO stations.
- **Propagation.** `client.propagation.path()`, `client.propagation.forecast()` and `client.propagation.conditions()`: HF path availability and recommended frequencies, hourly forecasts up to 72 hours and per-band conditions.
- **Observations.** `client.observations.live()`, `client.observations.paths()`, `client.observations.bands()` and `client.observations.callsign()`: PSK Reporter / WSPRnet reception reports.
- New literal types `Band`, `PropagationMode` and `NoiseEnvironment`. Arguments outside the server ranges raise `ValueError` without sending a request.

Model outputs (GloTEC-based MUF and propagation) and measurements (ionosonde, reception reports) are documented separately in the [API contract](https://github.com/hongjunna/ionoflux-python/blob/main/docs/api-contract.md). Keep each response's `attribution`; WSPRnet data via WSPR.live is not for commercial use.

Existing methods, retry/redirect/redaction behavior, UTM tags, PolyForm Noncommercial 1.0.0 and NOTICE are unchanged. Earlier tags and artifacts remain immutable.

## Validation — 2026-10-21 KST

- Parameters, enums, defaults and ranges compared with the service source and the live public OpenAPI schema.
- Local: offline tests for every new call (paths, parameters, UTM tags, key requirement, local validation without requests), Ruff lint/format, mypy, Twine, artifact/license/credential-pattern checks and clean wheel/sdist installs. No authenticated live API request was made.
- Reviewed hashes: see [release artifacts](release-artifacts.md).
