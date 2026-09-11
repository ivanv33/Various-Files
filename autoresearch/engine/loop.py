"""`autoresearch_session`: the experiment loop as a LangGraph Functional API entrypoint (spec 3 + refinements 1-2).

Control flow is plain Python. Every side-effecting step is a `@task`, so on resume after `interrupt()` the
body replays from the top and finished steps return their cached results without running; `ensure_workspace`
is a plain function and really re-creates the clone. Tasks receive strings and dicts (`root`, `branch`, `n`,
step results) and rebuild `Workspace` / the chat model inside.

Replay determinism (refinement 8): cached task results and `interrupt()` values are matched by *call order*
within the entrypoint run, so every decision the body makes must come out the same on each replay. The two
facts that drive control flow -- is `rubric.md` present, how many experiments are logged -- are therefore read
through the `read_state` task instead of straight from the clone (which `ensure_workspace` resets to origin,
where they may already have changed). Everything else follows spec 3 literally.
"""

from __future__ import annotations

from typing import Any

from langgraph.func import entrypoint, task
from langgraph.types import interrupt

from engine.config import Settings, make_model
from engine.tasks import decompose as decompose_mod
from engine.tasks import git_ops
from engine.tasks import propose as propose_mod
from engine.tasks import recommend as recommend_mod
from engine.tasks.judge import Verdict, judge
from engine.tasks.log import LogRow, append_row, digest, utc_now
from engine.tasks.notes import append_under_heading
from engine.tasks.promote import SCORE_NAME, promote
from engine.tasks.rubric import CORE_DIMENSIONS, Dimension, draft_extras, render_rubric
from engine.tasks.steps import describe
from engine.workspace import Workspace

RUBRIC_NAME = "rubric.md"
NOTES_NAME = "notes.md"
STEERING_HEADING = "## Human steering"
BEST_RECOMMENDATIONS = "best/recommendations.md"
ERROR_SUBJECT_CHARS = 80


# --- tasks ---------------------------------------------------------------------


@task
def read_state(root: str, branch: str) -> dict[str, Any]:
    """The facts the body branches on; cached per call so replays repeat the original decisions."""
    ws = Workspace(root, branch)
    return {
        "has_rubric": ws.has(RUBRIC_NAME),
        "n_experiments": ws.n_experiments(),
        "max_experiments": ws.max_experiments,
    }


@task
def draft_rubric_extras(root: str, branch: str) -> list[dict[str, Any]]:
    ws = Workspace(root, branch)
    return [d.model_dump(mode="json") for d in draft_extras(make_model(), ws.mission)]


@task
def propose_step(root: str, branch: str, n: int | None, seed: bool) -> dict[str, Any]:
    return propose_mod.run(make_model(), Workspace(root, branch), n, seed=seed)


@task
def use_seed_step(root: str, branch: str, n: int) -> dict[str, Any]:
    return propose_mod.use_seed(Workspace(root, branch), n)


@task
def decompose_step(root: str, branch: str, n: int, combination: dict[str, Any]) -> dict[str, Any]:
    return decompose_mod.run(make_model(), Workspace(root, branch), n, combination)


@task
def recommend_step(root: str, branch: str, n: int, decomposition: dict[str, Any]) -> dict[str, Any]:
    return recommend_mod.run(make_model(), Workspace(root, branch), n, decomposition)


@task
def judge_step(root: str, branch: str, n: int, recommendations: dict[str, Any], judge_model: str) -> dict[str, Any]:
    """`{"verdict": Verdict dump | None, "error": str | None}`; never raises for judge or upstream failures."""
    if recommendations.get("error") or not str(recommendations.get("content", "")).strip():
        return {"verdict": None, "error": f"nothing to judge: {recommendations.get('error') or 'empty recommendations'}"}
    ws = Workspace(root, branch)
    incumbent = ws.read(BEST_RECOMMENDATIONS) if ws.has(BEST_RECOMMENDATIONS) else None
    try:
        verdict = judge(
            make_model(),
            ws.read(RUBRIC_NAME),
            ws.mission,
            str(recommendations["content"]),
            incumbent,
            experiment=n,
            judge_model=judge_model,
        )
    except Exception as exc:  # JudgeError after the repair retry, provider errors, a malformed rubric
        return {"verdict": None, "error": describe(exc)}
    return {"verdict": verdict.model_dump(mode="json"), "error": None}


@task
def promote_step(root: str, branch: str, n: int, results: list[dict[str, Any]], verdict: dict[str, Any]) -> list[str]:
    """Re-materialize the attempt's files (they are scratch and may be gone after a restart), then promote."""
    ws = Workspace(root, branch)
    for result in results:
        ws.materialize(result)
    return promote(ws, n, Verdict.model_validate(verdict))


@task
def append_log(root: str, branch: str, row: dict[str, Any]) -> dict[str, Any]:
    """Revert stray edits outside the allowlist (naming them in `note`), then append the row."""
    ws = Workspace(root, branch)
    strays = git_ops.revert_stray_changes(root, ws.session_rel)
    if strays:
        row = {**row, "note": " | ".join(filter(None, [row.get("note", ""), f"reverted stray changes: {', '.join(strays)}"]))}
    log_row = LogRow.model_validate(row)
    append_row(root, ws.session_rel, log_row)
    return log_row.model_dump(mode="json")


@task
def apply_steer(root: str, branch: str, rubric: str | None, steer: str) -> dict[str, bool]:
    """Write `rubric.md` (checkpoint 0 only) and append the owner's steer under `## Human steering`."""
    ws = Workspace(root, branch)
    wrote_rubric = False
    if rubric and not ws.has(RUBRIC_NAME):
        ws.write(RUBRIC_NAME, rubric)
        wrote_rubric = True
    steer = steer.strip()
    if steer:
        notes = ws.read(NOTES_NAME) if ws.has(NOTES_NAME) else ""
        ws.write(NOTES_NAME, add_steering(notes, steer))
    return {"rubric": wrote_rubric, "steer": bool(steer)}


@task
def pull_step(root: str, branch: str) -> str:
    return git_ops.pull(root, branch)


@task
def commit_push_step(root: str, branch: str, message: str) -> str | None:
    return git_ops.commit_push(root, branch, message)


# --- helpers (pure) ------------------------------------------------------------


def add_steering(notes: str, steer: str, timestamp: str | None = None) -> str:
    """Append a timestamped entry at the end of the `## Human steering` section (created if missing)."""
    body = "\n  ".join(steer.strip().splitlines())
    return append_under_heading(notes, STEERING_HEADING, f"- {timestamp or utc_now()}: {body}\n")


def parse_reply(reply: Any) -> tuple[str, str]:
    """`(action, steer)` from a resume payload; anything but `stop` continues."""
    if isinstance(reply, str):
        return ("stop" if reply.strip().lower() == "stop" else "continue"), ""
    if not isinstance(reply, dict):
        return "continue", ""
    action = str(reply.get("action") or "continue").strip().lower()
    steer = reply.get("steer") or ""
    return ("stop" if action == "stop" else "continue"), str(steer)


def first_error(*results: dict[str, Any]) -> str | None:
    for r in results:
        if r.get("error"):
            return str(r["error"])
    return None


def experiment_row(n: int, combo: dict[str, Any], verdict: Verdict | None, error: str | None) -> dict[str, Any]:
    if error is not None or verdict is None:
        return {"n": n, "frameworks": combo.get("frameworks", []), "kept": "error", "note": error or "no verdict"}
    return {
        "n": n,
        "frameworks": combo.get("frameworks", []),
        "candidate_total": verdict.candidate_total,
        "incumbent_total": verdict.incumbent_total,
        "kept": verdict.kept,
        "note": combo.get("note", ""),
    }


def commit_subject(n: int, verdict: Verdict | None, error: str | None) -> str:
    if error is not None or verdict is None:
        return f"exp {n}: ERROR {(error or 'no verdict')[:ERROR_SUBJECT_CHARS]}"
    inc = "-" if verdict.incumbent_total is None else str(verdict.incumbent_total)
    return f"exp {n}: {'KEEP' if verdict.kept else 'discard'} {verdict.candidate_total} vs {inc}"


def summary(ws: Workspace, stopped: str) -> dict[str, Any]:
    rows = ws.rows()
    best_total = best_experiment = None
    if ws.has(f"best/{SCORE_NAME}"):
        score = Verdict.model_validate_json(ws.read(f"best/{SCORE_NAME}"))
        best_total, best_experiment = score.candidate_total, score.experiment
    return {
        "branch": ws.branch,
        "head": git_ops.git(ws.root, "rev-parse", "HEAD"),
        "attempts": len(rows),
        "kept": sum(1 for r in rows if r.kept == "1"),
        "best_total": best_total,
        "best_experiment": best_experiment,
        "stopped": stopped,
    }


# --- the entrypoint body ------------------------------------------------------


def run_session(inputs: dict[str, Any]) -> dict[str, Any]:
    branch = str(inputs["branch"])
    settings = Settings.from_env()
    ws = git_ops.ensure_workspace(branch, settings)  # plain: really re-creates the clone on every (re)run
    root = str(ws.root)

    state = read_state(root, branch).result()
    if not state["has_rubric"]:  # checkpoint 0 (refinement 1: seed is pushed before the pause)
        extras = draft_rubric_extras(root, branch).result()
        rubric = render_rubric(CORE_DIMENSIONS, [Dimension.model_validate(d) for d in extras])
        seed = propose_step(root, branch, None, True).result()
        sha = commit_push_step(root, branch, "checkpoint 0 draft: seed combination").result()
        reply = interrupt(digest("checkpoint0", branch=branch, rubric=rubric, seed=seed, sha=sha))
        action, steer = parse_reply(reply)
        if action == "stop":
            return summary(ws, "checkpoint0")
        apply_steer(root, branch, rubric, steer).result()
        commit_push_step(root, branch, "checkpoint 0: rubric approved").result()
        state = read_state(root, branch).result()

    stopped = "max_experiments"
    while state["n_experiments"] < state["max_experiments"]:
        pull_step(root, branch).result()
        n = state["n_experiments"] + 1
        combo = (use_seed_step(root, branch, n) if n == 1 else propose_step(root, branch, n, False)).result()
        decomp = decompose_step(root, branch, n, combo).result()
        recs = recommend_step(root, branch, n, decomp).result()
        judged = judge_step(root, branch, n, recs, settings.gemini_model).result()
        error = first_error(combo, decomp, recs, judged)
        verdict = Verdict.model_validate(judged["verdict"]) if judged["verdict"] else None
        kept = error is None and verdict is not None and verdict.kept
        if kept:
            promote_step(root, branch, n, [combo, decomp, recs], judged["verdict"]).result()
        append_log(root, branch, experiment_row(n, combo, verdict, error)).result()
        sha = commit_push_step(root, branch, commit_subject(n, verdict, error)).result()
        if kept:
            reply = interrupt(digest("new_best", branch=branch, n=n, verdict=verdict, trend=ws.totals(), sha=sha))
            action, steer = parse_reply(reply)
            if action == "stop":
                stopped = "stop"
                break
            apply_steer(root, branch, None, steer).result()
            commit_push_step(root, branch, f"steer after exp {n}").result()
        state = read_state(root, branch).result()
    return summary(ws, stopped)


def build_graph(checkpointer: Any = None):
    """The compiled entrypoint. Deployments pass no checkpointer (the platform supplies one); tests pass `MemorySaver()`."""
    return entrypoint(checkpointer=checkpointer)(run_session)


autoresearch_session = build_graph()
