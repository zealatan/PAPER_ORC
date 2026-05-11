# IEEE Heading Parser Patch Summary

## Problem

The PaperNav paper parser used a fixed-alternative regex (`_PDF_HEADING_RE`) that
only matched a predefined set of known section names in mixed case. It did not handle:

1. **IEEE Roman numeral headings** — headings of the form `I. INTRODUCTION`,
   `II. SYSTEM MODEL AND CHANNEL ESTIMATION`, etc.
2. **PDF extraction character-spacing artifacts** — pypdf splits uppercase letter
   sequences mid-word, producing `"I NTRODUCTION"` instead of `"INTRODUCTION"`,
   `"S YSTEM MODEL"` instead of `"SYSTEM MODEL"`, `"DNN S"` instead of `"DNNS"`.
3. **Unknown section headings** — headings not in the predefined set were silently
   discarded instead of being preserved as snake_case keys.

## Changes Made

### `src/papernav/parser.py`

**Expanded `_SECTION_ALIASES`** — added mappings required by the prompt:

| Raw heading (lowercase) | Canonical key |
|---|---|
| `background and related work` | `related_work` |
| `system model and channel estimation` | `system_model` |
| `analysis` | `analysis` |
| `analysis on dl based channel estimation` | `analysis` |
| `simulation results` | `experiment` |
| `robustness` | `robustness` |

Also corrected: `system model` was mapped to `"method"` — it now maps to `"system_model"`.

**Added `_ROMAN_HEADING_LINE_RE`** — a new regex that detects IEEE Roman numeral headings
regardless of whether the heading text is in the alias map:

```python
_ROMAN_HEADING_LINE_RE = re.compile(
    r"(?m)^([IVX]+)\.\s+([A-Z][A-Z\s]*[A-Z]|[A-Z]{2,})\s*$"
)
```

**Added `_denoise_pdf_heading(text)`** — fixes two PDF extraction artifacts:

- Pattern 1: single uppercase letter + space + 2+ uppercase continuation
  → `"I NTRODUCTION"` → `"INTRODUCTION"`
- Pattern 2: 2+ uppercase letters + space + single standalone uppercase letter
  → `"DNN S"` → `"DNNS"`

**Updated `_split_sections` Strategy 2** — the PDF heading detection now runs two passes:

- **Pass A**: existing `_PDF_HEADING_RE` (handles known mixed-case headings)
- **Pass B**: new `_ROMAN_HEADING_LINE_RE` (handles IEEE-style ALL-CAPS Roman headings)

Results from both passes are merged by position and sorted. Unknown headings fall back
to a snake_case key using `re.sub(r"[^a-z0-9]+", "_", clean_text.lower())`.

**Updated `_PDF_HEADING_RE`** — extended existing alternatives to also match:
- `Simulation Results?`
- `Analysis(?:\s+\w+)*` (allows "Analysis on DL based...")
- Expanded `Background` and `System Model` alternatives

## What Was Not Changed

- `_split_sections` Strategy 1 (synthetic `---` divider format) is unchanged.
- `parse_text`, `parse_file`, `parse_pdf`, `save_parsed_paper` signatures unchanged.
- All 17 original parser tests still pass.
- The `generate_step03_outputs` function is unchanged.

## Result

| Metric | Before | After |
|---|---:|---:|
| Sections detected (my_paper.pdf) | 2 | 9 |
| Total parser tests | 17 | 35 |
| Tests passing | 17 | 35 |
