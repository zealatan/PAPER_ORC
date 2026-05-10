"""Step 04: tests for the citation extractor."""

import json
import tempfile
from pathlib import Path

import pytest

from papernav.citation.extractor import (
    extract_citations,
    extract_citations_from_text,
    generate_step04_outputs,
    save_citation_mentions,
)
from papernav.models import CitationMention
from papernav.parser import load_parsed_paper

SAMPLE_JSON = Path("examples/sample_parsed_paper.json")
REAL_SNAP = Path("reports/step_outputs/step_03/real_paper_parsed_snapshot.json")


# --- extract_citations_from_text: pattern detection ---

def test_single_citation():
    results = extract_citations_from_text("See [1] for details.", "intro")
    ids = [m.citation_id for m in results]
    assert "ref_1" in ids


def test_grouped_citation_with_spaces():
    results = extract_citations_from_text("Compare [1, 2] in the paper.", "intro")
    ids = [m.citation_id for m in results]
    assert "ref_1" in ids
    assert "ref_2" in ids


def test_compact_grouped_citation():
    results = extract_citations_from_text("As shown in [1,2,3].", "intro")
    ids = [m.citation_id for m in results]
    assert "ref_1" in ids and "ref_2" in ids and "ref_3" in ids


def test_range_hyphen():
    results = extract_citations_from_text("Methods [1]-[3] were evaluated.", "exp")
    ids = [m.citation_id for m in results]
    assert "ref_1" in ids and "ref_2" in ids and "ref_3" in ids


def test_range_en_dash():
    results = extract_citations_from_text("Results [1]–[3] are shown.", "results")
    ids = [m.citation_id for m in results]
    assert "ref_1" in ids and "ref_2" in ids and "ref_3" in ids


def test_mixed_group():
    results = extract_citations_from_text("See [1, 3-5] for comparison.", "exp")
    ids = [m.citation_id for m in results]
    assert "ref_1" in ids
    assert "ref_3" in ids and "ref_4" in ids and "ref_5" in ids
    assert "ref_2" not in ids


def test_citation_id_normalized():
    results = extract_citations_from_text("Prior work [7] showed this.", "rw")
    assert results[0].citation_id == "ref_7"


def test_marker_preserved():
    results = extract_citations_from_text("See [1, 2] for details.", "intro")
    assert results[0].marker == "[1, 2]"
    assert results[1].marker == "[1, 2]"


def test_section_name_preserved():
    results = extract_citations_from_text("Baseline [3].", "experiment")
    assert results[0].section_name == "experiment"


def test_sentence_non_empty():
    results = extract_citations_from_text("Prior work [5] established this.", "intro")
    assert results[0].sentence.strip()


def test_context_window_present():
    results = extract_citations_from_text("Prior work [5] established this.", "intro")
    assert results[0].context_window.strip()


# --- extract_citations on synthetic fixture ---

def test_extract_citations_synthetic():
    parsed = load_parsed_paper(str(SAMPLE_JSON))
    mentions = extract_citations(parsed)
    assert len(mentions) >= 28  # at least body citations


def test_synthetic_has_introduction_citations():
    parsed = load_parsed_paper(str(SAMPLE_JSON))
    mentions = extract_citations(parsed)
    intro_ids = {m.citation_id for m in mentions if m.section_name == "introduction"}
    assert intro_ids, "No citations found in introduction"


def test_synthetic_has_experiment_citations():
    parsed = load_parsed_paper(str(SAMPLE_JSON))
    mentions = extract_citations(parsed)
    exp_ids = {m.citation_id for m in mentions if m.section_name == "experiment"}
    assert exp_ids, "No citations found in experiment"


def test_synthetic_has_references_citations():
    parsed = load_parsed_paper(str(SAMPLE_JSON))
    mentions = extract_citations(parsed)
    ref_mentions = [m for m in mentions if m.section_name == "references"]
    assert len(ref_mentions) >= 13, f"Expected >=13 reference anchors, got {len(ref_mentions)}"


# --- save_citation_mentions ---

def test_save_citation_mentions_valid_json():
    results = extract_citations_from_text("Compare [1, 2] methods.", "intro")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp = f.name
    save_citation_mentions(results, tmp)
    with open(tmp) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["citation_id"].startswith("ref_")


# --- generate_step04_outputs ---

def test_generate_step04_outputs_creates_files(tmp_path):
    status = generate_step04_outputs(
        parsed_paper_path=str(SAMPLE_JSON),
        output_dir=str(tmp_path),
    )
    assert (tmp_path / "citation_mentions_snapshot.json").exists()
    assert (tmp_path / "citation_extraction_table.md").exists()
    assert (tmp_path / "citation_extraction_flow.mmd").exists()
    assert (tmp_path / "real_paper_citation_summary.md").exists()
    assert status["total_mentions"] >= 28
    assert "introduction" in status["section_counts"]


# --- real paper smoke test ---

@pytest.mark.skipif(not REAL_SNAP.exists(), reason="Real paper snapshot not present")
def test_real_paper_citation_smoke():
    parsed = load_parsed_paper(str(REAL_SNAP))
    mentions = extract_citations(parsed)
    assert isinstance(mentions, list)
    # At minimum should detect some numeric citations in the real PDF
    assert len(mentions) > 0
