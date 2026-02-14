"""Generate infrastructure code command."""

import typer
from pathlib import Path
from rich.console import Console

from devops_ai.generators import (
    TerraformGenerator,
    KubernetesGenerator,
    GitHubActionsGenerator,
    DockerfileGenerator,
)
from devops_ai.utils import write_file

console = Console()
app = typer.Typer()


@app.command()
def generate(
    resource_type: str = typer.Argument(
        "terraform", help="Resource type (terraform, k8s, docker, github-actions)"
    ),
    description: str = typer.Option(
        "production-ready setup", "--desc", "-d", help="Natural language description"
    ),
    project_name: str = typer.Option(
        "my-project", "--project", "-p", help="Project name"
    ),
    output_dir: str = typer.Option(
        "outputs", "--output", "-o", help="Output directory"
    ),
):
    """Generate infrastructure code from natural language description."""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        console.print(f"[cyan]Generating {resource_type}...[/cyan]")
        console.print(f"[dim]Description: {description}[/dim]")

        # Generate based on resource type
        if resource_type.lower() == "terraform":
            generator = TerraformGenerator(project_name)
            content = generator.generate(description)
            output_file = output_path / "main.tf"

        elif resource_type.lower() == "k8s":
            generator = KubernetesGenerator(project_name)
            content = generator.generate(description)
            output_file = output_path / "deployment.yaml"

        elif resource_type.lower() == "docker":
            generator = DockerfileGenerator(project_name)
            if "compose" in description.lower():
                content = generator.generate_dockercompose(description)
                output_file = output_path / "docker-compose.yml"
            else:
                content = generator.generate(description)
                output_file = output_path / "Dockerfile"

        elif resource_type.lower() == "github-actions":
            generator = GitHubActionsGenerator(project_name)
            content = generator.generate(description)
            output_file = output_path / "ci-cd.yml"

        else:
            console.print(
                f"[red]Unknown resource type: {resource_type}[/red]",
                style="bold",
            )
            raise typer.Exit(1)

        # Write output
        write_file(output_file, content)

        console.print(
            f"[green]✓[/green] Generated {resource_type} configuration",
            style="bold",
        )
        console.print(f"[cyan]Output:[/cyan] {output_file}")
        console.print(
            f"\n[yellow]Preview:[/yellow]\n{content[:500]}...",
            style="dim",
        )

    except Exception as e:
        console.print(
            f"[red]✗ Error generating {resource_type}: {e}[/red]",
            style="bold",
        )
        raise typer.Exit(1)
