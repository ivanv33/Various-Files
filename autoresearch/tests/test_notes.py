"""`engine/tasks/notes.py`: heading-scoped append shared by `loop.add_steering` and `proposals.add_rubric_change_note`."""

from engine.loop import add_steering
from engine.tasks.notes import append_under_heading
from engine.tasks.proposals import add_rubric_change_note

NOTES = "# Notes\n\n## Insights\n\n- one\n\n## Human steering\n\n## Rubric changes\n\n- T0: first\n"


def test_creates_the_section_at_the_end_when_missing():
    assert append_under_heading("# Notes\n", "## Open questions", "- q\n") == "# Notes\n\n## Open questions\n\n- q\n"


def test_appends_to_an_empty_section_and_then_directly_after_the_last_entry():
    once = add_steering(NOTES, "stay concrete\nsecond line", timestamp="T1")
    assert "## Human steering\n\n- T1: stay concrete\n  second line\n\n## Rubric changes" in once
    twice = add_steering(once, "now MECE", timestamp="T2")
    assert "## Human steering\n\n- T1: stay concrete\n  second line\n- T2: now MECE\n\n## Rubric changes" in twice
    assert twice.count("## Human steering") == 1


def test_last_section_grows_without_touching_the_others():
    out = add_rubric_change_note(NOTES, "rubric-change-a.md accepted", timestamp="T1")
    assert out.endswith("## Rubric changes\n\n- T0: first\n- T1: rubric-change-a.md accepted\n")
    assert out.startswith("# Notes\n\n## Insights\n\n- one\n\n## Human steering\n\n## Rubric changes")
