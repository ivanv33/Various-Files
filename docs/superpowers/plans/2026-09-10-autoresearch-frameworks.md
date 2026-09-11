# Autoresearch over Frameworks — Implementation Plan

> **For agentic workers:** this plan is deliberately high level. Implementers work Markov-chain style: read the state (this file's Progress log, `git log`, the tree under `autoresearch/`, the spec), pick the next milestone piece that fits your budget, TDD it, verify, commit, append a Progress log entry. Protocol: `autoresearch/dev/IMPLEMENTER.md`.

**Goal:** ship the engine described in `docs/superpowers/specs/2026-09-10-autoresearch-frameworks-design.md` (the contract) so `autoresearch_session` runs end to end under `langgraph dev` against a real session branch, and is ready for `langgraph deploy`.

**Architecture:** LangGraph Functional API (`@entrypoint` / `@task`) loop in `autoresearch/engine/loop.py`; creative steps are `deepagents` deep agents over a `FilesystemBackend` rooted at a fresh git clone; judge is a structured-output call; every attempt is committed and pushed to the session branch, which is the only memory across experiments and containers.

**Tech Stack:** Python 3.13, `uv`, langgraph 1.2.11, deepagents 0.7.13, langchain 1.4.0, langchain-google-genai 4.4.0, pytest 9, langgraph-cli 0.4.31 (`langgraph dev`, `langgraph deploy`).

## Global constraints

- Spec is the contract. Deviations only where this plan says so (see "Refinements"). If you must deviate elsewhere, record it in the Progress log with a reason.
- Work only inside `autoresearch/` (plus this plan file). Never edit `.env`; never commit secrets. `.env` is gitignored; `.env.example` documents variables.
- All model calls go through `GEMINI_MODEL` (`gemini-3.8-flash`, verified live) via `init_chat_model(f"google_genai:{GEMINI_MODEL}")`. Same model for every role.
- Every side-effecting step in the loop is a `@task` (checkpointed, replayed from cache on resume); `ensure_workspace` is a plain function. Task arguments and return values must be serializable (strings, dicts, pydantic models). Pass `ws.root` and `branch` as strings, not a live object.
- Agents never run git. `commit_push` stages only the session-folder allowlist: `experiments.tsv`, `notes.md`, `proposals/`, `best/`, `rubric.md`, `catalog.json`. `attempts/` is never staged.
- Tests must not need network or Gemini unless marked `@pytest.mark.live`. Default `pytest` run = offline, temp git repos, fake model.
- One commit per finished unit of work, message `<area>: <what>` + trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Verified facts (do not re-derive)

- `gemini-3.8-flash` exists for the provided key; plain and `with_structured_output(PydanticModel)` calls work (~1–2 s). `AIMessage.content` is a **list of content blocks** for this model; use `msg.text` for plain text.
- Functional API resume (tested with `MemorySaver`): on `Command(resume=...)` the entrypoint body re-runs from the top, plain functions execute again, completed `@task`s return cached results without running, and a second `interrupt()` later in the body pauses again. Exactly the semantics the spec assumes.
- `deepagents.create_deep_agent(model=..., backend=FilesystemBackend(root_dir=...), system_prompt=..., subagents=[SubAgent(...)])` with Gemini works: agent used `read_file` / `write_file` and wrote the requested file (4 s). `FilesystemBackend(root_dir, virtual_mode=True)` presents paths as **virtual absolute paths anchored at root_dir** (`/autoresearch/sessions/<slug>/...` maps to `<root>/autoresearch/sessions/<slug>/...`); `..` traversal is blocked. `SubAgent` is a TypedDict: `name`, `description`, optional `system_prompt`, `tools`, `model`, `mode`.
- `langgraph.json` keys accepted by CLI 0.4.31 include `python_version`, `dependencies`, `graphs`, `env`, `dockerfile_lines`. Local package: `"dependencies": ["."]` with `pyproject.toml` at `autoresearch/` (already scaffolded).
- Seed frameworks: 22 READMEs at `decomposition-frameworks/<category>/<slug>/README.md` on `origin/claude/decomposition-frameworks-66ea98`; `decomposition-frameworks/_meta/frameworks.json` on the same branch already has `slug`, `name`, `category`, `blurb` (use as `summary`), `slots`, `relations`. Read them with `git show origin/claude/decomposition-frameworks-66ea98:<path>`; do not check the branch out.
- Shortest transcript for smoke tests: `tbpn-transcripts/transcripts/2025-10-25_diet-tbpn-october-24th-2025.md` (~2,000 words). Full transcripts are ~50k words (fits Gemini's 1M context).
- Toolchain: `autoresearch/.venv` (uv, Python 3.13) already has all pinned deps. Run everything as `autoresearch/.venv/bin/python -m pytest`, `autoresearch/.venv/bin/langgraph dev`. Do not use the anaconda `langgraph` (0.3.6).

## Refinements to the spec (decided; implement these)

1. **Seed is pushed before the checkpoint-0 pause.** Order: `draft_rubric_extras` → `propose(seed)` writes `best/combination-with-explanations.md` → `commit_push("checkpoint 0 draft: seed combination")` → `interrupt(...)` → `apply_steer` (a `@task`: writes `rubric.md`, appends steer) → `commit_push("checkpoint 0: rubric approved")`. Checkpoint-0 detection stays `not exists(rubric.md)`.
2. **Step results carry content.** Agent steps return `{"path": <repo-relative>, "content": <str>}`. Before using a prior step's file, the loop calls `ws.materialize(result)` (write the cached content if the file is missing). This makes a re-invoked run after a container crash self-healing.
3. **Remote and workdir from env.** `GIT_REMOTE` (required), `AUTORESEARCH_WORKDIR` (default `/tmp/autoresearch-ws`); clone path `<workdir>/<branch with / replaced by __>`. `ensure_workspace`: clone `--single-branch --branch <branch> --depth 50` if missing, else `fetch` + `checkout -B <branch> origin/<branch>` (hard) and `git clean -fd` (attempts/ is scratch; losing it is fine because interrupts only happen between experiments).
4. **Local origin for dev.** For tests and `langgraph dev` smoke, origin is a local bare repo (`git clone --bare` of this worktree, `GIT_REMOTE=file:///...`). `scripts/new_session.py` works against `GIT_REMOTE` (clone master shallow, branch, write files, commit, push), so the same script serves local and GitHub.
5. **Push conflicts.** On rejected push: `git pull --rebase`; if the only conflict is `experiments.tsv`, resolve as union of data rows sorted by `n` (dedupe on `n`), continue rebase, push once more; any other conflict raises.
6. **Deep-agent guardrails.** `recursion_limit` per step (propose 60, decompose 150, recommend 80); a step that raises or leaves the output file missing/empty yields `kept=error` with the reason in `note`; the loop continues.
7. **Judge order record.** `score.json` includes `order: ["candidate","incumbent"]` or reversed, `judge_model`, `experiment`, per-dimension scores for both, totals, rationale.

## File map and interfaces (names later milestones rely on)

```
autoresearch/
  langgraph.json, pyproject.toml, .env.example          (done)
  engine/
    config.py        Settings from env: gemini_model, git_remote, workdir, author name/email. make_model() -> BaseChatModel
    workspace.py     Workspace(root, branch, slug): session_dir, metadata, has(rel), read(rel), write(rel, text),
                     n_experiments(), max_experiments, totals(), materialize(result), virtual(rel) -> "/autoresearch/sessions/<slug>/<rel>"
    loop.py          @entrypoint autoresearch_session({"branch"}) — plain control flow exactly as spec §3 + refinements
    review.py        @entrypoint review_proposals({"branch"})
    tasks/git_ops.py ensure_workspace(branch) -> Workspace (plain); pull(root); commit_push(root, branch, message) -> sha|None;
                     stage_allowlist(root, session_rel) ; revert_stray_changes(root, session_rel) -> list[str]; merge_experiments_tsv(ours, theirs) -> str
    tasks/log.py     LogRow model; append_row(root, session_rel, row); read_rows(...) -> list[LogRow]; digest(kind, **facts) -> dict for interrupt()
    tasks/rubric.py  CORE_DIMENSIONS (fixed list of {id,name,description,scale 1-10}); draft_extras(model, mission) -> list[dim]; render_rubric(core, extras) -> str; parse_rubric(text) -> list[dim]
    tasks/judge.py   Verdict model (per-dim scores for candidate & incumbent, totals, rationale, order); judge(model, rubric, mission, candidate, incumbent|None) -> Verdict (one repair retry)
    tasks/propose.py / decompose.py / recommend.py   run(model, ws, n, brief...) -> {"path","content"}; each builds its deep agent from prompts/<step>.md
    tasks/promote.py copy attempts/<n>/* -> best/, write best/score.json
    prompts/*.md     propose.md, decompose.md, framework_decomposer.md, recommend.md, judge.md, rubric_extras.md, review.md
    catalog/catalog.json   22 seed entries {slug,name,category,summary,when_to_use,source:"seed"}
  scripts/build_catalog.py   reads the frameworks branch via `git show`, writes engine/catalog/catalog.json
  scripts/new_session.py     <slug> --mission --transcript --max-experiments [--remote]
  tests/                     conftest with tmp bare origin + seeded repo fixture; fake chat model fixture
  dev/IMPLEMENTER.md         the implementer protocol; dev/smoke.sh  (starts langgraph dev, runs one session, resumes through interrupts)
```

Keep files small and single-purpose; split when one grows past ~300 lines.

## Milestones (pick the next unfinished piece; tick when its tests pass and it is committed)

- [x] **M1 Foundations** — `config.py`, `workspace.py`, `tasks/git_ops.py`, `tasks/log.py` with unit tests on temp bare repos: clone-or-reset, allowlist staging, stray revert, push, push-conflict union merge, tsv append/parse/n_experiments/totals.
- [x] **M2 Catalog + session bootstrap** — `scripts/build_catalog.py` (generate and commit `engine/catalog/catalog.json`, 22 entries, `when_to_use` distilled from each README's "What it decomposes" + "Failure modes"), `scripts/new_session.py` + tests (branch created from master on a temp origin, files present, tsv header, notes skeleton).
- [ ] **M3 Rubric + judge** — `tasks/rubric.py` (core dims, extras drafting via structured output, render/parse), `tasks/judge.py` (Verdict schema, randomized order recorded, repair retry, no-incumbent path) with a fake model; one `live` test each.
- [ ] **M4 Agent steps** — prompts + `propose` / `decompose` (with `framework-decomposer` subagent) / `recommend` / `promote`; unit tests use a stub agent factory; one `live` test on the short transcript that writes real `attempts/1/*`.
- [ ] **M5 Loop** — `loop.py` per spec §3 + refinements; loop test with stubbed steps and `MemorySaver`: checkpoint-0 pause, seed committed before pause, stop, continue+steer, exp-1 no incumbent, keep/discard, one commit per attempt, cap. `langgraph dev` must start and list both graphs (M6 can stub `review.py` as a minimal entrypoint until M7).
- [ ] **M6 Local end-to-end** — `dev/smoke.sh`: bare origin from this worktree, `new_session.py` on the short transcript with `max_experiments=2`, `langgraph dev --no-browser`, drive the run through the SDK (create thread, run, resume `continue` at each interrupt), assert commits landed on the bare origin and `best/score.json` exists. Real Gemini.
- [ ] **M7 Reviewer** — `review.py` per spec §5 with tests (accept new-framework → catalog entry; accept rubric-change → rubric edited + notes line; frontmatter updated; commit).
- [ ] **M8 Deploy readiness** — `langgraph build` (or `langgraph dockerfile`) succeeds locally; README in `autoresearch/` with run/deploy instructions; `langgraph deploy` smoke is owner-gated (needs GitHub PAT) — document the exact command and env instead of running it.

## Definition of done

`autoresearch/.venv/bin/python -m pytest -m "not live"` green; `dev/smoke.sh` completes two experiments against a local origin with real Gemini; `langgraph dev` serves both graphs; `langgraph build -t autoresearch:dev` succeeds; all milestones ticked; Progress log has a final entry.

## Progress log

Append one entry per implementer run (newest last): `### <date> — <milestone/piece>` then 3–8 lines: what was done, commit sha(s), test command + result, what is next, any open problem.

### 2026-09-10 — M1 Foundations (implementer #1)
- Done: `engine/config.py` (`Settings.from_env`, `load_env`, `make_model`), `engine/tasks/log.py` (`LogRow`, `parse_tsv`/`render_tsv`, `append_row`/`read_rows`, `digest`), `engine/workspace.py` (`Workspace(root, branch)`: `session_rel/session_dir/rel/path/attempt_dir/attempt_rel`, `has` = present **and non-empty**, `read/write`, `metadata/mission/transcript_path/max_experiments`, `validate()`, `rows/n_experiments/totals`, `materialize`, `virtual/virtual_repo`), `engine/tasks/git_ops.py` (`ensure_workspace`, `pull`, `stage_allowlist`, `revert_stray_changes`, `merge_experiments_tsv`, `commit_push`, `clone_path`, `GitError`). Tests: `tests/conftest.py` (hermetic git env, `origin` bare repo, `session_branch` seeded via `seed_session()`, `settings`, `fake_model`), `test_config.py`, `test_log.py`, `test_workspace.py`, `test_git_ops.py`.
- Commit: `5c4c344`.
- Test: `cd autoresearch && .venv/bin/python -m pytest -m "not live" -q` → `36 passed` (~5 s; slowest test 0.9 s).
- Interface notes for later milestones: git_ops functions are **plain**; `loop.py` should wrap them with `langgraph.func.task(...)` (verified `task(commit_push)` yields a `_TaskFunction`). Pass `str(ws.root)` and `branch` into tasks and rebuild `Workspace(root, branch)` inside. `commit_push` also calls `revert_stray_changes`; call `revert_stray_changes` yourself before `append_log` if you want strays in the row's `note`. `attempts/` is neither staged nor reverted (scratch). Rebase conflict rule: only `experiments.tsv` may conflict; union by `n`, **local row wins** on duplicate `n`; anything else → `rebase --abort` + `GitError` (local commit kept for inspection). `ensure_workspace` discards local commits/edits and runs `git clean -fd`; it also (re)sets `remote.origin.url` from `GIT_REMOTE` and local `user.name/email`.
- Next (M2): `scripts/build_catalog.py` + `engine/catalog/catalog.json`; `scripts/new_session.py` should produce exactly what `tests/conftest.py::seed_session()` produces (metadata.json, `HEADER` tsv, `notes.md` with `## Insights` / `## Human steering`, `catalog.json` = seed catalog) — consider switching the fixture to call the script once it exists.
- Open: `fake_model` fixture is a `GenericFakeChatModel` (no `with_structured_output`); M3 will likely need a small custom fake that returns a pydantic instance. No deviations from the spec.

### 2026-09-10 — M2 Catalog + session bootstrap (implementer #2)
- Done: `scripts/build_catalog.py` (`extract_section`, `first_paragraph`, `failure_mode_titles`, `distill_when_to_use`, `build_entries(meta, read_readme)`, `build_catalog(repo, ref)`, CLI `main`; reads `_meta/frameworks.json` and the 22 READMEs from the frameworks branch via `git show`, never checks it out), `engine/catalog/__init__.py` (`CATALOG_PATH`, `load_seed_catalog()`) plus the committed `engine/catalog/catalog.json` (22 entries: `slug, name, category, summary, when_to_use, source="seed"`, in `frameworks.json` order), `scripts/new_session.py` (`create_session(slug, *, mission, transcript_path, max_experiments, remote, workdir=None, base="master", catalog=None, keep_clone=False) -> {"branch","session_rel","sha","remote"}`, `SessionError`, `NOTES_SKELETON`, `redact`, CLI `main`), `scripts/__init__.py`. `tests/conftest.py::seed_session()` now delegates to `create_session` so fixtures and real sessions cannot drift. Tests: `tests/test_build_catalog.py`, `tests/test_new_session.py`.
- Commit: `da88e96`.
- Test: `cd autoresearch && .venv/bin/python -m pytest -m "not live"` → `62 passed in 14.47s`. Generator is idempotent (`.venv/bin/python -m scripts.build_catalog` twice → identical md5).
- Decision: `when_to_use` is distilled **deterministically** — first paragraph of "## What it decomposes" + the titles of the "### Failure modes" items, which come in three shapes across the 22 READMEs (bold bullets, plain bullets, a `| Failure | ... |` table; all three handled and tested). No model call, so the catalog is reproducible and tests stay offline. Entries are 78–209 words; if agents need terser text later, `build_entries(meta, read_readme)` is the seam for a model-based distiller.
- Notes: `create_session` refuses an existing remote branch, a missing/empty transcript on `base`, or an existing session folder **before** pushing; shallow-clones (`--depth 1`) into `<workdir>/new-session__<slug>` and removes the clone unless `--keep-clone`; CLI reads `GIT_REMOTE`/`AUTORESEARCH_WORKDIR` from env (`.env` loaded without override) and redacts `user:token@` from anything it prints. Both `.venv/bin/python -m scripts.new_session ...` and `.venv/bin/python scripts/new_session.py ...` work.
- Next (M3): `tasks/rubric.py` (CORE_DIMENSIONS, `draft_extras(model, mission)` via `with_structured_output`, `render_rubric`, `parse_rubric`) then `tasks/judge.py`. The `fake_model` fixture is a `GenericFakeChatModel` with no `with_structured_output`; add a small fake in `conftest.py` whose `with_structured_output(Schema)` returns a runnable that yields queued pydantic instances and can raise once (to exercise the judge's repair retry).
- Open: none; no deviations from the spec.
