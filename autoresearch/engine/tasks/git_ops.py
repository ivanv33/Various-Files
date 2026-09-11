"""All git side effects: clone-or-reset, allowlist staging, stray revert, commit + push.

Plain functions; `loop.py` wraps the side-effecting ones with `langgraph.func.task` so they are
cached across resumes. `ensure_workspace` must stay plain: it re-creates the clone on resume.
Agents never run git; only these functions do.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from engine.config import Settings
from engine.tasks import log as log_mod
from engine.workspace import SESSIONS_REL, Workspace, slug_from_branch

# Session-folder paths that may be committed. `attempts/` is scratch and never staged.
ALLOWLIST = ("experiments.tsv", "notes.md", "proposals", "best", "rubric.md", "catalog.json")
SCRATCH = ("attempts",)


class GitError(RuntimeError):
    """A git command failed in a way the loop cannot recover from."""


def _run(root: Path | str, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


def git(root: Path | str, *args: str) -> str:
    """Run git, raise `GitError` on failure, return stripped stdout."""
    proc = _run(root, *args)
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


LOOP_ROLE = "loop"


def clone_path(workdir: Path | str, branch: str, role: str = LOOP_ROLE) -> Path:
    """`<workdir>/<branch with / -> __>` for the loop; any other role gets its own `--<role>` clone.

    The reviewer runs while the loop may be mid-experiment, and `ensure_workspace` hard-resets and
    cleans its clone, so the two graphs must never share one directory. Session slugs allow single
    hyphens only, so `--<role>` cannot collide with another branch's path.
    """
    name = branch.replace("/", "__")
    return Path(workdir) / (name if role == LOOP_ROLE else f"{name}--{role}")


# --- workspace ------------------------------------------------------------


def ensure_workspace(branch: str, settings: Settings | None = None, *, role: str = LOOP_ROLE) -> Workspace:
    """Clone `<GIT_REMOTE>` at `branch` (shallow, single-branch) or hard-reset an existing clone.

    Idempotent and safe to call on every (re)invocation of the entrypoint. Local commits, tracked
    edits and untracked files (including `attempts/`) are discarded; origin is the only truth.
    `role` selects the clone (see `clone_path`); the reviewer passes `role="review"`.
    """
    settings = settings or Settings.from_env()
    root = clone_path(settings.workdir, branch, role)
    if not (root / ".git").exists():
        if root.exists():
            shutil.rmtree(root)  # leftovers of an interrupted clone
        root.parent.mkdir(parents=True, exist_ok=True)
        git(
            root.parent,
            "clone",
            "-q",
            "--single-branch",
            "--branch",
            branch,
            "--depth",
            "50",
            settings.git_remote,
            str(root),
        )
    else:
        git(root, "remote", "set-url", "origin", settings.git_remote)
        for marker in ("rebase-merge", "rebase-apply"):
            if (root / ".git" / marker).exists():
                _run(root, "rebase", "--abort")
        git(root, "fetch", "-q", "origin", branch)
        git(root, "reset", "-q", "--hard")
        git(root, "checkout", "-q", "-B", branch, f"origin/{branch}")
        git(root, "reset", "-q", "--hard", f"origin/{branch}")
        git(root, "clean", "-q", "-fd")
    git(root, "config", "user.name", settings.author_name)
    git(root, "config", "user.email", settings.author_email)
    ws = Workspace(root, branch)
    ws.validate()
    return ws


def pull(root: Path | str, branch: str | None = None) -> str:
    """`git pull --rebase` from origin; returns the new HEAD sha."""
    branch = branch or git(root, "rev-parse", "--abbrev-ref", "HEAD")
    git(root, "pull", "-q", "--rebase", "--autostash", "origin", branch)
    return git(root, "rev-parse", "HEAD")


# --- staging --------------------------------------------------------------


def _pathspec_matches(root: Path, rel: str) -> bool:
    return (root / rel).exists() or bool(git(root, "ls-files", "--", rel))


def _in_allowlist(session_rel: str, path: str) -> bool:
    return any(path == f"{session_rel}/{name}" or path.startswith(f"{session_rel}/{name}/") for name in ALLOWLIST)


def _is_scratch(session_rel: str, path: str) -> bool:
    return any(path.startswith(f"{session_rel}/{name}/") for name in SCRATCH)


def stage_allowlist(root: Path | str, session_rel: str) -> list[str]:
    """Stage adds/edits/deletes under the session allowlist only. Returns staged paths."""
    root = Path(root)
    specs = [f"{session_rel}/{name}" for name in ALLOWLIST if _pathspec_matches(root, f"{session_rel}/{name}")]
    if specs:
        git(root, "add", "-A", "--", *specs)
    return sorted(git(root, "diff", "--cached", "--name-only").splitlines())


def _status_entries(root: Path) -> list[tuple[str, str, str]]:
    """(X, Y, path) from `git status --porcelain -z`, renames collapsed to their new path."""
    out = _run(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if out.returncode != 0:
        raise GitError(out.stderr.strip())
    fields = out.stdout.split("\0")
    entries: list[tuple[str, str, str]] = []
    i = 0
    while i < len(fields):
        field = fields[i]
        i += 1
        if len(field) < 4:
            continue
        x, y, path = field[0], field[1], field[3:]
        if x in "RC":
            i += 1  # skip the original path of a rename/copy
        entries.append((x, y, path))
    return entries


def revert_stray_changes(root: Path | str, session_rel: str) -> list[str]:
    """Undo every change outside the allowlist (scratch `attempts/` excepted). Returns the paths."""
    root = Path(root)
    strays: list[str] = []
    for x, y, path in _status_entries(root):
        if _in_allowlist(session_rel, path) or _is_scratch(session_rel, path):
            continue
        strays.append(path)
        if x == "?":
            target = root / path
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
            continue
        if x != " ":
            git(root, "reset", "-q", "--", path)
        in_head = _run(root, "cat-file", "-e", f"HEAD:{path}").returncode == 0
        if in_head:
            git(root, "checkout", "-q", "--", path)
        else:
            (root / path).unlink(missing_ok=True)
    return sorted(strays)


# --- commit + push --------------------------------------------------------


def merge_experiments_tsv(ours: str, theirs: str) -> str:
    """Union of data rows from both versions, sorted by `n`; on duplicate `n` the first argument wins."""
    rows: dict[int, log_mod.LogRow] = {}
    for row in log_mod.parse_tsv(ours) + log_mod.parse_tsv(theirs):
        rows.setdefault(row.n, row)
    return log_mod.render_tsv([rows[n] for n in sorted(rows)])


def _try_push(root: Path, branch: str) -> bool:
    proc = _run(root, "push", "-q", "origin", f"HEAD:refs/heads/{branch}")
    if proc.returncode == 0:
        return True
    err = proc.stderr
    if "rejected" in err or "non-fast-forward" in err or "fetch first" in err:
        return False
    raise GitError(f"git push failed: {err.strip()}")


def _show_stage(root: Path, stage: int, path: str) -> str:
    return _run(root, "show", f":{stage}:{path}").stdout


def _rebase_onto_origin(root: Path, branch: str, session_rel: str) -> None:
    """Rebase local commits onto origin; the only conflict allowed is `experiments.tsv` (union-merged)."""
    tsv = f"{session_rel}/{log_mod.TSV_NAME}"
    git(root, "fetch", "-q", "origin", branch)
    proc = _run(root, "rebase", f"origin/{branch}")
    while proc.returncode != 0:
        conflicted = _run(root, "diff", "--name-only", "--diff-filter=U").stdout.split()
        try:
            if set(conflicted) != {tsv}:
                raise GitError(
                    f"rebase onto origin/{branch} conflicts outside experiments.tsv: {conflicted or proc.stderr.strip()}"
                )
            upstream = _show_stage(root, 2, tsv)  # during a rebase, stage 2 is the upstream side
            local = _show_stage(root, 3, tsv)  # stage 3 is the local commit being replayed
            (root / tsv).write_text(merge_experiments_tsv(local, upstream), encoding="utf-8")
            git(root, "add", "--", tsv)
        except Exception:
            _run(root, "rebase", "--abort")
            raise
        proc = _run(root, "rebase", "--continue", env={"GIT_EDITOR": "true"})


def commit_push(root: Path | str, branch: str, message: str, session_rel: str | None = None) -> str | None:
    """Stage the allowlist, revert strays, commit, push (rebase + retry once). Returns sha or None."""
    root = Path(root)
    session_rel = session_rel or f"{SESSIONS_REL}/{slug_from_branch(branch)}"
    stage_allowlist(root, session_rel)
    revert_stray_changes(root, session_rel)
    if _run(root, "diff", "--cached", "--quiet").returncode == 0:
        return None
    git(root, "commit", "-q", "-m", message)
    if not _try_push(root, branch):
        _rebase_onto_origin(root, branch, session_rel)
        if not _try_push(root, branch):
            raise GitError(f"push to origin/{branch} rejected again after rebase")
    return git(root, "rev-parse", "HEAD")
