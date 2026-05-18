import os


def normalize_database_url(url: str) -> str:
    """Convert Vercel/Neon postgres:// URLs for SQLAlchemy + psycopg2."""
    url = url.strip()
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://") :]
    elif url.startswith("postgresql://") and "+psycopg2" not in url.split("://", 1)[0]:
        url = "postgresql+psycopg2://" + url[len("postgresql://") :]

    if url.startswith("postgresql") and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


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
            return normalize_database_url(explicit)

        for key in (
            "POSTGRES_URL",
            "DATABASE_URL",
            "PRISMA_DATABASE_URL",
            "POSTGRES_PRISMA_URL",
        ):
            raw = os.environ.get(key, "").strip()
            if raw:
                return normalize_database_url(raw)

        if os.environ.get("VERCEL"):
            return "sqlite:////tmp/licensing.db"
        return "sqlite:///./data/licensing.db"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
