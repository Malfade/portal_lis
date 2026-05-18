import os


class Settings:
    def __init__(self):
        self.database_url = self._database_url()
        self.admin_password = os.environ.get("LICENSING_ADMIN_PASSWORD", "")
        self.session_secret = os.environ.get(
            "LICENSING_SESSION_SECRET",
            "change-me-in-production-use-openssl-rand-hex-32",
        )
        self.rate_limit_per_minute = int(
            os.environ.get("LICENSING_RATE_LIMIT_PER_MINUTE", "120")
        )
        self.on_vercel = bool(os.environ.get("VERCEL"))

    @staticmethod
    def _database_url() -> str:
        explicit = os.environ.get("LICENSING_DATABASE_URL", "").strip()
        if explicit:
            return explicit
        if os.environ.get("VERCEL"):
            # Ephemeral; use Neon/Vercel Postgres in production (set LICENSING_DATABASE_URL).
            return "sqlite:////tmp/licensing.db"
        return "sqlite:///./data/licensing.db"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
