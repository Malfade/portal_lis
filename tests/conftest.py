import os
import tempfile

import pytest

_fd, _TEST_DB_PATH = tempfile.mkstemp(suffix="-licensing-test.db")
os.close(_fd)
os.environ["LICENSING_DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ["LICENSING_ADMIN_PASSWORD"] = "test-admin-password"
os.environ["LICENSING_SESSION_SECRET"] = "unit-test-secret-key-32bytes-min!!"
os.environ["LICENSING_RATE_LIMIT_PER_MINUTE"] = "10000"

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app

Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def pytest_sessionfinish(session, exitstatus):
    try:
        os.unlink(_TEST_DB_PATH)
    except OSError:
        pass
