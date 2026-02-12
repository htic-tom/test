from __future__ import annotations

import argparse

from simple_agentic_ai import RuleBasedPlanner, SimpleAgent, ToolRegistry, default_tools


def build_agent() -> SimpleAgent:
    return SimpleAgent(
        planner=RuleBasedPlanner(),
        tools=ToolRegistry(default_tools()),
    )


def run_once(query: str, show_trace: bool) -> None:
    result = build_agent().run(query)
    print(f"\nAssistant: {result.response}")
    if show_trace and result.trace:
        print("Trace:")
        for idx, step in enumerate(result.trace, start=1):
            print(f"  {idx}. tool={step['tool']} input={step['input']!r} observation={step['observation']!r}")


def run_interactive(show_trace: bool) -> None:
    print("Simple Agentic AI (type 'exit' to quit)")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            return
        if not user_input:
            continue
        run_once(query=user_input, show_trace=show_trace)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simple agentic AI demo.")
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Optional one-shot question. If omitted, interactive mode starts.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print agent tool-call trace.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.query:
        run_once(query=args.query, show_trace=args.trace)
    else:
        run_interactive(show_trace=args.trace)

