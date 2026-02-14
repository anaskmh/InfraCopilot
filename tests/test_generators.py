"""Tests for generators."""

import pytest
from devops_ai.generators import (
    TerraformGenerator,
    KubernetesGenerator,
    GitHubActionsGenerator,
    DockerfileGenerator,
)


class TestTerraformGenerator:
    """Test Terraform generator."""

    def test_generate_vpc(self):
        """Test VPC generation."""
        gen = TerraformGenerator("test-project")
        result = gen.generate("create vpc with network")
        assert "aws_vpc" in result
        assert "test-project" in result

    def test_generate_rds(self):
        """Test RDS generation."""
        gen = TerraformGenerator("test-project")
        result = gen.generate("create postgres database")
        assert "aws_db_instance" in result
        assert "postgres" in result.lower()

    def test_generate_eks(self):
        """Test EKS generation."""
        gen = TerraformGenerator("test-project")
        result = gen.generate("create kubernetes cluster")
        assert "aws_eks_cluster" in result


class TestKubernetesGenerator:
    """Test Kubernetes generator."""

    def test_generate_deployment(self):
        """Test deployment generation."""
        gen = KubernetesGenerator("test-app")
        result = gen.generate("deploy application")
        assert "kind: Deployment" in result
        assert "test-app" in result

    def test_generate_namespace(self):
        """Test namespace generation."""
        gen = KubernetesGenerator("test-app")
        result = gen.generate("create namespace")
        assert "kind: Namespace" in result

    def test_generate_hpa(self):
        """Test HPA generation."""
        gen = KubernetesGenerator("test-app")
        result = gen.generate("autoscale deployment")
        assert "HorizontalPodAutoscaler" in result


class TestGitHubActionsGenerator:
    """Test GitHub Actions generator."""

    def test_generate_test_workflow(self):
        """Test workflow generation."""
        gen = GitHubActionsGenerator("test-project")
        result = gen.generate("run tests")
        assert "pytest" in result or "test" in result.lower()

    def test_generate_docker_workflow(self):
        """Test Docker workflow generation."""
        gen = GitHubActionsGenerator("test-project")
        result = gen.generate("build docker image")
        assert "docker" in result.lower()


class TestDockerfileGenerator:
    """Test Dockerfile generator."""

    def test_generate_python_dockerfile(self):
        """Test Python Dockerfile generation."""
        gen = DockerfileGenerator("test-app")
        result = gen.generate("python app")
        assert "python" in result.lower()
        assert "FROM" in result

    def test_generate_docker_compose(self):
        """Test docker-compose generation."""
        gen = DockerfileGenerator("test-app")
        result = gen.generate_dockercompose("postgres redis")
        assert "version" in result
        assert "services" in result
