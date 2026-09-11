"""`engine/review.py`: the `review_proposals` entrypoint (M5 stub: lists open proposals; decisions are M7)."""

from __future__ import annotations

from pathlib import Path

from tests.conftest import SESSION_REL, git

OPEN = "---\nstatus: open\nexperiment: 2\n---\n# New framework: foo\n"
ACCEPTED = "---\nstatus: accepted\nexperiment: 1\n---\n# Rubric change: bar\n"


def push_proposals(origin: str, branch: str, work: Path) -> None:
    clone = work / "proposer"
    git(work, "clone", "-q", "--branch", branch, origin, str(clone))
    props = clone / SESSION_REL / "proposals"
    props.mkdir()
    (props / "new-framework-foo.md").write_text(OPEN, encoding="utf-8")
    (props / "rubric-change-bar.md").write_text(ACCEPTED, encoding="utf-8")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "two proposals")
    git(clone, "push", "-q", "origin", branch)


def test_review_lists_open_proposals_only(settings, origin, session_branch, tmp_path):
    from engine import review
    from langgraph.pregel import Pregel

    push_proposals(origin, session_branch, tmp_path)
    assert isinstance(review.review_proposals, Pregel)
    out = review.review_proposals.invoke({"branch": session_branch})
    assert out["branch"] == session_branch
    assert out["open"] == [f"{SESSION_REL}/proposals/new-framework-foo.md"]
    assert out["decided"] == [f"{SESSION_REL}/proposals/rubric-change-bar.md"]
    assert out["head"] == git(Path(origin.removeprefix("file://")), "rev-parse", session_branch)


def test_review_with_no_proposals_folder(settings, session_branch):
    from engine import review

    out = review.review_proposals.invoke({"branch": session_branch})
    assert out["open"] == [] and out["decided"] == []
