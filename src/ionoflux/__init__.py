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
from ._validation import (
    Band,
    Category,
    Dataset,
    Interval,
    Metric,
    NoiseEnvironment,
    PropagationMode,
)

__version__ = VERSION
__all__ = [
    "Client",
    "APIResponse",
    "RateLimit",
    "Category",
    "Dataset",
    "Interval",
    "Metric",
    "Band",
    "PropagationMode",
    "NoiseEnvironment",
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
