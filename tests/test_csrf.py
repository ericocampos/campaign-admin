import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def csrf_client(engine, session_factory, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("APP_HOST", "127.0.0.1")
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("CSRF_ENABLED", "true")
    import app.db as db_module
    db_module._engine = engine
    db_module._session_factory = session_factory
    from app.main import create_app
    app = create_app()
    client = TestClient(app)
    yield client
    db_module._engine = None
    db_module._session_factory = None


def test_csrf_blocks_post_without_token(csrf_client):
    r = csrf_client.post("/markdown/preview", data={"source": "x"})
    assert r.status_code in (401, 403)


def test_csrf_allows_post_with_token(csrf_client):
    # Any non-exempt request primes the CSRF cookie
    csrf_client.get("/_csrf_priming_")
    token = csrf_client.cookies.get("csrftoken")
    assert token, "CSRF cookie should have been set"
    r = csrf_client.post(
        "/markdown/preview",
        data={"source": "hi"},
        headers={"x-csrftoken": token},
    )
    assert r.status_code == 200
    assert "hi" in r.text


def test_base_template_embeds_csrf_in_hx_headers():
    from pathlib import Path
    base = Path("app/templates/base.html").read_text()
    assert "hx-headers" in base
    assert "x-csrftoken" in base
