# Step 05 — Bibliography Mapper

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/05_build_bibliography_mapper.md

If the file already exists, overwrite it with this full prompt.

Every Claude Code prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Implement the PaperNav Bibliography Mapper.

This step parses the References section of a ParsedPaper and maps citation IDs such as ref_1, ref_2, ..., ref_N to full bibliography entries.

Input from previous steps:

- examples/sample_parsed_paper.json
- examples/sample_citation_mentions.json
- reports/step_outputs/step_03/real_paper_parsed_snapshot.json
- reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json

Output of this step:

- BibliographyEntry list
- citation_id -> BibliographyEntry mapping
- bibliography_entries.json
- citation_to_bibliography_map.json
- Markdown / Mermaid visualization outputs

Do not implement citation role classification in this step.
Do not implement History Tree or Baseline Graph in this step.

This step only parses bibliography entries and maps them to citation mentions.

---

## Current Pipeline

Paper
  -> Step 03 Paper Parser
  -> ParsedPaper
  -> Step 04 Citation Extractor
  -> CitationMention list
  -> Step 05 Bibliography Mapper
  -> BibliographyEntry list
  -> citation_id-to-entry mapping

Later steps will use this output:

- Step 06 Citation Role Classifier
- Step 10 History Tree Builder
- Step 12 Baseline Graph Builder
- Step 15 Topic Relevance Agent

---

## Do Not Modify

Do not overwrite or delete:

README.md
assets/
prompts/00_bootstrap_repository.md
prompts/01_define_common_models.md
prompts/02_add_sample_paper_fixture.md
prompts/02b_complete_sample_fixture_docs_and_visual_outputs.md
prompts/02c_add_real_paper_smoke_fixture.md
prompts/03_build_paper_parser.md
prompts/04_build_citation_extractor.md
examples/sample_paper.txt
examples/sample_parsed_paper.json
examples/sample_citation_mentions.json
papers/real/rtlfixer_2311_16543.pdf
papers/real/rtlfixer_2311_16543.metadata.json

Do not implement citation role classification.
Do not implement graph building.

---

## Files to Create or Modify

Modify:

src/papernav/citation/bibliography.py

Create or update:

tests/test_bibliography_mapper.py
docs/bibliography_mapper.md

Create:

examples/sample_bibliography_entries.json
examples/sample_citation_to_bibliography_map.json
reports/step_outputs/step_05/bibliography_mapping_table.md
reports/step_outputs/step_05/citation_to_reference_map.mmd
reports/step_outputs/step_05/bibliography_entries_snapshot.json
reports/step_outputs/step_05/citation_to_bibliography_map_snapshot.json
reports/step_outputs/step_05/real_paper_bibliography_summary.md
reports/step_outputs/step_05/report.md

Optional:

reports/step_outputs/step_05/real_paper_bibliography_entries_snapshot.json
reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json

---

## Required Public Functions

Implement these functions in:

src/papernav/citation/bibliography.py

Functions:

split_reference_entries(references_text: str) -> list[str]

parse_reference_entry(raw_entry: str) -> BibliographyEntry

extract_bibliography_entries_from_text(references_text: str) -> list[BibliographyEntry]

extract_bibliography_entries(parsed_paper: ParsedPaper) -> list[BibliographyEntry]

map_mentions_to_bibliography(
    mentions: list[CitationMention],
    entries: list[BibliographyEntry]
) -> dict[str, BibliographyEntry]

save_bibliography_entries(
    entries: list[BibliographyEntry],
    output_path: str
) -> None

save_citation_to_bibliography_map(
    mapping: dict[str, BibliographyEntry],
    output_path: str
) -> None

generate_step05_outputs(
    parsed_paper_path: str = "examples/sample_parsed_paper.json",
    citation_mentions_path: str = "examples/sample_citation_mentions.json",
    output_dir: str = "reports/step_outputs/step_05"
) -> None

Use these existing models/functions:

- ParsedPaper
- CitationMention
- BibliographyEntry
- normalize_citation_id

---

## Reference Parsing Requirements

Support numeric reference formats:

[1] A. Author, "Paper Title", Conference, 2020.
[2] B. Author and C. Author, "Another Paper", Journal, 2021.
[3] A. Author, Paper Title without quotes, arXiv preprint, 2023.

Also support simple multi-line references:

[4] A. Author, "Long Paper Title",
    Conference Name, 2024.

For MVP, heuristics are acceptable.

Each BibliographyEntry must include:

- citation_id
- raw_text
- title if extractable
- authors if extractable
- year if extractable
- venue if extractable
- metadata

Most important fields:

- citation_id
- raw_text
- title
- year

---

## Citation ID Rules

Use normalize_citation_id.

Examples:

[1] -> ref_1
1 -> ref_1
ref_1 -> ref_1

All bibliography entries must use citation_id = ref_N format.

---

## Extraction Heuristics

Title extraction:

1. Prefer quoted title:
   "Paper Title"

2. If no quoted title exists, infer title heuristically.

3. If title extraction fails, set title = None.

Year extraction:

- Extract the last valid year between 1900 and 2099 from the reference entry.
- If no year is found, set year = None.

Author extraction:

- Try to extract text before the title or before the first quoted string.
- If uncertain, store the raw author segment as one string in authors.
- Do not fail if author parsing is imperfect.

---

## Mapping Requirements

map_mentions_to_bibliography must:

- accept citation mentions
- accept bibliography entries
- return dict[str, BibliographyEntry]
- include only citation IDs that have matching bibliography entries
- ignore missing citation IDs without failure
- allow reference-section anchors and body mentions

For the synthetic fixture:

- bibliography entry count should be 13
- mapping should include ref_1 through ref_13

---

## Real Paper Smoke Test

If this file exists:

reports/step_outputs/step_03/real_paper_parsed_snapshot.json

Then parse its references section.

If this file exists:

reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json

Then map real citation mentions to real bibliography entries.

Create:

reports/step_outputs/step_05/real_paper_bibliography_summary.md

The summary must include:

- whether real parsed snapshot exists
- whether references section was detected
- bibliography entry count
- mapped citation ID count
- first 10 bibliography entries by citation_id
- note that real PDF extraction and reference parsing are heuristic

Do not fail the entire step if real paper bibliography parsing is imperfect.

---

## Intermediate Visualization Outputs

Create:

reports/step_outputs/step_05/bibliography_mapping_table.md

It must include:

# Bibliography Mapping Table

## Summary

| Metric | Value |
|---|---:|

Metrics:

- Bibliography entries
- Citation IDs in mentions
- Mapped citation IDs
- Unmapped citation IDs

## Bibliography Entries

| Citation ID | Title | Year | Authors | Raw Preview |
|---|---|---:|---|---|

## Citation to Bibliography Mapping

| Citation ID | Mention Count | Title | Year |
|---|---:|---|---:|

Create:

reports/step_outputs/step_05/citation_to_reference_map.mmd

Use this Mermaid diagram:

flowchart TD
    A[Citation Mentions] --> B[Unique Citation IDs]
    C[References Section] --> D[Bibliography Entries]
    B --> E[Citation ID Matching]
    D --> E
    E --> F[citation_to_bibliography_map.json]
    F --> G[Step 06 Citation Role Classifier]
    E --> R1[ref_1]
    E --> R5[ref_5]
    E --> R13[ref_13]

Create valid JSON files:

reports/step_outputs/step_05/bibliography_entries_snapshot.json
reports/step_outputs/step_05/citation_to_bibliography_map_snapshot.json

Also create equivalent example outputs:

examples/sample_bibliography_entries.json
examples/sample_citation_to_bibliography_map.json

---

## Documentation Requirements

Create or update:

docs/bibliography_mapper.md

Include:

# Bibliography Mapper

## Purpose

Explain that this module parses the References section and maps citation IDs to full bibliography entries.

## Inputs

- ParsedPaper
- CitationMention list
- References section text

## Outputs

- BibliographyEntry list
- citation_id-to-entry mapping
- bibliography_entries.json
- citation_to_bibliography_map.json

## Supported Reference Styles

Explain numeric references:

[1] ...
[2] ...

Mention basic multi-line support.

## Parsing Heuristics

Explain:

- entry splitting
- title extraction
- year extraction
- author extraction

## Mapping Logic

Explain that CitationMention citation_id values are matched to BibliographyEntry citation_id values.

## Synthetic Fixture

Explain expected 13 entries.

## Real Paper Smoke Test

Explain heuristic behavior on RTLFixer parsed snapshot.

## Limitations

Mention:

- imperfect title extraction
- imperfect author extraction
- PDF text extraction can break references
- author-year bibliography style is not the MVP focus

---

## Test Requirements

Create or update:

tests/test_bibliography_mapper.py

Tests must cover:

1. split_reference_entries detects [1] and [2]
2. split_reference_entries handles multi-line references
3. parse_reference_entry extracts citation_id ref_1
4. parse_reference_entry extracts quoted title
5. parse_reference_entry extracts year
6. parse_reference_entry preserves raw_text
7. extract_bibliography_entries_from_text returns BibliographyEntry list
8. extract_bibliography_entries works on synthetic ParsedPaper
9. synthetic bibliography count is 13
10. map_mentions_to_bibliography maps ref_1 through ref_13
11. missing citation ID is ignored without failure
12. save_bibliography_entries writes valid JSON
13. save_citation_to_bibliography_map writes valid JSON
14. generate_step05_outputs creates required visualization files
15. real paper bibliography smoke test:
    - If real parsed snapshot exists, extraction runs and returns a list
    - If missing, skip with pytest.skip

Use pytest.

Do not make real paper exact bibliography counts brittle.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_bibliography_mapper.py -v
python3 -m pytest -q
python3 -m json.tool examples/sample_bibliography_entries.json > /tmp/sample_bibliography_entries_check.json
python3 -m json.tool examples/sample_citation_to_bibliography_map.json > /tmp/sample_citation_to_bibliography_map_check.json
python3 -m json.tool reports/step_outputs/step_05/bibliography_entries_snapshot.json > /tmp/bibliography_entries_snapshot_check.json
python3 -m json.tool reports/step_outputs/step_05/citation_to_bibliography_map_snapshot.json > /tmp/citation_to_bibliography_map_snapshot_check.json
ls -l reports/step_outputs/step_05/

---

## Final Report Format

At the end, report exactly:

# Step 05 — Bibliography Mapper — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/05_build_bibliography_mapper.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files.

## 4. Bibliography Functions Implemented

List:

- split_reference_entries
- parse_reference_entry
- extract_bibliography_entries_from_text
- extract_bibliography_entries
- map_mentions_to_bibliography
- save_bibliography_entries
- save_citation_to_bibliography_map
- generate_step05_outputs

## 5. Synthetic Fixture Mapping Result

Report:

- bibliography entry count
- mapped citation ID count
- unmapped citation ID count
- first 5 mapped entries
- output JSON paths

## 6. Real Paper Smoke Result

Report:

- real parsed snapshot status
- references section status
- bibliography entry count if available
- mapped citation ID count if available

## 7. Visualization Outputs

List files under:

reports/step_outputs/step_05/

## 8. Tests Run

List validation commands.

## 9. Result

PASS or FAIL.

## 10. Notes

Mention limitations.

## 11. Next Step

Recommend:

Step 06 — Citation Role Classifier

---

## Success Criteria

This step is complete only when:

- prompts/05_build_bibliography_mapper.md exists and contains this full prompt
- src/papernav/citation/bibliography.py implements split_reference_entries
- src/papernav/citation/bibliography.py implements parse_reference_entry
- src/papernav/citation/bibliography.py implements extract_bibliography_entries_from_text
- src/papernav/citation/bibliography.py implements extract_bibliography_entries
- src/papernav/citation/bibliography.py implements map_mentions_to_bibliography
- src/papernav/citation/bibliography.py implements save_bibliography_entries
- src/papernav/citation/bibliography.py implements save_citation_to_bibliography_map
- src/papernav/citation/bibliography.py implements generate_step05_outputs
- tests/test_bibliography_mapper.py exists
- docs/bibliography_mapper.md exists
- examples/sample_bibliography_entries.json exists
- examples/sample_citation_to_bibliography_map.json exists
- reports/step_outputs/step_05/bibliography_mapping_table.md exists
- reports/step_outputs/step_05/citation_to_reference_map.mmd exists
- reports/step_outputs/step_05/bibliography_entries_snapshot.json exists
- reports/step_outputs/step_05/citation_to_bibliography_map_snapshot.json exists
- reports/step_outputs/step_05/real_paper_bibliography_summary.md exists
- all JSON outputs are valid
- synthetic fixture bibliography count is 13
- synthetic mapping includes ref_1 through ref_13
- real paper smoke extraction is handled as success or skipped
- python3 -m compileall src passes
- python3 -m pytest tests/test_bibliography_mapper.py -v passes
- python3 -m pytest -q passes
