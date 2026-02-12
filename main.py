from __future__ import annotations

import argparse
from typing import Iterable

from simple_agentic_ai.agent import SimpleAgent
from simple_agentic_ai.brain import RuleBasedBrain
from simple_agentic_ai.tools import build_default_tools


def print_trace(trace: Iterable[str]) -> None:
    """Pretty-print an execution trace."""
    print("\nExecution trace:")
    for line in trace:
        print(f"  - {line}")


def run_once(goal: str, max_steps: int, show_trace: bool) -> None:
    """Execute one agent run and print the result."""
    agent = SimpleAgent(brain=RuleBasedBrain(), tools=build_default_tools())
    result = agent.run(goal=goal, max_steps=max_steps)

    print(f"\nGoal: {goal}")
    print(f"Answer: {result.final_answer}")
    if show_trace:
        print_trace(result.trace_lines())


def interactive_session(max_steps: int, show_trace: bool) -> None:
    """Start a simple REPL session for the agent."""
    print("Simple Agentic AI (type 'exit' to quit)")
    while True:
        goal = input("\nEnter goal > ").strip()
        if not goal:
            continue
        if goal.lower() in {"exit", "quit"}:
            print("Goodbye.")
            return
        run_once(goal=goal, max_steps=max_steps, show_trace=show_trace)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simple agentic AI demo.")
    parser.add_argument(
        "--goal",
        type=str,
        help="The goal for a single run (omit for interactive mode).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="Maximum agent loop steps (default: 5).",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print step-by-step reasoning trace.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode (REPL).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.interactive or not args.goal:
        interactive_session(max_steps=args.max_steps, show_trace=args.trace)
        return

    run_once(goal=args.goal, max_steps=args.max_steps, show_trace=args.trace)


if __name__ == "__main__":
    main()