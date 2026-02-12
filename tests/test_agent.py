import unittest

from simple_agentic_ai import RuleBasedPlanner, SimpleAgent, ToolRegistry, default_tools


def build_agent() -> SimpleAgent:
    return SimpleAgent(
        planner=RuleBasedPlanner(),
        tools=ToolRegistry(default_tools()),
    )


class TestSimpleAgent(unittest.TestCase):
    def test_calculator_tool_flow(self) -> None:
        result = build_agent().run("calculate 7 + 5")
        self.assertIn("12", result.response)
        self.assertEqual(result.trace[0]["tool"], "calculator")

    def test_time_tool_flow(self) -> None:
        result = build_agent().run("what time is it?")
        self.assertIn("Tool `current_time` returned:", result.response)
        self.assertEqual(result.trace[0]["tool"], "current_time")

    def test_fallback_without_tool(self) -> None:
        result = build_agent().run("tell me a poem")
        self.assertIn("I can use tools", result.response)
        self.assertEqual(result.trace, [])


if __name__ == "__main__":
    unittest.main()
