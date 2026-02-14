"""Tests for diagram generator."""

import pytest
from devops_ai.diagram import DiagramGenerator


class TestDiagramGenerator:
    """Test diagram generation."""

    def test_generate_microservices_diagram(self):
        """Test microservices diagram."""
        gen = DiagramGenerator()
        result = gen.generate_architecture("microservices")
        assert "graph" in result
        assert "Service" in result

    def test_generate_monolith_diagram(self):
        """Test monolith diagram."""
        gen = DiagramGenerator()
        result = gen.generate_architecture("monolith")
        assert "graph" in result
        assert "Application" in result

    def test_generate_serverless_diagram(self):
        """Test serverless diagram."""
        gen = DiagramGenerator()
        result = gen.generate_architecture("serverless")
        assert "graph" in result
        assert "Function" in result

    def test_generate_hybrid_diagram(self):
        """Test hybrid diagram."""
        gen = DiagramGenerator()
        result = gen.generate_architecture("hybrid")
        assert "graph" in result

    def test_generate_deployment_pipeline(self):
        """Test pipeline diagram."""
        gen = DiagramGenerator()
        result = gen.generate_deployment_pipeline()
        assert "graph" in result
        assert "Production" in result

    def test_generate_k8s_deployment(self):
        """Test K8s diagram."""
        gen = DiagramGenerator()
        result = gen.generate_k8s_deployment()
        assert "graph" in result
        assert "Pod" in result
