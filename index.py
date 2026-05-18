"""Vercel ASGI entry (see pyproject.toml)."""
import traceback

try:
    from licensing.main import app  # noqa: F401
except Exception:
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse

    _BOOT_ERROR = traceback.format_exc()
    app = FastAPI(title="portal-lis boot error")

    @app.get("/{full_path:path}")
    def _boot_failed(full_path: str = ""):
        return PlainTextResponse(_BOOT_ERROR, status_code=500)


__all__ = ["app"]
