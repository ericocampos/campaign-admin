from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1"}


def ensure_loopback_bind(host: str) -> None:
    if host not in ALLOWED_HOSTS:
        raise RuntimeError(
            f"refusing to start: app host is '{host}', must be one of {sorted(ALLOWED_HOSTS)}. "
            "This tool has no authentication and must not be exposed to non-loopback addresses."
        )


CSP = (
    "default-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "img-src 'self' data:; "
    "form-action 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = CSP
        return response
