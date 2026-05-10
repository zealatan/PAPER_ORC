"""Tests for the Citation Role Classifier (Step 06)."""

import json
import os
import tempfile

import pytest

from papernav.citation.classifier import (
    classify_citation_role,
    classify_citation_roles,
    generate_step06_outputs,
    generate_step06c_outputs,
    save_citation_roles,
)
from papernav.models import (
    CITATION_ROLE_LABELS,
    CONFIDENCE_LABELS,
    BibliographyEntry,
    CitationMention,
    CitationRole,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_mention(
    citation_id: str = "ref_1",
    section_name: str = "introduction",
    sentence: str = "",
    context_window: str = "",
) -> CitationMention:
    return CitationMention(
        citation_id=citation_id,
        marker="[1]",
        section_name=section_name,
        sentence=sentence,
        context_window=context_window,
    )


def _make_bib(citation_id: str = "ref_1", title: str = "A Paper", year: int = 2020) -> BibliographyEntry:
    return BibliographyEntry(citation_id=citation_id, raw_text="...", title=title, year=year)


# ---------------------------------------------------------------------------
# Unit tests — keyword-based rules
# ---------------------------------------------------------------------------

class TestKeywordRules:
    def test_intro_classical_gives_history_foundational(self):
        m = _make_mention(section_name="introduction", sentence="The classical method was first described in [1].")
        role = classify_citation_role(m)
        assert role.role == "history_foundational"

    def test_intro_recent_works_gives_history_direct_prior(self):
        m = _make_mention(
            section_name="introduction",
            sentence="Recent works by Smith et al. [1] have explored this approach.",
        )
        role = classify_citation_role(m)
        assert role.role == "history_direct_prior"

    def test_intro_default_gives_history_background(self):
        m = _make_mention(
            section_name="introduction",
            sentence="[1] is a relevant reference in this area.",
        )
        role = classify_citation_role(m)
        assert role.role == "history_background"

    def test_experiment_baseline_gives_baseline_direct(self):
        m = _make_mention(
            section_name="experiment",
            sentence="We evaluate against the baseline method [1].",
        )
        role = classify_citation_role(m)
        assert role.role == "baseline_direct"

    def test_experiment_compare_against_gives_baseline_direct(self):
        m = _make_mention(
            section_name="experiment",
            sentence="We compare against [1] across all conditions.",
        )
        role = classify_citation_role(m)
        assert role.role == "baseline_direct"

    def test_results_outperform_gives_competitor(self):
        m = _make_mention(
            section_name="results",
            sentence="Our method outperforms [1] by 3 dB.",
        )
        role = classify_citation_role(m)
        assert role.role == "competitor"

    def test_benchmark_keyword_gives_benchmark_source(self):
        m = _make_mention(
            section_name="experiment",
            sentence="We use the standard benchmark from [1] for evaluation.",
        )
        role = classify_citation_role(m)
        assert role.role == "benchmark_source"

    def test_metric_keyword_gives_metric_source(self):
        m = _make_mention(
            section_name="experiment",
            sentence="The accuracy metric [1] is computed per frame.",
        )
        role = classify_citation_role(m)
        assert role.role == "metric_source"

    def test_discussion_reported_gives_supporting_evidence(self):
        m = _make_mention(
            section_name="discussion",
            sentence="As reported in [1], the effect is consistent across domains.",
        )
        role = classify_citation_role(m)
        assert role.role == "supporting_evidence"

    def test_references_section_gives_misc(self):
        m = _make_mention(
            citation_id="ref_1",
            section_name="references",
            sentence="[1] A. Author, Title, 2020.",
        )
        role = classify_citation_role(m)
        assert role.role == "misc"
        assert role.confidence == "high"
        assert "anchor" in role.reason.lower()


# ---------------------------------------------------------------------------
# List-level tests
# ---------------------------------------------------------------------------

class TestClassifyList:
    def test_returns_same_length_as_mentions(self):
        mentions = [
            _make_mention("ref_1", "introduction", "The seminal work [1]."),
            _make_mention("ref_2", "experiment", "We compare against baseline [2]."),
            _make_mention("ref_3", "references", "[3] B. Author."),
        ]
        roles = classify_citation_roles(mentions)
        assert len(roles) == len(mentions)

    def test_all_roles_are_valid_labels(self):
        mentions = [
            _make_mention("ref_1", section_name=sec, sentence=f"Cite [1] in {sec}.")
            for sec in ["introduction", "experiment", "results", "discussion", "references", "unknown_section"]
        ]
        roles = classify_citation_roles(mentions)
        for r in roles:
            assert r.role in CITATION_ROLE_LABELS, f"Invalid role: {r.role}"

    def test_all_confidence_values_are_valid(self):
        mentions = [
            _make_mention("ref_1", section_name=sec, sentence=f"Cite [1] in {sec}.")
            for sec in ["introduction", "experiment", "results", "discussion", "references"]
        ]
        roles = classify_citation_roles(mentions)
        for r in roles:
            assert r.confidence in CONFIDENCE_LABELS, f"Invalid confidence: {r.confidence}"


# ---------------------------------------------------------------------------
# Synthetic fixture integration tests
# ---------------------------------------------------------------------------

SAMPLE_MENTIONS_PATH = "examples/sample_citation_mentions.json"
SAMPLE_BIB_MAP_PATH = "examples/sample_citation_to_bibliography_map.json"


def _load_fixture_roles():
    if not os.path.exists(SAMPLE_MENTIONS_PATH) or not os.path.exists(SAMPLE_BIB_MAP_PATH):
        pytest.skip("Sample fixture files not found")
    with open(SAMPLE_MENTIONS_PATH, encoding="utf-8") as fh:
        mentions = [CitationMention(**r) for r in json.load(fh)]
    with open(SAMPLE_BIB_MAP_PATH, encoding="utf-8") as fh:
        raw_bib = json.load(fh)
    bib_map = {k: BibliographyEntry(**v) for k, v in raw_bib.items()}
    return classify_citation_roles(mentions, bib_map)


class TestSyntheticFixture:
    def test_synthetic_produces_at_least_one_history_role(self):
        from papernav.models import is_history_role

        roles = _load_fixture_roles()
        history = [r for r in roles if is_history_role(r.role)]
        assert len(history) >= 1, "Expected at least one history role in synthetic fixture"

    def test_synthetic_produces_at_least_one_baseline_or_competitor(self):
        from papernav.models import is_baseline_role

        roles = _load_fixture_roles()
        baseline = [r for r in roles if is_baseline_role(r.role)]
        assert len(baseline) >= 1, "Expected at least one baseline/competitor role in synthetic fixture"


# ---------------------------------------------------------------------------
# I/O tests
# ---------------------------------------------------------------------------

class TestIO:
    def test_save_citation_roles_writes_valid_json(self, tmp_path):
        roles = [
            CitationRole(
                citation_id="ref_1",
                role="history_foundational",
                confidence="high",
                evidence_sentence="Seminal work [1].",
                section_name="introduction",
                reason="Test reason.",
            )
        ]
        out = str(tmp_path / "roles.json")
        save_citation_roles(roles, out)
        with open(out, encoding="utf-8") as fh:
            data = json.load(fh)
        assert isinstance(data, list)
        assert data[0]["role"] == "history_foundational"
        assert data[0]["reason"] == "Test reason."

    def test_generate_step06_outputs_creates_required_files(self, tmp_path):
        if not os.path.exists(SAMPLE_MENTIONS_PATH) or not os.path.exists(SAMPLE_BIB_MAP_PATH):
            pytest.skip("Sample fixture files not found")
        out_dir = str(tmp_path / "step_06")
        generate_step06_outputs(
            citation_mentions_path=SAMPLE_MENTIONS_PATH,
            bibliography_map_path=SAMPLE_BIB_MAP_PATH,
            output_dir=out_dir,
        )
        required = [
            "citation_roles_snapshot.json",
            "citation_role_summary.md",
            "citation_role_flow.mmd",
            "history_citation_candidates.md",
            "baseline_citation_candidates.md",
            "real_paper_citation_role_summary.md",
        ]
        for fname in required:
            path = os.path.join(out_dir, fname)
            assert os.path.exists(path), f"Missing required output: {fname}"
        # Verify JSON is valid
        with open(os.path.join(out_dir, "citation_roles_snapshot.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# Real paper smoke test
# ---------------------------------------------------------------------------

REAL_MENTIONS_PATH = "reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json"
REAL_BIB_MAP_PATH = "reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json"


class TestRealPaperSmoke:
    def test_real_paper_role_classification(self):
        if not os.path.exists(REAL_MENTIONS_PATH):
            pytest.skip("Real paper citation mentions snapshot not found")
        if not os.path.exists(REAL_BIB_MAP_PATH):
            pytest.skip("Real paper bibliography map not found")

        with open(REAL_MENTIONS_PATH, encoding="utf-8") as fh:
            mentions = [CitationMention(**r) for r in json.load(fh)]
        with open(REAL_BIB_MAP_PATH, encoding="utf-8") as fh:
            raw_bib = json.load(fh)
        bib_map = {k: BibliographyEntry(**v) for k, v in raw_bib.items()}

        roles = classify_citation_roles(mentions, bib_map)
        assert isinstance(roles, list)
        assert len(roles) == len(mentions)
        for r in roles:
            assert r.role in CITATION_ROLE_LABELS
            assert r.confidence in CONFIDENCE_LABELS


# ---------------------------------------------------------------------------
# Step 06c — Precision patch tests
# ---------------------------------------------------------------------------

class TestPrecisionPatch:
    """Verify sentence-first classification and tightened foundational keyword rules."""

    def test_classical_in_sentence_gives_history_foundational(self):
        m = _make_mention(
            section_name="introduction",
            sentence="The classical Schmidl-Cox method [1] is the standard reference for timing synchronization.",
        )
        role = classify_citation_role(m)
        assert role.role == "history_foundational"

    def test_introduced_alone_in_sentence_does_not_give_history_foundational(self):
        m = _make_mention(
            section_name="introduction",
            sentence="Smith et al. [1] introduced a new timing synchronization method.",
        )
        role = classify_citation_role(m)
        assert role.role != "history_foundational", (
            "'introduced' alone should not trigger history_foundational after the precision patch"
        )

    def test_recent_works_in_sentence_gives_history_direct_prior(self):
        m = _make_mention(
            section_name="introduction",
            sentence="Recent works [1] have explored deep learning for synchronization.",
        )
        role = classify_citation_role(m)
        assert role.role == "history_direct_prior"

    def test_deep_learning_in_related_work_sentence_gives_history_direct_prior(self):
        m = _make_mention(
            section_name="related_work",
            sentence="Deep learning methods [1] have been applied to OFDM receivers.",
        )
        role = classify_citation_role(m)
        assert role.role == "history_direct_prior"

    def test_context_classical_without_sentence_match_does_not_give_history_foundational(self):
        """Context-window bleed must not trigger history_foundational for a long sentence."""
        m = _make_mention(
            section_name="introduction",
            # Long sentence (> 10 words) with no foundational keyword
            sentence="The proposed method [1] extends this prior approach to handle frequency offsets efficiently.",
            context_window="The classical Schmidl-Cox approach [0] remains widely used. The proposed method [1] extends...",
        )
        role = classify_citation_role(m)
        assert role.role != "history_foundational", (
            "Context-window 'classical' should not trigger foundational when sentence is long and lacks foundational kw"
        )

    def test_experiment_sentence_baseline_gives_baseline_direct(self):
        m = _make_mention(
            section_name="experiment",
            sentence="We compare the proposed model against the baseline method [1].",
        )
        role = classify_citation_role(m)
        assert role.role == "baseline_direct"

    def test_context_benchmark_without_long_sentence_match_does_not_give_benchmark_source(self):
        """Long sentence (>= 10 words) with no benchmark kw in sentence must not get benchmark_source."""
        m = _make_mention(
            section_name="experiment",
            # Long sentence — no benchmark/dataset keyword
            sentence="We evaluate the proposed method using the standard OFDM channel model [1] across SNR levels.",
            context_window="using the VerilogEval benchmark and dataset from prior work...",
        )
        role = classify_citation_role(m)
        assert role.role != "benchmark_source", (
            "Context-window 'benchmark' should not override a long experiment sentence without benchmark kw"
        )

    def test_references_section_gives_misc(self):
        m = _make_mention(
            section_name="references",
            sentence="[1] A. Author, Title, 2020.",
        )
        role = classify_citation_role(m)
        assert role.role == "misc"

    def test_synthetic_fixture_still_has_history_role_after_patch(self):
        from papernav.models import is_history_role
        roles = _load_fixture_roles()
        assert any(is_history_role(r.role) for r in roles)

    def test_synthetic_fixture_still_has_baseline_or_benchmark_after_patch(self):
        from papernav.models import is_baseline_role
        roles = _load_fixture_roles()
        assert any(is_baseline_role(r.role) for r in roles)

    def test_generate_step06c_outputs_creates_required_files(self, tmp_path):
        if not os.path.exists(SAMPLE_MENTIONS_PATH) or not os.path.exists(SAMPLE_BIB_MAP_PATH):
            pytest.skip("Sample fixture files not found")
        old_roles_path = "examples/sample_citation_roles.json"
        if not os.path.exists(old_roles_path):
            pytest.skip("Old citation roles JSON not found")
        out_dir = str(tmp_path / "step_06c")
        generate_step06c_outputs(
            citation_mentions_path=SAMPLE_MENTIONS_PATH,
            bibliography_map_path=SAMPLE_BIB_MAP_PATH,
            old_roles_path=old_roles_path,
            output_dir=out_dir,
        )
        required = [
            "reclassified_citation_roles.json",
            "before_after_role_comparison.md",
            "history_tree_preview_after_patch.mmd",
            "classifier_precision_patch_summary.md",
        ]
        for fname in required:
            path = os.path.join(out_dir, fname)
            assert os.path.exists(path), f"Missing required output: {fname}"
        with open(os.path.join(out_dir, "reclassified_citation_roles.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        assert isinstance(data, list)
