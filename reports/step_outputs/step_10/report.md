# Step 10 — History Tree Builder — Final Report

## 1. Prompt Saved

Saved to: `prompts/10_build_history_tree_builder.md` (822 lines)

## 2. Files Created

| File | Description |
|---|---|
| `reports/step_outputs/step_10/history_tree.json` | Structured history tree (nodes, edges, reading path) |
| `reports/step_outputs/step_10/history_tree.md` | Markdown reading guide |
| `reports/step_outputs/step_10/history_tree.mmd` | Mermaid flowchart |
| `reports/step_outputs/step_10/history_tree_table.md` | Full candidate node table |
| `reports/step_outputs/step_10/history_tree_summary.md` | Narrative summary |
| `reports/step_outputs/step_10/history_tree.html` | HTML Mermaid preview (optional — created) |
| `reports/step_outputs/step_10/real_paper_history_tree_summary.md` | Real paper smoke result |
| `reports/step_outputs/step_10/real_paper_history_tree.json` | Real paper tree JSON (optional — created) |
| `reports/step_outputs/step_10/real_paper_history_tree.mmd` | Real paper Mermaid (optional — created) |
| `examples/sample_history_tree.json` | Sample fixture |
| `tests/test_history_tree_builder.py` | 16 tests |
| `docs/history_tree_builder.md` | Module documentation |
| `prompts/10_build_history_tree_builder.md` | This prompt |

## 3. Files Modified

| File | Change |
|---|---|
| `src/papernav/graph/history_tree.py` | Full implementation (was a 1-line stub) |

## 4. History Tree Functions Implemented

- `load_citation_roles(path)` — deserializes CitationRole list from JSON
- `load_bibliography_map(path)` — deserializes BibliographyEntry dict from JSON
- `select_history_roles(roles)` — filters to history_foundational / direct_prior / background
- `build_history_tree(roles, bibliography_map, target_title, paper_id)` — builds full tree dict
- `save_history_tree(tree, output_path)` — writes JSON
- `render_history_tree_markdown(tree)` — produces Markdown reading guide
- `render_history_tree_mermaid(tree)` — produces Mermaid flowchart LR with subgraphs
- `generate_step10_outputs(roles_path, bibliography_map_path, output_dir)` — orchestrates all outputs
- `render_history_tree_html(mermaid_text, output_path)` — optional HTML Mermaid preview (created)

Internal helpers: `_render_history_tree_table`, `_render_history_tree_summary`, `_generate_real_paper_outputs`

## 5. Synthetic History Tree Result

| Metric | Value |
|---|---:|
| History candidate mentions | 12 |
| Unique history nodes | 8 |
| Foundational works | 3 |
| Direct prior works | 3 |
| Background citations | 2 |
| Edges | 17 |

**Reading path:**

`ref_2` → `ref_3` → `ref_7` → `ref_4` → `ref_5` → `ref_8` → `ref_1` → `ref_6` → `target_paper`

- Output JSON: `reports/step_outputs/step_10/history_tree.json`
- Mermaid: `reports/step_outputs/step_10/history_tree.mmd`

## 6. Real Paper Smoke Result

| Metric | Value |
|---|---:|
| Real role file | found |
| Real bibliography map | found |
| History candidate mentions | 24 |
| Unique history nodes | 16 |
| Foundational | 2 |
| Direct prior | 0 |
| Background | 14 |
| Edges | 6 |

The real paper has a strong background-heavy profile, which reflects the role
classifier's conservative assignment pattern when processing the real PDF.

## 7. Visualization Outputs

```
reports/step_outputs/step_10/
  history_tree.json                    (11.1 KB)
  history_tree.md                      (3.9 KB)
  history_tree.mmd                     (1.2 KB)
  history_tree_table.md                (1.7 KB)
  history_tree_summary.md              (1.9 KB)
  history_tree.html                    (1.5 KB)
  real_paper_history_tree.json         (17.9 KB)
  real_paper_history_tree.mmd          (1.5 KB)
  real_paper_history_tree_summary.md   (0.6 KB)
```

## 8. Tests Run

```
python3 -m compileall src -q                      → OK (no errors)
python3 -m pytest tests/test_history_tree_builder.py -v  → 16 passed
python3 -m pytest -q                              → 128 passed
python3 -m json.tool reports/step_outputs/step_10/history_tree.json   → valid
python3 -m json.tool examples/sample_history_tree.json                → valid
ls -l reports/step_outputs/step_10/               → 9 files
```

## 9. Result

**PASS**

All 16 history tree tests pass. Full test suite: 128 passed, 0 failures.
All required output files created. JSON outputs valid.

## 10. Notes

- Edge count (17) is higher than a minimal tree because the full bipartite
  graph is used when group size ≤ 4 nodes; for 3×3 foundational→direct_prior
  that yields 9 edges. The heuristic can be adjusted by lowering
  `_MAX_GROUP_FOR_FULL_BIPARTITE`.
- Role deduplication resolves `history_foundational` over weaker roles when
  a citation appears in multiple sections with different classifications.
- The real paper has no `history_direct_prior` nodes — all DL/AI references
  were classified as `history_background` by the Step 06 classifier. This
  is expected given the conservative keyword-matching approach.
- No external API enrichment or true dependency inference is performed.

## 11. Next Step

**Step 12 — Baseline Graph Builder**

Optionally: Step 11 — Baseline Graph Model (if baseline node/edge models need
formalizing before Step 12 implementation).
