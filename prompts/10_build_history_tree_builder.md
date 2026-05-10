# Step 10 — History Tree Builder

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/10_build_history_tree_builder.md

If the file already exists, overwrite it with this full prompt.

Every Claude Code prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Implement the PaperNav History Tree Builder.

This step converts citation role classification outputs into a formal History Tree.

The History Tree should visualize how the target paper is positioned on top of prior work.

Input:

- CitationRole outputs from Step 06 / Step 06c
- Bibliography mapping from Step 05

Output:

- structured history_tree.json
- Markdown reading path
- Mermaid graph
- HTML preview if feasible
- section-aware history citation summary

This is the first formal graph-building step of PaperNav.

Do not implement Baseline Graph in this step.
Do not implement final importance scoring in this step.
Do not implement external API enrichment in this step.

---

## Project Context

PaperNav is a section-aware paper intelligence agent.

Current pipeline:

Paper
  -> Step 03 Paper Parser
  -> Step 04 Citation Extractor
  -> Step 05 Bibliography Mapper
  -> Step 06 Citation Role Classifier
  -> Step 06c Precision Patch
  -> Step 10 History Tree Builder

The main idea:

Introduction / Related Work / Background citations
  -> history_foundational
  -> history_direct_prior
  -> history_background
  -> History Tree

Experiment / Evaluation / Results citations
  -> baseline / competitor / metric roles
  -> Baseline Graph later

This step only builds the History Tree.

---

## Input Files

Primary synthetic inputs:

reports/step_outputs/step_06c/reclassified_citation_roles.json
examples/sample_citation_to_bibliography_map.json

Fallback synthetic inputs if Step 06c file is missing:

examples/sample_citation_roles.json
examples/sample_citation_to_bibliography_map.json

Real paper smoke inputs:

reports/step_outputs/step_06/real_paper_citation_roles_snapshot.json
reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json

Existing quick preview:

reports/step_outputs/step_06b/history_tree_preview.json
reports/step_outputs/step_06c/history_tree_preview_after_patch.mmd

---

## Do Not Modify

Do not overwrite or delete:

README.md
assets/
examples/sample_paper.txt
examples/sample_parsed_paper.json
examples/sample_citation_mentions.json
examples/sample_bibliography_entries.json
examples/sample_citation_to_bibliography_map.json
reports/step_outputs/step_03/
reports/step_outputs/step_04/
reports/step_outputs/step_05/
reports/step_outputs/step_06/
reports/step_outputs/step_06b/
reports/step_outputs/step_06c/

Do not modify the citation role classifier unless absolutely necessary.

Do not implement Baseline Graph in this step.

---

## Files to Create or Modify

Modify:

src/papernav/graph/history_tree.py

Create or update:

tests/test_history_tree_builder.py
docs/history_tree_builder.md

Create:

examples/sample_history_tree.json
reports/step_outputs/step_10/history_tree.json
reports/step_outputs/step_10/history_tree.md
reports/step_outputs/step_10/history_tree.mmd
reports/step_outputs/step_10/history_tree_table.md
reports/step_outputs/step_10/history_tree_summary.md
reports/step_outputs/step_10/real_paper_history_tree_summary.md
reports/step_outputs/step_10/report.md

Optional if feasible:

reports/step_outputs/step_10/history_tree.html
reports/step_outputs/step_10/real_paper_history_tree.json
reports/step_outputs/step_10/real_paper_history_tree.mmd

Update if useful:

prompts/PROMPT_INDEX.md

---

## Required Public Functions

Implement these functions in:

src/papernav/graph/history_tree.py

Required functions:

load_citation_roles(path: str) -> list[CitationRole]

load_bibliography_map(path: str) -> dict[str, BibliographyEntry]

select_history_roles(
    roles: list[CitationRole]
) -> list[CitationRole]

build_history_tree(
    roles: list[CitationRole],
    bibliography_map: dict[str, BibliographyEntry] | None = None,
    target_title: str = "Target Paper",
    paper_id: str = "sample_paper"
) -> dict

save_history_tree(
    tree: dict,
    output_path: str
) -> None

render_history_tree_markdown(
    tree: dict
) -> str

render_history_tree_mermaid(
    tree: dict
) -> str

generate_step10_outputs(
    roles_path: str = "reports/step_outputs/step_06c/reclassified_citation_roles.json",
    bibliography_map_path: str = "examples/sample_citation_to_bibliography_map.json",
    output_dir: str = "reports/step_outputs/step_10"
) -> None

Optional:

render_history_tree_html(
    mermaid_text: str,
    output_path: str
) -> None

---

## Model Requirements

Use existing models from:

src/papernav/models.py

Use:

- CitationRole
- BibliographyEntry
- HistoryTreeNode
- is_history_role

Do not require a new global model unless necessary.

Edges can be represented as dictionaries:

{
  "source": "ref_2",
  "target": "ref_5",
  "edge_type": "history_flow",
  "reason": "Foundational work precedes direct prior work",
  "weight": 1.0
}

---

## History Role Selection

Only include roles:

history_foundational
history_direct_prior
history_background

Exclude:

baseline_direct
baseline_extended
competitor
benchmark_source
metric_source
supporting_evidence
misc

References section anchors should not appear in the History Tree.

---

## Node Construction Rules

For each selected CitationRole, create one HistoryTreeNode.

Node fields:

node_id:
  citation_id, e.g. ref_2

citation_id:
  citation_id from CitationRole

title:
  title from bibliography map if available
  otherwise citation_id

year:
  year from bibliography map if available
  otherwise None

role:
  citation role

citation_frequency:
  number of times the same citation_id appears among selected history roles

parent_id:
  optional; can be assigned heuristically or left None in node object

metadata:
  include:
    section_name
    confidence
    evidence_sentence
    reason

Deduplicate nodes by citation_id, but preserve citation frequency.

If the same citation appears multiple times with different history roles, choose the strongest role using this priority:

history_foundational
history_direct_prior
history_background

Also preserve all evidence sentences in metadata if possible.

---

## Tree Ordering Rules

Sort nodes by:

1. role priority:
   - history_foundational
   - history_direct_prior
   - history_background

2. year ascending if available

3. citation_id numeric order

If year is missing, place after nodes with known year within the same role group.

---

## Edge Construction Rules

This is an MVP History Tree.

Create a directed acyclic graph using heuristic edges.

Required structure:

history_foundational nodes
  -> history_direct_prior nodes
  -> history_background nodes
  -> target_paper

If a role group is missing, connect available groups directly.

Examples:

Case 1:

foundational exists, direct prior exists, background exists:

foundational representative(s) -> direct prior representative(s)
direct prior representative(s) -> background representative(s)
background representative(s) -> target_paper

Case 2:

foundational exists, direct prior exists, no background:

foundational -> direct prior
direct prior -> target_paper

Case 3:

only foundational exists:

foundational -> target_paper

Case 4:

no history candidates:

empty tree with target_paper only and clear warning in summary.

For multiple nodes in a group:

- connect each node in a previous group to each node in the next group only if the group size is small
- if group size is large, connect representative nodes to avoid clutter
- for MVP synthetic fixture, simple readable connections are preferred over dense complete bipartite graph

Edge reason examples:

"Foundational work precedes direct prior work in the preview history path."

"Direct prior work provides immediate context for the target paper."

"Background citation connects to the target paper as supporting context."

---

## Target Node

Always add a target node:

{
  "node_id": "target_paper",
  "citation_id": null,
  "title": target_title,
  "year": null,
  "role": "target",
  "citation_frequency": 1,
  "parent_id": null,
  "metadata": {
    "paper_id": paper_id
  }
}

The final layer should connect to target_paper.

---

## history_tree.json Structure

Create valid JSON:

{
  "paper_id": "sample_paper",
  "target_node": {...},
  "summary": {
    "history_candidate_mentions": 0,
    "unique_history_nodes": 0,
    "history_foundational_count": 0,
    "history_direct_prior_count": 0,
    "history_background_count": 0,
    "edge_count": 0
  },
  "nodes": [],
  "edges": [],
  "reading_path": []
}

reading_path should be a list of node IDs in the suggested reading order.

---

## Mermaid Output Requirements

Create:

reports/step_outputs/step_10/history_tree.mmd

Use Mermaid:

flowchart LR

Use subgraphs:

subgraph F[Foundational Work]
...
end

subgraph P[Direct Prior Work]
...
end

subgraph B[Background Context]
...
end

subgraph T[Target]
...
end

Use readable labels:

ref_2["ref_2<br/>Robust Frequency and Timing Synchronization<br/>1997"]

Truncate long titles to around 55 characters.

Target node:

target_paper["Target Paper"]

Edges should follow the tree edges from history_tree.json.

Mermaid must be valid enough for GitHub rendering.

---

## Markdown Output Requirements

Create:

reports/step_outputs/step_10/history_tree.md

Use this structure:

# History Tree

## Purpose

Explain this tree shows the historical learning path behind the target paper.

## Summary

| Metric | Value |
|---|---:|

## Suggested Reading Path

| Order | Citation ID | Role | Year | Title | Evidence |
|---:|---|---|---:|---|---|

## Tree Edges

| Source | Target | Reason |
|---|---|---|

## Mermaid Graph

Reference:

reports/step_outputs/step_10/history_tree.mmd

## Notes

Mention this is heuristic and section-aware.

---

## Table Output Requirements

Create:

reports/step_outputs/step_10/history_tree_table.md

Include:

# History Tree Candidate Table

| Citation ID | Role | Year | Citation Frequency | Title | Section | Confidence | Evidence Preview |
|---|---|---:|---:|---|---|---|---|

---

## Summary Output Requirements

Create:

reports/step_outputs/step_10/history_tree_summary.md

Include:

# History Tree Summary

## Candidate Counts

## Role Distribution

## Reading Path

## Interpretation

Explain what the history tree suggests about the field.

For the synthetic fixture, it should mention:

- foundational timing synchronization / specification papers
- direct prior AI/deep-learning related works
- target paper as the final node

Do not hallucinate beyond bibliography titles and evidence sentences.

---

## Real Paper Smoke Test

If these files exist:

reports/step_outputs/step_06/real_paper_citation_roles_snapshot.json
reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json

Then build a real paper history tree smoke output.

Create:

reports/step_outputs/step_10/real_paper_history_tree_summary.md

The summary must include:

- whether real role file exists
- whether real bibliography map exists
- number of history role mentions
- number of unique history nodes
- role distribution
- note that role classification and PDF extraction are heuristic

Optional:

Create:

reports/step_outputs/step_10/real_paper_history_tree.json
reports/step_outputs/step_10/real_paper_history_tree.mmd

Do not fail the whole step if real paper graph is imperfect.

---

## HTML Output Optional

If easy, create:

reports/step_outputs/step_10/history_tree.html

It can be a simple HTML file embedding Mermaid from CDN.

Do not fail the step if HTML output is skipped.

If created, mention it in the final report.

---

## Documentation Requirements

Create or update:

docs/history_tree_builder.md

Include:

# History Tree Builder

## Purpose

Explain that this module turns history citation roles into a visual learning path.

## Inputs

- CitationRole list
- BibliographyEntry mapping

## Outputs

- history_tree.json
- history_tree.mmd
- history_tree.md
- history_tree_summary.md

## Included Roles

- history_foundational
- history_direct_prior
- history_background

## Excluded Roles

- baseline_direct
- competitor
- benchmark_source
- metric_source
- supporting_evidence
- misc

## Edge Heuristic

Explain group-based ordering:

foundational -> direct prior -> background -> target paper

## Difference from Quick Preview

Explain that Step 06b was a lightweight preview, while Step 10 creates structured JSON, deduplicated nodes, citation frequency, edge records, and formal exports.

## Limitations

- Does not infer true citation dependencies between referenced papers
- No external metadata enrichment yet
- Role classification errors can affect graph quality
- Edge reasoning is heuristic

---

## Test Requirements

Create or update:

tests/test_history_tree_builder.py

Tests must cover:

1. select_history_roles includes history_foundational
2. select_history_roles includes history_direct_prior
3. select_history_roles includes history_background
4. select_history_roles excludes baseline_direct
5. select_history_roles excludes misc
6. build_history_tree creates target_paper node
7. build_history_tree deduplicates repeated citation_id
8. build_history_tree computes citation_frequency
9. build_history_tree creates at least one edge when history nodes exist
10. build_history_tree reading_path ends with target_paper
11. render_history_tree_mermaid returns flowchart LR
12. render_history_tree_markdown includes Suggested Reading Path
13. save_history_tree writes valid JSON
14. generate_step10_outputs creates required files
15. synthetic fixture creates a non-empty history tree
16. real paper smoke test:
    - if real role files exist, build real tree and return dict
    - if missing, skip with pytest.skip

Do not make exact edge counts too brittle if the heuristic evolves.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_history_tree_builder.py -v
python3 -m pytest -q
python3 -m json.tool reports/step_outputs/step_10/history_tree.json > /tmp/history_tree_check.json
python3 -m json.tool examples/sample_history_tree.json > /tmp/sample_history_tree_check.json
ls -l reports/step_outputs/step_10/

---

## Final Report Format

At the end, report exactly:

# Step 10 — History Tree Builder — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/10_build_history_tree_builder.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files.

## 4. History Tree Functions Implemented

List:

- load_citation_roles
- load_bibliography_map
- select_history_roles
- build_history_tree
- save_history_tree
- render_history_tree_markdown
- render_history_tree_mermaid
- generate_step10_outputs

and optional functions if any.

## 5. Synthetic History Tree Result

Report:

- history candidate mention count
- unique history node count
- role distribution
- edge count
- reading path
- output JSON path
- Mermaid path

## 6. Real Paper Smoke Result

Report:

- real role file status
- real bibliography map status
- history node count if available
- edge count if available

## 7. Visualization Outputs

List files under:

reports/step_outputs/step_10/

## 8. Tests Run

List validation commands.

## 9. Result

PASS or FAIL.

## 10. Notes

Mention limitations.

## 11. Next Step

Recommend:

Step 12 — Baseline Graph Builder

or optionally:

Step 11 — Baseline Graph Model / Step 12 — Baseline Graph Builder

---

## Success Criteria

This step is complete only when:

- prompts/10_build_history_tree_builder.md exists
- src/papernav/graph/history_tree.py implements required functions
- tests/test_history_tree_builder.py exists
- docs/history_tree_builder.md exists
- examples/sample_history_tree.json exists
- reports/step_outputs/step_10/history_tree.json exists
- reports/step_outputs/step_10/history_tree.md exists
- reports/step_outputs/step_10/history_tree.mmd exists
- reports/step_outputs/step_10/history_tree_table.md exists
- reports/step_outputs/step_10/history_tree_summary.md exists
- reports/step_outputs/step_10/real_paper_history_tree_summary.md exists
- history_tree.json is valid JSON
- sample_history_tree.json is valid JSON
- synthetic history tree is non-empty
- Mermaid graph is generated
- python3 -m compileall src passes
- python3 -m pytest tests/test_history_tree_builder.py -v passes
- python3 -m pytest -q passes
