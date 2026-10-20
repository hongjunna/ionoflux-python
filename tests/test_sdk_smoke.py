"""Offline regression tests for the optional live workflow; never contact IonoFlux."""

import copy
import importlib.util
import json
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github/scripts/sdk_smoke.py"
if not SCRIPT.exists():
    pytest.skip("Repository-only smoke workflow", allow_module_level=True)
spec = importlib.util.spec_from_file_location("sdk_smoke", SCRIPT)
assert spec and spec.loader
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)
KEY = "offline-smoke-secret"
NOW = smoke.datetime(2026, 10, 20, tzinfo=smoke.UTC)
STAMP = "2026-10-20T00:00:00Z"


@pytest.fixture
def payloads():
    schema = json.loads((ROOT / "docs/openapi-v0.1.json").read_text())["components"]["schemas"]
    sfi = copy.deepcopy(schema["SeriesResponse"]["example"])
    kp = copy.deepcopy(sfi)
    kp.update(metric="kp", unit="index", forecast=None)
    statistics = {
        k: None
        for k in (
            "min",
            "max",
            "mean",
            "median",
            "stddev",
            "first",
            "last",
            "change",
            "first_time",
            "last_time",
        )
    }
    statistics.update(metric="sfi", source="swpc", unit="sfu", start=STAMP, end=STAMP, count=0)
    return dict(
        zip(
            smoke.PATHS,
            [
                copy.deepcopy(schema["CurrentResponse"]["example"]),
                sfi,
                kp,
                statistics,
                [],
                {"fetched_at": STAMP, "attribution": sfi["attribution"], "scales": {}},
                {
                    "sources": {"swpc": {"name": "NOAA", "url": None, "license": None}},
                    "collectors": [],
                },
                {
                    "generated_at": STAMP,
                    "datasets": [{"first_time": None, "last_time": None}],
                    "spot_archive": {},
                },
                {"dataset": "sfi", "rows": [{"time": STAMP, "value": None}]},
            ],
            strict=True,
        )
    )


def exercise(payloads, handler=None):
    calls = []

    def respond(request):
        calls.append(request)
        assert request.method == "GET"
        assert request.url.host == "ionoflux.runvia.app"
        assert KEY not in str(request.url)
        index = len(calls) - 1
        if index < 6:
            assert request.headers["x-api-key"] == KEY
        else:
            assert "x-api-key" not in request.headers
        assert request.extensions["timeout"] == dict.fromkeys(
            ("connect", "read", "write", "pool"), 10
        )
        if handler:
            result = handler(request, index)
            if result is not None:
                return result
        return httpx.Response(200, json=payloads[request.url.path.removeprefix("/v1")])

    summary = smoke.run(KEY, smoke.ORIGIN, transport=httpx.MockTransport(respond), now=NOW)
    return summary, calls


def test_nine_sequential_gets_and_close(payloads):
    original = copy.deepcopy(payloads)
    result, calls = exercise(payloads)
    assert result["result"] == "PASS"
    assert result["requests"] == len(calls) == 9
    assert result["session_closed"]
    assert [r.url.path for r in calls] == ["/v1" + p for p in smoke.PATHS]
    assert payloads == original
    assert calls[1].url.params["limit"] == "3"
    assert calls[2].url.params["include_forecast"] == "false"
    assert all(
        "start" not in r.url.params or r.url.params["start"].endswith("+00:00") for r in calls
    )


@pytest.mark.parametrize("status", [401, 403, 429])
@pytest.mark.parametrize("index", [0, 3, 8])
def test_auth_quota_immediate_stop(payloads, status, index):
    def fail(request, n):
        return (
            httpx.Response(status, json={"detail": KEY}, headers={"Retry-After": "86400"})
            if n == index
            else None
        )

    summary, calls = exercise(payloads, fail)
    assert len(calls) == summary["requests"] == index + 1
    assert summary["checks"][-1]["http_status"] == status
    assert summary["result"] == "FAIL" and summary["session_closed"]
    assert KEY not in json.dumps(summary)


@pytest.mark.parametrize("status", [302, 404, 422, 500, 502, 503, 504])
def test_no_redirect_or_retry_on_other_error(payloads, status):
    def fail(request, n):
        return httpx.Response(
            status, json={"detail": KEY}, headers={"Location": "https://untrusted.invalid/"}
        )

    summary, calls = exercise(payloads, fail)
    assert summary["requests"] == len(calls) == 1
    assert summary["result"] == "FAIL" and summary["session_closed"]


def test_timeout_is_not_retried(payloads):
    def fail(request, n):
        raise httpx.ReadTimeout(KEY, request=request)

    summary, calls = exercise(payloads, fail)
    assert summary["result"] == "FAIL" and summary["requests"] == len(calls) == 1
    assert KEY not in json.dumps(summary)
    assert summary["session_closed"]


@pytest.mark.parametrize(
    "url", [smoke.ORIGIN, smoke.ORIGIN + "/", smoke.ORIGIN + "/v1", smoke.ORIGIN + "/v1/"]
)
def test_safe_service_root_normalization(url):
    assert smoke.base_url(url) == smoke.ORIGIN + "/v1"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "http://ionoflux.runvia.app",
        "https://untrusted.invalid/v1",
        "https://user:pass@ionoflux.runvia.app/v1",
        smoke.ORIGIN + "?key=secret",
        smoke.ORIGIN + "/#fragment",
        smoke.ORIGIN + "/api/v1",
        smoke.ORIGIN + ":444/v1",
    ],
)
def test_bad_url_stops_before_any_request(url):
    result = smoke.run(KEY, url, transport=httpx.MockTransport(lambda r: pytest.fail("network")))
    assert result["requests"] == 0 and result["result"] == "FAIL"


@pytest.mark.parametrize(
    "change", ["utc", "missing_field", "wrong_unit", "wrong_source", "wrong_null"]
)
def test_schema_and_metadata_failures_stop(payloads, change):
    if change == "utc":
        payloads["/solar/flux"]["start"] = "2026-10-20T09:00:00+09:00"
    elif change == "missing_field":
        del payloads["/solar/flux"]["attribution"]["license"]
    elif change == "wrong_unit":
        payloads["/solar/flux"]["unit"] = "index"
    elif change == "wrong_source":
        payloads["/solar/flux"]["source"] = "unexpected"
    else:
        payloads["/solar/flux"]["data"][0]["value"] = "missing"
    result, calls = exercise(payloads)
    assert result["result"] == "FAIL" and len(calls) == 2


def test_null_and_missing_samples_pass_without_fabrication(payloads):
    payloads["/solar/flux"].update(data=[], latest=None, last_updated=None)
    payloads["/space-weather/current"]["solar"]["sfi"] = None
    result, _ = exercise(payloads)
    assert result["result"] == "PASS"
    assert payloads["/solar/flux"]["data"] == []
    assert payloads["/solar/flux"]["latest"] is None


def test_budget_and_method_enforced():
    budget = smoke.BudgetTransport(httpx.MockTransport(lambda r: httpx.Response(200)))
    for _ in range(9):
        budget.handle_request(httpx.Request("GET", smoke.ORIGIN + "/v1/sources"))
    with pytest.raises(ValueError):
        budget.handle_request(httpx.Request("GET", smoke.ORIGIN + "/v1/sources"))
    assert budget.count == 9
    for method, url in [
        ("POST", smoke.ORIGIN + "/v1/sources"),
        ("GET", "https://untrusted.invalid/v1/sources"),
        ("GET", smoke.ORIGIN + "/v1/admin"),
    ]:
        with pytest.raises(ValueError):
            smoke.BudgetTransport(
                httpx.MockTransport(lambda r: pytest.fail("network"))
            ).handle_request(httpx.Request(method, url))


def test_safe_cli_output(monkeypatch, capsys, tmp_path, payloads):
    report, _ = exercise(payloads, lambda request, n: httpx.Response(401, json={"detail": KEY}))
    monkeypatch.setattr(smoke, "run", lambda *a, **k: report)
    monkeypatch.setenv("IONOFLUX_API_KEY", KEY)
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "summary"))
    assert smoke.main() == 1
    output = capsys.readouterr()
    text = output.out + output.err + (tmp_path / "summary").read_text()
    assert KEY not in text and "detail" not in text and "x-api-key" not in text.lower()
    assert json.loads(output.out) == report


def test_manual_trusted_workflow_only():
    body = (ROOT / ".github/workflows/sdk-smoke.yml").read_text()
    assert "workflow_dispatch:" in body and "pull_request" not in body
    assert "github.ref == 'refs/heads/main'" in body
    assert "github.repository == 'hongjunna/ionoflux-python'" in body
    assert "ref: ${{ github.sha }}" in body
    assert "name: sdk-smoke" in body and "persist-credentials: false" in body
    assert body.count("secrets.IONOFLUX_API_KEY") == 1
    assert "id-token: write" not in body
    assert "upload-artifact" not in body


def test_invalid_key_closes_allocated_transport():
    class TrackingTransport(httpx.MockTransport):
        closed = False

        def close(self):
            self.closed = True
            super().close()

    transport = TrackingTransport(lambda r: pytest.fail("network"))
    result = smoke.run("invalid key", smoke.ORIGIN, transport=transport, now=NOW)
    assert result["requests"] == 0 and result["result"] == "FAIL"
    assert transport.closed


def test_invalid_json_is_safe_failure(payloads):
    summary, calls = exercise(payloads, lambda r, n: httpx.Response(200, content=b"not-json"))
    assert summary["result"] == "FAIL" and len(calls) == 1 and summary["session_closed"]
    assert summary["checks"][0]["http_status"] == 200
