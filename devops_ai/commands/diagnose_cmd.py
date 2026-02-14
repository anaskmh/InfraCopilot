"""Diagnose logs and infrastructure command."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from devops_ai.diagnostics import LogAnalyzer, DiagnosticRunner
from devops_ai.utils import read_file

console = Console()
app = typer.Typer()


@app.command()
def diagnose(
    log_file: str = typer.Option(
        None, "--file", "-f", help="Log file path to analyze"
    ),
    infrastructure: str = typer.Option(
        None, "--infra", "-i", help="Infrastructure type (k8s, docker)"
    ),
    namespace: str = typer.Option(
        "default", "--namespace", "-n", help="Kubernetes namespace"
    ),
):
    """Diagnose logs and infrastructure issues."""
    try:
        if log_file:
            # Analyze log file
            console.print("[cyan]Analyzing logs...[/cyan]")
            log_content = read_file(Path(log_file))

            analyzer = LogAnalyzer()
            analysis = analyzer.analyze(log_content)

            # Display results
            console.print(
                f"\n[bold]Analysis Results:[/bold]",
                style="green",
            )

            table = Table(title="Issue Summary")
            table.add_column("Severity", style="cyan")
            table.add_column("Count", style="magenta")
            table.add_row("Critical", str(analysis["critical"]))
            table.add_row("High", str(analysis["high"]))
            table.add_row("Medium", str(analysis["medium"]))

            console.print(table)

            # Show fixes
            if analysis["issues"]:
                console.print("\n[bold]Suggested Fixes:[/bold]", style="yellow")
                suggestions = analyzer.suggest_fixes(log_content)
                for suggestion in suggestions[:5]:  # Show top 5
                    console.print(suggestion)

            else:
                console.print("[green]✓ No issues found![/green]")

        elif infrastructure:
            # Diagnose infrastructure
            console.print(f"[cyan]Running {infrastructure} diagnostics...[/cyan]")
            runner = DiagnosticRunner()

            if infrastructure.lower() == "k8s":
                results = runner.diagnose_kubernetes(namespace)
                console.print(
                    f"[green]Kubernetes Diagnostics (ns: {namespace})[/green]"
                )

            elif infrastructure.lower() == "docker":
                results = runner.diagnose_docker("container")
                console.print("[green]Docker Diagnostics[/green]")

            else:
                console.print(f"[red]Unknown infrastructure type: {infrastructure}[/red]")
                raise typer.Exit(1)

            # Display results
            for check, result in results.items():
                console.print(f"\n[cyan]{check}:[/cyan]")
                if isinstance(result, dict):
                    for key, value in result.items():
                        console.print(f"  - {key}: {value}")

        else:
            console.print("[red]Provide either --file or --infra[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(
            f"[red]✗ Error during diagnosis: {e}[/red]",
            style="bold",
        )
        raise typer.Exit(1)
