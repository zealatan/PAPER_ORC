"""Step 01: unit tests for shared data models."""

from papernav.models import (
    BaselineGraphEdge,
    BaselineGraphNode,
    BibliographyEntry,
    CitationMention,
    CitationRole,
    HistoryTreeNode,
    ParsedPaper,
)


class TestParsedPaper:
    def test_required_fields(self):
        p = ParsedPaper(paper_id="p1", raw_text="body")
        assert p.paper_id == "p1"
        assert p.raw_text == "body"

    def test_defaults(self):
        p = ParsedPaper(paper_id="p1", raw_text="")
        assert p.title is None
        assert p.abstract is None
        assert p.authors == []
        assert p.sections == {}
        assert p.metadata == {}

    def test_mutable_defaults_independent(self):
        a = ParsedPaper(paper_id="a", raw_text="")
        b = ParsedPaper(paper_id="b", raw_text="")
        a.authors.append("Alice")
        assert b.authors == []


class TestCitationMention:
    def test_fields(self):
        m = CitationMention(
            citation_id="ref_1",
            marker="[1]",
            section_name="Introduction",
            sentence="This was first proposed in [1].",
            context_window="...[1]...",
        )
        assert m.citation_id == "ref_1"
        assert m.role is None

    def test_role_can_be_set(self):
        m = CitationMention(
            citation_id="ref_1",
            marker="[1]",
            section_name="Introduction",
            sentence="s",
            context_window="c",
            role="history_foundational",
        )
        assert m.role == "history_foundational"


class TestBibliographyEntry:
    def test_required_fields(self):
        e = BibliographyEntry(citation_id="ref_1", raw_text="A. Author. Title. 2020.")
        assert e.citation_id == "ref_1"
        assert e.title is None
        assert e.year is None
        assert e.venue is None

    def test_mutable_defaults_independent(self):
        a = BibliographyEntry(citation_id="a", raw_text="")
        b = BibliographyEntry(citation_id="b", raw_text="")
        a.authors.append("Alice")
        assert b.authors == []


class TestCitationRole:
    def test_fields(self):
        r = CitationRole(
            citation_id="ref_1",
            role="history_foundational",
            confidence="high",
            evidence_sentence="First proposed in [1].",
            section_name="Introduction",
        )
        assert r.role == "history_foundational"
        assert r.confidence == "high"


class TestHistoryTreeNode:
    def test_fields(self):
        n = HistoryTreeNode(
            node_id="n1",
            citation_id="ref_1",
            title="Foundational Work",
            role="history_foundational",
            citation_frequency=3,
        )
        assert n.year is None
        assert n.parent_id is None
        assert n.citation_frequency == 3


class TestBaselineGraphNode:
    def test_fields(self):
        n = BaselineGraphNode(
            node_id="n1",
            citation_id="ref_5",
            title="Baseline Method",
            node_type="method",
            role="baseline_direct",
        )
        assert n.year is None
        assert n.node_type == "method"


class TestBaselineGraphEdge:
    def test_fields(self):
        e = BaselineGraphEdge(
            source="n1",
            target="n2",
            edge_type="comparison",
            weight=1.0,
            reason="compared in Table 2",
        )
        assert e.weight == 1.0
        assert e.edge_type == "comparison"
