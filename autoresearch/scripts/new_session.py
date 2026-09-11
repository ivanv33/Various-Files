"""Create a session branch `autoresearch/<slug>` from the base branch with the session skeleton; push it.

Works against any `GIT_REMOTE` (a local bare repo for dev, GitHub for deploy): shallow-clone the base
branch, branch, write `autoresearch/sessions/<slug>/{metadata.json, experiments.tsv, notes.md,
catalog.json}` (catalog = copy of the seed catalog), commit, push. Then invoke `autoresearch_session`
with `{"branch": "autoresearch/<slug>"}`.

Usage (from `autoresearch/`; `.env` is loaded without overriding the environment):
    .venv/bin/python -m scripts.new_session <slug> --mission "..." --transcript tbpn-transcripts/<file>.md \
        --max-experiments N [--remote URL] [--base master] [--workdir DIR] [--keep-clone]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # `python scripts/new_session.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.catalog import load_seed_catalog  # noqa: E402
from engine.config import DEFAULT_AUTHOR_EMAIL, DEFAULT_AUTHOR_NAME, DEFAULT_WORKDIR, load_env  # noqa: E402
from engine.tasks.git_ops import GitError, git, redact, split_remote  # noqa: E402
from engine.tasks.log import HEADER  # noqa: E402
from engine.workspace import BRANCH_PREFIX, SESSIONS_REL  # noqa: E402

DEFAULT_BASE = "master"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NOTES_SKELETON = "# Notes\n\n## Insights\n\n## Human steering\n"

__all__ = ["SessionError", "create_session", "main", "redact", "session_files", "validate_slug"]


class SessionError(RuntimeError):
    """Bad arguments, or a remote state that makes the session impossible to create."""


def validate_slug(slug: str) -> str:
    if not SLUG_RE.match(slug or ""):
        raise SessionError(f"slug must be lowercase letters, digits and single hyphens, got {slug!r}")
    return slug


def session_files(
    mission: str, transcript_path: str, max_experiments: int, catalog: list[dict[str, Any]]
) -> dict[str, str]:
    """The four files every session starts with, keyed by file name."""
    metadata = {"mission": mission, "transcript_path": transcript_path, "max_experiments": max_experiments}
    return {
        "metadata.json": json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        "experiments.tsv": HEADER + "\n",
        "notes.md": NOTES_SKELETON,
        "catalog.json": json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
    }


def _branch_exists(cwd: Path, url: str, branch: str, env: dict[str, str]) -> bool:
    return bool(git(cwd, "ls-remote", "--heads", url, f"refs/heads/{branch}", env=env))


def create_session(
    slug: str,
    *,
    mission: str,
    transcript_path: str,
    max_experiments: int,
    remote: str,
    workdir: Path | str | None = None,
    base: str = DEFAULT_BASE,
    catalog: list[dict[str, Any]] | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    keep_clone: bool = False,
) -> dict[str, Any]:
    """Create and push `autoresearch/<slug>`; return `{"branch", "session_rel", "sha", "remote"}`.

    Fails before pushing anything if the slug is bad, the branch already exists on the remote, the
    transcript is missing from `base`, or the session folder already exists there.
    """
    validate_slug(slug)
    mission = (mission or "").strip()
    if not mission:
        raise SessionError("mission must be a non-empty string")
    transcript_path = (transcript_path or "").strip().lstrip("/")
    if not transcript_path:
        raise SessionError("transcript path must be a non-empty repo-relative path")
    try:
        max_experiments = int(max_experiments)
    except (TypeError, ValueError):
        raise SessionError(f"max_experiments must be a positive integer, got {max_experiments!r}") from None
    if max_experiments < 1:
        raise SessionError(f"max_experiments must be a positive integer, got {max_experiments!r}")
    remote = (remote or "").strip()
    if not remote:
        raise SessionError("remote is required (pass --remote or set GIT_REMOTE)")

    branch = f"{BRANCH_PREFIX}{slug}"
    session_rel = f"{SESSIONS_REL}/{slug}"
    workdir = Path(workdir or os.environ.get("AUTORESEARCH_WORKDIR") or DEFAULT_WORKDIR)
    workdir.mkdir(parents=True, exist_ok=True)
    clone = workdir / f"new-session__{slug}"
    if clone.exists():
        shutil.rmtree(clone)
    url, env = split_remote(remote)  # the token is sent per command, never written to the clone

    try:
        if _branch_exists(workdir, url, branch, env):
            raise SessionError(f"branch {branch!r} already exists on {url}")
        git(workdir, "clone", "-q", "--depth", "1", "--single-branch", "--branch", base, url, str(clone), env=env)
        transcript = clone / transcript_path
        if not (transcript.is_file() and transcript.stat().st_size > 0):
            raise SessionError(f"transcript not found or empty on {base!r}: {transcript_path!r}")
        session = clone / session_rel
        if session.exists():
            raise SessionError(f"{session_rel} already exists on {base!r}")
        git(clone, "config", "user.name", author_name or os.environ.get("GIT_AUTHOR_NAME") or DEFAULT_AUTHOR_NAME)
        git(clone, "config", "user.email", author_email or os.environ.get("GIT_AUTHOR_EMAIL") or DEFAULT_AUTHOR_EMAIL)
        git(clone, "checkout", "-q", "-b", branch)
        session.mkdir(parents=True)
        files = session_files(mission, transcript_path, max_experiments, load_seed_catalog() if catalog is None else catalog)
        for name, text in files.items():
            (session / name).write_text(text, encoding="utf-8")
        git(clone, "add", "-A", "--", session_rel)
        git(clone, "commit", "-q", "-m", f"session {slug}: bootstrap")
        git(clone, "push", "-q", "origin", f"HEAD:refs/heads/{branch}", env=env)
        sha = git(clone, "rev-parse", "HEAD")
    except GitError as exc:
        raise SessionError(redact(str(exc))) from exc
    finally:
        if not keep_clone and clone.exists():
            shutil.rmtree(clone)
    return {"branch": branch, "session_rel": session_rel, "sha": sha, "remote": remote}


def main(argv: list[str] | None = None) -> int:
    load_env()
    parser = argparse.ArgumentParser(description="Create and push a new autoresearch session branch.")
    parser.add_argument("slug", help="session slug; branch becomes autoresearch/<slug>")
    parser.add_argument("--mission", required=True, help="what the recommendations should move toward")
    parser.add_argument("--transcript", required=True, help="repo-relative path, e.g. tbpn-transcripts/transcripts/<file>.md")
    parser.add_argument("--max-experiments", type=int, required=True)
    parser.add_argument("--remote", default=None, help="git remote URL (default: $GIT_REMOTE)")
    parser.add_argument("--base", default=DEFAULT_BASE, help=f"branch to start from (default {DEFAULT_BASE})")
    parser.add_argument("--workdir", default=None, help="scratch dir for the clone (default: $AUTORESEARCH_WORKDIR)")
    parser.add_argument("--keep-clone", action="store_true", help="leave the scratch clone on disk")
    args = parser.parse_args(argv)

    remote = (args.remote or os.environ.get("GIT_REMOTE") or "").strip()
    if not remote:
        print("error: GIT_REMOTE is not set and --remote was not given", file=sys.stderr)
        return 2
    try:
        result = create_session(
            args.slug,
            mission=args.mission,
            transcript_path=args.transcript,
            max_experiments=args.max_experiments,
            remote=remote,
            workdir=args.workdir,
            base=args.base,
            keep_clone=args.keep_clone,
        )
    except SessionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"created {result['branch']} at {result['sha']} on {redact(result['remote'])}")
    print(f'next: invoke autoresearch_session with {{"branch": "{result["branch"]}"}}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
