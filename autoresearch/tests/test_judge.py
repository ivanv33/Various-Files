"""`engine/tasks/judge.py`: structured-output verdict for the candidate against a frozen-score reference."""

from __future__ import annotations

import json
import os

import pytest

from engine.tasks.judge import CANDIDATE_LABEL, REFERENCE_LABEL, DimScore, JudgeAnswer, JudgeError, Verdict, judge
from engine.tasks.rubric import CORE_DIMENSIONS, Dimension, render_rubric

DIMS = [
    Dimension(id="specificity", name="Specificity", description="Concrete steps."),
    Dimension(id="grounding", name="Grounding", description="Traces to the transcript."),
    Dimension(id="speed", name="Speed", description="Weeks, not years.", kind="extra"),
]
MISSION = "Find the underserved vertical"
CANDIDATE = "CANDIDATE-DOC: 1. Call three restaurant chains this week."
INCUMBENT = "INCUMBENT-DOC: 1. Think about markets."
FROZEN = {"specificity": 4, "grounding": 5, "speed": 3}  # 12


def _answer(
    scores: dict[str, int],
    deficiencies: list[str] | None = None,
    rationale: str = "Sharper than the reference.",
    gains: list[str] | None = None,
) -> JudgeAnswer:
    """A well-formed answer: one deficiency entry per dimension, `none:` entries wherever the score is 10, and (unless
    given) a gains entry per dimension so any score above the frozen reference is justified."""
    if deficiencies is None:
        deficiencies = [f"{k}: none — every step meets it" if v == 10 else f"{k}: step 1 is thin" for k, v in scores.items()]
    if gains is None:
        gains = [f"{k}: quotes 'Call three restaurant chains this week' where the reference only says 'think about markets'" for k in scores]
    return JudgeAnswer(
        deficiencies=deficiencies,
        gains=gains,
        scores=[DimScore(dimension_id=k, score=v) for k, v in scores.items()],
        rationale=rationale,
    )


def _flat(prompt_input) -> str:
    return str(prompt_input)


def _body(prompt_input) -> str:
    """The human turn: mission, the candidate, the reference block, closing line."""
    return str(prompt_input[1].content)


def test_judge_grades_the_candidate_and_copies_the_frozen_reference_scores(structured_fake):
    model = structured_fake([_answer({"specificity": 8, "grounding": 7, "speed": 9})])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN, experiment=3, judge_model="fake")
    assert isinstance(v, Verdict)
    assert v.candidate == {"specificity": 8, "grounding": 7, "speed": 9}
    assert v.incumbent == FROZEN
    assert (v.candidate_total, v.incumbent_total) == (24, 12)
    assert v.kept is True
    assert v.rationale == "Sharper than the reference."
    assert (v.experiment, v.judge_model) == (3, "fake")
    schema, prompt_input = model.calls[0]
    assert schema is JudgeAnswer
    flat = _flat(prompt_input)
    assert MISSION in flat and "Specificity" in flat and "Weeks, not years." in flat
    body = _body(prompt_input)
    assert body.index(CANDIDATE_LABEL) < body.index(CANDIDATE) < body.index(REFERENCE_LABEL) < body.index(INCUMBENT)
    assert "- `specificity`: 4" in body and "- total: 12" in body  # frozen scores shown, not asked for
    assert "has_reference=True" in str(prompt_input[0].content)


def test_judge_frozen_scores_are_never_regraded(structured_fake):
    """The model returns only candidate scores; whatever it says, the incumbent total is the stored one."""
    model = structured_fake([_answer({"specificity": 4, "grounding": 5, "speed": 3})])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, {"specificity": 9, "grounding": 9, "speed": 9})
    assert v.incumbent_total == 27 and v.candidate_total == 12
    assert v.kept is False


def test_judge_equal_totals_is_not_kept(structured_fake):
    model = structured_fake([_answer({"specificity": 5, "grounding": 5, "speed": 5})])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, {"specificity": 5, "grounding": 5, "speed": 5})
    assert v.candidate_total == v.incumbent_total == 15
    assert v.kept is False


def test_judge_without_incumbent_grades_alone(structured_fake):
    model = structured_fake([_answer({"specificity": 6, "grounding": 7, "speed": 8})])
    v = judge(model, DIMS, MISSION, CANDIDATE, None, None, experiment=1)
    assert v.candidate == {"specificity": 6, "grounding": 7, "speed": 8}
    assert v.incumbent is None and v.incumbent_total is None
    assert v.candidate_total == 21
    assert v.kept is True
    body = _body(model.calls[0][1])
    assert CANDIDATE_LABEL in body and REFERENCE_LABEL not in body
    assert "has_reference=False" in str(model.calls[0][1][0].content)


def test_judge_requires_incumbent_text_and_scores_together(structured_fake):
    model = structured_fake([_answer({"specificity": 6, "grounding": 7, "speed": 8})])
    with pytest.raises(JudgeError, match="together"):
        judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, None)
    with pytest.raises(JudgeError, match="together"):
        judge(model, DIMS, MISSION, CANDIDATE, None, FROZEN)


def test_judge_rejects_frozen_scores_that_lack_a_rubric_dimension(structured_fake):
    model = structured_fake([_answer({"specificity": 6, "grounding": 7, "speed": 8})])
    with pytest.raises(JudgeError, match="speed"):
        judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, {"specificity": 4, "grounding": 5})


def test_judge_accepts_rubric_markdown(structured_fake):
    text = render_rubric(CORE_DIMENSIONS, DIMS[2:])
    ids = [d.id for d in CORE_DIMENSIONS] + ["speed"]
    model = structured_fake([_answer({i: 5 for i in ids})])
    v = judge(model, text, MISSION, CANDIDATE, INCUMBENT, {i: 4 for i in ids})
    assert list(v.candidate) == ids
    assert v.candidate_total == 5 * len(ids)


@pytest.mark.parametrize(
    "bad, reason",
    [
        (_answer({"specificity": 8, "grounding": 7}), "speed"),  # missing dimension
        (_answer({"specificity": 11, "grounding": 7, "speed": 9}), "11"),  # out of range
        (_answer({"specificity": 8, "grounding": 7, "speed": 9, "bogus": 5}), "bogus"),
        (_answer({"specificity": 8, "grounding": 7, "speed": 9}, deficiencies=["specificity: thin"]), "grounding"),  # no entry per dimension
        (_answer({"specificity": 10, "grounding": 7, "speed": 9}, deficiencies=["specificity: step 2 is vague", "grounding: x", "speed: y"]), "none"),  # 10 next to a deficiency
        (ValueError("provider exploded"), "provider exploded"),
    ],
)
def test_judge_repairs_once_and_explains_the_problem(structured_fake, bad, reason):
    good = _answer({"specificity": 8, "grounding": 7, "speed": 9})
    model = structured_fake([bad, good])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN)
    assert v.candidate_total == 24
    assert len(model.calls) == 2
    assert reason in _flat(model.calls[1][1])


def test_judge_accepts_a_ten_backed_by_a_none_entry(structured_fake):
    model = structured_fake([_answer({"specificity": 10, "grounding": 7, "speed": 9}, deficiencies=["specificity: none — steps 1-3 name owner and date", "grounding: step 2 cites nothing", "speed: step 3 says 'soon'"])])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN)
    assert v.candidate["specificity"] == 10 and len(model.calls) == 1
    assert v.deficiencies[0].startswith("specificity: none")


def test_judge_requires_a_gains_entry_for_every_dimension_scored_above_the_reference(structured_fake):
    """Equal by default: a score above the frozen reference must quote what the candidate adds (v3 saturated at 80/80
    because raises came free)."""
    unjustified = _answer({"specificity": 8, "grounding": 5, "speed": 3}, gains=[])
    justified = _answer({"specificity": 8, "grounding": 5, "speed": 3}, gains=["specificity: quotes 'three restaurant chains this week' vs the reference's 'think about markets'"])
    model = structured_fake([unjustified, justified])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN)
    assert v.candidate_total == 16 and len(model.calls) == 2
    repair = _flat(model.calls[1][1])
    assert "gains" in repair and "specificity" in repair and "grounding" not in repair.split("gains", 1)[1][:200]
    assert v.gains == justified.gains


def test_judge_scores_at_or_below_the_reference_need_no_gains_entry(structured_fake):
    model = structured_fake([_answer({"specificity": 4, "grounding": 3, "speed": 3}, gains=[])])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN)
    assert v.candidate_total == 10 and len(model.calls) == 1 and v.gains == []


def test_judge_without_a_reference_ignores_gains(structured_fake):
    model = structured_fake([_answer({"specificity": 8, "grounding": 7, "speed": 9}, gains=[])])
    v = judge(model, DIMS, MISSION, CANDIDATE)
    assert v.candidate_total == 24 and len(model.calls) == 1


def test_judge_rejects_more_than_max_tens(structured_fake):
    from engine.tasks.judge import MAX_TENS

    assert MAX_TENS == 2
    three_tens = _answer({"specificity": 10, "grounding": 10, "speed": 10})
    two_tens = _answer({"specificity": 10, "grounding": 10, "speed": 9})
    model = structured_fake([three_tens, two_tens])
    v = judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN)
    assert v.candidate_total == 29 and len(model.calls) == 2
    assert "at most 2" in _flat(model.calls[1][1])


def test_judge_prompt_states_the_tens_cap_and_equal_by_default(structured_fake):
    model = structured_fake([_answer({"specificity": 4, "grounding": 5, "speed": 3}, gains=[])])
    judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN)
    system = str(model.calls[0][1][0].content)
    assert "at most 2" in system and "gains" in system


def test_judge_gives_up_after_one_repair(structured_fake):
    bad = _answer({"specificity": 8})
    model = structured_fake([bad, bad])
    with pytest.raises(JudgeError, match="repair"):
        judge(model, DIMS, MISSION, CANDIDATE, INCUMBENT, FROZEN)
    assert len(model.calls) == 2


def test_verdict_dumps_to_score_json_shape():
    v = Verdict(
        experiment=2,
        judge_model="gemini-x",
        candidate={"specificity": 8},
        incumbent={"specificity": 4},
        candidate_total=8,
        incumbent_total=4,
        deficiencies=["specificity: step 1 is thin"],
        rationale="r",
    )
    data = json.loads(json.dumps(v.model_dump(mode="json")))
    assert set(data) == {"experiment", "judge_model", "candidate", "incumbent", "candidate_total", "incumbent_total", "deficiencies", "gains", "rationale"}


def test_verdict_reads_score_json_written_before_deficiencies_existed():
    data = {"experiment": 1, "judge_model": "g", "candidate": {"specificity": 8}, "incumbent": None, "candidate_total": 8, "incumbent_total": None, "rationale": "r"}
    v = Verdict.model_validate(data)
    assert v.deficiencies == [] and v.gains == [] and v.kept is True


def test_judge_answer_schema_asks_for_deficiencies_and_gains_before_scores():
    """The field order is the mechanism (structured output is generated in schema order), so it is the contract;
    the prompt's wording is not pinned."""
    assert list(JudgeAnswer.model_fields)[:3] == ["deficiencies", "gains", "scores"]


def test_loop_judge_step_passes_the_frozen_best_scores(structured_fake, tmp_path, monkeypatch):
    """The live path reads `best/score.json` and hands its candidate scores to the judge as the frozen anchor."""
    from engine import loop
    from engine.workspace import Workspace

    branch = "autoresearch/demo"
    ws = Workspace(tmp_path, branch)
    ws.write("metadata.json", json.dumps({"mission": MISSION, "transcript_path": "t.md", "max_experiments": 3}))
    ws.write("rubric.md", render_rubric(CORE_DIMENSIONS, DIMS[2:]))
    ids = [d.id for d in CORE_DIMENSIONS] + ["speed"]
    ws.write("best/recommendations.md", INCUMBENT)
    ws.write("best/score.json", json.dumps({"experiment": 1, "candidate": {i: 6 for i in ids}, "candidate_total": 6 * len(ids), "rationale": "r"}))
    model = structured_fake([_answer({i: 7 for i in ids})])
    monkeypatch.setattr(loop, "make_model", lambda *a, **k: model)
    out = loop.judge_step.func(str(tmp_path), branch, 2, {"path": "attempts/2/recommendations.md", "content": CANDIDATE}, "fake")
    assert out["error"] is None
    assert out["verdict"]["incumbent"] == {i: 6 for i in ids}
    assert out["verdict"]["incumbent_total"] == 6 * len(ids)
    assert out["verdict"]["candidate_total"] == 7 * len(ids)
    assert "- total: " + str(6 * len(ids)) in _body(model.calls[0][1])


def test_loop_judge_step_without_a_best_grades_alone(structured_fake, tmp_path, monkeypatch):
    from engine import loop
    from engine.workspace import Workspace

    branch = "autoresearch/demo"
    ws = Workspace(tmp_path, branch)
    ws.write("metadata.json", json.dumps({"mission": MISSION, "transcript_path": "t.md", "max_experiments": 3}))
    ws.write("rubric.md", render_rubric(CORE_DIMENSIONS, DIMS[2:]))
    ids = [d.id for d in CORE_DIMENSIONS] + ["speed"]
    model = structured_fake([_answer({i: 7 for i in ids})])
    monkeypatch.setattr(loop, "make_model", lambda *a, **k: model)
    out = loop.judge_step.func(str(tmp_path), branch, 1, {"path": "attempts/1/recommendations.md", "content": CANDIDATE}, "fake")
    assert out["error"] is None and out["verdict"]["incumbent"] is None
    assert REFERENCE_LABEL not in _body(model.calls[0][1])


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
    model = make_model()
    weak_v = judge(model, CORE_DIMENSIONS, MISSION, weak, None, None, experiment=1)
    good_v = judge(model, CORE_DIMENSIONS, MISSION, good, weak, weak_v.candidate, experiment=2)
    assert set(good_v.candidate) == {d.id for d in CORE_DIMENSIONS}
    assert all(1 <= s <= 10 for s in good_v.candidate.values())
    assert good_v.incumbent_total == weak_v.candidate_total
    assert good_v.candidate_total > good_v.incumbent_total
    assert good_v.rationale.strip()


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
def test_judge_live_scores_the_same_document_alike_against_its_own_frozen_scores():
    """Comparability control: a document graded alone, then graded again as candidate with itself as the frozen
    reference, must land within a point of its frozen total (so a copy of the best never beats the best)."""
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    from engine.config import make_model

    model = make_model()
    alone = judge(model, CORE_DIMENSIONS, MISSION, SAME_DOC, None, None)
    again = judge(model, CORE_DIMENSIONS, MISSION, SAME_DOC, SAME_DOC, alone.candidate)
    print(f"\nalone={alone.candidate_total} again={again.candidate_total} per-dim alone={alone.candidate} again={again.candidate}")
    assert abs(again.candidate_total - alone.candidate_total) <= 1, (alone.candidate, again.candidate)
    assert again.kept is False
