#!/usr/bin/env bash
# Commit exactly one framework folder, safely, while other agents may be committing too.
# Usage: _meta/commit-framework.sh <framework-dir> "<subject>" ["<body>"]
# - Stages only <framework-dir>, commits only <framework-dir> (path-limited commit), so files
#   staged by concurrent agents are not swept in.
# - Retries with random backoff when git's index.lock is held by another process.
set -u
DIR="${1:?framework dir required}"
SUBJECT="${2:?commit subject required}"
BODY="${3:-}"
DIR="$(cd "$DIR" && pwd -P)"
ROOT="$(git -C "$DIR" rev-parse --show-toplevel)"
cd "$ROOT" || exit 1
REL="${DIR#$ROOT/}"
case "$REL" in
  decomposition-frameworks/0[1-4]-*/*) ;;
  *) echo "refusing: $REL is not a framework folder" >&2; exit 2 ;;
esac
MSG="$SUBJECT"
[ -n "$BODY" ] && MSG="$MSG"$'\n\n'"$BODY"
MSG="$MSG"$'\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'
ERR="$(mktemp)"
trap 'rm -f "$ERR"' EXIT
for attempt in $(seq 1 60); do
  if git add -- "$REL" 2>"$ERR" && git commit -q -m "$MSG" -- "$REL" 2>>"$ERR"; then
    echo "committed: $(git log -1 --format='%h %s')"
    exit 0
  fi
  if grep -qiE "nothing to commit|no changes added|nothing added" "$ERR"; then
    echo "nothing to commit for $REL"
    exit 0
  fi
  if grep -qiE "index\.lock|unable to create|another git process|could not lock" "$ERR"; then
    sleep "$((RANDOM % 3 + 1))"
    continue
  fi
  echo "commit failed (attempt $attempt):" >&2
  cat "$ERR" >&2
  exit 1
done
echo "gave up after 60 attempts; index.lock still held" >&2
exit 1
