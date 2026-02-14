"""Core utility functions for DevOps AI Copilot."""

import json
import re
from pathlib import Path
from typing import Any, Dict

from rich.console import Console

console = Console()


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return json.load(f)


def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    """Save configuration to JSON file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def parse_natural_language(text: str) -> Dict[str, str]:
    """Parse natural language input into structured format."""
    parsed = {"original": text, "keywords": [], "intent": ""}

    # Extract keywords
    keywords = re.findall(r"\b[a-z]+\b", text.lower())
    parsed["keywords"] = list(set(keywords))

    # Detect intent
    intents = {
        "create": ["create", "build", "setup", "init", "provision"],
        "deploy": ["deploy", "push", "release", "publish"],
        "diagnose": ["diagnose", "debug", "analyze", "check", "inspect"],
        "optimize": ["optimize", "improve", "reduce", "cost"],
        "document": ["document", "diagram", "visualize"],
    }

    for intent, words in intents.items():
        if any(word in keywords for word in words):
            parsed["intent"] = intent
            break

    return parsed


def format_output(data: Any, format: str = "json") -> str:
    """Format output in specified format."""
    if format == "json":
        return json.dumps(data, indent=2)
    elif format == "yaml":
        import yaml

        return yaml.dump(data, default_flow_style=False)
    else:
        return str(data)


def ensure_project_dir(path: Path) -> Path:
    """Ensure project directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_file(path: Path, content: str) -> None:
    """Write content to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def read_file(path: Path) -> str:
    """Read content from file."""
    with open(path) as f:
        return f.read()
