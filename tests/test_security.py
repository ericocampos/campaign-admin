import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.security import ensure_loopback_bind


def test_bind_guard_allows_loopback():
    ensure_loopback_bind("127.0.0.1")
    ensure_loopback_bind("localhost")
    ensure_loopback_bind("::1")


def test_bind_guard_rejects_public():
    with pytest.raises(RuntimeError, match="refusing to start"):
        ensure_loopback_bind("0.0.0.0")
    with pytest.raises(RuntimeError, match="refusing to start"):
        ensure_loopback_bind("192.168.1.10")


def test_security_headers_applied():
    from app.security import SecurityHeadersMiddleware

    async def ok(_):
        return PlainTextResponse("ok")

    app = Starlette(routes=[Route("/", ok)])
    app.add_middleware(SecurityHeadersMiddleware)
    client = TestClient(app)
    r = client.get("/")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "no-referrer"
    assert "default-src 'self'" in r.headers["content-security-policy"]
