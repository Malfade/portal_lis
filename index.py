"""Vercel / ASGI entry: re-export FastAPI app (see pyproject.toml tool.vercel.entrypoint)."""
from app.main import app

__all__ = ["app"]
