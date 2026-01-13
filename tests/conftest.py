"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "ai-engine"))

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path for testing."""
    db_path = tmp_path / "test_aegisx.db"
    os.environ["DATABASE_PATH"] = str(db_path)
    return db_path
