# Simple Agentic AI Project

A tiny Python project that demonstrates an **agentic loop**:

1. Think about a goal
2. Select tools
3. Execute tools
4. Observe results
5. Finish with an answer

This version is intentionally lightweight and dependency-free (standard library only).

## Features

- Bounded reasoning loop (`max_steps`)
- Deterministic planner (`RuleBasedPlanner`)
- Built-in tools:
  - `calculator` for arithmetic
  - `current_time` for UTC timestamps
  - `read_text_file` for local workspace text files
- CLI trace mode to inspect agent behavior

## Quickstart

```bash
python main.py "What is (19 * 7) and what time is it in UTC?" --show-trace
```

You can also run in interactive mode:

```bash
python main.py
```

## Project Layout

```text
.
├── agentic_ai
│   ├── __init__.py
│   ├── agent.py
│   └── tools.py
├── tests
│   └── test_agent.py
└── main.py
```

## Run tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Extend it

- Add a new tool in `agentic_ai/tools.py` and register it in `build_default_tool_registry`.
- Replace `RuleBasedPlanner` with an LLM-backed planner later if you want model-driven planning.
