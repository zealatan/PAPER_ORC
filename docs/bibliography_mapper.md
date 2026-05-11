# Bibliography Mapper

## Purpose

`src/papernav/citation/bibliography.py` parses the References section of a `ParsedPaper` and maps citation IDs (e.g., `ref_1`, `ref_5`) to full `BibliographyEntry` objects. This bridges the gap between raw citation markers extracted in Step 04 and structured bibliographic metadata needed by downstream steps.

## Inputs

- `ParsedPaper` object (references section text)
- `list[CitationMention]` (from Step 04 extractor)
- References section text (plain string)

## Outputs

- `list[BibliographyEntry]` — one entry per detected reference
- `dict[str, BibliographyEntry]` — citation_id to entry mapping
- `bibliography_entries.json`
- `citation_to_bibliography_map.json`

## Supported Reference Styles

Numeric reference format (IEEE/ACM style):

```
[1] A. Author. Paper Title. Venue, Year.
[2] B. Author and C. Author. Another Title. Journal, Year.
[3] A. Author. "Quoted Title". Conference, Year.
```

Multi-line entries are supported when continuation lines are indented:

```
[4] A. Author. Long Paper Title Spanning
    Multiple Lines. Venue, Year.
```

Author-year citation styles are not the MVP focus.

## Best-Effort References Extraction (Step 05b)

`extract_references_text_best_effort(parsed_paper)` is the entry point used by
`extract_bibliography_entries`. It handles PDFs where the REFERENCES heading is split by
the PDF extractor (e.g., `"R\nEFERENCES"` in IEEE multi-column layouts):

1. Returns `sections["references"]` (or `"bibliography"`) when ≥ 200 chars.
2. Falls back to scanning `raw_text` via `_find_reference_block_in_raw_text`:
   - **Strategy A:** Matches `REFERENCES` / `R\nEFERENCES` heading.
   - **Strategy B:** `[1] <Capital>` anchor with `[2]` confirmed nearby.
   - **Strategy C:** First consecutive `[N][N+1][N+2]` sequence.
3. `_trim_after_biography` removes trailing author biography / legal-footer text.

## Parsing Heuristics

**Entry splitting** (`split_reference_entries`): Hyphenated line-breaks (`sys-\ntem`) are
rejoined before splitting. The text is then split at lines beginning with `[N]`.

**Title extraction** (Step 10b): IEEE references use Unicode curly quotes `"…"` (U+201C/201D).
`_QUOTED_TITLE_RE` matches all common quote variants (ASCII `"`, Unicode `"`, `"`, etc.).
Garbage titles (author fragments, venue abbreviations shorter than 10 chars) are rejected by
`_BAD_TITLE_RE`. The `metadata["title_extraction_method"]` field records whether the title was
extracted via `"quoted_title"`, `"fallback_heuristic"`, or `"failed"`.

**Year extraction**: The last 4-digit number in range 1900–2099 in the entry text.

**Author extraction**: The text before the title boundary, split on ` and ` and `,`.

## Mapping Logic

`map_mentions_to_bibliography` matches each unique `CitationMention.citation_id` against the `BibliographyEntry.citation_id` lookup table. Only citation IDs that appear in both mentions and entries are included in the mapping. Missing IDs are silently skipped — this avoids failures when a citation marker in the body has no corresponding bibliography entry (e.g., due to PDF extraction gaps).

## Synthetic Fixture

Running on `examples/sample_parsed_paper.json` produces:

- **13 bibliography entries** (ref_1 through ref_13)
- **13 mapped citation IDs** (all mentions in the synthetic fixture map successfully)
- All entries have years extracted; most have titles and authors

## Real Paper Results

| Paper | Entries | Mapped | Source |
|---|---:|---:|---|
| RTLFixer (Step 05 snapshot) | 21 | 21 | sections["references"] |
| my_paper.pdf / DeepReceiver (Step 05b) | 43 | 43 | raw_text fallback |

All 43 DeepReceiver entries use `quoted_title` extraction (IEEE curly quotes working correctly).

## Limitations

- Title extraction may include venue fragments when titles and venues share similar structure
- Author parsing splits on ` and ` and `,`, which can produce segments rather than full author names for complex author lists
- PDF text extraction can corrupt or merge reference entries, reducing detection accuracy
- Author-year bibliography style (APA, Chicago) is not supported in the MVP
- Raw-text fallback may miss references if the PDF has no consistent `[N]` markers
