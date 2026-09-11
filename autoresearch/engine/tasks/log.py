"""`experiments.tsv` rows (one per attempt) and the digest handed to `interrupt()`.

Columns: n, timestamp, frameworks (`+`-joined slugs), candidate_total, incumbent_total,
kept (1 / 0 / error), note (one line). Append-only; `n_experiments` = number of data rows.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

COLUMNS = ["n", "timestamp", "frameworks", "candidate_total", "incumbent_total", "kept", "note"]
HEADER = "\t".join(COLUMNS)
TSV_NAME = "experiments.tsv"
KEPT_VALUES = ("1", "0", "error")

_WS = re.compile(r"[\t\r\n]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(value: str) -> int | None:
    value = value.strip()
    if value == "":
        return None
    return int(float(value))


class LogRow(BaseModel):
    n: int
    timestamp: str = Field(default_factory=utc_now)
    frameworks: list[str] = Field(default_factory=list)
    candidate_total: int | None = None
    incumbent_total: int | None = None
    kept: str
    note: str = ""

    @field_validator("kept", mode="before")
    @classmethod
    def _coerce_kept(cls, value: Any) -> str:
        if isinstance(value, bool):
            return "1" if value else "0"
        value = str(value).strip()
        if value not in KEPT_VALUES:
            raise ValueError(f"kept must be one of {KEPT_VALUES}, got {value!r}")
        return value

    @field_validator("note", mode="before")
    @classmethod
    def _one_line(cls, value: Any) -> str:
        return _WS.sub(" ", str(value or "")).strip()

    @field_validator("frameworks", mode="before")
    @classmethod
    def _split_frameworks(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [s for s in value.split("+") if s]
        return list(value or [])

    def to_tsv_line(self) -> str:
        return "\t".join(
            [
                str(self.n),
                self.timestamp,
                "+".join(self.frameworks),
                "" if self.candidate_total is None else str(self.candidate_total),
                "" if self.incumbent_total is None else str(self.incumbent_total),
                self.kept,
                self.note,
            ]
        )

    @classmethod
    def from_tsv_line(cls, line: str) -> "LogRow":
        parts = line.rstrip("\r\n").split("\t")
        if len(parts) < len(COLUMNS):
            parts += [""] * (len(COLUMNS) - len(parts))
        n, timestamp, frameworks, cand, inc, kept, *note = parts
        return cls(
            n=int(n),
            timestamp=timestamp,
            frameworks=frameworks,
            candidate_total=_num(cand),
            incumbent_total=_num(inc),
            kept=kept,
            note="\t".join(note),
        )


def parse_tsv(text: str) -> list[LogRow]:
    """Data rows of an `experiments.tsv`; blank lines and header lines (first cell `n`) are skipped wherever they are."""
    rows: list[LogRow] = []
    for line in text.splitlines():
        if not line.strip() or line.split("\t")[0].strip() == COLUMNS[0]:
            continue
        rows.append(LogRow.from_tsv_line(line))
    return rows


def render_tsv(rows: list[LogRow]) -> str:
    return "".join([HEADER + "\n"] + [r.to_tsv_line() + "\n" for r in rows])


def tsv_path(root: Path | str, session_rel: str) -> Path:
    return Path(root) / session_rel / TSV_NAME


def read_rows(root: Path | str, session_rel: str) -> list[LogRow]:
    path = tsv_path(root, session_rel)
    if not path.exists():
        return []
    return parse_tsv(path.read_text(encoding="utf-8"))


def append_row(root: Path | str, session_rel: str, row: LogRow) -> Path:
    path = tsv_path(root, session_rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8").strip() == "":
        path.write_text(HEADER + "\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + row.to_tsv_line() + "\n", encoding="utf-8")
    return path


RESUME_HELP = (
    'Resume with {"action": "continue" | "stop", "steer": "<optional free text appended to '
    "notes.md under '## Human steering'>\"}"
)


def _plain(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def digest(kind: str, **facts: Any) -> dict[str, Any]:
    """A JSON-serializable summary for `interrupt()`; `kind` is checkpoint0 | new_best."""
    return {"kind": kind, **_plain(facts), "resume": RESUME_HELP}
