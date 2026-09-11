"""`review_proposals`: the reviewer graph (spec 5), run on demand from Studio or the API.

`ensure_workspace(branch)` (plain), then for each `proposals/*.md` with `status: open`, in name order: one
structured accept/reject decision (`decide_step`, a model call unless a deterministic check settles it) and
its application (`apply_step`: catalog entry, or rubric re-render + `## Rubric changes` note, plus the
proposal's frontmatter). One commit for the whole review. A proposal whose decision failed stays open and
is reported under `errors`; the others are still applied and committed. No row is added to `experiments.tsv`.
"""

from __future__ import annotations

from typing import Any

from langgraph.func import entrypoint, task

from engine.config import Settings, make_model
from engine.tasks import git_ops, proposals
from engine.workspace import Workspace


@task
def decide_step(root: str, branch: str, file: str) -> dict[str, Any]:
    return proposals.decide(make_model(), Workspace(root, branch), file)


@task
def apply_step(root: str, branch: str, decision: dict[str, Any]) -> dict[str, Any]:
    return proposals.apply_decision(Workspace(root, branch), decision)


@task
def commit_push_step(root: str, branch: str, message: str) -> str | None:
    return git_ops.commit_push(root, branch, message)


def commit_subject(n: int, accepted: int, rejected: int, errors: int) -> str:
    noun = "proposal" if n == 1 else "proposals"
    tail = f", {errors} error{'s' if errors != 1 else ''}" if errors else ""
    return f"review: {n} {noun} ({accepted} accepted, {rejected} rejected{tail})"


def run_review(inputs: dict[str, Any]) -> dict[str, Any]:
    branch = str(inputs["branch"])
    ws = git_ops.ensure_workspace(branch, Settings.from_env())
    root = str(ws.root)
    open_, _decided = proposals.list_proposals(ws)
    decisions: list[dict[str, Any]] = []
    for file in open_:
        decided = decide_step(root, branch, file).result()
        applied = apply_step(root, branch, decided).result()
        decisions.append({"file": file, "kind": decided["kind"], "status": applied["status"], "reason": decided["reason"]})
    accepted = sum(d["status"] == proposals.STATUS_ACCEPTED for d in decisions)
    rejected = sum(d["status"] == proposals.STATUS_REJECTED for d in decisions)
    errors = sum(d["status"] == proposals.STATUS_OPEN for d in decisions)
    sha = commit_push_step(root, branch, commit_subject(len(open_), accepted, rejected, errors)).result() if open_ else None
    still_open, decided_now = proposals.list_proposals(ws)
    return {
        "branch": branch,
        "head": git_ops.git(ws.root, "rev-parse", "HEAD"),
        "sha": sha,
        "decisions": decisions,
        "accepted": accepted,
        "rejected": rejected,
        "errors": errors,
        "open": still_open,
        "decided": decided_now,
    }


review_proposals = entrypoint()(run_review)
