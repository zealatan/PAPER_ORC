# Step 05b — Raw-Text Reference Fallback — Design Summary

## Motivation

Some PDFs (IEEE conference papers, multi-column layouts) have their REFERENCES heading split by
the PDF extractor: `"R\nEFERENCES"` instead of `"REFERENCES"`. The parser's section detector
misses this, leaving `sections["references"]` empty. The bibliography extractor must not silently
return 0 entries when the reference list is present in `raw_text`.

## Implementation

### New public function: `extract_references_text_best_effort(parsed_paper)`

```
1. For each of "references", "bibliography", "reference":
   - If sections[key] has ≥ 200 chars → return it (sections path, fast)
2. If raw_text is non-empty → call _find_reference_block_in_raw_text(raw_text)
3. Return "" if nothing found.
```

### `_find_reference_block_in_raw_text(raw_text)`

Three strategies tried in order:

| Strategy | Pattern | Notes |
|---|---|---|
| A | `_REFS_HEADING_RE` (REFERENCES / R\nEFERENCES) | Follows heading to first `[N]` marker |
| B | `[1] <A-Z>` anchor | Finds ref 1 + verifies ref 2 within 3000 chars |
| C | Consecutive `[N]` triples | Densest sequence as fallback |

After finding the block, `_trim_after_biography()` strips trailing biography/footer text.

### `split_reference_entries` — dehyphenation

Added `re.sub(r"-\s*\n\s*", "", references_text)` before splitting on `\n[N]` boundaries.
Handles PDF line-wrap artifacts like `"sys-\ntem"` → `"system"`.

## Constants

```python
_MIN_REFS_SECTION_LEN = 200   # chars below which a section is treated as missing
```

## New Tests Added (10 tests, all passing)

| Test | What it checks |
|---|---|
| `test_best_effort_uses_sections_references_when_available` | Sections path takes priority |
| `test_best_effort_falls_back_to_raw_text_when_no_section` | raw_text fallback activates |
| `test_best_effort_raw_text_detects_ref1_and_ref2` | Detects low-numbered refs |
| `test_best_effort_raw_text_supports_high_numbered_refs` | Detects ref_44, ref_61 |
| `test_best_effort_raw_text_stops_before_biography` | Biography trimming works |
| `test_split_handles_multiline_ieee_entries` | Multi-line entries not split |
| `test_split_handles_hyphenated_line_breaks` | Dehyphenation before splitting |
| `test_parse_returns_entry_even_if_title_none` | Graceful parse with minimal input |
| `test_parse_extracts_curly_quote_title` | Curly quote still works |
| `test_my_paper_bibliography_count_positive_after_fallback` | Smoke: > 0 entries |
