"""Local / Docker entry; Vercel uses api/index.py."""
from licensing.main import app

__all__ = ["app"]
