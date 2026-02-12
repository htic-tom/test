# Simple Agentic AI Project

A minimal Python project that demonstrates an **agentic loop**:

1. Understand a goal
2. Plan a next action
3. Call a tool
4. Store result in memory
5. Produce a final answer

This project is intentionally small and easy to extend.

## Features

- Heuristic planner for common goal patterns
- Tool registry with built-in tools:
  - `calculator`
  - `now_iso`
  - `list_directory`
  - `read_text_file`
- Per-run memory and readable execution trace
- CLI mode for one-shot runs and interactive sessions
- Standard-library-only implementation (no runtime dependencies)

## Quickstart

```bash
python3 main.py --goal "calculate 22 * (7 - 2)" --trace
```

Interactive mode:

```bash
python3 main.py --interactive --trace
```

JSON output:

```bash
python3 main.py --goal "what time is it?" --json
```

## Example Goals

- `calculate (15 + 5) / 4`
- `what date is it`
- `list files in .`
- `read file README.md`

## Project Structure

```text
.
├── main.py
├── pyproject.toml
├── simple_agentic_ai
│   ├── __init__.py
│   ├── agent.py
│   ├── memory.py
│   └── tools.py
└── tests
    └── test_agent.py
```

## Run Tests

```bash
python3 -m unittest discover -s tests -v
```

## Extend It

- Add new tools in `simple_agentic_ai/tools.py`
- Add richer planning logic in `simple_agentic_ai/agent.py`
- Persist memory between runs by replacing `ConversationMemory`
