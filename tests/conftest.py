"""Shared test setup.

Point the app at a throwaway SQLite file *before* importing it, so tests
never write to your real development database.
"""

import os
import tempfile

# Must run before `app` is imported (database.py reads this at import time).
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
