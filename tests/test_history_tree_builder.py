"""Tests for the Step 10 History Tree Builder."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from papernav.models import BibliographyEntry, CitationRole
from papernav.graph.history_tree import (
    build_history_tree,
    generate_step10_outputs,
    load_bibliography_map,
    load_citation_roles,
    render_history_tree_markdown,
    render_history_tree_mermaid,
    save_history_tree,
    select_history_roles,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SAMPLE_ROLES = [
    CitationRole("ref_1", "history_foundational", "high", "First foundational work.", "introduction"),
    CitationRole("ref_2", "history_direct_prior", "high", "Recent DL approach.", "introduction"),
    CitationRole("ref_3", "history_background", "medium", "OFDM standard ref.", "introduction"),
    CitationRole("ref_4", "baseline_direct", "high", "Baseline model.", "experiments"),
    CitationRole("ref_5", "misc", "high", "[5] Y.", "references"),
    CitationRole("ref_1", "history_foundational", "high", "Seminal paper again.", "related_work"),
]

_SAMPLE_BIB: dict[str, BibliographyEntry] = {
    "ref_1": BibliographyEntry("ref_1", "[1] Author. Title One. 2000.", "Title One", ["Author"], 2000, "Journal"),
    "ref_2": BibliographyEntry("ref_2", "[2] Author B. DL Paper. 2020.", "DL Paper", ["Author B"], 2020, "Conf"),
    "ref_3": BibliographyEntry("ref_3", "[3] 3GPP. OFDM Spec. 2019.", "OFDM Spec", ["3GPP"], 2019, "Release"),
}


# ---------------------------------------------------------------------------
# 1-5: select_history_roles
# ---------------------------------------------------------------------------

def test_select_history_roles_includes_foundational():
    roles = [CitationRole("ref_1", "history_foundational", "high", "ev", "introduction")]
    selected = select_history_roles(roles)
    assert len(selected) == 1
    assert selected[0].role == "history_foundational"


def test_select_history_roles_includes_direct_prior():
    roles = [CitationRole("ref_2", "history_direct_prior", "medium", "ev", "introduction")]
    selected = select_history_roles(roles)
    assert len(selected) == 1
    assert selected[0].role == "history_direct_prior"


def test_select_history_roles_includes_background():
    roles = [CitationRole("ref_3", "history_background", "low", "ev", "related_work")]
    selected = select_history_roles(roles)
    assert len(selected) == 1
    assert selected[0].role == "history_background"


def test_select_history_roles_excludes_baseline_direct():
    roles = [CitationRole("ref_4", "baseline_direct", "high", "ev", "experiments")]
    selected = select_history_roles(roles)
    assert selected == []


def test_select_history_roles_excludes_misc():
    roles = [CitationRole("ref_5", "misc", "high", "[5] Y.", "references")]
    selected = select_history_roles(roles)
    assert selected == []


# ---------------------------------------------------------------------------
# 6-10: build_history_tree
# ---------------------------------------------------------------------------

def test_build_history_tree_creates_target_paper_node():
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    assert tree["target_node"]["node_id"] == "target_paper"
    assert tree["target_node"]["role"] == "target"


def test_build_history_tree_deduplicates_citation_id():
    # ref_1 appears twice as history_foundational
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    node_ids = [n["node_id"] for n in tree["nodes"]]
    assert node_ids.count("ref_1") == 1


def test_build_history_tree_computes_citation_frequency():
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    ref1_nodes = [n for n in tree["nodes"] if n["node_id"] == "ref_1"]
    assert ref1_nodes[0]["citation_frequency"] == 2


def test_build_history_tree_creates_edges_when_history_nodes_exist():
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    assert len(tree["edges"]) >= 1


def test_build_history_tree_reading_path_ends_with_target_paper():
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    assert tree["reading_path"][-1] == "target_paper"


# ---------------------------------------------------------------------------
# 11-12: render functions
# ---------------------------------------------------------------------------

def test_render_history_tree_mermaid_returns_flowchart_lr():
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    mmd = render_history_tree_mermaid(tree)
    assert mmd.startswith("flowchart LR")


def test_render_history_tree_markdown_includes_reading_path():
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    md = render_history_tree_markdown(tree)
    assert "Suggested Reading Path" in md


# ---------------------------------------------------------------------------
# 13: save_history_tree
# ---------------------------------------------------------------------------

def test_save_history_tree_writes_valid_json(tmp_path):
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    out = tmp_path / "tree.json"
    save_history_tree(tree, str(out))
    with open(out) as f:
        loaded = json.load(f)
    assert loaded["paper_id"] == "sample_paper"
    assert "nodes" in loaded
    assert "edges" in loaded


# ---------------------------------------------------------------------------
# 14: generate_step10_outputs
# ---------------------------------------------------------------------------

def test_generate_step10_outputs_creates_required_files(tmp_path):
    roles_path = "reports/step_outputs/step_06c/reclassified_citation_roles.json"
    bib_path = "examples/sample_citation_to_bibliography_map.json"

    if not Path(roles_path).exists():
        pytest.skip("reclassified_citation_roles.json not found")
    if not Path(bib_path).exists():
        pytest.skip("sample_citation_to_bibliography_map.json not found")

    out_dir = str(tmp_path / "step_10")
    generate_step10_outputs(
        roles_path=roles_path,
        bibliography_map_path=bib_path,
        output_dir=out_dir,
    )

    required = [
        "history_tree.json",
        "history_tree.md",
        "history_tree.mmd",
        "history_tree_table.md",
        "history_tree_summary.md",
        "real_paper_history_tree_summary.md",
    ]
    for fname in required:
        assert (tmp_path / "step_10" / fname).exists(), f"Missing: {fname}"


# ---------------------------------------------------------------------------
# 15: synthetic fixture creates non-empty tree
# ---------------------------------------------------------------------------

def test_synthetic_fixture_creates_nonempty_history_tree():
    tree = build_history_tree(_SAMPLE_ROLES, _SAMPLE_BIB)
    # ref_1 (foundational x2), ref_2 (direct_prior), ref_3 (background) — 3 unique nodes
    assert tree["summary"]["unique_history_nodes"] > 0
    assert len(tree["nodes"]) > 0
    assert len(tree["reading_path"]) > 1


# ---------------------------------------------------------------------------
# 16: real paper smoke test
# ---------------------------------------------------------------------------

def test_real_paper_smoke_test():
    real_roles_path = "reports/step_outputs/step_06/real_paper_citation_roles_snapshot.json"
    real_bib_path = "reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json"

    if not Path(real_roles_path).exists():
        pytest.skip("Real paper citation roles snapshot not found.")

    real_roles = load_citation_roles(real_roles_path)
    real_bib = load_bibliography_map(real_bib_path) if Path(real_bib_path).exists() else {}
    real_tree = build_history_tree(real_roles, real_bib, paper_id="real_paper")

    assert "paper_id" in real_tree
    assert real_tree["target_node"]["node_id"] == "target_paper"
    assert isinstance(real_tree["nodes"], list)
    assert isinstance(real_tree["edges"], list)
