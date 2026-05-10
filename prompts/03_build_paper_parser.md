# Step 03 — Build Paper Parser

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/03_build_paper_parser.md

If the file already exists, overwrite it with this full prompt.

This project rule is mandatory:

Every Claude Code step prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Implement the PaperNav paper parser.

The parser must convert a paper text file or PDF file into a ParsedPaper object.

This is the first real functional step of PaperNav.

The parser must support:

1. Synthetic fixture:
   examples/sample_paper.txt

2. Real paper smoke fixture:
   papers/real/rtlfixer_2311_16543.pdf

The parser should split papers into labeled sections and produce JSON snapshots for downstream steps.

Do not implement citation extraction, bibliography mapping, citation role classification, graph generation, or importance agents in this step.

This step only parses papers into structured sections.

---

## Project Context

PaperNav is a section-aware paper intelligence agent.

Core pipeline:

Paper
  -> Section Parsing
  -> Citation Extraction
  -> Bibliography Mapping
  -> Citation Role Classification
  -> History Tree + Baseline Graph
  -> Importance Report

This Step 03 implements only:

Paper file
  -> parser.py
  -> ParsedPaper
  -> parsed_paper.json

---

## Current Inputs

Synthetic fixture:

examples/sample_paper.txt

Expected synthetic sections:

- Introduction
- Related Work
- Experiment
- Results
- Discussion
- References

Expected metadata:

- citation markers: 41
- bibliography entries: 13

Real paper fixture:

papers/real/rtlfixer_2311_16543.pdf

Metadata:

papers/real/rtlfixer_2311_16543.metadata.json

The real PDF smoke test should not require perfect parsing. It only needs to confirm that text extraction works and that major sections can be detected if present.

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
examples/sample_paper.txt
examples/sample_expected_sections.json
papers/real/rtlfixer_2311_16543.pdf
papers/real/rtlfixer_2311_16543.metadata.json

Do not modify Step 01/02/02c outputs unless absolutely necessary.

Do not implement citation extraction logic in this step.

Do not implement bibliography mapping logic in this step.

---

## Files to Create or Modify

Modify:

src/papernav/parser.py

Create or update:

tests/test_parser.py
docs/parser.md
examples/sample_parsed_paper.json
reports/step_outputs/step_03/parsed_sections.md
reports/step_outputs/step_03/section_split_diagram.mmd
reports/step_outputs/step_03/parsed_paper_snapshot.json
reports/step_outputs/step_03/real_paper_parse_summary.md
reports/step_outputs/step_03/report.md

Optional if useful:

reports/step_outputs/step_03/real_paper_parsed_snapshot.json

---

## Implementation Requirements

Use the existing models from:

src/papernav/models.py

Use ParsedPaper and PaperSection.

The parser must provide these public functions:

parse_text(text: str, paper_id: str | None = None, metadata: dict | None = None) -> ParsedPaper

parse_file(path: str, paper_id: str | None = None) -> ParsedPaper

parse_pdf(path: str, paper_id: str | None = None) -> ParsedPaper

save_parsed_paper(parsed: ParsedPaper, output_path: str) -> None

Use pypdf for PDF text extraction.

For parse_file:

- If file extension is .txt, call parse_text.
- If file extension is .pdf, call parse_pdf.
- Otherwise raise ValueError.

For parse_pdf:

- Extract text from all pages with pypdf.
- Preserve raw extracted text.
- Then call parse_text on the extracted text.
- Add metadata fields:
  - source_file
  - source_type = pdf
  - page_count if available

For parse_text:

- Preserve raw_text.
- Try to infer title from the first non-empty line.
- Try to extract abstract if an Abstract section exists.
- Split sections using section headings.

---

## Section Detection Requirements

Support these heading patterns:

Abstract
1. Introduction
I. Introduction
Introduction

2. Related Work
II. Related Work
Related Work

3. Background
Background

4. Method
Method
Methodology
Approach
Proposed Method

5. Experiment
Experiment
Experiments
Experimental Setup
Evaluation

6. Results
Results

7. Discussion
Discussion

8. Conclusion
Conclusion

References
Bibliography

Normalize section names to lowercase snake-style keys:

abstract
introduction
related_work
background
method
experiment
results
discussion
conclusion
references

For the synthetic fixture, the parser must detect at least:

introduction
related_work
experiment
results
discussion
references

If Abstract does not exist in the sample fixture, abstract can be None.

The parser should be heuristic and robust, not perfect.

---

## ParsedPaper Requirements

The returned ParsedPaper must include:

paper_id
title
authors
abstract
sections
section_objects
raw_text
metadata

sections must be a dict where keys are normalized section names.

section_objects must be a list of PaperSection objects.

Each PaperSection should include:

name
title
text
start_char
end_char

Character offsets can be approximate but should be present when easy to compute.

---

## Synthetic Fixture Output

Parse:

examples/sample_paper.txt

Save output to:

examples/sample_parsed_paper.json

Also save the same parsed object or a compact version to:

reports/step_outputs/step_03/parsed_paper_snapshot.json

The JSON must be valid.

---

## Real Paper Smoke Test

If this file exists:

papers/real/rtlfixer_2311_16543.pdf

Then parse it with parse_pdf.

Create:

reports/step_outputs/step_03/real_paper_parse_summary.md

The summary must include:

- local PDF path
- whether PDF existed
- whether text extraction succeeded
- extracted raw text length
- detected title if available
- detected section keys
- whether references section was detected
- note that this is a smoke test, not full semantic validation

If the PDF is missing, do not fail. Create the same summary file and mark PDF status as missing.

Optional:

Create reports/step_outputs/step_03/real_paper_parsed_snapshot.json if parsing succeeds.

Do not require exact section count for the real paper.

---

## Intermediate Visualization Requirements

Create:

reports/step_outputs/step_03/parsed_sections.md

It must include a Markdown table:

| Section Key | Original Title | Character Count | Has Citations | Preview |
|---|---|---:|---|---|

Use the synthetic fixture parsed output.

Has Citations should be Yes if the section contains numeric citation markers like [1].

Preview should be the first 120 characters, cleaned into one line.

Create:

reports/step_outputs/step_03/section_split_diagram.mmd

It must be a valid Mermaid flowchart showing:

sample_paper.txt
  -> Paper Parser
  -> ParsedPaper
  -> section nodes:
     introduction
     related_work
     experiment
     results
     discussion
     references

Also show that ParsedPaper JSON is saved.

Create:

reports/step_outputs/step_03/parsed_paper_snapshot.json

This must be valid JSON.

---

## docs/parser.md Requirements

Create or update:

docs/parser.md

Include:

# Paper Parser

## Purpose

Explain that this parser converts text/PDF papers into ParsedPaper.

## Inputs

- text file
- PDF file

## Inputs

## Outputs

- ParsedPaper
- parsed paper JSON

## Section Detection

Explain the supported section headings.

## Synthetic Fixture

Explain that examples/sample_paper.txt is the main deterministic fixture.

## Real Paper Smoke Test

Explain that RTLFixer PDF is used as a real paper smoke test.

## Limitations

Mention:

- heuristic section splitting
- imperfect PDF extraction
- no citation extraction yet
- no bibliography mapping yet

---

## Test Requirements

Create or update:

tests/test_parser.py

Tests must cover:

1. parse_text returns ParsedPaper
2. parse_file works with examples/sample_paper.txt
3. synthetic fixture detects introduction
4. synthetic fixture detects related_work
5. synthetic fixture detects experiment
6. synthetic fixture detects results
7. synthetic fixture detects discussion
8. synthetic fixture detects references
9. parsed section text is non-empty
10. raw_text is preserved
11. save_parsed_paper writes valid JSON
12. examples/sample_parsed_paper.json can be generated
13. parse_file rejects unsupported extension
14. parse_pdf smoke test:
    - If papers/real/rtlfixer_2311_16543.pdf exists, parse_pdf returns ParsedPaper with non-empty raw_text.
    - If missing, skip the test with pytest.skip.

Also test that reports/step_outputs/step_03 files can be created by a helper or direct code if you implement a small function for step output generation.

Do not make tests brittle for the real PDF. Only require text extraction and a ParsedPaper object.

---

## Optional Helper Function

You may implement:

generate_step03_outputs(
    sample_path: str = "examples/sample_paper.txt",
    output_dir: str = "reports/step_outputs/step_03"
) -> None

This function can create:

- parsed_sections.md
- section_split_diagram.mmd
- parsed_paper_snapshot.json
- real_paper_parse_summary.md

If implemented, test it lightly.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_parser.py -v
python3 -m pytest -q
python3 -m json.tool examples/sample_parsed_paper.json > /tmp/sample_parsed_paper_check.json
python3 -m json.tool reports/step_outputs/step_03/parsed_paper_snapshot.json > /tmp/parsed_paper_snapshot_check.json
ls -l reports/step_outputs/step_03/

---

## Final Report Format

At the end, report exactly:

# Step 03 — Paper Parser — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/03_build_paper_parser.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files.

## 4. Parser Functions Implemented

List:

- parse_text
- parse_file
- parse_pdf
- save_parsed_paper

and any optional helper functions.

## 5. Synthetic Fixture Parse Result

Report:

- detected title
- detected section keys
- section count
- raw text length
- output JSON path

## 6. Real Paper Smoke Result

Report:

- PDF status: present or missing
- parse status: success, skipped, or failed
- detected section keys if parsed
- raw text length if parsed

## 7. Visualization Outputs

List files under:

reports/step_outputs/step_03/

## 8. Tests Run

List validation commands.

## 9. Result

PASS or FAIL.

## 10. Notes

Mention limitations.

## 11. Next Step

Recommend:

Step 04 — Citation Extractor

---

## Success Criteria

This step is complete only when:

- prompts/03_build_paper_parser.md exists and contains this full prompt
- src/papernav/parser.py implements parse_text
- src/papernav/parser.py implements parse_file
- src/papernav/parser.py implements parse_pdf
- src/papernav/parser.py implements save_parsed_paper
- tests/test_parser.py exists
- docs/parser.md exists
- examples/sample_parsed_paper.json exists
- reports/step_outputs/step_03/parsed_sections.md exists
- reports/step_outputs/step_03/section_split_diagram.mmd exists
- reports/step_outputs/step_03/parsed_paper_snapshot.json exists
- reports/step_outputs/step_03/real_paper_parse_summary.md exists
- examples/sample_parsed_paper.json is valid JSON
- parsed_paper_snapshot.json is valid JSON
- synthetic fixture sections are detected
- real PDF smoke test is handled as present or skipped if missing
- python3 -m compileall src passes
- python3 -m pytest tests/test_parser.py -v passes
- python3 -m pytest -q passes
