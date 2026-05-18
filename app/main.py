import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.admin_routes import router as admin_router
from app.api_v1 import router as api_v1_router
from app.config import get_settings
from app.db import ensure_schema

# No lifespan DB init — on Vercel a failing lifespan crashes every route including /health.
app = FastAPI(title="Ak-Shumkar licensing portal")
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


@app.get("/health/db")
def health_db():
    try:
        ensure_schema()
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": str(exc)},
        )
