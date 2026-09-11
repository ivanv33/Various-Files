"""One-time generator: the 22 framework READMEs on the frameworks branch -> `engine/catalog/catalog.json`.

Reads `decomposition-frameworks/_meta/frameworks.json` and every
`decomposition-frameworks/<category>/<slug>/README.md` with `git show <ref>:<path>`; the branch is
never checked out. `summary` is the framework's `blurb`. `when_to_use` is distilled *deterministically*:
the first paragraph of "## What it decomposes" (the object the framework takes apart) followed by the
bold leads of the "### Failure modes" bullets. No model call, so the committed file is reproducible
and the tests stay offline.

Usage (from `autoresearch/`):
    .venv/bin/python -m scripts.build_catalog [--ref origin/claude/decomposition-frameworks-66ea98]
                                              [--out engine/catalog/catalog.json] [--repo <path>]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

if __package__ in (None, ""):  # `python scripts/build_catalog.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.catalog import CATALOG_PATH  # noqa: E402

DEFAULT_REF = "origin/claude/decomposition-frameworks-66ea98"
FRAMEWORKS_DIR = "decomposition-frameworks"
META_PATH = f"{FRAMEWORKS_DIR}/_meta/frameworks.json"
OBJECT_HEADING = "## What it decomposes"
FAILURE_HEADING = "### Failure modes"
REQUIRED_KEYS = ("slug", "name", "category", "summary", "when_to_use", "source")

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_BOLD_LEAD = re.compile(r"^\s*[-*]\s+\*\*(.+?)\*\*")
_PLAIN_BULLET = re.compile(r"^\s*[-*]\s+(?!\*\*)(\S.*)$")
# A plain bullet's title ends at the first "(", ":", "," or a sentence-ending period.
_LEAD_END = re.compile(r"\s*(?:[(:,]|\.(?=\s|$))")
_SPACES = re.compile(r"\s+")


def _one_line(text: str) -> str:
    return _SPACES.sub(" ", text).strip()


# --- markdown ---------------------------------------------------------------


def extract_section(markdown: str, heading: str) -> str:
    """Body under the exact `heading` line, up to the next heading of the same or a higher level.

    Headings inside fenced code blocks are ignored. Raises `ValueError` if the heading is absent.
    """
    m = _HEADING.match(heading.strip())
    if not m:
        raise ValueError(f"not a markdown heading: {heading!r}")
    level = len(m.group(1))
    wanted = heading.strip()
    lines = markdown.splitlines()
    start: int | None = None
    in_fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.strip() == wanted:
            start = i + 1
            break
    if start is None:
        raise ValueError(f"heading not found: {heading!r}")
    body: list[str] = []
    in_fence = False
    for line in lines[start:]:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        hm = None if in_fence else _HEADING.match(line)
        if hm and len(hm.group(1)) <= level:
            break
        body.append(line)
    return "\n".join(body).strip()


def first_paragraph(text: str) -> str:
    """First non-empty paragraph, with wrapped lines joined by single spaces."""
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if lines:
            return _one_line(" ".join(lines))
    return ""


def _table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1):
        return None
    return [c.strip() for c in stripped[1:-1].split("|")]


def _is_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def failure_mode_titles(text: str) -> list[str]:
    """Titles of the failure modes: bold leads of `- **Title.** ...` bullets, or the first column of a
    `| Failure | ... |` table (data rows after the `|---|` separator). Trailing periods dropped."""
    titles: list[str] = []
    in_table_body = False
    for line in text.splitlines():
        m = _BOLD_LEAD.match(line)
        if m:
            titles.append(_one_line(m.group(1)).rstrip(".").strip())
            continue
        m = _PLAIN_BULLET.match(line)
        if m:
            lead = _LEAD_END.split(m.group(1), maxsplit=1)[0]
            if lead.strip():
                titles.append(_one_line(lead))
            continue
        cells = _table_cells(line)
        if cells is None:
            in_table_body = False  # a table ends at the first non-row line
            continue
        if _is_table_separator(cells):
            in_table_body = True  # the header row came before this; data rows follow
            continue
        if in_table_body and cells[0]:
            titles.append(_one_line(cells[0].strip("*")).rstrip(".").strip())
    return titles


def distill_when_to_use(readme: str) -> str:
    """One line: what the framework takes apart, then the failure modes to guard against."""
    obj = first_paragraph(extract_section(readme, OBJECT_HEADING))
    modes = failure_mode_titles(extract_section(readme, FAILURE_HEADING))
    parts = [obj]
    if modes:
        parts.append("Failure modes to guard against: " + "; ".join(modes) + ".")
    return _one_line(" ".join(p for p in parts if p))


# --- entries ----------------------------------------------------------------


def build_entries(meta: dict[str, Any], read_readme: Callable[[str, str], str]) -> list[dict[str, Any]]:
    """Catalog entries in `frameworks.json` order; `read_readme(category, slug)` supplies each README."""
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for fw in meta["frameworks"]:
        slug = str(fw["slug"]).strip()
        if slug in seen:
            raise ValueError(f"duplicate slug in frameworks.json: {slug!r}")
        seen.add(slug)
        category = str(fw["category"]).strip()
        entries.append(
            {
                "slug": slug,
                "name": _one_line(str(fw["name"])),
                "category": category,
                "summary": _one_line(str(fw.get("blurb", ""))),
                "when_to_use": distill_when_to_use(read_readme(category, slug)),
                "source": "seed",
            }
        )
    return entries


def render(entries: list[dict[str, Any]]) -> str:
    return json.dumps(entries, indent=2, ensure_ascii=False) + "\n"


# --- git --------------------------------------------------------------------


def repo_root(start: Path) -> Path:
    out = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    )
    return Path(out.stdout.strip())


def git_show(repo: Path, ref: str, path: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git show {ref}:{path} failed: {proc.stderr.strip()}")
    return proc.stdout


def build_catalog(repo: Path, ref: str) -> list[dict[str, Any]]:
    meta = json.loads(git_show(repo, ref, META_PATH))
    return build_entries(meta, lambda category, slug: git_show(repo, ref, f"{FRAMEWORKS_DIR}/{category}/{slug}/README.md"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate engine/catalog/catalog.json from the frameworks branch.")
    parser.add_argument("--ref", default=DEFAULT_REF, help=f"git ref holding the READMEs (default {DEFAULT_REF})")
    parser.add_argument("--out", type=Path, default=CATALOG_PATH, help=f"output path (default {CATALOG_PATH})")
    parser.add_argument("--repo", type=Path, default=None, help="repository root (default: the one containing this script)")
    args = parser.parse_args(argv)
    repo = args.repo or repo_root(Path(__file__).resolve().parent)
    entries = build_catalog(repo, args.ref)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(entries), encoding="utf-8")
    print(f"wrote {len(entries)} entries to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
