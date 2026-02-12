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

        text = user.lower()
        if "note" in text and ("save" in text or "write" in text):
            return json.dumps({"type": "tool_call", "tool": "write_note", "args": {"text": user}}, ensure_ascii=False)
        if "time" in text or "utc" in text:
            return json.dumps({"type": "tool_call", "tool": "time_now", "args": {}}, ensure_ascii=False)
        if any(k in text for k in ["calc", "calculate", "+", "-", "*", "/", "**"]):
            return json.dumps({"type": "tool_call", "tool": "calculator", "args": {"expression": user}}, ensure_ascii=False)
        return json.dumps({"type": "final", "answer": f"(mock) I received: {user}"}, ensure_ascii=False)

