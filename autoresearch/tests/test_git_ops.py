import base64
import subprocess
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
    redact,
    revert_stray_changes,
    split_remote,
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


# --- credentials ----------------------------------------------------------

TOKENISED = "https://x-access-token:SECRET@github.com/o/r.git"
BASIC = base64.b64encode(b"x-access-token:SECRET").decode()


def test_split_remote_moves_the_token_from_the_url_into_a_per_command_header():
    url, env = split_remote(TOKENISED)
    assert url == "https://github.com/o/r.git"
    assert env == {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.extraHeader", "GIT_CONFIG_VALUE_0": f"Authorization: Basic {BASIC}"}
    assert split_remote("https://x-access-token:SE%2FCRET@github.com/o/r.git")[1]["GIT_CONFIG_VALUE_0"].endswith(
        base64.b64encode(b"x-access-token:SE/CRET").decode()
    )
    for plain in ("file:///tmp/origin.git", "https://github.com/o/r.git", "ssh://git@github.com/o/r.git", "git@github.com:o/r.git"):
        assert split_remote(plain) == (plain, {})


def test_redact_strips_userinfo_and_basic_auth_values_and_git_errors_use_it():
    assert redact(f"git clone {TOKENISED} failed") == "git clone https://github.com/o/r.git failed"
    assert redact(f"Authorization: Basic {BASIC} rejected") == "Authorization: Basic [redacted] rejected"
    assert redact("nothing to hide") == "nothing to hide"
    err = GitError(f"git push {TOKENISED} failed: Authorization: Basic {BASIC}")
    assert "SECRET" not in str(err) and BASIC not in str(err) and "github.com/o/r.git" in str(err)


class OfflineGit:
    """Wraps `git_ops._run`: records every call; network subcommands never leave the machine.

    `clone` really clones from `origin` (the recorded argv keeps the URL the engine asked for); `fetch`, `pull`,
    `push` and `ls-remote` return success without running. Everything else runs for real.
    """

    NETWORK = {"fetch", "pull", "push", "ls-remote"}

    def __init__(self, real, origin: str):
        self.real, self.origin, self.calls = real, origin, []

    def __call__(self, root, *args, env=None):
        self.calls.append((list(args), dict(env or {})))
        if args and args[0] == "clone":
            args = tuple(self.origin if a.startswith("http") else a for a in args)
            return self.real(root, *args, env=env)
        if args and args[0] in self.NETWORK:
            return subprocess.CompletedProcess(["git", *args], 0, "", "")
        return self.real(root, *args, env=env)

    def argv(self, subcommand: str) -> list[list[str]]:
        return [a for a, _env in self.calls if a and a[0] == subcommand]

    def env(self, subcommand: str) -> list[dict[str, str]]:
        return [env for a, env in self.calls if a and a[0] == subcommand]


def test_ensure_workspace_never_writes_the_token_into_the_clone(settings, session_branch, monkeypatch):
    from engine.config import Settings
    from engine.tasks import git_ops

    spy = OfflineGit(git_ops._run, settings.git_remote)
    monkeypatch.setattr(git_ops, "_run", spy)
    tokenised = Settings(git_remote=TOKENISED, workdir=settings.workdir, author_name=settings.author_name, author_email=settings.author_email)
    header = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.extraHeader", "GIT_CONFIG_VALUE_0": f"Authorization: Basic {BASIC}"}

    ws = ensure_workspace(BRANCH, tokenised)  # fresh clone
    assert spy.argv("clone") and "https://github.com/o/r.git" in spy.argv("clone")[0]
    assert spy.env("clone") == [header]

    ws.write("attempts/1/x.md", "scratch\n")
    ws2 = ensure_workspace(BRANCH, tokenised)  # existing clone: set-url + fetch + reset
    assert ws2.root == ws.root
    assert git(ws.root, "config", "remote.origin.url") == "https://github.com/o/r.git"
    assert spy.env("fetch") == [header]

    config = (ws.root / ".git" / "config").read_text()
    assert "SECRET" not in config and BASIC not in config and "@" not in git(ws.root, "config", "remote.origin.url")
    for argv, _env in spy.calls:
        assert "SECRET" not in " ".join(argv) and BASIC not in " ".join(argv)


def test_pull_and_commit_push_send_the_header_per_command(settings, session_branch, monkeypatch):
    from engine.config import Settings
    from engine.tasks import git_ops

    ws = ensure_workspace(BRANCH, settings)
    spy = OfflineGit(git_ops._run, settings.git_remote)
    monkeypatch.setattr(git_ops, "_run", spy)
    monkeypatch.setenv("GIT_REMOTE", TOKENISED)  # what the loop's tasks see
    tokenised = Settings.from_env()
    header = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.extraHeader", "GIT_CONFIG_VALUE_0": f"Authorization: Basic {BASIC}"}

    pull(ws.root, BRANCH, tokenised)
    assert spy.env("pull") == [header]
    append_row(ws.root, SESSION_REL, LogRow(n=1, frameworks=["a"], candidate_total=30, kept="1", note="x"))
    assert commit_push(ws.root, BRANCH, "exp 1: KEEP 30 vs -") == git(ws.root, "rev-parse", "HEAD")  # settings from env
    assert spy.env("push") == [header]
    for argv, _env in spy.calls:
        assert "SECRET" not in " ".join(argv) and BASIC not in " ".join(argv)


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


def test_reviewer_workspace_is_a_separate_clone_that_leaves_the_loop_clone_alone(settings, session_branch):
    loop_ws = ensure_workspace(BRANCH, settings)
    loop_ws.write("attempts/1/x.md", "half-written scratch\n")
    loop_ws.write("notes.md", "# Notes\n\n## Insights\n- half-written\n")

    review_ws = ensure_workspace(BRANCH, settings, role="review")
    assert clone_path(settings.workdir, BRANCH) == settings.workdir / "autoresearch__demo"
    assert clone_path(settings.workdir, BRANCH, role="review") == settings.workdir / "autoresearch__demo--review"
    assert review_ws.root == clone_path(settings.workdir, BRANCH, role="review") != loop_ws.root
    assert review_ws.branch == BRANCH and git(review_ws.root, "rev-parse", "HEAD") == origin_head(settings.git_remote)
    assert git(review_ws.root, "status", "--porcelain") == ""
    assert not review_ws.has("attempts/1/x.md")
    # the loop's clone is untouched: scratch and its unfinished edit are still there
    assert loop_ws.read("attempts/1/x.md") == "half-written scratch\n"
    assert "half-written" in loop_ws.read("notes.md")


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
