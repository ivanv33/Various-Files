"""`engine/tasks/judge.py`: structured-output verdict with randomized, recorded document order."""

from __future__ import annotations

import json
import os
import random

import pytest

from engine.tasks.judge import DocScore, JudgeAnswer, JudgeError, Verdict, judge
from engine.tasks.rubric import CORE_DIMENSIONS, Dimension, render_rubric

DIMS = [
    Dimension(id="specificity", name="Specificity", description="Concrete steps."),
    Dimension(id="grounding", name="Grounding", description="Traces to the transcript."),
    Dimension(id="speed", name="Speed", description="Weeks, not years.", kind="extra"),
]
MISSION = "Find the underserved vertical"
CANDIDATE = "CANDIDATE-DOC: 1. Call three restaurant chains this week."
INCUMBENT = "INCUMBENT-DOC: 1. Think about markets."


class FixedRng:
    def __init__(self, value: float):
        self.value = value

    def random(self) -> float:
        return self.value


def _answer(a: dict[str, int], b: dict[str, int] | None = None, rationale: str = "A is sharper.") -> JudgeAnswer:
    return JudgeAnswer(
        deficiencies_a=[],
        deficiencies_b=None if b is None else [],
        scores=[DocScore(dimension_id=k, a=v, b=None if b is None else b[k]) for k, v in a.items()],
        rationale=rationale,
    )


def _flat(prompt_input) -> str:
    return str(prompt_input)


def _body(prompt_input) -> str:
    """The human turn: mission, the labelled documents, closing line (the system prompt also names the labels)."""
    return str(prompt_input[1].content)


def test_judge_maps_document_a_b_back_to_candidate_incumbent_when_candidate_is_first(structured_fake):
    model = structured_fake([_answer({"specificity": 8, "grounding": 7, "speed": 9}, {"specificity": 4, "grounding": 5, "speed": 3})])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, experiment=3, judge_model="fake", rng=FixedRng(0.1))
    assert isinstance(v, Verdict)
    assert v.order == ["candidate", "incumbent"]
    assert v.candidate == {"specificity": 8, "grounding": 7, "speed": 9}
    assert v.incumbent == {"specificity": 4, "grounding": 5, "speed": 3}
    assert (v.candidate_total, v.incumbent_total) == (24, 12)
    assert v.kept is True
    assert v.rationale == "A is sharper."
    assert (v.experiment, v.judge_model) == (3, "fake")
    schema, prompt_input = model.calls[0]
    assert schema is JudgeAnswer
    flat = _flat(prompt_input)
    assert MISSION in flat and "Specificity" in flat and "Weeks, not years." in flat
    body = _body(prompt_input)
    assert body.index("Document A") < body.index(CANDIDATE) < body.index("Document B") < body.index(INCUMBENT)


def test_judge_reverses_mapping_when_incumbent_is_first(structured_fake):
    # the model scores A (= incumbent) low and B (= candidate) high
    model = structured_fake([_answer({"specificity": 4, "grounding": 5, "speed": 3}, {"specificity": 8, "grounding": 7, "speed": 9})])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, rng=FixedRng(0.9))
    assert v.order == ["incumbent", "candidate"]
    assert v.candidate == {"specificity": 8, "grounding": 7, "speed": 9}
    assert v.incumbent == {"specificity": 4, "grounding": 5, "speed": 3}
    assert (v.candidate_total, v.incumbent_total) == (24, 12)
    body = _body(model.calls[0][1])
    assert body.index("Document A") < body.index(INCUMBENT) < body.index("Document B") < body.index(CANDIDATE)


def test_judge_without_rng_randomizes_order_across_calls(structured_fake):
    orders = set()
    for _ in range(40):
        model = structured_fake([_answer({"specificity": 5, "grounding": 5, "speed": 5}, {"specificity": 5, "grounding": 5, "speed": 5})])
        orders.add(tuple(judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT).order))
    assert orders == {("candidate", "incumbent"), ("incumbent", "candidate")}


def test_judge_equal_totals_is_not_kept(structured_fake):
    model = structured_fake([_answer({"specificity": 5, "grounding": 5, "speed": 5}, {"specificity": 5, "grounding": 5, "speed": 5})])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, rng=FixedRng(0.1))
    assert v.candidate_total == v.incumbent_total == 15
    assert v.kept is False


def test_judge_without_incumbent_scores_only_document_a(structured_fake):
    model = structured_fake([_answer({"specificity": 6, "grounding": 7, "speed": 8})])
    v = judge(model, DIMS, MISSION, CANDIDATE, None, experiment=1, rng=FixedRng(0.9))
    assert v.order == ["candidate"]
    assert v.candidate == {"specificity": 6, "grounding": 7, "speed": 8}
    assert v.incumbent is None and v.incumbent_total is None
    assert v.candidate_total == 21
    assert v.kept is True
    body = _body(model.calls[0][1])
    assert "Document A" in body and "Document B" not in body


def test_judge_accepts_rubric_markdown(structured_fake):
    text = render_rubric(CORE_DIMENSIONS, DIMS[2:])
    ids = [d.id for d in CORE_DIMENSIONS] + ["speed"]
    model = structured_fake([_answer({i: 5 for i in ids}, {i: 4 for i in ids})])
    v = judge(model, text, MISSION, CANDIDATE, INCUMBENT, rng=FixedRng(0.1))
    assert list(v.candidate) == ids
    assert v.candidate_total == 5 * len(ids)


@pytest.mark.parametrize(
    "bad, reason",
    [
        (_answer({"specificity": 8, "grounding": 7}, {"specificity": 4, "grounding": 5}), "speed"),  # missing dimension
        (_answer({"specificity": 11, "grounding": 7, "speed": 9}, {"specificity": 4, "grounding": 5, "speed": 3}), "11"),  # out of range
        (_answer({"specificity": 8, "grounding": 7, "speed": 9}), "Document B"),  # incumbent present but b omitted
        (_answer({"specificity": 8, "grounding": 7, "speed": 9, "bogus": 5}, {"specificity": 4, "grounding": 5, "speed": 3, "bogus": 5}), "bogus"),
        (ValueError("provider exploded"), "provider exploded"),
    ],
)
def test_judge_repairs_once_and_explains_the_problem(structured_fake, bad, reason):
    good = _answer({"specificity": 8, "grounding": 7, "speed": 9}, {"specificity": 4, "grounding": 5, "speed": 3})
    model = structured_fake([bad, good])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, rng=FixedRng(0.1))
    assert v.candidate_total == 24
    assert len(model.calls) == 2
    assert reason in _flat(model.calls[1][1])


def test_judge_gives_up_after_one_repair(structured_fake):
    bad = _answer({"specificity": 8}, {"specificity": 4})
    model = structured_fake([bad, bad])
    with pytest.raises(JudgeError, match="repair"):
        judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, rng=FixedRng(0.1))
    assert len(model.calls) == 2


def test_verdict_dumps_to_score_json_shape():
    v = Verdict(
        experiment=2,
        judge_model="gemini-x",
        order=["incumbent", "candidate"],
        candidate={"specificity": 8},
        incumbent={"specificity": 4},
        candidate_total=8,
        incumbent_total=4,
        rationale="r",
    )
    data = json.loads(json.dumps(v.model_dump(mode="json")))
    assert set(data) == {"experiment", "judge_model", "order", "candidate", "incumbent", "candidate_total", "incumbent_total", "rationale"}
    assert data["order"] == ["incumbent", "candidate"]


@pytest.mark.live
def test_judge_live_prefers_the_obviously_better_document():
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    from engine.config import make_model

    good = (
        "1. This week, call the three regional restaurant-supply distributors the guest named (Sysco's regional "
        "rival, the two family firms) and ask for their current software spend per branch; the transcript's "
        "'nobody sells to on-premise' claim is the gap to verify.\n"
        "2. Draft a one-page pricing sheet priced per delivery route, not per seat, as the guest's '$5 trillion "
        "services' remark implies; owner: founder; due Friday.\n"
        "3. Kill the sales-enablement idea: the transcript calls that branch crowded with no winner."
    )
    weak = "Think about markets. Consider AI. Talk to people. Build something good."
    v = judge(make_model(), CORE_DIMENSIONS, MISSION, good, weak, experiment=1, judge_model=os.environ.get("GEMINI_MODEL", ""))
    assert set(v.candidate) == {d.id for d in CORE_DIMENSIONS}
    assert all(1 <= s <= 10 for s in v.candidate.values())
    assert v.incumbent is not None and all(1 <= s <= 10 for s in v.incumbent.values())
    assert v.candidate_total > v.incumbent_total
    assert v.rationale.strip()


SAME_DOC = """# Recommendations

1. This week, call the three regional restaurant-supply distributors the guest named (the Sysco regional rival and
   the two family firms) and ask each for its software spend per branch; the transcript's claim that "nobody sells
   to on-premise" is the gap to verify. Owner: founder. Due Friday.
2. Draft a one-page pricing sheet priced per delivery route rather than per seat, following the guest's "$5 trillion
   of services" remark; owner: founder; due Friday.
3. Kill the sales-enablement idea: the hosts call that branch "crowded with no winner" at minute 14.
4. Run a two-week pilot with one distributor branch: instrument route planning only, measure hours saved per
   dispatcher, and stop if the saving is under two hours a week.
5. Hire nobody until the pilot reports; the guest's line that early teams "die of payroll before they die of
   product" sets the constraint.
6. Write the pilot's definition of done before the first call and share it with the branch manager, so the exit
   criterion is agreed rather than argued.
"""


@pytest.mark.live
def test_judge_live_scores_the_same_document_alike_in_both_positions():
    """Symmetry control for spec 4.2: one document shown as both candidate and incumbent, once per order."""
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    from engine.config import make_model

    model = make_model()
    verdicts = [judge(model, CORE_DIMENSIONS, MISSION, SAME_DOC, SAME_DOC, rng=FixedRng(value)) for value in (0.1, 0.9)]
    orders = {tuple(v.order) for v in verdicts}
    for v in verdicts:
        print(f"\norder={v.order} candidate={v.candidate_total} incumbent={v.incumbent_total} per-dim c={v.candidate} i={v.incumbent}")
    assert orders == {("candidate", "incumbent"), ("incumbent", "candidate")}
    for v in verdicts:
        assert abs(v.candidate_total - v.incumbent_total) <= 1, (v.order, v.candidate, v.incumbent)


VAGUE_DOC = """# Recommendations

1. Talk to some restaurant-supply distributors about their software needs.
2. Think about pricing per route instead of per seat.
3. Avoid the crowded sales-enablement space.
"""


@pytest.mark.live
def test_judge_live_ranks_two_documents_the_same_in_both_orders():
    """Position-bias probe: the same pair in both orders must give the same winner and stable per-document totals."""
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    from engine.config import make_model

    model = make_model()
    verdicts = [judge(model, CORE_DIMENSIONS, MISSION, SAME_DOC, VAGUE_DOC, rng=FixedRng(value)) for value in (0.1, 0.9)]
    for v in verdicts:
        print(f"\norder={v.order} strong={v.candidate_total} vague={v.incumbent_total} per-dim strong={v.candidate} vague={v.incumbent}")
    assert {tuple(v.order) for v in verdicts} == {("candidate", "incumbent"), ("incumbent", "candidate")}
    for v in verdicts:
        assert v.candidate_total > v.incumbent_total
    assert abs(verdicts[0].candidate_total - verdicts[1].candidate_total) <= 3
    assert abs(verdicts[0].incumbent_total - verdicts[1].incumbent_total) <= 3


def test_judge_answer_schema_asks_for_deficiencies_before_scores():
    """The field order is the mechanism (structured output is generated in schema order), so it is the contract;
    the prompt's wording is not pinned."""
    assert list(JudgeAnswer.model_fields)[:3] == ["deficiencies_a", "deficiencies_b", "scores"]


def test_judge_repairs_a_missing_second_deficiency_list(structured_fake):
    bad = _answer({"specificity": 8, "grounding": 7, "speed": 9}, {"specificity": 4, "grounding": 5, "speed": 3})
    bad.deficiencies_b = None
    good = _answer({"specificity": 8, "grounding": 7, "speed": 9}, {"specificity": 4, "grounding": 5, "speed": 3})
    model = structured_fake([bad, good])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, rng=FixedRng(0.1))
    assert v.candidate_total == 24 and len(model.calls) == 2
    assert "deficiency list" in _flat(model.calls[1][1])


def test_loop_judge_step_defers_order_to_the_unseeded_module_rng(structured_fake, tmp_path, monkeypatch):
    """The live path (`loop.judge_step`) passes no rng: it consults `judge.random` once per call, and with the real
    module (nothing in the engine or its imports seeds it) both orders occur."""
    from engine import loop
    from engine.tasks import judge as judge_mod
    from engine.workspace import Workspace

    branch = "autoresearch/demo"
    ws = Workspace(tmp_path, branch)
    ws.write("metadata.json", json.dumps({"mission": MISSION, "transcript_path": "t.md", "max_experiments": 3}))
    ws.write("rubric.md", render_rubric(CORE_DIMENSIONS, DIMS[2:]))
    ws.write("best/recommendations.md", INCUMBENT)
    ids = [d.id for d in CORE_DIMENSIONS] + ["speed"]
    fresh = lambda *a, **k: structured_fake([_answer({i: 5 for i in ids}, {i: 6 for i in ids})])  # noqa: E731
    monkeypatch.setattr(loop, "make_model", fresh)

    class Recorder:
        calls = 0

        def random(self) -> float:
            Recorder.calls += 1
            return 0.9

    monkeypatch.setattr(judge_mod, "random", Recorder())
    out = loop.judge_step.func(str(tmp_path), branch, 2, {"path": "attempts/2/recommendations.md", "content": CANDIDATE}, "fake")
    assert out["error"] is None and Recorder.calls == 1
    assert out["verdict"]["order"] == ["incumbent", "candidate"]
    assert out["verdict"]["candidate_total"] == 6 * len(ids)  # Document B was the candidate

    monkeypatch.setattr(judge_mod, "random", random)
    orders = set()
    for _ in range(40):
        out = loop.judge_step.func(str(tmp_path), branch, 2, {"path": "attempts/2/recommendations.md", "content": CANDIDATE}, "fake")
        orders.add(tuple(out["verdict"]["order"]))
    assert orders == {("candidate", "incumbent"), ("incumbent", "candidate")}
