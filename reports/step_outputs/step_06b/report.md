# Step 06b Report — Quick History Tree Preview

## Status: PASS

## Input Files

| File | Status |
|---|---|
| `examples/sample_citation_roles.json` | PRESENT |
| `examples/sample_citation_to_bibliography_map.json` | PRESENT |

## Output Files

| File | Size |
|---|---|
| `history_tree_preview.json` | generated |
| `history_tree_preview.mmd` | generated |
| `history_tree_preview.md` | generated |
| `history_tree_preview_table.md` | generated |
| `report.md` | this file |

## History Candidate Counts

| Metric | Value |
|---|---:|
| Total history candidates | 8 |
| history_foundational | 5 |
| history_direct_prior | 2 |
| history_background | 1 |
| Generated nodes | 8 |
| Generated edges | 8 |

## Generated Preview

Candidates in reading-path order:

| Order | Citation ID | Role | Year | Title |
|---:|---|---|---:|---|
| 1 | ref_2 | history_foundational | 1997 | Robust Frequency and Timing Synchronization… |
| 2 | ref_3 | history_foundational | 1997 | ML Estimation of Time and Frequency Offset… |
| 3 | ref_7 | history_foundational | 1999 | An Improved Frequency Offset Estimator… |
| 4 | ref_5 | history_foundational | 2019 | Deep Learning Based Channel Estimation… |
| 5 | ref_8 | history_foundational | 2020 | Convolutional Feature Extraction for OFDM… |
| 6 | ref_4 | history_direct_prior | 2017 | An Introduction to Deep Learning… |
| 7 | ref_6 | history_direct_prior | 2020 | Recurrent Neural Network for Timing… |
| 8 | ref_1 | history_background | 2020 | Technical Specification 38.211: NR Physical… |

Edge pattern: all 5 foundational nodes → ref_4 (first direct_prior); both direct_prior nodes → ref_1 (background); ref_1 → Target Paper.

## Limitations

- Year ordering within history_foundational puts ref_4 (2017) after ref_8 (2020) in the direct_prior group, not the foundational group, because ref_4's best role is history_direct_prior despite a 2017 publication year. Foundational candidates with later dates (ref_5: 2019, ref_8: 2020) are ordered after earlier ones within the foundational group.
- Context bleed in the classifier caused ref_5 and ref_8 to receive `history_foundational` in the related_work section (the word "introduced" from an adjacent sentence triggered the foundational keyword). The actual works are more accurately direct priors, but the classifier correctly applies the highest-priority matching keyword.
- This preview does not infer real dependency edges between cited papers.

## Next Step

**Step 10 — History Tree Builder**: construct a full directed graph from history citation roles with real edge reasoning, HistoryTreeNode objects, and importance scoring.

Step 07/08 may optionally produce a Milestone 1 summary report before moving to graph construction.
