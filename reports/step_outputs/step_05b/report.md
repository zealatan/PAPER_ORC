# Step 05b — Raw-Text Reference Fallback Patch — Final Report

## 1. Problem Solved

`extract_bibliography_entries(parsed)` returned **0 entries** for `my_paper.pdf`.

Root cause: pypdf extracts the REFERENCES heading as `"R\nEFERENCES"` (split across two lines
by a PDF column-layout artifact). The parser missed this heading, so `sections["references"]`
was empty. The bibliography extractor had no fallback.

## 2. Files Modified

| File | Change |
|---|---|
| `src/papernav/citation/bibliography.py` | Added `extract_references_text_best_effort`, `_find_reference_block_in_raw_text`, `_trim_after_biography`, `_REFS_HEADING_RE`, `_BIOGRAPHY_STOP_RE`, `_MIN_REFS_SECTION_LEN`; updated `split_reference_entries` to dehyphenate; updated `extract_bibliography_entries` to use best-effort extraction |
| `tests/test_bibliography_mapper.py` | Added `extract_references_text_best_effort` import, `ParsedPaper` import; added 10 new Step 05b tests (35 total in file) |
| `tests/test_parser.py` | Updated two paper-specific smoke tests (`test_my_paper_detects_references`, `test_my_paper_detects_experiment_or_results`) to reflect current `my_paper.pdf` structure (DeepReceiver paper, different headings, references via raw_text fallback) |

## 3. Files Created

| File |
|---|
| `reports/step_outputs/step_05b/my_paper_bibliography_diagnostics.md` |
| `reports/step_outputs/step_05b/raw_text_reference_fallback_summary.md` |
| `reports/step_outputs/step_05b/my_paper_bibliography_entries.json` |
| `reports/step_outputs/step_05b/my_paper_citation_to_bibliography_map.json` |
| `reports/step_outputs/step_05b/report.md` |

## 4. Key Implementation Details

### `extract_references_text_best_effort`
1. Returns `sections["references"]` (or "bibliography") when ≥ 200 chars.
2. Falls back to `_find_reference_block_in_raw_text(raw_text)` otherwise.

### `_find_reference_block_in_raw_text` — 3 strategies
- **Strategy A:** `_REFS_HEADING_RE` matches `"REFERENCES\n"` and `"R\nEFERENCES\n"`.
- **Strategy B:** `[1] <Capital-letter>` anchor with `[2]` nearby.
- **Strategy C:** First consecutive `[N], [N+1], [N+2]` sequence.

### `split_reference_entries` — dehyphenation
Adds `re.sub(r"-\s*\n\s*", "", text)` before splitting on `\n[N]` boundaries.

### `_trim_after_biography`
Removes trailing biography/footer text matching patterns like `"received the B.S."`,
`"is currently"`, `"Authorized licensed use"`.

## 5. Pipeline Results After Patch

| Metric | Before | After |
|---|---:|---:|
| Bibliography entries | 0 | **43** |
| Mapped citations | 0 | **43** |
| Citation roles | 127 | 127 |
| History tree nodes | ~0 useful | **49** |
| History tree edges | 0 | 6 |

## 6. Tests

```
python3 -m compileall src -q       → COMPILE OK
python3 -m pytest tests/test_bibliography_mapper.py -v  → 35 passed
python3 -m pytest -q               → 166 passed, 0 failures
```

## 7. Result

**PASS** — Full suite 166 passed. `my_paper.pdf` (DeepReceiver, 61 references in PDF, 43 reliably
extractable) now yields 43 bibliography entries with correct IEEE curly-quote title extraction.

## 8. Next Step

**Step 12 — Baseline Graph Builder**

The bibliography mapper now robustly handles split-heading PDFs via raw_text fallback.
The history tree for `my_paper.pdf` has 49 nodes representing the paper's intellectual lineage.
Proceed to Step 12 to build the Baseline Graph (competitor/metric/benchmark classification).
