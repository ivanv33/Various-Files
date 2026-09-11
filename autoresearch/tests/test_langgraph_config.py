"""Deploy readiness (plan M8): `langgraph.json` matches the code and renders a Dockerfile offline.

`langgraph build` needs a Docker daemon and `langgraph deploy` needs the owner's credentials, so neither runs
here. What can be checked without them: every graph path in the config resolves to a compiled entrypoint,
and `langgraph dockerfile` accepts the config and emits the lines the deployment relies on (git for the
workspace clone, the Python version, both graphs).
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from langgraph.pregel import Pregel

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "langgraph.json"
LANGGRAPH_CLI = Path(sys.executable).with_name("langgraph")


def load_config() -> dict:
    return json.loads(CONFIG.read_text())


def test_graph_paths_resolve_to_compiled_entrypoints():
    config = load_config()
    assert set(config["graphs"]) == {"autoresearch_session", "review_proposals"}
    for name, target in config["graphs"].items():
        rel_path, attr = target.split(":")
        module_path = ROOT / rel_path
        assert module_path.is_file(), f"{name}: {rel_path} missing"
        module_name = ".".join(module_path.relative_to(ROOT).with_suffix("").parts)
        graph = getattr(importlib.import_module(module_name), attr)
        assert isinstance(graph, Pregel), f"{name}: {target} is not a compiled graph"


def test_config_pins_runtime_and_installs_git():
    config = load_config()
    assert config["python_version"] == "3.13"
    assert config["dependencies"] == ["."]
    assert config["env"] == ".env"
    assert any("apt-get install" in line and "git" in line for line in config["dockerfile_lines"])


@pytest.mark.skipif(not LANGGRAPH_CLI.exists(), reason="langgraph CLI not installed in this venv")
def test_langgraph_dockerfile_renders_from_config(tmp_path: Path):
    out = tmp_path / "Dockerfile"
    proc = subprocess.run(
        [str(LANGGRAPH_CLI), "dockerfile", "--config", str(CONFIG), str(out)],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    dockerfile = out.read_text()
    assert dockerfile.startswith("FROM langchain/langgraph-api:3.13")
    assert "apt-get install -y --no-install-recommends git" in dockerfile
    graphs = json.loads(dockerfile.split("ENV LANGSERVE_GRAPHS='", 1)[1].split("'", 1)[0])
    assert graphs == {
        "autoresearch_session": "/deps/autoresearch/engine/loop.py:autoresearch_session",
        "review_proposals": "/deps/autoresearch/engine/review.py:review_proposals",
    }


def test_dockerignore_keeps_secrets_and_scratch_out_of_the_image():
    """`ADD . /deps/autoresearch` copies the whole build context; `.env` and `.venv/` live in it."""
    patterns = {
        line.strip() for line in (ROOT / ".dockerignore").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    for required in (".env", ".venv/", ".langgraph_api/", "tests/", "dev/"):
        assert required in patterns, f".dockerignore must list {required}"
