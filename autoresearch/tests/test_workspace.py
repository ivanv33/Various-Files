import json
from pathlib import Path

import pytest

from engine.tasks.log import HEADER, LogRow, append_row
from engine.workspace import SESSIONS_REL, Workspace, WorkspaceError, slug_from_branch

SLUG = "demo"
BRANCH = f"autoresearch/{SLUG}"
SESSION_REL = f"{SESSIONS_REL}/{SLUG}"


def make_root(tmp_path: Path, *, metadata=True, transcript=True, rows=()) -> Path:
    root = tmp_path / "root"
    session = root / SESSION_REL
    session.mkdir(parents=True)
    if metadata:
        (session / "metadata.json").write_text(
            json.dumps(
                {"mission": "m", "transcript_path": "tbpn-transcripts/t.md", "max_experiments": 4}
            )
        )
    if transcript:
        (root / "tbpn-transcripts").mkdir()
        (root / "tbpn-transcripts" / "t.md").write_text("words\n")
    (session / "experiments.tsv").write_text(HEADER + "\n")
    for row in rows:
        append_row(root, SESSION_REL, row)
    return root


def test_slug_from_branch():
    assert slug_from_branch("autoresearch/demo") == "demo"
    with pytest.raises(WorkspaceError):
        slug_from_branch("feature/demo")
    with pytest.raises(WorkspaceError):
        slug_from_branch("autoresearch/")


def test_paths_and_virtual(tmp_path: Path):
    ws = Workspace(make_root(tmp_path), BRANCH)
    assert ws.slug == SLUG
    assert ws.session_rel == SESSION_REL
    assert ws.session_dir == ws.root / SESSION_REL
    assert ws.virtual("best/score.json") == f"/autoresearch/sessions/{SLUG}/best/score.json"
    assert ws.virtual_repo("tbpn-transcripts/t.md") == "/tbpn-transcripts/t.md"
    assert ws.attempt_dir(3) == ws.session_dir / "attempts" / "3"
    assert ws.attempt_rel(3, "decomposition.md") == f"{SESSION_REL}/attempts/3/decomposition.md"
    assert ws.rel("notes.md") == f"{SESSION_REL}/notes.md"


def test_has_read_write(tmp_path: Path):
    ws = Workspace(make_root(tmp_path), BRANCH)
    assert not ws.has("rubric.md")
    ws.write("rubric.md", "# Rubric\n")
    assert ws.has("rubric.md")
    assert ws.read("rubric.md") == "# Rubric\n"
    ws.write("proposals/new-framework-x.md", "---\nstatus: open\n---\n")
    assert (ws.session_dir / "proposals" / "new-framework-x.md").exists()
    assert not ws.has("best/empty.md")
    ws.write("best/empty.md", "")
    assert not ws.has("best/empty.md")  # has() means present and non-empty


def test_metadata_and_validate(tmp_path: Path):
    ws = Workspace(make_root(tmp_path), BRANCH)
    assert ws.metadata["mission"] == "m"
    assert ws.max_experiments == 4
    assert ws.mission == "m"
    assert ws.transcript_path == "tbpn-transcripts/t.md"
    ws.validate()


def test_validate_missing_metadata(tmp_path: Path):
    ws = Workspace(make_root(tmp_path, metadata=False), BRANCH)
    with pytest.raises(WorkspaceError, match="metadata.json"):
        ws.validate()


def test_validate_missing_transcript(tmp_path: Path):
    ws = Workspace(make_root(tmp_path, transcript=False), BRANCH)
    with pytest.raises(WorkspaceError, match="transcript"):
        ws.validate()


def test_validate_bad_max_experiments(tmp_path: Path):
    root = make_root(tmp_path)
    (root / SESSION_REL / "metadata.json").write_text(
        json.dumps({"mission": "m", "transcript_path": "tbpn-transcripts/t.md", "max_experiments": 0})
    )
    with pytest.raises(WorkspaceError, match="max_experiments"):
        Workspace(root, BRANCH).validate()


def test_n_experiments_and_totals(tmp_path: Path):
    rows = [
        LogRow(n=1, frameworks=["a"], candidate_total=30, incumbent_total=None, kept="1", note=""),
        LogRow(n=2, frameworks=["b"], candidate_total=28, incumbent_total=30, kept="0", note=""),
        LogRow(n=3, frameworks=["c"], candidate_total=None, incumbent_total=None, kept="error", note="x"),
    ]
    ws = Workspace(make_root(tmp_path, rows=rows), BRANCH)
    assert ws.n_experiments() == 3
    assert ws.totals() == [
        {"n": 1, "candidate_total": 30, "incumbent_total": None, "kept": "1"},
        {"n": 2, "candidate_total": 28, "incumbent_total": 30, "kept": "0"},
        {"n": 3, "candidate_total": None, "incumbent_total": None, "kept": "error"},
    ]
    assert ws.rows()[0].frameworks == ["a"]


def test_materialize_writes_missing_file_only(tmp_path: Path):
    ws = Workspace(make_root(tmp_path), BRANCH)
    result = {"path": f"{SESSION_REL}/attempts/1/decomposition.md", "content": "cached body\n"}
    path = ws.materialize(result)
    assert path == ws.root / result["path"]
    assert path.read_text() == "cached body\n"
    path.write_text("edited on disk\n")
    assert ws.materialize(result).read_text() == "edited on disk\n"
    path.write_text("")
    assert ws.materialize(result).read_text() == "cached body\n"  # empty counts as missing
    with pytest.raises(WorkspaceError):
        ws.materialize({"path": "../escape.md", "content": "x"})
