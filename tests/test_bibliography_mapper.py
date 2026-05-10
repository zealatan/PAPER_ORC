"""Step 05: tests for the bibliography mapper."""

import json
import tempfile
from pathlib import Path

import pytest

from papernav.citation.bibliography import (
    extract_bibliography_entries,
    extract_bibliography_entries_from_text,
    generate_step05_outputs,
    map_mentions_to_bibliography,
    parse_reference_entry,
    save_bibliography_entries,
    save_citation_to_bibliography_map,
    split_reference_entries,
)
from papernav.models import BibliographyEntry, CitationMention
from papernav.parser import load_parsed_paper

SAMPLE_JSON = Path("examples/sample_parsed_paper.json")
SAMPLE_MENTIONS = Path("examples/sample_citation_mentions.json")
REAL_SNAP = Path("reports/step_outputs/step_03/real_paper_parsed_snapshot.json")

SIMPLE_REFS = """[1] A. Author. Simple Paper Title. Journal Name, 2020.
[2] B. Author and C. Author. Another Paper Title. Conference, 2021.
[3] D. Author. Multi-Line Paper Title with Long Name.
    Venue Proceedings, 2022."""

QUOTED_REF = '[1] A. Author. "Quoted Paper Title". IEEE Conference, 2020.'


# --- split_reference_entries ---

def test_split_detects_two_entries():
    text = "[1] Author One. Title. Venue, 2020.\n[2] Author Two. Other. Conf, 2021."
    entries = split_reference_entries(text)
    assert len(entries) == 2


def test_split_handles_multiline():
    entries = split_reference_entries(SIMPLE_REFS)
    assert len(entries) == 3
    assert entries[2].startswith("[3]")
    assert "Multi-Line" in entries[2]
    assert "Venue Proceedings" in entries[2]


# --- parse_reference_entry ---

def test_parse_extracts_citation_id():
    entry = parse_reference_entry("[1] A. Author. Title. Venue, 2020.")
    assert entry.citation_id == "ref_1"


def test_parse_extracts_quoted_title():
    entry = parse_reference_entry(QUOTED_REF)
    assert entry.title == "Quoted Paper Title"


def test_parse_extracts_year():
    entry = parse_reference_entry("[3] A. Author. Some Title. Conf, 1997.")
    assert entry.year == 1997


def test_parse_preserves_raw_text():
    raw = "[5] H. Wang. Deep Learning. IEEE, 2019."
    entry = parse_reference_entry(raw)
    assert entry.raw_text == raw


# --- extract_bibliography_entries_from_text ---

def test_extract_from_text_returns_list():
    entries = extract_bibliography_entries_from_text(SIMPLE_REFS)
    assert isinstance(entries, list)
    assert len(entries) == 3
    for e in entries:
        assert isinstance(e, BibliographyEntry)


# --- extract_bibliography_entries on synthetic fixture ---

def test_extract_bibliography_entries_synthetic():
    parsed = load_parsed_paper(str(SAMPLE_JSON))
    entries = extract_bibliography_entries(parsed)
    assert isinstance(entries, list)
    assert len(entries) > 0


def test_synthetic_bibliography_count_is_13():
    parsed = load_parsed_paper(str(SAMPLE_JSON))
    entries = extract_bibliography_entries(parsed)
    assert len(entries) == 13, f"Expected 13 entries, got {len(entries)}"


# --- map_mentions_to_bibliography ---

def test_map_mentions_covers_ref1_through_ref13():
    parsed = load_parsed_paper(str(SAMPLE_JSON))
    entries = extract_bibliography_entries(parsed)
    with open(SAMPLE_MENTIONS) as f:
        mentions = [CitationMention(**d) for d in json.load(f)]
    mapping = map_mentions_to_bibliography(mentions, entries)
    for i in range(1, 14):
        assert f"ref_{i}" in mapping, f"ref_{i} missing from mapping"


def test_map_missing_citation_id_ignored():
    entries = [BibliographyEntry(citation_id="ref_1", raw_text="[1] Author. Title. 2020.")]
    mentions = [CitationMention(
        citation_id="ref_99", marker="[99]",
        section_name="intro", sentence="See [99].", context_window="See [99].",
    )]
    mapping = map_mentions_to_bibliography(mentions, entries)
    assert "ref_99" not in mapping
    assert len(mapping) == 0


# --- save functions ---

def test_save_bibliography_entries_valid_json():
    entries = extract_bibliography_entries_from_text(SIMPLE_REFS)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp = f.name
    save_bibliography_entries(entries, tmp)
    with open(tmp) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["citation_id"].startswith("ref_")


def test_save_citation_to_bibliography_map_valid_json():
    entries = extract_bibliography_entries_from_text(SIMPLE_REFS)
    mentions = [
        CitationMention(citation_id="ref_1", marker="[1]",
                        section_name="intro", sentence="See [1].", context_window="[1]."),
        CitationMention(citation_id="ref_2", marker="[2]",
                        section_name="exp", sentence="Compare [2].", context_window="[2]."),
    ]
    mapping = map_mentions_to_bibliography(mentions, entries)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp = f.name
    save_citation_to_bibliography_map(mapping, tmp)
    with open(tmp) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert "ref_1" in data


# --- generate_step05_outputs ---

def test_generate_step05_outputs_creates_files(tmp_path):
    status = generate_step05_outputs(
        parsed_paper_path=str(SAMPLE_JSON),
        citation_mentions_path=str(SAMPLE_MENTIONS),
        output_dir=str(tmp_path),
    )
    assert (tmp_path / "bibliography_entries_snapshot.json").exists()
    assert (tmp_path / "citation_to_bibliography_map_snapshot.json").exists()
    assert (tmp_path / "bibliography_mapping_table.md").exists()
    assert (tmp_path / "citation_to_reference_map.mmd").exists()
    assert (tmp_path / "real_paper_bibliography_summary.md").exists()
    assert status["entry_count"] == 13
    assert status["mapped_count"] == 13


# --- real paper smoke test ---

@pytest.mark.skipif(not REAL_SNAP.exists(), reason="Real paper snapshot not present")
def test_real_paper_bibliography_smoke():
    parsed = load_parsed_paper(str(REAL_SNAP))
    entries = extract_bibliography_entries(parsed)
    assert isinstance(entries, list)
