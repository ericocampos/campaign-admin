from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def init_db(database_url: str) -> None:
    global _engine, _session_factory
    _engine = build_engine(database_url)
    _session_factory = build_session_factory(_engine)


def get_db() -> Iterator[Session]:
    assert _session_factory is not None, "init_db() must be called before get_db()"
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
