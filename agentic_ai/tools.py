"""Tooling primitives for the simple agentic AI demo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
import ast
import operator


ToolHandler = Callable[[str], str]
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Tool:
    """Represents a callable tool exposed to the agent."""

    name: str
    description: str
    handler: ToolHandler


class ToolRegistry:
    """Stores and executes tools by name."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def run(self, name: str, tool_input: str) -> str:
        if name not in self._tools:
            available = ", ".join(sorted(self._tools)) or "none"
            raise KeyError(f"Unknown tool '{name}'. Available tools: {available}")
        return self._tools[name].handler(tool_input)

    def descriptions(self) -> list[str]:
        return [f"{tool.name}: {tool.description}" for tool in self._tools.values()]

    @property
    def names(self) -> set[str]:
        return set(self._tools)


def _safe_eval_expression(expression: str) -> str:
    """Safely evaluate a small arithmetic expression."""

    allowed_bin_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    allowed_unary_ops = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def eval_node(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_bin_ops:
            left = eval_node(node.left)
            right = eval_node(node.right)
            return allowed_bin_ops[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary_ops:
            return allowed_unary_ops[type(node.op)](eval_node(node.operand))
        raise ValueError("Unsupported expression. Use only numbers and arithmetic operators.")

    tree = ast.parse(expression, mode="eval")
    result = eval_node(tree)
    if result.is_integer():
        return str(int(result))
    return str(result)


def calculator_tool(tool_input: str) -> str:
    expression = tool_input.strip()
    if not expression:
        raise ValueError("Calculator input is empty.")
    return _safe_eval_expression(expression)


def current_time_tool(_: str) -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text_file_tool(tool_input: str) -> str:
    raw_path = tool_input.strip().strip("\"'")
    if not raw_path:
        raise ValueError("read_text_file requires a path.")

    candidate = Path(raw_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (WORKSPACE_ROOT / candidate).resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {resolved}")
    if WORKSPACE_ROOT != resolved and WORKSPACE_ROOT not in resolved.parents:
        raise PermissionError("Path must stay inside the project workspace.")

    if resolved.stat().st_size > 50_000:
        raise ValueError("File is too large for this demo tool (limit: 50 KB).")

    return resolved.read_text(encoding="utf-8")


def build_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="calculator",
            description="Evaluate a basic arithmetic expression like '(12 * 7) - 4'.",
            handler=calculator_tool,
        )
    )
    registry.register(
        Tool(
            name="current_time",
            description="Return current time in UTC (ISO-8601).",
            handler=current_time_tool,
        )
    )
    registry.register(
        Tool(
            name="read_text_file",
            description="Read a UTF-8 text file from the current workspace.",
            handler=read_text_file_tool,
        )
    )
    return registry
