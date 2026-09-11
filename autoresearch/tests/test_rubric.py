"""`engine/tasks/rubric.py`: core dimensions, extras drafting (structured output), render/parse."""

from __future__ import annotations

import os
import re

import pytest

from engine.tasks.rubric import (
    CORE_DIMENSIONS,
    MAX_EXTRAS,
    MIN_EXTRAS,
    SCORE_MAX,
    SCORE_MIN,
    Dimension,
    ExtraDimension,
    RubricError,
    RubricExtras,
    draft_extras,
    parse_rubric,
    render_rubric,
)

EXTRAS = [
    Dimension(id="unit_economics", name="Unit economics", description="Steps name the cost or revenue lever they move.", kind="extra"),
    Dimension(id="time_to_signal", name="Time to signal", description="Weeks until a measurable result.", kind="extra"),
]


def test_core_dimensions_are_fixed_and_well_formed():
    assert 4 <= len(CORE_DIMENSIONS) <= 6
    ids = [d.id for d in CORE_DIMENSIONS]
    assert len(set(ids)) == len(ids)
    for d in CORE_DIMENSIONS:
        assert d.kind == "core"
        assert re.fullmatch(r"[a-z][a-z0-9_]*", d.id), d.id
        assert d.name.strip() and d.description.strip()
        assert d.scale == "1-10"
    assert (SCORE_MIN, SCORE_MAX) == (1, 10)
    assert (MIN_EXTRAS, MAX_EXTRAS) == (1, 3)


def test_dimension_rejects_bad_id_and_blank_text():
    with pytest.raises(ValueError):
        Dimension(id="Not Valid", name="x", description="y")
    with pytest.raises(ValueError):
        Dimension(id="ok", name="  ", description="y")


def test_render_then_parse_round_trips_core_and_extras():
    text = render_rubric(CORE_DIMENSIONS, EXTRAS)
    assert text.startswith("# Rubric")
    assert "## Core dimensions" in text and "## Mission-specific dimensions" in text
    assert f"{SCORE_MIN}" in text and f"{SCORE_MAX}" in text
    assert parse_rubric(text) == list(CORE_DIMENSIONS) + EXTRAS


def test_render_with_no_extras_still_parses_to_core_only():
    assert parse_rubric(render_rubric(CORE_DIMENSIONS, [])) == list(CORE_DIMENSIONS)


def test_parse_rubric_tolerates_owner_edits_to_prose_and_extra_sections():
    text = render_rubric(CORE_DIMENSIONS, EXTRAS)
    text = text.replace("# Rubric", "# Rubric (edited by owner)\n\nSome preamble the owner added.\n")
    text += "\n## Notes from the owner\n\n### not_a_dimension: ignored\n\nThis section is not a dimension list.\n"
    assert parse_rubric(text) == list(CORE_DIMENSIONS) + EXTRAS


def test_parse_rubric_rejects_text_without_dimensions():
    with pytest.raises(RubricError, match="no dimensions"):
        parse_rubric("# Rubric\n\nnothing here\n")


def test_parse_rubric_rejects_duplicate_ids():
    dup = Dimension(id=CORE_DIMENSIONS[0].id, name="Dup", description="collides", kind="extra")
    with pytest.raises(RubricError, match="duplicate"):
        parse_rubric(render_rubric(CORE_DIMENSIONS, [dup]))


# --- draft_extras -------------------------------------------------------------


def _good() -> RubricExtras:
    return RubricExtras(
        dimensions=[
            ExtraDimension(name="Unit Economics", description="A 10 names the lever; a 1 ignores money."),
            ExtraDimension(name="Time to first signal", description="A 10 gets a result in weeks; a 1 in years."),
        ]
    )


def test_draft_extras_returns_extra_dimensions_with_slug_ids(structured_fake):
    model = structured_fake([_good()])
    dims = draft_extras(model, "Grow ARR 3x in 12 months")
    assert [d.id for d in dims] == ["unit_economics", "time_to_first_signal"]
    assert [d.name for d in dims] == ["Unit Economics", "Time to first signal"]
    assert all(d.kind == "extra" and d.scale == "1-10" for d in dims)
    assert len(model.calls) == 1
    schema, prompt_input = model.calls[0]
    assert schema is RubricExtras
    flat = str(prompt_input)
    assert "Grow ARR 3x in 12 months" in flat
    assert CORE_DIMENSIONS[0].name in flat, "the prompt lists the core dimensions so the model does not duplicate them"


def test_draft_extras_repairs_once_when_output_collides_with_core(structured_fake):
    bad = RubricExtras(dimensions=[ExtraDimension(name=CORE_DIMENSIONS[0].name, description="restates a core dimension")])
    model = structured_fake([bad, _good()])
    dims = draft_extras(model, "m")
    assert [d.id for d in dims] == ["unit_economics", "time_to_first_signal"]
    assert len(model.calls) == 2
    assert "core" in str(model.calls[1][1]).lower(), "the repair turn explains the violation"


def test_draft_extras_repairs_once_when_model_raises(structured_fake):
    model = structured_fake([ValueError("malformed structured output"), _good()])
    dims = draft_extras(model, "m")
    assert len(dims) == 2
    assert len(model.calls) == 2
    assert "malformed structured output" in str(model.calls[1][1])


def test_draft_extras_gives_up_after_one_repair(structured_fake):
    empty = RubricExtras(dimensions=[])
    model = structured_fake([empty, empty])
    with pytest.raises(RubricError, match="repair"):
        draft_extras(model, "m")
    assert len(model.calls) == 2


def test_draft_extras_rejects_too_many_and_duplicate_extras(structured_fake):
    four = RubricExtras(dimensions=[ExtraDimension(name=f"Dim {i}", description="d") for i in range(4)])
    dupes = RubricExtras(dimensions=[ExtraDimension(name="Same", description="a"), ExtraDimension(name="same", description="b")])
    model = structured_fake([four, dupes])
    with pytest.raises(RubricError):
        draft_extras(model, "m")


@pytest.mark.live
def test_draft_extras_live_returns_one_to_three_non_core_dimensions():
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    from engine.config import make_model

    dims = draft_extras(make_model(), "Find the underserved vertical-AI market that TBPN guests keep circling without naming")
    assert MIN_EXTRAS <= len(dims) <= MAX_EXTRAS
    assert not {d.id for d in dims} & {d.id for d in CORE_DIMENSIONS}
    assert all(len(d.description) > 20 for d in dims)
    # the drafted extras must survive a round trip through rubric.md
    assert parse_rubric(render_rubric(CORE_DIMENSIONS, dims)) == list(CORE_DIMENSIONS) + dims
