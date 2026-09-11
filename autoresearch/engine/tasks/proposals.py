"""Proposal files (`proposals/*.md`) and the reviewer's decisions on them (spec 5).

A proposal is markdown with a small frontmatter (`status: open|accepted|rejected`, `experiment: n`, `title`).
Its kind and slug come from the file name: `new-framework-<slug>.md` or `rubric-change-<slug>.md`. The reviewer
makes one structured-output call per open proposal (one repair retry, like `rubric.draft_extras`) unless a
deterministic check settles it first (unknown kind, slug already in the catalog, no approved rubric yet), then
applies the decision: a catalog entry, or a re-rendered rubric plus a `## Rubric changes` line in `notes.md`,
and in every case the frontmatter (`status`, `decision_reason`). Nothing here runs git or raises for model
failures: `decide` returns a decision with `error` set and `apply_decision` then leaves the proposal open.
"""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from engine.prompts import load_prompt
from engine.tasks.log import utc_now
from engine.tasks.notes import append_under_heading
from engine.tasks.rubric import (
    CORE_DIMENSIONS,
    Dimension,
    ExtraDimension,
    RubricError,
    RubricExtras,
    parse_rubric,
    render_rubric,
    validate_extras,
)
from engine.tasks.steps import describe, log_tail
from engine.workspace import Workspace

PROPOSALS_DIR = "proposals"
CATALOG_NAME = "catalog.json"
RUBRIC_NAME = "rubric.md"
NOTES_NAME = "notes.md"
RUBRIC_CHANGES_HEADING = "## Rubric changes"
KIND_FRAMEWORK, KIND_RUBRIC, KIND_UNKNOWN = "new-framework", "rubric-change", "unknown"
STATUS_OPEN, STATUS_ACCEPTED, STATUS_REJECTED = "open", "accepted", "rejected"
ENTRY_FIELDS = ("name", "category", "summary", "when_to_use")

_FRONTMATTER = re.compile(r"\A\s*---[ \t]*\n((?:.*\n)*?)---[ \t]*(?:\n|\Z)")  # leading blank lines tolerated
_FIELD = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$")
_KIND = re.compile(rf"^({KIND_FRAMEWORK}|{KIND_RUBRIC})-([a-z0-9][a-z0-9-]*)\.md$")


class ReviewError(RuntimeError):
    """A decision could not be made or validated."""


def one_line(value: Any) -> str:
    return " ".join(str(value).split())


def basename(rel: str) -> str:
    return rel.rsplit("/", 1)[-1]


# --- proposal files ----------------------------------------------------------------


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """`(fields, body)`; `({}, text)` when there is no frontmatter. Values keep their text, minus matching quotes."""
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, text
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        f = _FIELD.match(line)
        if f:
            value = f.group(2)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            fields[f.group(1)] = value
    return fields, text[m.end() :]


def set_frontmatter(text: str, **fields: Any) -> str:
    """Replace or append `key: value` lines (values collapsed to one line); creates the frontmatter if missing."""
    values = {k: one_line(v) for k, v in fields.items()}
    m = _FRONTMATTER.match(text)
    lines = m.group(1).splitlines() if m else []
    body = text[m.end() :] if m else text
    out: list[str] = []
    for line in lines:
        f = _FIELD.match(line)
        if f and f.group(1) in values:
            out.append(f"{f.group(1)}: {values.pop(f.group(1))}")
        else:
            out.append(line)
    out += [f"{k}: {v}" for k, v in values.items()]
    return "---\n" + "\n".join(out) + "\n---\n" + body


def proposal_status(text: str) -> str:
    """`status:` from the frontmatter; `open` when absent (an unlabeled proposal still needs a decision)."""
    return parse_frontmatter(text)[0].get("status", "").strip().lower() or STATUS_OPEN


def proposal_kind(rel: str) -> tuple[str, str]:
    """`(kind, slug)` from the file name; `("unknown", "")` for anything but `new-framework-*` / `rubric-change-*`."""
    m = _KIND.match(basename(rel))
    return (m.group(1), m.group(2)) if m else (KIND_UNKNOWN, "")


def list_proposals(ws: Workspace) -> tuple[list[str], list[str]]:
    """`(open, decided)` repo-relative paths of `proposals/*.md`, sorted by name."""
    folder = ws.path(PROPOSALS_DIR)
    if not folder.is_dir():
        return [], []
    open_, decided = [], []
    for p in sorted(folder.glob("*.md")):
        rel = ws.rel(f"{PROPOSALS_DIR}/{p.name}")
        (open_ if proposal_status(p.read_text(encoding="utf-8")) == STATUS_OPEN else decided).append(rel)
    return open_, decided


def add_rubric_change_note(notes: str, text: str, timestamp: str | None = None) -> str:
    """Append a timestamped list item at the end of `## Rubric changes` (created at the end of the notes if missing)."""
    return append_under_heading(notes, RUBRIC_CHANGES_HEADING, f"- {timestamp or utc_now()}: {one_line(text)}\n")


# --- session views ---------------------------------------------------------------------


def load_catalog(ws: Workspace) -> list[dict[str, Any]]:
    return json.loads(ws.read(CATALOG_NAME)) if ws.has(CATALOG_NAME) else []


def catalog_listing(catalog: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {e.get('slug')} ({e.get('category')}): {one_line(e.get('summary', ''))}" for e in catalog) or "(empty)"


def core_dimensions(rubric_text: str) -> list[Dimension]:
    """The core dimensions as written in `rubric.md` (owner edits included); the engine's when it does not parse."""
    try:
        core = [d for d in parse_rubric(rubric_text) if d.kind == "core"]
    except RubricError:
        core = []
    return core or list(CORE_DIMENSIONS)


# --- decisions (structured output) ---------------------------------------------------


class ProposedFramework(BaseModel):
    name: str = Field(description="Framework name as practitioners say it")
    category: str = Field(description="One of the catalog's category ids, e.g. 02-strategic-and-business")
    summary: str = Field(description="One or two sentences: what it decomposes and into what")
    when_to_use: str = Field(description="When it beats the neighbouring catalog entries, and its failure modes")


class FrameworkDecision(BaseModel):
    accept: bool
    reason: str = Field(description="One or two specific sentences the proposer will read; cite the catalog or the log")
    entry: ProposedFramework | None = Field(default=None, description="Required when accept is true: the catalog entry to add")


class RubricDecision(BaseModel):
    accept: bool
    reason: str = Field(description="One or two specific sentences the proposer will read; cite the rubric or the log")
    dimensions: list[ExtraDimension] | None = Field(
        default=None,
        description="Required when accept is true: the complete new list of 1-3 mission-specific dimensions (core dimensions never change)",
    )


def decision(
    file: str, kind: str, slug: str, *, accept: bool, reason: str, payload: dict[str, Any] | None = None, error: str | None = None
) -> dict[str, Any]:
    return {"file": file, "kind": kind, "slug": slug, "accept": accept, "reason": reason, "payload": payload, "error": error}


def precheck(ws: Workspace, rel: str) -> dict[str, Any] | None:
    """A rejection that needs no model: unknown kind, slug already in the catalog, or no approved rubric yet."""
    kind, slug = proposal_kind(rel)
    if kind == KIND_UNKNOWN:
        reason = f"unsupported proposal kind: the file must be named {KIND_FRAMEWORK}-<slug>.md or {KIND_RUBRIC}-<slug>.md"
        return decision(rel, kind, slug, accept=False, reason=reason)
    if kind == KIND_FRAMEWORK and any(e.get("slug") == slug for e in load_catalog(ws)):
        return decision(rel, kind, slug, accept=False, reason=f"the catalog already has a framework with slug {slug!r}")
    if kind == KIND_RUBRIC and not ws.has(RUBRIC_NAME):
        reason = f"{RUBRIC_NAME} has not been approved yet (checkpoint 0); the rubric cannot change before it exists"
        return decision(rel, kind, slug, accept=False, reason=reason)
    return None


def validate_decision(kind: str, answer: Any, core: list[Dimension]) -> tuple[bool, str, dict[str, Any] | None]:
    """`(accept, reason, payload)` from a model answer, or `ReviewError` / `RubricError` naming what to fix."""
    reason = one_line(answer.reason)
    if not reason:
        raise ReviewError("reason must not be blank")
    if not answer.accept:
        return False, reason, None
    if kind == KIND_FRAMEWORK:
        if answer.entry is None:
            raise ReviewError("accept is true but entry is missing: supply name, category, summary and when_to_use, or reject")
        fields = {k: one_line(getattr(answer.entry, k)) for k in ENTRY_FIELDS}
        blank = [k for k, v in fields.items() if not v]
        if blank:
            raise ReviewError(f"entry fields must not be blank: {', '.join(blank)}")
        return True, reason, fields
    if not answer.dimensions:
        raise ReviewError("accept is true but dimensions is missing: supply the complete new list of 1-3 mission-specific dimensions, or reject")
    extras = validate_extras(RubricExtras(dimensions=answer.dimensions), core)
    return True, reason, {"dimensions": [d.model_dump(mode="json") for d in extras]}


def decide(model: Any, ws: Workspace, rel: str) -> dict[str, Any]:
    """One structured-output call (one repair retry) unless `precheck` settles it; never raises (see `error`)."""
    pre = precheck(ws, rel)
    if pre is not None:
        return pre
    kind, slug = proposal_kind(rel)
    name = basename(rel)
    rubric_text = ws.read(RUBRIC_NAME) if ws.has(RUBRIC_NAME) else "(not drafted yet)"
    system = load_prompt("review").format(
        mission=ws.mission.strip(),
        rubric=rubric_text.strip(),
        catalog=catalog_listing(load_catalog(ws)),
        log=log_tail(ws),
    )
    human = f"Proposal file: {name}\nKind: {kind}\nSlug: {slug}\n\n{ws.read(f'{PROPOSALS_DIR}/{name}')}"
    messages: list[Any] = [SystemMessage(content=system), HumanMessage(content=human)]
    structured = model.with_structured_output(FrameworkDecision if kind == KIND_FRAMEWORK else RubricDecision)
    core = core_dimensions(rubric_text)
    error: str | None = None
    for _attempt in range(2):
        turn = messages if error is None else messages + [
            HumanMessage(content=f"Your previous answer was rejected: {error}\nReturn a corrected answer.")
        ]
        try:
            accept, reason, payload = validate_decision(kind, structured.invoke(turn), core)
            return decision(rel, kind, slug, accept=accept, reason=reason, payload=payload)
        except Exception as exc:  # provider errors, schema errors, ReviewError / RubricError
            error = one_line(describe(exc))
    failure = f"could not decide {name} after one repair: {error}"
    return decision(rel, kind, slug, accept=False, reason=failure, error=failure)


def apply_decision(ws: Workspace, decision: dict[str, Any]) -> dict[str, Any]:
    """Apply an accepted change, then write `status` / `decision_reason`; an errored decision changes nothing."""
    rel = decision["file"]
    name = basename(rel)
    if decision.get("error"):
        return {"file": rel, "status": STATUS_OPEN, "changed": []}
    changed: list[str] = []
    if decision["accept"] and decision["kind"] == KIND_FRAMEWORK:
        catalog = load_catalog(ws)
        catalog.append({"slug": decision["slug"], **decision["payload"], "source": f"proposal:{name}"})
        ws.write(CATALOG_NAME, json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
        changed.append(ws.rel(CATALOG_NAME))
    elif decision["accept"] and decision["kind"] == KIND_RUBRIC:
        core = core_dimensions(ws.read(RUBRIC_NAME))
        extras = [Dimension.model_validate(d) for d in decision["payload"]["dimensions"]]
        ws.write(RUBRIC_NAME, render_rubric(core, extras))
        notes = ws.read(NOTES_NAME) if ws.has(NOTES_NAME) else ""
        line = f"{name} accepted; mission-specific dimensions are now {', '.join(d.id for d in extras)}. {decision['reason']}"
        ws.write(NOTES_NAME, add_rubric_change_note(notes, line))
        changed += [ws.rel(RUBRIC_NAME), ws.rel(NOTES_NAME)]
    status = STATUS_ACCEPTED if decision["accept"] else STATUS_REJECTED
    local = f"{PROPOSALS_DIR}/{name}"
    ws.write(local, set_frontmatter(ws.read(local), status=status, decision_reason=decision["reason"]))
    changed.append(rel)
    return {"file": rel, "status": status, "changed": changed}
