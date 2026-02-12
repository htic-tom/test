"""Tests for the simple agentic AI implementation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from simple_agentic_ai import build_default_agent


class SimpleAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = build_default_agent()

    def test_calculation_goal_uses_calculator_tool(self) -> None:
        result = self.agent.run("calculate 2 * (3 + 4)")
        self.assertIn("14", result.final_answer)
        self.assertEqual(result.memory.tool_results()[0].payload["tool_name"], "calculator")

    def test_time_goal_uses_now_tool(self) -> None:
        result = self.agent.run("what time is it?")
        self.assertIn("Result from now_iso:", result.final_answer)
        self.assertIn("T", result.final_answer)

    def test_list_files_goal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "a.txt").write_text("hello", encoding="utf-8")
            result = self.agent.run(f'list files in "{path}"')
        self.assertIn("a.txt", result.final_answer)

    def test_read_file_goal(self) -> None:
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as temp_file:
            temp_file.write("agentic test file")
            temp_path = temp_file.name
        try:
            result = self.agent.run(f'read file "{temp_path}"')
        finally:
            Path(temp_path).unlink(missing_ok=True)
        self.assertIn("agentic test file", result.final_answer)

    def test_unknown_goal_returns_guidance(self) -> None:
        result = self.agent.run("tell me a joke about robots")
        self.assertIn("could not identify a tool-based plan", result.final_answer.lower())


if __name__ == "__main__":
    unittest.main()
