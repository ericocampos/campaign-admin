def test_health_returns_ok():
    # Health endpoint doesn't need the DB, so build a minimal app directly.
    import os
    os.environ.setdefault("SECRET_KEY", "t")
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    from fastapi.testclient import TestClient
    from app.main import create_app
    app = create_app()
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
