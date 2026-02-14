"""Fix generation and remediation planning."""

from typing import List, Dict, Any
from dataclasses import dataclass
from .detector import Issue


@dataclass
class RemediationStep:
    """Single step in remediation process."""
    order: int
    title: str
    description: str
    command: str
    config_changes: str


@dataclass
class RemediationPlan:
    """Complete remediation plan for an issue."""
    issue: Issue
    steps: List[RemediationStep]
    estimated_time: str  # e.g., "5 minutes"
    risk_level: str  # low, medium, high
    requires_approval: bool


class FixGenerator:
    """Generate fixes for detected issues."""

    # Kubernetes fixes
    K8S_FIXES = {
        "k8s-001": {
            "title": "Add Resource Limits",
            "fix": """
spec:
  containers:
  - name: app
    resources:
      limits:
        cpu: 500m
        memory: 512Mi
      requests:
        cpu: 250m
        memory: 256Mi
""",
        },
        "k8s-004": {
            "title": "Add Liveness Probe",
            "fix": """
spec:
  containers:
  - name: app
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
""",
        },
        "k8s-005": {
            "title": "Add Readiness Probe",
            "fix": """
spec:
  containers:
  - name: app
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 2
""",
        },
        "k8s-003": {
            "title": "Add HorizontalPodAutoscaler",
            "fix": """
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
""",
        },
        "k8s-006": {
            "title": "Add RBAC Configuration",
            "fix": """
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: app-role
subjects:
- kind: ServiceAccount
  name: app-sa
""",
        },
        "k8s-007": {
            "title": "Add NetworkPolicy",
            "fix": """
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: myapp
    ports:
    - protocol: TCP
      port: 8080
""",
        },
    }

    # Terraform fixes
    TF_FIXES = {
        "tf-001": {
            "title": "Define Variables",
            "fix": """
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}
""",
        },
        "tf-003": {
            "title": "Remove Hardcoded Secrets",
            "fix": """
# Use terraform.tfvars instead of hardcoding
# terraform.tfvars example:
# db_password = var("DB_PASSWORD")

resource "aws_db_instance" "main" {
  password = var.db_password  # Use variable
}
""",
        },
        "tf-004": {
            "title": "Add State Locking",
            "fix": """
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
""",
        },
        "tf-005": {
            "title": "Set Provider Region",
            "fix": """
provider "aws" {
  region = var.region
  
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
""",
        },
        "tf-006": {
            "title": "Add Resource Tags",
            "fix": """
resource "aws_instance" "main" {
  # ... other configuration ...
  
  tags = {
    Name        = "${var.project_name}-instance"
    Environment = var.environment
    ManagedBy   = "Terraform"
    CreatedAt   = timestamp()
  }
}
""",
        },
    }

    # GitHub Actions fixes
    GHA_FIXES = {
        "gha-001": {
            "title": "Add Workflow Permissions",
            "fix": """
permissions:
  contents: read
  pull-requests: write
  checks: write
  deployments: write
  packages: read
""",
        },
        "gha-002": {
            "title": "Use GitHub Secrets",
            "fix": """
# Define secrets in GitHub Settings > Secrets and variables > Actions
# Then reference in workflow:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
        run: ./deploy.sh
""",
        },
        "gha-003": {
            "title": "Pin Action Versions",
            "fix": """
steps:
  # Bad: uses: actions/checkout@v4 (unpinned minor)
  # Good: pin specific versions
  
  - uses: actions/checkout@v4.1.1
  - uses: docker/setup-buildx-action@v3.0.0
  - uses: docker/build-push-action@v5.0.0
  # Or use commit SHA for maximum safety:
  - uses: actions/checkout@b4ffde65f46336ab88eb53be0f245ec8763ff594
""",
        },
        "gha-004": {
            "title": "Add Branch Conditions",
            "fix": """
on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run deploy
""",
        },
        "gha-005": {
            "title": "Add Job Timeout",
            "fix": """
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
      - uses: actions/checkout@v4
      - run: npm run build
""",
        },
    }

    def generate_fix(self, issue: Issue) -> RemediationPlan:
        """Generate fix for an issue."""
        # Select fix templates based on issue category
        fixes = self._get_fixes_for_category(issue.category)
        fix_template = fixes.get(issue.id, {})

        # Generate remediation steps
        steps = self._generate_steps(issue, fix_template)

        # Determine risk level and approval requirements
        risk_level = "low" if issue.severity.value == "info" else \
                    "medium" if issue.severity.value == "warning" else "high"
        requires_approval = issue.severity.value != "info"

        return RemediationPlan(
            issue=issue,
            steps=steps,
            estimated_time=self._estimate_time(issue),
            risk_level=risk_level,
            requires_approval=requires_approval,
        )

    def _get_fixes_for_category(self, category: str) -> Dict[str, Any]:
        """Get fix templates for category."""
        if category == "kubernetes":
            return self.K8S_FIXES
        elif category == "terraform":
            return self.TF_FIXES
        elif category == "github":
            return self.GHA_FIXES
        return {}

    def _generate_steps(self, issue: Issue, fix_template: Dict) -> List[RemediationStep]:
        """Generate remediation steps."""
        steps = []

        # Step 1: Understand the issue
        steps.append(RemediationStep(
            order=1,
            title="Understand the Issue",
            description=issue.root_cause,
            command=f"# Review issue: {issue.title}",
            config_changes=f"Issue: {issue.description}\nResource: {issue.resource}"
        ))

        # Step 2: Review suggested fix
        config_fix = fix_template.get("fix", issue.suggested_fix)
        steps.append(RemediationStep(
            order=2,
            title=fix_template.get("title", "Apply Fix"),
            description=f"Apply the following configuration change",
            command="# Update configuration",
            config_changes=config_fix
        ))

        # Step 3: Validate changes
        if issue.category == "kubernetes":
            steps.append(RemediationStep(
                order=3,
                title="Validate Kubernetes YAML",
                description="Ensure YAML syntax is valid",
                command="kubectl apply --dry-run=client -f updated-manifest.yaml",
                config_changes="Run kubectl validation"
            ))
        elif issue.category == "terraform":
            steps.append(RemediationStep(
                order=3,
                title="Validate Terraform",
                description="Check Terraform syntax and plan changes",
                command="terraform validate && terraform plan",
                config_changes="Review Terraform plan output"
            ))

        # Step 4: Apply changes
        if issue.category == "kubernetes":
            steps.append(RemediationStep(
                order=4,
                title="Apply to Cluster",
                description="Deploy updated manifests",
                command="kubectl apply -f updated-manifest.yaml",
                config_changes="Manifests deployed to cluster"
            ))
        elif issue.category == "terraform":
            steps.append(RemediationStep(
                order=4,
                title="Apply Changes",
                description="Apply Terraform changes",
                command="terraform apply -auto-approve",
                config_changes="Infrastructure updated via Terraform"
            ))

        # Step 5: Verify fix
        steps.append(RemediationStep(
            order=5,
            title="Verify Fix",
            description="Confirm the issue is resolved",
            command=self._get_verify_command(issue),
            config_changes="Verification complete"
        ))

        return steps

    def _get_verify_command(self, issue: Issue) -> str:
        """Get verification command for issue type."""
        if "k8s" in issue.id:
            return "kubectl get pods -o wide && kubectl describe pod <pod-name>"
        elif "tf" in issue.id:
            return "terraform show && terraform state list"
        elif "gha" in issue.id:
            return "git log --oneline && gh run list"
        elif "log" in issue.id:
            return "tail -f application.log"
        return "# Verify issue is resolved"

    def _estimate_time(self, issue: Issue) -> str:
        """Estimate time to fix issue."""
        if issue.severity.value == "critical":
            return "5-15 minutes"
        elif issue.severity.value == "warning":
            return "15-30 minutes"
        else:
            return "30-60 minutes"

    def generate_fixed_config(self, issue: Issue, original_config: str) -> str:
        """Generate complete fixed configuration."""
        fixes = self._get_fixes_for_category(issue.category)
        fix_template = fixes.get(issue.id, {})
        config_fix = fix_template.get("fix", "")

        if issue.category == "kubernetes":
            return self._merge_k8s_config(original_config, config_fix)
        elif issue.category == "terraform":
            return original_config + "\n\n# Fixed:\n" + config_fix
        elif issue.category == "github":
            return original_config + "\n# Fixed:\n" + config_fix

        return original_config + "\n" + config_fix

    def _merge_k8s_config(self, original: str, fix: str) -> str:
        """Merge Kubernetes fix into original config."""
        if "resources:" not in original:
            return original.replace("containers:", "containers:") + "\n" + fix
        return original + "\n---\n" + fix
