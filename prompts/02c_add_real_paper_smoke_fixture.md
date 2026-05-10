# Step 02c — Add Real Paper Smoke Fixture

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, overwrite the existing incomplete prompt file with this full prompt:

prompts/02c_add_real_paper_smoke_fixture.md

The current file is incomplete because the previous paste was cut off. Replace it with this full prompt.

After saving this prompt, continue with the implementation.

## Working Directory

/home/zealatan/PAPER_ORC

## Objective

Add a real research paper smoke-test fixture for PaperNav.

This step prepares one real paper for downstream parser, citation extraction, bibliography mapping, citation role classification, history-tree, baseline-graph, and topic-relevance tests.

Do not implement parser logic in this step.

## Target Paper

Use this paper:

Title: RTLFixer: Automatically Fixing RTL Syntax Errors with Large Language Models
arXiv ID: 2311.16543
Expected local PDF path: papers/real/rtlfixer_2311_16543.pdf
PDF URL: https://arxiv.org/pdf/2311.16543

## Required Behavior

1. Create the directory:

papers/real/

2. Check whether this file exists:

papers/real/rtlfixer_2311_16543.pdf

3. If the PDF exists, record status as "present".

4. If the PDF is missing, do not fail. Instead create:

papers/real/MISSING_RTLFIXER_PDF.md

The missing-PDF file must explain how to download the PDF manually:

wget -O papers/real/rtlfixer_2311_16543.pdf https://arxiv.org/pdf/2311.16543

Do not attempt complex downloading logic in this step.

## Files to Create

Create these files:

papers/real/rtlfixer_2311_16543.metadata.json
docs/real_paper_smoke_test.md
reports/step_outputs/step_02c/real_paper_fixture_summary.md
reports/step_outputs/step_02c/real_paper_fixture_flow.mmd

## Metadata JSON Requirements

Create valid JSON at:

papers/real/rtlfixer_2311_16543.metadata.json

Required content:

{
  "paper_id": "rtlfixer_2311_16543",
  "title": "RTLFixer: Automatically Fixing RTL Syntax Errors with Large Language Models",
  "arxiv_id": "2311.16543",
  "source": "arXiv",
  "pdf_url": "https://arxiv.org/pdf/2311.16543",
  "local_pdf": "papers/real/rtlfixer_2311_16543.pdf",
  "expected_domain": "LLM-assisted RTL debugging",
  "expected_history_sections": ["Introduction", "Related Work"],
  "expected_baseline_sections": ["Experiment", "Evaluation", "Results"],
  "expected_use_in_papernav": [
    "real parser smoke test",
    "citation extraction smoke test",
    "bibliography mapping smoke test",
    "citation role classification smoke test",
    "baseline graph candidate",
    "topic relevance test"
  ],
  "pdf_status": "present_or_missing"
}

Set pdf_status to "present" if the local PDF exists. Set it to "missing" if it does not exist.

## docs/real_paper_smoke_test.md Requirements

Create:

docs/real_paper_smoke_test.md

It must include:

# Real Paper Smoke Test

## Target Paper

List title, arXiv ID, URL, and local PDF path.

## Why This Paper

Explain that RTLFixer is useful because it is related to LLM-assisted RTL debugging, syntax repair, Verilog, and hardware design automation.

## How It Will Be Used

Explain that this paper will be used in:

- Step 03 Paper Parser
- Step 04 Citation Extractor
- Step 05 Bibliography Mapper
- Step 06 Citation Role Classifier
- Milestone 2 History Tree and Baseline Graph
- Milestone 3 Topic Relevance Agent

## If PDF Is Missing

Explain this command:

wget -O papers/real/rtlfixer_2311_16543.pdf https://arxiv.org/pdf/2311.16543

## Limitations

Mention that this step only prepares metadata and smoke-test documentation. It does not parse the PDF yet.

## real_paper_fixture_summary.md Requirements

Create:

reports/step_outputs/step_02c/real_paper_fixture_summary.md

Include:

# Real Paper Smoke Fixture

## Status

Show whether the local PDF is present or missing.

## Target Paper

Show title, arXiv ID, URL, and local path.

## Expected Use

List downstream steps.

## Next Parser Test

Explain that Step 03 should parse both examples/sample_paper.txt and this real PDF if available.

## real_paper_fixture_flow.mmd Requirements

Create:

reports/step_outputs/step_02c/real_paper_fixture_flow.mmd

Use this Mermaid flowchart:

flowchart LR
    A[RTLFixer PDF] --> B[Step 03 Paper Parser]
    B --> C[ParsedPaper JSON]
    C --> D[Step 04 Citation Extractor]
    D --> E[Step 05 Bibliography Mapper]
    E --> F[Step 06 Citation Role Classifier]
    F --> G[History Tree + Baseline Graph]
    G --> H[Importance Report]

## Validation Commands

Run these commands:

python3 -m json.tool papers/real/rtlfixer_2311_16543.metadata.json > /tmp/rtlfixer_metadata_check.json
ls -l papers/real/
ls -l reports/step_outputs/step_02c/

If pytest exists, also run:

python3 -m pytest -q

## Final Report Format

At the end, report:

# Step 02c — Real Paper Smoke Fixture — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/02c_add_real_paper_smoke_fixture.md

## 2. Files Created

List created files.

## 3. PDF Status

Say whether papers/real/rtlfixer_2311_16543.pdf is present or missing.

## 4. Validation Commands

List commands run.

## 5. Result

PASS or FAIL.

## 6. Next Step

Recommend:

Step 03 — Paper Parser

## Success Criteria

This step is complete only when:

- prompts/02c_add_real_paper_smoke_fixture.md contains this full prompt
- papers/real/rtlfixer_2311_16543.metadata.json exists
- docs/real_paper_smoke_test.md exists
- reports/step_outputs/step_02c/real_paper_fixture_summary.md exists
- reports/step_outputs/step_02c/real_paper_fixture_flow.mmd exists
- metadata JSON is valid
- local PDF status is clearly recorded as present or missing
