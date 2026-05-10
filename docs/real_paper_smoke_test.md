# Real Paper Smoke Test

## Target Paper

- **Title:** RTLFixer: Automatically Fixing RTL Syntax Errors with Large Language Models
- **arXiv ID:** 2311.16543
- **URL:** https://arxiv.org/pdf/2311.16543
- **Local PDF path:** `papers/real/rtlfixer_2311_16543.pdf`

## Why This Paper

RTLFixer is a strong smoke-test target for PaperNav because it sits at the intersection of multiple relevant sub-fields: LLM-assisted RTL debugging, automated syntax repair, Verilog and SystemVerilog correctness, and hardware design automation. These topic signals make it a useful candidate for both citation role classification (distinguishing foundational work from direct baselines) and the Milestone 3 Topic Relevance Agent. The paper also follows a standard IEEE/ACM conference structure with clearly labelled Introduction, Related Work, and Evaluation sections, which makes it a realistic but tractable target for early parser and extractor smoke tests.

## How It Will Be Used

This paper will be used as a real-document smoke-test target at each step of the PaperNav pipeline:

- **Step 03 Paper Parser** — parse the PDF into a `ParsedPaper` dataclass with labelled sections
- **Step 04 Citation Extractor** — extract `[N]` and author-year citation markers from each section
- **Step 05 Bibliography Mapper** — map citation markers to full bibliography entries
- **Step 06 Citation Role Classifier** — assign roles (history_foundational, baseline_direct, competitor, etc.) based on section and context
- **Milestone 2 History Tree and Baseline Graph** — use extracted citations to build the history tree and baseline comparison graph
- **Milestone 3 Topic Relevance Agent** — score the paper's relevance to target research topics

## If PDF Is Missing

If `papers/real/rtlfixer_2311_16543.pdf` is not present, download it with:

```bash
wget -O papers/real/rtlfixer_2311_16543.pdf https://arxiv.org/pdf/2311.16543
```

## Limitations

This step only prepares metadata and smoke-test documentation. It does not parse the PDF, extract citations, or validate section structure. All parsing logic is deferred to Step 03.
