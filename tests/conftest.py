import os

import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_AGENT"] = "1"
os.environ["DATABASE_URL"] = "postgresql://fiscal:fiscal_demo_2026@localhost:5544/fiscal_copilot"

from app.main import app


@pytest.fixture(scope="module")
def db_client():
    """TestClient with lifespan triggered (DB pool initialized)."""
    with TestClient(app) as c:
        yield c
