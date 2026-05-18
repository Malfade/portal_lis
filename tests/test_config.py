from app.config import normalize_database_url


def test_normalize_postgres_url():
    assert normalize_database_url(
        "postgres://u:p@host:5432/db"
    ) == "postgresql+psycopg2://u:p@host:5432/db"
