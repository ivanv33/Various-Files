"""Decompose: a deep agent applies the combination to the transcript and writes `attempts/<n>/decomposition.md`.

The orchestrating agent fans out one `framework-decomposer` subagent per framework (each writes
`attempts/<n>/decomposition-<slug>.md`) and merges the results with a cross-framework synthesis.
"""

from __future__ import annotations

from typing import Any

from engine.prompts import load_prompt
from engine.tasks.propose import parse_combination
from engine.tasks.steps import LIMITS, brief_header, failure, run_step
from engine.workspace import Workspace

DECOMPOSITION_NAME = "decomposition.md"
SUBAGENT_NAME = "framework-decomposer"


def framework_decomposer_subagent() -> dict[str, Any]:
    """A `deepagents.SubAgent` spec; it shares the main agent's filesystem backend."""
    return {
        "name": SUBAGENT_NAME,
        "description": (
            "Applies ONE decomposition framework to the transcript and writes the result to the file path "
            "you give it. Give it: the framework slug and catalog entry, the combination's instructions for "
            "that framework, the transcript path, any earlier per-framework file it should build on, and the output path."
        ),
        "system_prompt": load_prompt("framework_decomposer"),
    }


def run(
    model: Any,
    ws: Workspace,
    n: int,
    combination: dict[str, Any],
    *,
    recursion_limit: int = LIMITS["decompose"],
) -> dict[str, Any]:
    """`combination` is `propose.run` / `use_seed`'s result; returns `{"path", "content", "error"}`."""
    output_rel = ws.attempt_rel(n, DECOMPOSITION_NAME)
    if combination.get("error") or not str(combination.get("content", "")).strip():
        return failure(output_rel, f"no combination to decompose: {combination.get('error') or 'empty content'}")
    ws.materialize(combination)
    frameworks, _note = parse_combination(str(combination["content"]))
    brief = "\n".join(
        [
            brief_header(ws),
            "",
            f"Task: decompose the transcript with the combination for experiment {n}.",
            f"Combination: {Workspace.virtual_repo(str(combination['path']))}",
            f"Frameworks to apply (from its frontmatter): {', '.join(frameworks) or '(none listed; read the body)'}",
            f"Catalog entries for each framework: {ws.virtual('catalog.json')}",
            f"Per-framework scratch files: {ws.virtual(f'attempts/{n}/decomposition-<slug>.md')}",
            f"Write the merged decomposition to: {Workspace.virtual_repo(output_rel)}",
        ]
    )
    return run_step(
        model,
        ws,
        prompt_name="decompose",
        prompt_vars={"subagent": SUBAGENT_NAME},
        brief=brief,
        output_rel=output_rel,
        recursion_limit=recursion_limit,
        subagents=[framework_decomposer_subagent()],
    )
