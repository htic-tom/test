"""Core agent loop and a small heuristic planner."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .memory import ConversationMemory
from .tools import ToolRegistry, build_default_registry


@dataclass
class ToolAction:
    """A single tool call request from the planner."""

    tool_name: str
    tool_args: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStep:
    """A thought/action/final output snapshot for one iteration."""

    thought: str
    action: ToolAction | None = None
    final_answer: str | None = None


@dataclass
class AgentRunResult:
    """Final answer and trace from an agent run."""

    goal: str
    final_answer: str
    steps: list[AgentStep]
    memory: ConversationMemory

    def format_trace(self) -> str:
        lines: list[str] = []
        for index, step in enumerate(self.steps, start=1):
            lines.append(f"Step {index}: {step.thought}")
            if step.action:
                lines.append(f"  -> tool: {step.action.tool_name} args={step.action.tool_args}")
            if step.final_answer is not None:
                lines.append(f"  -> final: {step.final_answer}")
        return "\n".join(lines)


class HeuristicPlanner:
    """Simple planner that maps natural-language goals to tool calls."""

    _READ_PATTERN = re.compile(
        r"(?:read|open)\s+(?:the\s+)?(?:file\s+)?(?:\"([^\"]+)\"|'([^']+)'|(\S+))",
        flags=re.IGNORECASE,
    )
    _LIST_PATTERN = re.compile(
        r"(?:list|show)\s+(?:files|directory|dir)(?:\s+(?:in|from)\s+(?:\"([^\"]+)\"|'([^']+)'|(\S+)))?",
        flags=re.IGNORECASE,
    )

    def plan_next_step(
        self,
        goal: str,
        memory: ConversationMemory,
        tools: ToolRegistry,
        remaining_steps: int,
    ) -> AgentStep:
        if remaining_steps <= 0:
            return AgentStep(
                thought="Reached the configured step limit.",
                final_answer="I stopped because I reached the maximum number of steps.",
            )

        latest_tool_result = memory.latest_tool_result()
        if latest_tool_result is not None:
            payload = latest_tool_result.payload
            tool_name = payload["tool_name"]
            result = payload["result"]
            return AgentStep(
                thought=f"I have the result from '{tool_name}', so I can answer now.",
                final_answer=f"Result from {tool_name}:\n{result}",
            )

        lower_goal = goal.lower().strip()

        if "tool" in lower_goal and any(word in lower_goal for word in ("list", "available", "what")):
            tool_lines = [f"- {tool.name}: {tool.description}" for tool in tools.list_tools()]
            return AgentStep(
                thought="The user asked about available tools.",
                final_answer="Available tools:\n" + "\n".join(tool_lines),
            )

        read_path = self._extract_read_path(goal)
        if read_path:
            return AgentStep(
                thought=f"The goal asks to read a file: {read_path}",
                action=ToolAction(tool_name="read_text_file", tool_args={"path": read_path}),
            )

        list_path = self._extract_list_path(goal)
        if list_path is not None:
            return AgentStep(
                thought="The goal asks to list directory contents.",
                action=ToolAction(tool_name="list_directory", tool_args={"path": list_path}),
            )

        if self._is_time_request(lower_goal):
            return AgentStep(
                thought="The goal is about current date/time.",
                action=ToolAction(tool_name="now_iso"),
            )

        expression = self._extract_math_expression(goal)
        if expression:
            return AgentStep(
                thought=f"The goal contains a math expression: {expression}",
                action=ToolAction(tool_name="calculator", tool_args={"expression": expression}),
            )

        return AgentStep(
            thought="No matching tool strategy was detected.",
            final_answer=(
                "I could not identify a tool-based plan for that request. "
                "Try asking me to calculate, list files, read a file, or get the current time."
            ),
        )

    @classmethod
    def _extract_read_path(cls, text: str) -> str | None:
        match = cls._READ_PATTERN.search(text)
        if not match:
            return None
        for group in match.groups():
            if group:
                return group
        return None

    @classmethod
    def _extract_list_path(cls, text: str) -> str | None:
        match = cls._LIST_PATTERN.search(text)
        if not match:
            return None
        for group in match.groups():
            if group:
                return group
        return "."

    @staticmethod
    def _is_time_request(lower_text: str) -> bool:
        return ("time" in lower_text) or ("date" in lower_text) or ("day is it" in lower_text)

    @staticmethod
    def _extract_math_expression(goal: str) -> str | None:
        if not re.search(r"\d", goal):
            return None

        explicit_intent = re.search(
            r"\b(calculate|compute|evaluate|eval|what is|solve)\b",
            goal,
            flags=re.IGNORECASE,
        )
        stripped_goal = goal.strip()
        if not explicit_intent and not re.fullmatch(r"[\d\.\s\+\-\*\/%\(\)]+", stripped_goal):
            return None

        match = re.search(r"([\d\.\s\+\-\*\/%\(\)]+)", goal)
        if not match:
            return None
        candidate = match.group(1).strip()
        if not candidate or not re.search(r"\d", candidate):
            return None
        return candidate


class SimpleAgent:
    """Agent runner that loops planner -> tool -> memory."""

    def __init__(self, tools: ToolRegistry, planner: HeuristicPlanner | None = None, max_steps: int = 4) -> None:
        self.tools = tools
        self.planner = planner or HeuristicPlanner()
        self.max_steps = max_steps

    def run(self, goal: str) -> AgentRunResult:
        memory = ConversationMemory()
        memory.add_user_goal(goal)
        steps: list[AgentStep] = []

        for step_index in range(self.max_steps):
            remaining_steps = self.max_steps - step_index
            step = self.planner.plan_next_step(goal, memory, self.tools, remaining_steps)
            steps.append(step)

            if step.final_answer is not None:
                return AgentRunResult(goal=goal, final_answer=step.final_answer, steps=steps, memory=memory)

            if step.action is None:
                break

            tool_name = step.action.tool_name
            tool_args = step.action.tool_args
            try:
                tool_result = self.tools.run(tool_name, **tool_args)
            except Exception as exc:  # pragma: no cover - exercised indirectly in tests
                tool_result = f"Tool error: {exc}"
            memory.add_tool_result(tool_name=tool_name, args=tool_args, result=tool_result)

        fallback_answer = (
            "I did not reach a final answer within the step limit. "
            "Try rephrasing your request with a specific tool-friendly goal."
        )
        return AgentRunResult(goal=goal, final_answer=fallback_answer, steps=steps, memory=memory)


def build_default_agent() -> SimpleAgent:
    """Convenience constructor with built-in tools and planner."""

    return SimpleAgent(tools=build_default_registry(), planner=HeuristicPlanner(), max_steps=4)
