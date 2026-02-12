from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMProvider:
    def complete(self, messages: list[Message], *, model: str) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self._client = OpenAI(api_key=api_key)

    def complete(self, messages: list[Message], *, model: str) -> str:
        resp = self._client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""


class MockProvider(LLMProvider):
    """
    A deterministic fallback that returns tool-call JSON for a couple patterns.
    Useful for testing the agent loop without network/API keys.
    """

    def complete(self, messages: list[Message], *, model: str) -> str:
        _ = model
        user = ""
        for m in reversed(messages):
            if m.role == "user":
                user = m.content
                break

        # If we just received a tool result, finish with a short summary.
        if user.startswith("Tool result:"):
            payload = user[len("Tool result:") :].strip()
            try:
                tr = json.loads(payload)
            except Exception:
                return json.dumps({"type": "final", "answer": f"(mock) Tool returned: {payload}"}, ensure_ascii=False)

            if not isinstance(tr, dict):
                return json.dumps({"type": "final", "answer": f"(mock) Tool returned: {payload}"}, ensure_ascii=False)

            if not tr.get("ok"):
                return json.dumps(
                    {"type": "final", "answer": f"(mock) Tool error from {tr.get('tool')}: {tr.get('error')}"},
                    ensure_ascii=False,
                )

            tool = tr.get("tool")
            result = tr.get("result") or {}

            if tool == "time_now":
                return json.dumps({"type": "final", "answer": str(result.get("utc_now", ""))}, ensure_ascii=False)
            if tool == "calculator":
                return json.dumps({"type": "final", "answer": str(result.get("value", ""))}, ensure_ascii=False)
            if tool == "write_note":
                note = result.get("note") or {}
                return json.dumps({"type": "final", "answer": f"(mock) saved note at {note.get('ts')}"}, ensure_ascii=False)
            if tool == "list_notes":
                notes = result.get("notes") or []
                if not notes:
                    return json.dumps({"type": "final", "answer": "(mock) no notes yet"}, ensure_ascii=False)
                lines = [f"- [{n.get('ts')}] {n.get('text')}" for n in notes]
                return json.dumps({"type": "final", "answer": "(mock) notes:\n" + "\n".join(lines)}, ensure_ascii=False)

            return json.dumps({"type": "final", "answer": f"(mock) Tool {tool} returned: {result}"}, ensure_ascii=False)

        text = user.lower()
        if "list notes" in text or "show notes" in text:
            return json.dumps({"type": "tool_call", "tool": "list_notes", "args": {}}, ensure_ascii=False)
        if "note" in text and ("save" in text or "write" in text):
            return json.dumps({"type": "tool_call", "tool": "write_note", "args": {"text": user}}, ensure_ascii=False)
        if "time" in text or "utc" in text:
            return json.dumps({"type": "tool_call", "tool": "time_now", "args": {}}, ensure_ascii=False)
        if any(k in text for k in ["calc", "calculate", "+", "-", "*", "/", "**"]):
            expr = "".join(c for c in user if c in "0123456789+-*/().% \t")
            expr = expr.strip() or user
            return json.dumps({"type": "tool_call", "tool": "calculator", "args": {"expression": expr}}, ensure_ascii=False)
        return json.dumps({"type": "final", "answer": f"(mock) I received: {user}"}, ensure_ascii=False)

