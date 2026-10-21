import math
import re
from datetime import UTC, datetime, timedelta
from typing import Literal

Interval = Literal["raw", "1m", "5m", "1h", "3h", "1d", "7d", "1mo"]
Metric = Literal[
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
]
Band = Literal["160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m"]
PropagationMode = Literal["ft8", "ft4", "wspr", "cw", "ssb", "am", "rtty", "psk31"]
NoiseEnvironment = Literal["city", "residential", "rural", "quiet"]
Category = Literal["ALERT", "WARNING", "WATCH", "SUMMARY", "CANCEL", "OTHER", "ES_OPENING"]
Dataset = Literal[
    "sfi",
    "ssn",
    "xray",
    "solar_wind",
    "kp",
    "ap",
    "tec",
    "ionosonde",
    "stations",
    "pskreporter",
    "wsprnet",
    "activity",
    "alerts",
    "places",
]
METRIC_SOURCES = {
    "sfi": ("swpc",),
    "ssn": ("swpc", "silso"),
    "kp": ("swpc", "gfz"),
    "ap": ("gfz",),
    "xray_long": ("primary",),
    "xray_short": ("primary",),
    "solar_wind_speed": ("swpc-rtsw",),
    "solar_wind_density": ("swpc-rtsw",),
    "imf_bt": ("swpc-rtsw",),
    "imf_bz": ("swpc-rtsw",),
}
BANDS = ("160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m")
PROPAGATION_MODES = ("ft8", "ft4", "wspr", "cw", "ssb", "am", "rtty", "psk31")
NOISE_ENVIRONMENTS = ("city", "residential", "rural", "quiet")
# Same pattern as the server; checked locally so a malformed value never becomes a path segment.
CALLSIGN = re.compile(r"[A-Za-z0-9][A-Za-z0-9/-]{1,22}[A-Za-z0-9]")
INTERVALS = ("raw", "1m", "5m", "1h", "3h", "1d", "7d", "1mo")
CATEGORIES = ("ALERT", "WARNING", "WATCH", "SUMMARY", "CANCEL", "OTHER", "ES_OPENING")
DATASETS = (
    "sfi",
    "ssn",
    "xray",
    "solar_wind",
    "kp",
    "ap",
    "tec",
    "ionosonde",
    "stations",
    "pskreporter",
    "wsprnet",
    "activity",
    "alerts",
    "places",
)


def utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Use a timezone-aware datetime; naive datetimes are ambiguous")
    return value.astimezone(UTC)


def integer(value: int, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"limit must be an integer between 1 and {maximum}")


def date_range(start: datetime | None, end: datetime | None) -> dict[str, str]:
    a = utc(start) if start is not None else None
    b = utc(end) if end is not None else None
    # If end is omitted the server uses now. Do not invent its exact clock value.
    if a and b and (a >= b or b - a > timedelta(days=3660)):
        raise ValueError("Require start < end and a range of at most 3660 days")
    return {k: v.isoformat() for k, v in (("start", a), ("end", b)) if v is not None}


def choice(name: str, value: object, options: tuple[str, ...]) -> None:
    if value not in options:
        raise ValueError(f"Unsupported {name}; use one of: {', '.join(options)}")


def whole(name: str, value: int, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} must be an integer between {low} and {high}")
    return value


def number(name: str, value: float, low: float, high: float, *, above: bool = False) -> float:
    """Finite real number in [low, high], or (low, high] when above is set."""
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value > high
        or (value <= low if above else value < low)
    ):
        bound = f"greater than {low}" if above else f"at least {low}"
        raise ValueError(f"{name} must be a finite number {bound} and at most {high}")
    return value


def place(name: str, value: str) -> str:
    """Server-resolved place: `lat,lon`, Maidenhead locator or place name (2..200 chars)."""
    if not isinstance(value, str) or not 2 <= len(value) <= 200:
        raise ValueError(f"{name} must be a string of 2 to 200 characters")
    return value
