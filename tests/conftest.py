import socket

import pytest


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("IONOFLUX_API_KEY", raising=False)

    def blocked(*args, **kwargs):
        raise AssertionError("Tests must never access the network")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
