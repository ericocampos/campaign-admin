import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import db as db_module
from app.db import build_session_factory

try:
    from app.models import Base  # populated in Phase 2
except ImportError:
    Base = None


@pytest.fixture
def engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def session_factory(engine):
    assert Base is not None, "app.models.Base required; implement Phase 2 first"
    Base.metadata.create_all(engine)
    return build_session_factory(engine)


@pytest.fixture
def session(session_factory) -> Session:
    with session_factory() as s:
        yield s


@pytest.fixture
def app_with_db(engine, session_factory, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("APP_HOST", "127.0.0.1")
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("CSRF_ENABLED", "false")
    from app.main import create_app

    db_module._engine = engine
    db_module._session_factory = session_factory
    app = create_app()
    yield app
    db_module._engine = None
    db_module._session_factory = None


@pytest.fixture
def client(app_with_db) -> TestClient:
    return TestClient(app_with_db)
