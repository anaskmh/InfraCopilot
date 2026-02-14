"""Tests for diagnostics."""

import pytest
from devops_ai.diagnostics import LogAnalyzer, DiagnosticRunner


class TestLogAnalyzer:
    """Test log analysis."""

    def test_analyze_connection_error(self, sample_log):
        """Test connection error detection."""
        analyzer = LogAnalyzer()
        result = analyzer.analyze(sample_log)
        assert result["total_issues"] > 0
        assert result["high"] > 0

    def test_analyze_oom_error(self, sample_log):
        """Test OOM error detection."""
        analyzer = LogAnalyzer()
        result = analyzer.analyze(sample_log)
        assert result["critical"] > 0

    def test_suggest_fixes(self, sample_log):
        """Test fix suggestions."""
        analyzer = LogAnalyzer()
        suggestions = analyzer.suggest_fixes(sample_log)
        assert len(suggestions) > 0
        assert any("fix" in s.lower() for s in suggestions)

    def test_empty_log(self):
        """Test empty log handling."""
        analyzer = LogAnalyzer()
        result = analyzer.analyze("")
        assert result["total_issues"] == 0


class TestDiagnosticRunner:
    """Test diagnostic runner."""

    def test_diagnose_kubernetes(self):
        """Test Kubernetes diagnostics."""
        runner = DiagnosticRunner()
        result = runner.diagnose_kubernetes("default")
        assert "pods_running" in result
        assert "services_ready" in result

    def test_diagnose_docker(self):
        """Test Docker diagnostics."""
        runner = DiagnosticRunner()
        result = runner.diagnose_docker("test-container")
        assert "status" in result

    def test_diagnose_database(self):
        """Test database diagnostics."""
        runner = DiagnosticRunner()
        result = runner.diagnose_database("postgres")
        assert "connection" in result
        assert "performance" in result
