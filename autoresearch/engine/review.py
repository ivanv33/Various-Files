"""`review_proposals`: the reviewer graph (spec 5). M5 stub: finds the session's open proposals.

M7 adds the structured accept/reject call per proposal, the catalog / rubric edits, the frontmatter update
and the commit. Until then the graph is read-only, so `langgraph dev` can list and run it safely.
"""

from __future__ import annotations

import re
from typing import Any

from langgraph.func import entrypoint

from engine.config import Settings
from engine.tasks import git_ops
from engine.workspace import Workspace

PROPOSALS_DIR = "proposals"
_STATUS = re.compile(r"^status:\s*(\S+)\s*$", re.M)
_FRONTMATTER = re.compile(r"\A\s*---[ \t]*\n(.*?)\n---", re.S)


def proposal_status(text: str) -> str:
    """`status:` from the frontmatter; `open` when absent (an unlabeled proposal still needs a decision)."""
    m = _FRONTMATTER.match(text)
    if not m:
        return "open"
    s = _STATUS.search(m.group(1))
    return s.group(1).strip().lower() if s else "open"


def list_proposals(ws: Workspace) -> tuple[list[str], list[str]]:
    """`(open, decided)` repo-relative paths of `proposals/*.md`, sorted by name."""
    folder = ws.path(PROPOSALS_DIR)
    if not folder.is_dir():
        return [], []
    open_, decided = [], []
    for p in sorted(folder.glob("*.md")):
        rel = ws.rel(f"{PROPOSALS_DIR}/{p.name}")
        (open_ if proposal_status(p.read_text(encoding="utf-8")) == "open" else decided).append(rel)
    return open_, decided


def run_review(inputs: dict[str, Any]) -> dict[str, Any]:
    branch = str(inputs["branch"])
    ws = git_ops.ensure_workspace(branch, Settings.from_env())
    open_, decided = list_proposals(ws)
    return {
        "branch": branch,
        "head": git_ops.git(ws.root, "rev-parse", "HEAD"),
        "open": open_,
        "decided": decided,
        "note": "review decisions are not implemented yet (plan M7); nothing was changed",
    }


review_proposals = entrypoint()(run_review)
