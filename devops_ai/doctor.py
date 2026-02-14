"""System diagnostics and tool checker."""

import subprocess
from typing import Optional

from devops_ai.ui import (
    check_command_installed,
    get_command_version,
    create_status_table,
    print_success,
    print_warning,
    print_section,
    console,
)


class DoctorRunner:
    """Check system dependencies and tool installation."""

    REQUIRED_TOOLS = [
        ("terraform", "--version", "Infrastructure as Code"),
        ("kubectl", "version --client", "Kubernetes CLI"),
        ("docker", "--version", "Container runtime"),
        ("git", "--version", "Version control"),
        ("python", "--version", "Python runtime"),
    ]

    OPTIONAL_TOOLS = [
        ("aws-cli", "--version", "AWS CLI"),
        ("gcloud", "--version", "Google Cloud CLI"),
        ("az", "--version", "Azure CLI"),
        ("helm", "version", "Kubernetes package manager"),
        ("kind", "version", "Local Kubernetes"),
        ("minikube", "version", "Local Kubernetes"),
        ("docker-compose", "--version", "Docker Compose"),
        ("ansible", "--version", "Configuration management"),
        ("jq", "--version", "JSON processor"),
    ]

    @staticmethod
    def check_tool(command: str, version_flag: str = "--version") -> tuple[bool, Optional[str]]:
        """Check if tool is installed and get version."""
        installed = check_command_installed(command)
        version = None

        if installed:
            version = get_command_version(command, version_flag)

        return installed, version

    @staticmethod
    def run_diagnostics() -> dict:
        """Run full system diagnostics."""
        print_section("System Health Check")

        # Check required tools
        required_status = []
        for tool, flag, description in DoctorRunner.REQUIRED_TOOLS:
            installed, version = DoctorRunner.check_tool(tool, flag)
            version_info = version or ("Not installed" if not installed else "Unknown version")
            required_status.append((f"{tool} ({description})", installed, version_info))

        # Display required tools
        console.print(create_status_table(required_status, "Required Tools"))
        console.print()

        # Check optional tools
        optional_status = []
        for tool, flag, description in DoctorRunner.OPTIONAL_TOOLS:
            installed, version = DoctorRunner.check_tool(tool, flag)
            if installed:
                version_info = version or "Installed"
                optional_status.append(
                    (f"{tool} ({description})", installed, version_info)
                )

        if optional_status:
            console.print(create_status_table(optional_status, "Optional Tools"))
            console.print()

        # Determine health status
        required_installed = sum(1 for _, installed, _ in required_status if installed)
        required_total = len(required_status)

        print_section("Summary")

        if required_installed == required_total:
            print_success(f"All {required_total} required tools are installed!")
            print_warning(
                f"Optional tools installed: {len(optional_status)}\n"
                "                       Install more for enhanced functionality"
            )
            health = "excellent"
        elif required_installed >= required_total - 1:
            print_warning(
                f"Missing {required_total - required_installed} required tool(s)\n"
                "                       Some features may not work"
            )
            health = "fair"
        else:
            print_warning(
                f"Missing {required_total - required_installed} required tool(s)\n"
                "                       Most features will not work"
            )
            health = "poor"

        return {
            "required": required_status,
            "optional": optional_status,
            "health": health,
            "required_installed": required_installed,
            "required_total": required_total,
        }

    @staticmethod
    def print_installation_guide() -> None:
        """Print installation guide for missing tools."""
        print_section("Installation Guide")

        guides = {
            "terraform": "https://www.terraform.io/downloads.html",
            "kubectl": "https://kubernetes.io/docs/tasks/tools/",
            "docker": "https://www.docker.com/products/docker-desktop",
            "git": "https://git-scm.com/downloads",
            "python": "https://www.python.org/downloads/",
            "aws-cli": "https://aws.amazon.com/cli/",
            "gcloud": "https://cloud.google.com/sdk/docs/install",
            "az": "https://docs.microsoft.com/cli/azure/install-azure-cli",
            "helm": "https://helm.sh/docs/intro/install/",
            "kind": "https://kind.sigs.k8s.io/docs/user/quick-start/",
            "minikube": "https://minikube.sigs.k8s.io/docs/start/",
        }

        console.print("[yellow]Missing tools can be installed from:[/yellow]\n")
        for tool, url in guides.items():
            console.print(f"  • [cyan]{tool}[/cyan]: [underline blue]{url}[/underline blue]")

    @staticmethod
    def print_recommendations() -> None:
        """Print recommendations based on diagnosis."""
        print_section("Recommendations")

        recommendations = [
            "✓ Keep tools updated to latest versions",
            "✓ Use virtual environments for Python projects",
            "✓ Configure kubectl for your cluster context",
            "✓ Set up cloud CLI credentials (AWS/GCP/Azure)",
            "✓ Enable Docker Desktop for Mac/Windows",
            "✓ Use kind or minikube for local Kubernetes testing",
        ]

        for rec in recommendations:
            console.print(f"  {rec}")
