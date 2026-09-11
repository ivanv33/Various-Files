"""`engine/tasks/judge.py`: structured-output verdict with randomized, recorded document order."""

from __future__ import annotations

import json
import os

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
        scores=[DocScore(dimension_id=k, a=v, b=None if b is None else b[k]) for k, v in a.items()],
        rationale=rationale,
    )


def _flat(prompt_input) -> str:
    return str(prompt_input)


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
    assert flat.index("Document A") < flat.index(CANDIDATE) < flat.index("Document B") < flat.index(INCUMBENT)


def test_judge_reverses_mapping_when_incumbent_is_first(structured_fake):
    # the model scores A (= incumbent) low and B (= candidate) high
    model = structured_fake([_answer({"specificity": 4, "grounding": 5, "speed": 3}, {"specificity": 8, "grounding": 7, "speed": 9})])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, rng=FixedRng(0.9))
    assert v.order == ["incumbent", "candidate"]
    assert v.candidate == {"specificity": 8, "grounding": 7, "speed": 9}
    assert v.incumbent == {"specificity": 4, "grounding": 5, "speed": 3}
    assert (v.candidate_total, v.incumbent_total) == (24, 12)
    flat = _flat(model.calls[0][1])
    assert flat.index("Document A") < flat.index(INCUMBENT) < flat.index("Document B") < flat.index(CANDIDATE)


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
    flat = _flat(model.calls[0][1])
    assert "Document A" in flat and "Document B" not in flat


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
