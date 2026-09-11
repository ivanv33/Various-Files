"""Shared fixtures: hermetic git, a temp bare origin, a seeded session branch, settings.

Everything here is offline. `.env` is loaded (without override) so `live` tests can
find `GOOGLE_API_KEY`; offline tests override `GIT_REMOTE` / `AUTORESEARCH_WORKDIR`.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from dotenv import load_dotenv

AUTORESEARCH_DIR = Path(__file__).resolve().parents[1]
load_dotenv(AUTORESEARCH_DIR / ".env", override=False)

TRANSCRIPT_REL = "tbpn-transcripts/transcripts/short.md"
SLUG = "demo"
BRANCH = f"autoresearch/{SLUG}"
SESSION_REL = f"autoresearch/sessions/{SLUG}"

TEST_GIT_ENV = {
    "GIT_AUTHOR_NAME": "test-author",
    "GIT_AUTHOR_EMAIL": "author@test.invalid",
    "GIT_COMMITTER_NAME": "test-author",
    "GIT_COMMITTER_EMAIL": "author@test.invalid",
}


def git(cwd: Path | str, *args: str, check: bool = True) -> str:
    """Run git in `cwd` with a test identity; return stripped stdout."""
    proc = subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        env={**os.environ, **TEST_GIT_ENV},
    )
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed:\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout.strip()


@pytest.fixture(autouse=True)
def _hermetic_git(tmp_path_factory, monkeypatch):
    """Ignore the developer's global/system git config (signing, hooks, aliases)."""
    empty = tmp_path_factory.mktemp("gitcfg") / "gitconfig"
    empty.write_text("")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for key, value in TEST_GIT_ENV.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def origin(tmp_path: Path) -> str:
    """A bare origin whose `master` has a README and a short transcript. Returns a file:// URL."""
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-q", "-b", "master")
    (seed / "README.md").write_text("# seed repo\n")
    transcript = seed / TRANSCRIPT_REL
    transcript.parent.mkdir(parents=True)
    transcript.write_text("Speaker A: hello.\nSpeaker B: hi.\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "seed master")
    bare = tmp_path / "origin.git"
    git(tmp_path, "clone", "-q", "--bare", str(seed), str(bare))
    return bare.as_uri()


def seed_session(
    remote: str,
    work: Path,
    *,
    slug: str = SLUG,
    mission: str = "Ship a great product",
    transcript_path: str = TRANSCRIPT_REL,
    max_experiments: int = 3,
) -> str:
    """Create `autoresearch/<slug>` from master with the session skeleton; push it. Returns branch."""
    from engine.tasks.log import HEADER

    branch = f"autoresearch/{slug}"
    session_rel = f"autoresearch/sessions/{slug}"
    clone = work / f"seed-{slug}"
    git(work, "clone", "-q", "--branch", "master", remote, str(clone))
    git(clone, "checkout", "-q", "-b", branch)
    session = clone / session_rel
    session.mkdir(parents=True)
    (session / "metadata.json").write_text(
        json.dumps(
            {"mission": mission, "transcript_path": transcript_path, "max_experiments": max_experiments},
            indent=2,
        )
        + "\n"
    )
    (session / "experiments.tsv").write_text(HEADER + "\n")
    (session / "notes.md").write_text("# Notes\n\n## Insights\n\n## Human steering\n")
    (session / "catalog.json").write_text("[]\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", f"session {slug}: bootstrap")
    git(clone, "push", "-q", "origin", branch)
    return branch


@pytest.fixture
def session_branch(origin: str, tmp_path: Path) -> str:
    return seed_session(origin, tmp_path)


@pytest.fixture
def settings(origin: str, tmp_path: Path, monkeypatch):
    from engine.config import Settings

    monkeypatch.setenv("GIT_REMOTE", origin)
    monkeypatch.setenv("AUTORESEARCH_WORKDIR", str(tmp_path / "ws"))
    monkeypatch.setenv("GIT_AUTHOR_NAME", "autoresearch-bot")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "bot@test.invalid")
    monkeypatch.setenv("GEMINI_MODEL", "fake-model")
    return Settings.from_env()


@pytest.fixture
def fake_model():
    """Factory: fake_model(["reply 1", "reply 2"]) -> chat model that returns those in order."""
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
    from langchain_core.messages import AIMessage

    def make(replies):
        return GenericFakeChatModel(messages=iter(AIMessage(content=r) for r in replies))

    return make
