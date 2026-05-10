"""Shared data models for PaperNav."""

from dataclasses import dataclass, field


@dataclass
class ParsedPaper:
    paper_id: str
    raw_text: str
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    abstract: str | None = None
    sections: dict[str, str] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class CitationMention:
    citation_id: str
    marker: str
    section_name: str
    sentence: str
    context_window: str
    role: str | None = None


@dataclass
class BibliographyEntry:
    citation_id: str
    raw_text: str
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None


@dataclass
class CitationRole:
    citation_id: str
    role: str
    confidence: str
    evidence_sentence: str
    section_name: str


@dataclass
class HistoryTreeNode:
    node_id: str
    citation_id: str
    title: str
    role: str
    citation_frequency: int
    year: int | None = None
    parent_id: str | None = None


@dataclass
class BaselineGraphNode:
    node_id: str
    citation_id: str
    title: str
    node_type: str
    role: str
    year: int | None = None


@dataclass
class BaselineGraphEdge:
    source: str
    target: str
    edge_type: str
    weight: float
    reason: str
