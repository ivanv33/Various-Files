"""`notes.md` helper shared by the loop (owner steering) and the reviewer (rubric changes)."""

from __future__ import annotations

import re

_HEADING = re.compile(r"^## ", re.M)


def append_under_heading(notes: str, heading: str, entry: str) -> str:
    """Append `entry` (a line ending in a newline) at the end of the `heading` section.

    The section is created at the end of the notes when missing; a heading with an empty body gets a blank
    line before the first entry; later entries follow the previous one directly.
    """
    m = re.search(rf"^{re.escape(heading)}[ \t]*$", notes, re.M)
    if not m:
        return notes.rstrip("\n") + f"\n\n{heading}\n\n{entry}"
    after = m.end()
    nxt = _HEADING.search(notes, after)
    end = nxt.start() if nxt else len(notes)
    section = notes[after:end].rstrip("\n")
    joined = section + "\n" + entry if section.strip() else "\n\n" + entry
    return notes[:after] + joined + ("\n" if nxt else "") + notes[end:]
