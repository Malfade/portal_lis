import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.engine.url import make_url
from starlette.middleware.sessions import SessionMiddleware

from app.admin_routes import router as admin_router
from app.api_v1 import router as api_v1_router
from app.config import get_settings
from app.db import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    u = make_url(get_settings().database_url)
    if u.drivername == "sqlite" and u.database and u.database != ":memory:":
        Path(u.database).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Ak-Shumkar licensing portal", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().session_secret,
    same_site="lax",
    https_only=bool(os.environ.get("VERCEL")),
)
app.include_router(api_v1_router)
app.include_router(admin_router, prefix="/admin")


@app.get("/")
def root():
    return RedirectResponse("/admin/login", status_code=302)


@app.get("/health")
def health():
    return {"status": "ok"}
