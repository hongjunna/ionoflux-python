"""Official IonoFlux Python SDK."""

from ._client import VERSION, Client
from ._exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    IonoFluxError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    RedirectError,
    ResponseError,
    ServerError,
    TransportError,
    ValidationError,
)
from ._response import APIResponse, RateLimit
from ._validation import Category, Dataset, Interval, Metric

__version__ = VERSION
__all__ = [
    "Client",
    "APIResponse",
    "RateLimit",
    "Category",
    "Dataset",
    "Interval",
    "Metric",
    "IonoFluxError",
    "APIError",
    "AuthenticationError",
    "ConfigurationError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "RedirectError",
    "ResponseError",
    "ServerError",
    "TransportError",
    "ValidationError",
]
