"""Vercel / ASGI entry: re-export FastAPI app (see pyproject.toml tool.vercel.entrypoint)."""
from licensing.main import app

__all__ = ["app"]
