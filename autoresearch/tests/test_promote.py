"""`engine/tasks/promote.py`: attempts/<n>/* -> best/ plus best/score.json (refinement 7 shape)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.tasks.judge import Verdict
from engine.tasks.promote import PromoteError, promote
from engine.workspace import Workspace

BRANCH = "autoresearch/demo"
FILES = {
    "combination-with-explanations.md": "---\nframeworks: [swot]\nnote: n\n---\n# combo\n",
    "decomposition.md": "# decomposition\n",
    "recommendations.md": "# recommendations\n",
}


def verdict(n: int = 2) -> Verdict:
    return Verdict(
        experiment=n,
        judge_model="fake",
        order=["incumbent", "candidate"],
        candidate={"specificity": 8, "grounding": 7},
        incumbent={"specificity": 4, "grounding": 5},
        candidate_total=15,
        incumbent_total=9,
        rationale="sharper",
    )


def fill_attempt(ws: Workspace, n: int) -> None:
    for name, text in FILES.items():
        ws.write(f"attempts/{n}/{name}", text)


def test_promote_copies_the_required_files_and_writes_score_json(tmp_path: Path):
    ws = Workspace(tmp_path / "clone", BRANCH)
    fill_attempt(ws, 2)
    ws.write("attempts/2/decomposition-swot.md", "per-framework scratch\n")  # subagent output, never promoted
    ws.write("best/recommendations.md", "# old best\n")
    ws.write("best/score.json", "{}")
    written = promote(ws, 2, verdict(2))
    assert sorted(written) == sorted(ws.rel(f"best/{name}") for name in [*FILES, "score.json"])
    for name, text in FILES.items():
        assert ws.read(f"best/{name}") == text
    assert sorted(p.name for p in ws.path("best").iterdir()) == sorted([*FILES, "score.json"])
    assert not ws.path("best/decomposition-swot.md").exists()
    score = json.loads(ws.read("best/score.json"))
    assert score == verdict(2).model_dump(mode="json")
    assert score["order"] == ["incumbent", "candidate"] and score["experiment"] == 2 and score["judge_model"] == "fake"
    assert score["candidate_total"] == 15 and score["incumbent_total"] == 9
    # attempts/ is left in place (scratch; the loop never stages it)
    assert ws.has("attempts/2/recommendations.md")


def test_promote_without_incumbent_writes_null_incumbent_fields(tmp_path: Path):
    ws = Workspace(tmp_path / "clone", BRANCH)
    fill_attempt(ws, 1)
    promote(ws, 1, Verdict(order=["candidate"], candidate={"specificity": 6}, candidate_total=6, rationale="only one"))
    score = json.loads(ws.read("best/score.json"))
    assert score["incumbent"] is None and score["incumbent_total"] is None and score["candidate_total"] == 6


def test_promote_does_not_leave_stale_best_files_from_a_previous_best(tmp_path: Path):
    ws = Workspace(tmp_path / "clone", BRANCH)
    fill_attempt(ws, 3)
    ws.write("best/extra-from-before.md", "stale\n")
    promote(ws, 3, verdict(3))
    assert not ws.path("best/extra-from-before.md").exists()
    assert ws.has("best/recommendations.md")


def test_promote_requires_the_judged_files(tmp_path: Path):
    ws = Workspace(tmp_path / "clone", BRANCH)
    ws.write("attempts/1/combination-with-explanations.md", "x\n")
    with pytest.raises(PromoteError, match="recommendations.md"):
        promote(ws, 1, verdict(1))
    with pytest.raises(PromoteError, match="attempts/9"):
        promote(ws, 9, verdict(9))
    assert not ws.path("best").exists()  # nothing half-written
