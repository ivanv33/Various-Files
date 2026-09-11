"""Local end-to-end smoke (plan M6): real Gemini, `langgraph dev`, a bare origin cloned from this worktree.

    dev/smoke.sh [--max-experiments 2] [--slug smoke] [--port 2024] [--root /tmp/autoresearch-smoke] [--allow-errors]

1. Load `autoresearch/.env` into this process (API key, model, LangSmith tracing) -- secrets stay in the
   process environment and are inherited by the server; they are never written to disk by this script.
2. `git clone --bare` this worktree to `<root>/origin.git`; create the session branch there with
   `scripts/new_session.py` (short transcript, `max_experiments` small).
3. Start `langgraph dev --no-browser --no-reload --config <root>/langgraph.json`. The temp config is the real
   `langgraph.json` with `env` replaced by the mapping `{GIT_REMOTE, AUTORESEARCH_WORKDIR}`: `langgraph dev`
   applies the config's env *over* the inherited environment (`patch_environment` sets unconditionally), so an
   exported `GIT_REMOTE` would lose to the `.env` file the real config points at. `dependencies: ["."]` is
   resolved against the server's cwd, which is `autoresearch/`.
4. Drive `autoresearch_session` through the SDK: create a thread, run, resume `{"action": "continue"}` at every
   interrupt (checkpoint 0, each new best) until the summary comes back.
5. Verify the bare origin: one `exp n:` commit and one tsv row per experiment, no error rows unless
   `--allow-errors`, `rubric.md` and `best/score.json` on the branch, nothing from `attempts/`.

The scratch root is wiped at the start of every run and kept afterwards for inspection (`smoke.log`,
`server.log`, the bare origin, the engine's clone under `ws/`). The server is always killed on exit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from engine.config import load_env
from engine.tasks.git_ops import git
from engine.tasks.log import LogRow, parse_tsv

AUTORESEARCH_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = AUTORESEARCH_DIR.parent
ASSISTANT = "autoresearch_session"
DEFAULT_ROOT = "/tmp/autoresearch-smoke"
DEFAULT_SLUG = "smoke"
DEFAULT_TRANSCRIPT = "tbpn-transcripts/transcripts/2025-10-25_diet-tbpn-october-24th-2025.md"
DEFAULT_MISSION = (
    "Give an early-stage founder concrete, non-obvious next steps for the coming quarter, grounded in what this "
    "episode reveals about where money, talent and attention in tech are moving."
)
SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD")
_EXP_SUBJECT = re.compile(r"^exp (\d+): ")

Log = Callable[[str], None]


class SmokeError(RuntimeError):
    """The smoke could not run, or the origin does not show what a healthy session leaves behind."""


# --- pure helpers ---------------------------------------------------------------


def smoke_config(base: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    """The real `langgraph.json` with `env` replaced by an inline mapping (no secrets allowed in it).

    The dev server still writes its checkpoints to `autoresearch/.langgraph_api/` (gitignored): CLI 0.4.31
    drops a `disable_persistence` key in `validate_config`, so there is no way to turn that off from here.
    """
    secrets = [k for k in env if any(marker in k.upper() for marker in SECRET_MARKERS)]
    if secrets:
        raise SmokeError(f"refusing to write secrets into the temp langgraph.json: {', '.join(sorted(secrets))}")
    return {**base, "env": dict(env)}


def describe_interrupt(value: Any) -> str:
    if not isinstance(value, dict):
        return repr(value)[:200]
    kind = value.get("kind")
    if kind == "checkpoint0":
        seed = value.get("seed") or {}
        return f"checkpoint0 seed={'+'.join(seed.get('frameworks', []))} sha={value.get('sha')}"
    if kind == "new_best":
        verdict = value.get("verdict") or {}
        return (
            f"new_best n={value.get('n')} {verdict.get('candidate_total')} vs {verdict.get('incumbent_total')} "
            f"sha={value.get('sha')}"
        )
    return f"{kind}"


def drive(client: Any, branch: str, *, max_resumes: int = 10, log: Log = print) -> tuple[dict[str, Any], list[Any]]:
    """Run `autoresearch_session` on a fresh thread, resuming `continue` at each interrupt; `(summary, interrupts)`."""
    thread_id = client.threads.create()["thread_id"]
    log(f"thread {thread_id}: run {ASSISTANT} on {branch}")
    started = time.monotonic()
    result = client.runs.wait(thread_id, ASSISTANT, input={"branch": branch})
    interrupts: list[Any] = []
    resumes = 0
    while isinstance(result, dict) and "__interrupt__" in result:
        for item in result["__interrupt__"]:
            value = item.get("value", item) if isinstance(item, dict) else item
            interrupts.append(value)
            log(f"[{_elapsed(started)}] interrupt {len(interrupts)}: {describe_interrupt(value)}")
        if resumes >= max_resumes:
            raise SmokeError(f"still interrupted after {max_resumes} resumes; giving up")
        resumes += 1
        log(f"[{_elapsed(started)}] resume {resumes}: continue")
        result = client.runs.wait(thread_id, ASSISTANT, command={"resume": {"action": "continue"}})
    log(f"[{_elapsed(started)}] finished: {json.dumps(result, default=str)}")
    return result, interrupts


def check_origin(
    bare: Path | str, branch: str, session_rel: str, expected_experiments: int, *, allow_errors: bool = False
) -> dict[str, Any]:
    """What a healthy session leaves on origin; raises `SmokeError` on the first missing piece."""
    subjects = git(bare, "log", "--reverse", "--format=%s", branch).splitlines()
    exp_subjects = [s for s in subjects if _EXP_SUBJECT.match(s)]
    checkpoint_subjects = [s for s in subjects if s.startswith("checkpoint 0")]
    if len(exp_subjects) != expected_experiments:
        raise SmokeError(
            f"expected {expected_experiments} 'exp n:' commits on {branch}, found {len(exp_subjects)}: {exp_subjects}"
        )
    tree = git(bare, "ls-tree", "-r", "--name-only", branch, "--", session_rel).splitlines()
    files = sorted(p.removeprefix(session_rel + "/") for p in tree)
    strays = [f for f in files if f.startswith("attempts/")]
    if strays:
        raise SmokeError(f"scratch files were committed: {strays}")
    rows: list[LogRow] = parse_tsv(git(bare, "show", f"{branch}:{session_rel}/experiments.tsv"))
    if len(rows) != expected_experiments:
        raise SmokeError(f"expected {expected_experiments} rows in experiments.tsv, found {len(rows)}")
    errors = [r for r in rows if r.kept == "error"]
    if errors and not allow_errors:
        raise SmokeError("error rows in experiments.tsv: " + "; ".join(f"{r.n}: {r.note}" for r in errors))
    for name in ("rubric.md", "best/score.json"):
        if name not in files:
            raise SmokeError(f"{name} is not on {branch}")
    score = json.loads(git(bare, "show", f"{branch}:{session_rel}/best/score.json"))
    return {
        "head": git(bare, "rev-parse", branch),
        "subjects": subjects,
        "exp_subjects": exp_subjects,
        "checkpoint_subjects": checkpoint_subjects,
        "rows": rows,
        "score": score,
        "files": files,
    }


# --- server -------------------------------------------------------------------------


def _elapsed(started: float) -> str:
    return f"{time.monotonic() - started:6.0f}s"


def _http(url: str, payload: dict[str, Any] | None = None, timeout: float = 5.0) -> Any:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"content-type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read() or b"null")


def start_server(config_path: Path, port: int, server_log: Path) -> subprocess.Popen:
    exe = Path(sys.executable).parent / "langgraph"
    cmd = [str(exe), "dev", "--no-browser", "--no-reload", "--port", str(port), "--config", str(config_path)]
    return subprocess.Popen(
        cmd,
        cwd=AUTORESEARCH_DIR,
        stdout=server_log.open("ab"),
        stderr=subprocess.STDOUT,
        start_new_session=True,  # its own process group, so stop_server can take down every child too
    )


def wait_for_server(server: subprocess.Popen, url: str, server_log: Path, timeout: float, log: Log) -> list[str]:
    """Poll `/ok` until the server answers; return the graph ids it serves."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise SmokeError(f"langgraph dev exited with {server.returncode} during boot\n{tail(server_log)}")
        try:
            if _http(f"{url}/ok").get("ok"):
                break
        except (urllib.error.URLError, OSError, ValueError):
            pass
        time.sleep(1.0)
    else:
        raise SmokeError(f"langgraph dev did not answer /ok within {timeout:.0f}s\n{tail(server_log)}")
    graphs = sorted({a["graph_id"] for a in _http(f"{url}/assistants/search", {})})
    log(f"server up at {url}; graphs: {graphs}")
    if ASSISTANT not in graphs:
        raise SmokeError(f"{ASSISTANT} is not served; graphs: {graphs}")
    return graphs


def stop_server(server: subprocess.Popen | None, log: Log) -> None:
    if server is None or server.poll() is not None:
        return
    for sig, grace in ((signal.SIGTERM, 15.0), (signal.SIGKILL, 5.0)):
        try:
            os.killpg(server.pid, sig)
        except ProcessLookupError:
            return
        try:
            server.wait(timeout=grace)
            log(f"server stopped ({sig.name})")
            return
        except subprocess.TimeoutExpired:
            continue


def tail(path: Path, lines: int = 40) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(text[-lines:])


# --- main -------------------------------------------------------------------------------


def _make_log(path: Path) -> Log:
    def log(line: str) -> None:
        stamped = f"{time.strftime('%H:%M:%S')} {line}"
        print(stamped, flush=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(stamped + "\n")

    return log


def report(summary: dict[str, Any], interrupts: list[Any], facts: dict[str, Any], root: Path, log: Log) -> None:
    log("--- smoke OK ---")
    log(f"summary: {json.dumps(summary, default=str)}")
    log(f"interrupts: {[describe_interrupt(v) for v in interrupts]}")
    log(f"origin head: {facts['head']}")
    for s in facts["subjects"]:
        log(f"  commit: {s}")
    for r in facts["rows"]:
        log(f"  row: {r.to_tsv_line()}")
    score = facts["score"]
    log(
        f"best/score.json: experiment={score.get('experiment')} candidate_total={score.get('candidate_total')} "
        f"incumbent_total={score.get('incumbent_total')} order={score.get('order')} judge_model={score.get('judge_model')}"
    )
    log(f"session files on branch: {facts['files']}")
    log(f"scratch kept at {root} (server.log, smoke.log, origin.git, ws/)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--slug", default=DEFAULT_SLUG, help=f"session slug (default {DEFAULT_SLUG})")
    parser.add_argument("--mission", default=DEFAULT_MISSION)
    parser.add_argument("--transcript", default=DEFAULT_TRANSCRIPT, help="repo-relative path on master")
    parser.add_argument("--max-experiments", type=int, default=2)
    parser.add_argument("--port", type=int, default=2024)
    parser.add_argument("--root", default=DEFAULT_ROOT, help=f"scratch root, wiped on start (default {DEFAULT_ROOT})")
    parser.add_argument("--allow-errors", action="store_true", help="pass even if some rows are kept=error")
    parser.add_argument("--max-resumes", type=int, default=10)
    parser.add_argument("--boot-timeout", type=float, default=120.0, help="seconds to wait for langgraph dev")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    log = _make_log(root / "smoke.log")
    server_log = root / "server.log"
    url = f"http://127.0.0.1:{args.port}"
    server: subprocess.Popen | None = None

    def on_sigterm(*_: Any) -> None:
        raise KeyboardInterrupt  # unwinds through `finally`, so a killed driver still stops the server

    signal.signal(signal.SIGTERM, on_sigterm)

    try:
        load_env()
        if not os.environ.get("GOOGLE_API_KEY"):
            raise SmokeError("GOOGLE_API_KEY is not set (expected in autoresearch/.env)")
        log(f"model: {os.environ.get('GEMINI_MODEL', '(default)')}; tracing: {os.environ.get('LANGSMITH_TRACING', 'off')}")

        origin = root / "origin.git"
        git(root, "clone", "-q", "--bare", str(REPO_ROOT), str(origin))
        remote = origin.as_uri()
        workdir = root / "ws"
        log(f"bare origin {remote} (master {git(origin, 'rev-parse', '--short', 'master')})")

        from scripts.new_session import create_session

        session = create_session(
            args.slug,
            mission=args.mission,
            transcript_path=args.transcript,
            max_experiments=args.max_experiments,
            remote=remote,
            workdir=workdir,
        )
        branch, session_rel = session["branch"], session["session_rel"]
        log(f"session {branch} at {session['sha'][:12]} (max_experiments={args.max_experiments})")

        config = smoke_config(
            json.loads((AUTORESEARCH_DIR / "langgraph.json").read_text(encoding="utf-8")),
            {"GIT_REMOTE": remote, "AUTORESEARCH_WORKDIR": str(workdir)},
        )
        config_path = root / "langgraph.json"
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

        server = start_server(config_path, args.port, server_log)
        log(f"langgraph dev pid {server.pid}; log {server_log}")
        wait_for_server(server, url, server_log, args.boot_timeout, log)

        import httpx
        from langgraph_sdk import get_sync_client

        # An experiment is ~5-6 min of Gemini time on the short transcript; never time out a wait.
        client = get_sync_client(url=url, timeout=httpx.Timeout(connect=10.0, read=None, write=60.0, pool=10.0))
        summary, interrupts = drive(client, branch, max_resumes=args.max_resumes, log=log)
        facts = check_origin(origin, branch, session_rel, args.max_experiments, allow_errors=args.allow_errors)
        report(summary, interrupts, facts, root, log)
        return 0
    except KeyboardInterrupt:
        log("interrupted")
        return 130
    except Exception as exc:  # SmokeError, GitError, SessionError, SDK errors: report and fail
        log(f"--- smoke FAILED: {type(exc).__name__}: {exc}")
        if server_log.exists():
            log("server log tail:\n" + tail(server_log))
        return 1
    finally:
        stop_server(server, log)


if __name__ == "__main__":
    raise SystemExit(main())
