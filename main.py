"""CLI entrypoint for a simple agentic AI project."""

from __future__ import annotations

import argparse

from agentic_ai import SimpleAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simple local agentic AI demo.")
    parser.add_argument(
        "goal",
        nargs="*",
        help="Goal for the agent (if omitted, interactive prompt is used).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=6,
        help="Maximum number of reasoning steps.",
    )
    parser.add_argument(
        "--show-trace",
        action="store_true",
        help="Print planner actions and tool calls.",
    )
    return parser.parse_args()


def render_trace(history: list[dict[str, str]]) -> str:
    rows: list[str] = []
    for item in history:
        item_type = item.get("type")
        step = item.get("step", "-")
        if item_type == "planner_action":
            rows.append(
                f"[step {step}] planner -> {item['action_type']} | {item['reasoning']}"
            )
        elif item_type == "tool_call":
            rows.append(
                f"[step {step}] tool_call -> {item['tool']}({item.get('input', '')})"
            )
        elif item_type == "tool_result":
            rows.append(f"[step {step}] tool_result -> {item['tool']}: {item['output']}")
    return "\n".join(rows)


def main() -> None:
    args = parse_args()
    goal = " ".join(args.goal).strip()
    if not goal:
        goal = input("Enter a goal for the agent: ").strip()

    if not goal:
        raise SystemExit("A goal is required.")
    if args.max_steps < 1:
        raise SystemExit("--max-steps must be at least 1.")

    agent = SimpleAgent(max_steps=args.max_steps)
    result = agent.run(goal)

    print("\n=== Final Answer ===")
    print(result["answer"])
    print(f"\n(steps used: {result['steps_used']})")

    if args.show_trace:
        print("\n=== Trace ===")
        print(render_trace(result["history"]))  # type: ignore[arg-type]


if __name__ == "__main__":
    main()