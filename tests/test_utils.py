"""Tests for utilities."""

import pytest
import json
from pathlib import Path
from devops_ai.utils import (
    load_config,
    save_config,
    parse_natural_language,
    format_output,
    write_file,
    read_file,
)


class TestConfig:
    """Test configuration functions."""

    def test_save_and_load_config(self, temp_project):
        """Test saving and loading config."""
        config = {"project": "test", "version": "1.0"}
        config_path = temp_project / "config.json"

        save_config(config_path, config)
        loaded = load_config(config_path)

        assert loaded["project"] == "test"
        assert loaded["version"] == "1.0"

    def test_load_nonexistent_config(self, temp_project):
        """Test loading nonexistent config."""
        config_path = temp_project / "nonexistent.json"
        result = load_config(config_path)
        assert result == {}


class TestNLP:
    """Test natural language parsing."""

    def test_parse_create_intent(self):
        """Test parsing create intent."""
        result = parse_natural_language("create a vpc with public subnets")
        assert result["intent"] == "create"
        assert "vpc" in result["keywords"]

    def test_parse_deploy_intent(self):
        """Test parsing deploy intent."""
        result = parse_natural_language("deploy to kubernetes cluster")
        assert result["intent"] == "deploy"

    def test_parse_optimize_intent(self):
        """Test parsing optimize intent."""
        result = parse_natural_language("reduce cloud costs")
        assert result["intent"] == "optimize"


class TestFormatting:
    """Test output formatting."""

    def test_format_json(self):
        """Test JSON formatting."""
        data = {"key": "value"}
        result = format_output(data, "json")
        assert json.loads(result)["key"] == "value"

    def test_format_yaml(self):
        """Test YAML formatting."""
        data = {"key": "value"}
        result = format_output(data, "yaml")
        assert "key" in result
        assert "value" in result


class TestFileOperations:
    """Test file operations."""

    def test_write_and_read_file(self, temp_project):
        """Test writing and reading files."""
        file_path = temp_project / "test.txt"
        content = "test content"

        write_file(file_path, content)
        read_content = read_file(file_path)

        assert read_content == content

    def test_write_creates_directories(self, temp_project):
        """Test write creates necessary directories."""
        file_path = temp_project / "subdir" / "nested" / "file.txt"
        content = "test"

        write_file(file_path, content)

        assert file_path.exists()
        assert read_file(file_path) == content
