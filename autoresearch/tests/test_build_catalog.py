"""`scripts/build_catalog.py`: README section extraction, `when_to_use` distillation, entry build.

Pure-function tests on synthetic markdown, plus sanity checks on the committed seed catalog.
"""

from __future__ import annotations

import json

import pytest

from engine.catalog import CATALOG_PATH, load_seed_catalog
from scripts.build_catalog import (
    REQUIRED_KEYS,
    build_entries,
    distill_when_to_use,
    extract_section,
    failure_mode_titles,
    first_paragraph,
)

README = """# Widget Method

> One-line tagline. Category: Things. Reference: [x](http://example.invalid).

## What this graph derived

Given that somebody said something, we derived a thing.

## What it decomposes

The Widget Method takes apart a whole with a size: a budget, a roster, a market.
It splits it into parts under one rule.

What it forces into the open is the rule you cut on.

## The slots

- `part`: a piece.

## Building a knowledge graph with this framework

### Extraction recipe

1. Read.

### Failure modes

- **The rule is never chosen.** Parts with no rule. Guard: name the rule.
- **Two rules in one cut.** Mixed dimensions. Guard: test each part.
- **Fake exhaustiveness.** A catch-all "Other". Guard: size the residual.

### Where the opportunity shows up

Somewhere.

## Related frameworks

- Other Method.
"""


def test_extract_section_returns_body_until_next_heading_of_same_or_higher_level():
    body = extract_section(README, "## What it decomposes")
    assert body.startswith("The Widget Method takes apart")
    assert "What it forces into the open" in body
    assert "The slots" not in body
    assert "`part`" not in body


def test_extract_section_h3_stops_at_next_h3_or_h2():
    body = extract_section(README, "### Failure modes")
    assert "The rule is never chosen" in body
    assert "Fake exhaustiveness" in body
    assert "Where the opportunity shows up" not in body
    assert "Somewhere" not in body


def test_extract_section_missing_heading_raises():
    with pytest.raises(ValueError, match="Nope"):
        extract_section(README, "## Nope")


def test_first_paragraph_joins_wrapped_lines():
    body = extract_section(README, "## What it decomposes")
    para = first_paragraph(body)
    assert para == (
        "The Widget Method takes apart a whole with a size: a budget, a roster, a market. "
        "It splits it into parts under one rule."
    )


def test_failure_mode_titles_are_the_bold_bullet_leads_without_trailing_period():
    body = extract_section(README, "### Failure modes")
    assert failure_mode_titles(body) == [
        "The rule is never chosen",
        "Two rules in one cut",
        "Fake exhaustiveness",
    ]


TABLE_FAILURES = """
| Failure | What it looks like | Guard |
|---|---|---|
| Invented quotes | A fact node with a quote the transcript never says. | Validator string match. |
| Post hoc attribution as fact | "Renewals rose" after "I sent the notice". | Fact only with a stated connective. |
| PAR that swallows the graph | The problem node absorbs every fact. | Two to four `supported_by` edges. |
"""


def test_failure_mode_titles_reads_first_column_of_a_table():
    """Three seed READMEs (star-par, carl, toulmin-model) use a table instead of bold bullets."""
    assert failure_mode_titles(TABLE_FAILURES) == [
        "Invented quotes",
        "Post hoc attribution as fact",
        "PAR that swallows the graph",
    ]


PLAIN_FAILURES = """
- Warrant restated as the claim ("the data centers are safe"). Guard: conditional form.
- Invented grounds: a plausible number the speaker did not say. Guard: the quote check.
- Dropped qualifier. Guard: search for hedges first.
- The business reading written into the rationale, so the two cannot be told apart. Guard: rationale only.
"""


def test_failure_mode_titles_takes_the_lead_of_plain_bullets():
    """toulmin-model uses plain bullets: the lead runs to the first `(`, `:`, `,` or sentence end."""
    assert failure_mode_titles(PLAIN_FAILURES) == [
        "Warrant restated as the claim",
        "Invented grounds",
        "Dropped qualifier",
        "The business reading written into the rationale",
    ]


def test_distill_when_to_use_combines_object_and_failure_modes_on_one_line():
    text = distill_when_to_use(README)
    assert "\n" not in text
    assert text.startswith("The Widget Method takes apart a whole with a size")
    assert "Failure modes to guard against: The rule is never chosen; Two rules in one cut; Fake exhaustiveness." in text


def test_build_entries_uses_meta_fields_and_readme_distillation():
    meta = {
        "categories": [{"id": "99-things", "name": "Things", "order": 1}],
        "frameworks": [
            {
                "slug": "widget-method",
                "name": "Widget Method",
                "category": "99-things",
                "blurb": "Splits a whole into parts under one rule.",
                "slots": [],
                "relations": [],
                "wikipedia": "http://example.invalid",
            }
        ],
    }
    seen: list[str] = []

    def read_readme(category: str, slug: str) -> str:
        seen.append(f"{category}/{slug}")
        return README

    entries = build_entries(meta, read_readme)
    assert seen == ["99-things/widget-method"]
    assert len(entries) == 1
    entry = entries[0]
    assert set(entry) == set(REQUIRED_KEYS)
    assert entry["slug"] == "widget-method"
    assert entry["name"] == "Widget Method"
    assert entry["category"] == "99-things"
    assert entry["summary"] == "Splits a whole into parts under one rule."
    assert entry["when_to_use"].startswith("The Widget Method takes apart")
    assert entry["source"] == "seed"


def test_build_entries_rejects_duplicate_slugs():
    fw = {"slug": "dup", "name": "Dup", "category": "c", "blurb": "b"}
    meta = {"frameworks": [fw, dict(fw)]}
    with pytest.raises(ValueError, match="duplicate slug"):
        build_entries(meta, lambda c, s: README)


# --- the committed seed catalog ---------------------------------------------


def test_committed_seed_catalog_has_22_well_formed_entries():
    assert CATALOG_PATH.is_file(), f"missing {CATALOG_PATH}"
    entries = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert isinstance(entries, list)
    assert len(entries) == 22
    slugs = [e["slug"] for e in entries]
    assert len(set(slugs)) == 22
    for e in entries:
        assert set(e) == set(REQUIRED_KEYS), e.get("slug")
        for key in REQUIRED_KEYS:
            assert isinstance(e[key], str) and e[key].strip(), (e.get("slug"), key)
        assert e["source"] == "seed"
        assert "\n" not in e["when_to_use"]
    assert {"mece", "cynefin", "five-whys", "wardley-mapping"} <= set(slugs)
    assert {e["category"] for e in entries} == {
        "01-narrative-and-statement",
        "02-strategic-and-business",
        "03-engineering-and-cognitive",
        "04-sensemaking-and-complex-systems",
    }


def test_load_seed_catalog_returns_fresh_list_each_call():
    a = load_seed_catalog()
    b = load_seed_catalog()
    assert a == b and a is not b
    assert len(a) == 22
