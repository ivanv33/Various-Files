"""`dev/smoke.py` helpers: config rendering, the SDK resume loop (fake client) and the origin checks (temp bare repo)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dev import smoke
from tests.conftest import BRANCH, SESSION_REL, git

# --- smoke_config ---------------------------------------------------------------


def test_smoke_config_replaces_env_with_a_dict_and_keeps_the_rest():
    base = {
        "python_version": "3.13",
        "dependencies": ["."],
        "graphs": {"autoresearch_session": "./engine/loop.py:autoresearch_session"},
        "env": ".env",
        "dockerfile_lines": ["RUN true"],
    }
    env = {"GIT_REMOTE": "file:///tmp/o.git", "AUTORESEARCH_WORKDIR": "/tmp/ws"}
    out = smoke.smoke_config(base, env)
    assert out["env"] == env
    assert {k: v for k, v in out.items() if k != "env"} == {k: v for k, v in base.items() if k != "env"}
    assert base["env"] == ".env"  # input untouched


def test_smoke_config_refuses_secret_keys_in_the_dict():
    with pytest.raises(smoke.SmokeError, match="GOOGLE_API_KEY"):
        smoke.smoke_config({"graphs": {}}, {"GOOGLE_API_KEY": "x", "GIT_REMOTE": "file:///o"})


# --- drive ------------------------------------------------------------------------


class FakeRuns:
    def __init__(self, results):
        self.results = list(results)
        self.calls: list[dict] = []

    def wait(self, thread_id, assistant_id, **kwargs):
        self.calls.append({"thread_id": thread_id, "assistant_id": assistant_id, **kwargs})
        return self.results.pop(0)


class FakeClient:
    def __init__(self, results):
        self.runs = FakeRuns(results)
        self.threads = self

    def create(self):
        return {"thread_id": "t-1"}


def test_drive_resumes_continue_at_every_interrupt_and_returns_the_summary():
    pause0 = {"__interrupt__": [{"value": {"kind": "checkpoint0", "sha": "a1"}}]}
    pause1 = {"__interrupt__": [{"value": {"kind": "new_best", "n": 1, "sha": "b2"}}]}
    final = {"branch": BRANCH, "attempts": 2, "kept": 1, "stopped": "max_experiments"}
    client = FakeClient([pause0, pause1, final])
    seen = []
    out, interrupts = smoke.drive(client, BRANCH, max_resumes=5, log=seen.append)
    assert out == final
    assert [i["kind"] for i in interrupts] == ["checkpoint0", "new_best"]
    calls = client.runs.calls
    assert calls[0]["input"] == {"branch": BRANCH} and calls[0]["assistant_id"] == "autoresearch_session"
    assert calls[1]["command"] == {"resume": {"action": "continue"}} and "input" not in calls[1]
    assert calls[2]["command"] == {"resume": {"action": "continue"}}
    assert all(c["thread_id"] == "t-1" for c in calls)
    assert any("checkpoint0" in line for line in seen)


def test_drive_gives_up_after_max_resumes():
    pause = {"__interrupt__": [{"value": {"kind": "new_best", "n": 1}}]}
    client = FakeClient([pause, pause, pause, pause])
    with pytest.raises(smoke.SmokeError, match="resumes"):
        smoke.drive(client, BRANCH, max_resumes=2)
    assert len(client.runs.calls) == 3  # initial run + 2 resumes


# --- check_origin -----------------------------------------------------------------

TSV = (
    "n\ttimestamp\tframeworks\tcandidate_total\tincumbent_total\tkept\tnote\n"
    "1\t2026-09-10T00:00:00Z\tmece+dialectical-decomposition\t40\t\t1\tseed\n"
    "2\t2026-09-10T00:10:00Z\tsystems-thinking\t30\t40\t0\ttry a systems lens\n"
)
TSV_ERROR = TSV.replace("30\t40\t0\ttry a systems lens", "\t\terror\tRecursionError: limit")


def push_session_history(origin_url: str, work: Path, *, tsv: str, with_score: bool = True) -> Path:
    """Clone the seeded session branch, add checkpoint-0 + two experiment commits like the loop does, push."""
    clone = work / "clone"
    git(work, "clone", "-q", "--branch", BRANCH, origin_url, str(clone))
    session = clone / SESSION_REL
    (session / "best").mkdir(exist_ok=True)

    def commit(subject: str) -> None:
        git(clone, "add", "-A", "--", SESSION_REL)
        git(clone, "commit", "-q", "--allow-empty", "-m", subject)

    (session / "best" / "combination-with-explanations.md").write_text("---\nframeworks: [mece]\n---\nseed\n")
    commit("checkpoint 0 draft: seed combination")
    (session / "rubric.md").write_text("# Rubric\n\n## Core dimensions\n\n### specificity: Specificity\nx\n")
    commit("checkpoint 0: rubric approved")
    if with_score:
        (session / "best" / "recommendations.md").write_text("1. Do the thing.\n")
        (session / "best" / "score.json").write_text(json.dumps({"experiment": 1, "candidate_total": 40, "incumbent_total": None}))
    (session / "experiments.tsv").write_text(tsv.splitlines(keepends=True)[0] + tsv.splitlines(keepends=True)[1])
    commit("exp 1: KEEP 40 vs -")
    (session / "experiments.tsv").write_text(tsv)
    commit("exp 2: discard 30 vs 40" if "error" not in tsv else "exp 2: ERROR RecursionError: limit")
    git(clone, "push", "-q", "origin", BRANCH)
    return clone


def test_check_origin_passes_on_a_healthy_two_experiment_history(origin, session_branch, tmp_path):
    push_session_history(origin, tmp_path, tsv=TSV)
    bare = Path(origin.removeprefix("file://"))
    facts = smoke.check_origin(bare, BRANCH, SESSION_REL, 2)
    assert facts["subjects"][0] == "session demo: bootstrap" and len(facts["subjects"]) == 5  # not master's history
    assert facts["exp_subjects"] == ["exp 1: KEEP 40 vs -", "exp 2: discard 30 vs 40"]
    assert facts["checkpoint_subjects"] == ["checkpoint 0 draft: seed combination", "checkpoint 0: rubric approved"]
    assert [r.kept for r in facts["rows"]] == ["1", "0"]
    assert facts["score"]["candidate_total"] == 40 and facts["score"]["experiment"] == 1
    assert facts["head"] == git(bare, "rev-parse", BRANCH)


def test_check_origin_fails_when_fewer_experiments_landed(origin, session_branch, tmp_path):
    push_session_history(origin, tmp_path, tsv=TSV)
    bare = Path(origin.removeprefix("file://"))
    with pytest.raises(smoke.SmokeError, match="expected 3 'exp n:' commits"):
        smoke.check_origin(bare, BRANCH, SESSION_REL, 3)


def test_check_origin_fails_on_error_rows_unless_allowed(origin, session_branch, tmp_path):
    push_session_history(origin, tmp_path, tsv=TSV_ERROR)
    bare = Path(origin.removeprefix("file://"))
    with pytest.raises(smoke.SmokeError, match="RecursionError"):
        smoke.check_origin(bare, BRANCH, SESSION_REL, 2)
    facts = smoke.check_origin(bare, BRANCH, SESSION_REL, 2, allow_errors=True)
    assert [r.kept for r in facts["rows"]] == ["1", "error"]


def test_check_origin_fails_without_best_score(origin, session_branch, tmp_path):
    push_session_history(origin, tmp_path, tsv=TSV, with_score=False)
    bare = Path(origin.removeprefix("file://"))
    with pytest.raises(smoke.SmokeError, match="score.json"):
        smoke.check_origin(bare, BRANCH, SESSION_REL, 2)
