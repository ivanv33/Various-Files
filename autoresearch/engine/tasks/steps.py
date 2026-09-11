"""Shared plumbing for the deep-agent steps (`propose`, `decompose`, `recommend`).

Each step builds a fresh deep agent over a `FilesystemBackend` rooted at the clone (fresh context,
no thread), hands it a short brief that names the session files by their virtual paths, and then
checks the output file. Failures never raise: they come back as
`{"path": <repo-relative>, "content": "", "error": <one-line reason>}` so a `@task` result is
cached on resume and the loop logs the attempt as `kept=error` (refinement 6). Successful results
are `{"path", "content", "error": None}`; the loop re-materializes `content` when the file is gone
(refinement 2).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from langchain_core.messages import AIMessage, HumanMessage

from engine.prompts import load_prompt
from engine.workspace import Workspace

LIMITS: dict[str, int] = {"propose": 120, "decompose": 150, "recommend": 80}
"""`recursion_limit` per step (refinement 6)."""

TAIL_ROWS = 12
"""How many recent `experiments.tsv` rows a brief spells out inline."""

EMPTY_REPLY_RETRIES = 1
"""How many times a step nudges the agent when its turn ends with an empty reply and no output file. Gemini
occasionally returns `finish_reason STOP` with empty content and no tool call mid-task; without the nudge the
attempt is lost as `kept=error`."""

EMPTY_REPLY_NUDGE = (
    "Your last reply was empty and the output file {output} does not exist or is blank. "
    "Continue from where you stopped and finish by writing the complete output file at that path with your file tools."
)

DENIED_PATHS = ("/.git", "/.git/**")
"""Virtual paths no agent (or subagent) may read or write: the clone's git metadata. Agents never run git, and
`git_ops.split_remote` keeps the remote token out of `.git/config`; this rule is the second layer."""


def default_agent_factory(*, model: Any, root: str, system_prompt: str, subagents: Sequence[Any] | None = None) -> Any:
    """A `deepagents` deep agent over the clone. `checkpointer=False`: the step is a cached `@task`,
    so the agent's own state must not be persisted under the loop's thread.

    `run_step` looks this name up at call time, so tests replace it with `monkeypatch.setattr(steps,
    "default_agent_factory", stub)` -- the one seam for every step."""
    from deepagents import FilesystemPermission, create_deep_agent
    from deepagents.backends import FilesystemBackend

    return create_deep_agent(
        model=model,
        backend=FilesystemBackend(root_dir=root, virtual_mode=True),
        system_prompt=system_prompt,
        subagents=list(subagents) if subagents else None,
        permissions=[FilesystemPermission(operations=["read", "write"], paths=list(DENIED_PATHS), mode="deny")],
        checkpointer=False,
    )


def failure(output_rel: str, reason: str) -> dict[str, Any]:
    return {"path": output_rel, "content": "", "error": " ".join(str(reason).split())[:600]}


def describe(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def brief_header(ws: Workspace) -> str:
    """The lines every step's brief starts with (spec 4.1)."""
    return "\n".join(
        [
            f"Mission: {ws.mission.strip()}",
            f"Session folder: {ws.virtual('')[:-1]}",
            f"Transcript: {Workspace.virtual_repo(ws.transcript_path)}",
            f"Rubric: {ws.virtual('rubric.md')}",
            f"Experiment log: {ws.virtual('experiments.tsv')} (tab-separated; columns n, timestamp, frameworks, "
            "candidate_total, incumbent_total, kept, note)",
            f"Notes: {ws.virtual('notes.md')} (sections: Insights, Human steering)",
            "Before acting, read the tail of the experiment log and notes.md; Human steering overrides everything else.",
            "Use only your file tools; never run git. Paths above are absolute paths for your tools.",
        ]
    )


def log_tail(ws: Workspace, rows: int = TAIL_ROWS) -> str:
    """Recent attempts as `n: frameworks -> kept, candidate vs incumbent` lines (or a one-line note)."""
    tail = ws.rows()[-rows:]
    if not tail:
        return "Framework sets already tried: none (this is the first attempt)."
    lines = ["Framework sets already tried (n: frameworks -> kept, candidate_total vs incumbent_total):"]
    for r in tail:
        inc = "-" if r.incumbent_total is None else str(r.incumbent_total)
        cand = "-" if r.candidate_total is None else str(r.candidate_total)
        lines.append(f"  {r.n}: {'+'.join(r.frameworks) or '(none)'} -> kept {r.kept}, {cand} vs {inc}")
    return "\n".join(lines)


def run_step(
    model: Any,
    ws: Workspace,
    *,
    prompt_name: str,
    prompt_vars: Mapping[str, Any],
    brief: str,
    output_rel: str,
    recursion_limit: int,
    subagents: Sequence[Any] | None = None,
) -> dict[str, Any]:
    """Build the agent from `prompts/<prompt_name>.md`, run it once on `brief`, check `output_rel`.

    When the run ends with an empty AI reply (no content, no tool call) and the output is still missing, the same
    conversation is re-invoked up to `EMPTY_REPLY_RETRIES` times with a nudge; the agent has no checkpointer, so the
    history is carried explicitly."""
    system_prompt = load_prompt(prompt_name).format(**prompt_vars)
    config = {"recursion_limit": recursion_limit}
    empty_replies = 0
    try:
        agent = default_agent_factory(model=model, root=str(ws.root), system_prompt=system_prompt, subagents=subagents)
        state = agent.invoke({"messages": [HumanMessage(content=brief)]}, config=config)
        while finish(ws, output_rel)["error"] and ended_with_empty_reply(state) and empty_replies < EMPTY_REPLY_RETRIES:
            empty_replies += 1
            history = list(state["messages"]) + [HumanMessage(content=EMPTY_REPLY_NUDGE.format(output=output_rel))]
            state = agent.invoke({"messages": history}, config=config)
    except Exception as exc:  # recursion limit, provider errors, tool errors: the attempt becomes kept=error
        return failure(output_rel, describe(exc))
    result = finish(ws, output_rel)
    if result["error"] and empty_replies:
        result = failure(output_rel, f"{result['error']} (agent ended with an empty reply {empty_replies + 1} times)")
    return result


def ended_with_empty_reply(state: Any) -> bool:
    """True when the agent's final message is an AI turn with no content and no tool call."""
    try:
        last = state["messages"][-1]
    except (KeyError, IndexError, TypeError):
        return False
    if not isinstance(last, AIMessage) or getattr(last, "tool_calls", None):
        return False
    content = last.content
    if isinstance(content, list):
        content = " ".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    return not str(content).strip()


def finish(ws: Workspace, output_rel: str) -> dict[str, Any]:
    """Read the step's output file; missing or blank is an error result (spec 4.1 output contract)."""
    path = ws.root / output_rel
    if not path.is_file():
        return failure(output_rel, f"output missing or empty: {output_rel}")
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        return failure(output_rel, f"output missing or empty: {output_rel}")
    return {"path": output_rel, "content": content, "error": None}
