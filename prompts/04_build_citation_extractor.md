# Step 04 — Citation Extractor

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/04_build_citation_extractor.md

If the file already exists, overwrite it with this full prompt.

This project rule is mandatory:

Every Claude Code step prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Implement the PaperNav Citation Extractor.

This step takes a ParsedPaper object from Step 03 and extracts citation mentions from each section.

The output of this step is a list of CitationMention objects and section-level citation visualization outputs.

This is the first step where PaperNav begins to understand references inside a paper.

Do not implement bibliography mapping in this step.
Do not implement citation role classification in this step.
Do not implement History Tree or Baseline Graph in this step.

This step only extracts citation markers and their sentence-level context.

---

## Project Context

PaperNav is a section-aware paper intelligence agent.

Current pipeline status:

Paper
  -> Step 03 Paper Parser
  -> ParsedPaper

This Step 04 implements:

ParsedPaper
  -> Citation Extractor
  -> CitationMention list
  -> citation_mentions.json
  -> section-level citation extraction visualization

Later steps will use this output:

Step 05 Bibliography Mapper
Step 06 Citation Role Classifier
Step 10 History Tree Builder
Step 12 Baseline Graph Builder

---

## Current Inputs

Synthetic parsed paper:

examples/sample_paper.txt
examples/sample_parsed_paper.json

Real paper smoke fixture:

papers/real/rtlfixer_2311_16543.pdf
reports/step_outputs/step_03/real_paper_parsed_snapshot.json

The synthetic fixture has:

- 41 numeric citation markers total
- 13 bibliography entries
- body citations in Introduction, Related Work, Experiment, Results, and Discussion
- reference anchor markers [1] through [13] in References

For Step 04, extract citation mentions from sections, including References if present, but clearly mark their section_name.

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
examples/sample_paper.txt
examples/sample_expected_sections.json
examples/sample_parsed_paper.json
papers/real/rtlfixer_2311_16543.pdf
papers/real/rtlfixer_2311_16543.metadata.json

Do not implement bibliography mapping logic in this step.

Do not implement citation role classification logic in this step.

---

## Files to Create or Modify

Modify:

src/papernav/citation/extractor.py

Create or update:

tests/test_citation_extractor.py
docs/citation_extractor.md

Create:

examples/sample_citation_mentions.json
reports/step_outputs/step_04/citation_extraction_table.md
reports/step_outputs/step_04/citation_extraction_flow.mmd
reports/step_outputs/step_04/citation_mentions_snapshot.json
reports/step_outputs/step_04/real_paper_citation_summary.md
reports/step_outputs/step_04/report.md

Optional if useful:

reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json

---

## Implementation Requirements

Use existing models from:

src/papernav/models.py

Use:

ParsedPaper
CitationMention
normalize_citation_id

The extractor must provide these public functions:

extract_citations_from_text(
    text: str,
    section_name: str,
    section_offset: int | None = None
) -> list[CitationMention]

extract_citations(parsed_paper: ParsedPaper) -> list[CitationMention]

save_citation_mentions(
    mentions: list[CitationMention],
    output_path: str
) -> None

generate_step04_outputs(
    parsed_paper_path: str = "examples/sample_parsed_paper.json",
    output_dir: str = "reports/step_outputs/step_04"
) -> None

---

## Citation Pattern Requirements

Support numeric citation styles:

[1]
[1, 2]
[1,2,3]
[1, 2, 3]
[1]-[3]
[1–3]
[1-3]
[1, 3-5]

For ranges:

[1]-[3] should produce ref_1, ref_2, ref_3
[1–3] should produce ref_1, ref_2, ref_3
[1, 3-5] should produce ref_1, ref_3, ref_4, ref_5

For grouped citations:

[1, 2] should produce two CitationMention objects, one for ref_1 and one for ref_2.

Each CitationMention must preserve:

- citation_id, e.g. ref_5
- marker, e.g. [5] or [1, 2]
- section_name
- sentence
- context_window
- start_char
- end_char
- role = None

---

## Sentence Context Requirements

For each citation, capture the sentence containing the citation marker.

Heuristic is acceptable.

A sentence can be split by:

.
?
!
newline boundaries

But avoid breaking inside reference entries too aggressively.

context_window should include a short text window around the citation, approximately 200 characters if possible.

start_char and end_char should be approximate offsets relative to the section text if exact offsets are easy.

---

## Duplicate Handling

Do not globally deduplicate citations.

If [5] appears three times in the paper, produce three CitationMention objects.

If [1, 2] appears in one sentence, produce two CitationMention objects sharing the same sentence and marker.

This is important because later role classification depends on section and sentence context.

---

## Reference Section Handling

References section contains anchor markers like:

[1] ...
[2] ...

For Step 04, it is acceptable to extract them too, but they must have:

section_name = "references"

Later Step 05 will use the References section for bibliography mapping.

In reports, separate body citations from reference-section anchor citations.

---

## Synthetic Fixture Expectations

When running on examples/sample_parsed_paper.json:

- total numeric citation mentions should be at least 41 if references are included
- detected sections should include:
  - introduction
  - related_work
  - experiment
  - results
  - discussion
  - references

Create a section-level summary table showing citation counts per section.

Do not make the tests overly brittle if exact count differs slightly due to sentence splitting, but the synthetic fixture should detect numeric citations in body sections and references.

---

## Real Paper Smoke Test

If this file exists:

reports/step_outputs/step_03/real_paper_parsed_snapshot.json

Then load it and run extract_citations.

Create:

reports/step_outputs/step_04/real_paper_citation_summary.md

The summary must include:

- whether real parsed snapshot exists
- total citation mentions extracted
- section-level counts
- top 10 citation IDs by frequency
- note that PDF extraction and citation detection are heuristic

Optional:

Create:

reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json

Do not fail the entire step if real paper citation extraction gives imperfect results, as long as it runs and produces a summary.

---

## Intermediate Visualization Requirements

Create:

reports/step_outputs/step_04/citation_extraction_table.md

It must include:

# Citation Extraction Table

## Summary by Section

| Section | Citation Mention Count | Unique Citation IDs | Example Markers |
|---|---:|---:|---|

## Body Citation Examples

| Section | Citation ID | Marker | Sentence Preview |
|---|---|---|---|

## Reference Anchor Examples

| Citation ID | Marker | Sentence Preview |
|---|---|---|

Create:

reports/step_outputs/step_04/citation_extraction_flow.mmd

It must be a valid Mermaid flowchart.

Use this structure:

flowchart TD
    A[ParsedPaper JSON] --> B[Citation Extractor]
    B --> C[Introduction citations]
    B --> D[Related Work citations]
    B --> E[Experiment citations]
    B --> F[Results citations]
    B --> G[Discussion citations]
    B --> H[Reference anchors]
    C --> I[citation_mentions.json]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J[Step 05 Bibliography Mapper]

Create:

reports/step_outputs/step_04/citation_mentions_snapshot.json

It must be valid JSON.

This file should contain the CitationMention list for the synthetic fixture.

Also create:

examples/sample_citation_mentions.json

with the same or equivalent data.

---

## docs/citation_extractor.md Requirements

Create or update:

docs/citation_extractor.md

Include:

# Citation Extractor

## Purpose

Explain that this module extracts numeric citation mentions from ParsedPaper sections.

## Inputs

- ParsedPaper object
- parsed_paper.json

## Outputs

- list of CitationMention
- citation_mentions.json

## Supported Citation Styles

List:

[1]
[1, 2]
[1]-[3]
[1–3]
[1, 3-5]

## Sentence Context

Explain sentence and context_window extraction.

## Reference Section Handling

Explain that reference anchors are extracted but separated in reports.

## Synthetic Fixture

Explain expected behavior on examples/sample_paper.txt.

## Real Paper Smoke Test

Explain behavior on RTLFixer parsed snapshot.

## Limitations

Mention:

- numeric citations only in MVP
- author-year citations not supported yet
- sentence splitting is heuristic
- PDF extraction quality affects citation detection

---

## Test Requirements

Create or update:

tests/test_citation_extractor.py

Tests must cover:

1. extract_citations_from_text detects single citation [1]
2. detects grouped citations [1, 2]
3. detects compact grouped citations [1,2,3]
4. expands range [1]-[3]
5. expands en-dash range [1–3]
6. expands mixed group [1, 3-5]
7. CitationMention has citation_id normalized as ref_N
8. CitationMention preserves marker
9. CitationMention preserves section_name
10. CitationMention has non-empty sentence
11. CitationMention has context_window
12. extract_citations works on ParsedPaper synthetic fixture
13. synthetic fixture includes citations from introduction
14. synthetic fixture includes citations from experiment
15. synthetic fixture includes citations from references
16. save_citation_mentions writes valid JSON
17. generate_step04_outputs creates required visualization files
18. real paper citation smoke test:
    - If real parsed snapshot exists, extraction runs and returns a list
    - If missing, skip with pytest.skip

Use pytest.

Do not make real paper exact citation counts brittle.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_citation_extractor.py -v
python3 -m pytest -q
python3 -m json.tool examples/sample_citation_mentions.json > /tmp/sample_citation_mentions_check.json
python3 -m json.tool reports/step_outputs/step_04/citation_mentions_snapshot.json > /tmp/citation_mentions_snapshot_check.json
ls -l reports/step_outputs/step_04/

---

## Final Report Format

At the end, report exactly:

# Step 04 — Citation Extractor — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/04_build_citation_extractor.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files.

## 4. Extractor Functions Implemented

List:

- extract_citations_from_text
- extract_citations
- save_citation_mentions
- generate_step04_outputs

## 5. Synthetic Fixture Extraction Result

Report:

- total citation mentions
- body citation mentions
- reference anchor mentions
- section-level counts
- unique citation IDs
- output JSON path

## 6. Real Paper Smoke Result

Report:

- real parsed snapshot status
- extraction status
- total citation mentions if available
- section-level counts if available

## 7. Visualization Outputs

List files under:

reports/step_outputs/step_04/

## 8. Tests Run

List validation commands.

## 9. Result

PASS or FAIL.

## 10. Notes

Mention limitations.

## 11. Next Step

Recommend:

Step 05 — Bibliography Mapper

---

## Success Criteria

This step is complete only when:

- prompts/04_build_citation_extractor.md exists and contains this full prompt
- src/papernav/citation/extractor.py implements extract_citations_from_text
- src/papernav/citation/extractor.py implements extract_citations
- src/papernav/citation/extractor.py implements save_citation_mentions
- src/papernav/citation/extractor.py implements generate_step04_outputs
- tests/test_citation_extractor.py exists
- docs/citation_extractor.md exists
- examples/sample_citation_mentions.json exists
- reports/step_outputs/step_04/citation_extraction_table.md exists
- reports/step_outputs/step_04/citation_extraction_flow.mmd exists
- reports/step_outputs/step_04/citation_mentions_snapshot.json exists
- reports/step_outputs/step_04/real_paper_citation_summary.md exists
- citation_mentions_snapshot.json is valid JSON
- sample_citation_mentions.json is valid JSON
- synthetic fixture citation extraction works
- real paper smoke extraction is handled as success or skipped
- python3 -m compileall src passes
- python3 -m pytest tests/test_citation_extractor.py -v passes
- python3 -m pytest -q passes
