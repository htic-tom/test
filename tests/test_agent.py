from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from simple_agentic_ai.agent import SimpleAgent
from simple_agentic_ai.brain import RuleBasedBrain
from simple_agentic_ai.tools import build_default_tools


class SimpleAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = SimpleAgent(brain=RuleBasedBrain(), tools=build_default_tools())

    def test_calculator_goal(self) -> None:
        result = self.agent.run("calculate 6 * 7", max_steps=4)
        self.assertIn("42", result.final_answer)

    def test_time_goal(self) -> None:
        result = self.agent.run("what time is it?", max_steps=4)
        self.assertIn("Based on the tool output", result.final_answer)

    def test_read_file_goal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "note.txt"
            file_path.write_text("hello agent", encoding="utf-8")

            result = self.agent.run(f"read {file_path}", max_steps=4)
            self.assertIn("hello agent", result.final_answer)


if __name__ == "__main__":
    unittest.main()
