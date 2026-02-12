from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .agent import Agent
from .config import load_settings
from .llm import MockProvider, OpenAIProvider
from .memory import Memory
from .tools import build_tools


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="simple-agentic-ai", description="A tiny agentic AI CLI.")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run an interactive agent session")
    run.add_argument("--mock", action="store_true", help="Use a deterministic mock model (no API key needed)")
    run.add_argument("--model", default=None, help="Override model name (default from OPENAI_MODEL)")
    run.add_argument("--max-steps", type=int, default=8, help="Maximum tool/LLM steps per user goal")
    return p


def main(argv: list[str] | None = None) -> int:
    load_dotenv(override=False)
    args = _build_parser().parse_args(argv)
    settings = load_settings()

    mem = Memory(path=Path(settings.memory_path))
    mem.load()
    tools = build_tools(mem)

    if args.cmd == "run":
        model = args.model or settings.openai_model
        llm = MockProvider() if args.mock else OpenAIProvider(api_key=settings.openai_api_key)
        agent = Agent(llm=llm, tools=tools, model=model)

        print("Type your goal and press enter. Ctrl+C to exit.\n")
        while True:
            try:
                goal = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye")
                return 0
            if not goal:
                continue
            try:
                result = agent.run(goal, max_steps=args.max_steps)
            except Exception as e:
                print(f"[error] {e}")
                continue
            print(result.answer)
            print()

    return 0

