# Implementer protocol (one run = one agent, sequential)

You are one link in a chain of implementer agents. Nothing carries over between agents except the repo. Budget: about 200k tokens for the whole run, so pick a piece you can finish, test and commit well within that.

## 1. Get the state (read, do not assume)
1. `docs/superpowers/plans/2026-09-10-autoresearch-frameworks.md` — milestones, verified facts, refinements, **Progress log** (read the last entries first).
2. `docs/superpowers/specs/2026-09-10-autoresearch-frameworks-design.md` — the contract.
3. `git log --oneline -15` and `git status`; `find autoresearch -type f -not -path '*/.venv/*' | sort`; skim existing modules and tests you will touch or depend on.
4. Run the suite to know the baseline: `autoresearch/.venv/bin/python -m pytest -m "not live" -q` (from repo root; set `PYTHONPATH=autoresearch` or run from `autoresearch/`).

## 2. Decide
Pick the next unfinished milestone piece (in order unless something is blocked). Write a 5–10 line plan: files, interfaces (match the plan's names), tests you will write first. If the last Progress entry left an open problem, that is your first candidate.

## 3. TDD
Failing test → minimal code → green → refactor. Tests are offline by default (temp git repos, fake chat model); anything that hits Gemini is `@pytest.mark.live`. Run the live test once if you added one (the `.env` in `autoresearch/` is loaded by `conftest.py` via python-dotenv; never print or commit secrets).

## 4. Verify
- Full offline suite green.
- If you touched `loop.py`, `review.py` or `langgraph.json`: `cd autoresearch && .venv/bin/langgraph dev --no-browser --port 2024` in the background, confirm `curl -s localhost:2024/ok` and that `curl -s -X POST localhost:2024/assistants/search -H 'content-type: application/json' -d '{}'` lists both graphs, then kill it.
- Quote the actual commands and outputs in your final report; no claims without evidence.

## 5. Commit and hand off
- `git add` only the files you changed (never `.env`, `.venv`, scratch). Commit message `<area>: <what>` + blank line + `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Tick milestone checkboxes you completed in the plan; append a Progress log entry (what, sha, test command + result, next, open problems). Commit that too (`plan: progress after <piece>`).
- Final report to the orchestrator: what you finished, sha(s), evidence, what the next agent should do, and whether the project is DONE (all milestones ticked and the definition of done met).

## Rules
- Work only under `autoresearch/` and the plan file. Do not `cd` outside the worktree. Never use bare `git stash`.
- Do not refactor finished modules unless a test forces it. Do not add features outside the spec.
- If blocked on something only the owner can provide (GitHub PAT, deploy), document the exact next command in the plan and move to the next unblocked piece.
