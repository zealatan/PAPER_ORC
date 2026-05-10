# Quick History Tree Preview

## Purpose

This is a lightweight preview generated from Step 06 citation role classification.
It converts history-role citations into a suggested reading path ordered by role
priority (foundational → direct prior → background) and by publication year.
It is not the final History Tree Builder — no real citation-to-citation dependency
is inferred.

## Input Files

- `examples/sample_citation_roles.json`
- `examples/sample_citation_to_bibliography_map.json`

## History Candidate Summary

| Role | Count |
|---|---:|
| history_foundational | 5 |
| history_direct_prior | 2 |
| history_background | 1 |
| **Total** | **8** |

## Reading Path Preview

Citations are listed in suggested reading order: foundational work first, then
direct prior work, then background context, sorted by year within each group.

| Order | Citation ID | Role | Year | Title | Section | Evidence |
|---:|---|---|---:|---|---|---|
| 1 | ref_2 | history_foundational | 1997 | Robust Frequency and Timing Synchronization f… | introduction | The problem of timing synchronization was first propose… |
| 2 | ref_3 | history_foundational | 1997 | ML Estimation of Time and Frequency Offset in… | introduction | [3] later proposed a maximum-likelihood estimator for j… |
| 3 | ref_7 | history_foundational | 1999 | An Improved Frequency Offset Estimator for OF… | related_work | The foundational work of Schmidl and Cox [2] remains a … |
| 4 | ref_5 | history_foundational | 2019 | Deep Learning Based Channel Estimation for OF… | related_work | Previous studies on machine-learning-based synchronizat… |
| 5 | ref_8 | history_foundational | 2020 | Convolutional Feature Extraction for OFDM Tim… | related_work | [8] introduced a convolutional feature extractor for ti… |
| 6 | ref_4 | history_direct_prior | 2017 | An Introduction to Deep Learning for the Phys… | introduction | Recent advances in deep learning have motivated the app… |
| 7 | ref_6 | history_direct_prior | 2020 | Recurrent Neural Network for Timing Synchroni… | introduction | [6] explored recurrent networks for timing correction i… |
| 8 | ref_1 | history_background | 2020 | Technical Specification 38.211: NR Physical C… | introduction | Orthogonal frequency-division multiplexing (OFDM) has b… |

## Mermaid Preview

See: `reports/step_outputs/step_06b/history_tree_preview.mmd`

## Notes

- This is not the final History Tree Builder.
- Ordering is heuristic: role group first, then year, then citation number.
- No real citation-to-citation dependency is inferred between referenced papers.
- The final Step 10 History Tree Builder will use richer graph logic, edge
  reasoning, external metadata, and structured export.
