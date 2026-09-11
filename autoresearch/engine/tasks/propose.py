"""Propose: a deep agent picks the next framework combination and writes `combination-with-explanations.md`.

Seed mode (checkpoint 0) writes `best/combination-with-explanations.md`; experiment `n` writes
`attempts/<n>/combination-with-explanations.md`. The file starts with frontmatter
(`frameworks: [slug, ...]`, `note: <one line>`) that the loop parses for the log row; a
combination without parseable `frameworks:` is an error result. `use_seed` copies the committed
seed into `attempts/1/` for experiment 1 (spec 3, "Seed experiment").
"""

from __future__ import annotations

import re
from typing import Any

from engine.tasks.steps import LIMITS, AgentFactory, brief_header, failure, log_tail, run_step
from engine.workspace import Workspace

COMBINATION_NAME = "combination-with-explanations.md"
SEED_REL = f"best/{COMBINATION_NAME}"
INSIGHTS_LINE_BUDGET = 40

_FRONTMATTER = re.compile(r"\A\s*---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)
_SPLIT = re.compile(r"[+,\s]+")


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1].strip()
    return value


def _slugs(value: str) -> list[str]:
    value = _unquote(value).strip().strip("[]")
    return [s for s in (_unquote(part) for part in _SPLIT.split(value)) if s]


def parse_combination(text: str) -> tuple[list[str], str]:
    """`(frameworks, note)` from the frontmatter; `([], "")` when there is none.

    Accepts `frameworks: [a, b]`, `frameworks: a + b`, `frameworks: a, b` and a dash list on the
    following lines; `note:` may be quoted.
    """
    m = _FRONTMATTER.match(text)
    if not m:
        return [], ""
    frameworks: list[str] = []
    note = ""
    key: str | None = None
    for raw in m.group(1).splitlines():
        if not raw.strip():
            continue
        if raw[0] in " \t-" and key == "frameworks":
            item = raw.strip()
            if item.startswith("-"):
                frameworks += _slugs(item[1:])
            continue
        k, sep, v = raw.partition(":")
        if not sep:
            continue
        key = k.strip().lower()
        if key == "frameworks":
            frameworks = _slugs(v)
        elif key == "note":
            note = " ".join(_unquote(v).split())
    return frameworks, note


def _with_combination(result: dict[str, Any]) -> dict[str, Any]:
    frameworks, note = parse_combination(result["content"]) if result["content"] else ([], "")
    if result["error"] is None and not frameworks:
        result = {**result, "error": f"combination at {result['path']} has no `frameworks:` frontmatter"}
    return {**result, "frameworks": frameworks, "note": note}


def _brief(ws: Workspace, n: int | None, seed: bool, output_rel: str) -> str:
    lines = [brief_header(ws), ""]
    if seed:
        lines += [
            "Task: write the seed combination. There is no experiment log, no incumbent and no Insights yet; "
            "experiment 1 will evaluate exactly this file.",
        ]
    else:
        lines += [f"Task: propose the combination for experiment {n}.", log_tail(ws)]
        has_best = ws.has(SEED_REL)
        lines.append(
            f"Current best: {ws.virtual(SEED_REL)}"
            + (" plus best/recommendations.md and best/score.json" if has_best else " (absent)")
        )
    lines += [
        f"Catalog of frameworks: {ws.virtual('catalog.json')}",
        f"Write the combination to: {Workspace.virtual_repo(output_rel)}",
        f"Experiment number for proposal frontmatter: {n if n is not None else 0}",
    ]
    return "\n".join(lines)


def run(
    model: Any,
    ws: Workspace,
    n: int | None,
    *,
    seed: bool = False,
    agent_factory: AgentFactory | None = None,
    recursion_limit: int = LIMITS["propose"],
) -> dict[str, Any]:
    """Return `{"path", "content", "error", "frameworks", "note"}` for the new combination."""
    if seed:
        output_rel = ws.rel(SEED_REL)
    else:
        if n is None:
            raise ValueError("propose.run needs an experiment number n unless seed=True")
        output_rel = ws.attempt_rel(n, COMBINATION_NAME)
    result = run_step(
        model,
        ws,
        prompt_name="propose",
        prompt_vars={"insights_budget": INSIGHTS_LINE_BUDGET},
        brief=_brief(ws, n, seed, output_rel),
        output_rel=output_rel,
        recursion_limit=recursion_limit,
        agent_factory=agent_factory,
    )
    return _with_combination(result)


def use_seed(ws: Workspace, n: int) -> dict[str, Any]:
    """Experiment 1: copy the committed seed into `attempts/<n>/` instead of proposing."""
    output_rel = ws.attempt_rel(n, COMBINATION_NAME)
    if not ws.has(SEED_REL):
        return {**failure(output_rel, f"seed combination missing: {ws.rel(SEED_REL)}"), "frameworks": [], "note": ""}
    text = ws.read(SEED_REL)
    ws.write(f"attempts/{n}/{COMBINATION_NAME}", text)
    return _with_combination({"path": output_rel, "content": text, "error": None})
