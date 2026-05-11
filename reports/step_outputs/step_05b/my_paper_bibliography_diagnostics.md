# Step 05b — Bibliography Diagnostics for my_paper.pdf

## Paper

DeepReceiver (deep learning-based OFDM receiver)

## Problem

Before Step 05b, `extract_bibliography_entries(parsed)` returned 0 entries for `my_paper.pdf`.

**Root cause:** pypdf extracts the REFERENCES heading as `"R\nEFERENCES"` (split across two
characters by a column layout artifact). The parser's section detector did not recognise this
pattern, so `parsed.sections["references"]` was empty and the extractor returned nothing.

## Fix

Added `extract_references_text_best_effort()` which:
1. Tries `sections["references"]` / `"bibliography"` first (≥ 200 chars).
2. Falls back to `_find_reference_block_in_raw_text(raw_text)` when the section is short/missing.
3. The fallback searches for:
   - Strategy A: `REFERENCES` / `R\nEFERENCES` heading variants.
   - Strategy B: `[1] <capital-letter>` anchor.
   - Strategy C: densest consecutive `[N]` sequence.
4. Trims biography/footer text at `"received the B.S."` etc.
5. Dehyphenates line-wrapped words before splitting entries.

## Result

| Metric | Before | After |
|---|---:|---:|
| Bibliography entries | 0 | **43** |
| Mapped citations | 0 | **43** |
| Title extraction method | — | quoted_title (all 43) |
| History tree nodes | 0 useful | **49** |

## First 10 Entries Extracted

| Citation ID | Method | Year | Title (truncated) |
|---|---|---:|---|
| ref_1 | quoted_title | 2015 | A survey of 5G network: Architecture and emerging technologies |
| ref_2 | quoted_title | 2017 | Intelligent 5G: When cellular networks meet artificial intelligence |
| ref_3 | quoted_title | 2015 | Internet of Things: A survey on enabling technologies, protocols |
| ref_4 | quoted_title | 2015 | Deep learning |
| ref_5 | quoted_title | 2016 | A survey of machine learning for big data processing |
| ref_6 | quoted_title | 2018 | A very brief introduction to machine learning with applications |
| ref_7 | quoted_title | 2018 | Big data processing architecture for radio signals empowered |
| ref_8 | quoted_title | 2020 | Deep learning based channel estimation algorithm over time selective |
| ref_9 | quoted_title | 2019 | Deep learning-based channel estimation for doubly selective |
| ref_10 | quoted_title | 2019 | RoemNet: Robust meta learning based channel estimation in OFDM |

All 43 entries use `quoted_title` extraction method — the IEEE curly quote fix (Step 10b) is
working correctly for every entry in this paper.
