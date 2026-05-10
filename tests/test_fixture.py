"""Step 02: sanity checks for the sample paper fixture."""

import re
from pathlib import Path

FIXTURE = Path("examples/sample_paper.txt")

REQUIRED_SECTIONS = ["Introduction", "Related Work", "Experiment", "References"]


def test_fixture_exists():
    assert FIXTURE.exists(), f"{FIXTURE} not found"


def test_fixture_non_empty():
    assert FIXTURE.stat().st_size > 0


def test_required_sections_present():
    text = FIXTURE.read_text()
    for section in REQUIRED_SECTIONS:
        assert section in text, f"Section '{section}' missing from fixture"


def test_citation_markers_count():
    text = FIXTURE.read_text()
    markers = re.findall(r"\[\d+\]", text)
    assert len(markers) >= 8, f"Expected >= 8 citation markers, found {len(markers)}"


def test_bibliography_entries_count():
    text = FIXTURE.read_text()
    refs_section = text.split("References:")[-1]
    entries = re.findall(r"^\[\d+\]", refs_section, re.MULTILINE)
    assert len(entries) >= 8, f"Expected >= 8 bibliography entries, found {len(entries)}"


def test_keyword_triggers_present():
    text = FIXTURE.read_text()
    assert "first proposed" in text or "pioneer" in text or "classical" in text
    assert "baseline" in text or "we compare with" in text or "compared against" in text
    assert "outperform" in text or "state-of-the-art" in text
