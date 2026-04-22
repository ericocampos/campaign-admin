import pytest

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
