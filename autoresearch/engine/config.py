"""Settings from environment variables and the single chat-model factory.

All model calls go through `GEMINI_MODEL` via `init_chat_model("google_genai:<model>")`.
`langgraph dev` / the deployment inject the env; scripts may call `load_env()` first.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from langchain.chat_models import init_chat_model

DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"
DEFAULT_WORKDIR = "/tmp/autoresearch-ws"
DEFAULT_AUTHOR_NAME = "autoresearch-bot"
DEFAULT_AUTHOR_EMAIL = "autoresearch-bot@users.noreply.github.com"


class ConfigError(RuntimeError):
    """A required setting is missing or malformed."""


@dataclass(frozen=True)
class Settings:
    git_remote: str
    gemini_model: str = DEFAULT_GEMINI_MODEL
    workdir: Path = Path(DEFAULT_WORKDIR)
    author_name: str = DEFAULT_AUTHOR_NAME
    author_email: str = DEFAULT_AUTHOR_EMAIL

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        env = os.environ if env is None else env
        remote = (env.get("GIT_REMOTE") or "").strip()
        if not remote:
            raise ConfigError(
                "GIT_REMOTE is not set. Local dev: file:///path/to/origin.git; "
                "deploy: https://x-access-token:${GITHUB_TOKEN}@github.com/<owner>/<repo>.git"
            )
        return cls(
            git_remote=remote,
            gemini_model=(env.get("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL).strip(),
            workdir=Path((env.get("AUTORESEARCH_WORKDIR") or DEFAULT_WORKDIR).strip()),
            author_name=(env.get("GIT_AUTHOR_NAME") or DEFAULT_AUTHOR_NAME).strip(),
            author_email=(env.get("GIT_AUTHOR_EMAIL") or DEFAULT_AUTHOR_EMAIL).strip(),
        )


def load_env(path: Path | None = None) -> None:
    """Load `autoresearch/.env` (if present) without overriding existing variables."""
    from dotenv import load_dotenv

    load_dotenv(path or Path(__file__).resolve().parents[1] / ".env", override=False)


def make_model(settings: Settings | None = None):
    """One chat model for every role: `google_genai:<GEMINI_MODEL>`."""
    if settings is None:
        model_id = (os.environ.get("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL).strip()
    else:
        model_id = settings.gemini_model
    return init_chat_model(f"google_genai:{model_id}")
