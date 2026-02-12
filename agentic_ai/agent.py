"""Core agent and planner implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol
import re

from .tools import ToolRegistry, build_default_tool_registry


ActionType = Literal["think", "tool", "finish"]


@dataclass
class PlannerAction:
    action_type: ActionType
    reasoning: str
    tool_name: str | None = None
    tool_input: str | None = None
    final_answer: str | None = None


class Planner(Protocol):
    def decide(
        self,
        *,
        goal: str,
        history: list[dict[str, str]],
        available_tools: list[str],
    ) -> PlannerAction:
        """Decide the agent's next action."""


class RuleBasedPlanner:
    """
    A tiny deterministic planner to keep this project dependency-free.

    It mimics a basic "reason -> choose tool -> observe -> answer" loop.
    """

    _EXPRESSION_RE = re.compile(r"(?P<expr>[0-9\.\+\-\*\/\(\)\s%]{3,})")
    _QUOTED_PATH_RE = re.compile(r"['\"](?P<path>[^'\"]+\.[a-zA-Z0-9]+)['\"]")

    def decide(
        self,
        *,
        goal: str,
        history: list[dict[str, str]],
        available_tools: list[str],
    ) -> PlannerAction:
        used_tools = [entry["tool"] for entry in history if entry.get("type") == "tool_call"]
        lower_goal = goal.lower()

        if not history:
            return PlannerAction(
                action_type="think",
                reasoning="I should inspect the goal, then pick tools if useful.",
            )

        if "calculator" in available_tools and "calculator" not in used_tools:
            expression = self._extract_expression(goal)
            if expression:
                return PlannerAction(
                    action_type="tool",
                    reasoning="This goal contains arithmetic, so I will calculate it.",
                    tool_name="calculator",
                    tool_input=expression,
                )

        if "read_text_file" in available_tools and "read_text_file" not in used_tools:
            path = self._extract_quoted_path(goal)
            if path:
                return PlannerAction(
                    action_type="tool",
                    reasoning="A quoted file path is present; reading it may help.",
                    tool_name="read_text_file",
                    tool_input=path,
                )

        if "current_time" in available_tools and "current_time" not in used_tools:
            if any(term in lower_goal for term in ("time", "date", "today", "utc")):
                return PlannerAction(
                    action_type="tool",
                    reasoning="The user asked for current time/date information.",
                    tool_name="current_time",
                    tool_input="",
                )

        return PlannerAction(
            action_type="finish",
            reasoning="I have enough context to deliver a final response.",
            final_answer=self._compose_final_answer(goal=goal, history=history),
        )

    def _extract_expression(self, goal: str) -> str | None:
        for match in self._EXPRESSION_RE.finditer(goal):
            candidate = match.group("expr").strip()
            has_digit = any(ch.isdigit() for ch in candidate)
            has_operator = any(ch in "+-*/%" for ch in candidate)
            if has_digit and has_operator:
                return candidate
        return None

    def _extract_quoted_path(self, goal: str) -> str | None:
        match = self._QUOTED_PATH_RE.search(goal)
        if match:
            return match.group("path")
        return None

    def _compose_final_answer(self, *, goal: str, history: list[dict[str, str]]) -> str:
        tool_results = [
            entry for entry in history if entry.get("type") == "tool_result"
        ]
        if not tool_results:
            return (
                "I could not identify a tool action that would improve this answer. "
                f"Goal received: {goal}"
            )

        lines = ["Result summary:"]
        for result in tool_results:
            lines.append(f"- {result['tool']}: {result['output']}")
        return "\n".join(lines)


class SimpleAgent:
    """Runs a bounded action loop with planner + tools."""

    def __init__(
        self,
        *,
        planner: Planner | None = None,
        tools: ToolRegistry | None = None,
        max_steps: int = 6,
    ) -> None:
        self.planner = planner or RuleBasedPlanner()
        self.tools = tools or build_default_tool_registry()
        self.max_steps = max_steps

    def run(self, goal: str) -> dict[str, object]:
        history: list[dict[str, str]] = []
        final_answer = "Agent stopped before producing an answer."

        for step in range(1, self.max_steps + 1):
            action = self.planner.decide(
                goal=goal,
                history=history,
                available_tools=sorted(self.tools.names),
            )
            history.append(
                {
                    "type": "planner_action",
                    "step": str(step),
                    "action_type": action.action_type,
                    "reasoning": action.reasoning,
                }
            )

            if action.action_type == "think":
                continue

            if action.action_type == "tool":
                tool_name = action.tool_name or ""
                tool_input = action.tool_input or ""
                history.append(
                    {
                        "type": "tool_call",
                        "step": str(step),
                        "tool": tool_name,
                        "input": tool_input,
                    }
                )
                try:
                    output = self.tools.run(tool_name, tool_input)
                except Exception as exc:  # pragma: no cover - exercised via runtime
                    output = f"ERROR: {exc}"
                history.append(
                    {
                        "type": "tool_result",
                        "step": str(step),
                        "tool": tool_name,
                        "output": output,
                    }
                )
                continue

            if action.action_type == "finish":
                final_answer = action.final_answer or "No final answer provided."
                return {
                    "goal": goal,
                    "answer": final_answer,
                    "history": history,
                    "steps_used": step,
                }

        return {
            "goal": goal,
            "answer": final_answer,
            "history": history,
            "steps_used": self.max_steps,
        }
