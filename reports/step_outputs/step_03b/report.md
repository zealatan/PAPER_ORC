# Step 03b — IEEE Roman Heading Parser Patch — Final Report

## 1. Prompt Saved

Saved to: `prompts/03b_ieee_roman_heading_parser_patch.md` (360 lines)

## 2. Files Modified

| File | Change |
|---|---|
| `src/papernav/parser.py` | Added `_denoise_pdf_heading`, `_ROMAN_HEADING_LINE_RE`; expanded `_SECTION_ALIASES`; updated Strategy 2 in `_split_sections` |
| `tests/test_parser.py` | Added 18 new IEEE Roman heading tests (35 total, all pass) |
| `docs/parser.md` | Updated section detection documentation to cover Step 03b changes |

## 3. Files Created

| File |
|---|
| `prompts/03b_ieee_roman_heading_parser_patch.md` |
| `reports/step_outputs/step_03b/ieee_heading_parser_patch_summary.md` |
| `reports/step_outputs/step_03b/my_paper_section_check.md` |
| `reports/step_outputs/step_03b/my_paper_parsed_snapshot.json` |
| `reports/step_outputs/step_03b/my_paper_section_split_diagram.mmd` |
| `reports/step_outputs/step_03b/report.md` |

## 4. Parser Patch Summary

**Root cause:** `my_paper.pdf` uses IEEE-style Roman numeral headings in ALL CAPS.
The pypdf extractor introduces an additional artifact where single uppercase letters
are split from their continuation by a space: `"I NTRODUCTION"` instead of `"INTRODUCTION"`.

**Changes:**

1. Added `_ROMAN_HEADING_LINE_RE` — matches any line of the form `[IVX]+. [A-Z...]+`
2. Added `_denoise_pdf_heading()` — collapses split letter patterns before normalization
3. Expanded `_SECTION_ALIASES` with 6 new entries required by the prompt
4. `_split_sections` Strategy 2 now runs two passes (known-heading regex + Roman heading regex) and merges results
5. Unknown headings fall back to snake_case keys automatically

## 5. my_paper Reparse Result

| Metric | Before | After |
|---|---:|---:|
| Sections detected | 2 | 9 |
| Introduction detected | No | **Yes** |
| References detected | Yes | **Yes** |
| Experiment/Simulation detected | No | **Yes** (`experiment`) |

Detected sections after patch:
- `abstract`
- `introduction` ← newly detected
- `system_model` ← newly detected
- `internal_mechanism_of_relu_dnns` ← newly detected (snake_case fallback)
- `analysis` ← newly detected
- `robustness_of_channel_estimation_to_mismatched_information` ← newly detected
- `experiment` ← newly detected (from "VI. SIMULATION RESULTS")
- `conclusion` ← newly detected
- `references`

## 6. Pipeline Rerun Result

After running `analyze_one_paper.py papers/real/my_paper.pdf --paper-id my_paper`:

| Metric | Value |
|---|---:|
| Sections detected | 9 |
| Citation mentions | 89 |
| Bibliography entries | 36 |
| Mapped citations | 36 |
| Citation roles | 89 |
| History tree nodes | 20 |
| History tree edges | 6 |

The history tree now has **20 nodes** (vs. essentially 0 useful nodes before, since the
introduction section was not being detected). This confirms the parser fix propagates
correctly through the full pipeline.

## 7. Tests Run

```
python3 -m compileall src -q                    → COMPILE OK
python3 -m pytest tests/test_parser.py -v       → 35 passed
python3 -m pytest -q                            → 146 passed
python3 -m json.tool reports/step_outputs/step_03b/my_paper_parsed_snapshot.json  → valid
ls -l reports/step_outputs/step_03b/            → 6 files
python3 scripts/analyze_one_paper.py ...        → 20 history nodes, 6 edges
```

## 8. Result

**PASS** — All 35 parser tests pass. Full suite: 146 passed, 0 failures.
`my_paper.pdf` now parses into 9 sections including introduction and references.
The full pipeline produces 20 history tree nodes.

## 9. Next Step

**Step 12 — Baseline Graph Builder**

The parser now correctly detects IEEE-style section headings, which improves citation
role classification for the `experiment`, `introduction`, `analysis`, and other sections.
The history tree output for `my_paper.pdf` can be re-examined after running Step 10 outputs
on the updated pipeline. Proceed to Step 12 when ready to build the Baseline Graph.
