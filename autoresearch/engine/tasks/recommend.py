"""Recommend: a deep agent turns `decomposition.md` into `attempts/<n>/recommendations.md` (the judged artifact)."""

from __future__ import annotations

from typing import Any

from engine.tasks.propose import COMBINATION_NAME
from engine.tasks.steps import LIMITS, AgentFactory, brief_header, failure, run_step
from engine.workspace import Workspace

RECOMMENDATIONS_NAME = "recommendations.md"


def run(
    model: Any,
    ws: Workspace,
    n: int,
    decomposition: dict[str, Any],
    *,
    agent_factory: AgentFactory | None = None,
    recursion_limit: int = LIMITS["recommend"],
) -> dict[str, Any]:
    """`decomposition` is `decompose.run`'s result; returns `{"path", "content", "error"}`."""
    output_rel = ws.attempt_rel(n, RECOMMENDATIONS_NAME)
    if decomposition.get("error") or not str(decomposition.get("content", "")).strip():
        return failure(output_rel, f"no decomposition to recommend from: {decomposition.get('error') or 'empty content'}")
    ws.materialize(decomposition)
    brief = "\n".join(
        [
            brief_header(ws),
            "",
            f"Task: write the recommendations for experiment {n}.",
            f"Decomposition: {Workspace.virtual_repo(str(decomposition['path']))}",
            f"Combination it came from: {ws.virtual(f'attempts/{n}/{COMBINATION_NAME}')}",
            f"Write the recommendations to: {Workspace.virtual_repo(output_rel)}",
        ]
    )
    return run_step(
        model,
        ws,
        prompt_name="recommend",
        prompt_vars={},
        brief=brief,
        output_rel=output_rel,
        recursion_limit=recursion_limit,
        agent_factory=agent_factory,
    )
