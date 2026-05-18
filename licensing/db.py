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


class Base(DeclarativeBase):
    pass


def _engine():
    url = get_settings().database_url
    connect_args: dict = {}
    engine_kwargs: dict = {"pool_pre_ping": True}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    else:
        # Serverless: do not keep pooled connections between invocations.
        engine_kwargs["poolclass"] = NullPool

    return create_engine(url, connect_args=connect_args, **engine_kwargs)


engine = _engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
        Base.metadata.create_all(bind=engine)
        _schema_ready = True


def get_db() -> Generator:
    ensure_schema()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
