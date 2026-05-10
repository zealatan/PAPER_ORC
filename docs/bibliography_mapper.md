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

## Parsing Heuristics

**Entry splitting** (`split_reference_entries`): The references text is split at lines beginning with `[N]`. Continuation lines (indented with whitespace) stay attached to the preceding entry.

**Title extraction**: Quoted titles (`"..."`) are extracted first. If absent, the text between the authors and the venue is used as the title. The author–title boundary is the first `. ` after a word of 3+ characters (to skip initials like `T.`, `M.`).

**Year extraction**: The last 4-digit number in range 1900–2099 in the entry text.

**Author extraction**: The text before the title boundary, split on ` and ` and `,`.

## Mapping Logic

`map_mentions_to_bibliography` matches each unique `CitationMention.citation_id` against the `BibliographyEntry.citation_id` lookup table. Only citation IDs that appear in both mentions and entries are included in the mapping. Missing IDs are silently skipped — this avoids failures when a citation marker in the body has no corresponding bibliography entry (e.g., due to PDF extraction gaps).

## Synthetic Fixture

Running on `examples/sample_parsed_paper.json` produces:

- **13 bibliography entries** (ref_1 through ref_13)
- **13 mapped citation IDs** (all mentions in the synthetic fixture map successfully)
- All entries have years extracted; most have titles and authors

## Real Paper Smoke Test

Running on `reports/step_outputs/step_03/real_paper_parsed_snapshot.json` (RTLFixer PDF):

- **21 bibliography entries** detected
- **21 citation IDs mapped** from the real paper's citation mentions

## Limitations

- Title extraction may include venue fragments when titles and venues share similar structure
- Author parsing splits on ` and ` and `,`, which can produce segments rather than full author names for complex author lists
- PDF text extraction can corrupt or merge reference entries, reducing detection accuracy
- Author-year bibliography style (APA, Chicago) is not supported in the MVP
