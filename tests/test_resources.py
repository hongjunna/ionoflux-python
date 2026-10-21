"""Ionosphere, propagation and observation resources (v0.1.3) against mocked HTTP only."""

from datetime import UTC, datetime, timedelta, timezone

import httpx
import pytest

from ionoflux import Client, ConfigurationError, NotFoundError

KEY = "sdk_mock_secret_never_real"
UTM = {"utm_source", "utm_medium", "utm_content"}


def recorder():
    seen: list[httpx.Request] = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"echo": request.url.path, "attribution": None})

    return Client(KEY, transport=httpx.MockTransport(handler)), seen


def query(request: httpx.Request) -> dict[str, str]:
    return {k: v for k, v in request.url.params.items() if k not in UTM}


KST = timezone(timedelta(hours=9))


@pytest.mark.parametrize(
    "call,path,expected",
    [
        (lambda c: c.ionosphere.tec(), "/v1/ionosphere/tec", {"format": "json"}),
        (
            lambda c: c.ionosphere.tec(
                time=datetime(2026, 10, 21, 9, tzinfo=KST), lat=37.5, lon=127, format="geojson"
            ),
            "/v1/ionosphere/tec",
            {"format": "geojson", "time": "2026-10-21T00:00:00+00:00", "lat": "37.5", "lon": "127"},
        ),
        (
            lambda c: c.ionosphere.muf(hop_km=1500),
            "/v1/ionosphere/muf",
            {"format": "json", "hop_km": "1500", "source": "model"},
        ),
        (
            lambda c: c.ionosphere.muf(source="ionosonde"),
            "/v1/ionosphere/muf",
            {"format": "json", "hop_km": "3000.0", "source": "ionosonde"},
        ),
        (
            lambda c: c.ionosphere.stations(max_age_hours=12),
            "/v1/ionosphere/stations",
            {"max_age_hours": "12"},
        ),
        (
            lambda c: c.propagation.path("Seoul", "FN20", 14.074),
            "/v1/propagation/path",
            {
                "from": "Seoul",
                "to": "FN20",
                "frequency": "14.074",
                "mode": "ft8",
                "power": "100.0",
                "tx_gain": "2.15",
                "rx_gain": "2.15",
                "noise": "rural",
                "path": "auto",
            },
        ),
        (
            lambda c: c.propagation.path(
                "37.5665,126.9780",
                "PM95",
                7.074,
                time=datetime(2026, 10, 21, 12, tzinfo=UTC),
                mode="cw",
                power=5,
                noise="city",
                path="long",
            ),
            "/v1/propagation/path",
            {
                "from": "37.5665,126.9780",
                "to": "PM95",
                "frequency": "7.074",
                "mode": "cw",
                "power": "5",
                "tx_gain": "2.15",
                "rx_gain": "2.15",
                "noise": "city",
                "path": "long",
                "datetime": "2026-10-21T12:00:00+00:00",
            },
        ),
        (
            lambda c: c.propagation.forecast("Seoul", "Tokyo", hours=6, mode="ssb"),
            "/v1/propagation/forecast",
            {
                "from": "Seoul",
                "to": "Tokyo",
                "hours": "6",
                "mode": "ssb",
                "power": "100.0",
                "tx_gain": "2.15",
                "rx_gain": "2.15",
                "noise": "rural",
                "path": "auto",
            },
        ),
        (lambda c: c.propagation.conditions(), "/v1/propagation/conditions", {}),
        (
            lambda c: c.propagation.conditions("IO91", time=datetime(2026, 10, 21, tzinfo=UTC)),
            "/v1/propagation/conditions",
            {"location": "IO91", "datetime": "2026-10-21T00:00:00+00:00"},
        ),
        (
            lambda c: c.observations.live(),
            "/v1/observations/live",
            {"minutes": "15", "limit": "2000"},
        ),
        (
            lambda c: c.observations.live(
                minutes=5, band="20m", mode="FT8", source="wsprnet", bbox=(-10, 35, 30, 60.5)
            ),
            "/v1/observations/live",
            {
                "minutes": "5",
                "limit": "2000",
                "band": "20m",
                "mode": "FT8",
                "source": "wsprnet",
                "bbox": "-10,35,30,60.5",
            },
        ),
        (
            lambda c: c.observations.paths("Seoul", "Tokyo", hours=0.5, band="40m"),
            "/v1/observations/paths",
            {"from": "Seoul", "to": "Tokyo", "radius_km": "500.0", "hours": "0.5", "band": "40m"},
        ),
        (
            lambda c: c.observations.bands(),
            "/v1/observations/bands",
            {"radius_km": "1000.0", "role": "rx", "minutes": "15"},
        ),
        (
            lambda c: c.observations.bands("JO62", role="tx", mode="CW"),
            "/v1/observations/bands",
            {
                "radius_km": "1000.0",
                "role": "tx",
                "minutes": "15",
                "location": "JO62",
                "mode": "CW",
            },
        ),
        (
            lambda c: c.observations.callsign("DS1UPG"),
            "/v1/observations/callsign/DS1UPG",
            {"role": "tx", "hours": "24.0", "limit": "300"},
        ),
    ],
)
def test_requests(call, path, expected):
    c, seen = recorder()
    with c:
        response = call(c)
    assert response.data["echo"] == path
    (request,) = seen
    assert request.method == "GET"
    assert request.url.path == path
    assert request.headers["X-API-Key"] == KEY
    assert query(request) == expected
    assert UTM <= set(request.url.params)


def test_callsign_path_is_encoded():
    c, seen = recorder()
    with c:
        c.observations.callsign("DS1UPG/P", role="rx", hours=1, limit=10)
    assert seen[0].url.raw_path.startswith(b"/v1/observations/callsign/DS1UPG%2FP?")


@pytest.mark.parametrize(
    "call",
    [
        lambda c: c.ionosphere.tec(lat=10),
        lambda c: c.ionosphere.tec(lon=10),
        lambda c: c.ionosphere.tec(lat=91, lon=0),
        lambda c: c.ionosphere.tec(lat=0, lon=float("nan")),
        lambda c: c.ionosphere.tec(lat=True, lon=0),
        lambda c: c.ionosphere.tec(format="csv"),
        lambda c: c.ionosphere.tec(time=datetime(2026, 10, 21)),
        lambda c: c.ionosphere.muf(hop_km=4001),
        lambda c: c.ionosphere.muf(source="measured"),
        lambda c: c.ionosphere.muf(source="ionosonde", lat=1, lon=1),
        lambda c: c.ionosphere.muf(source="ionosonde", format="geojson"),
        lambda c: c.ionosphere.muf(source="ionosonde", hop_km=1000),
        lambda c: c.ionosphere.stations(max_age_hours=0),
        lambda c: c.ionosphere.stations(max_age_hours=49),
        lambda c: c.propagation.path("S", "Tokyo", 14),
        lambda c: c.propagation.path("Seoul", "x" * 201, 14),
        lambda c: c.propagation.path("Seoul", "Tokyo", 1.7),
        lambda c: c.propagation.path("Seoul", "Tokyo", 55),
        lambda c: c.propagation.path("Seoul", "Tokyo", 14, mode="FT8"),
        lambda c: c.propagation.path("Seoul", "Tokyo", 14, power=0),
        lambda c: c.propagation.path("Seoul", "Tokyo", 14, tx_gain=31),
        lambda c: c.propagation.path("Seoul", "Tokyo", 14, noise="urban"),
        lambda c: c.propagation.path("Seoul", "Tokyo", 14, path="both"),
        lambda c: c.propagation.path("Seoul", "Tokyo", 14, time=datetime(2026, 1, 1)),
        lambda c: c.propagation.forecast("Seoul", "Tokyo", hours=73),
        lambda c: c.propagation.forecast("Seoul", "Tokyo", hours=1.5),
        lambda c: c.propagation.conditions("X"),
        lambda c: c.observations.live(minutes=61),
        lambda c: c.observations.live(limit=5001),
        lambda c: c.observations.live(band="2m"),
        lambda c: c.observations.live(mode=""),
        lambda c: c.observations.live(mode="X" * 17),
        lambda c: c.observations.live(source="rbn"),
        lambda c: c.observations.live(bbox=(30, 35, -10, 60)),
        lambda c: c.observations.live(bbox=(-10, 35, 30)),
        lambda c: c.observations.live(bbox=[-10, 35, 30, 60]),
        lambda c: c.observations.live(bbox=(-181, 35, 30, 60)),
        lambda c: c.observations.paths("Seoul", "Tokyo", radius_km=49),
        lambda c: c.observations.paths("Seoul", "Tokyo", hours=0),
        lambda c: c.observations.paths("Seoul", "Tokyo", hours=6.5),
        lambda c: c.observations.bands(radius_km=3001),
        lambda c: c.observations.bands(minutes=4),
        lambda c: c.observations.bands(role="both"),
        lambda c: c.observations.callsign("../x"),
        lambda c: c.observations.callsign("AB"),
        lambda c: c.observations.callsign("DS1UPG?role=rx"),
        lambda c: c.observations.callsign("DS1UPG", hours=49),
        lambda c: c.observations.callsign("DS1UPG", limit=1001),
        lambda c: c.observations.callsign("DS1UPG", role="any"),
    ],
)
def test_invalid_arguments_never_send(call):
    c, seen = recorder()
    with c, pytest.raises(ValueError):
        call(c)
    assert seen == []


def test_new_resources_require_server_key():
    def handler(request):
        raise AssertionError("must not send without a key")

    with Client(transport=httpx.MockTransport(handler)) as c:
        for call in (
            c.ionosphere.tec,
            c.ionosphere.stations,
            c.propagation.conditions,
            c.observations.live,
            lambda: c.propagation.path("Seoul", "Tokyo", 14),
        ):
            with pytest.raises(ConfigurationError, match="account"):
                call()


def test_payload_and_errors_pass_through_unchanged():
    payload = {
        "time": "2026-10-21T00:00:00Z",
        "attribution": {"key": "giro", "license": "x"},
        "stations": [{"code": "JJ433", "fof2_mhz": None, "future": 1}],
    }

    def handler(request):
        if request.url.path.endswith("/callsign/N0CALL"):
            return httpx.Response(404, json={"detail": "Not Found"})
        return httpx.Response(200, json=payload)

    with Client(KEY, transport=httpx.MockTransport(handler)) as c:
        assert c.ionosphere.muf(source="ionosonde").data == payload
        with pytest.raises(NotFoundError):
            c.observations.callsign("N0CALL")
