"""Promote a kept attempt: `attempts/<n>/*` -> `best/`, plus `best/score.json` (refinement 7 shape).

`best/` is replaced wholesale so files from an earlier best cannot linger; `attempts/` is left
alone (scratch, never staged). Plain function; the loop wraps it in a `@task`.
"""

from __future__ import annotations

import json
import shutil
from typing import Any

from pydantic import BaseModel

from engine.tasks.judge import Verdict
from engine.workspace import Workspace

REQUIRED = ("combination-with-explanations.md", "decomposition.md", "recommendations.md")
SCORE_NAME = "score.json"


class PromoteError(RuntimeError):
    """The attempt directory is missing one of the judged files; nothing was written."""


def promote(ws: Workspace, n: int, verdict: Verdict | BaseModel | dict[str, Any]) -> list[str]:
    """Copy every file in `attempts/<n>/` into `best/` and write `best/score.json`; return repo-relative paths written."""
    src = ws.attempt_dir(n)
    if not src.is_dir():
        raise PromoteError(f"no attempt directory: {ws.attempt_rel(n, '')}")
    missing = [name for name in REQUIRED if not ws.has(f"attempts/{n}/{name}")]
    if missing:
        raise PromoteError(f"attempt {n} lacks {', '.join(missing)}")
    if isinstance(verdict, BaseModel):
        score = verdict.model_dump(mode="json")
    else:
        score = Verdict.model_validate(verdict).model_dump(mode="json")

    best = ws.path("best")
    if best.exists():
        shutil.rmtree(best)
    best.mkdir(parents=True)
    written: list[str] = []
    for p in sorted(src.iterdir()):
        if p.is_file():
            shutil.copyfile(p, best / p.name)
            written.append(ws.rel(f"best/{p.name}"))
    ws.write(f"best/{SCORE_NAME}", json.dumps(score, indent=2, ensure_ascii=False) + "\n")
    written.append(ws.rel(f"best/{SCORE_NAME}"))
    return written
