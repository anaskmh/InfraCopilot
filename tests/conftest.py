"""Test configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project directory."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def sample_log():
    """Sample log file for testing."""
    return """
2024-01-10 10:30:45 ERROR Connection refused to database server
2024-01-10 10:30:46 ERROR ECONNREFUSED at port 5432
2024-01-10 10:30:47 WARN Timeout connecting to Redis
2024-01-10 10:30:48 ERROR OOMKilled: out of memory
2024-01-10 10:30:49 ERROR permission denied: /var/data
"""
