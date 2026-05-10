# Step 02 Patch — Complete Sample Paper Fixture Documentation and Visual Outputs

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, overwrite the existing incomplete prompt file with this full prompt:

prompts/02b_complete_sample_fixture_docs_and_visual_outputs.md

The previous file only contains the first few lines and is incomplete. Replace it with this full prompt.

After saving this prompt, continue with the patch.

## Working Directory

/home/zealatan/PAPER_ORC

## Objective

Complete Step 02.

Current files exist:
- prompts/02_add_sample_paper_fixture.md
- examples/sample_paper.txt
- reports/step_outputs/step_02/report.md

Missing files:
- examples/sample_expected_sections.json
- docs/sample_paper_design.md
- reports/step_outputs/step_02/sample_paper_structure.md
- reports/step_outputs/step_02/sample_paper_flow.mmd
- reports/step_outputs/step_02/expected_citation_map.json

Create these missing files.

Do not proceed to Step 03.

## Do Not Modify

Do not overwrite or delete:
- README.md
- assets/
- prompts/00_bootstrap_repository.md
- prompts/01_define_common_models.md
- prompts/02_add_sample_paper_fixture.md
- examples/sample_paper.txt
- src/
- tests/test_fixture.py

This patch is only for completing Step 02 documentation and visualization outputs.

## Required File 1

Create:

examples/sample_expected_sections.json

It must be valid JSON.

Use this information:
- paper_id: sample_paper
- expected sections:
  - Introduction
  - Related Work
  - Experiment
  - Results
  - Discussion
  - References
- expected history sections:
  - Introduction
  - Related Work
- expected baseline sections:
  - Experiment
  - Results
- expected reference section:
  - References
- expected citation marker count: 41
- expected bibliography entry count: 13

Also include section_role_expectations:
- Introduction: history_foundational, history_direct_prior, history_background
- Related Work: history_direct_prior, history_background
- Experiment: baseline_direct, competitor, benchmark_source, metric_source
- Results: competitor, metric_source, supporting_evidence
- Discussion: supporting_evidence
- References: empty list

## Required File 2

Create:

docs/sample_paper_design.md

It must explain the design of examples/sample_paper.txt.

Use this structure:

# Sample Paper Fixture Design

## Purpose

Explain that examples/sample_paper.txt is a synthetic paper used to test the PaperNav pipeline.

## Design Goals

- Include Introduction citations for History Tree testing
- Include Related Work citations for direct prior work testing
- Include Experiment citations for Baseline Graph testing
- Include Results citations for competitor and metric-source testing
- Include References section for bibliography mapping

## Section Design

Add a Markdown table:

| Section | Purpose | Expected Citation Roles |
|---|---|---|

Include:
- Introduction
- Related Work
- Experiment
- Results
- Discussion
- References

## Citation Design

Explain that numeric citations like [1], [2], [5] are intentionally used because the MVP focuses on numeric citation extraction.

## Expected Counts

- Sections: 6
- Citation markers: 41
- Bibliography entries: 13

## Downstream Use

Explain that this fixture will be used by:
- Step 03 Paper Parser
- Step 04 Citation Extractor
- Step 05 Bibliography Mapper
- Step 06 Citation Role Classifier
- Step 08 Milestone 1 Pipeline

## Required File 3

Create:

reports/step_outputs/step_02/sample_paper_structure.md

It must include this Markdown table:

| Section | Purpose | Expected Citation Role Family | Citation Examples |
|---|---|---|---|

Include:
- Introduction
- Related Work
- Experiment
- Results
- Discussion
- References

Use actual citation examples from examples/sample_paper.txt if easy. Otherwise use representative markers such as [1], [2], [5], [6].

## Required File 4

Create:

reports/step_outputs/step_02/sample_paper_flow.mmd

It must be a valid Mermaid flowchart.

Use this content:

flowchart TD
    A[Sample Paper Fixture] --> B[Introduction]
    A --> C[Related Work]
    A --> D[Experiment]
    A --> E[Results]
    A --> F[Discussion]
    A --> G[References]

    B --> B1[History citations]
    C --> C1[Direct prior / background citations]
    D --> D1[Baseline / competitor citations]
    E --> E1[Metric / competitor / evidence citations]
    F --> F1[Supporting evidence citations]
    G --> G1[Bibliography entries]

    B1 --> H[History Tree input]
    C1 --> H
    D1 --> I[Baseline Graph input]
    E1 --> I
    G1 --> J[Bibliography Mapper input]

## Required File 5

Create:

reports/step_outputs/step_02/expected_citation_map.json

It must be valid JSON.

Required content:
- paper_id: sample_paper
- source_file: examples/sample_paper.txt
- summary:
  - section_count: 6
  - citation_marker_count: 41
  - bibliography_entry_count: 13
- sections:
  - Introduction:
    - expected_role_family: history
    - expected_roles: history_foundational, history_direct_prior, history_background
  - Related Work:
    - expected_role_family: history
    - expected_roles: history_direct_prior, history_background
  - Experiment:
    - expected_role_family: baseline
    - expected_roles: baseline_direct, competitor, benchmark_source, metric_source
  - Results:
    - expected_role_family: baseline_or_evidence
    - expected_roles: competitor, metric_source, supporting_evidence
  - Discussion:
    - expected_role_family: evidence
    - expected_roles: supporting_evidence
  - References:
    - expected_role_family: bibliography
    - expected_roles: empty list

## Optional Update

Update:

reports/step_outputs/step_02/report.md

Add this section:

## Required Visualization Outputs

- sample_paper_structure.md
- sample_paper_flow.mmd
- expected_citation_map.json

Also mention:
- examples/sample_expected_sections.json
- docs/sample_paper_design.md

## Validation Commands

Run:

python3 -m json.tool examples/sample_expected_sections.json > /tmp/sample_expected_sections_check.json
python3 -m json.tool reports/step_outputs/step_02/expected_citation_map.json > /tmp/expected_citation_map_check.json
python3 -m pytest tests/test_fixture.py -v
ls -l examples/sample_expected_sections.json docs/sample_paper_design.md
ls -l reports/step_outputs/step_02/

## Final Report Format

At the end, report:

# Step 02 Patch — Complete Sample Fixture Docs and Visual Outputs — Final Report

## 1. Prompt Saved

Confirm saved to:
prompts/02b_complete_sample_fixture_docs_and_visual_outputs.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files.

## 4. Validation Commands

List commands run.

## 5. Result

PASS or FAIL.

## 6. Notes

Mention assumptions or limitations.

## 7. Next Step

Recommend:
Step 03 — Paper Parser

## Success Criteria

This patch is complete only when:
- prompts/02b_complete_sample_fixture_docs_and_visual_outputs.md exists and contains this full prompt
- examples/sample_expected_sections.json exists
- docs/sample_paper_design.md exists
- reports/step_outputs/step_02/sample_paper_structure.md exists
- reports/step_outputs/step_02/sample_paper_flow.mmd exists
- reports/step_outputs/step_02/expected_citation_map.json exists
- examples/sample_expected_sections.json is valid JSON
- expected_citation_map.json is valid JSON
- python3 -m pytest tests/test_fixture.py -v passes
