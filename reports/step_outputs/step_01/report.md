# Step 01 Report — Common Data Models

## Status: PASS

## Models defined

| Model | File | Line |
|---|---|---|
| `ParsedPaper` | `src/papernav/models.py` | 7 |
| `CitationMention` | `src/papernav/models.py` | 18 |
| `BibliographyEntry` | `src/papernav/models.py` | 28 |
| `CitationRole` | `src/papernav/models.py` | 38 |
| `HistoryTreeNode` | `src/papernav/models.py` | 47 |
| `BaselineGraphNode` | `src/papernav/models.py` | 58 |
| `BaselineGraphEdge` | `src/papernav/models.py` | 68 |

## Test results

```
tests/test_models.py — 11 passed in 0.12s
```

## Sanity checks

- All models use `@dataclass`
- Mutable defaults (`list`, `dict`) use `field(default_factory=...)` — no shared state
- Optional fields default to `None`
- No methods beyond dataclass-generated `__init__`, `__repr__`, `__eq__`

## Next step

Step 02 — `prompts/02_add_sample_paper_fixture.md`  
Create `examples/sample_paper.txt` with realistic Introduction and Experiment sections containing numeric citations and a bibliography.
