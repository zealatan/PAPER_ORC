# Sample Paper Fixture Design

## Purpose

`examples/sample_paper.txt` is a synthetic paper used to test the PaperNav pipeline end-to-end. It is not a real publication. It is designed to exercise every citation role and section type that the pipeline must handle, in a compact and fully controlled document.

## Design Goals

- Include Introduction citations for History Tree testing (foundational, direct prior, background)
- Include Related Work citations for direct prior work testing
- Include Experiment citations for Baseline Graph testing (baselines, competitors, benchmark and metric sources)
- Include Results citations for competitor and metric-source testing
- Include References section for bibliography mapping

## Section Design

| Section | Purpose | Expected Citation Roles |
|---|---|---|
| Introduction | Establish historical context and motivation | history_foundational, history_direct_prior, history_background |
| Related Work | Survey direct predecessors and close competitors | history_direct_prior, history_background |
| Experiment | Define evaluation setup and compare against baselines | baseline_direct, competitor, benchmark_source, metric_source |
| Results | Report quantitative outcomes vs. baselines and state-of-the-art | competitor, metric_source, supporting_evidence |
| Discussion | Interpret results with supporting evidence from literature | supporting_evidence |
| References | Enumerate all cited works for bibliography mapping | (none — bibliography entries only) |

## Citation Design

Numeric citations in the form `[1]`, `[2]`, `[5]` are used throughout the fixture. This is intentional: the MVP citation extractor focuses on numeric-style citation markers, which are dominant in IEEE-format papers. Author-year citations (e.g., Smith et al., 2020) are out of scope for Step 04.

## Expected Counts

- Sections: 6
- Citation markers: 41 (28 in body sections + 13 in References)
- Bibliography entries: 13

## Downstream Use

This fixture will be used by:

- **Step 03 Paper Parser** — split the text into labeled sections
- **Step 04 Citation Extractor** — extract `[N]` markers from each section
- **Step 05 Bibliography Mapper** — map `[N]` markers to full bibliography entries in the References section
- **Step 06 Citation Role Classifier** — assign roles (history_foundational, baseline_direct, etc.) based on section and surrounding text
- **Step 08 Milestone 1 Pipeline** — run the full extraction pipeline on this fixture as an integration test
