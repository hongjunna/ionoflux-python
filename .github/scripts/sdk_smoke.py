"""Opt-in live acceptance. Importing this module never performs network I/O.

Print only fixed check names, HTTP status and pass/fail; never print payloads,
exception messages, requests, headers, environment values or user-supplied URLs.
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from jsonschema import Draft202012Validator, FormatChecker

from ionoflux import Client

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = "https://ionoflux.runvia.app"
MAX_REQUESTS = 9
PATHS = (
    "/space-weather/current",
    "/solar/flux",
    "/geomagnetic/kp",
    "/statistics/sfi",
    "/alerts",
    "/alerts/scales",
    "/sources",
    "/data-status",
    "/data-status/sfi",
)
NAMES = (
    "current",
    "sfi",
    "kp",
    "statistics_sfi",
    "alerts",
    "scales",
    "sources",
    "data_status",
    "sfi_status_detail",
)
TIME_FIELDS = {
    "time",
    "generated_at",
    "start",
    "end",
    "last_updated",
    "issue_time",
    "fetched_at",
    "first_time",
    "last_time",
    "last_success_at",
    "tec_map_time",
}


class InvalidResponse(Exception):
    """Deliberately contains no server data."""


def base_url(value: str) -> str:
    # Environment currently holds the service origin, while Client needs /v1.
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "ionoflux.runvia.app"
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/", "/v1", "/v1/")
    ):
        raise ValueError("Only the approved HTTPS origin or its /v1 root is allowed")
    return ORIGIN + "/v1"


def utc_timestamp(value: object) -> bool:
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() == timedelta(0)
    except ValueError:
        return False


FORMATS = FormatChecker()
FORMATS.checks("date-time")(utc_timestamp)


class BudgetTransport(httpx.BaseTransport):
    def __init__(self, inner: httpx.BaseTransport):
        self.inner = inner
        self.count = 0
        self.last_status: int | None = None
        self.closed = False

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if (
            request.method != "GET"
            or str(request.url.copy_with(path="/", query=None)) != ORIGIN + "/"
            or request.url.path not in {"/v1" + p for p in PATHS}
            or self.count >= MAX_REQUESTS
        ):
            raise ValueError("Request outside the fixed read-only budget")
        self.count += 1
        self.last_status = None
        response = self.inner.handle_request(request)
        self.last_status = response.status_code
        return response

    def close(self) -> None:
        self.closed = True
        self.inner.close()


def check_times(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in TIME_FIELDS and item is not None and not utc_timestamp(item):
                raise InvalidResponse()
            check_times(item)
    elif isinstance(value, list):
        for item in value:
            check_times(item)
    elif isinstance(value, float) and not math.isfinite(value):
        raise InvalidResponse()


def validate(name: str, path: str, response: object, contract: dict) -> None:
    data = response.data
    if response.status_code != 200 or json.loads(response.raw_body) != data:
        raise InvalidResponse()
    route = (
        "/v1/statistics/{metric}"
        if name == "statistics_sfi"
        else ("/v1/data-status/{dataset}" if name == "sfi_status_detail" else "/v1" + path)
    )
    schema = contract["paths"][route]["get"]["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    validator = Draft202012Validator(
        {"components": contract["components"], **schema}, format_checker=FORMATS
    )
    if not validator.is_valid(data):
        raise InvalidResponse()
    check_times(data)
    if name in {"sfi", "kp", "statistics_sfi"}:
        metric, unit = ("kp", "index") if name == "kp" else ("sfi", "sfu")
        if data["metric"] != metric or data["unit"] != unit or data["source"] != "swpc":
            raise InvalidResponse()
        if name != "statistics_sfi" and data["attribution"]["key"] != data["source"]:
            raise InvalidResponse()
    if name == "scales":
        if not {"fetched_at", "attribution", "scales"} <= data.keys():
            raise InvalidResponse()
        if not isinstance(data["scales"], dict) or not isinstance(data["attribution"], dict):
            raise InvalidResponse()
        if not utc_timestamp(data["fetched_at"]):
            raise InvalidResponse()
        if not Draft202012Validator(contract["components"]["schemas"]["Attribution"]).is_valid(
            data["attribution"]
        ):
            raise InvalidResponse()
    if name == "sources":
        if not isinstance(data.get("sources"), dict) or not isinstance(
            data.get("collectors"), list
        ):
            raise InvalidResponse()
        for source in data["sources"].values():
            if not isinstance(source, dict) or not {"name", "url", "license"} <= source.keys():
                raise InvalidResponse()
    if name == "data_status":
        if (
            not utc_timestamp(data.get("generated_at"))
            or not isinstance(data.get("datasets"), list)
            or not isinstance(data.get("spot_archive"), dict)
        ):
            raise InvalidResponse()
    if name == "sfi_status_detail":
        if data.get("dataset") != "sfi" or not isinstance(data.get("rows"), list):
            raise InvalidResponse()


def run(
    key: str, url: str, *, transport: httpx.BaseTransport | None = None, now: datetime | None = None
) -> dict:
    """Run the fixed sequence; tests inject MockTransport, never real credentials."""
    logging.disable(logging.CRITICAL)
    results: list[dict] = []
    budget: BudgetTransport | None = None
    client: Client | None = None
    try:
        if not key:
            raise ValueError("Missing key")
        root = base_url(url)
        contract = json.loads((ROOT / "docs/openapi-v0.1.json").read_text())
        end = now if now is not None else datetime.now(UTC)
        if end.tzinfo is None or end.utcoffset() != timedelta(0):
            raise ValueError("UTC required")
        start = end - timedelta(days=7)
        budget = BudgetTransport(
            transport if transport is not None else httpx.HTTPTransport(retries=0, trust_env=False)
        )
        with Client(
            api_key=key, base_url=root, timeout=10.0, max_retries=0, transport=budget
        ) as client:
            calls = (
                client.space_weather.current,
                lambda: client.solar.flux(start=start, end=end, interval="1d", limit=3),
                lambda: client.geomagnetic.kp(
                    start=start, end=end, source="swpc", limit=3, include_forecast=False
                ),
                lambda: client.statistics("sfi", start=start, end=end, source="swpc"),
                lambda: client.alerts.list(since=end - timedelta(days=1), limit=3),
                client.alerts.scales,
                client.sources,
                client.data.status,
                lambda: client.data.status("sfi"),
            )
            for name, path, call in zip(NAMES, PATHS, calls, strict=True):
                try:
                    validate(name, path, call(), contract)
                except Exception:
                    results.append(
                        {"check": name, "http_status": budget.last_status, "result": "FAIL"}
                    )
                    break  # Every failure stops; in particular 401/403/429 never repeats.
                results.append({"check": name, "http_status": budget.last_status, "result": "PASS"})
    except Exception:
        results.append({"check": "configuration", "http_status": None, "result": "FAIL"})
    finally:
        # Client construction can reject a key before taking transport ownership.
        if budget is not None and not budget.closed:
            budget.close()
    closed = bool(client is not None and client.is_closed and budget is not None and budget.closed)
    passed = len(results) == MAX_REQUESTS and all(r["result"] == "PASS" for r in results) and closed
    return {
        "result": "PASS" if passed else "FAIL",
        "requests": budget.count if budget else 0,
        "session_closed": closed,
        "checks": results,
    }


def main() -> int:
    # No exception values, raw response, headers or environment values are emitted.
    summary = run(os.environ.get("IONOFLUX_API_KEY", ""), os.environ.get("IONOFLUX_BASE_URL", ""))
    safe = json.dumps(summary, sort_keys=True)
    print(safe)
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        Path(path).write_text("SDK live API smoke (manual only)\n\n```json\n" + safe + "\n```\n")
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
