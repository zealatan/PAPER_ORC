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

**Strategy 2 — Combined heading detection** (used for PDF-extracted text):

- **Pass A** (`_PDF_HEADING_RE`): Regex matching common section headings in both title-case
  and ALL-CAPS, with optional leading numbering (`1.`, `I.`, `II.`, etc.).
- **Pass B** (`_ROMAN_HEADING_LINE_RE`): Added in Step 03b. Detects any IEEE-style Roman
  numeral heading (`I.`, `II.`, …, `VII.`) with ALL-CAPS text. PDF extraction artifacts
  are corrected by `_denoise_pdf_heading` before normalization.

Results from both passes are merged and sorted by position.

**`_denoise_pdf_heading`** fixes PDF character-spacing artifacts in headings:

- `"I NTRODUCTION"` → `"INTRODUCTION"` (single letter split from continuation)
- `"DNN S"` → `"DNNS"` (suffix letter split from base word)

Unknown headings not in the alias map fall back to a **snake_case key**:

```
"INTERNAL MECHANISM OF RELU DNNS" → "internal_mechanism_of_relu_dnns"
```

Supported canonical section keys (Step 03b expanded):

| Key | Matches |
|---|---|
| `abstract` | Abstract |
| `introduction` | Introduction, I. INTRODUCTION |
| `related_work` | Related Work, Background and Related Work |
| `background` | Background, Preliminaries |
| `system_model` | System Model, II. SYSTEM MODEL AND CHANNEL ESTIMATION |
| `method` | Method, Methodology, Approach, Proposed Method |
| `analysis` | Analysis, IV. ANALYSIS ON DL BASED CHANNEL ESTIMATION |
| `experiment` | Experiment, Experiments, Simulation Results, VI. SIMULATION RESULTS |
| `results` | Results |
| `discussion` | Discussion |
| `conclusion` | Conclusion, Conclusions, VII. CONCLUSIONS |
| `references` | References, Bibliography, REFERENCES |
| _(snake_case)_ | Any other ALL-CAPS Roman numeral heading |

## Synthetic Fixture

`examples/sample_paper.txt` is the primary deterministic test fixture. It uses `---` separators and `Heading:` lines. Expected sections: `introduction`, `related_work`, `method`, `experiment`, `results`, `discussion`, `references`.

Parsed output is saved to:
- `examples/sample_parsed_paper.json`
- `reports/step_outputs/step_03/parsed_paper_snapshot.json`

## Real Paper Smoke Test

`papers/real/rtlfixer_2311_16543.pdf` (RTLFixer, arXiv 2311.16543) is used as a real-world smoke test. The parser extracts text with `pypdf` and applies Strategy 2 heading detection. The smoke test only verifies that text extraction succeeds and a `ParsedPaper` is returned — it does not validate semantic accuracy.

Smoke test output: `reports/step_outputs/step_03/real_paper_parse_summary.md`

## Real Paper Smoke Tests

Two real papers are used as smoke tests:

- `rtlfixer_2311_16543.pdf` — standard section names in mixed case
- `papers/real/my_paper.pdf` — IEEE-style Roman numeral headings (added Step 03b)

Both parse correctly after the Step 03b patch.

## Limitations

- Section splitting is heuristic; it may miss or misclassify sections in unusual layouts.
- PDF text extraction via `pypdf` is imperfect for multi-column or heavily formatted papers.
- Title inference from PDFs takes the first non-empty line, which may be a page header.
- The Roman numeral heading denoiser assumes that single-letter splits are artifacts; this
  assumption holds for IEEE-style PDFs but may not generalize to all extractors.
- No citation extraction in this step.
- No bibliography mapping in this step.
