"""`engine/loop.py`: `autoresearch_session` end to end with scripted agents, a fake judge model and `MemorySaver`.

Covers spec 3 + refinements 1-2: checkpoint-0 pause with the seed already on origin, `stop`, `continue` + steer,
experiment 1 without an incumbent, keep / discard / error rows, stray revert noted in the row, one commit per
attempt, the cap, and that no agent step or judge call is repeated when the entrypoint replays after a resume.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from engine import loop
from engine.tasks import steps as steps_mod
from engine.tasks.judge import DimScore, JudgeAnswer
from engine.tasks.log import parse_tsv
from engine.tasks.rubric import CORE_DIMENSIONS, ExtraDimension, RubricExtras
from tests.conftest import BOOTSTRAP, SESSION_REL, bare, git, head, seed_session, show, subjects

EXTRA = ExtraDimension(name="Vertical focus", description="Names one concrete customer segment and stays with it.")
DIM_IDS = [d.id for d in CORE_DIMENSIONS] + ["vertical_focus"]

_TARGET = re.compile(r"Write the (combination|merged decomposition|recommendations) to: (\S+)")
_ATTEMPT = re.compile(r"/attempts/(\d+)/")



class ScriptedAgents:
    """Stands in for `create_deep_agent`: writes the file each brief asks for.

    `combos[n]` is the framework list for attempt `n`'s combination (`combos[0]` is the seed). Briefs in `fail`
    raise instead of writing; briefs in `stray` also drop a file outside the session allowlist.
    """

    def __init__(self, combos: dict[int, list[str]], fail=(), stray=()):
        self.combos = combos
        self.fail = set(fail)
        self.stray = set(stray)
        self.briefs: list[tuple[str, int, str]] = []

    def __call__(self, *, model, root, system_prompt, subagents=None):
        return _Agent(self, Path(root))

    @property
    def kinds(self) -> list[tuple[str, int]]:
        return [(kind, n) for kind, n, _brief in self.briefs]


class _Agent:
    def __init__(self, owner: ScriptedAgents, root: Path):
        self.owner = owner
        self.root = root

    def invoke(self, inputs, config=None):
        brief = str(inputs["messages"][-1].content)
        kind, vpath = _TARGET.search(brief).groups()
        m = _ATTEMPT.search(vpath)
        n = int(m.group(1)) if m else 0
        self.owner.briefs.append((kind, n, brief))
        if (kind, n) in self.owner.fail:
            raise RuntimeError(f"{kind} {n} exploded")
        if kind == "combination":
            fw = self.owner.combos[n]
            text = f"---\nframeworks: [{', '.join(fw)}]\nnote: attempt {n} tries {'+'.join(fw)}\n---\n\n# Combination {n}\n"
        else:
            text = f"# {kind} for attempt {n}\n"
        p = self.root / vpath.lstrip("/")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        if (kind, n) in self.owner.stray:
            (self.root / "STRAY.txt").write_text("should never be committed\n", encoding="utf-8")
        return {"messages": []}


def answer(candidate: int, incumbent: int | None) -> JudgeAnswer:
    """Same candidate score on every dimension; the incumbent's frozen scores come from best/score.json, so
    `incumbent` is accepted for the call sites' readability and ignored."""
    return JudgeAnswer(
        deficiencies=[f"{i}: none — scripted" if candidate == 10 else f"{i}: scripted" for i in DIM_IDS],
        scores=[DimScore(dimension_id=i, score=candidate) for i in DIM_IDS],
        rationale="scripted",
    )


def cfg(thread: str) -> dict:
    return {"configurable": {"thread_id": thread}}


@pytest.fixture
def harness(settings, structured_fake, monkeypatch):
    """`harness(combos=..., judge_outputs=[...])` -> (graph, agents, model) with every seam stubbed."""

    def make(*, combos, judge_outputs, fail=(), stray=()):
        agents = ScriptedAgents(combos, fail, stray)
        model = structured_fake([RubricExtras(dimensions=[EXTRA]), *judge_outputs])
        monkeypatch.setattr(steps_mod, "default_agent_factory", agents)
        monkeypatch.setattr(loop, "make_model", lambda *a, **k: model)
        return loop.build_graph(checkpointer=MemorySaver()), agents, model

    return make


# --- origin inspection -------------------------------------------------------------


def files(origin: str, branch: str) -> set[str]:
    out = git(bare(origin), "ls-tree", "-r", "--name-only", branch, "--", SESSION_REL)
    return {p.removeprefix(SESSION_REL + "/") for p in out.splitlines()}


# --- tests -------------------------------------------------------------------------


def test_checkpoint0_pauses_after_the_seed_is_on_origin(harness, origin, session_branch):
    graph, agents, model = harness(combos={0: ["swot", "five-whys"]}, judge_outputs=[])
    out = graph.invoke({"branch": session_branch}, cfg("t0"))
    payload = out["__interrupt__"][0].value
    assert payload["kind"] == "checkpoint0"
    assert "### vertical_focus: Vertical focus" in payload["rubric"]
    assert payload["seed"]["frameworks"] == ["swot", "five-whys"]
    assert payload["seed"]["content"].startswith("---\nframeworks: [swot, five-whys]")
    assert "resume" in payload
    assert subjects(origin, session_branch) == ["checkpoint 0 draft: seed combination"]
    assert "best/combination-with-explanations.md" in files(origin, session_branch)
    assert "rubric.md" not in files(origin, session_branch)
    assert parse_tsv(show(origin, session_branch, "experiments.tsv")) == []
    assert agents.kinds == [("combination", 0)]
    assert len(model.calls) == 1  # rubric extras only


def test_stop_at_checkpoint0_returns_a_summary_without_writing_the_rubric(harness, origin, session_branch):
    graph, _agents, _model = harness(combos={0: ["swot"]}, judge_outputs=[])
    graph.invoke({"branch": session_branch}, cfg("t1"))
    out = graph.invoke(Command(resume={"action": "stop"}), cfg("t1"))
    assert out["stopped"] == "checkpoint0"
    assert out["attempts"] == 0 and out["kept"] == 0 and out["best_total"] is None
    assert out["branch"] == session_branch and out["head"] == head(origin, session_branch)
    assert "rubric.md" not in files(origin, session_branch)


def test_keep_discard_steer_cap_and_no_replayed_steps(harness, origin, tmp_path):
    branch = seed_session(origin, tmp_path, max_experiments=3)
    graph, agents, model = harness(
        combos={0: ["swot", "five-whys"], 2: ["mece", "swot"], 3: ["issue-hypothesis-trees"]},
        judge_outputs=[answer(6, None), answer(4, 6), answer(8, 6)],
    )
    c = cfg("t2")
    graph.invoke({"branch": branch}, c)

    # continue + steer -> rubric approved, experiment 1 has no incumbent and is kept -> pause
    out = graph.invoke(Command(resume={"action": "continue", "steer": "Focus on restaurants."}), c)
    p = out["__interrupt__"][0].value
    assert p["kind"] == "new_best" and p["n"] == 1
    assert p["verdict"]["candidate_total"] == 36 and p["verdict"]["incumbent_total"] is None
    assert p["verdict"]["incumbent"] is None
    assert p["trend"] == [{"n": 1, "candidate_total": 36, "incumbent_total": None, "kept": "1"}]
    assert subjects(origin, branch) == [
        "checkpoint 0 draft: seed combination",
        "checkpoint 0: rubric approved",
        "exp 1: KEEP 36 vs -",
    ]
    assert "### vertical_focus: Vertical focus" in show(origin, branch, "rubric.md")

    # continue + steer -> experiment 2 loses (no pause), experiment 3 wins -> pause
    out = graph.invoke(Command(resume={"action": "continue", "steer": "Now try MECE."}), c)
    p = out["__interrupt__"][0].value
    assert p["kind"] == "new_best" and p["n"] == 3
    assert p["verdict"]["candidate_total"] == 48 and p["verdict"]["incumbent_total"] == 36
    assert p["verdict"]["incumbent"] == {i: 6 for i in DIM_IDS}

    # continue with nothing to say -> cap reached -> summary
    out = graph.invoke(Command(resume={"action": "continue"}), c)
    assert out == {
        "branch": branch,
        "head": head(origin, branch),
        "attempts": 3,
        "kept": 2,
        "best_total": 48,
        "best_experiment": 3,
        "stopped": "max_experiments",
    }

    rows = parse_tsv(show(origin, branch, "experiments.tsv"))
    assert [(r.n, r.frameworks, r.candidate_total, r.incumbent_total, r.kept) for r in rows] == [
        (1, ["swot", "five-whys"], 36, None, "1"),
        (2, ["mece", "swot"], 24, 36, "0"),
        (3, ["issue-hypothesis-trees"], 48, 36, "1"),
    ]
    assert rows[0].note == "attempt 0 tries swot+five-whys" and rows[2].note == "attempt 3 tries issue-hypothesis-trees"
    assert subjects(origin, branch) == [
        "checkpoint 0 draft: seed combination",
        "checkpoint 0: rubric approved",
        "exp 1: KEEP 36 vs -",
        "steer after exp 1",
        "exp 2: discard 24 vs 36",
        "exp 3: KEEP 48 vs 36",
    ]
    notes = show(origin, branch, "notes.md")
    steering = notes[notes.index("## Human steering") :]
    assert "Focus on restaurants." in steering and "Now try MECE." in steering
    assert steering.index("Focus on restaurants.") < steering.index("Now try MECE.")

    committed = files(origin, branch)
    assert {f for f in committed if f.startswith("best/")} == {
        "best/combination-with-explanations.md",
        "best/decomposition.md",
        "best/recommendations.md",
        "best/score.json",
    }
    assert not any(f.startswith("attempts/") for f in committed)
    score = json.loads(show(origin, branch, "best/score.json"))
    assert score["experiment"] == 3 and score["candidate_total"] == 48 and score["incumbent_total"] == 36
    assert show(origin, branch, "best/recommendations.md") == "# recommendations for attempt 3"  # git() strips stdout
    assert show(origin, branch, "best/combination-with-explanations.md").startswith("---\nframeworks: [issue-hypothesis-trees]")

    # every agent step and judge call ran exactly once despite three replays of the entrypoint body
    assert agents.kinds == [
        ("combination", 0),
        ("merged decomposition", 1),
        ("recommendations", 1),
        ("combination", 2),
        ("merged decomposition", 2),
        ("recommendations", 2),
        ("combination", 3),
        ("merged decomposition", 3),
        ("recommendations", 3),
    ]
    assert len(model.calls) == 4  # extras + three judge calls
    exp2_brief = next(b for k, n, b in agents.briefs if (k, n) == ("combination", 2))
    assert "1: swot+five-whys -> kept 1, 36 vs -" in exp2_brief


def test_failed_step_logs_an_error_row_and_the_loop_continues(harness, origin, tmp_path):
    branch = seed_session(origin, tmp_path, max_experiments=2)
    graph, agents, model = harness(
        combos={0: ["swot"], 2: ["mece"]},
        judge_outputs=[answer(5, None)],
        fail={("merged decomposition", 1)},
        stray={("recommendations", 2)},
    )
    c = cfg("t3")
    graph.invoke({"branch": branch}, c)
    out = graph.invoke(Command(resume={"action": "continue"}), c)
    p = out["__interrupt__"][0].value
    assert p["kind"] == "new_best" and p["n"] == 2  # experiment 1 errored without a pause

    rows = parse_tsv(show(origin, branch, "experiments.tsv"))
    assert rows[0].n == 1 and rows[0].kept == "error" and rows[0].frameworks == ["swot"]
    assert rows[0].candidate_total is None and rows[0].incumbent_total is None
    assert "RuntimeError: merged decomposition 1 exploded" in rows[0].note
    assert rows[1].n == 2 and rows[1].kept == "1" and rows[1].incumbent_total is None and rows[1].candidate_total == 30
    assert "reverted stray changes: STRAY.txt" in rows[1].note
    assert subjects(origin, branch)[2].startswith("exp 1: ERROR ")
    assert subjects(origin, branch)[3] == "exp 2: KEEP 30 vs -"
    assert "STRAY.txt" not in git(bare(origin), "ls-tree", "-r", "--name-only", branch)
    assert ("recommendations", 1) not in agents.kinds  # short-circuited after the decompose failure
    assert len(model.calls) == 2  # extras + one judge call; the errored attempt was never judged

    out = graph.invoke(Command(resume={"action": "stop"}), c)
    assert out["stopped"] == "stop" and out["attempts"] == 2 and out["kept"] == 1 and out["best_total"] == 30


def test_judge_failure_after_its_repair_retry_logs_an_error_row_and_the_loop_continues(harness, origin, tmp_path):
    """Spec 7: malformed / failing judge output gets one repair turn, then the attempt is `kept=error` and the loop goes on."""
    branch = seed_session(origin, tmp_path, max_experiments=2)
    graph, agents, model = harness(
        combos={0: ["swot"], 2: ["mece"]},
        judge_outputs=[RuntimeError("judge exploded"), RuntimeError("judge exploded again"), answer(5, None)],
    )
    c = cfg("t4")
    graph.invoke({"branch": branch}, c)
    out = graph.invoke(Command(resume={"action": "continue"}), c)
    p = out["__interrupt__"][0].value
    assert p["kind"] == "new_best" and p["n"] == 2  # experiment 1 errored without a pause; experiment 2 ran

    rows = parse_tsv(show(origin, branch, "experiments.tsv"))
    assert [(r.n, r.frameworks, r.kept, r.candidate_total, r.incumbent_total) for r in rows] == [
        (1, ["swot"], "error", None, None),
        (2, ["mece"], "1", 30, None),
    ]
    assert "JudgeError" in rows[0].note and "judge exploded again" in rows[0].note
    subj = subjects(origin, branch)
    assert subj[2].startswith("exp 1: ERROR JudgeError") and len(subj[2]) <= len("exp 1: ERROR ") + loop.ERROR_SUBJECT_CHARS
    assert subj[3] == "exp 2: KEEP 30 vs -"
    assert json.loads(show(origin, branch, "best/score.json"))["experiment"] == 2
    assert len(model.calls) == 4  # extras + experiment 1's judge call and its repair turn + experiment 2's judge
    assert "rejected" in str(model.calls[2][1][-1].content).lower() or "previous" in str(model.calls[2][1][-1].content).lower()
    assert [k for k in agents.kinds if k[1] == 1] == [("merged decomposition", 1), ("recommendations", 1)]  # the attempt was fully built


def test_module_exports_a_graph_without_a_checkpointer():
    from langgraph.pregel import Pregel

    assert isinstance(loop.autoresearch_session, Pregel)
    assert loop.autoresearch_session.checkpointer is None
