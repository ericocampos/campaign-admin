from sqlalchemy import text

from app.db import build_engine, build_session_factory


def test_engine_can_execute_simple_query():
    engine = build_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_session_factory_yields_session():
    engine = build_engine("sqlite:///:memory:")
    factory = build_session_factory(engine)
    with factory() as session:
        assert session.execute(text("SELECT 2")).scalar() == 2
