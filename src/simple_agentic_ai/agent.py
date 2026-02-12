from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .llm import LLMProvider, Message
from .tools import Tool, ToolError


class AgentProtocolError(RuntimeError):
    pass


@dataclass
class AgentResult:
    answer: str
    steps: int


SYSTEM_PROMPT = """You are a small agent.

You must respond with ONE JSON object and no surrounding text.

Schema:
- To call a tool:
  {"type":"tool_call","tool":"<tool_name>","args":{...}}
- To finish:
  {"type":"final","answer":"..."}

Rules:
- If a tool can help, prefer tool_call.
- Keep args strictly to the tool schema.
"""


def _extract_json_object(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        raise AgentProtocolError("Empty model response")

    # Best-effort: allow fenced code blocks or extra text; find outermost JSON object.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise AgentProtocolError("Model response does not contain a JSON object")

    snippet = text[start : end + 1]
    try:
        obj = json.loads(snippet)
    except json.JSONDecodeError as e:
        raise AgentProtocolError(f"Invalid JSON from model: {e}") from e

    if not isinstance(obj, dict):
        raise AgentProtocolError("Top-level JSON must be an object")
    return obj


class Agent:
    def __init__(self, llm: LLMProvider, tools: list[Tool], *, model: str) -> None:
        self._llm = llm
        self._tools = {t.name: t for t in tools}
        self._model = model

    def run(self, goal: str, *, max_steps: int = 8) -> AgentResult:
        messages: list[Message] = [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=goal),
        ]

        for step in range(1, max_steps + 1):
            raw = self._llm.complete(messages, model=self._model)
            action = _extract_json_object(raw)
            action_type = action.get("type")

            if action_type == "final":
                answer = str(action.get("answer", "")).strip()
                return AgentResult(answer=answer, steps=step)

            if action_type != "tool_call":
                raise AgentProtocolError(f"Unknown action type: {action_type!r}")

            tool_name = action.get("tool")
            if tool_name not in self._tools:
                raise AgentProtocolError(f"Unknown tool: {tool_name!r}")

            args = action.get("args") or {}
            if not isinstance(args, dict):
                raise AgentProtocolError("Tool args must be an object")

            tool = self._tools[tool_name]
            try:
                result = tool.handler(args)
                tool_msg = {"ok": True, "tool": tool.name, "result": result}
            except ToolError as e:
                tool_msg = {"ok": False, "tool": tool.name, "error": str(e)}

            messages.append(Message(role="assistant", content=json.dumps(action, ensure_ascii=False)))
            messages.append(Message(role="user", content=f"Tool result: {json.dumps(tool_msg, ensure_ascii=False)}"))

        raise RuntimeError(f"Agent did not finish within {max_steps} steps")

