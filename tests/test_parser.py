"""Step 03: tests for the paper parser."""

import json
import tempfile
from pathlib import Path

import pytest

from papernav.models import ParsedPaper
from papernav.parser import (
    generate_step03_outputs,
    parse_file,
    parse_pdf,
    parse_text,
    save_parsed_paper,
)

SAMPLE_TXT = Path("examples/sample_paper.txt")
REAL_PDF = Path("papers/real/rtlfixer_2311_16543.pdf")


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
