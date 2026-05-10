# History Tree

## Purpose

This tree shows the historical learning path behind the target paper. It traces how foundational works, direct prior contributions, and background citations collectively position the target paper within its field. The graph is section-aware: only citations drawn from Introduction, Related Work, and Background sections are included.

## Summary

| Metric | Value |
|---|---:|
| History candidate mentions | 12 |
| Unique history nodes | 8 |
| Foundational works | 3 |
| Direct prior works | 3 |
| Background citations | 2 |
| Edges | 17 |

## Suggested Reading Path

| Order | Citation ID | Role | Year | Title | Evidence |
|---:|---|---|---:|---|---|
| 1 | ref_2 | history_foundational | 1997 | Robust Frequency and Timing Synchronization for OFDM | The problem of timing synchronization was first proposed in the seminal work of… |
| 2 | ref_3 | history_foundational | 1997 | ML Estimation of Time and Frequency Offset in OFDM Systems | [3] later proposed a maximum-likelihood estimator for joint timing and frequenc… |
| 3 | ref_7 | history_foundational | 1999 | An Improved Frequency Offset Estimator for OFDM Applications | The foundational work of Schmidl and Cox [2] remains a standard reference, and … |
| 4 | ref_4 | history_direct_prior | 2017 | An Introduction to Deep Learning for the Physical Layer | Recent advances in deep learning have motivated the application of neural netwo… |
| 5 | ref_5 | history_direct_prior | 2019 | Deep Learning Based Channel Estimation for OFDM Systems | [5] applied deep neural networks to channel estimation, while previous studies … |
| 6 | ref_8 | history_direct_prior | 2020 | Convolutional Feature Extraction for OFDM Timing Detection | [8] introduced a convolutional feature extractor for timing detection, which we… |
| 7 | ref_1 | history_background | 2020 | Technical Specification 38.211: NR Physical Channels | Orthogonal frequency-division multiplexing (OFDM) has become the dominant wavef… |
| 8 | ref_6 | history_background | 2020 | Recurrent Neural Network for Timing Synchronization in OFDM | [6] explored recurrent networks for timing correction in OFDM systems. |
| 9 | target_paper | target | — | Target Paper | — |

## Tree Edges

| Source | Target | Reason |
|---|---|---|
| ref_2 | ref_4 | Foundational work precedes direct prior work in the history path. |
| ref_2 | ref_5 | Foundational work precedes direct prior work in the history path. |
| ref_2 | ref_8 | Foundational work precedes direct prior work in the history path. |
| ref_3 | ref_4 | Foundational work precedes direct prior work in the history path. |
| ref_3 | ref_5 | Foundational work precedes direct prior work in the history path. |
| ref_3 | ref_8 | Foundational work precedes direct prior work in the history path. |
| ref_7 | ref_4 | Foundational work precedes direct prior work in the history path. |
| ref_7 | ref_5 | Foundational work precedes direct prior work in the history path. |
| ref_7 | ref_8 | Foundational work precedes direct prior work in the history path. |
| ref_4 | ref_1 | Direct prior work connects to background supporting context. |
| ref_4 | ref_6 | Direct prior work connects to background supporting context. |
| ref_5 | ref_1 | Direct prior work connects to background supporting context. |
| ref_5 | ref_6 | Direct prior work connects to background supporting context. |
| ref_8 | ref_1 | Direct prior work connects to background supporting context. |
| ref_8 | ref_6 | Direct prior work connects to background supporting context. |
| ref_1 | target_paper | Background citation connects to the target paper as supporting context. |
| ref_6 | target_paper | Background citation connects to the target paper as supporting context. |

## Mermaid Graph

See: `reports/step_outputs/step_10/history_tree.mmd`

## Notes

This History Tree is heuristic and section-aware. Edge connections are based on role group ordering, not on true citation dependencies. Role classification accuracy directly affects tree quality.