---
name: mission-lab
description: Use when the owner says "start a mission lab", "run autoresearch on <transcript> toward <mission>", or asks for mission-lab status, resume, steer, or stop; the autoresearch loop served by a local langgraph dev server and watched in LangSmith Studio.
---

# Mission Lab

A playbook, not a script. The agent settles the fuzzy inputs; `git`, `langgraph dev` and `curl` against the local LangGraph API (`http://127.0.0.1:2024`) do the deterministic work. Run every command from the repo root (the checkout holding `autoresearch/` and `tbpn-transcripts/`). Engine contract: `autoresearch/README.md`.

## 1. Gather (main agent; one round of questions at most, never guess)

| Input | Rule |
|---|---|
| transcript | repo-relative path; corpus `tbpn-transcripts/transcripts/`. Fuzzy description: `ls tbpn-transcripts/transcripts \| grep -i <hint>`; one hit, name it; several, ask |
| mission | the owner's words, 1-3 sentences: what the recommendations should move toward |
| max_experiments | default 10 |
| base ref | default `master`; the current branch or any ref is fine. It must hold the transcript, not the engine (the engine runs from this checkout; `master` has no `autoresearch/`) |
| slug | `[a-z0-9]+(-[a-z0-9]+)*`, from the transcript date/topic (`2025-10-25_diet-tbpn-...` gives `diet-tbpn-oct24`) unless given |

## 2. Delegate the start

Dispatch one general-purpose subagent with this brief (fill the `<...>`, keep the rest verbatim) so the main context receives only its result.

```text
Start an autoresearch session. Work only inside <repo root>, plus /tmp/mission-lab for the server log (the engine clones under /tmp/autoresearch-ws on its own). Use absolute paths: your cwd resets between commands. Never print secrets (redact any token you quote), never `cat` .env, no bare `git stash`. If a step fails, stop and report exactly what failed; no fallbacks.
Inputs: transcript=<path> mission='<text>' max_experiments=<n> base=<ref> slug=<slug>

1. Preconditions. `grep -c '^NAME=.' autoresearch/.env` must be 1 for GOOGLE_API_KEY, LANGSMITH_API_KEY, GIT_REMOTE, and LANGSMITH_TRACING must be `true`. `langgraph dev` runs as the owner, so a tokenless GIT_REMOTE works through the git credential helper: if it is empty, set it to `git remote get-url origin` with `sed -i '' "s#^GIT_REMOTE=.*#GIT_REMOTE=$URL#" autoresearch/.env` and say so in one line. Verify `git ls-remote "$URL" HEAD`.
2. Branch + skeleton in the owner's checkout. `git status --porcelain --untracked-files=no` must be empty; otherwise stop.
   SLUG=<slug>; BASE=<ref>; S=autoresearch/sessions/$SLUG; PREV=$(git branch --show-current)
   git fetch -q origin; git ls-remote --exit-code --heads origin autoresearch/$SLUG && { echo "branch exists on origin"; exit 1; }
   mkdir -p /tmp/mission-lab && cp autoresearch/engine/catalog/catalog.json /tmp/mission-lab/catalog.json   # seed catalog from this checkout's engine: BASE may not carry autoresearch/
   git checkout -b autoresearch/$SLUG $BASE          # BASE = origin/<name> when the ref lives on origin (what new_session.py clones), else the local ref
   test -s '<transcript>' || { echo "transcript missing on $BASE"; exit 1; }; test -e "$S" && { echo "$S already exists"; exit 1; }; mkdir -p "$S"
   jq -n --arg m '<mission>' --arg t '<transcript>' --argjson n <n> '{mission:$m,transcript_path:$t,max_experiments:$n}' > "$S/metadata.json"
   printf 'n\ttimestamp\tframeworks\tcandidate_total\tincumbent_total\tkept\tnote\n' > "$S/experiments.tsv"
   printf '# Notes\n\n## Insights\n\n## Human steering\n' > "$S/notes.md"
   cp /tmp/mission-lab/catalog.json "$S/catalog.json"
   git add -A -- "$S" && git commit -q -m "session $SLUG: bootstrap" && git push -u origin autoresearch/$SLUG; git checkout -q "$PREV"
   (Escape a literal ' in the mission as '\''. A Co-Authored-By trailer as a second -m is fine; keep the subject verbatim. The push doubles as the credential check: the server pushes as the same user.)
3. Server. If `curl -sf http://127.0.0.1:2024/ok` fails: `mkdir -p /tmp/mission-lab; cd autoresearch && nohup .venv/bin/langgraph dev --no-browser --no-reload --port 2024 > /tmp/mission-lab/dev.log 2>&1 & echo $! > /tmp/mission-lab/dev.pid` (`--no-reload`: a .py edit must not restart the server under a paused run), poll `/ok` every 2 s for up to 60 s, then confirm `curl -sf -X POST http://127.0.0.1:2024/assistants/search -H 'content-type: application/json' -d '{}' | jq -r '.[].graph_id'` lists autoresearch_session.
4. Thread + run; do not wait for the run.
   TID=$(curl -sf -X POST http://127.0.0.1:2024/threads -H 'content-type: application/json' -d "{\"metadata\":{\"branch\":\"autoresearch/$SLUG\"}}" | jq -r .thread_id)
   curl -sf -X POST http://127.0.0.1:2024/threads/$TID/runs -H 'content-type: application/json' -d "{\"assistant_id\":\"autoresearch_session\",\"input\":{\"branch\":\"autoresearch/$SLUG\"}}" | jq -r .status
5. Return, verbatim: thread_id; branch https://github.com/ivanv33/Various-Files/tree/autoresearch/$SLUG/autoresearch/sessions/$SLUG; Studio thread https://smith.langchain.com/studio/thread/$TID?baseUrl=http://127.0.0.1:2024; Studio root https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024; LANGSMITH_PROJECT from .env; whether the server was already up or started by you (pid); the one-line GIT_REMOTE note if you set it.
```

## 3. Report

Hand the owner the links and thread_id verbatim, then two lines on steering:
- Studio: open the thread link; at each pause (checkpoint 0 after 1-2 min, then every new best) resume with `{"action":"continue","steer":"<optional text>"}` or `{"action":"stop"}`. Steer text lands under `## Human steering` in `notes.md` and the next `propose` reads it.
- curl: `curl -s -X POST http://127.0.0.1:2024/threads/<id>/runs -H 'content-type: application/json' -d '{"assistant_id":"autoresearch_session","command":{"resume":{"action":"continue","steer":""}}}'`

## 4. Other requests

- find the thread: `curl -s -X POST http://127.0.0.1:2024/threads/search -H 'content-type: application/json' -d '{"metadata":{"branch":"autoresearch/<slug>"}}' | jq -r '.[].thread_id'`
- status: `curl -s http://127.0.0.1:2024/threads/<id> | jq -r .status` gives `interrupted` (paused), `busy` (running), `idle` (finished) or `error`; read the thread, a run object says `success` for a paused run. Pause details: `curl -s http://127.0.0.1:2024/threads/<id>/state | jq '{next, interrupts: [.tasks[].interrupts[].value | {kind, n, sha, seed: .seed.frameworks, verdict}]}'` (`n`, `verdict` are null at checkpoint 0). Then `git fetch -q origin && git show origin/autoresearch/<slug>:autoresearch/sessions/<slug>/experiments.tsv | tail -3`.
- resume / steer / stop: the curl in section 3 with `continue` + steer text, or `stop`.
- stop server: `kill $(cat /tmp/mission-lab/dev.pid)` (or `pkill -f "langgraph dev"`).
- server died mid-pause: the dev checkpointer is in-memory (pickled under `autoresearch/.langgraph_api/` and reloaded on boot; do not rely on it). Restart it (step 3) and start a new run for the same branch (step 4): the branch holds every committed state and the loop resumes from it.
- `429 Monthly unique traces usage limit exceeded` in `dev.log` is LangSmith tracing only; the run and Studio's thread view (it reads the local server) are unaffected.

## 5. TODO: `langgraph up` runtime (Docker; not implemented, not live-tested)

Known so far. `cd autoresearch && .venv/bin/langgraph up --port 8123 --wait` builds the image and starts the API with Postgres and Redis containers: the checkpointer is durable, so a paused run survives a restart, and a rebuilt image is needed after code changes (`langgraph up` again, or `--watch`). Pushes happen inside the container, where the owner's credential helper does not reach, so `GIT_REMOTE` in `.env` must carry a token: `https://x-access-token:<GITHUB_TOKEN>@github.com/ivanv33/Various-Files.git` (expanded; the engine does not interpolate, and it strips the token before it touches any clone). Everything else in this playbook stays the same with `2024` replaced by `8123`, including the Studio `baseUrl`. There is no `langgraph down`: stop it with `docker compose down` on the project `langgraph up` created (`docker compose ls` shows the name). Verify every claim here live before ticking plan milestone M10.
