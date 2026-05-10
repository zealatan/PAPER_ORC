# Step 05 Report — Bibliography Mapper

## Status: PASS

## Bibliography Functions

| Function | Status |
|---|---|
| `split_reference_entries` | implemented |
| `parse_reference_entry` | implemented |
| `extract_bibliography_entries_from_text` | implemented |
| `extract_bibliography_entries` | implemented |
| `map_mentions_to_bibliography` | implemented |
| `save_bibliography_entries` | implemented |
| `save_citation_to_bibliography_map` | implemented |
| `generate_step05_outputs` | implemented |

## Synthetic Fixture Mapping Result

| Metric | Value |
|---|---|
| Bibliography entries | 13 |
| Citation IDs in mentions | 13 |
| Mapped citation IDs | 13 |
| Unmapped citation IDs | 0 |

First 5 mapped entries:

| Citation ID | Title | Year |
|---|---|---:|
| ref_1 | Technical Specification 38.211: NR Physical... | 2020 |
| ref_2 | Robust Frequency and Timing Synchronization... | 1997 |
| ref_3 | ML Estimation of Time and Frequency Offset... | 1997 |
| ref_4 | An Introduction to Deep Learning for the Ph... | 2017 |
| ref_5 | Deep Learning Based Channel Estimation for ... | 2019 |

Output JSON paths:
- `examples/sample_bibliography_entries.json`
- `examples/sample_citation_to_bibliography_map.json`
- `reports/step_outputs/step_05/bibliography_entries_snapshot.json`
- `reports/step_outputs/step_05/citation_to_bibliography_map_snapshot.json`

## Real Paper Smoke Result

| Metric | Value |
|---|---|
| Real parsed snapshot | PRESENT |
| References section | Yes |
| Bibliography entries | 21 |
| Mapped citation IDs | 21 |

## Visualization Outputs

| File | Description |
|---|---|
| `bibliography_mapping_table.md` | Summary + entry table + citation-to-bib mapping table |
| `citation_to_reference_map.mmd` | Mermaid flowchart of mapping pipeline |
| `bibliography_entries_snapshot.json` | Full BibliographyEntry list (synthetic) |
| `citation_to_bibliography_map_snapshot.json` | Full mapping dict (synthetic) |
| `real_paper_bibliography_summary.md` | RTLFixer smoke test result |
| `real_paper_bibliography_entries_snapshot.json` | RTLFixer BibliographyEntry list |
| `real_paper_citation_to_bibliography_map_snapshot.json` | RTLFixer mapping dict |

## Test Results

```
tests/test_bibliography_mapper.py — 15 passed
Full suite — 83 passed
```

## Notes

- Author–title boundary heuristic (first `. ` after word ≥ 3 chars) correctly handles all 13 synthetic entries including initials like `T.`, `M.`, `J.`, single-char authors, and organisation names like `3GPP`, `ITU-R`.
- Unmapped count is 0: all 13 citation IDs in mentions exist in entries.
- RTLFixer real paper: 21 entries detected from the references section extracted by pypdf; mapping covers all 21 IDs found in the citation mentions.

## Next Step

Step 06 — Citation Role Classifier: assign roles (history_foundational, baseline_direct, competitor, metric_source, etc.) to each `CitationMention` using section name and sentence-level text signals.
