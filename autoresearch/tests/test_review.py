"""`engine/review.py` + `engine/tasks/proposals.py`: the `review_proposals` graph (spec 5).

Offline: a temp bare origin, hand-written proposals pushed to the session branch, `structured_fake` as the
model. Covers accept new-framework (catalog entry), accept rubric-change (rubric re-rendered, notes line, no
tsv row), reject (frontmatter only), deterministic rejections that skip the model, the repair retry, a model
failure that leaves the proposal open, and the no-op run (no commit).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from engine.tasks import proposals as props
from engine.tasks.log import HEADER, parse_tsv
from engine.tasks.rubric import CORE_DIMENSIONS, Dimension, ExtraDimension, parse_rubric, render_rubric
from tests.conftest import SESSION_REL, git

EXTRA = Dimension(id="vertical_focus", name="Vertical focus", description="Names one customer segment and stays with it.", kind="extra")
RUBRIC = render_rubric(CORE_DIMENSIONS, [EXTRA])
NOTES = "# Notes\n\n## Insights\n\n- none yet\n\n## Human steering\n\n- 2026-09-10T00:00:00Z: stay concrete\n"
BOOTSTRAP = "session demo: bootstrap"

FRAMEWORK_OPEN = (
    "---\nstatus: open\nexperiment: 2\ntitle: Add Jobs-to-be-Done\n---\n"
    "# New framework: jobs-to-be-done\n\nThe catalog has no demand-side lens; guests keep describing hiring criteria.\n"
)
RUBRIC_OPEN = (
    "---\nstatus: open\nexperiment: 3\ntitle: Reward time to first dollar\n---\n"
    "# Rubric change\n\nReplace vertical_focus: every kept attempt already names a segment; reward speed to revenue instead.\n"
)
DECIDED = "---\nstatus: accepted\nexperiment: 1\ndecision_reason: earlier run\n---\n# Rubric change: bar\n"

JTBD = props.ProposedFramework(
    name="Jobs to be Done",
    category="02-strategic-and-business",
    summary="Decomposes demand into the job a customer hires a product for, the circumstances and the hiring criteria.",
    when_to_use="Use when the transcript describes why customers switch. Failure modes: job stated as a feature; no circumstance.",
)
ACCEPT_FW = props.FrameworkDecision(accept=True, reason="Fills the missing demand-side lens.", entry=JTBD)
REJECT_FW = props.FrameworkDecision(accept=False, reason="Already covered by mece and issue trees.")
TTFD = ExtraDimension(name="Time to first dollar", description="A 10 names the first paying customer and a date; a 1 never mentions revenue.")
ACCEPT_RUBRIC = props.RubricDecision(accept=True, reason="Kept attempts all name a segment already.", dimensions=[TTFD])


# --- origin helpers ------------------------------------------------------------------


def bare(origin: str) -> Path:
    return Path(origin.removeprefix("file://"))


def subjects(origin: str, branch: str) -> list[str]:
    log = git(bare(origin), "log", "--reverse", "--format=%s", branch).splitlines()
    return log[log.index(BOOTSTRAP) + 1 :]


def show(origin: str, branch: str, name: str) -> str:
    return git(bare(origin), "show", f"{branch}:{SESSION_REL}/{name}")


def head(origin: str, branch: str) -> str:
    return git(bare(origin), "rev-parse", branch)


def push_files(origin: str, branch: str, work: Path, files: dict[str, str]) -> None:
    """Commit session files (session-relative names) to the branch on origin, like an earlier run would."""
    clone = work / f"pusher-{len(list(work.iterdir()))}"
    git(work, "clone", "-q", "--branch", branch, origin, str(clone))
    for name, text in files.items():
        p = clone / SESSION_REL / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "earlier run")
    git(clone, "push", "-q", "origin", branch)


def rel(name: str) -> str:
    return f"{SESSION_REL}/proposals/{name}"


@pytest.fixture
def reviewer(settings, structured_fake, monkeypatch):
    """`reviewer([decision, ...]) -> (graph, model)`; the model's queued outputs are consumed in proposal order."""
    from engine import review

    def make(outputs):
        model = structured_fake(outputs)
        monkeypatch.setattr(review, "make_model", lambda *a, **k: model)
        return review.review_proposals, model

    return make


# --- pure helpers --------------------------------------------------------------------


def test_frontmatter_parse_and_set():
    fields, body = props.parse_frontmatter(FRAMEWORK_OPEN)
    assert fields == {"status": "open", "experiment": "2", "title": "Add Jobs-to-be-Done"}
    assert body.startswith("# New framework: jobs-to-be-done")
    updated = props.set_frontmatter(FRAMEWORK_OPEN, status="accepted", decision_reason="fills a\n  gap")
    assert updated.startswith("---\nstatus: accepted\nexperiment: 2\ntitle: Add Jobs-to-be-Done\ndecision_reason: fills a gap\n---\n# New")
    assert props.parse_frontmatter(updated)[0]["status"] == "accepted"
    assert props.parse_frontmatter(updated)[1] == body
    assert props.set_frontmatter("# bare\n", status="rejected", decision_reason="x") == "---\nstatus: rejected\ndecision_reason: x\n---\n# bare\n"
    assert props.parse_frontmatter("# bare\n") == ({}, "# bare\n")
    assert props.proposal_status(DECIDED) == "accepted" and props.proposal_status("no frontmatter") == "open"


def test_proposal_kind_from_file_name():
    assert props.proposal_kind(rel("new-framework-jobs-to-be-done.md")) == ("new-framework", "jobs-to-be-done")
    assert props.proposal_kind("proposals/rubric-change-ttfd.md") == ("rubric-change", "ttfd")
    assert props.proposal_kind("proposals/idea.md") == ("unknown", "")
    assert props.proposal_kind("proposals/new-framework-.md") == ("unknown", "")


def test_add_rubric_change_note_creates_or_extends_the_section():
    once = props.add_rubric_change_note(NOTES, "rubric-change-a.md accepted", timestamp="T1")
    assert once.endswith("## Human steering\n\n- 2026-09-10T00:00:00Z: stay concrete\n\n## Rubric changes\n\n- T1: rubric-change-a.md accepted\n")
    twice = props.add_rubric_change_note(once, "rubric-change-b.md accepted", timestamp="T2")
    assert twice.endswith("## Rubric changes\n\n- T1: rubric-change-a.md accepted\n- T2: rubric-change-b.md accepted\n")
    assert twice.count("## Rubric changes") == 1 and "## Human steering" in twice


# --- the graph -----------------------------------------------------------------------


def test_accept_new_framework_appends_a_catalog_entry_and_commits(reviewer, origin, session_branch, tmp_path):
    push_files(origin, session_branch, tmp_path, {"rubric.md": RUBRIC, "proposals/new-framework-jobs-to-be-done.md": FRAMEWORK_OPEN})
    graph, model = reviewer([ACCEPT_FW])
    out = graph.invoke({"branch": session_branch})

    assert (out["accepted"], out["rejected"], out["errors"]) == (1, 0, 0)
    assert out["open"] == [] and out["decided"] == [rel("new-framework-jobs-to-be-done.md")]
    assert out["decisions"] == [
        {"file": rel("new-framework-jobs-to-be-done.md"), "kind": "new-framework", "status": "accepted", "reason": ACCEPT_FW.reason}
    ]
    assert out["sha"] == out["head"] == head(origin, session_branch)
    assert subjects(origin, session_branch)[-1] == "review: 1 proposal (1 accepted, 0 rejected)"

    catalog = json.loads(show(origin, session_branch, "catalog.json"))
    assert len(catalog) == 23
    assert catalog[-1] == {
        "slug": "jobs-to-be-done",
        "name": JTBD.name,
        "category": JTBD.category,
        "summary": JTBD.summary,
        "when_to_use": JTBD.when_to_use,
        "source": "proposal:new-framework-jobs-to-be-done.md",
    }
    fields, body = props.parse_frontmatter(show(origin, session_branch, "proposals/new-framework-jobs-to-be-done.md"))
    assert fields["status"] == "accepted" and fields["decision_reason"] == ACCEPT_FW.reason and fields["experiment"] == "2"
    assert body == props.parse_frontmatter(FRAMEWORK_OPEN)[1].rstrip("\n")  # `git show` output is stripped
    assert show(origin, session_branch, "rubric.md") == RUBRIC.rstrip("\n")
    assert parse_tsv(show(origin, session_branch, "experiments.tsv")) == []

    schema, messages = model.calls[0]
    assert schema is props.FrameworkDecision
    prompt = "\n".join(str(m.content) for m in messages)
    assert "Ship a great product" in prompt and "demand-side lens" in prompt and "mece" in prompt and "vertical_focus" in prompt


def test_accept_rubric_change_rewrites_extras_and_notes_without_a_log_row(reviewer, origin, session_branch, tmp_path):
    push_files(
        origin,
        session_branch,
        tmp_path,
        {"rubric.md": RUBRIC, "notes.md": NOTES, "proposals/rubric-change-time-to-first-dollar.md": RUBRIC_OPEN},
    )
    graph, model = reviewer([ACCEPT_RUBRIC])
    out = graph.invoke({"branch": session_branch})

    assert (out["accepted"], out["rejected"], out["errors"]) == (1, 0, 0)
    dims = parse_rubric(show(origin, session_branch, "rubric.md"))
    assert [d for d in dims if d.kind == "core"] == list(CORE_DIMENSIONS)
    assert [(d.id, d.name) for d in dims if d.kind == "extra"] == [("time_to_first_dollar", "Time to first dollar")]
    notes = show(origin, session_branch, "notes.md")
    assert "## Human steering\n\n- 2026-09-10T00:00:00Z: stay concrete\n" in notes
    changes = notes.split("## Rubric changes\n", 1)[1]
    assert "rubric-change-time-to-first-dollar.md" in changes and "time_to_first_dollar" in changes and ACCEPT_RUBRIC.reason in changes
    assert parse_tsv(show(origin, session_branch, "experiments.tsv")) == []
    assert len(json.loads(show(origin, session_branch, "catalog.json"))) == 22
    assert props.parse_frontmatter(show(origin, session_branch, "proposals/rubric-change-time-to-first-dollar.md"))[0]["status"] == "accepted"
    assert model.calls[0][0] is props.RubricDecision


def test_reject_changes_only_the_frontmatter(reviewer, origin, session_branch, tmp_path):
    push_files(origin, session_branch, tmp_path, {"rubric.md": RUBRIC, "proposals/new-framework-jobs-to-be-done.md": FRAMEWORK_OPEN})
    graph, _model = reviewer([REJECT_FW])
    out = graph.invoke({"branch": session_branch})

    assert (out["accepted"], out["rejected"], out["errors"]) == (0, 1, 0)
    assert out["decisions"][0]["status"] == "rejected" and out["decisions"][0]["reason"] == REJECT_FW.reason
    fields, _ = props.parse_frontmatter(show(origin, session_branch, "proposals/new-framework-jobs-to-be-done.md"))
    assert fields["status"] == "rejected" and fields["decision_reason"] == REJECT_FW.reason
    assert len(json.loads(show(origin, session_branch, "catalog.json"))) == 22
    assert subjects(origin, session_branch)[-1] == "review: 1 proposal (0 accepted, 1 rejected)"


def test_no_open_proposals_means_no_model_call_and_no_commit(reviewer, origin, session_branch, tmp_path):
    push_files(origin, session_branch, tmp_path, {"proposals/rubric-change-bar.md": DECIDED})
    before = head(origin, session_branch)
    graph, model = reviewer([])
    out = graph.invoke({"branch": session_branch})
    assert out["sha"] is None and out["head"] == before == head(origin, session_branch)
    assert out["open"] == [] and out["decided"] == [rel("rubric-change-bar.md")] and out["decisions"] == []
    assert model.calls == []


def test_review_with_no_proposals_folder(reviewer, session_branch):
    graph, model = reviewer([])
    out = graph.invoke({"branch": session_branch})
    assert out["open"] == [] and out["decided"] == [] and out["sha"] is None and model.calls == []


def test_deterministic_rejections_skip_the_model(reviewer, origin, session_branch, tmp_path):
    push_files(
        origin,
        session_branch,
        tmp_path,
        {
            "proposals/idea.md": "---\nstatus: open\n---\n# an idea\n",
            "proposals/new-framework-mece.md": FRAMEWORK_OPEN,
            "proposals/rubric-change-x.md": RUBRIC_OPEN,  # no rubric.md on the branch yet
        },
    )
    graph, model = reviewer([])
    out = graph.invoke({"branch": session_branch})
    assert (out["accepted"], out["rejected"], out["errors"]) == (0, 3, 0) and model.calls == []
    reasons = {d["file"].rsplit("/", 1)[1]: d["reason"] for d in out["decisions"]}
    assert "unsupported" in reasons["idea.md"]
    assert "mece" in reasons["new-framework-mece.md"] and "already" in reasons["new-framework-mece.md"]
    assert "rubric.md" in reasons["rubric-change-x.md"]
    for name in reasons:
        assert props.parse_frontmatter(show(origin, session_branch, f"proposals/{name}"))[0]["status"] == "rejected"
    assert subjects(origin, session_branch)[-1] == "review: 3 proposals (0 accepted, 3 rejected)"


def test_invalid_answer_gets_one_repair_turn(reviewer, origin, session_branch, tmp_path):
    push_files(origin, session_branch, tmp_path, {"rubric.md": RUBRIC, "proposals/new-framework-jobs-to-be-done.md": FRAMEWORK_OPEN})
    graph, model = reviewer([props.FrameworkDecision(accept=True, reason="yes", entry=None), ACCEPT_FW])
    out = graph.invoke({"branch": session_branch})
    assert out["accepted"] == 1 and len(model.calls) == 2
    assert "rejected" in str(model.calls[1][1][-1].content)
    assert len(json.loads(show(origin, session_branch, "catalog.json"))) == 23


def test_model_failure_leaves_that_proposal_open_and_reviews_the_rest(reviewer, origin, session_branch, tmp_path):
    push_files(
        origin,
        session_branch,
        tmp_path,
        {
            "rubric.md": RUBRIC,
            "proposals/new-framework-aaa.md": FRAMEWORK_OPEN,
            "proposals/new-framework-jobs-to-be-done.md": FRAMEWORK_OPEN,
        },
    )
    graph, model = reviewer([RuntimeError("boom"), RuntimeError("boom again"), ACCEPT_FW])
    out = graph.invoke({"branch": session_branch})
    assert (out["accepted"], out["rejected"], out["errors"]) == (1, 0, 1) and len(model.calls) == 3
    assert out["open"] == [rel("new-framework-aaa.md")] and out["decided"] == [rel("new-framework-jobs-to-be-done.md")]
    assert out["decisions"][0]["status"] == "open" and "boom again" in out["decisions"][0]["reason"]
    assert props.parse_frontmatter(show(origin, session_branch, "proposals/new-framework-aaa.md"))[0]["status"] == "open"
    assert len(json.loads(show(origin, session_branch, "catalog.json"))) == 23
    assert subjects(origin, session_branch)[-1] == "review: 2 proposals (1 accepted, 0 rejected, 1 error)"


# --- live ------------------------------------------------------------------------------


@pytest.mark.live
def test_decide_live_on_both_proposal_kinds(tmp_path: Path):
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    from engine.catalog import load_seed_catalog
    from engine.config import make_model
    from engine.workspace import Workspace

    ws = Workspace(tmp_path, "autoresearch/live")
    ws.write("metadata.json", json.dumps({"mission": "Find the vertical-AI market TBPN guests circle without naming", "transcript_path": "t.md", "max_experiments": 3}))
    ws.write("catalog.json", json.dumps(load_seed_catalog()))
    ws.write("rubric.md", RUBRIC)
    ws.write("experiments.tsv", HEADER + "\n")
    ws.write("proposals/new-framework-jobs-to-be-done.md", FRAMEWORK_OPEN)
    ws.write("proposals/rubric-change-time-to-first-dollar.md", RUBRIC_OPEN)
    model = make_model()
    for name, kind in [("new-framework-jobs-to-be-done.md", "new-framework"), ("rubric-change-time-to-first-dollar.md", "rubric-change")]:
        decision = props.decide(model, ws, ws.rel(f"proposals/{name}"))
        assert decision["kind"] == kind and decision["error"] is None and isinstance(decision["accept"], bool)
        assert len(decision["reason"]) > 10
        if decision["accept"]:
            payload = decision["payload"]
            if kind == "new-framework":
                assert all(payload[k].strip() for k in ("name", "category", "summary", "when_to_use"))
            else:
                assert 1 <= len(payload["dimensions"]) <= 3 and all(d["id"] for d in payload["dimensions"])
