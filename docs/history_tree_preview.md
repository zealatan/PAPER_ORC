# History Tree Preview

## Purpose

This preview converts history citation roles (produced by Step 06 Citation Role Classifier) into a rough suggested reading path — a heuristic approximation of the paper's intellectual lineage before the full History Tree Builder is implemented.

## Inputs

- `CitationRole` list (`examples/sample_citation_roles.json`)
- Bibliography mapping (`examples/sample_citation_to_bibliography_map.json`)

## Outputs

- `history_tree_preview.mmd` — Mermaid LR flowchart with subgraphs per role group
- `history_tree_preview.json` — JSON graph with nodes and preview edges
- `history_tree_preview.md` — Human-readable reading path table
- `history_tree_preview_table.md` — Compact history candidate table

## How It Works

1. Load all `CitationRole` records from Step 06 output.
2. Filter to history roles only: `history_foundational`, `history_direct_prior`, `history_background`.
3. Deduplicate by `citation_id`, keeping the highest-priority role when a reference is cited in multiple sections.
4. Sort within each role group by publication year (ascending), then by citation number.
5. Emit preview edges: every foundational node → first direct-prior node; every direct-prior node → first background node; every background node → target paper.
6. Render as Mermaid `flowchart LR` with three subgraphs (Foundational, Direct Prior, Background).

## Difference from Final History Tree Builder

| Aspect | Step 06b Preview | Step 10 Final Builder |
|---|---|---|
| Edge logic | Role-group ordering heuristic | Inferred from citation text and metadata |
| Year data | From bibliography entry | May query external APIs |
| Graph structure | Linear flow: F → P → B → T | DAG with real citation-to-citation dependencies |
| Export | Mermaid + JSON | Full graph model with HistoryTreeNode objects |
| Importance | Not computed | Computed by citation frequency and role weight |

## Limitations

- Does not infer real citation-to-citation dependencies between referenced papers.
- Does not query external metadata (e.g., Semantic Scholar, CrossRef).
- Depends on rule-based citation role classification — context bleed can cause "introduced" in a neighbor's context window to fire `history_foundational` for an adjacent citation.
- Ordering by year is only as accurate as the bibliography entry parser.
- A multi-section citation is deduplicated to a single role; the highest-priority role wins.
