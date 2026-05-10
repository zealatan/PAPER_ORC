# Paper Parser

## Purpose

`src/papernav/parser.py` converts a plain-text or PDF paper file into a `ParsedPaper` object. It is the first functional module in the PaperNav pipeline — all downstream steps (citation extraction, bibliography mapping, role classification) operate on `ParsedPaper` output.

## Inputs

- Plain-text `.txt` file (e.g. `examples/sample_paper.txt`)
- PDF `.pdf` file (e.g. `papers/real/rtlfixer_2311_16543.pdf`)

## Outputs

- `ParsedPaper` dataclass instance with labelled sections
- Optional JSON snapshot via `save_parsed_paper`

## Public API

```python
parse_text(text: str, paper_id: str | None, metadata: dict | None) -> ParsedPaper
parse_file(path: str, paper_id: str | None) -> ParsedPaper
parse_pdf(path: str, paper_id: str | None) -> ParsedPaper
save_parsed_paper(parsed: ParsedPaper, output_path: str) -> None
generate_step03_outputs(sample_path: str, output_dir: str) -> dict
```

## Section Detection

Two strategies are used in order:

**Strategy 1 — `---` separator** (used by synthetic fixture): The text is split on `\n---\n` lines. Each resulting block starts with a heading line ending in `:`. This gives precise, deterministic splits.

**Strategy 2 — Regex heading detection** (used for PDF-extracted text): A pattern matches common section headings in both title-case and ALL-CAPS, with optional leading numbering (`1.`, `I.`, `II.`, etc.).

Supported canonical section keys:

| Key | Matches |
|---|---|
| `abstract` | Abstract |
| `introduction` | Introduction, 1. Introduction, I. Introduction |
| `related_work` | Related Work, Related Works, II. Related Work |
| `background` | Background, Preliminaries |
| `method` | Method, Methodology, Approach, Proposed Method, System Model |
| `experiment` | Experiment, Experiments, Experimental Setup, Evaluation |
| `results` | Results |
| `discussion` | Discussion |
| `conclusion` | Conclusion, Conclusions, Conclusion and Future Work |
| `references` | References, Bibliography |

## Synthetic Fixture

`examples/sample_paper.txt` is the primary deterministic test fixture. It uses `---` separators and `Heading:` lines. Expected sections: `introduction`, `related_work`, `method`, `experiment`, `results`, `discussion`, `references`.

Parsed output is saved to:
- `examples/sample_parsed_paper.json`
- `reports/step_outputs/step_03/parsed_paper_snapshot.json`

## Real Paper Smoke Test

`papers/real/rtlfixer_2311_16543.pdf` (RTLFixer, arXiv 2311.16543) is used as a real-world smoke test. The parser extracts text with `pypdf` and applies Strategy 2 heading detection. The smoke test only verifies that text extraction succeeds and a `ParsedPaper` is returned — it does not validate semantic accuracy.

Smoke test output: `reports/step_outputs/step_03/real_paper_parse_summary.md`

## Limitations

- Section splitting is heuristic; it may miss or misclassify sections in unusual layouts.
- PDF text extraction via `pypdf` is imperfect for multi-column or heavily formatted papers.
- Title inference from PDFs takes the first non-empty line, which may be a page header.
- No citation extraction in this step.
- No bibliography mapping in this step.
