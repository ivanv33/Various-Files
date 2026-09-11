from pathlib import Path

import pytest

from engine import config
from engine.config import ConfigError, Settings


def test_from_env_requires_git_remote(monkeypatch):
    monkeypatch.delenv("GIT_REMOTE", raising=False)
    with pytest.raises(ConfigError, match="GIT_REMOTE"):
        Settings.from_env()


def test_from_env_defaults(monkeypatch):
    for key in ("GEMINI_MODEL", "AUTORESEARCH_WORKDIR", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GIT_REMOTE", "file:///tmp/o.git")
    s = Settings.from_env()
    assert s.git_remote == "file:///tmp/o.git"
    assert s.gemini_model == "gemini-3.8-flash"
    assert s.workdir == Path("/tmp/autoresearch-ws")
    assert s.author_name and s.author_email


def test_from_env_reads_overrides(settings):
    assert settings.gemini_model == "fake-model"
    assert settings.git_remote.startswith("file://")
    assert settings.workdir.name == "ws"
    assert settings.author_name == "autoresearch-bot"


def test_make_model_uses_google_genai_prefix(monkeypatch, settings):
    seen = {}

    def fake_init(spec, **kwargs):
        seen["spec"] = spec
        seen["kwargs"] = kwargs
        return "MODEL"

    monkeypatch.setattr(config, "init_chat_model", fake_init)
    assert config.make_model(settings) == "MODEL"
    assert seen["spec"] == "google_genai:fake-model"
