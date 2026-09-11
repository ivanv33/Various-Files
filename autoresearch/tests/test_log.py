from pathlib import Path

import pytest

from engine.tasks.log import (
    COLUMNS,
    HEADER,
    LogRow,
    append_row,
    digest,
    parse_tsv,
    read_rows,
    render_tsv,
)

SESSION_REL = "autoresearch/sessions/demo"


def test_header_matches_spec_columns():
    assert COLUMNS == ["n", "timestamp", "frameworks", "candidate_total", "incumbent_total", "kept", "note"]
    assert HEADER == "\t".join(COLUMNS)


def test_row_round_trips_through_tsv_line():
    row = LogRow(
        n=2,
        timestamp="2026-09-10T12:00:00Z",
        frameworks=["jobs-to-be-done", "first-principles"],
        candidate_total=41,
        incumbent_total=39,
        kept="1",
        note="better sequencing",
    )
    line = row.to_tsv_line()
    assert line == "2\t2026-09-10T12:00:00Z\tjobs-to-be-done+first-principles\t41\t39\t1\tbetter sequencing"
    assert LogRow.from_tsv_line(line) == row


def test_empty_incumbent_and_error_rows():
    first = LogRow(n=1, frameworks=["a"], candidate_total=30, incumbent_total=None, kept=True, note="seed")
    assert first.kept == "1"
    assert first.to_tsv_line().split("\t")[4] == ""
    err = LogRow(n=3, frameworks=[], candidate_total=None, incumbent_total=None, kept="error", note="boom")
    parsed = LogRow.from_tsv_line(err.to_tsv_line())
    assert parsed.frameworks == []
    assert parsed.candidate_total is None
    assert parsed.kept == "error"
    assert first.timestamp.endswith("Z")


def test_kept_accepts_bool_and_rejects_garbage():
    assert LogRow(n=1, frameworks=[], kept=False, note="").kept == "0"
    with pytest.raises(ValueError):
        LogRow(n=1, frameworks=[], kept="maybe", note="")


def test_note_is_flattened_to_one_line():
    row = LogRow(n=1, frameworks=["a"], kept="0", note="line one\nline\ttwo\r\nthree")
    assert "\n" not in row.note and "\t" not in row.note and "\r" not in row.note
    assert row.note == "line one line two three"


def test_append_creates_header_and_read_rows_parses(tmp_path: Path):
    assert read_rows(tmp_path, SESSION_REL) == []
    append_row(tmp_path, SESSION_REL, LogRow(n=1, frameworks=["a"], candidate_total=10, kept="1", note="x"))
    append_row(tmp_path, SESSION_REL, LogRow(n=2, frameworks=["b"], candidate_total=9, incumbent_total=10, kept="0", note="y"))
    text = (tmp_path / SESSION_REL / "experiments.tsv").read_text()
    assert text.startswith(HEADER + "\n")
    assert text.endswith("\n")
    rows = read_rows(tmp_path, SESSION_REL)
    assert [r.n for r in rows] == [1, 2]
    assert rows[1].incumbent_total == 10


def test_append_to_header_only_file_without_trailing_newline(tmp_path: Path):
    path = tmp_path / SESSION_REL / "experiments.tsv"
    path.parent.mkdir(parents=True)
    path.write_text(HEADER)  # no trailing newline
    append_row(tmp_path, SESSION_REL, LogRow(n=1, frameworks=["a"], kept="1", note=""))
    assert len(read_rows(tmp_path, SESSION_REL)) == 1


def test_parse_and_render_skip_blank_lines():
    text = HEADER + "\n\n1\t2026\ta\t5\t\t1\tn\n\n"
    rows = parse_tsv(text)
    assert len(rows) == 1
    assert render_tsv(rows) == HEADER + "\n1\t2026\ta\t5\t\t1\tn\n"


def test_parse_skips_the_header_after_a_leading_blank_line_and_when_repeated():
    """A hand-edited tsv may start with a blank line or carry a second header after a merge; neither is a row."""
    text = "\n" + HEADER + "\n1\t2026\ta\t5\t\t1\tn\n" + HEADER + "\n2\t2026\tb\t4\t5\t0\tm\n"
    assert [(r.n, r.kept) for r in parse_tsv(text)] == [(1, "1"), (2, "0")]
    assert parse_tsv("\n\n" + HEADER + "\n") == []
    assert parse_tsv("  \n" + HEADER + "  \n") == []


def test_digest_is_plain_serializable_dict():
    row = LogRow(n=1, frameworks=["a"], kept="1", note="")
    d = digest("new_best", n=1, row=row, path=Path("/x"), trend=[{"n": 1}])
    assert d["kind"] == "new_best"
    assert d["row"]["n"] == 1 and isinstance(d["row"], dict)
    assert d["path"] == "/x"
    assert "resume" in d and "continue" in d["resume"] and "stop" in d["resume"]
    import json

    json.dumps(d)
