# Step 06 Report — Citation Role Classifier

## Status: PASS

## Classifier Functions

| Function | Status |
|---|---|
| `classify_citation_role` | implemented |
| `classify_citation_roles` | implemented |
| `save_citation_roles` | implemented |
| `generate_step06_outputs` | implemented |

## Synthetic Fixture Role Result

| Metric | Value |
|---|---|
| Total roles | 41 |
| History candidates | 12 |
| Baseline/experiment candidates | 12 |
| Misc / reference anchors | 13 |
| Unmapped | 0 |

Role counts:

| Role | Count |
|---|---:|
| history_foundational | 8 |
| history_direct_prior | 3 |
| history_background | 1 |
| baseline_direct | 5 |
| benchmark_source | 6 |
| metric_source | 1 |
| competitor | 0 |
| supporting_evidence | 4 |
| misc | 13 |

Note: `competitor` fires 0 times on the synthetic fixture because benchmark_source (priority 2) fires first wherever "benchmark" appears in context, and baseline_direct fires before competitor in results. The real paper produces competitor=0 for the same reason — "state-of-the-art" does appear but benchmark_source has higher priority in those contexts.

Section-level role counts (synthetic):

| Section | Role | Count |
|---|---|---:|
| introduction | history_foundational | 3 |
| introduction | history_direct_prior | 2 |
| introduction | history_background | 1 |
| introduction | benchmark_source | 1 |
| related_work | history_foundational | 3 |
| related_work | history_direct_prior | 1 |
| related_work | supporting_evidence | 1 |
| related_work | benchmark_source | 1 |
| method | supporting_evidence | 1 |
| experiment | benchmark_source | 4 |
| experiment | baseline_direct | 3 |
| experiment | metric_source | 1 |
| experiment | history_foundational | 1 |
| results | baseline_direct | 2 |
| discussion | supporting_evidence | 2 |
| references | misc | 13 |

Output JSON paths:
- `examples/sample_citation_roles.json`
- `reports/step_outputs/step_06/citation_roles_snapshot.json`

## Real Paper Smoke Result

| Metric | Value |
|---|---|
| Real citation mentions | PRESENT |
| Real bibliography map | PRESENT |
| Total roles classified | 64 |
| history_foundational | 2 |
| history_background | 22 |
| baseline_direct | 4 |
| benchmark_source | 10 |
| metric_source | 3 |
| supporting_evidence | 2 |
| misc | 21 |

## Visualization Outputs

| File | Description |
|---|---|
| `citation_role_summary.md` | Overall and section-level role counts + history/baseline tables |
| `citation_role_flow.mmd` | Mermaid flowchart of classification pipeline |
| `citation_roles_snapshot.json` | Full CitationRole list (synthetic) |
| `history_citation_candidates.md` | History role mentions with evidence |
| `baseline_citation_candidates.md` | Baseline/experiment role mentions with evidence |
| `real_paper_citation_role_summary.md` | RTLFixer smoke result |
| `real_paper_citation_roles_snapshot.json` | RTLFixer CitationRole list |
| `report.md` | This report |

## Test Results

```
tests/test_citation_role_classifier.py — 18 passed
Full suite — 101 passed
```

## Notes

- `benchmark_source` (priority 2) fires broadly because context_window includes adjacent text; this causes some in-text baseline mentions to be labelled benchmark_source rather than baseline_direct when "dataset" or "benchmark" appears in the surrounding context. This is a known limitation of full-context keyword matching.
- `competitor` fires 0 times in the synthetic fixture because benchmark or baseline keywords appear earlier in priority in every sentence that also contains "outperform" or "state-of-the-art".
- The `reason` field on `CitationRole` was added as a required output; the `models.py` `CitationRole` dataclass was updated with `reason: str = ""` (default preserves backward compatibility with existing tests).
- RTLFixer real paper: 64 mentions, 21 misc anchors, 43 body citations classified.

## Next Step

Step 10 — History Tree Builder: use `history_foundational` and `history_direct_prior` roles to construct a directed precedence graph of prior work.

Note: Step 07–08 may optionally produce a Milestone 1 summary report before moving to graph construction.
