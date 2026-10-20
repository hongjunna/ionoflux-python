"""Regression cases discovered during the v0.1 release review; all keys are synthetic."""

import logging

import httpx
import pytest

from ionoflux import Client, RateLimitError, ResponseError, ServerError, TransportError
from scripts.check_artifacts import inspect_file

KEY = "review_mock_key_not_real"


@pytest.mark.parametrize(
    "failure",
    [
        httpx.DecodingError,
        httpx.TooManyRedirects,
        httpx.PoolTimeout,
        httpx.LocalProtocolError,
        httpx.UnsupportedProtocol,
    ],
)
def test_request_failure_is_sanitized_and_not_retried(failure, monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        raise failure(KEY, request=request)

    def no_sleep(_):
        pytest.fail("Permanent/local failures must not retry")

    monkeypatch.setattr("ionoflux._client.time.sleep", no_sleep)
    with Client(KEY, transport=httpx.MockTransport(handler), max_retries=3) as client:
        with pytest.raises((ResponseError, TransportError)) as caught:
            client.solar.flux()
    error = caught.value
    assert KEY not in str(error)
    assert error.__context__ is None
    assert not hasattr(error, "request")
    assert len(calls) == 1


def test_real_invalid_gzip_becomes_safe_response_error():
    def handler(request):
        # A real HTTPX decoder error, not a manually raised transport exception.
        return httpx.Response(200, content=b"not-gzip", headers={"Content-Encoding": "gzip"})

    with Client(KEY, transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ResponseError) as caught:
            client.solar.flux()
    assert caught.value.__context__ is None
    assert not hasattr(caught.value, "request")


@pytest.mark.parametrize("status", [200, 429])
def test_oversized_rate_header_does_not_hide_payload_or_status(status):
    def handler(request):
        return httpx.Response(
            status,
            json={"detail": "quota"},
            headers={"X-RateLimit-Reset": "9" * 5000, "Retry-After": "123"},
        )

    with Client(KEY, transport=httpx.MockTransport(handler)) as client:
        if status == 429:
            with pytest.raises(RateLimitError) as caught:
                client.solar.flux()
            assert caught.value.rate_limit.reset_seconds is None
            assert caught.value.retry_after == "123"
        else:
            assert client.solar.flux().rate_limit.reset_seconds is None


@pytest.mark.parametrize("headers", [{"Retry-After": "86400"}, {"X-RateLimit-Remaining": "0"}])
def test_server_wait_or_exhausted_quota_prevents_5xx_retry(headers, monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(503, json={"detail": "unavailable"}, headers=headers)

    monkeypatch.setattr("ionoflux._client.time.sleep", lambda _: pytest.fail("Must not retry"))
    with Client(KEY, transport=httpx.MockTransport(handler), max_retries=3) as client:
        with pytest.raises(ServerError):
            client.solar.flux()
    assert len(calls) == 1


def test_artifact_scanner_detects_urlsafe_service_key():
    synthetic = b"ifx_" + b"ab_-" * 11
    with pytest.raises(AssertionError, match="Credential-like"):
        inspect_file("ionoflux/example.py", synthetic, True)


@pytest.mark.parametrize(
    "name",
    [
        "ionoflux-0.1.0/docs/agent-handoff.md",
        "ionoflux-0.1.0/docs/development-plan.md",
        "ionoflux-0.1.0/docs/verification.md",
    ],
)
def test_internal_development_docs_are_not_distribution_content(name):
    with pytest.raises(AssertionError):
        inspect_file(name, b"internal", False)


def test_client_does_not_log_authentication_headers(caplog):
    caplog.set_level(logging.DEBUG)
    with Client(
        KEY, transport=httpx.MockTransport(lambda r: httpx.Response(200, json={}))
    ) as client:
        client.solar.flux()
    assert KEY not in caplog.text


@pytest.mark.parametrize("payload", [[1], [None], ["alert"], [{}, 2]])
def test_alert_array_elements_match_advertised_object_type(payload):
    with Client(
        KEY, transport=httpx.MockTransport(lambda r: httpx.Response(200, json=payload))
    ) as c:
        with pytest.raises(ResponseError):
            c.alerts.list()
