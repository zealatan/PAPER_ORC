# Prompt 02 — Add Sample Paper Fixture

## Working directory

`/home/zealatan/PAPER_ORC`

## Objective

Create a realistic synthetic paper text file at `examples/sample_paper.txt`. This fixture is the standard test input used by all downstream pipeline steps (parser, extractor, bibliography mapper, classifier).

## Context

The fixture must exercise all citation roles defined in the system:
- Introduction / Related Work → history citations
- Experiment / Evaluation → baseline and competitor citations
- References section → bibliography entries to map against

## Allowed modifications

- `examples/sample_paper.txt` (create)
- `examples/sample_parsed_paper.json` (create — hand-written expected parse result)
- `tests/test_fixture.py` (create)
- `reports/step_outputs/step_02/` (create)

## Implementation requirements

- The paper text must contain at minimum:
  - Title line
  - Authors line
  - Abstract section
  - Introduction section with >= 4 numeric citations
  - Related Work section with >= 3 numeric citations
  - Experiment section with >= 4 numeric citations (baselines, competitors)
  - References section with >= 8 numbered bibliography entries
- Citations use numeric bracket format: [1], [2], [3], ...
- Each section must start with a recognizable header line
- Keyword triggers must appear in context sentences:
  - `first proposed`, `pioneer`, `classical` → history_foundational
  - `prior work`, `previous studies` → history_direct_prior
  - `we compare with`, `compared against`, `baseline` → baseline_direct
  - `outperform`, `state-of-the-art` → competitor
  - `dataset`, `benchmark` → benchmark_source

## Tests

Create `tests/test_fixture.py`:
- Assert `examples/sample_paper.txt` exists and is non-empty
- Assert the text contains the strings "Introduction", "Related Work", "Experiment", "References"
- Assert at least 8 citation markers of the form `[N]` are present

## Final report format

```
PASS/FAIL
Sections present: N
Citation markers found: N
Bibliography entries: N
```
