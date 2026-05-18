import os
from functools import lru_cache


@lru_cache
def get_settings():
    return Settings()


class Settings:
    def __init__(self):
        self.database_url = os.environ.get(
            "LICENSING_DATABASE_URL",
            "sqlite:///./data/licensing.db",
        )
        self.admin_password = os.environ.get("LICENSING_ADMIN_PASSWORD", "")
        self.session_secret = os.environ.get(
            "LICENSING_SESSION_SECRET",
            "change-me-in-production-use-openssl-rand-hex-32",
        )
        self.rate_limit_per_minute = int(
            os.environ.get("LICENSING_RATE_LIMIT_PER_MINUTE", "120")
        )
