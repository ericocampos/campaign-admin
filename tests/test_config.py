
from app.config import Settings


def test_settings_reads_from_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-123")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("APP_HOST", "127.0.0.1")
    monkeypatch.setenv("APP_PORT", "9999")
    monkeypatch.setenv("ENV", "test")
    s = Settings()
    assert s.secret_key == "test-secret-123"
    assert s.database_url == "sqlite:///:memory:"
    assert s.app_host == "127.0.0.1"
    assert s.app_port == 9999
    assert s.env == "test"


def test_settings_defaults_host_and_port(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "x")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.delenv("APP_HOST", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)
    s = Settings()
    assert s.app_host == "127.0.0.1"
    assert s.app_port == 8001
