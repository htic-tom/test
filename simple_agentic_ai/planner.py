from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Action:
    kind: str
    tool_name: str = ""
    tool_input: str = ""
    message: str = ""


class RuleBasedPlanner:
    """
    A tiny deterministic planner to keep this project dependency-free.
    It picks a tool on step 1, then summarizes the observation on step 2.
    """

    def plan(self, user_input: str, trace: list[dict[str, str]]) -> Action:
        if trace:
            last = trace[-1]
            return Action(
                kind="final",
                message=f"Tool `{last['tool']}` returned: {last['observation']}",
            )

        lowered = user_input.lower().strip()

        if any(token in lowered for token in ("calculate", "sum", "add", "subtract", "multiply", "divide")):
            expression = _extract_expression(user_input)
            if expression:
                return Action(kind="tool", tool_name="calculator", tool_input=expression)
            return Action(
                kind="final",
                message="I can calculate values if you provide an explicit arithmetic expression (example: 12 / (3 + 1)).",
            )

        if any(token in lowered for token in ("time", "date", "clock")):
            return Action(kind="tool", tool_name="current_time")

        if lowered.startswith("echo "):
            return Action(kind="tool", tool_name="echo", tool_input=user_input[5:])

        if "repeat" in lowered:
            cleaned = lowered.replace("repeat", "", 1).strip(" :")
            if cleaned:
                return Action(kind="tool", tool_name="echo", tool_input=cleaned)

        return Action(
            kind="final",
            message="I can use tools for arithmetic, current UTC time, and echo. Try: 'calculate 4 * (2 + 3)'.",
        )


def _extract_expression(text: str) -> str:
    candidate = re.sub(r"[^0-9+\-*/(). ]", " ", text)
    candidate = re.sub(r"\s+", " ", candidate).strip()
    return candidate
