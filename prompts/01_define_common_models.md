# Prompt 01 — Define Common Data Models

## Working directory

`/home/zealatan/PAPER_ORC`

## Objective

Define all shared dataclasses for PaperNav in `src/papernav/models.py`. These are the canonical data structures passed between every pipeline stage. No business logic — types and fields only.

## Context

The pipeline passes structured data between stages:

```
Parser → CitationExtractor → BibliographyMapper → RoleClassifier → TreeBuilders → Agents
```

All stages must share the same model definitions from this module.

## Allowed modifications

- `src/papernav/models.py`
- `tests/test_models.py` (create)

## Models to define

All models use `@dataclass` with type annotations. Use `field(default_factory=...)` for mutable defaults.

### ParsedPaper
- `paper_id: str`
- `title: str | None`
- `authors: list[str]`
- `abstract: str | None`
- `sections: dict[str, str]` — section name → full text
- `raw_text: str`
- `metadata: dict`

### CitationMention
- `citation_id: str` — e.g. `"ref_12"`
- `marker: str` — e.g. `"[12]"`
- `section_name: str`
- `sentence: str`
- `context_window: str`
- `role: str | None`

### BibliographyEntry
- `citation_id: str`
- `raw_text: str`
- `title: str | None`
- `authors: list[str]`
- `year: int | None`
- `venue: str | None`

### CitationRole
- `citation_id: str`
- `role: str` — one of the 10 role labels
- `confidence: str` — `"high"`, `"medium"`, or `"low"`
- `evidence_sentence: str`
- `section_name: str`

### HistoryTreeNode
- `node_id: str`
- `citation_id: str`
- `title: str`
- `year: int | None`
- `role: str`
- `citation_frequency: int`
- `parent_id: str | None`

### BaselineGraphNode
- `node_id: str`
- `citation_id: str`
- `title: str`
- `year: int | None`
- `node_type: str`
- `role: str`

### BaselineGraphEdge
- `source: str`
- `target: str`
- `edge_type: str`
- `weight: float`
- `reason: str`

## Implementation requirements

- Use `from dataclasses import dataclass, field`
- All models are plain dataclasses — no ORM, no Pydantic
- Mutable default fields use `field(default_factory=list)` or `field(default_factory=dict)`
- No methods other than what `@dataclass` generates automatically

## Tests

Create `tests/test_models.py`:
- Instantiate each model with minimal required arguments
- Assert field values are stored correctly
- Assert default mutable fields are independent per instance (no shared state)

## Final report format

```
PASS/FAIL
Models defined: N
Tests: N passed
```
