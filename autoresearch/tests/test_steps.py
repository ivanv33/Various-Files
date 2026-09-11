"""Agent steps (`propose` / `decompose` / `recommend`) driven by a stub agent factory.

The stub stands in for `create_deep_agent`: it records the system prompt, subagents, brief and
config it was given and writes whatever files the test asks for, so every contract of the steps
(paths, briefs, recursion limits, error handling, frontmatter parsing) is checked offline.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from engine.catalog import load_seed_catalog
from engine.tasks import decompose, propose, recommend
from engine.tasks.log import HEADER, LogRow, append_row
from engine.tasks.rubric import CORE_DIMENSIONS, render_rubric
from engine.tasks.steps import LIMITS, brief_header, default_agent_factory, run_step
from engine.workspace import Workspace

SLUG = "demo"
BRANCH = f"autoresearch/{SLUG}"
SESSION_REL = f"autoresearch/sessions/{SLUG}"
TRANSCRIPT_REL = "tbpn-transcripts/transcripts/short.md"
MISSION = "Find the underserved vertical the guests keep circling"

SEED_COMBO = (
    "---\n"
    "frameworks: [star-par, five-whys]\n"
    "note: start from narrative plus causal digging\n"
    "---\n\n"
    "# Combination\n\nSTAR to structure each story, Five Whys on the result.\n"
)


def make_session(tmp_path: Path, *, transcript: str = "Speaker A: restaurants need AI.\nSpeaker B: nobody sells it.\n") -> Workspace:
    root = tmp_path / "clone"
    ws = Workspace(root, BRANCH)
    ws.write("metadata.json", json.dumps({"mission": MISSION, "transcript_path": TRANSCRIPT_REL, "max_experiments": 3}))
    ws.write("catalog.json", json.dumps(load_seed_catalog()))
    ws.write("notes.md", "# Notes\n\n## Insights\n\n## Human steering\n")
    ws.write("experiments.tsv", HEADER + "\n")
    ws.write("rubric.md", render_rubric(CORE_DIMENSIONS, []))
    t = root / TRANSCRIPT_REL
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text(transcript, encoding="utf-8")
    return ws


class StubAgent:
    """Writes `writes` (virtual path -> text) under `root` on invoke; optionally raises first."""

    def __init__(self, root: str, writes: dict[str, str], raise_exc: Exception | None = None):
        self.root = Path(root)
        self.writes = writes
        self.raise_exc = raise_exc
        self.calls: list[tuple[dict, dict | None]] = []

    def invoke(self, inputs, config=None):
        self.calls.append((inputs, config))
        if self.raise_exc is not None:
            raise self.raise_exc
        for vpath, text in self.writes.items():
            p = self.root / vpath.lstrip("/")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        return {"messages": []}


class StubFactory:
    def __init__(self, writes: dict[str, str] | None = None, raise_exc: Exception | None = None):
        self.writes = writes or {}
        self.raise_exc = raise_exc
        self.created: list[dict] = []
        self.agents: list[StubAgent] = []

    def __call__(self, *, model, root, system_prompt, subagents=None):
        self.created.append({"model": model, "root": root, "system_prompt": system_prompt, "subagents": subagents})
        agent = StubAgent(root, self.writes, self.raise_exc)
        self.agents.append(agent)
        return agent

    @property
    def brief(self) -> str:
        inputs, _config = self.agents[-1].calls[-1]
        return str(inputs["messages"][-1].content)

    @property
    def config(self) -> dict:
        return self.agents[-1].calls[-1][1] or {}


# --- shared plumbing -------------------------------------------------------------


def test_brief_header_names_mission_and_virtual_paths(tmp_path: Path):
    ws = make_session(tmp_path)
    header = brief_header(ws)
    assert MISSION in header
    assert f"/{SESSION_REL}" in header
    assert f"/{TRANSCRIPT_REL}" in header
    assert f"/{SESSION_REL}/rubric.md" in header
    assert "experiments.tsv" in header and "notes.md" in header


def test_run_step_returns_path_content_and_no_error_on_success(tmp_path: Path):
    ws = make_session(tmp_path)
    out = ws.attempt_rel(1, "thing.md")
    factory = StubFactory({f"/{out}": "hello\n"})
    result = run_step("model", ws, prompt_name="recommend", prompt_vars={}, brief="do it", output_rel=out, recursion_limit=7, agent_factory=factory)
    assert result == {"path": out, "content": "hello\n", "error": None}
    assert factory.created[0]["model"] == "model"
    assert factory.created[0]["root"] == str(ws.root)
    assert factory.config["recursion_limit"] == 7
    assert factory.brief == "do it"


def test_run_step_reports_agent_exception_as_error(tmp_path: Path):
    ws = make_session(tmp_path)
    out = ws.attempt_rel(1, "thing.md")
    factory = StubFactory(raise_exc=RuntimeError("recursion limit of 7 reached"))
    result = run_step("model", ws, prompt_name="recommend", prompt_vars={}, brief="b", output_rel=out, recursion_limit=7, agent_factory=factory)
    assert result["path"] == out and result["content"] == ""
    assert "RuntimeError" in result["error"] and "recursion limit of 7 reached" in result["error"]


def test_run_step_reports_missing_or_empty_output_as_error(tmp_path: Path):
    ws = make_session(tmp_path)
    out = ws.attempt_rel(1, "thing.md")
    missing = run_step("m", ws, prompt_name="recommend", prompt_vars={}, brief="b", output_rel=out, recursion_limit=7, agent_factory=StubFactory({}))
    assert missing["error"] and "missing or empty" in missing["error"] and out in missing["error"]
    empty = run_step("m", ws, prompt_name="recommend", prompt_vars={}, brief="b", output_rel=out, recursion_limit=7, agent_factory=StubFactory({f"/{out}": "  \n"}))
    assert empty["error"] and "missing or empty" in empty["error"]


def test_limits_match_refinement_6():
    assert LIMITS == {"propose": 60, "decompose": 150, "recommend": 80}


class ToolCallingFake(GenericFakeChatModel):
    """`GenericFakeChatModel` that accepts `bind_tools` so a real deep agent can run its scripted tool calls."""

    def bind_tools(self, tools, **kwargs):
        return self


def test_default_agent_factory_denies_the_git_dir(tmp_path: Path):
    """Belt and braces for the credential hygiene: even if something leaked into `.git/`, agents cannot read it."""
    ws = make_session(tmp_path)
    (ws.root / ".git").mkdir()
    (ws.root / ".git" / "config").write_text('[remote "origin"]\n\turl = https://x:SECRET@h/r.git\n')
    calls = [
        AIMessage(content="", tool_calls=[{"name": "read_file", "args": {"file_path": "/.git/config"}, "id": "c1"}]),
        AIMessage(content="", tool_calls=[{"name": "ls", "args": {"path": "/.git"}, "id": "c2"}]),
        AIMessage(content="", tool_calls=[{"name": "write_file", "args": {"file_path": "/.git/hooks/pre-commit", "content": "x"}, "id": "c3"}]),
        AIMessage(content="", tool_calls=[{"name": "read_file", "args": {"file_path": f"/{SESSION_REL}/metadata.json"}, "id": "c4"}]),
        AIMessage(content="done"),
    ]
    agent = default_agent_factory(model=ToolCallingFake(messages=iter(calls)), root=str(ws.root), system_prompt="x")
    out = agent.invoke({"messages": [HumanMessage(content="go")]}, config={"recursion_limit": 20})
    tool_msgs = {m.tool_call_id: str(m.content) for m in out["messages"] if isinstance(m, ToolMessage)}
    assert "permission denied" in tool_msgs["c1"] and "SECRET" not in tool_msgs["c1"]
    assert "SECRET" not in tool_msgs["c2"] and "config" not in tool_msgs["c2"]
    assert "permission denied" in tool_msgs["c3"] and not (ws.root / ".git" / "hooks").exists()
    assert MISSION in tool_msgs["c4"]  # everything else stays readable


# --- propose ---------------------------------------------------------------------


def test_parse_combination_reads_frontmatter_forms():
    fw, note = propose.parse_combination(SEED_COMBO)
    assert fw == ["star-par", "five-whys"] and note == "start from narrative plus causal digging"
    fw, note = propose.parse_combination("---\nframeworks: star-par + five-whys\nnote: 'quoted'\n---\nbody\n")
    assert fw == ["star-par", "five-whys"] and note == "quoted"
    fw, note = propose.parse_combination("---\nframeworks:\n  - star-par\n  - five-whys\n---\nbody\n")
    assert fw == ["star-par", "five-whys"] and note == ""
    assert propose.parse_combination("# no frontmatter\n") == ([], "")


def test_propose_seed_writes_best_combination_and_parses_frontmatter(tmp_path: Path):
    ws = make_session(tmp_path)
    out = ws.rel("best/combination-with-explanations.md")
    factory = StubFactory({f"/{out}": SEED_COMBO})
    result = propose.run("model", ws, None, seed=True, agent_factory=factory)
    assert result["path"] == out and result["content"] == SEED_COMBO and result["error"] is None
    assert result["frameworks"] == ["star-par", "five-whys"]
    assert result["note"] == "start from narrative plus causal digging"
    assert factory.config["recursion_limit"] == LIMITS["propose"]
    system = factory.created[0]["system_prompt"]
    assert "frameworks:" in system and "combination" in system.lower()
    brief = factory.brief
    assert f"/{out}" in brief and MISSION in brief and f"/{SESSION_REL}/catalog.json" in brief
    assert "seed" in brief.lower()
    assert factory.created[0]["subagents"] in (None, [])


def test_propose_experiment_n_targets_attempt_dir_and_lists_tried_sets(tmp_path: Path):
    ws = make_session(tmp_path)
    ws.write("best/combination-with-explanations.md", SEED_COMBO)
    append_row(ws.root, ws.session_rel, LogRow(n=1, frameworks=["star-par", "five-whys"], candidate_total=30, kept="1", note="seed"))
    out = ws.attempt_rel(2, "combination-with-explanations.md")
    factory = StubFactory({f"/{out}": "---\nframeworks: [swot]\nnote: try a single lens\n---\n# SWOT only\n"})
    result = propose.run("model", ws, 2, agent_factory=factory)
    assert result["path"] == out and result["frameworks"] == ["swot"] and result["note"] == "try a single lens"
    brief = factory.brief
    assert f"/{out}" in brief
    assert "star-par+five-whys" in brief  # already-tried sets are spelled out
    assert f"/{SESSION_REL}/best/combination-with-explanations.md" in brief
    assert "seed combination" not in brief.lower()  # not seed mode


def test_propose_requires_n_unless_seed(tmp_path: Path):
    ws = make_session(tmp_path)
    with pytest.raises(ValueError):
        propose.run("model", ws, None, agent_factory=StubFactory())


def test_propose_without_frameworks_frontmatter_is_an_error(tmp_path: Path):
    ws = make_session(tmp_path)
    out = ws.attempt_rel(1, "combination-with-explanations.md")
    result = propose.run("model", ws, 1, agent_factory=StubFactory({f"/{out}": "# Combination\n\nno frontmatter\n"}))
    assert result["error"] and "frameworks" in result["error"]
    assert result["frameworks"] == [] and result["content"]  # content kept for inspection


def test_propose_agent_failure_is_an_error_result(tmp_path: Path):
    ws = make_session(tmp_path)
    result = propose.run("model", ws, 1, agent_factory=StubFactory(raise_exc=TimeoutError("slow")))
    assert result["error"] and "TimeoutError" in result["error"]
    assert result["frameworks"] == [] and result["note"] == ""


def test_use_seed_copies_best_combination_into_attempt_dir(tmp_path: Path):
    ws = make_session(tmp_path)
    ws.write("best/combination-with-explanations.md", SEED_COMBO)
    result = propose.use_seed(ws, 1)
    assert result["path"] == ws.attempt_rel(1, "combination-with-explanations.md")
    assert result["content"] == SEED_COMBO and result["error"] is None
    assert result["frameworks"] == ["star-par", "five-whys"]
    assert ws.attempt_dir(1).joinpath("combination-with-explanations.md").read_text() == SEED_COMBO


def test_use_seed_without_seed_is_an_error_result(tmp_path: Path):
    ws = make_session(tmp_path)
    result = propose.use_seed(ws, 1)
    assert result["error"] and "best/combination-with-explanations.md" in result["error"]


# --- decompose -------------------------------------------------------------------


def test_decompose_materializes_combination_and_fans_out_with_subagent(tmp_path: Path):
    ws = make_session(tmp_path)
    combo = {"path": ws.attempt_rel(1, "combination-with-explanations.md"), "content": SEED_COMBO, "error": None}
    out = ws.attempt_rel(1, "decomposition.md")
    factory = StubFactory({f"/{out}": "# Decomposition\n\n## star-par\n..."})
    result = decompose.run("model", ws, 1, combo, agent_factory=factory)
    assert result == {"path": out, "content": "# Decomposition\n\n## star-par\n...", "error": None}
    # the cached combination was written to disk before the agent ran
    assert (ws.root / combo["path"]).read_text() == SEED_COMBO
    assert factory.config["recursion_limit"] == LIMITS["decompose"]
    subagents = factory.created[0]["subagents"]
    assert len(subagents) == 1 and subagents[0]["name"] == "framework-decomposer"
    assert "transcript" in subagents[0]["system_prompt"].lower()
    brief = factory.brief
    assert f"/{combo['path']}" in brief and f"/{TRANSCRIPT_REL}" in brief and f"/{out}" in brief
    assert "star-par" in brief and "five-whys" in brief  # frameworks named so the agent can fan out
    assert "framework-decomposer" in factory.created[0]["system_prompt"]


def test_decompose_refuses_a_failed_combination(tmp_path: Path):
    ws = make_session(tmp_path)
    combo = {"path": ws.attempt_rel(1, "combination-with-explanations.md"), "content": "", "error": "boom"}
    result = decompose.run("model", ws, 1, combo, agent_factory=StubFactory())
    assert result["error"] and "combination" in result["error"] and "boom" in result["error"]


# --- recommend -------------------------------------------------------------------


def test_recommend_materializes_decomposition_and_writes_recommendations(tmp_path: Path):
    ws = make_session(tmp_path)
    decomp = {"path": ws.attempt_rel(1, "decomposition.md"), "content": "# Decomposition\n\nfindings\n", "error": None}
    out = ws.attempt_rel(1, "recommendations.md")
    factory = StubFactory({f"/{out}": "# Recommendations\n\n1. Call three chains.\n"})
    result = recommend.run("model", ws, 1, decomp, agent_factory=factory)
    assert result == {"path": out, "content": "# Recommendations\n\n1. Call three chains.\n", "error": None}
    assert (ws.root / decomp["path"]).read_text() == decomp["content"]
    assert factory.config["recursion_limit"] == LIMITS["recommend"]
    brief = factory.brief
    assert f"/{decomp['path']}" in brief and f"/{out}" in brief and MISSION in brief
    assert f"/{SESSION_REL}/rubric.md" in brief
    assert factory.created[0]["subagents"] in (None, [])


def test_recommend_refuses_a_failed_decomposition(tmp_path: Path):
    ws = make_session(tmp_path)
    decomp = {"path": ws.attempt_rel(1, "decomposition.md"), "content": "", "error": "limit"}
    result = recommend.run("model", ws, 1, decomp, agent_factory=StubFactory())
    assert result["error"] and "decomposition" in result["error"] and "limit" in result["error"]


# --- live -------------------------------------------------------------------------


@pytest.mark.live
def test_steps_live_on_short_transcript_write_attempts_1(tmp_path: Path):
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    from engine.config import make_model

    repo_root = Path(__file__).resolve().parents[2]
    transcript = repo_root / "tbpn-transcripts/transcripts/2025-10-25_diet-tbpn-october-24th-2025.md"
    ws = make_session(tmp_path, transcript=transcript.read_text(encoding="utf-8"))
    model = make_model()
    slugs = {e["slug"] for e in load_seed_catalog()}

    seed = propose.run(model, ws, None, seed=True)
    assert seed["error"] is None, seed["error"]
    assert seed["frameworks"] and set(seed["frameworks"]) <= slugs, seed["frameworks"]
    assert ws.has("best/combination-with-explanations.md")

    combo = propose.use_seed(ws, 1)
    decomp = decompose.run(model, ws, 1, combo)
    assert decomp["error"] is None, decomp["error"]
    assert len(decomp["content"]) > 500

    recs = recommend.run(model, ws, 1, decomp)
    assert recs["error"] is None, recs["error"]
    assert len(recs["content"]) > 300
    for name in ("combination-with-explanations.md", "decomposition.md", "recommendations.md"):
        assert ws.has(f"attempts/1/{name}")
