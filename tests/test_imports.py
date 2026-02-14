"""Test __init__ files."""

from devops_ai import app, __version__
from devops_ai.generators import TerraformGenerator
from devops_ai.diagnostics import LogAnalyzer
from devops_ai.cost import CostOptimizer
from devops_ai.diagram import DiagramGenerator


def test_imports():
    """Test that all imports work correctly."""
    assert app is not None
    assert __version__ == "0.1.0"
    assert TerraformGenerator is not None
    assert LogAnalyzer is not None
    assert CostOptimizer is not None
    assert DiagramGenerator is not None
