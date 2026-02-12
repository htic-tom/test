"""Memory primitives used by the simple agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryEvent:
    """A single event in the agent timeline."""

    kind: str
    payload: dict[str, Any]


@dataclass
class ConversationMemory:
    """Stores events for each run and makes them easy to inspect."""

    events: list[MemoryEvent] = field(default_factory=list)

    def add_user_goal(self, goal: str) -> None:
        self.events.append(MemoryEvent(kind="user_goal", payload={"goal": goal}))

    def add_tool_result(self, tool_name: str, args: dict[str, Any], result: str) -> None:
        self.events.append(
            MemoryEvent(
                kind="tool_result",
                payload={"tool_name": tool_name, "args": args, "result": result},
            )
        )

    def tool_results(self) -> list[MemoryEvent]:
        return [event for event in self.events if event.kind == "tool_result"]

    def latest_tool_result(self) -> MemoryEvent | None:
        for event in reversed(self.events):
            if event.kind == "tool_result":
                return event
        return None
