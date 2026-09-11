"""One markdown prompt per step (`propose.md`, `judge.md`, ...), loaded by name.

Templates use `str.format` placeholders (`{mission}`); keep other braces out of the files.
"""

from __future__ import annotations

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"no prompt named {name!r} in {PROMPTS_DIR}")
    return path.read_text(encoding="utf-8")
