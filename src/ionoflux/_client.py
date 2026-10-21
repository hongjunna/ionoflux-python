"""Synchronous, bounded GET-only transport for the public IonoFlux API."""

from __future__ import annotations

import json
import math
import os
import time
from datetime import datetime
from types import TracebackType
from typing import Any, Literal
from urllib.parse import quote

import httpx

from ._exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    RedirectError,
    ResponseError,
    ServerError,
    TransportError,
    ValidationError,
)
from ._response import APIResponse, JSONObject, RateLimit
from ._validation import (
    BANDS,
    CALLSIGN,
    CATEGORIES,
    DATASETS,
    INTERVALS,
    METRIC_SOURCES,
    NOISE_ENVIRONMENTS,
    PROPAGATION_MODES,
    Band,
    Category,
    Dataset,
    Interval,
    Metric,
    NoiseEnvironment,
    PropagationMode,
    choice,
    date_range,
    integer,
    number,
    place,
    utc,
    whole,
)

Params = dict[str, Any]
VERSION = "0.1.3"
KEY_URL = "https://ionoflux.runvia.app/account"
# Fixed request-origin tags for IonoFlux usage statistics; never user, key or host data.
UTM_PARAMS = {"utm_source": "python", "utm_medium": "sdk", "utm_content": VERSION}
SAFE_HEADERS = {
    "content-type",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "retry-after",
}


class Client:
    """One reusable HTTP session. base_url includes /v1; redirects are refused.

    timeout is a finite positive HTTPX per-operation timeout (not a wall-clock deadline).
    max_retries is 0..3; retries wait at most 0.25 + 0.5 + 1 seconds in total.
    transport ownership transfers to this client and it is closed with the client.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = "https://ionoflux.runvia.app/v1",
        timeout: float = 10.0,
        max_retries: int = 1,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        key = os.environ.get("IONOFLUX_API_KEY") if api_key is None else api_key
        if key is not None and (
            not key.strip() or not key.isascii() or any(ord(c) <= 32 or ord(c) == 127 for c in key)
        ):
            raise ConfigurationError("API key must be a nonempty printable ASCII token")
        try:
            url = httpx.URL(base_url)
        except (httpx.InvalidURL, ValueError):
            raise ConfigurationError("Invalid base_url") from None
        if (
            url.scheme != "https"
            or not url.host
            or url.userinfo
            or url.query
            or url.fragment
            or not url.path.rstrip("/").endswith("/v1")
        ):
            raise ConfigurationError("base_url must be an HTTPS API root ending in /v1")
        if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise ConfigurationError("timeout must be a finite positive number")
        if (
            isinstance(max_retries, bool)
            or not isinstance(max_retries, int)
            or not 0 <= max_retries <= 3
        ):
            raise ConfigurationError("max_retries must be an integer from 0 to 3")
        self._key = key
        self._http = httpx.Client(
            base_url=str(url).rstrip("/") + "/",
            timeout=timeout,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
            params=UTM_PARAMS,
            headers={"Accept": "application/json", "User-Agent": f"ionoflux-python/{VERSION}"},
        )
        self._max_retries = max_retries
        self.space_weather = SpaceWeather(self)
        self.solar = Solar(self)
        self.geomagnetic = Geomagnetic(self)
        self.alerts = Alerts(self)
        self.data = Data(self)
        self.ionosphere = Ionosphere(self)
        self.propagation = Propagation(self)
        self.observations = Observations(self)

    def __repr__(self) -> str:
        return "Client(api_key=<redacted>)"

    @property
    def is_closed(self) -> bool:
        return self._http.is_closed

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def _redact(self, text: str) -> str:
        if self._key:
            for token in (self._key, quote(self._key, safe=""), json.dumps(self._key)[1:-1]):
                text = text.replace(token, "<redacted>")
        return text

    def _get(
        self, path: str, params: Params | None = None, *, public: bool = False, array: bool = False
    ) -> APIResponse[Any]:
        if not public and not self._key:
            raise ConfigurationError(
                f"Set IONOFLUX_API_KEY or api_key to a Server API key. Get an API key: {KEY_URL}"
            )
        for attempt in range(self._max_retries + 1):
            response: httpx.Response | None = None
            retryable = False
            decoding_failure = False
            try:
                # No API key at all for unauthenticated metadata routes.
                response = self._http.get(
                    path,
                    params=params,
                    headers={"X-API-Key": self._key} if not public and self._key else {},
                )
            except httpx.RequestError as exc:
                # Do not retain request-bearing HTTPX exceptions or exception chains.
                decoding_failure = isinstance(exc, httpx.DecodingError)
                retryable = isinstance(
                    exc,
                    (
                        httpx.ConnectError,
                        httpx.ConnectTimeout,
                        httpx.ReadError,
                        httpx.ReadTimeout,
                        httpx.RemoteProtocolError,
                    ),
                )
            if response is None:
                if decoding_failure:
                    raise ResponseError("Could not decode the IonoFlux response")
                if retryable and attempt < self._max_retries:
                    time.sleep(0.25 * 2**attempt)
                    continue
                raise TransportError("IonoFlux GET failed after bounded retries")
            headers = {k: self._redact(v) for k, v in response.headers.items() if k in SAFE_HEADERS}
            rate = RateLimit.from_headers(headers)
            code = response.status_code
            if (
                code in (502, 503, 504)
                and attempt < self._max_retries
                and rate.retry_after is None
                and rate.remaining != 0
            ):
                response.close()
                time.sleep(0.25 * 2**attempt)
                continue
            if not 200 <= code < 300:
                detail = "Request failed"
                try:
                    body = response.json()
                    if isinstance(body, dict) and "detail" in body:
                        detail = json.dumps(body["detail"], ensure_ascii=False)
                except (ValueError, UnicodeError):
                    pass  # HTML/proxy errors are never copied into exceptions.
                detail = self._redact(detail)[:2000]
                response.close()
                error = {
                    401: AuthenticationError,
                    403: PermissionDeniedError,
                    404: NotFoundError,
                    422: ValidationError,
                    429: RateLimitError,
                }.get(code, APIError)
                if 300 <= code < 400:
                    error = RedirectError
                elif code >= 500:
                    error = ServerError
                raise error(code, detail, rate)
            payload: Any = None
            valid = False
            try:
                payload = response.json()
                valid = (
                    isinstance(payload, list) and all(isinstance(item, dict) for item in payload)
                    if array
                    else isinstance(payload, dict)
                )
            except (ValueError, UnicodeError):
                pass
            raw = response.content
            response.close()
            if not valid:
                raise ResponseError(
                    "Expected a JSON array of objects" if array else "Expected a JSON object"
                )
            return APIResponse(payload, raw, code, headers, rate)
        raise AssertionError("unreachable")

    def sources(self) -> APIResponse[JSONObject]:
        return self._get("sources", public=True)

    def statistics(
        self,
        metric: Metric,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        source: str | None = None,
    ) -> APIResponse[JSONObject]:
        if metric not in METRIC_SOURCES:
            raise ValueError("Unsupported metric; see the API contract")
        if source is not None and source not in METRIC_SOURCES[metric]:
            raise ValueError("Unsupported source for this metric")
        params: Params = date_range(start, end)
        if source is not None:
            params["source"] = source
        return self._get(f"statistics/{metric}", params)


class Resource:
    def __init__(self, client: Client) -> None:
        self._client = client

    def _series(
        self,
        path: str,
        *,
        start: datetime | None,
        end: datetime | None,
        interval: Interval,
        limit: int,
        **extra: Any,
    ) -> APIResponse[JSONObject]:
        integer(limit, 10000)
        if interval not in INTERVALS:
            raise ValueError("Unsupported interval")
        params: Params = date_range(start, end)
        params.update(interval=interval, limit=limit)
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._client._get(path, params)


class SpaceWeather(Resource):
    def current(self) -> APIResponse[JSONObject]:
        return self._client._get("space-weather/current")


class Alerts(Resource):
    def list(
        self,
        *,
        since: datetime | None = None,
        category: list[Category] | None = None,
        limit: int = 50,
    ) -> APIResponse[list[JSONObject]]:
        integer(limit, 500)
        if category is not None and any(c not in CATEGORIES for c in category):
            raise ValueError("Unsupported alert category")
        params: Params = {"limit": limit}
        if since is not None:
            params["since"] = utc(since).isoformat()
        if category is not None:
            params["category"] = category
        return self._client._get("alerts", params, array=True)

    def scales(self) -> APIResponse[JSONObject]:
        return self._client._get("alerts/scales")


class Data(Resource):
    def status(self, dataset: Dataset | None = None) -> APIResponse[JSONObject]:
        if dataset is not None and dataset not in DATASETS:
            raise ValueError("Unsupported dataset; see the API contract")
        return self._client._get("data-status" + (f"/{dataset}" if dataset else ""), public=True)


class Solar(Resource):
    def flux(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        interval: Interval = "raw",
        limit: int = 5000,
    ) -> APIResponse[JSONObject]:
        return self._series("solar/flux", start=start, end=end, interval=interval, limit=limit)

    def sunspots(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        interval: Interval = "raw",
        limit: int = 5000,
        source: Literal["swpc", "silso"] | None = None,
    ) -> APIResponse[JSONObject]:
        if source not in ("swpc", "silso", None):
            raise ValueError("Unsupported source")
        return self._series(
            "solar/sunspots", start=start, end=end, interval=interval, limit=limit, source=source
        )

    def xray(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        interval: Interval = "raw",
        limit: int = 5000,
        band: Literal["long", "short"] = "long",
    ) -> APIResponse[JSONObject]:
        if band not in ("long", "short"):
            raise ValueError("Unsupported band")
        return self._series(
            "solar/xray", start=start, end=end, interval=interval, limit=limit, band=band
        )

    def wind(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        interval: Interval = "raw",
        limit: int = 5000,
        parameter: Literal["speed", "density", "bt", "bz"] = "speed",
    ) -> APIResponse[JSONObject]:
        if parameter not in ("speed", "density", "bt", "bz"):
            raise ValueError("Unsupported parameter")
        return self._series(
            "solar/wind", start=start, end=end, interval=interval, limit=limit, parameter=parameter
        )


class Geomagnetic(Resource):
    def kp(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        interval: Interval = "raw",
        limit: int = 5000,
        source: Literal["swpc", "gfz"] | None = None,
        include_forecast: bool = True,
    ) -> APIResponse[JSONObject]:
        if source not in ("swpc", "gfz", None):
            raise ValueError("Unsupported source")
        if not isinstance(include_forecast, bool):
            raise ValueError("include_forecast must be a boolean")
        return self._series(
            "geomagnetic/kp",
            start=start,
            end=end,
            interval=interval,
            limit=limit,
            source=source,
            include_forecast=include_forecast,
        )

    def ap(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        interval: Interval = "raw",
        limit: int = 5000,
    ) -> APIResponse[JSONObject]:
        return self._series("geomagnetic/ap", start=start, end=end, interval=interval, limit=limit)


def _time(params: Params, name: str, value: datetime | None) -> None:
    if value is not None:
        params[name] = utc(value).isoformat()


class Ionosphere(Resource):
    """GloTEC-derived maps (model) and GIRO ionosonde measurements (observations)."""

    @staticmethod
    def _map(time: datetime | None, lat: float | None, lon: float | None, fmt: str) -> Params:
        choice("format", fmt, ("json", "geojson"))
        params: Params = {"format": fmt}
        _time(params, "time", time)
        if (lat is None) != (lon is None):
            raise ValueError("Pass lat and lon together for a point value, or neither for the grid")
        if lat is not None and lon is not None:
            params["lat"] = number("lat", lat, -90, 90)
            params["lon"] = number("lon", lon, -180, 180)
        return params

    def tec(
        self,
        *,
        time: datetime | None = None,
        lat: float | None = None,
        lon: float | None = None,
        format: Literal["json", "geojson"] = "json",
    ) -> APIResponse[JSONObject]:
        return self._client._get("ionosphere/tec", self._map(time, lat, lon, format))

    def muf(
        self,
        *,
        time: datetime | None = None,
        lat: float | None = None,
        lon: float | None = None,
        format: Literal["json", "geojson"] = "json",
        hop_km: float = 3000.0,
        source: Literal["model", "ionosonde"] = "model",
    ) -> APIResponse[JSONObject]:
        choice("source", source, ("model", "ionosonde"))
        params = self._map(time, lat, lon, format)
        if source == "ionosonde" and (lat is not None or format != "json" or hop_km != 3000.0):
            # The server returns measured station values only; it would silently ignore these.
            raise ValueError("source='ionosonde' does not accept lat/lon, geojson or hop_km")
        params.update(hop_km=number("hop_km", hop_km, 0, 4000), source=source)
        return self._client._get("ionosphere/muf", params)

    def stations(self, *, max_age_hours: int = 6) -> APIResponse[JSONObject]:
        params = {"max_age_hours": whole("max_age_hours", max_age_hours, 1, 48)}
        return self._client._get("ionosphere/stations", params)


class Propagation(Resource):
    """IonoFlux HF path model predictions; see the response `model` for method and limits."""

    @staticmethod
    def _link(
        mode: PropagationMode,
        power: float,
        tx_gain: float,
        rx_gain: float,
        noise: NoiseEnvironment,
        path: Literal["auto", "short", "long"],
    ) -> Params:
        choice("mode", mode, PROPAGATION_MODES)
        choice("noise", noise, NOISE_ENVIRONMENTS)
        choice("path", path, ("auto", "short", "long"))
        return {
            "mode": mode,
            "power": number("power", power, 0, 100000, above=True),
            "tx_gain": number("tx_gain", tx_gain, -20, 30),
            "rx_gain": number("rx_gain", rx_gain, -20, 30),
            "noise": noise,
            "path": path,
        }

    def path(
        self,
        from_: str,
        to: str,
        frequency: float,
        *,
        time: datetime | None = None,
        mode: PropagationMode = "ft8",
        power: float = 100.0,
        tx_gain: float = 2.15,
        rx_gain: float = 2.15,
        noise: NoiseEnvironment = "rural",
        path: Literal["auto", "short", "long"] = "auto",
    ) -> APIResponse[JSONObject]:
        params: Params = {
            "from": place("from_", from_),
            "to": place("to", to),
            "frequency": number("frequency", frequency, 1.8, 54),
        }
        params.update(self._link(mode, power, tx_gain, rx_gain, noise, path))
        _time(params, "datetime", time)
        return self._client._get("propagation/path", params)

    def forecast(
        self,
        from_: str,
        to: str,
        *,
        start: datetime | None = None,
        hours: int = 24,
        mode: PropagationMode = "ft8",
        power: float = 100.0,
        tx_gain: float = 2.15,
        rx_gain: float = 2.15,
        noise: NoiseEnvironment = "rural",
        path: Literal["auto", "short", "long"] = "auto",
    ) -> APIResponse[JSONObject]:
        params: Params = {
            "from": place("from_", from_),
            "to": place("to", to),
            "hours": whole("hours", hours, 1, 72),
        }
        params.update(self._link(mode, power, tx_gain, rx_gain, noise, path))
        _time(params, "start", start)
        return self._client._get("propagation/forecast", params)

    def conditions(
        self, location: str | None = None, *, time: datetime | None = None
    ) -> APIResponse[JSONObject]:
        params: Params = {}
        if location is not None:
            params["location"] = place("location", location)
        _time(params, "datetime", time)
        return self._client._get("propagation/conditions", params)


class Observations(Resource):
    """Real PSK Reporter / WSPRnet reception reports; absence of reports is not a closed band."""

    def live(
        self,
        *,
        minutes: int = 15,
        band: Band | None = None,
        mode: str | None = None,
        source: Literal["pskreporter", "wsprnet"] | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        limit: int = 2000,
    ) -> APIResponse[JSONObject]:
        params: Params = {
            "minutes": whole("minutes", minutes, 1, 60),
            "limit": whole("limit", limit, 1, 5000),
        }
        if source is not None:
            choice("source", source, ("pskreporter", "wsprnet"))
            params["source"] = source
        if bbox is not None:
            if not isinstance(bbox, tuple) or len(bbox) != 4:
                raise ValueError("bbox must be a (min_lon, min_lat, max_lon, max_lat) tuple")
            w, s, e, n = (
                number("bbox longitude", bbox[0], -180, 180),
                number("bbox latitude", bbox[1], -90, 90),
                number("bbox longitude", bbox[2], -180, 180),
                number("bbox latitude", bbox[3], -90, 90),
            )
            if not (w < e and s < n):
                raise ValueError("bbox requires min_lon < max_lon and min_lat < max_lat")
            params["bbox"] = f"{w},{s},{e},{n}"
        return self._client._get("observations/live", _filters(params, band, mode))

    def paths(
        self,
        from_: str,
        to: str,
        *,
        radius_km: float = 500.0,
        hours: float = 1.0,
        band: Band | None = None,
    ) -> APIResponse[JSONObject]:
        params: Params = {
            "from": place("from_", from_),
            "to": place("to", to),
            "radius_km": number("radius_km", radius_km, 50, 1500),
            "hours": number("hours", hours, 0, 6, above=True),
        }
        return self._client._get("observations/paths", _filters(params, band, None))

    def bands(
        self,
        location: str | None = None,
        *,
        radius_km: float = 1000.0,
        role: Literal["rx", "tx"] = "rx",
        minutes: int = 15,
        mode: str | None = None,
    ) -> APIResponse[JSONObject]:
        choice("role", role, ("rx", "tx"))
        params: Params = {
            "radius_km": number("radius_km", radius_km, 50, 3000),
            "role": role,
            "minutes": whole("minutes", minutes, 5, 60),
        }
        if location is not None:
            params["location"] = place("location", location)
        return self._client._get("observations/bands", _filters(params, None, mode))

    def callsign(
        self,
        callsign: str,
        *,
        role: Literal["tx", "rx"] = "tx",
        hours: float = 24.0,
        limit: int = 300,
    ) -> APIResponse[JSONObject]:
        if not isinstance(callsign, str) or not CALLSIGN.fullmatch(callsign):
            raise ValueError("Invalid callsign")
        choice("role", role, ("tx", "rx"))
        params: Params = {
            "role": role,
            "hours": number("hours", hours, 0, 48, above=True),
            "limit": whole("limit", limit, 1, 1000),
        }
        return self._client._get(f"observations/callsign/{quote(callsign, safe='')}", params)


def _filters(params: Params, band: Band | None, mode: str | None) -> Params:
    if band is not None:
        choice("band", band, BANDS)
        params["band"] = band
    if mode is not None:
        if not isinstance(mode, str) or not 1 <= len(mode) <= 16:
            raise ValueError("mode must be a string of 1 to 16 characters")
        params["mode"] = mode
    return params
