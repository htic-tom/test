"""Tool registry and built-in tools."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


ToolHandler = Callable[..., str]


@dataclass(frozen=True)
class Tool:
    """A named capability that the agent can call."""

    name: str
    description: str
    handler: ToolHandler


class ToolRegistry:
    """Container for tools and safe execution wrappers."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> list[Tool]:
        return sorted(self._tools.values(), key=lambda tool: tool.name)

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def run(self, tool_name: str, **kwargs: object) -> str:
        if tool_name not in self._tools:
            available = ", ".join(sorted(self._tools))
            raise ValueError(f"Unknown tool '{tool_name}'. Available tools: {available}")
        return self._tools[tool_name].handler(**kwargs)


_ALLOWED_BINARY_OPERATORS: dict[type[ast.AST], Callable[[float, float], float]] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a**b,
}

_ALLOWED_UNARY_OPERATORS: dict[type[ast.AST], Callable[[float], float]] = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
}


def _evaluate_numeric_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_numeric_ast(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_BINARY_OPERATORS:
            raise ValueError("Unsupported binary operator.")
        left = _evaluate_numeric_ast(node.left)
        right = _evaluate_numeric_ast(node.right)
        return _ALLOWED_BINARY_OPERATORS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARY_OPERATORS:
            raise ValueError("Unsupported unary operator.")
        value = _evaluate_numeric_ast(node.operand)
        return _ALLOWED_UNARY_OPERATORS[op_type](value)
    raise ValueError("Expression includes unsupported syntax.")


def calculator(expression: str) -> str:
    """Safely evaluates a math expression containing numeric operators."""

    source = expression.strip()
    if not source:
        raise ValueError("Expression must not be empty.")
    parsed = ast.parse(source, mode="eval")
    result = _evaluate_numeric_ast(parsed)
    if result.is_integer():
        return str(int(result))
    return str(result)


def now_iso() -> str:
    """Returns the current UTC date/time in ISO format."""

    return datetime.now(timezone.utc).isoformat()


def list_directory(path: str = ".") -> str:
    """Lists files and folders in a directory."""

    directory = Path(path).expanduser()
    if not directory.exists():
        raise FileNotFoundError(f"Path does not exist: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    entries = sorted(directory.iterdir(), key=lambda item: item.name.lower())
    if not entries:
        return "(empty directory)"
    output_lines: list[str] = []
    for item in entries[:100]:
        suffix = "/" if item.is_dir() else ""
        output_lines.append(f"{item.name}{suffix}")
    if len(entries) > 100:
        output_lines.append(f"... and {len(entries) - 100} more")
    return "\n".join(output_lines)


def read_text_file(path: str, max_chars: int = 4000) -> str:
    """Reads a UTF-8 text file and truncates long output."""

    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    if not file_path.is_file():
        raise IsADirectoryError(f"Expected a file path, got directory: {file_path}")
    text = file_path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}\n\n[truncated to {max_chars} characters]"


def build_default_registry() -> ToolRegistry:
    """Creates a tool registry with a small practical toolset."""

    registry = ToolRegistry()
    registry.register(Tool(name="calculator", description="Evaluate a math expression.", handler=calculator))
    registry.register(Tool(name="now_iso", description="Get current UTC timestamp.", handler=now_iso))
    registry.register(
        Tool(
            name="list_directory",
            description="List files in a directory. Optional arg: path.",
            handler=list_directory,
        )
    )
    registry.register(
        Tool(
            name="read_text_file",
            description="Read UTF-8 text from a file. Required arg: path.",
            handler=read_text_file,
        )
    )
    return registry
