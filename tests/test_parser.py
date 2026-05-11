"""Step 03 / 03b: tests for the paper parser."""

import json
import re
import tempfile
from pathlib import Path

import pytest

from papernav.models import ParsedPaper
from papernav.parser import (
    _denoise_pdf_heading,
    generate_step03_outputs,
    parse_file,
    parse_pdf,
    parse_text,
    save_parsed_paper,
)

SAMPLE_TXT = Path("examples/sample_paper.txt")
REAL_PDF = Path("papers/real/rtlfixer_2311_16543.pdf")
MY_PAPER_PDF = Path("papers/real/my_paper.pdf")


# --- basic parse_text ---

def test_parse_text_returns_parsed_paper():
    result = parse_text("Some text about a paper.", paper_id="test")
    assert isinstance(result, ParsedPaper)


def test_parse_text_preserves_raw_text():
    text = "Title: Foo\nSome body text."
    result = parse_text(text, paper_id="t")
    assert result.raw_text == text


# --- parse_file with synthetic fixture ---

def test_parse_file_txt_returns_parsed_paper():
    result = parse_file(str(SAMPLE_TXT))
    assert isinstance(result, ParsedPaper)
    assert result.raw_text


def test_synthetic_detects_introduction():
    assert "introduction" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_detects_related_work():
    assert "related_work" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_detects_experiment():
    assert "experiment" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_detects_results():
    assert "results" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_detects_discussion():
    assert "discussion" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_detects_references():
    assert "references" in parse_file(str(SAMPLE_TXT)).sections


def test_section_text_non_empty():
    result = parse_file(str(SAMPLE_TXT))
    for key, text in result.sections.items():
        assert text.strip(), f"Section '{key}' has empty text"


def test_raw_text_preserved():
    result = parse_file(str(SAMPLE_TXT))
    assert result.raw_text == SAMPLE_TXT.read_text(encoding="utf-8")


def test_section_objects_populated():
    result = parse_file(str(SAMPLE_TXT))
    assert len(result.section_objects) >= 6
    for sec in result.section_objects:
        assert sec.name
        assert sec.text.strip()


# --- save / JSON ---

def test_save_parsed_paper_writes_valid_json():
    result = parse_file(str(SAMPLE_TXT))
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp = f.name
    save_parsed_paper(result, tmp)
    with open(tmp) as f:
        data = json.load(f)
    assert "paper_id" in data
    assert "sections" in data
    assert "section_objects" in data


def test_sample_parsed_paper_json_generated():
    result = parse_file(str(SAMPLE_TXT))
    out = "examples/sample_parsed_paper.json"
    save_parsed_paper(result, out)
    assert Path(out).exists()
    with open(out) as f:
        data = json.load(f)
    assert "sections" in data
    assert "introduction" in data["sections"]


# --- error handling ---

def test_parse_file_rejects_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file extension"):
        parse_file("somefile.docx")


# --- real PDF smoke test ---

@pytest.mark.skipif(not REAL_PDF.exists(), reason="Real PDF not present")
def test_parse_pdf_smoke():
    result = parse_pdf(str(REAL_PDF), paper_id="rtlfixer_2311_16543")
    assert isinstance(result, ParsedPaper)
    assert len(result.raw_text) > 100
    assert result.metadata.get("source_type") == "pdf"
    assert result.metadata.get("page_count", 0) > 0


# --- generate_step03_outputs ---

def test_generate_step03_outputs_creates_files(tmp_path):
    status = generate_step03_outputs(
        sample_path=str(SAMPLE_TXT),
        output_dir=str(tmp_path),
    )
    assert (tmp_path / "parsed_paper_snapshot.json").exists()
    assert (tmp_path / "parsed_sections.md").exists()
    assert (tmp_path / "section_split_diagram.mmd").exists()
    assert (tmp_path / "real_paper_parse_summary.md").exists()
    assert status["section_count"] >= 6
    assert "introduction" in status["section_keys"]


# ---------------------------------------------------------------------------
# Step 03b — IEEE Roman numeral heading tests
# ---------------------------------------------------------------------------

def _parse_roman_text(headings_body: str) -> dict:
    """Helper: parse a synthetic text with IEEE-style Roman numeral headings."""
    return parse_text(headings_body, paper_id="test_roman").sections


def test_roman_heading_introduction_detected():
    text = "I. INTRODUCTION\nThis is the introduction body."
    sections = _parse_roman_text(text)
    assert "introduction" in sections


def test_roman_heading_system_model_detected():
    text = "I. INTRODUCTION\nIntro body.\nII. SYSTEM MODEL AND CHANNEL ESTIMATION\nSystem body."
    sections = _parse_roman_text(text)
    assert "system_model" in sections


def test_roman_heading_simulation_results_maps_to_experiment():
    text = "VI. SIMULATION RESULTS\nHere are results."
    sections = _parse_roman_text(text)
    assert "experiment" in sections


def test_roman_heading_conclusions_detected():
    text = "VII. CONCLUSIONS\nWe conclude here."
    sections = _parse_roman_text(text)
    assert "conclusion" in sections


def test_roman_heading_unknown_preserved_as_snake_case():
    text = "III. INTERNAL MECHANISM OF RELU DNNS\nBody text here."
    sections = _parse_roman_text(text)
    assert "internal_mechanism_of_relu_dnns" in sections


def test_synthetic_fixture_still_detects_introduction():
    assert "introduction" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_fixture_still_detects_related_work():
    assert "related_work" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_fixture_still_detects_experiment():
    assert "experiment" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_fixture_still_detects_results():
    assert "results" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_fixture_still_detects_discussion():
    assert "discussion" in parse_file(str(SAMPLE_TXT)).sections


def test_synthetic_fixture_still_detects_references():
    assert "references" in parse_file(str(SAMPLE_TXT)).sections


@pytest.mark.skipif(not MY_PAPER_PDF.exists(), reason="my_paper.pdf not present")
def test_my_paper_detects_more_than_two_sections():
    result = parse_file(str(MY_PAPER_PDF), paper_id="my_paper")
    assert len(result.sections) > 2, f"Only found: {list(result.sections.keys())}"


@pytest.mark.skipif(not MY_PAPER_PDF.exists(), reason="my_paper.pdf not present")
def test_my_paper_detects_introduction():
    result = parse_file(str(MY_PAPER_PDF), paper_id="my_paper")
    assert "introduction" in result.sections, f"Sections: {list(result.sections.keys())}"


@pytest.mark.skipif(not MY_PAPER_PDF.exists(), reason="my_paper.pdf not present")
def test_my_paper_references_accessible():
    # References may appear as a parsed section OR only in raw_text (split-heading PDF artifact).
    # Verify that at least one of these holds so downstream extractors can find them.
    result = parse_file(str(MY_PAPER_PDF), paper_id="my_paper")
    has_section = "references" in result.sections
    has_raw_refs = bool(result.raw_text and re.search(r"\[1\]", result.raw_text))
    assert has_section or has_raw_refs, (
        f"Neither references section nor [1] marker found. Sections: {list(result.sections.keys())}"
    )


@pytest.mark.skipif(not MY_PAPER_PDF.exists(), reason="my_paper.pdf not present")
def test_my_paper_has_body_sections_beyond_intro_and_conclusion():
    # Verify the paper has at least one substantive body section (model, system, method, etc.)
    # beyond introduction and conclusion — exact names vary by paper.
    result = parse_file(str(MY_PAPER_PDF), paper_id="my_paper")
    skip = {"introduction", "abstract", "conclusion", "conclusion_and_discussion",
            "references", "bibliography"}
    body_sections = [k for k in result.sections if k not in skip]
    assert len(body_sections) >= 1, (
        f"Expected at least one body section. Sections: {list(result.sections.keys())}"
    )


def test_denoise_pdf_heading_introduction():
    assert _denoise_pdf_heading("I NTRODUCTION") == "INTRODUCTION"


def test_denoise_pdf_heading_system_model():
    assert _denoise_pdf_heading("S YSTEM MODEL") == "SYSTEM MODEL"


def test_denoise_pdf_heading_dnn_suffix():
    assert _denoise_pdf_heading("DNN S") == "DNNS"
