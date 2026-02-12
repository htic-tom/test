from __future__ import annotations

from pathlib import Path
import unittest

from agentic_ai import SimpleAgent


class SimpleAgentTests(unittest.TestCase):
    def test_handles_arithmetic_goal(self) -> None:
        agent = SimpleAgent(max_steps=6)
        result = agent.run("What is 19 * 7?")

        self.assertIn("133", str(result["answer"]))
        self.assertGreaterEqual(int(result["steps_used"]), 1)

    def test_handles_time_goal(self) -> None:
        agent = SimpleAgent(max_steps=6)
        result = agent.run("Tell me the current UTC time.")

        self.assertIn("current_time", str(result["answer"]))

    def test_reads_quoted_file_path(self) -> None:
        workspace = Path(__file__).resolve().parents[1]
        sample = workspace / "sample_note.txt"
        sample.write_text("hello from test\n", encoding="utf-8")
        try:
            agent = SimpleAgent(max_steps=6)
            result = agent.run('Summarize this file: "sample_note.txt"')
            self.assertIn("hello from test", str(result["answer"]))
        finally:
            if sample.exists():
                sample.unlink()


if __name__ == "__main__":
    unittest.main()
