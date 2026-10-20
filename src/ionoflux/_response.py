"""Lossless JSON payloads and safe HTTP metadata; no request/auth objects."""

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")
JSONObject = dict[str, Any]


def _seconds(value: str | None) -> int | None:
    if value is None or len(value) > 20 or not value.isascii() or not value.isdecimal():
        return None
    return int(value)


@dataclass(frozen=True)
class RateLimit:
    limit: int | None = None
    remaining: int | None = None
    reset_seconds: int | None = None
    retry_after: str | None = None

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> "RateLimit":
        return cls(
            _seconds(headers.get("x-ratelimit-limit")),
            _seconds(headers.get("x-ratelimit-remaining")),
            _seconds(headers.get("x-ratelimit-reset")),
            headers.get("retry-after"),
        )


@dataclass(frozen=True)
class APIResponse(Generic[T]):
    """data is unmodified decoded JSON; raw_body preserves the original response bytes.

    Timestamp strings, unknown fields, units, attribution and nulls remain untouched.
    Only quota/content-type headers are retained, never request authentication headers.
    """

    data: T
    raw_body: bytes
    status_code: int
    headers: dict[str, str]
    rate_limit: RateLimit
