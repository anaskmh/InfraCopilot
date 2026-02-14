"""Tests for cost optimizer."""

import pytest
from devops_ai.cost import CostOptimizer


class TestCostOptimizer:
    """Test cost optimization."""

    def test_analyze_infrastructure(self):
        """Test infrastructure analysis."""
        optimizer = CostOptimizer()
        result = optimizer.analyze_infrastructure({})
        assert result["total_recommendations"] > 0
        assert "recommendations" in result

    def test_high_priority_recommendations(self):
        """Test high-priority detection."""
        optimizer = CostOptimizer()
        result = optimizer.analyze_infrastructure({})
        assert result["high_priority"] > 0

    def test_estimate_savings(self):
        """Test savings estimation."""
        optimizer = CostOptimizer()
        recommendations = optimizer.analyze_infrastructure({})["recommendations"]
        savings = optimizer.estimate_monthly_savings(recommendations)
        assert savings > 0

    def test_generate_report(self):
        """Test report generation."""
        optimizer = CostOptimizer()
        report = optimizer.generate_cost_report({})
        assert "Cost Optimization Report" in report
        assert "Summary" in report
        assert "Recommendations" in report
