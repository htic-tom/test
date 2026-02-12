from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    memory_path: str


def load_settings() -> Settings:
    # .env loading is handled in the CLI so that importing this module is side-effect free.
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL") or "gpt-4.1-mini",
        memory_path=os.getenv("AGENT_MEMORY_PATH") or ".agent_memory.json",
    )

