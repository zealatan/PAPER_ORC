# Classifier Precision Patch Summary (Step 06c)

## Changes Applied

- **Sentence-first strategy**: all strong keyword checks now use `mention.sentence` first;
  `mention.context_window` is used only when the sentence has fewer than 10 words.
- **`introduced` removed** from foundational keywords: it appeared too frequently in
  neighboring sentences, causing false `history_foundational` assignments.
- **Rule 3 keywords added** to `_PRIOR_KWS`: `deep learning`, `neural`, `neural network`,
  `neural networks`, `cnn`, `learning-based`, `data-driven` — these signal ML-era prior
  work when cited in history sections.
- **Reason field** now explicitly states whether the decision came from sentence keyword,
  context fallback, or section default.

## Role Count Summary

| Metric | Before | After |
|---|---:|---:|
| Total mentions | 41 | 41 |
| History roles total | 12 | 12 |
| history_foundational | 8 | 6 |
| history_direct_prior | 3 | 4 |
| history_background | 1 | 2 |
| Baseline/experiment roles total | 12 | 12 |
| baseline_direct | 5 | 5 |
| benchmark_source | 6 | 3 |
| competitor | 0 | 2 |
| misc | 13 | 13 |
| Changed roles | — | 7 |
