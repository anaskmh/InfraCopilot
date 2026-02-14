"""Main healing orchestration engine."""

from typing import List, Dict, Any, Optional
from .detector import (
    Issue,
    IssueSeverity,
    KubernetesDetector,
    TerraformDetector,
    GitHubActionsDetector,
    LogAnalyzer,
)
from .fixer import FixGenerator, RemediationPlan


class HealingRunner:
    """Orchestrates infrastructure healing."""

    def __init__(self):
        """Initialize healing runner."""
        self.k8s_detector = KubernetesDetector()
        self.tf_detector = TerraformDetector()
        self.gha_detector = GitHubActionsDetector()
        self.log_analyzer = LogAnalyzer()
        self.fix_generator = FixGenerator()

    def scan_kubernetes(self, manifests: str, namespace: Optional[str] = None) -> List[Issue]:
        """Scan Kubernetes manifests for issues."""
        return self.k8s_detector.detect(manifests)

    def scan_terraform(self, terraform_code: str) -> List[Issue]:
        """Scan Terraform code for issues."""
        return self.tf_detector.detect(terraform_code)

    def scan_github_actions(self, workflow_yaml: str) -> List[Issue]:
        """Scan GitHub Actions workflows for issues."""
        return self.gha_detector.detect(workflow_yaml)

    def analyze_logs(self, logs: str) -> List[Issue]:
        """Analyze application logs for issues."""
        return self.log_analyzer.detect(logs)

    def scan_all(self, config: Dict[str, Any]) -> List[Issue]:
        """Scan all available configurations."""
        all_issues = []

        if "kubernetes" in config:
            all_issues.extend(self.scan_kubernetes(config["kubernetes"]))

        if "terraform" in config:
            all_issues.extend(self.scan_terraform(config["terraform"]))

        if "github_actions" in config:
            all_issues.extend(self.scan_github_actions(config["github_actions"]))

        if "logs" in config:
            all_issues.extend(self.analyze_logs(config["logs"]))

        return sorted(all_issues, key=lambda x: self._severity_order(x.severity))

    def get_remediation_plans(self, issues: List[Issue]) -> List[RemediationPlan]:
        """Generate remediation plans for issues."""
        plans = []
        for issue in issues:
            plan = self.fix_generator.generate_fix(issue)
            plans.append(plan)
        return plans

    def filter_by_severity(self, issues: List[Issue], severity: IssueSeverity) -> List[Issue]:
        """Filter issues by severity."""
        return [i for i in issues if i.severity == severity]

    def get_summary(self, issues: List[Issue]) -> Dict[str, Any]:
        """Get summary of detected issues."""
        critical = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
        warnings = len([i for i in issues if i.severity == IssueSeverity.WARNING])
        info = len([i for i in issues if i.severity == IssueSeverity.INFO])

        categories = {}
        for issue in issues:
            if issue.category not in categories:
                categories[issue.category] = 0
            categories[issue.category] += 1

        return {
            "total_issues": len(issues),
            "critical": critical,
            "warnings": warnings,
            "info": info,
            "by_category": categories,
            "issues": issues,
        }

    @staticmethod
    def _severity_order(severity: IssueSeverity) -> int:
        """Get sort order for severity."""
        order = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.WARNING: 1,
            IssueSeverity.INFO: 2,
        }
        return order.get(severity, 99)
