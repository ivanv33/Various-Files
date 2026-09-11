# Autoresearch over Frameworks — Design

Date: 2026-09-10
Status: approved by owner, awaiting implementation plan

## 1. Purpose

An autoresearch loop (after Karpathy's `autoresearch`) applied to a document rather than a training script.

- The **program under mutation** is a combination of mental/decomposition frameworks, written as `combination-with-explanations.md`.
- The **metric** is a judge's rubric score on `recommendations.md`: concrete steps toward a `mission`, derived from decomposing the input document with that combination.
- Keep the combination if its recommendations out-score the incumbent; otherwise discard. Log every attempt.

A **session** is one `(mission, input document)` pair and lives on its own git branch. The branch HEAD is the complete memory of every agent that touches the session. Each experiment runs in fresh model context; the runtime container is ephemeral and may die at any time without losing work.

Runtime: LangGraph Functional API (`@entrypoint` / `@task`), deployed to LangSmith Deployment via `langgraph deploy`. Models: Gemini (owner-supplied model id, one model for all roles in v1). Creative steps use LangChain `deepagents`; the judge is a plain structured-output call.

## 2. Repository layout

All paths are inside the `Various-Files` repo.

### 2.1 Engine (on `master`)

```
autoresearch/
  langgraph.json
  pyproject.toml
  engine/
    loop.py                # @entrypoint autoresearch_session
    review.py              # @entrypoint review_proposals
    tasks/
      git_ops.py           # ensure_workspace, pull, commit_push, staging allowlist
      propose.py           # deep agent
      decompose.py         # deep agent (+ framework-decomposer subagent)
      recommend.py         # deep agent
      judge.py             # structured-output call
      log.py               # experiments.tsv read/append, digest builder
      rubric.py            # core rubric, extras drafting, merge
    prompts/               # one markdown file per step
    catalog/catalog.json   # seed catalog: 22 frameworks
  scripts/
    build_catalog.py       # one-time: decomposition-frameworks/*/README.md -> catalog.json
    new_session.py         # creates a session branch + folder, pushes
  tests/
```

`catalog.json` is generated once from the 22 READMEs on branch `claude/decomposition-frameworks-66ea98` and committed to the engine. Sessions do not depend on that branch. Each entry: `slug`, `name`, `summary`, `when_to_use`, `source: seed`.

### 2.2 Session (branch `autoresearch/<slug>`, created from `master`)

Folder `autoresearch/sessions/<slug>/`:

| Path | Written by | Purpose |
|---|---|---|
| `metadata.json` | `new_session.py` | `{ "mission": str, "transcript_path": str, "max_experiments": int }`. `transcript_path` is repo-relative (e.g. `tbpn-transcripts/<file>`). These are the only knobs. |
| `rubric.md` | engine at checkpoint 0 | Core dimensions (fixed in engine) plus 1–3 mission-specific extras drafted by the model and approved by the owner. Frozen except via the reviewer. |
| `catalog.json` | `new_session.py`, reviewer | Copy of the seed catalog plus accepted additions (`source: proposal:<file>`). Session-local. |
| `best/combination-with-explanations.md` | promote | Current best program. |
| `best/decomposition.md` | promote | Decomposition produced by the best program. |
| `best/recommendations.md` | promote | The judged artifact. |
| `best/score.json` | promote | Per-dimension scores, total, experiment id, judge model, order used. |
| `experiments.tsv` | engine, every attempt | Columns: `n`, `timestamp`, `frameworks` (slugs, `+`-joined), `candidate_total`, `incumbent_total`, `kept` (`1`/`0`/`error`), `note` (one line). |
| `notes.md` | agents (insights), engine (steering) | Agent-maintained "## Insights" section, bounded (agent prunes to a fixed line budget); engine-appended "## Human steering" entries with timestamps. |
| `proposals/*.md` | propose agent | `new-framework-<slug>.md` or `rubric-change-<slug>.md`; frontmatter `status: open|accepted|rejected`, `experiment: n`. Never blocks the loop. |

`attempts/<n>/` is scratch inside the clone and is never committed.

Commit policy (autoresearch-style, improvements only + full log): every attempt commits `experiments.tsv`, `notes.md`, and any new or changed `proposals/*.md`. `best/` changes only when an attempt is kept. Every commit is pushed immediately because the container is ephemeral.

## 3. Control flow — `loop.py`

One `@entrypoint autoresearch_session(inputs: {"branch": str})`. Plain Python control flow; every step below marked *task* is a `@task`.

```
ws = ensure_workspace(branch)                        # plain function, idempotent clone-or-pull
if not ws.has("rubric.md"):                          # checkpoint 0
    extras = draft_rubric_extras(ws)                 # task, plain call
    seed   = propose(ws, seed=True)                  # task, deep agent -> best/combination-with-explanations.md
    reply  = interrupt(digest(kind="checkpoint0", rubric=core+extras, seed=seed))
    if reply.action == "stop": return summary(ws)
    apply_steer(ws, reply)                           # writes rubric.md, appends steer to notes.md
    commit_push(ws, "checkpoint 0: rubric + seed")   # task; seed lands on origin before any pause
while ws.n_experiments() < ws.max_experiments:
    pull(ws)                                         # task: pick up owner edits / reviewer merges
    n       = ws.n_experiments() + 1
    combo   = (use_seed(ws, n) if n == 1             # experiment 1 evaluates the committed seed
               else propose(ws, n))                  # task, deep agent -> attempts/n/combination-with-explanations.md
    decomp  = decompose(ws, n, combo)                # task, deep agent -> attempts/n/decomposition.md
    recs    = recommend(ws, n, decomp)               # task, deep agent -> attempts/n/recommendations.md
    verdict = judge(ws, n, recs)                     # task, structured-output call
    kept    = verdict.candidate_total > verdict.incumbent_total   # strict
    if kept: promote(ws, n, verdict)                 # attempts/n/* -> best/, write score.json
    append_log(ws, n, combo, verdict, kept)
    commit_push(ws, f"exp {n}: {'KEEP' if kept else 'discard'} {candidate_total} vs {incumbent_total}")
    if kept:
        reply = interrupt(digest(kind="new_best", n=n, verdict=verdict, trend=ws.totals()))
        if reply.action == "stop": break
        apply_steer(ws, reply); commit_push(ws, f"steer after exp {n}")
return summary(ws)
```

Resume payload: `{"action": "continue" | "stop", "steer": "<free text, optional>"}`. Steer text is appended under `## Human steering` in `notes.md` with a timestamp; the next `propose` reads it. The owner may also edit any session file in the branch before resuming; `pull` picks it up. If the owner edits `best/` by hand, no special handling is needed: the judge grades the incumbent afresh every experiment.

Pauses in v1: checkpoint 0 and each new best. No every-K pause, no plateau pause; the owner interrupts in the LangSmith UI when needed.

Termination: `max_experiments` reached, or `action: stop` at a pause. The summary returns the best score, kept count, attempt count, and the branch HEAD sha.

Seed experiment: at checkpoint 0 the seed combination is written to `best/combination-with-explanations.md` and committed (no decomposition, recommendations, or score yet), so it survives a container restart during the pause. Experiment 1 skips `propose`, copies the seed into `attempts/1/`, and runs decompose → recommend → judge with no incumbent; `incumbent_total` is recorded as empty and `kept = 1`. `promote` then fills the rest of `best/`.

`ws.n_experiments()` is the number of data rows in `experiments.tsv`.

## 4. Agents

### 4.1 Deep agents: propose, decompose, recommend

- Constructed per step with `create_deep_agent(model=<GEMINI_MODEL>, backend=FilesystemBackend(root_dir=<clone root>), system_prompt=<prompts/<step>.md>, subagents=...)`. No thread id: fresh context every step.
- Each receives a short brief: mission, session folder path, transcript path, rubric path, and the instruction to read `experiments.tsv` (tail) and `notes.md` before acting. Everything else it reads with its file tools.
- `propose`: chooses the next combination given catalog, log, notes, and the current best. Must not repeat a `frameworks` set already in the log unless the explanation materially differs, and must say why in `note`. May write `proposals/new-framework-*.md` or `proposals/rubric-change-*.md`. Writes `attempts/n/combination-with-explanations.md` and updates the `## Insights` section of `notes.md` within its line budget.
- `decompose`: applies the combination to the transcript. Given a `framework-decomposer` subagent spec so it can fan out one subagent per framework and merge. Writes `attempts/n/decomposition.md`.
- `recommend`: turns the decomposition into concrete steps toward the mission. Writes `attempts/n/recommendations.md`.
- Output contract: each step returns the path it wrote; the loop verifies the file exists and is non-empty, otherwise the attempt is logged as `error`.

### 4.2 Judge

One structured-output call per experiment. Input: rubric, mission, candidate `recommendations.md`, incumbent `best/recommendations.md` (absent on experiment 1). Order of candidate/incumbent is randomized per call and recorded in `score.json`. Output schema: per-dimension integer scores for both documents, totals, one-paragraph rationale. Grading the incumbent alongside the candidate every time controls score drift across calls.

### 4.3 Write discipline

Agents may write anywhere in the clone, but `commit_push` stages only paths inside the session folder from this allowlist: `experiments.tsv`, `notes.md`, `proposals/`, `best/`, `rubric.md`, `catalog.json`. `attempts/` is never staged; `promote` copies from it into `best/`. Any other change is reverted (`git checkout -- <path>`, untracked files removed) and mentioned in the log row's `note`. Agents never run git.

### 4.4 Context limits

Each step is a fresh agent, so nothing accumulates across experiments. Within a step, `deepagents`' summarization middleware plus Gemini's long context handle a full transcript. The compressed memory that crosses experiments is `experiments.tsv` (one line per attempt) and the bounded `## Insights` section of `notes.md`.

## 5. Reviewer — `review.py`

Second graph, `@entrypoint review_proposals(inputs: {"branch": str})`, run on demand from Studio or the API.

- `ensure_workspace(branch)`, read `proposals/*.md` with `status: open`.
- One structured-output call per proposal: `accept | reject` plus reason, given mission, rubric, catalog, and the log.
- Accept `new-framework`: append an entry to session `catalog.json` with `source: proposal:<file>`.
- Accept `rubric-change`: edit `rubric.md` and append a timestamped line under `## Rubric changes` in `notes.md` naming the proposal file. No row is added to `experiments.tsv` (rows are experiments only). Scores before and after are not comparable; the judge's fresh incumbent grading absorbs this.
- Write decision and reason into the proposal's frontmatter (`status`, `decision_reason`), commit, push.

The main loop never blocks on proposals.

## 6. Deployment

`autoresearch/langgraph.json`:

```json
{
  "dependencies": ["./engine"],
  "graphs": {
    "autoresearch_session": "./engine/loop.py:autoresearch_session",
    "review_proposals": "./engine/review.py:review_proposals"
  },
  "env": ".env",
  "dockerfile_lines": ["RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*"]
}
```

Environment / secrets on the deployment:

| Name | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Gemini |
| `GEMINI_MODEL` | model id, owner-supplied |
| `GITHUB_TOKEN` | fine-grained PAT, `contents: write` on `ivanv33/Various-Files` |
| `GIT_REMOTE` | `https://x-access-token:${GITHUB_TOKEN}@github.com/ivanv33/Various-Files.git` |
| `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` | commit identity |

LangSmith Deployment supplies the checkpointer; the entrypoints do not pass one. Local development uses `langgraph dev` with the same env in `.env`.

Session start (manual): `python scripts/new_session.py <slug> --mission "..." --transcript tbpn-transcripts/<file> --max-experiments N` creates `autoresearch/<slug>` from `master`, writes `metadata.json`, copies the seed catalog, writes an empty `experiments.tsv` header and `notes.md` skeleton, commits, pushes. Then invoke `autoresearch_session` with `{"branch": "autoresearch/<slug>"}`.

## 7. Error handling

- **Resume semantics.** On resume after `interrupt()`, the entrypoint re-executes from the top; completed `@task`s return cached results without running. Therefore `ensure_workspace` is a plain function (it must actually re-create the clone), and every side-effecting step (`commit_push`, `promote`, `append_log`, agent steps) is a `@task` so it is not repeated.
- **Push rejected** (someone pushed to the branch mid-run): `git pull --rebase`, retry once. Conflicts in `experiments.tsv` are resolved by union of rows (append-only, sorted by `n`). Any other conflict fails the run loudly; state up to the previous attempt is already on origin.
- **Malformed judge output**: one repair retry with the validation error; then log the attempt as `kept = error` and continue.
- **Agent step fails** (recursion limit, timeout, missing output file): log as `kept = error` with the reason, continue.
- **Missing transcript / bad metadata**: fail before checkpoint 0 with a clear message.

## 8. Testing

- Unit (pure Python, temp git repos, no model): `experiments.tsv` append/parse/union-merge, `promote`, staging allowlist and revert, judge output parsing and order randomization record, rubric core+extras merge, `new_session.py` output.
- Loop test with stubbed tasks and a fake chat model: keep and discard paths, experiment-1 no-incumbent path, `interrupt` and resume with steer text, `stop` at a pause, one commit per attempt, cap termination.
- Live smoke: `langgraph dev`, short transcript, `max_experiments = 2`, real Gemini.
- Deploy smoke: `langgraph deploy`, one experiment, verify the commit landed on origin and the trace shows one span per task.

## 9. Not in v1 (design keeps it possible)

- Parallel N candidates per iteration: N `propose → decompose → recommend` futures, then a tournament judge. The step boundaries already allow this.
- Islands with periodic exchange.
- Cross-session shared catalog.
- Push-triggered session start (GitHub Action → LangSmith API).
- Plateau or every-K pauses.
- Different models per role.

## 10. Local start skill (`/mission-lab`) — owner-requested 2026-09-11

A Claude Code project skill, `.claude/skills/mission-lab/SKILL.md`, starts and steers a session without a new
script. The agent settles the fuzzy inputs with the owner (which transcript, mission wording, slug, base ref,
steering text) and delegates the start to a subagent; the deterministic steps are existing commands: `git`
writes and pushes the §2.2 skeleton (byte-identical to `new_session.py`'s), `langgraph dev` serves the graphs on
port 2024, `curl` creates the thread and run and resumes it with the §3 payload. Watching and steering happen in
LangSmith Studio through `?baseUrl=http://127.0.0.1:2024`. A new case (another base branch, another corpus) is
a wording change in the playbook, never a code change. Docker `langgraph up` (port 8123, durable checkpointer,
token inside `GIT_REMOTE` because pushes run in the container) is a TODO in the skill and plan milestone M10.
