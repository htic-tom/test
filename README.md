# Simple Agentic AI Project

A minimal Python starter project that demonstrates an **agentic loop**:

1. Interpret a goal
2. Choose a tool
3. Execute the tool
4. Observe output
5. Produce a final answer

This project is intentionally lightweight and requires no external API keys.

## Features

- Rule-based "brain" (`RuleBasedBrain`) that plans one step at a time
- Tool registry with built-in tools:
  - `calculator` (safe arithmetic)
  - `get_time` (current local datetime)
  - `list_files` (directory listing)
  - `read_file` (read UTF-8 text files)
  - `echo` (fallback)
- CLI entry point for single runs or interactive mode

## Project Structure

```text
.
├── main.py
└── simple_agentic_ai
    ├── __init__.py
    ├── agent.py
    ├── brain.py
    ├── models.py
    └── tools.py
```

## Requirements

- Python 3.10+

## Quick Start

Run a single goal:

```bash
python3 main.py --goal "what time is it?" --trace
```

Arithmetic example:

```bash
python3 main.py --goal "calculate 25 * 4 + 10" --trace
```

Interactive mode:

```bash
python3 main.py --interactive --trace
```

## Notes

- This is a starter project meant to be easy to extend.
- You can add your own tools in `simple_agentic_ai/tools.py` and expand planning behavior in `simple_agentic_ai/brain.py`.
