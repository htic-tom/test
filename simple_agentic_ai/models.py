from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentAction:
    """A single decision from the brain."""

    thought: str
    tool_name: str | None = None
    tool_input: dict[str, Any] = field(default_factory=dict)
    final_answer: str | None = None


@dataclass(slots=True)
class AgentStep:
    """One executed step in the loop."""

    step_number: int
    thought: str
    tool_name: str | None
    tool_input: dict[str, Any]
    observation: str


@dataclass(slots=True)
class AgentRunResult:
    """Outcome of one call to the agent."""

    goal: str
    final_answer: str
    steps: list[AgentStep]
    completed: bool

    def trace_lines(self) -> list[str]:
        lines: list[str] = []
        for step in self.steps:
            lines.append(f"Step {step.step_number} thought: {step.thought}")
            if step.tool_name:
                lines.append(
                    f"Step {step.step_number} tool: {step.tool_name}({step.tool_input})"
                )
            lines.append(f"Step {step.step_number} observation: {step.observation}")
        return lines
