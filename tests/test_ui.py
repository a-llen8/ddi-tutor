"""ml/ui.py: pills, summary and the notice text."""
import pytest

from ml.ui import CSS, NOTICE, severity_pill, severity_summary


def test_pill_shows_the_word_and_rejects_unknown_levels():
    assert "Major" in severity_pill("Major")
    assert "Listed, not graded" in severity_pill("Unknown")
    with pytest.raises(ValueError):
        severity_pill("<script>")


def test_every_level_has_a_style():
    for level in ("major", "moderate", "minor", "unknown"):
        assert ".ddi-" + level in CSS


def test_summary_counts_only_levels_present():
    out = severity_summary(["Major", "Major", "Minor"])
    assert "Major" in out and "Minor" in out and "Moderate" not in out
    assert "2" in out


def test_notice_keeps_the_honesty_rule():
    assert "never means safe" in NOTICE and "Learning only" in NOTICE
    assert "8 DDInter files" in NOTICE