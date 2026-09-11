#!/usr/bin/env bash
# Plan M6: local end-to-end smoke with real Gemini against a bare origin cloned from this worktree.
# Thin wrapper; the driver and its options live in dev/smoke.py (`dev/smoke.sh --help`).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec .venv/bin/python -m dev.smoke "$@"
