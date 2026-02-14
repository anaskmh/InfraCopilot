"""Infrastructure issue detection engine."""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


class IssueSeverity(str, Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """Represents a detected infrastructure issue."""
    id: str
    title: str
    description: str
    severity: IssueSeverity
    category: str  # kubernetes, terraform, github, logs
    resource: str  # pod name, resource name, file name
    root_cause: str
    suggested_fix: str
    affected_config: Optional[str] = None


class IssueDetector:
    """Base class for issue detection."""

    def detect(self, config: Dict[str, Any]) -> List[Issue]:
        """Detect issues in configuration."""
        raise NotImplementedError


class KubernetesDetector(IssueDetector):
    """Detect Kubernetes configuration and runtime issues."""

    CRASH_LOOP_INDICATORS = [
        "CrashLoopBackOff",
        "OOMKilled",
        "ImagePullBackOff",
        "CreateContainerConfigError",
    ]

    SECURITY_ISSUES = [
        ("runAsUser: 0", "Container running as root"),
        ("privileged: true", "Privileged container"),
        ("allowPrivilegeEscalation: true", "Privilege escalation allowed"),
        ("capabilities:", "Unnecessary capabilities"),
    ]

    def detect(self, manifests: str) -> List[Issue]:
        """Detect issues in Kubernetes YAML manifests."""
        issues = []

        # Check for missing resource limits
        if "resources:" not in manifests or "limits:" not in manifests:
            issues.append(Issue(
                id="k8s-001",
                title="Missing Resource Limits",
                description="Containers lack CPU/memory limits",
                severity=IssueSeverity.WARNING,
                category="kubernetes",
                resource="deployment",
                root_cause="Uncontrolled resource consumption",
                suggested_fix="Add resources.limits section to all containers",
                affected_config=manifests[:100]
            ))

        # Check for missing requests
        if "requests:" not in manifests:
            issues.append(Issue(
                id="k8s-002",
                title="Missing Resource Requests",
                description="Containers lack resource requests for scheduling",
                severity=IssueSeverity.WARNING,
                category="kubernetes",
                resource="deployment",
                root_cause="Scheduler cannot make informed decisions",
                suggested_fix="Add resources.requests section to all containers"
            ))

        # Check for autoscaling
        if "HorizontalPodAutoscaler" not in manifests and "Deployment" in manifests:
            issues.append(Issue(
                id="k8s-003",
                title="Missing Autoscaling",
                description="Deployments lack HPA for automatic scaling",
                severity=IssueSeverity.INFO,
                category="kubernetes",
                resource="deployment",
                root_cause="Cannot handle traffic spikes",
                suggested_fix="Add HorizontalPodAutoscaler with CPU/memory targets"
            ))

        # Check for security issues
        for pattern, issue_name in self.SECURITY_ISSUES:
            if pattern.split(":")[0] in manifests.lower():
                issues.append(Issue(
                    id=f"k8s-sec-{len(issues)}",
                    title=f"Security: {issue_name}",
                    description=f"Found: {issue_name}",
                    severity=IssueSeverity.CRITICAL if "root" in issue_name.lower() else IssueSeverity.WARNING,
                    category="kubernetes",
                    resource="pod-spec",
                    root_cause=f"{issue_name} exposes security risks",
                    suggested_fix=f"Remove or configure: {pattern}"
                ))

        # Check for missing probes
        if "livenessProbe:" not in manifests:
            issues.append(Issue(
                id="k8s-004",
                title="Missing Liveness Probe",
                description="Pods lack liveness probe for crash detection",
                severity=IssueSeverity.WARNING,
                category="kubernetes",
                resource="container",
                root_cause="Failed containers not detected",
                suggested_fix="Add livenessProbe to detect and restart failed containers"
            ))

        if "readinessProbe:" not in manifests:
            issues.append(Issue(
                id="k8s-005",
                title="Missing Readiness Probe",
                description="Pods lack readiness probe for traffic routing",
                severity=IssueSeverity.WARNING,
                category="kubernetes",
                resource="container",
                root_cause="Traffic sent to not-ready pods",
                suggested_fix="Add readinessProbe to prevent traffic to unready pods"
            ))

        # Check for RBAC
        if "Role" not in manifests and "Deployment" in manifests:
            issues.append(Issue(
                id="k8s-006",
                title="Missing RBAC",
                description="No Role-based access control configured",
                severity=IssueSeverity.WARNING,
                category="kubernetes",
                resource="namespace",
                root_cause="Overly permissive access by default",
                suggested_fix="Define Role and RoleBinding for least privilege access"
            ))

        # Check for NetworkPolicies
        if "NetworkPolicy" not in manifests and "Pod" in manifests:
            issues.append(Issue(
                id="k8s-007",
                title="Missing Network Policies",
                description="No pod-to-pod network segmentation",
                severity=IssueSeverity.INFO,
                category="kubernetes",
                resource="namespace",
                root_cause="No network isolation between pods",
                suggested_fix="Add NetworkPolicy for pod communication control"
            ))

        return issues


class TerraformDetector(IssueDetector):
    """Detect Terraform configuration issues."""

    def detect(self, terraform_code: str) -> List[Issue]:
        """Detect issues in Terraform code."""
        issues = []

        # Check for missing variable definitions
        if "variable" not in terraform_code and "${var." in terraform_code:
            issues.append(Issue(
                id="tf-001",
                title="Missing Variable Definitions",
                description="Variable references without definitions",
                severity=IssueSeverity.CRITICAL,
                category="terraform",
                resource="variables.tf",
                root_cause="Unresolved variable references",
                suggested_fix="Define all variables in variables.tf file"
            ))

        # Check for empty resource definitions
        if re.search(r'resource\s+"\w+"\s+"\w+"\s+\{\s*\}', terraform_code):
            issues.append(Issue(
                id="tf-002",
                title="Empty Resource Definition",
                description="Resource block without configuration",
                severity=IssueSeverity.CRITICAL,
                category="terraform",
                resource="main.tf",
                root_cause="Incomplete resource configuration",
                suggested_fix="Complete all required resource arguments"
            ))

        # Check for hardcoded values
        if re.search(r'(password|api_key|secret)\s*=\s*"[^"]{8,}"', terraform_code):
            issues.append(Issue(
                id="tf-003",
                title="Hardcoded Secrets",
                description="Sensitive values hardcoded in configuration",
                severity=IssueSeverity.CRITICAL,
                category="terraform",
                resource="main.tf",
                root_cause="Secrets exposed in version control",
                suggested_fix="Use terraform.tfvars or environment variables"
            ))

        # Check for missing state locking
        if "terraform" in terraform_code and "dynamodb_table" not in terraform_code:
            issues.append(Issue(
                id="tf-004",
                title="Missing State Locking",
                description="No state locking configured for remote state",
                severity=IssueSeverity.WARNING,
                category="terraform",
                resource="backend.tf",
                root_cause="Concurrent modifications can corrupt state",
                suggested_fix="Configure DynamoDB locking for S3 backend"
            ))

        # Check for missing provider region
        if "provider" in terraform_code and '"region"' not in terraform_code:
            issues.append(Issue(
                id="tf-005",
                title="Missing Provider Region",
                description="AWS provider without region specification",
                severity=IssueSeverity.WARNING,
                category="terraform",
                resource="main.tf",
                root_cause="Ambiguous provider configuration",
                suggested_fix="Explicitly set provider region"
            ))

        # Check for missing tags
        if "tags" not in terraform_code and "resource" in terraform_code:
            issues.append(Issue(
                id="tf-006",
                title="Missing Resource Tags",
                description="Resources lack proper tagging",
                severity=IssueSeverity.INFO,
                category="terraform",
                resource="main.tf",
                root_cause="Resource organization and tracking issues",
                suggested_fix="Add tags to all resources for organization"
            ))

        return issues


class GitHubActionsDetector(IssueDetector):
    """Detect GitHub Actions workflow issues."""

    def detect(self, workflow_yaml: str) -> List[Issue]:
        """Detect issues in GitHub Actions workflows."""
        issues = []

        # Check for missing permissions
        if "permissions:" not in workflow_yaml:
            issues.append(Issue(
                id="gha-001",
                title="Missing Workflow Permissions",
                description="Workflow jobs lack explicit permissions",
                severity=IssueSeverity.WARNING,
                category="github",
                resource=".github/workflows",
                root_cause="Default excessive permissions",
                suggested_fix="Add permissions block with minimal required access"
            ))

        # Check for hardcoded secrets
        if re.search(r'(TOKEN|SECRET|PASSWORD|KEY)\s*[:=]\s*[\'"][a-zA-Z0-9]{20,}[\'"]', workflow_yaml):
            issues.append(Issue(
                id="gha-002",
                title="Hardcoded Secrets in Workflow",
                description="Secrets hardcoded in workflow file",
                severity=IssueSeverity.CRITICAL,
                category="github",
                resource="workflow.yml",
                root_cause="Secrets exposed in repository",
                suggested_fix="Use GitHub secrets instead of hardcoded values"
            ))

        # Check for missing dependency versions
        if "uses:" in workflow_yaml and "@" not in workflow_yaml:
            issues.append(Issue(
                id="gha-003",
                title="Unpinned Action Versions",
                description="Actions without specific version pins",
                severity=IssueSeverity.WARNING,
                category="github",
                resource="workflow.yml",
                root_cause="Dependency version changes could break builds",
                suggested_fix="Pin action versions with specific tags/commits"
            ))

        # Check for missing branch protection
        if "if:" not in workflow_yaml and "push" in workflow_yaml:
            issues.append(Issue(
                id="gha-004",
                title="No Branch Protection Conditions",
                description="Workflow runs on all branches without filtering",
                severity=IssueSeverity.INFO,
                category="github",
                resource="workflow.yml",
                root_cause="Workflow runs unnecessarily on all branches",
                suggested_fix="Add branch conditions: if: github.ref == 'refs/heads/main'"
            ))

        # Check for timeout issues
        if "timeout-minutes:" not in workflow_yaml:
            issues.append(Issue(
                id="gha-005",
                title="Missing Job Timeout",
                description="Jobs lack timeout configuration",
                severity=IssueSeverity.INFO,
                category="github",
                resource="workflow.yml",
                root_cause="Jobs can run indefinitely",
                suggested_fix="Add timeout-minutes to prevent stuck jobs"
            ))

        return issues


class LogAnalyzer(IssueDetector):
    """Analyze logs for error patterns and issues."""

    ERROR_PATTERNS = {
        "out of memory": ("oom", "Memory exhaustion detected", IssueSeverity.CRITICAL),
        "connection refused": ("conn_refused", "Service connection error", IssueSeverity.CRITICAL),
        "timeout": ("timeout", "Operation timeout detected", IssueSeverity.WARNING),
        "permission denied": ("perm_denied", "Permission/authentication error", IssueSeverity.WARNING),
        "not found": ("not_found", "Resource not found", IssueSeverity.WARNING),
        "pod crash": ("pod_crash", "Pod termination detected", IssueSeverity.CRITICAL),
        "image pull": ("img_pull", "Container image pull failure", IssueSeverity.WARNING),
        "disk full": ("disk_full", "Storage exhaustion detected", IssueSeverity.CRITICAL),
    }

    def detect(self, logs: str) -> List[Issue]:
        """Analyze logs and detect issues."""
        issues = []
        logs_lower = logs.lower()

        for pattern, (issue_id, title, severity) in self.ERROR_PATTERNS.items():
            if pattern in logs_lower:
                count = len(re.findall(pattern, logs_lower))
                issues.append(Issue(
                    id=f"log-{issue_id}",
                    title=title,
                    description=f"Found {count} occurrence(s) of '{pattern}'",
                    severity=severity,
                    category="logs",
                    resource="application.log",
                    root_cause=f"Error pattern: {pattern}",
                    suggested_fix=f"Investigate: {pattern} errors in logs"
                ))

        # Check for repeated errors
        error_count = len(re.findall(r"error|Error|ERROR", logs))
        if error_count > 10:
            issues.append(Issue(
                id="log-high-errors",
                title="High Error Rate",
                description=f"Found {error_count} errors in logs",
                severity=IssueSeverity.WARNING,
                category="logs",
                resource="application.log",
                root_cause="Application generating many errors",
                suggested_fix="Review error logs and fix underlying issues"
            ))

        return issues
