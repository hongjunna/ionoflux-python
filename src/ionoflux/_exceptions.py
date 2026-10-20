"""Stable exception hierarchy without HTTP request objects."""

from ._response import RateLimit


class IonoFluxError(Exception):
    """Base SDK error."""


class ConfigurationError(IonoFluxError, ValueError):
    """Invalid client configuration or missing API key."""


class TransportError(IonoFluxError):
    """A request failed after the bounded retry policy."""


class ResponseError(IonoFluxError):
    """A successful HTTP response did not contain the expected JSON container."""


class APIError(IonoFluxError):
    def __init__(self, status_code: int, detail: str, rate_limit: RateLimit) -> None:
        self.status_code = status_code
        self.detail = detail
        self.rate_limit = rate_limit
        self.retry_after = rate_limit.retry_after
        super().__init__(f"IonoFlux API returned HTTP {status_code}: {detail}")


class AuthenticationError(APIError):
    """HTTP 401: missing/invalid key."""


class PermissionDeniedError(APIError):
    """HTTP 403: revoked, expired, incompatible key or origin restriction."""


class NotFoundError(APIError):
    """HTTP 404."""


class ValidationError(APIError):
    """HTTP 422; detail retains the server's validation explanation as text."""


class RateLimitError(APIError):
    """HTTP 429. Never automatically retried or slept on."""


class ServerError(APIError):
    """HTTP 5xx."""


class RedirectError(APIError):
    """HTTP 3xx. Redirects are never followed."""
