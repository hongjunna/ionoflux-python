"""Runnable without an API key or network: python examples/offline.py."""

import httpx

from ionoflux import Client


def mock_api(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "generated_at": "2026-10-20T00:00:00Z",
            "solar": {"sfi": {"value": 123.0, "time": "2026-10-19T20:00:00Z", "source": "swpc"}},
            "geomagnetic": {"kp": None},
            "ionosphere": {},
            "noaa_scales": None,
            "alerts_last_24h": 0,
            "freshness": [],
        },
    )


with Client(api_key="offline_example_only", transport=httpx.MockTransport(mock_api)) as client:
    current = client.space_weather.current()
    print(current.data["solar"]["sfi"])
