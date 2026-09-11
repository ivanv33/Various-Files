"""Judge: one structured-output call scoring the candidate and the incumbent on the rubric.

The documents are shown as "Document A" / "Document B" in random order so position bias cannot
systematically favour the candidate; `Verdict.order` records which was which (refinement 7). The
incumbent is re-graded every experiment to control score drift. Malformed output gets one repair
turn carrying the validation error; then `JudgeError` (the loop logs `kept=error`).
"""

from __future__ import annotations

import random
from typing import Any, Sequence

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from engine.prompts import load_prompt
from engine.tasks.rubric import SCORE_MAX, SCORE_MIN, Dimension, parse_rubric

LABELS = ("Document A", "Document B")


class JudgeError(RuntimeError):
    """No valid verdict after one repair; the attempt is logged as `kept=error`."""


# --- what the model returns -----------------------------------------------------


class DocScore(BaseModel):
    dimension_id: str = Field(description="the exact dimension id from the rubric")
    a: int = Field(description=f"score for the first document, integer {SCORE_MIN}-{SCORE_MAX}")
    b: int | None = Field(
        default=None,
        description=f"score for the second document, integer {SCORE_MIN}-{SCORE_MAX}; null when only one document is provided",
    )


class JudgeAnswer(BaseModel):
    scores: list[DocScore] = Field(description="exactly one entry per rubric dimension")
    rationale: str = Field(description="one paragraph naming the dimensions on which the documents differ and why")


# --- what the loop records (best/score.json) -----------------------------------


class Verdict(BaseModel):
    experiment: int | None = None
    judge_model: str = ""
    order: list[str]  # ["candidate", "incumbent"], ["incumbent", "candidate"], or ["candidate"]
    candidate: dict[str, int]
    incumbent: dict[str, int] | None = None
    candidate_total: int
    incumbent_total: int | None = None
    rationale: str

    @property
    def kept(self) -> bool:
        """Strictly better than the incumbent; experiment 1 (no incumbent) is always kept."""
        return self.incumbent_total is None or self.candidate_total > self.incumbent_total


# --- validation -----------------------------------------------------------------


def _check_range(value: int, dimension_id: str, label: str) -> None:
    if not SCORE_MIN <= value <= SCORE_MAX:
        raise JudgeError(
            f"{label} score for {dimension_id!r} is {value}; scores must be integers from {SCORE_MIN} to {SCORE_MAX}"
        )


def _validate_answer(
    answer: JudgeAnswer | dict[str, Any], dims: Sequence[Dimension], has_b: bool
) -> tuple[dict[str, int], dict[str, int] | None, str]:
    """Return `(a_scores, b_scores | None, rationale)` in rubric order, or raise `JudgeError` with the reason."""
    if isinstance(answer, dict):
        try:
            answer = JudgeAnswer.model_validate(answer)
        except ValidationError as exc:
            raise JudgeError(f"answer does not match the JudgeAnswer schema: {exc}") from exc
    expected = [d.id for d in dims]
    seen: dict[str, DocScore] = {}
    for score in answer.scores:
        if score.dimension_id not in expected:
            raise JudgeError(f"unknown dimension id {score.dimension_id!r}; use exactly these ids: {expected}")
        if score.dimension_id in seen:
            raise JudgeError(f"dimension {score.dimension_id!r} is scored twice")
        seen[score.dimension_id] = score
    missing = [i for i in expected if i not in seen]
    if missing:
        raise JudgeError(f"missing scores for dimensions: {missing}")
    a: dict[str, int] = {}
    b: dict[str, int] | None = {} if has_b else None
    for dimension_id in expected:
        score = seen[dimension_id]
        _check_range(score.a, dimension_id, LABELS[0])
        a[dimension_id] = score.a
        if has_b:
            if score.b is None:
                raise JudgeError(f"{LABELS[1]} is present but has no score for {dimension_id!r}")
            _check_range(score.b, dimension_id, LABELS[1])
            b[dimension_id] = score.b  # type: ignore[index]
        elif score.b is not None:
            raise JudgeError(f"only one document was provided, but {dimension_id!r} has a second score; leave b null")
    return a, b, " ".join(answer.rationale.split())


# --- the call -------------------------------------------------------------------


def _rubric_listing(dims: Sequence[Dimension]) -> str:
    return "\n".join(f"- `{d.id}` — {d.name}: {d.description}" for d in dims)


def judge(
    model: Any,
    rubric: str | Sequence[Dimension],
    mission: str,
    candidate: str,
    incumbent: str | None = None,
    *,
    experiment: int | None = None,
    judge_model: str = "",
    rng: Any = None,
) -> Verdict:
    """Score `candidate` (and `incumbent`, if any) on the rubric; documents shown in random order.

    `rubric` is `rubric.md` text or parsed dimensions. `rng` needs a `.random()` (tests pass a fixed one).
    """
    dims = parse_rubric(rubric) if isinstance(rubric, str) else list(rubric)
    if not dims:
        raise JudgeError("rubric has no dimensions")
    rng = rng or random
    texts = {"candidate": candidate}
    if incumbent is None:
        order = ["candidate"]
    else:
        texts["incumbent"] = incumbent
        order = ["candidate", "incumbent"] if rng.random() < 0.5 else ["incumbent", "candidate"]
    docs = list(zip(LABELS, (texts[name] for name in order)))

    system = load_prompt("judge").format(
        rubric=_rubric_listing(dims), n_docs=len(docs), score_min=SCORE_MIN, score_max=SCORE_MAX
    )
    body = "\n\n".join(f"## {label}\n\n{text.strip()}" for label, text in docs)
    if len(docs) == 1:
        closing = "Only one document is provided; score it as `a` and leave every `b` null."
    else:
        closing = f"Score both documents on every dimension: `a` is {LABELS[0]}, `b` is {LABELS[1]}."
    messages: list[Any] = [
        SystemMessage(content=system),
        HumanMessage(content=f"Mission: {mission.strip()}\n\n{body}\n\n{closing}"),
    ]

    structured = model.with_structured_output(JudgeAnswer)
    error: str | None = None
    for _attempt in range(2):
        turn = messages if error is None else messages + [
            HumanMessage(content=f"Your previous answer was rejected: {error}\nReturn a corrected answer.")
        ]
        try:
            a, b, rationale = _validate_answer(structured.invoke(turn), dims, has_b=incumbent is not None)
        except Exception as exc:  # provider errors, schema errors, our own JudgeError
            error = " ".join(str(exc).split())
            continue
        by_label = {LABELS[0]: a, LABELS[1]: b}
        scores = {name: by_label[label] for name, (label, _text) in zip(order, docs)}
        cand = scores["candidate"]
        inc = scores.get("incumbent")
        return Verdict(
            experiment=experiment,
            judge_model=judge_model,
            order=order,
            candidate=cand,
            incumbent=inc,
            candidate_total=sum(cand.values()),
            incumbent_total=None if inc is None else sum(inc.values()),
            rationale=rationale,
        )
    raise JudgeError(f"could not get a valid verdict after one repair: {error}")
