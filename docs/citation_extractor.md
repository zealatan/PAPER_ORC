# Citation Extractor

## Purpose

`src/papernav/citation/extractor.py` extracts numeric citation mentions from `ParsedPaper` sections. Each mention is returned as a `CitationMention` object containing the citation ID, the raw marker text, the section name, the surrounding sentence, and a context window — all of which are needed by the downstream role classifier.

## Inputs

- `ParsedPaper` object (from Step 03 parser)
- `parsed_paper.json` file (loaded via `load_parsed_paper`)

## Outputs

- `list[CitationMention]`
- `citation_mentions.json` (via `save_citation_mentions`)

## Supported Citation Styles

| Pattern | Example | Produces |
|---|---|---|
| Single | `[1]` | ref_1 |
| Grouped (spaces) | `[1, 2]` | ref_1, ref_2 |
| Grouped (compact) | `[1,2,3]` | ref_1, ref_2, ref_3 |
| Intra-bracket range | `[1-3]` | ref_1, ref_2, ref_3 |
| En-dash range | `[1]–[3]` | ref_1, ref_2, ref_3 |
| Inter-bracket range | `[1]-[3]` | ref_1, ref_2, ref_3 |
| Mixed | `[1, 3-5]` | ref_1, ref_3, ref_4, ref_5 |

Author-year citations (e.g., Smith et al., 2020) are not supported in the MVP.

## Sentence Context

For each citation marker found, `_extract_sentence` scans backward and forward from the marker position to find the enclosing sentence. Sentence boundaries are detected by `.!?` followed by whitespace, or double newlines (paragraph breaks). The result is normalised to a single line (whitespace collapsed).

`context_window` captures approximately 200 characters centred on the citation marker for use as additional context in role classification.

## Reference Section Handling

Citations in the References section (anchor markers `[1] Author...`) are extracted with `section_name = "references"`. They are included in the full `CitationMention` list but reported separately in visualisation outputs. Step 05 uses the References section text for bibliography mapping rather than these anchor-based `CitationMention` objects.

## Synthetic Fixture

When run on `examples/sample_parsed_paper.json`:

- **Total mentions:** 41 (28 body + 13 reference anchors)
- **Body sections with citations:** introduction (7), related_work (6), method (1), experiment (9), results (3), discussion (2)
- **Unique citation IDs:** ref_1 through ref_13

## Real Paper Smoke Test

When run on `reports/step_outputs/step_03/real_paper_parsed_snapshot.json` (RTLFixer PDF):

- **Total mentions:** 64 (approximate; depends on pypdf extraction quality)
- **Sections with citations:** introduction, background, experiment, references

## Limitations

- Numeric citations only (MVP scope)
- Author-year citations not supported
- Sentence splitting is heuristic — may capture multi-sentence fragments or partial sentences for wrapped PDF text
- PDF text extraction quality directly affects citation detection completeness
