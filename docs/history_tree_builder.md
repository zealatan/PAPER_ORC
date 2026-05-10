# History Tree Builder

## Purpose

This module turns history citation roles into a visual learning path — a directed
graph that shows how the target paper is positioned on top of prior work.
It is the first formal graph-building step in the PaperNav pipeline (Step 10).

## Inputs

- **CitationRole list** — output of the Citation Role Classifier (Step 06 / 06c)
- **BibliographyEntry mapping** — output of the Bibliography Mapper (Step 05)

## Outputs

| File | Description |
|---|---|
| `history_tree.json` | Structured tree with nodes, edges, reading path, and summary |
| `history_tree.mmd` | Mermaid flowchart diagram |
| `history_tree.md` | Markdown reading guide with tables |
| `history_tree_table.md` | Full candidate node table |
| `history_tree_summary.md` | Narrative summary and interpretation |
| `history_tree.html` | Optional HTML Mermaid preview |
| `examples/sample_history_tree.json` | Sample fixture |

## Included Roles

| Role | Meaning |
|---|---|
| `history_foundational` | Seminal works that established the problem/field |
| `history_direct_prior` | Closest prior approaches the target paper builds on |
| `history_background` | Supporting context cited in intro/related work |

## Excluded Roles

| Role | Reason |
|---|---|
| `baseline_direct` | Belongs to Baseline Graph (Step 12) |
| `baseline_extended` | Belongs to Baseline Graph |
| `competitor` | Belongs to Baseline Graph |
| `benchmark_source` | Evaluation context, not historical lineage |
| `metric_source` | Evaluation context |
| `supporting_evidence` | Not part of historical narrative |
| `misc` | Reference anchors and unclassified |

## Edge Heuristic

Edges follow group-based ordering. The pipeline uses role priority to chain
citation groups into a directed acyclic graph:

```
history_foundational  →  history_direct_prior  →  history_background  →  target_paper
```

If a role group is missing, available groups connect directly to the next available
group or to `target_paper`. For large groups (> 4 nodes), only representative nodes
(the top 2 by sort order) are used for cross-group edges to avoid a dense bipartite
graph.

## Node Deduplication

A citation may appear multiple times in the role list (e.g., cited in both
Introduction and Related Work). Nodes are deduplicated by `citation_id`.
When the same citation appears with multiple history roles, the strongest role
wins according to this priority:

1. `history_foundational`
2. `history_direct_prior`
3. `history_background`

`citation_frequency` records how many times the citation appeared as a history
role mention before deduplication.

## Difference from Quick Preview (Step 06b)

Step 06b produced a lightweight `history_tree_preview.json` as a side effect of
the precision patch. Step 10 builds the formal graph:

| Feature | Step 06b Preview | Step 10 Builder |
|---|---|---|
| Deduplicated nodes | No | Yes |
| Citation frequency | No | Yes |
| Edge records | No | Yes |
| Reading path | No | Yes |
| Mermaid subgraphs | Partial | Full |
| JSON schema | Informal | Structured |
| Markdown report | No | Yes |
| Table export | No | Yes |
| Narrative summary | No | Yes |

## Limitations

- Does not infer true citation dependencies *between* referenced papers
- No external metadata enrichment (author disambiguation, DOI lookup) yet
- Role classification errors from Step 06 propagate into the tree
- Edge reasoning is heuristic — it reflects field convention, not actual citation links
- Section detection quality affects which roles are assigned
