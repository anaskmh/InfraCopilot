"""Base classes for code generators."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseGenerator(ABC):
    """Abstract base class for all generators."""

    def __init__(self, project_name: str, config: Optional[Dict[str, Any]] = None):
        self.project_name = project_name
        self.config = config or {}

    @abstractmethod
    def generate(self, requirements: str) -> str:
        """Generate code from natural language requirements."""
        pass

    def validate_input(self, requirements: str) -> bool:
        """Validate input requirements."""
        return bool(requirements and len(requirements.strip()) > 0)

    def format_output(self) -> str:
        """Format output for display."""
        return ""
