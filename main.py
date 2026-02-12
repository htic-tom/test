"""
Backwards-compatible entrypoint.

Prefer running:
  python -m simple_agentic_ai run
"""

from simple_agentic_ai.__main__ import main


if __name__ == "__main__":
    raise SystemExit(main())
