"""Enhanced UI components with spinners, progress, and colors."""

import subprocess
import time
from pathlib import Path
from typing import Optional, Callable, Any

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

console = Console()


class Spinner:
    """Custom spinner wrapper for elegant loading indicators."""

    def __init__(self, message: str = "Loading", style: str = "cyan"):
        self.message = message
        self.style = style
        self._start_time = None

    def __enter__(self):
        from rich.live import Live
        from rich.spinner import Spinner as RichSpinner

        self.spinner = RichSpinner("dots", text=self.message, style=self.style)
        self.live = Live(self.spinner, console=console, refresh_per_second=12.5)
        self.live.__enter__()
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.__exit__(exc_type, exc_val, exc_tb)

    def update(self, message: str):
        """Update spinner message."""
        from rich.spinner import Spinner as RichSpinner

        self.spinner.text = message


class ErrorHandler:
    """Centralized error handling with helpful messages."""

    ERROR_MESSAGES = {
        "file_not_found": "📁 File not found: {path}\n💡 Make sure the file path is correct",
        "invalid_resource": "❌ Invalid resource type: {resource}\n💡 Supported: terraform, k8s, docker, github-actions",
        "empty_input": "⚠️ Empty input provided\n💡 Please provide a description or requirements",
        "terraform_not_installed": "🔨 Terraform is not installed\n💡 Install from: https://www.terraform.io/downloads.html",
        "kubectl_not_installed": "☸️ kubectl is not installed\n💡 Install from: https://kubernetes.io/docs/tasks/tools/",
        "docker_not_installed": "🐳 Docker is not installed\n💡 Install from: https://www.docker.com/products/docker-desktop",
        "permission_denied": "🔒 Permission denied: {path}\n💡 Check file permissions or run with appropriate privileges",
        "network_error": "🌐 Network error\n💡 Check your internet connection",
    }

    @staticmethod
    def handle(error_type: str, **kwargs) -> None:
        """Display helpful error message."""
        message = ErrorHandler.ERROR_MESSAGES.get(
            error_type,
            f"❌ Error: {error_type}",
        )
        formatted = message.format(**kwargs) if kwargs else message

        console.print(Panel(formatted, style="red", border_style="red"))

    @staticmethod
    def handle_exception(exc: Exception, context: str = "") -> None:
        """Handle exception with context."""
        error_msg = str(exc)
        panel_text = f"❌ {context}\n\n[red]{error_msg}[/red]"

        if "No such file" in error_msg or "not found" in error_msg:
            panel_text += "\n\n💡 Make sure all paths are correct"
        elif "permission" in error_msg.lower():
            panel_text += "\n\n💡 Check file permissions or privileges"

        console.print(Panel(panel_text, style="red", border_style="red"))


class ProgressBar:
    """Simple progress bar for operations."""

    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.description = description
        self.current = 0

    def update(self, advance: int = 1):
        """Advance progress."""
        self.current = min(self.current + advance, self.total)
        percent = (self.current / self.total) * 100
        filled = int(percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        console.print(f"[cyan]{self.description}[/cyan] [{bar}] {percent:.0f}%", end="\r")

    def finish(self):
        """Mark as complete."""
        console.print(f"[green]✓ {self.description} Complete![/green]")


def print_success(message: str, icon: str = "✓") -> None:
    """Print success message."""
    console.print(f"[green]{icon}[/green] [bold green]{message}[/bold green]")


def print_error(message: str, icon: str = "✗") -> None:
    """Print error message."""
    console.print(f"[red]{icon}[/red] [bold red]{message}[/bold red]")


def print_info(message: str, icon: str = "ℹ") -> None:
    """Print info message."""
    console.print(f"[cyan]{icon}[/cyan] [bold cyan]{message}[/bold cyan]")


def print_warning(message: str, icon: str = "⚠") -> None:
    """Print warning message."""
    console.print(f"[yellow]{icon}[/yellow] [bold yellow]{message}[/bold yellow]")


def print_header(title: str, subtitle: str = "") -> None:
    """Print header with styling."""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]" if subtitle else f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()


def print_section(title: str) -> None:
    """Print section divider."""
    console.print(f"\n[bold cyan]▶ {title}[/bold cyan]")
    console.print("[dim]" + "─" * 60 + "[/dim]")


def print_code(code: str, language: str = "text", title: str = "Output") -> None:
    """Print code with syntax highlighting."""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="green"))


def print_example(command: str, description: str = "") -> None:
    """Print example command."""
    panel_text = f"[yellow]{command}[/yellow]"
    if description:
        panel_text = f"[dim]{description}[/dim]\n\n{panel_text}"

    console.print(Panel(
        panel_text,
        title="[bold]Example[/bold]",
        border_style="yellow",
        padding=(1, 2),
    ))


def create_help_text(
    description: str,
    examples: list[tuple[str, str]],
    tips: Optional[list[str]] = None,
) -> str:
    """Create rich help text with examples and tips."""
    help_text = f"{description}\n\n"

    if examples:
        help_text += "[bold cyan]Examples:[/bold cyan]\n"
        for cmd, desc in examples:
            help_text += f"  • [yellow]{cmd}[/yellow]\n"
            help_text += f"    → {desc}\n"

    if tips:
        help_text += "\n[bold cyan]Tips:[/bold cyan]\n"
        for tip in tips:
            help_text += f"  💡 {tip}\n"

    return help_text


def run_with_spinner(
    func: Callable,
    message: str = "Processing",
    success_message: str = "Done!",
) -> Any:
    """Run function with spinner."""
    with Spinner(message=f"[cyan]{message}[/cyan]") as spinner:
        try:
            result = func()
            return result
        except Exception as e:
            raise


def check_command_installed(command: str) -> bool:
    """Check if command is installed."""
    try:
        subprocess.run(
            ["which", command],
            capture_output=True,
            check=True,
            timeout=2,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_command_version(command: str, version_flag: str = "--version") -> Optional[str]:
    """Get version of installed command."""
    try:
        result = subprocess.run(
            [command, version_flag],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            # Extract first line containing version info
            output = result.stdout.strip()
            return output.split('\n')[0]
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def create_status_table(
    items: list[tuple[str, bool, Optional[str]]],
    title: str = "Status",
) -> Table:
    """Create a status table."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Version/Info", style="green")

    for name, installed, version_info in items:
        status = "[green]✓ Installed[/green]" if installed else "[red]✗ Not Found[/red]"
        info = version_info or ""
        table.add_row(name, status, info)

    return table
