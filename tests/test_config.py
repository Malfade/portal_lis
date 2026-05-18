from licensing.config import normalize_database_url


def test_normalize_postgres_url():
    out = normalize_database_url("postgres://u:p@host:5432/db")
    assert out.startswith("postgresql+psycopg://u:p@host:5432/db")
    assert "sslmode=require" in out
