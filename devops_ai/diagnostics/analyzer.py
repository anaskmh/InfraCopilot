"""Log analysis and diagnostics module."""

import re
from typing import Dict, List, Tuple

from rich.console import Console

console = Console()


class LogAnalyzer:
    """Analyze logs and provide diagnostics."""

    # Define common error patterns and fixes
    PATTERNS = {
        "connection_refused": {
            "pattern": r"(connection refused|refused|ECONNREFUSED)",
            "severity": "high",
            "fixes": [
                "Ensure the service is running and listening on the correct port",
                "Check firewall rules and network connectivity",
                "Verify DNS resolution for the host",
                "Check if the port is already in use: lsof -i :PORT",
            ],
        },
        "timeout": {
            "pattern": r"(timeout|timed out|ETIMEDOUT)",
            "severity": "high",
            "fixes": [
                "Increase timeout values in configuration",
                "Check network latency and bandwidth",
                "Verify service is responsive",
                "Look for resource exhaustion (CPU, memory)",
            ],
        },
        "out_of_memory": {
            "pattern": r"(out of memory|OOMKilled|OOM|memory limit exceeded)",
            "severity": "critical",
            "fixes": [
                "Increase memory limits in container/pod configuration",
                "Profile application memory usage",
                "Check for memory leaks",
                "Optimize data structures and algorithms",
            ],
        },
        "permission_denied": {
            "pattern": r"(permission denied|EACCES|forbidden|403)",
            "severity": "high",
            "fixes": [
                "Check file permissions: ls -la",
                "Verify user ownership",
                "Ensure proper IAM/RBAC configuration",
                "Check API key and authentication tokens",
            ],
        },
        "not_found": {
            "pattern": r"(not found|404|no such file|cannot find)",
            "severity": "medium",
            "fixes": [
                "Verify file/resource path",
                "Check if dependency is installed",
                "Look for typos in configuration",
                "Ensure all required environment variables are set",
            ],
        },
        "database_error": {
            "pattern": r"(database|sql|query|postgres|mysql|connection pool)",
            "severity": "high",
            "fixes": [
                "Check database connection string",
                "Verify database is running and accessible",
                "Check connection pool settings",
                "Review and optimize slow queries",
            ],
        },
        "dependency_error": {
            "pattern": r"(import error|module not found|cannot import|dependency)",
            "severity": "medium",
            "fixes": [
                "Install missing dependencies: pip install -r requirements.txt",
                "Check Python version compatibility",
                "Verify virtual environment is activated",
                "Check for version conflicts",
            ],
        },
        "deployment_failed": {
            "pattern": r"(deployment failed|failed to deploy|rollback|release failed)",
            "severity": "critical",
            "fixes": [
                "Check pod logs: kubectl logs POD_NAME",
                "Verify resource availability",
                "Check image availability and pull secrets",
                "Review rollback history",
            ],
        },
    }

    def analyze(self, log_content: str) -> Dict:
        """Analyze log content and provide diagnostics."""
        issues = []
        lines = log_content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for error_type, config in self.PATTERNS.items():
                if re.search(config["pattern"], line, re.IGNORECASE):
                    issues.append(
                        {
                            "line": line_num,
                            "type": error_type,
                            "severity": config["severity"],
                            "message": line.strip(),
                            "fixes": config["fixes"],
                        }
                    )

        return {
            "total_issues": len(issues),
            "critical": sum(1 for i in issues if i["severity"] == "critical"),
            "high": sum(1 for i in issues if i["severity"] == "high"),
            "medium": sum(1 for i in issues if i["severity"] == "medium"),
            "issues": issues,
        }

    def suggest_fixes(self, log_content: str) -> List[str]:
        """Generate fix suggestions from logs."""
        analysis = self.analyze(log_content)
        suggestions = []

        for issue in analysis["issues"]:
            suggestions.append(
                f"[{issue['severity'].upper()}] Line {issue['line']}: {issue['type']}\n"
                + f"Message: {issue['message']}\n"
                + "Suggested fixes:\n"
                + "\n".join(f"  - {fix}" for fix in issue["fixes"])
            )

        return suggestions


class DiagnosticRunner:
    """Run diagnostics on infrastructure."""

    def diagnose_kubernetes(self, namespace: str = "default") -> Dict:
        """Diagnose Kubernetes cluster."""
        checks = {
            "pods_running": self._check_pods(namespace),
            "services_ready": self._check_services(namespace),
            "pvc_bound": self._check_pvc(namespace),
            "resource_usage": self._check_resource_usage(namespace),
        }
        return checks

    def diagnose_docker(self, container_name: str) -> Dict:
        """Diagnose Docker container."""
        return {
            "status": "running",
            "resource_usage": "Requires 'docker stats' command",
            "logs": "Available via 'docker logs' command",
            "health": "Check HEALTHCHECK configuration",
        }

    def diagnose_database(self, db_type: str) -> Dict:
        """Diagnose database."""
        checks = {
            "connection": "Test connectivity to database",
            "performance": "Review slow query logs",
            "storage": "Check disk usage and IOPS",
            "replication": "Verify replication status",
        }
        return checks

    def _check_pods(self, namespace: str) -> Dict:
        """Check pod status."""
        return {
            "status": "Check 'kubectl get pods -n NAMESPACE'",
            "restarts": "High restart count indicates issues",
            "pending": "Pods stuck in Pending state need investigation",
        }

    def _check_services(self, namespace: str) -> Dict:
        """Check service status."""
        return {
            "endpoints": "Verify endpoints are assigned",
            "ports": "Check port mappings",
            "dns": "Ensure service discovery works",
        }

    def _check_pvc(self, namespace: str) -> Dict:
        """Check PersistentVolumeClaim status."""
        return {
            "status": "Should be 'Bound'",
            "storage": "Verify storage class exists",
            "usage": "Monitor storage usage",
        }

    def _check_resource_usage(self, namespace: str) -> Dict:
        """Check resource usage."""
        return {
            "cpu": "Monitor CPU requests and limits",
            "memory": "Monitor memory requests and limits",
            "disk": "Monitor disk I/O",
        }
