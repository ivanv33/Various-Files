from pathlib import Path

import pytest

from engine.tasks.git_ops import (
    ALLOWLIST,
    GitError,
    clone_path,
    commit_push,
    ensure_workspace,
    merge_experiments_tsv,
    pull,
    revert_stray_changes,
    stage_allowlist,
)
from engine.tasks.log import HEADER, LogRow, append_row, read_rows
from tests.conftest import BRANCH, SESSION_REL, git


def other_clone(origin: str, tmp_path: Path, name: str = "other") -> Path:
    path = tmp_path / name
    git(tmp_path, "clone", "-q", "--branch", BRANCH, origin, str(path))
    return path


def push_from_other(clone: Path, message: str) -> str:
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", message)
    git(clone, "push", "-q", "origin", BRANCH)
    return git(clone, "rev-parse", "HEAD")


def origin_head(origin: str) -> str:
    return git(Path(origin.removeprefix("file://")), "rev-parse", BRANCH)


# --- pure -----------------------------------------------------------------


def test_merge_experiments_tsv_union_sorted_dedupe():
    ours = HEADER + "\n1\tt1\ta\t30\t\t1\tseed\n3\tt3\tc\t20\t30\t0\tours-3\n"
    theirs = HEADER + "\n2\tt2\tb\t25\t30\t0\tx\n3\tt3\tc\t99\t30\t1\ttheirs-3\n"
    merged = merge_experiments_tsv(ours, theirs)
    rows = [line.split("\t") for line in merged.splitlines()[1:]]
    assert merged.startswith(HEADER + "\n") and merged.endswith("\n")
    assert [r[0] for r in rows] == ["1", "2", "3"]
    assert rows[2][6] == "ours-3"  # first argument wins on duplicate n


def test_allowlist_matches_spec():
    assert set(ALLOWLIST) == {"experiments.tsv", "notes.md", "proposals", "best", "rubric.md", "catalog.json"}


# --- ensure_workspace -----------------------------------------------------


def test_ensure_workspace_clones_shallow_single_branch(settings, session_branch):
    ws = ensure_workspace(BRANCH, settings)
    assert ws.root == clone_path(settings.workdir, BRANCH) == settings.workdir / "autoresearch__demo"
    assert (ws.root / ".git").exists()
    assert git(ws.root, "rev-parse", "--abbrev-ref", "HEAD") == BRANCH
    assert ws.metadata["max_experiments"] == 3
    assert git(ws.root, "config", "user.name") == "autoresearch-bot"
    assert git(ws.root, "config", "user.email") == "bot@test.invalid"
    assert git(ws.root, "rev-parse", "HEAD") == origin_head(settings.git_remote)


def test_ensure_workspace_resets_dirty_clone_and_fetches_remote(settings, session_branch, tmp_path):
    ws = ensure_workspace(BRANCH, settings)
    (ws.root / "README.md").write_text("dirty\n")
    (ws.root / "stray.txt").write_text("x\n")
    ws.write("attempts/1/decomposition.md", "scratch\n")
    git(ws.root, "commit", "-q", "-am", "local-only commit")  # must be discarded

    other = other_clone(settings.git_remote, tmp_path)
    (other / SESSION_REL / "notes.md").write_text("# Notes\n\n## Insights\n- owner edit\n")
    remote_sha = push_from_other(other, "owner edits notes")

    ws2 = ensure_workspace(BRANCH, settings)
    assert ws2.root == ws.root
    assert (ws2.root / "README.md").read_text() == "# seed repo\n"
    assert not (ws2.root / "stray.txt").exists()
    assert not ws2.has("attempts/1/decomposition.md")
    assert "owner edit" in ws2.read("notes.md")
    assert git(ws2.root, "rev-parse", "HEAD") == remote_sha
    assert git(ws2.root, "status", "--porcelain") == ""


def test_ensure_workspace_fails_clearly_on_bad_metadata(settings, session_branch, tmp_path):
    other = other_clone(settings.git_remote, tmp_path)
    (other / SESSION_REL / "metadata.json").write_text('{"mission": "m"}')
    push_from_other(other, "break metadata")
    with pytest.raises(Exception, match="transcript_path|max_experiments"):
        ensure_workspace(BRANCH, settings)


# --- staging / stray revert -----------------------------------------------


def dirty_everything(ws):
    append_row(ws.root, SESSION_REL, LogRow(n=1, frameworks=["a"], candidate_total=30, kept="1", note="seed"))
    ws.write("notes.md", "# Notes\n\n## Insights\n- one\n")
    ws.write("proposals/new-framework-x.md", "---\nstatus: open\n---\n")
    ws.write("best/recommendations.md", "do things\n")
    ws.write("rubric.md", "# Rubric\n")
    ws.write("catalog.json", "[{}]\n")
    ws.write("attempts/1/decomposition.md", "scratch\n")
    ws.write("stray-in-session.md", "oops\n")
    (ws.root / "README.md").write_text("agent edited the readme\n")
    (ws.root / "stray.txt").write_text("oops\n")


def test_stage_allowlist_stages_only_session_allowlist(settings, session_branch):
    ws = ensure_workspace(BRANCH, settings)
    dirty_everything(ws)
    staged = stage_allowlist(ws.root, SESSION_REL)
    assert sorted(staged) == sorted(
        f"{SESSION_REL}/{p}"
        for p in [
            "experiments.tsv",
            "notes.md",
            "proposals/new-framework-x.md",
            "best/recommendations.md",
            "rubric.md",
            "catalog.json",
        ]
    )
    assert staged == sorted(git(ws.root, "diff", "--cached", "--name-only").splitlines())


def test_stage_allowlist_on_clean_tree_is_noop(settings, session_branch):
    ws = ensure_workspace(BRANCH, settings)
    assert stage_allowlist(ws.root, SESSION_REL) == []


def test_revert_stray_changes_restores_tracked_and_removes_untracked(settings, session_branch):
    ws = ensure_workspace(BRANCH, settings)
    dirty_everything(ws)
    stage_allowlist(ws.root, SESSION_REL)
    reverted = revert_stray_changes(ws.root, SESSION_REL)
    assert reverted == sorted(["README.md", "stray.txt", f"{SESSION_REL}/stray-in-session.md"])
    assert (ws.root / "README.md").read_text() == "# seed repo\n"
    assert not (ws.root / "stray.txt").exists()
    assert not (ws.root / SESSION_REL / "stray-in-session.md").exists()
    assert ws.has("attempts/1/decomposition.md")  # scratch is left alone
    assert len(git(ws.root, "diff", "--cached", "--name-only").splitlines()) == 6
    assert revert_stray_changes(ws.root, SESSION_REL) == []


# --- commit_push ----------------------------------------------------------


def test_commit_push_returns_none_when_nothing_to_commit(settings, session_branch):
    ws = ensure_workspace(BRANCH, settings)
    ws.write("attempts/1/x.md", "scratch\n")
    assert commit_push(ws.root, BRANCH, "exp 1: nothing") is None
    assert git(ws.root, "rev-parse", "HEAD") == origin_head(settings.git_remote)


def test_commit_push_commits_allowlist_and_pushes(settings, session_branch):
    ws = ensure_workspace(BRANCH, settings)
    before = origin_head(settings.git_remote)
    dirty_everything(ws)
    sha = commit_push(ws.root, BRANCH, "exp 1: KEEP 30 vs -")
    assert sha and sha == git(ws.root, "rev-parse", "HEAD") == origin_head(settings.git_remote) != before
    files = git(ws.root, "show", "--name-only", "--format=", sha).splitlines()
    assert all(f.startswith(SESSION_REL + "/") for f in files)
    assert not any("/attempts/" in f or f.endswith("stray-in-session.md") for f in files)
    assert len(files) == 6
    assert git(ws.root, "log", "-1", "--format=%s%n%an <%ae>") == "exp 1: KEEP 30 vs -\nautoresearch-bot <bot@test.invalid>"
    assert (ws.root / "README.md").read_text() == "# seed repo\n"
    # only untracked scratch may remain
    assert git(ws.root, "status", "--porcelain").splitlines() == [f"?? {SESSION_REL}/attempts/"]


def test_commit_push_rebases_and_unions_tsv_on_conflict(settings, session_branch, tmp_path):
    ws = ensure_workspace(BRANCH, settings)
    other = other_clone(settings.git_remote, tmp_path)
    append_row(other, SESSION_REL, LogRow(n=1, frameworks=["a"], candidate_total=30, kept="1", note="from-other"))
    push_from_other(other, "exp 1 from other")

    append_row(ws.root, SESSION_REL, LogRow(n=2, frameworks=["b"], candidate_total=20, incumbent_total=30, kept="0", note="from-ws"))
    ws.write("notes.md", "# Notes\n\n## Insights\n- ws insight\n")
    sha = commit_push(ws.root, BRANCH, "exp 2: discard 20 vs 30")

    assert sha == git(ws.root, "rev-parse", "HEAD") == origin_head(settings.git_remote)
    rows = read_rows(ws.root, SESSION_REL)
    assert [(r.n, r.note) for r in rows] == [(1, "from-other"), (2, "from-ws")]
    assert git(ws.root, "log", "--format=%s", "-3").splitlines() == [
        "exp 2: discard 20 vs 30",
        "exp 1 from other",
        "session demo: bootstrap",
    ]
    assert git(ws.root, "status", "--porcelain") == ""
    assert not (ws.root / ".git" / "rebase-merge").exists()


def test_commit_push_rebases_cleanly_when_no_conflict(settings, session_branch, tmp_path):
    ws = ensure_workspace(BRANCH, settings)
    other = other_clone(settings.git_remote, tmp_path)
    (other / SESSION_REL / "notes.md").write_text("# Notes\n\n## Insights\n\n## Human steering\n- go faster\n")
    push_from_other(other, "steer")
    append_row(ws.root, SESSION_REL, LogRow(n=1, frameworks=["a"], candidate_total=30, kept="1", note="x"))
    sha = commit_push(ws.root, BRANCH, "exp 1: KEEP")
    assert sha == origin_head(settings.git_remote)
    assert "go faster" in ws.read("notes.md")
    assert len(read_rows(ws.root, SESSION_REL)) == 1


def test_commit_push_raises_on_non_tsv_conflict_and_aborts_rebase(settings, session_branch, tmp_path):
    ws = ensure_workspace(BRANCH, settings)
    other = other_clone(settings.git_remote, tmp_path)
    (other / SESSION_REL / "notes.md").write_text("# Notes (other)\n")
    remote_sha = push_from_other(other, "other notes")
    ws.write("notes.md", "# Notes (ws)\n")
    with pytest.raises(GitError, match="notes.md"):
        commit_push(ws.root, BRANCH, "exp 1: KEEP")
    assert not (ws.root / ".git" / "rebase-merge").exists()
    assert origin_head(settings.git_remote) == remote_sha
    assert ws.read("notes.md") == "# Notes (ws)\n"  # local commit preserved for inspection


# --- pull -----------------------------------------------------------------


def test_pull_picks_up_remote_changes(settings, session_branch, tmp_path):
    ws = ensure_workspace(BRANCH, settings)
    other = other_clone(settings.git_remote, tmp_path)
    (other / SESSION_REL / "rubric.md").write_text("# Rubric edited by owner\n")
    remote_sha = push_from_other(other, "owner rubric")
    assert pull(ws.root) == remote_sha
    assert ws.read("rubric.md") == "# Rubric edited by owner\n"
    assert git(ws.root, "rev-parse", "HEAD") == remote_sha
