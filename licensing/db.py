import threading
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from licensing.config import get_settings

_schema_lock = threading.Lock()
_schema_ready = False
_engine = None
_SessionLocal = None


class Base(DeclarativeBase):
    pass


def _build_engine():
    url = get_settings().database_url
    connect_args: dict = {}
    engine_kwargs: dict = {"pool_pre_ping": True}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    else:
        engine_kwargs["poolclass"] = NullPool

    return create_engine(url, connect_args=connect_args, **engine_kwargs)


def get_engine():
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def ensure_schema() -> None:
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        u = make_url(get_settings().database_url)
        if u.drivername == "sqlite" and u.database and u.database != ":memory:":
            Path(u.database).parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=get_engine())
        _schema_ready = True


def get_db() -> Generator:
    ensure_schema()
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
