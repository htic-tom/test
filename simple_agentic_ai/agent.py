from __future__ import annotations

from dataclasses import dataclass, field

from .planner import RuleBasedPlanner
from .tools import ToolRegistry


@dataclass(frozen=True)
class AgentResult:
    response: str
    trace: list[dict[str, str]] = field(default_factory=list)


class SimpleAgent:
    def __init__(
        self,
        planner: RuleBasedPlanner,
        tools: ToolRegistry,
        max_steps: int = 3,
    ) -> None:
        self._planner = planner
        self._tools = tools
        self._max_steps = max_steps

    def run(self, user_input: str) -> AgentResult:
        trace: list[dict[str, str]] = []

        for _ in range(self._max_steps):
            action = self._planner.plan(user_input=user_input, trace=trace)

            if action.kind == "final":
                return AgentResult(response=action.message, trace=trace)

            if action.kind != "tool":
                return AgentResult(response=f"Unsupported action kind: {action.kind}", trace=trace)

            try:
                observation = self._tools.call(action.tool_name, action.tool_input)
            except Exception as exc:  # noqa: BLE001 - intentional for simple demo robustness
                observation = f"Tool error: {exc}"

            trace.append(
                {
                    "tool": action.tool_name,
                    "input": action.tool_input,
                    "observation": observation,
                }
            )

        return AgentResult(
            response="Reached max steps before final answer.",
            trace=trace,
        )
