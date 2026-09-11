# Autoresearch over frameworks

An autoresearch loop (after Karpathy's `autoresearch`) applied to a document instead of a training script.
The program under mutation is a combination of decomposition frameworks; the metric is a judge's rubric
score on the recommendations that combination produces for a `mission` over an input transcript. Every
attempt is committed and pushed to a session branch, which is the only memory across experiments and
containers.

- Contract: `docs/superpowers/specs/2026-09-10-autoresearch-frameworks-design.md`
- Plan and progress log: `docs/superpowers/plans/2026-09-10-autoresearch-frameworks.md`
- Implementer protocol: `dev/IMPLEMENTER.md`

Runtime: LangGraph Functional API (`@entrypoint` / `@task`), `deepagents` for the creative steps, Gemini for
every role, served by `langgraph dev` locally and LangSmith Deployment in production.

## Layout

```
autoresearch/
  langgraph.json          two graphs: autoresearch_session, review_proposals
  pyproject.toml          package `engine` (+ dev extras: langgraph-cli, langgraph-sdk, pytest)
  .env.example            every variable the engine reads; copy to .env (gitignored)
  .dockerignore           keeps .env, .venv/, scratch and tests out of the image
  engine/
    loop.py               @entrypoint autoresearch_session({"branch"})
    review.py             @entrypoint review_proposals({"branch"})
    config.py             Settings.from_env(), make_model()
    workspace.py          Workspace over the session clone
    tasks/                git_ops, log, rubric, judge, propose, decompose, recommend, promote, proposals, steps
    prompts/*.md          one prompt per step
    catalog/catalog.json  22 seed frameworks
  scripts/new_session.py  create + push a session branch
  scripts/build_catalog.py one-time catalog generation
  dev/smoke.sh            local end-to-end run with real Gemini
  tests/                  offline suite (temp git repos, fake model); `live` tests hit Gemini
```

A session lives on branch `autoresearch/<slug>` under `autoresearch/sessions/<slug>/` (spec section 2.2):
`metadata.json`, `rubric.md`, `catalog.json`, `best/`, `experiments.tsv`, `notes.md`, `proposals/`.

## Setup

Python 3.13, `uv` and `git` on PATH.

```sh
cd autoresearch
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -e ".[dev]"
cp .env.example .env      # then fill it in; .env is gitignored and never leaves this machine
```

Variables (all read from the environment; `langgraph dev` loads `.env` through `langgraph.json`):

| Name | Required | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | yes | Gemini |
| `GEMINI_MODEL` | no | model id for every role (default `gemini-3.8-flash`) |
| `GIT_REMOTE` | yes | where sessions are cloned from and pushed to; local dev: `file:///tmp/autoresearch-origin.git`, deploy: `https://x-access-token:${GITHUB_TOKEN}@github.com/ivanv33/Various-Files.git` |
| `GITHUB_TOKEN` | deploy | fine-grained PAT, `contents: write` on `ivanv33/Various-Files`; only used inside `GIT_REMOTE` |
| `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` | no | commit identity (defaults `autoresearch-bot`, `autoresearch-bot@users.noreply.github.com`) |
| `AUTORESEARCH_WORKDIR` | no | where clones live (default `/tmp/autoresearch-ws`; one subdir per branch for the loop, `<branch>--review` for the reviewer, which never shares the loop's clone) |
| `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT` | no | tracing; `LANGSMITH_API_KEY` also authenticates `langgraph deploy` |

## Run locally

1. Point `GIT_REMOTE` at a local bare origin so nothing reaches GitHub while you iterate:

   ```sh
   git clone --bare /path/to/Various-Files /tmp/autoresearch-origin.git
   # in .env: GIT_REMOTE=file:///tmp/autoresearch-origin.git
   ```

2. Create a session branch (clones `master` from `GIT_REMOTE`, writes `metadata.json`, copies the seed
   catalog, writes the `experiments.tsv` header and `notes.md` skeleton, commits, pushes):

   ```sh
   .venv/bin/python scripts/new_session.py <slug> \
     --mission "..." \
     --transcript tbpn-transcripts/transcripts/<file>.md \
     --max-experiments 3
   ```

3. Serve both graphs:

   ```sh
   .venv/bin/langgraph dev --no-browser --port 2024
   curl -s localhost:2024/ok
   ```

   `langgraph dev` writes its checkpoints to `.langgraph_api/` (gitignored). Studio opens against the same
   server if you drop `--no-browser`.

4. Drive a session through the SDK. The graph pauses (`interrupt`) at checkpoint 0 and after every new
   best; resume with `{"action": "continue" | "stop", "steer": "<optional text>"}`. Steer text is appended
   under `## Human steering` in `notes.md` and read by the next `propose`. One experiment takes several
   minutes, longer than the SDK's default 300 s read timeout, so disable it:

   ```python
   import httpx
   from langgraph_sdk import get_sync_client

   client = get_sync_client(url="http://localhost:2024",
                            timeout=httpx.Timeout(connect=10, read=None, write=60, pool=10))
   thread_id = client.threads.create()["thread_id"]
   result = client.runs.wait(thread_id, "autoresearch_session", input={"branch": "autoresearch/<slug>"})
   while isinstance(result, dict) and "__interrupt__" in result:
       for item in result["__interrupt__"]:
           print(item["value"]["kind"])          # checkpoint0 | new_best, plus rubric / verdict / trend
       result = client.runs.wait(thread_id, "autoresearch_session",
                                 command={"resume": {"action": "continue", "steer": ""}})
   print(result)   # {branch, head, attempts, kept, best_total, best_experiment, stopped}
   ```

   `stopped` is `max_experiments` or `stop`. You may edit any session file on the branch while the run is
   paused; the loop pulls before each experiment.

5. Review open proposals (`proposals/*.md` with `status: open`) on demand; it never blocks the loop:

   ```python
   client.runs.wait(client.threads.create()["thread_id"], "review_proposals",
                    input={"branch": "autoresearch/<slug>"})
   # -> {branch, head, sha, decisions: [{file, kind, status, reason}], accepted, rejected, errors, open, decided}
   ```

Commits on the session branch read `session <slug>: bootstrap`, `checkpoint 0 draft: seed combination`,
`checkpoint 0: rubric approved`, `exp <n>: KEEP|discard <candidate> vs <incumbent>`, `steer after exp <n>`,
`review: <n> proposal(s) (...)`. `attempts/` is scratch and is never committed.

### One-shot smoke

```sh
dev/smoke.sh --max-experiments 2            # real Gemini; ~11 min on the short transcript
dev/smoke.sh --help                         # --slug --mission --transcript --port --root --allow-errors
```

It clones this worktree to a bare origin under `/tmp/autoresearch-smoke`, creates the session, starts
`langgraph dev` on a temp config, drives the run to completion, and checks the origin (one commit and one
`experiments.tsv` row per experiment, `rubric.md` and `best/score.json` present, nothing from `attempts/`).
Scratch (`smoke.log`, `server.log`, `origin.git`, `ws/`) is kept for inspection and wiped on the next run.

## Tests

```sh
.venv/bin/python -m pytest -m "not live"    # offline: temp git repos, fake chat model
.venv/bin/python -m pytest -m live          # a handful of real Gemini calls; needs .env
```

## Deploy (LangSmith Deployment)

`langgraph.json` declares both graphs, Python 3.13, the local package (`dependencies: ["."]`) and a
`dockerfile_lines` entry that installs `git` (the engine clones and pushes the session branch). The
deployment supplies the checkpointer; the entrypoints do not pass one. The container is ephemeral: the
session branch is the only state, so a killed run is re-invoked with the same `{"branch"}` and resumes from
what already landed on origin.

### Image

```sh
cd autoresearch
.venv/bin/langgraph dockerfile Dockerfile        # offline; renders the Dockerfile from langgraph.json
.venv/bin/langgraph build -t autoresearch:dev    # needs a running Docker daemon (linux/amd64 image)
```

`langgraph dockerfile` is verified on every test run (`tests/test_langgraph_config.py`). The generated
Dockerfile does `ADD . /deps/autoresearch`, so `.dockerignore` excludes `.env`, `.venv/`,
`.langgraph_api/`, `tests/` and `dev/`; a local `docker build` honours only `.dockerignore`, and the CLI's
remote build archive honours `.dockerignore` plus a sibling `.gitignore` (there is none in this directory).
Do not delete `.dockerignore` or the API key would be baked into the image.

### Deployment environment

Set these as environment variables / secrets on the deployment (LangSmith UI or API), not in the image:

| Name | Value |
|---|---|
| `GOOGLE_API_KEY` | Gemini key |
| `GEMINI_MODEL` | `gemini-3.8-flash` (or the owner's choice) |
| `GITHUB_TOKEN` | fine-grained PAT, `contents: write` on `ivanv33/Various-Files` |
| `GIT_REMOTE` | `https://x-access-token:${GITHUB_TOKEN}@github.com/ivanv33/Various-Files.git` (expand the token; the engine does not interpolate) |
| `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` | commit identity |
| `LANGSMITH_TRACING`, `LANGSMITH_PROJECT` | optional tracing (the platform injects its own API key) |

### Deploy command (owner-gated: needs the GitHub PAT above and a LangSmith API key)

```sh
cd autoresearch
.venv/bin/langgraph deploy --name autoresearch-frameworks --deployment-type dev
```

`--api-key` is read from `LANGSMITH_API_KEY` in `.env`. Without a local Docker daemon the CLI builds
remotely by default (`--remote`); with one, `--image autoresearch:dev` reuses the image built above. Then
run the deploy smoke from spec section 8: point the SDK snippet at the deployment URL
(`get_sync_client(url=<deployment url>, api_key=<LANGSMITH_API_KEY>)`), create a session with
`scripts/new_session.py` against the GitHub `GIT_REMOTE`, run one experiment, and confirm the `exp 1:` commit
landed on `origin/autoresearch/<slug>` and the trace shows one span per task.

## Operational notes

- `langgraph dev` applies the config's `env` over the inherited environment, so an exported `GIT_REMOTE`
  loses to the `.env` file; `dev/smoke.sh` therefore serves a temp config whose `env` is an inline mapping.
- Judge noise is comparable to the margins being decided (spec 4.2 re-grades the incumbent every experiment;
  observed swing of 7 points on the same document). Read `experiments.tsv` and `best/score.json` together.
- Timings on the 2,002-word transcript: checkpoint 0 about 1 min, experiment 1 about 3.5 min (seed, no
  propose), later experiments 6-7 min.
- Deep-agent nodes show up as `langgraph_node=model|tools` in the server log, not under the loop's task names;
  the LangSmith trace has one span per `@task`.
