"""Requires IONOFLUX_API_KEY; deliberately not executed in CI."""

from ionoflux import Client

with Client() as client:
    current = client.space_weather.current()
    print(current.data)
