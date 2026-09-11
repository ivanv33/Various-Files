"""A session clone on disk: paths, metadata, the tsv view, and virtual paths for agents.

`Workspace` is a thin, stateless view over `<root>/autoresearch/sessions/<slug>/`. It never
runs git (see `tasks/git_ops.py`). Pass `ws.root` / `ws.branch` as strings into `@task`s and
rebuild with `Workspace(root, branch)` inside them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.tasks import log as log_mod

BRANCH_PREFIX = "autoresearch/"
SESSIONS_REL = "autoresearch/sessions"
REQUIRED_METADATA = ("mission", "transcript_path", "max_experiments")


class WorkspaceError(RuntimeError):
    """Bad branch name, metadata, or transcript; raised before checkpoint 0."""


def slug_from_branch(branch: str) -> str:
    if not branch.startswith(BRANCH_PREFIX) or not branch[len(BRANCH_PREFIX) :].strip("/"):
        raise WorkspaceError(f"session branch must look like 'autoresearch/<slug>', got {branch!r}")
    return branch[len(BRANCH_PREFIX) :].strip("/")


class Workspace:
    def __init__(self, root: Path | str, branch: str):
        self.root = Path(root)
        self.branch = branch
        self.slug = slug_from_branch(branch)

    # --- paths ----------------------------------------------------------
    @property
    def session_rel(self) -> str:
        return f"{SESSIONS_REL}/{self.slug}"

    @property
    def session_dir(self) -> Path:
        return self.root / self.session_rel

    def rel(self, name: str) -> str:
        """Repo-relative path of a session file."""
        return f"{self.session_rel}/{name}"

    def path(self, name: str) -> Path:
        return self.session_dir / name

    def attempt_dir(self, n: int) -> Path:
        return self.session_dir / "attempts" / str(n)

    def attempt_rel(self, n: int, name: str) -> str:
        return self.rel(f"attempts/{n}/{name}")

    def virtual(self, name: str) -> str:
        """Path as a deep agent sees it (`FilesystemBackend(virtual_mode=True)` rooted at root)."""
        return f"/{self.rel(name)}"

    @staticmethod
    def virtual_repo(repo_rel: str) -> str:
        return "/" + repo_rel.lstrip("/")

    # --- files ----------------------------------------------------------
    def has(self, name: str) -> bool:
        """Present and non-empty."""
        p = self.path(name)
        return p.is_file() and p.stat().st_size > 0

    def read(self, name: str) -> str:
        return self.path(name).read_text(encoding="utf-8")

    def write(self, name: str, text: str) -> Path:
        p = self.path(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def materialize(self, result: dict[str, Any]) -> Path:
        """Ensure a cached step result `{"path": repo-relative, "content": str}` exists on disk."""
        rel = str(result["path"])
        target = (self.root / rel).resolve()
        if self.root.resolve() not in target.parents:
            raise WorkspaceError(f"step result path escapes the clone: {rel!r}")
        if not (target.is_file() and target.stat().st_size > 0):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(result.get("content", "")), encoding="utf-8")
        return self.root / rel

    # --- metadata -------------------------------------------------------
    @property
    def metadata(self) -> dict[str, Any]:
        p = self.path("metadata.json")
        if not p.is_file():
            raise WorkspaceError(f"missing {self.rel('metadata.json')} in clone {self.root}")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise WorkspaceError(f"{self.rel('metadata.json')} is not valid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise WorkspaceError(f"{self.rel('metadata.json')} must be a JSON object")
        return data

    @property
    def mission(self) -> str:
        return str(self.metadata["mission"])

    @property
    def transcript_path(self) -> str:
        return str(self.metadata["transcript_path"])

    @property
    def max_experiments(self) -> int:
        return int(self.metadata["max_experiments"])

    def validate(self) -> None:
        """Fail loudly (before checkpoint 0) on bad metadata or a missing transcript."""
        data = self.metadata
        missing = [k for k in REQUIRED_METADATA if k not in data]
        if missing:
            raise WorkspaceError(f"{self.rel('metadata.json')} lacks {', '.join(missing)}")
        try:
            n = int(data["max_experiments"])
        except (TypeError, ValueError):
            n = 0
        if n < 1:
            raise WorkspaceError(f"max_experiments must be a positive integer, got {data['max_experiments']!r}")
        transcript = self.root / str(data["transcript_path"])
        if not (transcript.is_file() and transcript.stat().st_size > 0):
            raise WorkspaceError(f"transcript not found or empty in clone: {data['transcript_path']!r}")

    # --- log view -------------------------------------------------------
    def rows(self) -> list[log_mod.LogRow]:
        return log_mod.read_rows(self.root, self.session_rel)

    def n_experiments(self) -> int:
        return len(self.rows())

    def totals(self) -> list[dict[str, Any]]:
        return [
            {"n": r.n, "candidate_total": r.candidate_total, "incumbent_total": r.incumbent_total, "kept": r.kept}
            for r in self.rows()
        ]
