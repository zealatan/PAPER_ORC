# Step 06c Report — Citation Role Classifier Precision Patch

## Status: PASS

## Input Files

| File | Status |
|---|---|
| `examples/sample_citation_mentions.json` | PRESENT |
| `examples/sample_citation_to_bibliography_map.json` | PRESENT |
| `reports/step_outputs/step_06/citation_roles_snapshot.json` | PRESENT (before-state) |

## Classifier Changes Applied

1. **Sentence-first strategy**: `mention.sentence` is the primary text for all keyword checks.  
   `mention.context_window` is used only as a fallback when the sentence has fewer than 10 words.

2. **`introduced` removed from `_FOUNDATIONAL_KWS`**: the word "introduced" appeared too
   frequently in neighboring sentences, causing false `history_foundational` assignments via
   context_window bleed (e.g., ref_5 and ref_8 in related_work section).

3. **Rule 3 keywords added to `_PRIOR_KWS`**: `deep learning`, `neural`, `neural network`,
   `neural networks`, `cnn`, `learning-based`, `data-driven` — these signal ML-era prior work
   when cited in history sections (intro/related_work/background).

4. **Reason field clarity**: the reason string now states whether the keyword came from a
   "sentence keyword", "context fallback", or "section default".

## Before / After Role Counts

| Role | Before | After | Δ |
|---|---:|---:|---:|
| history_foundational | 8 | 6 | −2 |
| history_direct_prior | 3 | 4 | +1 |
| history_background | 1 | 2 | +1 |
| baseline_direct | 5 | 5 | 0 |
| benchmark_source | 6 | 3 | −3 |
| competitor | 0 | 2 | +2 |
| metric_source | 1 | 2 | +1 |
| supporting_evidence | 4 | 4 | 0 |
| misc | 13 | 13 | 0 |

**Total changed: 7**

## Changed Roles Detail

| Citation ID | Section | Old Role | New Role | Reason |
|---|---|---|---|---|
| ref_5 | related_work | history_foundational | history_direct_prior | "introduced" in context removed; "previous studies" in sentence matches direct_prior |
| ref_8 | related_work | history_foundational | history_direct_prior | "introduced" removed from foundational; section default |
| ref_6 | introduction | history_direct_prior | history_background | "previous studies" was in context_window only (long sentence); section default |
| ref_2 | experiment | benchmark_source | baseline_direct | "dataset" was in context_window only; sentence has "compare with" + "baseline" |
| ref_10 | experiment | benchmark_source | metric_source | "benchmark" was in context; sentence has "metric" |
| ref_12 | experiment | benchmark_source | competitor | "benchmark" was in context; sentence has "outperforms" |
| ref_12 | results | baseline_direct | competitor | "state-of-the-art" in sentence fires competitor before baseline_direct |

## Key Targets: ref_5 and ref_8

| Citation | Section | Before | After |
|---|---|---|---|
| ref_5 | related_work | history_foundational ❌ | history_direct_prior ✅ |
| ref_8 | related_work | history_foundational ❌ | history_direct_prior ✅ |

Both citations no longer receive false `history_foundational` assignments.

## Limitations

- ref_8 in related_work now gets `history_direct_prior` via section default since its sentence
  "[8] introduced a convolutional feature extractor..." has no matching prior_kw after removing
  "introduced". This is acceptable — the work is a direct prior.
- Context fallback (threshold < 10 words) still fires for very short fragment sentences like
  "[8] and the recurrent approach of Liu et al." (9 words). This is intentional.
- Keyword coverage for `_PRIOR_KWS` ("neural", "deep learning") may fire on non-prior
  mentions in unusual contexts, but only within history sections.

## Next Step

**Step 10 — History Tree Builder**: build a full directed graph from history citation roles.

Step 08 — Milestone 1 Summary Report may optionally be produced first.
