import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

import ionoflux
from ionoflux import (
    APIError,
    AuthenticationError,
    Client,
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

KEY = "sdk_mock_secret_never_real"


def client(handler, **kwargs):
    return Client(KEY, transport=httpx.MockTransport(handler), **kwargs)


def test_current_raw_metadata_session_and_context():
    payload = {
        "generated_at": "2026-10-20T00:00:00Z",
        "solar": {"sfi": None},
        "freshness": [],
        "extra_future_field": {"unit": "sfu", "source": "swpc"},
    }
    seen = []

    def handler(request):
        seen.append(request)
        assert request.headers["X-API-Key"] == KEY
        assert KEY not in str(request.url)
        assert request.url.path == "/v1/space-weather/current"
        return httpx.Response(
            200,
            json=payload,
            headers={
                "X-RateLimit-Limit": "1000",
                "X-RateLimit-Remaining": "997",
                "X-RateLimit-Reset": "123",
                "X-API-Key": KEY,
            },
        )

    with client(handler) as c:
        session = c._http
        response = c.space_weather.current()
        c.space_weather.current()
        assert c._http is session
        assert KEY not in repr(c)
        assert response.data == payload
        assert json.loads(response.raw_body) == payload
        assert response.rate_limit.reset_seconds == 123
        assert response.rate_limit.remaining == 997
        assert "x-api-key" not in response.headers
    assert c.is_closed
    assert len(seen) == 2


def test_environment_precedence_and_public_routes(monkeypatch):
    monkeypatch.setenv("IONOFLUX_API_KEY", "environment_key")
    with Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(200, json={"key": r.headers.get("x-api-key")})
        )
    ) as c:
        assert c.space_weather.current().data["key"] == "environment_key"
        assert c.sources().data["key"] is None
    with client(lambda r: httpx.Response(200, json={"key": r.headers["x-api-key"]})) as c:
        assert c.space_weather.current().data["key"] == KEY


def test_missing_key_allows_metadata_but_not_private_calls():
    paths = []

    def handler(r):
        paths.append(r.url.path)
        assert "x-api-key" not in r.headers
        return httpx.Response(200, json={})

    with Client(transport=httpx.MockTransport(handler)) as c:
        c.sources()
        c.data.status()
        c.data.status("sfi")
        with pytest.raises(ConfigurationError) as caught:
            c.space_weather.current()
    assert paths == ["/v1/sources", "/v1/data-status", "/v1/data-status/sfi"]
    message = str(caught.value)
    assert "IONOFLUX_API_KEY or api_key" in message
    assert message.endswith("Get an API key: https://ionoflux.runvia.app/account")
    assert "\n" not in message


def test_requests_carry_fixed_sdk_utm_tags_and_version():
    seen = []

    def handler(r):
        seen.append(r)
        return httpx.Response(200, json={})

    tags = {"utm_source": "python", "utm_medium": "sdk", "utm_content": ionoflux.__version__}
    with client(handler) as c:
        c.sources()
        c.solar.flux(interval="1d", limit=10)
    assert ionoflux.__version__ == "0.1.2"
    for r in seen:
        assert {k: r.url.params[k] for k in tags} == tags
        assert r.headers["user-agent"] == f"ionoflux-python/{ionoflux.__version__}"
        assert KEY not in str(r.url)
    assert seen[0].url.params.keys() == tags.keys()
    assert seen[1].url.params["interval"] == "1d"
    assert seen[1].url.params["limit"] == "10"


@pytest.mark.parametrize("key", ["", " ", "line\nbreak", "nonascii_한", "space key", "x\x7f"])
def test_bad_keys(key):
    with pytest.raises(ConfigurationError):
        Client(key)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/v1",
        "https://user:pass@example.com/v1",
        "https://example.com/v1?q=x",
        "https://example.com/v1#x",
        "https://example.com",
        "//example.com/v1",
    ],
)
def test_unsafe_base_url(url):
    with pytest.raises(ConfigurationError):
        Client(KEY, base_url=url)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_retries": -1},
        {"max_retries": 4},
        {"max_retries": True},
        {"timeout": 0},
        {"timeout": float("inf")},
        {"timeout": float("nan")},
    ],
)
def test_bad_configuration(kwargs):
    with pytest.raises(ConfigurationError):
        Client(KEY, **kwargs)


def test_custom_base_url():
    with client(
        lambda r: httpx.Response(200, json={"url": str(r.url)}),
        base_url="https://staging.example/api/v1/",
    ) as c:
        url = httpx.URL(c.sources().data["url"])
        assert url.copy_with(query=None) == "https://staging.example/api/v1/sources"


@pytest.mark.parametrize(
    "status,error",
    [
        (401, AuthenticationError),
        (403, PermissionDeniedError),
        (404, NotFoundError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, ServerError),
        (503, ServerError),
        (400, APIError),
        (302, RedirectError),
    ],
)
def test_structured_errors_and_redaction(status, error):
    calls = []

    def handler(r):
        calls.append(r)
        return httpx.Response(
            status,
            json={"detail": f"bad key {KEY}"},
            headers={
                "Retry-After": "80000",
                "X-RateLimit-Reset": "80000",
                "Location": "https://attacker.example/",
            },
        )

    with client(handler, max_retries=0) as c, pytest.raises(error) as caught:
        c.space_weather.current()
    e = caught.value
    assert e.status_code == status
    assert e.retry_after == "80000"
    assert e.rate_limit.reset_seconds == 80000
    assert KEY not in str(e) + repr(e) + e.detail
    assert not hasattr(e, "request")
    assert not hasattr(e, "response")
    assert len(calls) == 1


def test_no_retry_or_sleep_for_quota(monkeypatch):
    def no_sleep(_):
        pytest.fail("429 must not sleep")

    monkeypatch.setattr("ionoflux._client.time.sleep", no_sleep)
    with client(
        lambda r: httpx.Response(429, json={"detail": "quota"}, headers={"Retry-After": "86400"}),
        max_retries=3,
    ) as c:
        with pytest.raises(RateLimitError):
            c.solar.flux()


@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
def test_redirect_never_leaks_header(code):
    seen = []

    def handler(r):
        seen.append(r.url.host)
        return httpx.Response(code, headers={"Location": "https://attacker.example/collect"})

    with client(handler) as c, pytest.raises(RedirectError):
        c.solar.flux()
    assert seen == ["ionoflux.runvia.app"]


@pytest.mark.parametrize("failure", ["connect", "timeout", "503"])
def test_bounded_retries_then_success(monkeypatch, failure):
    calls = []
    sleeps = []
    monkeypatch.setattr("ionoflux._client.time.sleep", sleeps.append)

    def handler(r):
        calls.append(r.method)
        if len(calls) < 3:
            if failure == "connect":
                raise httpx.ConnectError(KEY, request=r)
            if failure == "timeout":
                raise httpx.ReadTimeout(KEY, request=r)
            return httpx.Response(503, json={})
        return httpx.Response(200, json={})

    with client(handler, max_retries=2) as c:
        c.solar.flux()
    assert calls == ["GET"] * 3
    assert sleeps == [0.25, 0.5]


def test_transport_exception_has_no_secret_context(monkeypatch):
    monkeypatch.setattr("ionoflux._client.time.sleep", lambda _: None)

    def handler(r):
        raise httpx.ReadTimeout(KEY, request=r)

    with client(handler) as c, pytest.raises(TransportError) as caught:
        c.solar.flux()
    assert KEY not in str(caught.value)
    assert caught.value.__context__ is None


@pytest.mark.parametrize("body", [b"not-json", b"[]", b"null", b"1"])
def test_malformed_success(body):
    with client(lambda r: httpx.Response(200, content=body)) as c:
        with pytest.raises(ResponseError):
            c.solar.flux()


def test_validation_error_array_and_html_server_error():
    with client(
        lambda r: httpx.Response(422, json={"detail": [{"msg": "invalid", "input": KEY}]})
    ) as c:
        with pytest.raises(ValidationError) as e:
            c.solar.flux()
        assert KEY not in e.value.detail
        assert "invalid" in e.value.detail
    with client(lambda r: httpx.Response(500, text=KEY)) as c:
        with pytest.raises(ServerError) as e:
            c.solar.flux()
        assert KEY not in str(e.value)


@pytest.mark.parametrize(
    "method,path,extra",
    [
        ("solar.flux", "solar/flux", {}),
        ("solar.sunspots", "solar/sunspots", {"source": "silso"}),
        ("solar.xray", "solar/xray", {"band": "short"}),
        ("solar.wind", "solar/wind", {"parameter": "bz"}),
        ("geomagnetic.kp", "geomagnetic/kp", {"source": "gfz", "include_forecast": False}),
        ("geomagnetic.ap", "geomagnetic/ap", {}),
    ],
)
def test_series_endpoints_and_lossless_payload(method, path, extra):
    payload = {
        "metric": "test",
        "unit": "nT",
        "attribution": {"license": "CC BY 4.0"},
        "latest": None,
        "last_updated": None,
        "data": [{"value": None}],
        "forecast": [{"status": "predicted", "kp": 5}],
    }

    def handler(r):
        assert r.url.path == "/v1/" + path
        assert r.url.params["interval"] == "1mo"
        assert r.url.params["limit"] == "10000"
        assert r.url.params["start"] == "2026-10-01T00:00:00+00:00"
        for k, v in extra.items():
            assert r.url.params[k] == (str(v).lower() if isinstance(v, bool) else v)
        return httpx.Response(200, json=payload)

    with client(handler) as c:
        group, name = method.split(".")
        response = getattr(getattr(c, group), name)(
            start=datetime(2026, 10, 1, 9, tzinfo=timezone(timedelta(hours=9))),
            end=datetime(2026, 10, 2, tzinfo=UTC),
            interval="1mo",
            limit=10000,
            **extra,
        )
        assert response.data == payload


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit": 0},
        {"limit": 10001},
        {"limit": True},
        {"interval": "month"},
        {"start": datetime(2026, 1, 1)},
        {"start": datetime(2026, 1, 2, tzinfo=UTC), "end": datetime(2026, 1, 1, tzinfo=UTC)},
        {"start": datetime(2000, 1, 1, tzinfo=UTC), "end": datetime(2026, 1, 1, tzinfo=UTC)},
    ],
)
def test_local_series_validation(kwargs):
    with client(lambda r: pytest.fail("Invalid input must not make a request")) as c:
        with pytest.raises(ValueError):
            c.solar.flux(**kwargs)


def test_source_band_parameter_and_path_validation():
    with client(lambda r: pytest.fail("Must validate locally")) as c:
        for call in [
            lambda: c.solar.sunspots(source="bad"),
            lambda: c.solar.xray(band="bad"),
            lambda: c.solar.wind(parameter="bad"),
            lambda: c.geomagnetic.kp(source="bad"),
            lambda: c.geomagnetic.kp(include_forecast="false"),
            lambda: c.statistics("../admin"),
            lambda: c.statistics("ap", source="swpc"),
            lambda: c.data.status("../admin"),
            lambda: c.alerts.list(category=["bad"]),
            lambda: c.alerts.list(limit=501),
        ]:
            with pytest.raises(ValueError):
                call()


def test_alerts_repeatable_categories_and_scales():
    def handler(r):
        if r.url.path.endswith("scales"):
            return httpx.Response(200, json={"scales": {}, "attribution": {}})
        assert r.url.params.get_list("category") == ["ALERT", "ES_OPENING"]
        assert r.url.params["limit"] == "50"
        assert "since" in r.url.params
        return httpx.Response(200, json=[{"category": "ES_OPENING", "source": "ionoflux"}])

    with client(handler) as c:
        assert (
            c.alerts.list(
                category=["ALERT", "ES_OPENING"], since=datetime(2026, 10, 1, tzinfo=UTC)
            ).data[0]["source"]
            == "ionoflux"
        )
        assert c.alerts.scales().data["scales"] == {}


@pytest.mark.parametrize(
    "metric",
    [
        "sfi",
        "ssn",
        "kp",
        "ap",
        "xray_long",
        "xray_short",
        "solar_wind_speed",
        "solar_wind_density",
        "imf_bt",
        "imf_bz",
    ],
)
def test_all_statistics_metrics(metric):
    with client(
        lambda r: httpx.Response(200, json={"path": r.url.path, "count": 0, "mean": None})
    ) as c:
        assert c.statistics(metric).data["path"] == f"/v1/statistics/{metric}"


def test_contract_defaults_match_captured_openapi():
    schema = json.loads(
        (Path(__file__).parents[1] / "docs/openapi-v0.1.json").read_text(encoding="utf-8")
    )
    paths = schema["paths"]
    seen = []

    def handler(r):
        seen.append(r.url.path)
        template = r.url.path
        if template.startswith("/v1/data-status/"):
            template = "/v1/data-status/{dataset}"
        elif template.startswith("/v1/statistics/"):
            template = "/v1/statistics/{metric}"
        parameters = paths[template]["get"].get("parameters", [])
        for parameter in parameters:
            name, s = parameter["name"], parameter["schema"]
            if "default" in s and name in r.url.params:
                expected = s["default"]
                assert r.url.params[name] == (
                    str(expected).lower() if isinstance(expected, bool) else str(expected)
                )
        return httpx.Response(200, json=[] if r.url.path == "/v1/alerts" else {})

    with client(handler) as c:
        for call in [
            c.solar.flux,
            c.solar.sunspots,
            c.solar.xray,
            c.solar.wind,
            c.geomagnetic.kp,
            c.geomagnetic.ap,
            c.alerts.list,
            c.alerts.scales,
            c.space_weather.current,
            c.sources,
            c.data.status,
            lambda: c.data.status("sfi"),
            lambda: c.statistics("sfi"),
        ]:
            call()
    assert len(seen) == 13


@pytest.mark.parametrize("key", ['mock"quoted\\key', "mock+encoded/key"])
def test_escaped_or_encoded_key_is_redacted(key):
    from urllib.parse import quote

    def handler(r):
        return httpx.Response(422, json={"detail": [key, quote(key, safe="")]})

    with Client(key, transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(ValidationError) as caught:
            c.solar.flux()
        assert key not in str(caught.value)
        assert json.dumps(key)[1:-1] not in str(caught.value)
        assert quote(key, safe="") not in str(caught.value)


def test_empty_alerts_and_missing_or_malformed_rate_headers():
    with client(
        lambda r: httpx.Response(
            200,
            json=[],
            headers={
                "X-RateLimit-Limit": "not-an-integer",
                "X-RateLimit-Reset": "-1",
                "Retry-After": "Wed, 21 Oct 2026 00:00:00 GMT",
            },
        )
    ) as c:
        response = c.alerts.list()
        assert response.data == []
        assert response.rate_limit.limit is None
        assert response.rate_limit.remaining is None
        assert response.rate_limit.reset_seconds is None
        assert response.rate_limit.retry_after == "Wed, 21 Oct 2026 00:00:00 GMT"


def test_all_retries_exhausted_are_bounded(monkeypatch):
    calls, sleeps = [], []
    monkeypatch.setattr("ionoflux._client.time.sleep", sleeps.append)

    def handler(r):
        calls.append(r)
        return httpx.Response(504, json={"detail": "temporarily unavailable"})

    with client(handler, max_retries=3) as c, pytest.raises(ServerError):
        c.solar.flux()
    assert len(calls) == 4
    assert sleeps == [0.25, 0.5, 1.0]


def test_transport_close_on_context_exception():
    closed = []

    class TrackingTransport(httpx.MockTransport):
        def close(self):
            closed.append(True)
            super().close()

    c = Client(KEY, transport=TrackingTransport(lambda r: httpx.Response(200, json={})))
    with pytest.raises(RuntimeError), c:
        raise RuntimeError("application failure")
    assert c.is_closed
    assert closed == [True]


def test_invalid_alert_success_shape():
    with client(lambda r: httpx.Response(200, json={})) as c, pytest.raises(ResponseError):
        c.alerts.list()
