"""`scripts/new_session.py`: create a session branch from master on a temp origin and push it."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.catalog import load_seed_catalog
from engine.tasks.log import HEADER
from scripts.new_session import NOTES_SKELETON, SessionError, create_session, main
from tests.conftest import TRANSCRIPT_REL, git


def _clone_branch(remote: str, branch: str, dest: Path) -> Path:
    git(dest.parent, "clone", "-q", "--branch", branch, remote, str(dest))
    return dest


def test_create_session_creates_branch_from_master_with_skeleton(origin: str, tmp_path: Path):
    master_before = git(tmp_path, "ls-remote", origin, "refs/heads/master").split()[0]

    result = create_session(
        "demo",
        mission="Ship a great product",
        transcript_path=TRANSCRIPT_REL,
        max_experiments=3,
        remote=origin,
        workdir=tmp_path / "work",
    )

    assert result["branch"] == "autoresearch/demo"
    assert result["session_rel"] == "autoresearch/sessions/demo"
    assert len(result["sha"]) == 40

    heads = dict(
        (line.split()[1], line.split()[0]) for line in git(tmp_path, "ls-remote", "--heads", origin).splitlines()
    )
    assert heads["refs/heads/autoresearch/demo"] == result["sha"]
    assert heads["refs/heads/master"] == master_before, "master must not move"

    clone = _clone_branch(origin, "autoresearch/demo", tmp_path / "check")
    # branch is one commit ahead of master
    assert git(clone, "rev-parse", "HEAD~1") == master_before
    session = clone / "autoresearch/sessions/demo"
    assert json.loads((session / "metadata.json").read_text()) == {
        "mission": "Ship a great product",
        "transcript_path": TRANSCRIPT_REL,
        "max_experiments": 3,
    }
    assert (session / "experiments.tsv").read_text() == HEADER + "\n"
    notes = (session / "notes.md").read_text()
    assert notes == NOTES_SKELETON
    assert "## Insights" in notes and "## Human steering" in notes
    assert json.loads((session / "catalog.json").read_text()) == load_seed_catalog()
    assert not (session / "rubric.md").exists()
    assert not (session / "best").exists()
    # only the session folder was added
    changed = git(clone, "diff", "--name-only", "HEAD~1", "HEAD").splitlines()
    assert changed == sorted(
        f"autoresearch/sessions/demo/{name}" for name in ("catalog.json", "experiments.tsv", "metadata.json", "notes.md")
    )
    # scratch clone is removed by default
    assert not (tmp_path / "work").exists() or not any((tmp_path / "work").iterdir())


def test_create_session_result_workspace_is_usable_by_ensure_workspace(origin: str, tmp_path: Path, settings):
    from engine.tasks.git_ops import ensure_workspace

    create_session(
        "demo",
        mission="m",
        transcript_path=TRANSCRIPT_REL,
        max_experiments=2,
        remote=origin,
        workdir=tmp_path / "work",
    )
    ws = ensure_workspace("autoresearch/demo", settings)
    assert ws.mission == "m"
    assert ws.max_experiments == 2
    assert ws.n_experiments() == 0
    assert not ws.has("rubric.md")
    assert len(json.loads(ws.read("catalog.json"))) == 22


def test_create_session_rejects_missing_transcript_without_pushing(origin: str, tmp_path: Path):
    with pytest.raises(SessionError, match="transcript"):
        create_session(
            "demo",
            mission="m",
            transcript_path="tbpn-transcripts/transcripts/does-not-exist.md",
            max_experiments=1,
            remote=origin,
            workdir=tmp_path / "work",
        )
    assert "autoresearch/demo" not in git(tmp_path, "ls-remote", "--heads", origin)


def test_create_session_rejects_existing_branch(origin: str, tmp_path: Path):
    kwargs = dict(mission="m", transcript_path=TRANSCRIPT_REL, max_experiments=1, remote=origin)
    create_session("demo", workdir=tmp_path / "w1", **kwargs)
    with pytest.raises(SessionError, match="already exists"):
        create_session("demo", workdir=tmp_path / "w2", **kwargs)


@pytest.mark.parametrize("bad", ["", "Has Space", "UPPER", "a/b", "-lead", "trail-", "dots.too"])
def test_create_session_rejects_bad_slugs(origin: str, tmp_path: Path, bad: str):
    with pytest.raises(SessionError, match="slug"):
        create_session(bad, mission="m", transcript_path=TRANSCRIPT_REL, max_experiments=1, remote=origin, workdir=tmp_path)


def test_create_session_rejects_non_positive_max_experiments(origin: str, tmp_path: Path):
    with pytest.raises(SessionError, match="max_experiments"):
        create_session("demo", mission="m", transcript_path=TRANSCRIPT_REL, max_experiments=0, remote=origin, workdir=tmp_path)


def test_cli_main_uses_git_remote_env_and_prints_branch(origin: str, tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("GIT_REMOTE", origin)
    monkeypatch.setenv("AUTORESEARCH_WORKDIR", str(tmp_path / "ws"))
    rc = main(
        [
            "cli-demo",
            "--mission",
            "Find the next move",
            "--transcript",
            TRANSCRIPT_REL,
            "--max-experiments",
            "4",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "autoresearch/cli-demo" in out
    assert "refs/heads/autoresearch/cli-demo" in git(tmp_path, "ls-remote", "--heads", origin)


def test_cli_main_reports_errors_and_returns_nonzero(origin: str, tmp_path: Path, monkeypatch, capsys):
    # empty (not deleted): `main()` loads `.env` without override, so a present-but-empty value wins
    monkeypatch.setenv("GIT_REMOTE", "")
    rc = main(["demo", "--mission", "m", "--transcript", TRANSCRIPT_REL, "--max-experiments", "1"])
    assert rc == 2
    assert "GIT_REMOTE" in capsys.readouterr().err
