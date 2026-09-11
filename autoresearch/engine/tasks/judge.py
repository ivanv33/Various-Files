"""Judge: one structured-output call scoring the candidate on the rubric against a frozen anchor.

Only the candidate is graded. The incumbent (`best/recommendations.md`) is shown as a reference together
with the per-dimension scores it received when it was kept (`best/score.json`); those scores are frozen and
are never re-graded, so every total in `experiments.tsv` is on one scale and the log reads as a leaderboard.
The reference calibrates the judge: a candidate weaker than the reference on a dimension must score lower
there, one equally good the same, one stronger higher. Malformed output gets one repair turn carrying the
validation error; then `JudgeError` (the loop logs `kept=error`).
"""

from __future__ import annotations

from typing import Any, Sequence

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from engine.prompts import load_prompt
from engine.tasks.rubric import SCORE_MAX, SCORE_MIN, Dimension, parse_rubric

CANDIDATE_LABEL = "Candidate"
REFERENCE_LABEL = "Reference (current best, frozen scores)"


class JudgeError(RuntimeError):
    """No valid verdict after one repair; the attempt is logged as `kept=error`."""


# --- what the model returns -----------------------------------------------------


class DimScore(BaseModel):
    dimension_id: str = Field(description="the exact dimension id from the rubric")
    score: int = Field(description=f"the candidate's score on this dimension, integer {SCORE_MIN}-{SCORE_MAX}")


class JudgeAnswer(BaseModel):
    """Field order is the grading order: deficiencies with evidence first, then scores, then the rationale."""

    deficiencies: list[str] = Field(
        description="the candidate's concrete deficiencies, at least one entry per rubric dimension: each starts with the dimension id and either quotes the passage that shows the deficiency, names exactly what is missing, or states 'none:' followed by the evidence that nothing is missing on that dimension"
    )
    scores: list[DimScore] = Field(description="exactly one entry per rubric dimension, derived from the deficiency list")
    rationale: str = Field(
        description="one paragraph: where the candidate is weaker, equal and stronger than the reference (if any), citing entries from the deficiency list"
    )


# --- what the loop records (best/score.json) -----------------------------------


class Verdict(BaseModel):
    experiment: int | None = None
    judge_model: str = ""
    candidate: dict[str, int]
    incumbent: dict[str, int] | None = None  # the frozen scores the reference carried, copied for the record
    candidate_total: int
    incumbent_total: int | None = None
    deficiencies: list[str] = []
    rationale: str

    @property
    def kept(self) -> bool:
        """Strictly better than the frozen incumbent total; experiment 1 (no incumbent) is always kept."""
        return self.incumbent_total is None or self.candidate_total > self.incumbent_total


# --- validation -----------------------------------------------------------------


def _check_range(value: int, dimension_id: str) -> None:
    if not SCORE_MIN <= value <= SCORE_MAX:
        raise JudgeError(
            f"score for {dimension_id!r} is {value}; scores must be integers from {SCORE_MIN} to {SCORE_MAX}"
        )


def _validate_answer(answer: JudgeAnswer | dict[str, Any], dims: Sequence[Dimension]) -> tuple[dict[str, int], list[str], str]:
    """Return `(scores, deficiencies, rationale)` in rubric order, or raise `JudgeError` with the reason."""
    if isinstance(answer, dict):
        try:
            answer = JudgeAnswer.model_validate(answer)
        except ValidationError as exc:
            raise JudgeError(f"answer does not match the JudgeAnswer schema: {exc}") from exc
    expected = [d.id for d in dims]
    seen: dict[str, DimScore] = {}
    for score in answer.scores:
        if score.dimension_id not in expected:
            raise JudgeError(f"unknown dimension id {score.dimension_id!r}; use exactly these ids: {expected}")
        if score.dimension_id in seen:
            raise JudgeError(f"dimension {score.dimension_id!r} is scored twice")
        seen[score.dimension_id] = score
    missing = [i for i in expected if i not in seen]
    if missing:
        raise JudgeError(f"missing scores for dimensions: {missing}")
    deficiencies = [" ".join(d.split()) for d in answer.deficiencies if d.strip()]
    uncovered = [i for i in expected if not any(d.startswith(i) for d in deficiencies)]
    if uncovered:
        raise JudgeError(
            f"no deficiency entry for dimensions: {uncovered}; every dimension needs at least one entry starting with its id "
            "(quote the deficiency, or write 'none:' with the evidence)"
        )
    scores: dict[str, int] = {}
    for dimension_id in expected:
        value = seen[dimension_id].score
        _check_range(value, dimension_id)
        if value == SCORE_MAX and not any(
            d.startswith(dimension_id) and d[len(dimension_id):].lstrip(" :-").lower().startswith("none") for d in deficiencies
        ):
            raise JudgeError(
                f"{dimension_id!r} scored {SCORE_MAX} but its deficiency entry is not 'none: ...'; "
                f"a {SCORE_MAX} requires an empty deficiency list on that dimension"
            )
        scores[dimension_id] = value
    return scores, deficiencies, " ".join(answer.rationale.split())


# --- the call -------------------------------------------------------------------


def _rubric_listing(dims: Sequence[Dimension]) -> str:
    return "\n".join(f"- `{d.id}` — {d.name}: {d.description}" for d in dims)


def _reference_block(text: str, scores: dict[str, int], dims: Sequence[Dimension]) -> str:
    lines = [f"- `{d.id}`: {scores[d.id]}" for d in dims if d.id in scores]
    total = sum(scores[d.id] for d in dims if d.id in scores)
    return (
        f"## {REFERENCE_LABEL}\n\nFrozen scores (do not re-grade; calibrate against them):\n"
        + "\n".join(lines)
        + f"\n- total: {total}\n\n{text.strip()}"
    )


def judge(
    model: Any,
    rubric: str | Sequence[Dimension],
    mission: str,
    candidate: str,
    incumbent: str | None = None,
    incumbent_scores: dict[str, int] | None = None,
    *,
    experiment: int | None = None,
    judge_model: str = "",
) -> Verdict:
    """Score `candidate` on the rubric; `incumbent` and its frozen `incumbent_scores` (both or neither) are shown
    as a calibration reference and are not graded.

    `rubric` is `rubric.md` text or parsed dimensions.
    """
    dims = parse_rubric(rubric) if isinstance(rubric, str) else list(rubric)
    if not dims:
        raise JudgeError("rubric has no dimensions")
    if (incumbent is None) != (incumbent_scores is None):
        raise JudgeError("incumbent text and incumbent_scores must be given together")
    frozen: dict[str, int] | None = None
    if incumbent_scores is not None:
        missing = [d.id for d in dims if d.id not in incumbent_scores]
        if missing:
            raise JudgeError(f"frozen incumbent scores lack dimensions {missing}; the rubric changed since the best was kept")
        frozen = {d.id: int(incumbent_scores[d.id]) for d in dims}

    system = load_prompt("judge").format(
        rubric=_rubric_listing(dims), score_min=SCORE_MIN, score_max=SCORE_MAX, has_reference=incumbent is not None
    )
    parts = [f"Mission: {mission.strip()}", f"## {CANDIDATE_LABEL}\n\n{candidate.strip()}"]
    if incumbent is not None and frozen is not None:
        parts.append(_reference_block(incumbent, frozen, dims))
        closing = "Grade the Candidate only. The Reference is already graded; use its frozen scores to place the Candidate on the same scale."
    else:
        closing = "No reference exists yet: grade the Candidate against the scale anchors alone."
    parts.append(closing)
    messages: list[Any] = [SystemMessage(content=system), HumanMessage(content="\n\n".join(parts))]

    structured = model.with_structured_output(JudgeAnswer)
    error: str | None = None
    for _attempt in range(2):
        turn = messages if error is None else messages + [
            HumanMessage(content=f"Your previous answer was rejected: {error}\nReturn a corrected answer.")
        ]
        try:
            scores, deficiencies, rationale = _validate_answer(structured.invoke(turn), dims)
        except Exception as exc:  # provider errors, schema errors, our own JudgeError
            error = " ".join(str(exc).split())
            continue
        return Verdict(
            experiment=experiment,
            judge_model=judge_model,
            candidate=scores,
            incumbent=frozen,
            candidate_total=sum(scores.values()),
            incumbent_total=None if frozen is None else sum(frozen.values()),
            deficiencies=deficiencies,
            rationale=rationale,
        )
    raise JudgeError(f"could not get a valid verdict after one repair: {error}")
