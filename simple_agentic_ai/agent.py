from __future__ import annotations

from typing import Protocol

from .models import AgentAction, AgentRunResult, AgentStep
from .tools import Tool


class BrainProtocol(Protocol):
    def decide(
        self,
        goal: str,
        available_tools: list[str],
        steps: list[AgentStep],
    ) -> AgentAction: ...


class SimpleAgent:
    """Executes a think-act-observe loop."""

    def __init__(self, brain: BrainProtocol, tools: dict[str, Tool]) -> None:
        self.brain = brain
        self.tools = tools

    def run(self, goal: str, max_steps: int = 5) -> AgentRunResult:
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1")

        steps: list[AgentStep] = []
        tool_names = list(self.tools.keys())

        for step_number in range(1, max_steps + 1):
            action = self.brain.decide(goal=goal, available_tools=tool_names, steps=steps)
            if action.final_answer is not None:
                return AgentRunResult(
                    goal=goal,
                    final_answer=action.final_answer,
                    steps=steps,
                    completed=True,
                )

            if not action.tool_name:
                steps.append(
                    AgentStep(
                        step_number=step_number,
                        thought=action.thought,
                        tool_name=None,
                        tool_input=action.tool_input,
                        observation="No tool selected by brain.",
                    )
                )
                break

            observation = self._run_tool(action.tool_name, action.tool_input)
            steps.append(
                AgentStep(
                    step_number=step_number,
                    thought=action.thought,
                    tool_name=action.tool_name,
                    tool_input=action.tool_input,
                    observation=observation,
                )
            )

        return AgentRunResult(
            goal=goal,
            final_answer=self._build_fallback_answer(goal=goal, steps=steps),
            steps=steps,
            completed=False,
        )

    def _run_tool(self, tool_name: str, tool_input: dict[str, object]) -> str:
        tool = self.tools.get(tool_name)
        if tool is None:
            return f"Unknown tool: {tool_name}"
        try:
            return tool.run(tool_input)
        except Exception as exc:  # pragma: no cover - defensive path
            return f"Tool '{tool_name}' failed: {exc}"

    @staticmethod
    def _build_fallback_answer(goal: str, steps: list[AgentStep]) -> str:
        if not steps:
            return f"I could not complete the goal: {goal}"

        last = steps[-1]
        return (
            "I reached the step limit before a final answer.\n"
            f"Latest observation: {last.observation}"
        )
