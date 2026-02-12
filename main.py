"""CLI entrypoint for the simple agentic AI project."""

from __future__ import annotations

import argparse
import json
from typing import Any

from simple_agentic_ai import build_default_agent


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simple tool-using AI agent.")
    parser.add_argument("goal", nargs="?", help="Goal for the agent to solve.")
    parser.add_argument("--goal", dest="goal_flag", help="Goal for the agent to solve.")
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print the internal thought/action trace.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit output as JSON.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run an interactive prompt until you enter 'exit'.",
    )
    return parser


def _result_to_json(result: Any) -> str:
    payload = {
        "goal": result.goal,
        "final_answer": result.final_answer,
        "steps": [
            {
                "thought": step.thought,
                "action": (
                    None
                    if step.action is None
                    else {"tool_name": step.action.tool_name, "tool_args": step.action.tool_args}
                ),
                "final_answer": step.final_answer,
            }
            for step in result.steps
        ],
    }
    return json.dumps(payload, indent=2)


def _resolve_goal(parsed: argparse.Namespace) -> str | None:
    return parsed.goal_flag or parsed.goal


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    agent = build_default_agent()

    if args.interactive:
        print("Simple Agentic AI interactive mode. Type 'exit' to quit.")
        while True:
            goal = input("\nGoal> ").strip()
            if not goal:
                continue
            if goal.lower() in {"exit", "quit"}:
                print("Goodbye.")
                break
            result = agent.run(goal)
            if args.json:
                print(_result_to_json(result))
            else:
                print(f"\nFinal answer:\n{result.final_answer}")
                if args.trace:
                    print("\nTrace:")
                    print(result.format_trace())
        return

    goal = _resolve_goal(args)
    if not goal:
        parser.error("Provide a goal argument or use --interactive.")
    result = agent.run(goal)

    if args.json:
        print(_result_to_json(result))
        return

    print(f"Goal: {result.goal}\n")
    print(f"Final answer:\n{result.final_answer}")
    if args.trace:
        print("\nTrace:")
        print(result.format_trace())


if __name__ == "__main__":
    main()
