from __future__ import annotations

import ast
import datetime as dt
from dataclasses import dataclass
from typing import Any, Callable

from .memory import Memory


class ToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any]]


def _safe_eval_expr(expr: str) -> float:
    """
    Safe arithmetic evaluator: supports numbers and + - * / ** ( ) only.
    """

    node = ast.parse(expr, mode="eval")

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Constant,
        ast.Load,
        ast.Mod,
        ast.FloorDiv,
    )

    for n in ast.walk(node):
        if not isinstance(n, allowed_nodes):
            raise ToolError(f"Unsupported expression element: {type(n).__name__}")
        if isinstance(n, ast.Constant) and not isinstance(n.value, (int, float)):
            raise ToolError("Only numeric constants are allowed")

    return float(eval(compile(node, "<expr>", "eval"), {"__builtins__": {}}, {}))


def build_tools(memory: Memory) -> list[Tool]:
    def calculator(args: dict[str, Any]) -> dict[str, Any]:
        expr = str(args.get("expression", "")).strip()
        if not expr:
            raise ToolError("Missing 'expression'")
        value = _safe_eval_expr(expr)
        return {"value": value}

    def time_now(_: dict[str, Any]) -> dict[str, Any]:
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        return {"utc_now": now}

    def write_note(args: dict[str, Any]) -> dict[str, Any]:
        text = str(args.get("text", "")).strip()
        if not text:
            raise ToolError("Missing 'text'")
        ts = dt.datetime.now(dt.timezone.utc).isoformat()
        note = memory.add_note(text=text, ts=ts)
        return {"note": note}

    def list_notes(args: dict[str, Any]) -> dict[str, Any]:
        limit = args.get("limit", 20)
        try:
            limit_i = int(limit)
        except Exception as e:
            raise ToolError("limit must be an integer") from e
        return {"notes": memory.list_notes(limit=limit_i)}

    return [
        Tool(
            name="calculator",
            description="Evaluate a basic arithmetic expression.",
            args_schema={"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
            handler=calculator,
        ),
        Tool(
            name="time_now",
            description="Get the current UTC time as ISO-8601.",
            args_schema={"type": "object", "properties": {}},
            handler=time_now,
        ),
        Tool(
            name="write_note",
            description="Persist a short note to agent memory.",
            args_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
            handler=write_note,
        ),
        Tool(
            name="list_notes",
            description="List recent notes from agent memory.",
            args_schema={"type": "object", "properties": {"limit": {"type": "integer", "default": 20}}},
            handler=list_notes,
        ),
    ]

