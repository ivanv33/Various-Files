"""The judge's rubric: fixed core dimensions plus 1–3 mission-specific extras.

`draft_extras` is one structured-output call (with one repair retry) made at checkpoint 0; the
owner approves the result and the loop writes `rubric.md` with `render_rubric`. Every later step
reads the dimensions back with `parse_rubric`, so the two must round-trip. The file format is
plain markdown the owner (and the reviewer) may edit: only `### <id>: <name>` headings under the
two section headings are parsed; all other prose is ignored.
"""

from __future__ import annotations

import re
from typing import Any, Literal, Sequence

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError, field_validator

from engine.prompts import load_prompt

SCORE_MIN, SCORE_MAX = 1, 10
SCALE = f"{SCORE_MIN}-{SCORE_MAX}"
MIN_EXTRAS, MAX_EXTRAS = 1, 3
CORE_HEADING = "## Core dimensions"
EXTRAS_HEADING = "## Mission-specific dimensions"

_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_DIM_HEADING = re.compile(r"^###\s+([a-z][a-z0-9_]*)\s*:\s*(.+?)\s*$")


class RubricError(RuntimeError):
    """Extras could not be drafted, or `rubric.md` does not parse."""


class Dimension(BaseModel):
    id: str
    name: str
    description: str
    scale: str = SCALE
    kind: Literal["core", "extra"] = "core"

    @field_validator("id")
    @classmethod
    def _slug(cls, value: str) -> str:
        if not _ID_RE.match(value):
            raise ValueError(f"dimension id must match [a-z][a-z0-9_]*, got {value!r}")
        return value

    @field_validator("name", "description")
    @classmethod
    def _non_blank(cls, value: str) -> str:
        value = " ".join(str(value).split())
        if not value:
            raise ValueError("must not be blank")
        return value


CORE_DIMENSIONS: tuple[Dimension, ...] = (
    Dimension(
        id="specificity",
        name="Specificity",
        description=(
            "Each step names a concrete action, its object and, where possible, its owner and a first "
            "deadline. A 10 has no step that could be pasted into an unrelated plan; a 1 is generic advice."
        ),
    ),
    Dimension(
        id="grounding",
        name="Grounding in the transcript",
        description=(
            "Each step traces to something specific in the source document (a quoted claim, number or "
            "exchange) and the link is stated. A 10 grounds every step; a 1 could have been written "
            "without reading the transcript."
        ),
    ),
    Dimension(
        id="mission_fit",
        name="Mission fit",
        description=(
            "The steps, taken together, move the stated mission forward and nothing is off-target. A 10 "
            "covers the mission's main levers and risks; a 1 answers a different question."
        ),
    ),
    Dimension(
        id="actionability",
        name="Actionability and sequencing",
        description=(
            "The steps can be started now with the resources the mission implies, dependencies are "
            "ordered, and the first step is unambiguous. A 10 is a runnable plan; a 1 needs another "
            "planning pass."
        ),
    ),
    Dimension(
        id="insight",
        name="Non-obvious insight",
        description=(
            "The recommendations surface something a careful plain read of the transcript would miss: "
            "a gap, a contradiction, a leverage point the decomposition exposed. A 10 changes what you "
            "would do next; a 1 restates the transcript."
        ),
    ),
)


# --- extras (structured output) ---------------------------------------------


class ExtraDimension(BaseModel):
    name: str = Field(description="Short title, 1-4 words, not a synonym of a core dimension")
    description: str = Field(
        description=f"One or two sentences saying what a {SCORE_MAX} looks like and what a {SCORE_MIN} looks like"
    )


class RubricExtras(BaseModel):
    dimensions: list[ExtraDimension] = Field(
        description=f"{MIN_EXTRAS} to {MAX_EXTRAS} mission-specific dimensions the core rubric cannot see"
    )


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if not slug:
        return "dimension"
    return slug if slug[0].isalpha() else f"d_{slug}"


def validate_extras(extras: RubricExtras | dict[str, Any], core: Sequence[Dimension] = CORE_DIMENSIONS) -> list[Dimension]:
    """Turn a model answer into `Dimension(kind="extra")`s or raise `RubricError` with the reason."""
    if isinstance(extras, dict):
        try:
            extras = RubricExtras.model_validate(extras)
        except ValidationError as exc:
            raise RubricError(f"answer does not match the RubricExtras schema: {exc}") from exc
    items = extras.dimensions
    if not MIN_EXTRAS <= len(items) <= MAX_EXTRAS:
        raise RubricError(f"expected {MIN_EXTRAS} to {MAX_EXTRAS} extra dimensions, got {len(items)}")
    core_ids = {d.id for d in core}
    core_names = {d.name.lower() for d in core}
    dims: list[Dimension] = []
    for item in items:
        try:
            dim = Dimension(id=slugify(item.name), name=item.name, description=item.description, kind="extra")
        except ValidationError as exc:
            raise RubricError(f"bad extra dimension {item.name!r}: {exc}") from exc
        if dim.id in core_ids or dim.name.lower() in core_names:
            raise RubricError(f"{item.name!r} duplicates a core dimension; extras must add something the core cannot see")
        if any(dim.id == d.id for d in dims):
            raise RubricError(f"extra dimensions must be distinct; {item.name!r} repeats {dim.id!r}")
        dims.append(dim)
    return dims


def _core_listing(core: Sequence[Dimension]) -> str:
    return "\n".join(f"- {d.name} ({d.id}): {d.description}" for d in core)


def draft_extras(model: Any, mission: str, *, core: Sequence[Dimension] = CORE_DIMENSIONS) -> list[Dimension]:
    """One structured-output call, one repair retry with the validation error; then `RubricError`."""
    structured = model.with_structured_output(RubricExtras)
    system = load_prompt("rubric_extras").format(
        core_dimensions=_core_listing(core),
        mission=mission.strip(),
        min_extras=MIN_EXTRAS,
        max_extras=MAX_EXTRAS,
        score_min=SCORE_MIN,
        score_max=SCORE_MAX,
    )
    messages: list[Any] = [SystemMessage(content=system), HumanMessage(content=f"Mission: {mission.strip()}")]
    error: str | None = None
    for _attempt in range(2):
        turn = messages if error is None else messages + [
            HumanMessage(content=f"Your previous answer was rejected: {error}\nReturn a corrected answer.")
        ]
        try:
            return validate_extras(structured.invoke(turn), core)
        except Exception as exc:  # provider errors, schema errors, our own RubricError
            error = " ".join(str(exc).split())
    raise RubricError(f"could not draft rubric extras after one repair: {error}")


# --- rubric.md ----------------------------------------------------------------


def render_rubric(core: Sequence[Dimension], extras: Sequence[Dimension]) -> str:
    lines = [
        "# Rubric",
        "",
        f"Score each dimension from {SCORE_MIN} (absent or harmful) to {SCORE_MAX} (could not be better), "
        "integers only; the total is the sum over all dimensions. Core dimensions are fixed by the engine. "
        "Mission-specific dimensions were drafted for this session's mission and approved at checkpoint 0. "
        "Only the reviewer changes this file afterwards.",
        "",
        CORE_HEADING,
        "",
    ]
    for d in core:
        lines += [f"### {d.id}: {d.name}", "", d.description, ""]
    lines += [EXTRAS_HEADING, ""]
    if extras:
        for d in extras:
            lines += [f"### {d.id}: {d.name}", "", d.description, ""]
    else:
        lines += ["_None._", ""]
    return "\n".join(lines)


def parse_rubric(text: str) -> list[Dimension]:
    """Dimensions in file order; `kind` follows the section heading. Prose outside headings is ignored."""
    found: list[dict[str, Any]] = []
    kind: str | None = None
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line == CORE_HEADING or line == EXTRAS_HEADING:
            kind = "core" if line == CORE_HEADING else "extra"
            current = None
            continue
        if line.startswith("## ") or line.startswith("# "):
            kind, current = None, None  # some other section: not a dimension list
            continue
        m = _DIM_HEADING.match(line)
        if m:
            if kind is None:
                current = None
                continue
            current = {"id": m.group(1), "name": m.group(2), "kind": kind, "lines": []}
            found.append(current)
            continue
        if current is not None and line:
            current["lines"].append(line)
    if not found:
        raise RubricError(
            f"rubric has no dimensions: expected '### <id>: <name>' headings under '{CORE_HEADING}' / '{EXTRAS_HEADING}'"
        )
    ids = [d["id"] for d in found]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise RubricError(f"rubric has duplicate dimension ids: {dupes}")
    dims: list[Dimension] = []
    for d in found:
        try:
            dims.append(Dimension(id=d["id"], name=d["name"], description=" ".join(d["lines"]), kind=d["kind"]))
        except ValidationError as exc:
            raise RubricError(f"dimension {d['id']!r} is malformed: {exc}") from exc
    return dims
