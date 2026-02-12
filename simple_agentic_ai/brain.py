from __future__ import annotations

import re

from .models import AgentAction, AgentStep


class RuleBasedBrain:
    """
    A tiny planner/executor policy.

    This intentionally keeps decisions simple so the project can run
    with no external API keys while still demonstrating an agent loop.
    """

    _math_pattern = re.compile(
        r"(-?\d+(?:\.\d+)?(?:\s*[-+*/%]\s*-?\d+(?:\.\d+)?)+)"
    )

    def decide(
        self,
        goal: str,
        available_tools: list[str],
        steps: list[AgentStep],
    ) -> AgentAction:
        if steps:
            last = steps[-1]
            return AgentAction(
                thought="I used a tool and can now answer the user.",
                final_answer=f"Based on the tool output, here is the result:\n{last.observation}",
            )

        normalized_goal = goal.strip()
        lower_goal = normalized_goal.lower()

        if "time" in lower_goal or "date" in lower_goal:
            return AgentAction(
                thought="The user is asking for time information.",
                tool_name="get_time",
            )

        if (
            "list files" in lower_goal
            or "show files" in lower_goal
            or "what files" in lower_goal
        ):
            return AgentAction(
                thought="The user wants a directory listing.",
                tool_name="list_files",
                tool_input={"path": "."},
            )

        read_path = self._extract_path_after_keywords(
            text=normalized_goal,
            keywords=("read file", "open file", "read", "open"),
        )
        if read_path:
            return AgentAction(
                thought="The user asked to read a file.",
                tool_name="read_file",
                tool_input={"path": read_path},
            )

        math_match = self._math_pattern.search(normalized_goal)
        if math_match:
            return AgentAction(
                thought="This looks like an arithmetic request.",
                tool_name="calculator",
                tool_input={"expression": math_match.group(1)},
            )

        if "echo" in available_tools:
            return AgentAction(
                thought="No specialized tool matched, so I will echo the request.",
                tool_name="echo",
                tool_input={"text": normalized_goal},
            )

        return AgentAction(
            thought="No good action available.",
            final_answer="I could not determine a suitable action.",
        )

    @staticmethod
    def _extract_path_after_keywords(text: str, keywords: tuple[str, ...]) -> str | None:
        cleaned = text.strip()
        lower = cleaned.lower()

        for keyword in keywords:
            if keyword not in lower:
                continue

            start_index = lower.find(keyword) + len(keyword)
            remainder = cleaned[start_index:].strip()
            if not remainder:
                return None

            if remainder[0] in {'"', "'"} and remainder[-1] == remainder[0]:
                return remainder[1:-1].strip()

            first_token = remainder.split()[0]
            return first_token.strip(".,")

        return None
