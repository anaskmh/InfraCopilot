"""Cost optimization command."""

import typer
from rich.console import Console
from rich.table import Table

from devops_ai.cost import CostOptimizer

console = Console()
app = typer.Typer()


@app.command()
def cost(
    report: bool = typer.Option(False, "--report", "-r", help="Generate full report"),
):
    """Analyze cost optimization opportunities."""
    try:
        console.print("[cyan]Analyzing cost optimization opportunities...[/cyan]")

        optimizer = CostOptimizer()
        analysis = optimizer.analyze_infrastructure({})

        if report:
            # Generate detailed report
            report_content = optimizer.generate_cost_report({})
            console.print(report_content)

        else:
            # Display summary table
            table = Table(title="Cost Optimization Recommendations")
            table.add_column("Priority", style="cyan")
            table.add_column("Title", style="magenta")
            table.add_column("Effort", style="yellow")
            table.add_column("Savings", style="green")

            for rec in analysis["recommendations"][:5]:  # Top 5
                table.add_row(
                    rec["priority"],
                    rec["title"],
                    rec["effort"],
                    rec["estimated_savings"],
                )

            console.print(table)

            console.print(
                f"\n[green]✓[/green] Found {analysis['high_priority']} high-priority opportunities"
            )
            console.print("[cyan]Use --report flag for detailed analysis[/cyan]")

    except Exception as e:
        console.print(
            f"[red]✗ Error analyzing costs: {e}[/red]",
            style="bold",
        )
        raise typer.Exit(1)
