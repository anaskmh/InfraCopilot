"""GitHub Actions CI/CD workflow generator."""

from .base import BaseGenerator


class GitHubActionsGenerator(BaseGenerator):
    """Generate GitHub Actions workflows."""

    def generate(self, requirements: str) -> str:
        """Generate GitHub Actions workflow from requirements."""
        if not self.validate_input(requirements):
            return "# Error: Invalid requirements"

        requirements_lower = requirements.lower()

        # Detect workflow type
        if any(x in requirements_lower for x in ["test", "unit"]):
            return self._generate_test_workflow()

        if any(x in requirements_lower for x in ["build", "docker", "container"]):
            return self._generate_docker_workflow()

        if any(x in requirements_lower for x in ["deploy", "kubernetes", "k8s"]):
            return self._generate_deploy_workflow()

        if any(x in requirements_lower for x in ["lint", "quality"]):
            return self._generate_lint_workflow()

        # Default: comprehensive workflow
        return self._generate_comprehensive_workflow()

    def _generate_test_workflow(self) -> str:
        """Generate test workflow."""
        return f"""name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Lint with Ruff
      run: ruff check . --config pyproject.toml

    - name: Run tests
      run: pytest --cov=devops_ai --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
"""

    def _generate_docker_workflow(self) -> str:
        """Generate Docker build and push workflow."""
        return f"""name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{{{ secrets.DOCKER_USERNAME }}}}
        password: ${{{{ secrets.DOCKER_PASSWORD }}}}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{{{ secrets.DOCKER_REGISTRY }}}}/{self.project_name}
        tags: |
          type=ref,event=branch
          type=semver,pattern={{{{version}}}}
          type=sha

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: ${{{{ github.event_name != 'pull_request' }}}}
        tags: ${{{{ steps.meta.outputs.tags }}}}
        labels: ${{{{ steps.meta.outputs.labels }}}}
        cache-from: type=gha
        cache-to: type=gha,mode=max
"""

    def _generate_deploy_workflow(self) -> str:
        """Generate deployment workflow."""
        return f"""name: Deploy to Kubernetes

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production

    steps:
    - uses: actions/checkout@v4

    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: '1.28'

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
        aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
        aws-region: us-east-1

    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region us-east-1 --name {self.project_name}-cluster

    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/
        kubectl rollout status deployment/{self.project_name}-deployment -n {self.project_name}

    - name: Verify deployment
      run: |
        kubectl get pods -n {self.project_name}
        kubectl get svc -n {self.project_name}
"""

    def _generate_lint_workflow(self) -> str:
        """Generate linting workflow."""
        return f"""name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install ruff black mypy

    - name: Run Ruff
      run: ruff check . --config pyproject.toml

    - name: Check formatting with Black
      run: black --check devops_ai tests

    - name: Type check with mypy
      run: mypy devops_ai --ignore-missing-imports

    - name: Security check with bandit
      run: |
        pip install bandit
        bandit -r devops_ai -f json -o bandit-report.json
      continue-on-error: true
"""

    def _generate_comprehensive_workflow(self) -> str:
        """Generate comprehensive CI/CD workflow."""
        return f"""name: CI/CD

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{{{ github.repository }}}}

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/pyproject.toml') }}}}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Lint with Ruff
      run: ruff check . --config pyproject.toml

    - name: Format check with Black
      run: black --check devops_ai tests

    - name: Type check
      run: mypy devops_ai --ignore-missing-imports

    - name: Run tests
      run: pytest --cov=devops_ai --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        fail_ci_if_error: true

  build:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{{{ env.REGISTRY }}}}
        username: ${{{{ github.actor }}}}
        password: ${{{{ secrets.GITHUB_TOKEN }}}}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{{{ env.REGISTRY }}}}/${{{{ env.IMAGE_NAME }}}}
        tags: |
          type=ref,event=branch
          type=semver,pattern={{{{version}}}}
          type=sha,prefix={{{{branch}}}}-

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: ${{{{ github.ref == 'refs/heads/main' }}}}
        tags: ${{{{ steps.meta.outputs.tags }}}}
        labels: ${{{{ steps.meta.outputs.labels }}}}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://{self.project_name}.example.com

    steps:
    - uses: actions/checkout@v4

    - name: Deploy notification
      run: echo "Deployment step - configure your deployment here"
"""
