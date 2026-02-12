from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Memory:
    """
    Very small persistence layer.
    Stored as JSON like:
      { "notes": [ {"text": "...", "ts": "..."} ] }
    """

    path: Path
    data: dict[str, Any] = field(default_factory=lambda: {"notes": []})

    def load(self) -> None:
        if not self.path.exists():
            return
        raw = self.path.read_text(encoding="utf-8").strip()
        if not raw:
            return
        self.data = json.loads(raw)
        if "notes" not in self.data or not isinstance(self.data["notes"], list):
            self.data["notes"] = []

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def add_note(self, text: str, ts: str) -> dict[str, Any]:
        note = {"text": text, "ts": ts}
        self.data.setdefault("notes", [])
        self.data["notes"].append(note)
        self.save()
        return note

    def list_notes(self, limit: int = 20) -> list[dict[str, Any]]:
        notes = self.data.get("notes", [])
        if not isinstance(notes, list):
            return []
        return notes[-limit:]

