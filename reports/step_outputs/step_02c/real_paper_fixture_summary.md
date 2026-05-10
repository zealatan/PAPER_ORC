# Real Paper Smoke Fixture

## Status

**PDF: PRESENT** — `papers/real/rtlfixer_2311_16543.pdf` exists locally.

## Target Paper

| Field | Value |
|---|---|
| Title | RTLFixer: Automatically Fixing RTL Syntax Errors with Large Language Models |
| arXiv ID | 2311.16543 |
| URL | https://arxiv.org/pdf/2311.16543 |
| Local path | `papers/real/rtlfixer_2311_16543.pdf` |

## Expected Use

| Step | Use |
|---|---|
| Step 03 Paper Parser | Parse PDF into labelled sections |
| Step 04 Citation Extractor | Extract `[N]` markers per section |
| Step 05 Bibliography Mapper | Map markers to full bibliography entries |
| Step 06 Citation Role Classifier | Assign citation roles by section and context |
| Milestone 2 History Tree + Baseline Graph | Build citation graph from extracted references |
| Milestone 3 Topic Relevance Agent | Score relevance to target research topics |

## Next Parser Test

Step 03 should parse **both** fixtures:

1. `examples/sample_paper.txt` — synthetic fixture with known ground truth (41 markers, 13 bibliography entries, 6 sections)
2. `papers/real/rtlfixer_2311_16543.pdf` — real paper smoke test; expected section structure is Introduction, Related Work, Evaluation/Results, References

The synthetic fixture verifies parser correctness against known counts. The real PDF verifies that the parser handles authentic formatting, multi-column layout, and realistic citation density.
