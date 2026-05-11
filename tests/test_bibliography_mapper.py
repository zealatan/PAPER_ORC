"""Step 05: tests for the bibliography mapper."""

import json
import tempfile
from pathlib import Path

import pytest

from papernav.citation.bibliography import (
    extract_bibliography_entries,
    extract_bibliography_entries_from_text,
    extract_references_text_best_effort,
    generate_step05_outputs,
    map_mentions_to_bibliography,
    parse_reference_entry,
    save_bibliography_entries,
    save_citation_to_bibliography_map,
    split_reference_entries,
)
from papernav.models import BibliographyEntry, CitationMention, ParsedPaper
from papernav.parser import load_parsed_paper

SAMPLE_JSON = Path("examples/sample_parsed_paper.json")
SAMPLE_MENTIONS = Path("examples/sample_citation_mentions.json")
REAL_SNAP = Path("reports/step_outputs/step_03/real_paper_parsed_snapshot.json")

SIMPLE_REFS = """[1] A. Author. Simple Paper Title. Journal Name, 2020.
[2] B. Author and C. Author. Another Paper Title. Conference, 2021.
[3] D. Author. Multi-Line Paper Title with Long Name.
    Venue Proceedings, 2022."""

QUOTED_REF = '[1] A. Author. "Quoted Paper Title". IEEE Conference, 2020.'

# IEEE-style references with Unicode curly quotes (U+201C / U+201D)
IEEE_CURLY_REF_1 = (
    '[1] T. Wang, C.-K. Wen, H. Wang, F. Gao, T. Jiang, and S. Jin, '
    '“Deep learning for wireless physical layer: Opportunities and\n'
    'challenges,” China Commun., vol. 14, no. 11, pp. 92–111, Sep. 2017.'
)
IEEE_CURLY_REF_2 = (
    '[2] X. Gao, S. Jin, C.-K. Wen, and G. Y . Li, '
    '“ComNet: Combination of deep learning and expert knowledge in OFDM\n'
    'receivers,” IEEE Commun. Lett., vol. 22, no. 12, pp. 2627–2630, Dec. 2018.'
)
IEEE_CURLY_REF_10 = (
    '[10] T. O’Shea and J. Hoydis, '
    '“An introduction to deep learning for the physical layer,” '
    'IEEE Trans. Cogn. Commun. Netw., vol. 3, no. 4, pp. 563–575, Dec. 2017.'
)
MY_PAPER_PDF = Path("papers/real/my_paper.pdf")


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


# ---------------------------------------------------------------------------
# Step 10b — IEEE Unicode curly quote title extraction tests
# ---------------------------------------------------------------------------

def test_ieee_curly_quote_ref1_title():
    entry = parse_reference_entry(IEEE_CURLY_REF_1)
    assert entry.title == "Deep learning for wireless physical layer: Opportunities and challenges"


def test_ieee_curly_quote_ref2_title():
    entry = parse_reference_entry(IEEE_CURLY_REF_2)
    assert entry.title == "ComNet: Combination of deep learning and expert knowledge in OFDM receivers"


def test_ieee_curly_quote_ref10_title():
    entry = parse_reference_entry(IEEE_CURLY_REF_10)
    assert entry.title == "An introduction to deep learning for the physical layer"


def test_ieee_curly_quote_ref1_authors():
    entry = parse_reference_entry(IEEE_CURLY_REF_1)
    assert "T. Wang" in entry.authors
    assert "S. Jin" in entry.authors


def test_ieee_curly_quote_ref1_year():
    entry = parse_reference_entry(IEEE_CURLY_REF_1)
    assert entry.year == 2017


def test_ieee_curly_quote_extraction_method_is_quoted_title():
    entry = parse_reference_entry(IEEE_CURLY_REF_1)
    assert entry.metadata.get("title_extraction_method") == "quoted_title"


def test_fallback_rejects_author_fragment_as_title():
    # Reference with period-separated authors but no quoted title;
    # old heuristic would return "Wen, H" as title — this must not happen.
    ref = "[7] A. Long-Author, C.-K. Wen, H. Another. Some Title Here About Networks. Venue, 2020."
    entry = parse_reference_entry(ref)
    # Title should not be a short author fragment like "Wen, H"
    if entry.title is not None:
        assert len(entry.title) >= 10
        assert not entry.title.startswith("Wen")


def test_bibliography_entry_has_metadata_field():
    entry = parse_reference_entry(IEEE_CURLY_REF_1)
    assert hasattr(entry, "metadata")
    assert isinstance(entry.metadata, dict)


@pytest.mark.skipif(not MY_PAPER_PDF.exists(), reason="my_paper.pdf not present")
def test_my_paper_ref1_title_extracted_correctly():
    from papernav.parser import parse_file
    from papernav.citation.bibliography import extract_bibliography_entries
    parsed = parse_file(str(MY_PAPER_PDF), paper_id="my_paper")
    entries = extract_bibliography_entries(parsed)
    entry_map = {e.citation_id: e for e in entries}
    ref1 = entry_map.get("ref_1")
    assert ref1 is not None
    assert ref1.title is not None
    assert len(ref1.title) > 20


@pytest.mark.skipif(not MY_PAPER_PDF.exists(), reason="my_paper.pdf not present")
def test_my_paper_ref10_title_extracted_correctly():
    from papernav.parser import parse_file
    from papernav.citation.bibliography import extract_bibliography_entries
    parsed = parse_file(str(MY_PAPER_PDF), paper_id="my_paper")
    entries = extract_bibliography_entries(parsed)
    entry_map = {e.citation_id: e for e in entries}
    ref10 = entry_map.get("ref_10")
    assert ref10 is not None
    assert ref10.title is not None
    assert len(ref10.title) > 10


# ---------------------------------------------------------------------------
# Step 05b — extract_references_text_best_effort tests
# ---------------------------------------------------------------------------

_REFS_SECTION_TEXT = (
    "[1] A. Author. First Paper Title About Deep Learning. Journal of Neural Computation, 2020.\n"
    "[2] B. Author and C. Author. Second Paper on Channel Estimation Methods. Conf. on Communications, 2021.\n"
    "[3] C. Author, D. Author, and E. Author. Third Paper with a Long Descriptive Title on Signal Processing. Venue Proceedings, 2022.\n"
)

_RAW_TEXT_WITH_REFS = (
    "Some body text here.\n\n"
    "REFERENCES\n"
    "[1] A. Author. First Paper Title Here. Journal, 2020.\n"
    "[2] B. Author. Second Paper Title There. Conference, 2021.\n"
)

_RAW_TEXT_HIGH_NUMBERED = (
    "Body text.\n\n"
    "REFERENCES\n"
    + "".join(
        f"[{n}] Author{n}. Paper Title Number {n}. Venue, 20{10 + n % 10}.\n"
        for n in range(1, 62)
    )
)

_RAW_TEXT_WITH_BIOGRAPHY = (
    "Body text.\n\nREFERENCES\n"
    "[1] A. Author. Title One. Venue, 2020.\n"
    "[2] B. Author. Title Two. Venue, 2021.\n"
    "John Smith received the B.S. degree in EE from MIT.\n"
    "[3] Should not appear after biography stop.\n"
)

_HYPHENATED_REFS = (
    "[1] A. Author. This is a Long Paper Ti-\n"
    "tle About Channel Estimation. Venue, 2020.\n"
    "[2] B. Author. Another Short Title. Conference, 2021.\n"
)


def _make_parsed(sections: dict, raw_text: str = "") -> ParsedPaper:
    return ParsedPaper(paper_id="test", raw_text=raw_text, sections=sections)


# Test 1: uses sections["references"] when available
def test_best_effort_uses_sections_references_when_available():
    parsed = _make_parsed({"references": _REFS_SECTION_TEXT})
    result = extract_references_text_best_effort(parsed)
    assert "[1]" in result
    assert "[2]" in result


# Test 2: falls back to raw_text when references section is missing
def test_best_effort_falls_back_to_raw_text_when_no_section():
    parsed = _make_parsed({}, raw_text=_RAW_TEXT_WITH_REFS)
    result = extract_references_text_best_effort(parsed)
    assert "[1]" in result
    assert "[2]" in result


# Test 3: raw_text fallback detects [1] and [2]
def test_best_effort_raw_text_detects_ref1_and_ref2():
    parsed = _make_parsed({}, raw_text=_RAW_TEXT_WITH_REFS)
    result = extract_references_text_best_effort(parsed)
    assert result.count("[1]") >= 1
    assert result.count("[2]") >= 1


# Test 4: raw_text fallback supports high-numbered refs like [44] and [61]
def test_best_effort_raw_text_supports_high_numbered_refs():
    parsed = _make_parsed({}, raw_text=_RAW_TEXT_HIGH_NUMBERED)
    result = extract_references_text_best_effort(parsed)
    assert "[44]" in result
    assert "[61]" in result


# Test 5: raw_text fallback stops before "received the B.S."
def test_best_effort_raw_text_stops_before_biography():
    parsed = _make_parsed({}, raw_text=_RAW_TEXT_WITH_BIOGRAPHY)
    result = extract_references_text_best_effort(parsed)
    assert "received the B.S." not in result
    assert "[3] Should not appear" not in result


# Test 6: split_reference_entries handles multi-line IEEE entries
def test_split_handles_multiline_ieee_entries():
    text = (
        "[1] T. Wang, C.-K. Wen, H. Wang, F. Gao, T. Jiang, and S. Jin, "
        '"Deep learning for wireless physical layer," '
        "China Commun., vol. 14, no. 11, pp. 92-111, Sep. 2017.\n"
        "[2] X. Gao, S. Jin, C.-K. Wen, and G. Y. Li, "
        '"ComNet: Combination of deep learning," '
        "IEEE Commun. Lett., vol. 22, no. 12, pp. 2627-2630, Dec. 2018.\n"
    )
    entries = split_reference_entries(text)
    assert len(entries) == 2
    assert entries[0].startswith("[1]")
    assert entries[1].startswith("[2]")


# Test 7: split_reference_entries rejoins hyphenated line breaks
def test_split_handles_hyphenated_line_breaks():
    entries = split_reference_entries(_HYPHENATED_REFS)
    assert len(entries) == 2
    assert "Ti-" not in entries[0]
    assert "TiTitle" not in entries[0] or "Title" in entries[0]


# Test 8: parse_reference_entry returns BibliographyEntry even if title is None
def test_parse_returns_entry_even_if_title_none():
    raw = "[42] X."
    entry = parse_reference_entry(raw)
    assert isinstance(entry, BibliographyEntry)
    assert entry.citation_id == "ref_42"


# Test 9: parse_reference_entry extracts curly quote title
def test_parse_extracts_curly_quote_title():
    entry = parse_reference_entry(IEEE_CURLY_REF_2)
    assert entry.title is not None
    assert "ComNet" in entry.title


# Test 10: my_paper smoke — bibliography entry count > 0 after fallback
@pytest.mark.skipif(not MY_PAPER_PDF.exists(), reason="my_paper.pdf not present")
def test_my_paper_bibliography_count_positive_after_fallback():
    from papernav.parser import parse_file
    parsed = parse_file(str(MY_PAPER_PDF), paper_id="my_paper")
    entries = extract_bibliography_entries(parsed)
    assert len(entries) > 0, "Expected at least one bibliography entry via raw-text fallback"
