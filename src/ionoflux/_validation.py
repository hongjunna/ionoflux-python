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
