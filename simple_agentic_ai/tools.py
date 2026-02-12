from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import ast
import operator
from typing import Callable, Iterable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Callable[[str], str]


class ToolRegistry:
    def __init__(self, tools: Iterable[Tool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def list_tool_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def call(self, name: str, arg: str) -> str:
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Unknown tool: {name}")
        return tool.handler(arg)


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator_tool(expression: str) -> str:
    allowed_chars = set("0123456789.+-*/() ")
    if not expression or any(char not in allowed_chars for char in expression):
        raise ValueError("Expression contains unsupported characters")

    parsed = ast.parse(expression, mode="eval")
    result = _safe_eval(parsed)
    as_int = int(result)
    return str(as_int) if as_int == result else str(result)


def time_tool(_: str) -> str:
    now = datetime.now(timezone.utc)
    return now.isoformat()


def echo_tool(text: str) -> str:
    return text


def default_tools() -> list[Tool]:
    return [
        Tool(
            name="calculator",
            description="Evaluates arithmetic expressions like 2 + 2 * 3",
            handler=calculator_tool,
        ),
        Tool(
            name="current_time",
            description="Returns the current UTC timestamp",
            handler=time_tool,
        ),
        Tool(name="echo", description="Returns text unchanged", handler=echo_tool),
    ]
