# Simple Agentic AI Project

This repository contains a small, dependency-free example of an **agentic AI loop** in Python.

The project demonstrates:

- A planner that decides whether to use a tool or return a final response
- A tool registry with pluggable tools
- An execution loop that records tool-call trace
- A CLI for one-shot and interactive usage

## Project structure

```text
.
├── main.py
├── simple_agentic_ai
│   ├── __init__.py
│   ├── agent.py
│   ├── planner.py
│   └── tools.py
└── tests
    └── test_agent.py
```

## Requirements

- Python 3.10+

## Run the demo

### One-shot mode

```bash
python main.py "calculate 4 * (2 + 3)" --trace
```

### Interactive mode

```bash
python main.py --trace
```

Example prompts:

- `calculate 12 / (3 + 1)`
- `what is the time right now?`
- `echo hello from the agent`

## Run tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
