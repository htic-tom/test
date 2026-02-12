from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


@dataclass(slots=True)
class Tool:
    """A callable capability the agent can choose."""

    name: str
    description: str
    handler: Callable[[dict[str, Any]], str]

    def run(self, payload: dict[str, Any]) -> str:
        return self.handler(payload)


def _evaluate_expression(expression: str) -> float:
    if not expression.strip():
        raise ValueError("Expression is empty.")

    tree = ast.parse(expression, mode="eval")
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.FloorDiv,
        ast.USub,
        ast.UAdd,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Unsupported expression element: {type(node).__name__}")
    value = eval(compile(tree, "<calculator>", "eval"), {"__builtins__": {}}, {})
    return float(value)


def calculator_tool(payload: dict[str, Any]) -> str:
    expression = str(payload.get("expression", "")).strip()
    value = _evaluate_expression(expression)
    if value.is_integer():
        return str(int(value))
    return str(value)


def clock_tool(_: dict[str, Any]) -> str:
    return datetime.now().isoformat(timespec="seconds")


def echo_tool(payload: dict[str, Any]) -> str:
    return str(payload.get("text", ""))


def list_files_tool(payload: dict[str, Any]) -> str:
    raw_path = str(payload.get("path", ".")).strip() or "."
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        return f"Path not found: {path}"
    if not path.is_dir():
        return f"Not a directory: {path}"

    entries = sorted(item.name for item in path.iterdir())
    if not entries:
        return f"{path} is empty."

    preview = entries[:30]
    output = "\n".join(preview)
    if len(entries) > len(preview):
        output += f"\n... ({len(entries) - len(preview)} more)"
    return output


def read_file_tool(payload: dict[str, Any]) -> str:
    raw_path = str(payload.get("path", "")).strip()
    if not raw_path:
        return "No file path provided."

    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        return f"File not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "File is not valid UTF-8 text."

    text = text.strip()
    if not text:
        return "File is empty."

    max_chars = 2000
    if len(text) > max_chars:
        return text[:max_chars] + "\n...[truncated]"
    return text


def build_default_tools() -> dict[str, Tool]:
    return {
        "calculator": Tool(
            name="calculator",
            description="Evaluate a basic arithmetic expression.",
            handler=calculator_tool,
        ),
        "get_time": Tool(
            name="get_time",
            description="Get current local datetime.",
            handler=clock_tool,
        ),
        "list_files": Tool(
            name="list_files",
            description="List file and folder names in a directory.",
            handler=list_files_tool,
        ),
        "read_file": Tool(
            name="read_file",
            description="Read UTF-8 text from a local file.",
            handler=read_file_tool,
        ),
        "echo": Tool(
            name="echo",
            description="Repeat user text.",
            handler=echo_tool,
        ),
    }
