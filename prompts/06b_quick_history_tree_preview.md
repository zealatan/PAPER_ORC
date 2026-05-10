# Step 06b — Quick History Tree Preview

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/06b_quick_history_tree_preview.md

If the file already exists, overwrite it with this full prompt.

Every Claude Code prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Create a quick History Tree preview from the Step 06 citation role classification output.

This is not the final History Tree Builder yet.

The goal is to quickly visualize how introduction / related-work / background citations can become a historical learning path.

This step should consume:

examples/sample_citation_roles.json
examples/sample_citation_to_bibliography_map.json

and generate a simple history tree preview using only citations classified as:

history_foundational
history_direct_prior
history_background

The output should be GitHub-friendly and easy to inspect.

Do not implement the full Step 10 History Tree Builder yet.
Do not implement Baseline Graph yet.
Do not implement final importance scoring.

This is a lightweight preview step.

---

## Current Pipeline Status

Paper
  -> Step 03 Paper Parser
  -> Step 04 Citation Extractor
  -> Step 05 Bibliography Mapper
  -> Step 06 Citation Role Classifier
  -> Step 06b Quick History Tree Preview

Step 06 already produced:

- examples/sample_citation_roles.json
- reports/step_outputs/step_06/history_citation_candidates.md
- reports/step_outputs/step_06/citation_roles_snapshot.json

This step should turn the history candidates into a simple visual tree.

---

## Do Not Modify

Do not overwrite or delete:

README.md
assets/
src/papernav/citation/classifier.py
src/papernav/citation/extractor.py
src/papernav/citation/bibliography.py
examples/sample_citation_roles.json
examples/sample_citation_to_bibliography_map.json
reports/step_outputs/step_06/

Do not modify Step 06 outputs.

Do not implement full graph builder modules yet.

---

## Files to Create

Create:

reports/step_outputs/step_06b/history_tree_preview.md
reports/step_outputs/step_06b/history_tree_preview.mmd
reports/step_outputs/step_06b/history_tree_preview.json
reports/step_outputs/step_06b/history_tree_preview_table.md
reports/step_outputs/step_06b/report.md

Create or update:

docs/history_tree_preview.md

Optional:

prompts/PROMPT_INDEX.md

Add Step 06b entry if this file exists.

---

## Input Files

Use:

examples/sample_citation_roles.json
examples/sample_citation_to_bibliography_map.json

If the bibliography map is missing, still generate a preview using citation_id only.

---

## Required Behavior

Load citation roles from:

examples/sample_citation_roles.json

Load bibliography mapping from:

examples/sample_citation_to_bibliography_map.json

Select only history roles:

- history_foundational
- history_direct_prior
- history_background

Ignore:

- baseline_direct
- baseline_extended
- competitor
- benchmark_source
- metric_source
- supporting_evidence
- misc

Group selected citations by role.

The preview should create a simple directed tree-like structure:

history_foundational
  -> history_direct_prior
  -> history_background
  -> Target Paper

This is a heuristic preview. It does not need to infer real citation dependency between papers yet.

---

## Ordering Rules

Sort history candidates by:

1. role priority:
   - history_foundational first
   - history_direct_prior second
   - history_background third

2. year if available from bibliography entry

3. citation_id numeric order

If year is missing, put it after entries with known years within the same role group.

---

## Node Labels

Each node label should include:

- citation_id
- title if available
- year if available
- role

Example:

ref_2
Robust Frequency and Timing Synchronization...
1997
history_foundational

If title is long, truncate it to around 50 characters in Mermaid labels.

---

## history_tree_preview.json Requirements

Create valid JSON with this structure:

{
  "paper_id": "sample_paper",
  "target_node": {
    "node_id": "target_paper",
    "label": "Target Paper",
    "role": "target"
  },
  "summary": {
    "history_candidate_count": 0,
    "history_foundational_count": 0,
    "history_direct_prior_count": 0,
    "history_background_count": 0
  },
  "nodes": [],
  "edges": []
}

Each node should include:

{
  "node_id": "ref_2",
  "citation_id": "ref_2",
  "title": "...",
  "year": 1997,
  "role": "history_foundational",
  "section_name": "introduction"
}

Each edge should include:

{
  "source": "ref_2",
  "target": "ref_5",
  "edge_type": "preview_history_flow",
  "reason": "Preview edge based on role ordering"
}

The final edge should connect the last history node to:

target_paper

If no history candidates exist, create a valid JSON with empty nodes and edges and explain in report.md.

---

## history_tree_preview.mmd Requirements

Create a valid Mermaid flowchart.

Use:

flowchart LR

Structure:

Foundational citations
  -> Direct prior citations
  -> Background citations
  -> Target Paper

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

Then connect these subgraphs through representative nodes if possible.

Example structure:

flowchart LR
    subgraph F[Foundational Work]
        ref_2["ref_2<br/>Robust Frequency and Timing Synchronization<br/>1997"]
        ref_3["ref_3<br/>ML Estimation of Time and Frequency Offset<br/>1997"]
    end

    subgraph P[Direct Prior Work]
        ref_5["ref_5<br/>Deep Learning Based Channel Estimation<br/>2019"]
    end

    subgraph B[Background Context]
        ref_8["ref_8<br/>CNN-Aided Receiver Design<br/>2021"]
    end

    T["Target Paper"]

    ref_2 --> ref_5
    ref_3 --> ref_5
    ref_5 --> ref_8
    ref_8 --> T

If there are multiple nodes in the same group, connect each group to the next group using a simple representative connection.

Do not over-engineer.

---

## history_tree_preview.md Requirements

Create a human-readable preview report.

Use this structure:

# Quick History Tree Preview

## Purpose

Explain that this is a lightweight preview generated from Step 06 citation roles.

## Input Files

List input files.

## History Candidate Summary

| Role | Count |
|---|---:|

## Reading Path Preview

List citations in suggested reading order.

Table:

| Order | Citation ID | Role | Year | Title | Section | Evidence |
|---:|---|---|---:|---|---|---|

## Mermaid Preview

Reference:

reports/step_outputs/step_06b/history_tree_preview.mmd

## Notes

Mention that this is not the final graph builder. It is a quick preview based on role grouping and year ordering.

---

## history_tree_preview_table.md Requirements

Create a compact table:

# History Candidate Table

| Citation ID | Role | Year | Title | Section | Evidence Preview |
|---|---|---:|---|---|---|

Include only history candidates.

---

## docs/history_tree_preview.md Requirements

Create or update:

docs/history_tree_preview.md

Include:

# History Tree Preview

## Purpose

Explain that this preview converts history citation roles into a rough learning path.

## Inputs

- CitationRole list
- Bibliography mapping

## Outputs

- Mermaid history tree preview
- JSON preview graph
- Markdown reading path

## Difference from Final History Tree Builder

Explain that this preview uses simple role/year ordering.

The final builder will later support richer graph logic, edge reasoning, layout, and export.

## Limitations

- Does not infer real citation dependencies between referenced papers
- Does not query external metadata
- Depends on rule-based citation role classification
- Uses heuristic ordering

---

## report.md Requirements

Create:

reports/step_outputs/step_06b/report.md

Use:

# Step 06b Report — Quick History Tree Preview

## Status

PASS or FAIL

## Input Files

## Output Files

## History Candidate Counts

## Generated Preview

## Limitations

## Next Step

Recommend:

Step 10 — History Tree Builder

or:

Step 07/08 — Milestone 1 Summary Report

---

## Validation Commands

Run:

python3 -m json.tool reports/step_outputs/step_06b/history_tree_preview.json > /tmp/history_tree_preview_check.json
ls -l reports/step_outputs/step_06b/

If pytest exists, run:

python3 -m pytest -q

---

## Final Report Format

At the end, report exactly:

# Step 06b — Quick History Tree Preview — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/06b_quick_history_tree_preview.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files if any.

## 4. History Candidate Result

Report:

- total history candidates
- history_foundational count
- history_direct_prior count
- history_background count
- generated node count
- generated edge count

## 5. Visualization Outputs

List files under:

reports/step_outputs/step_06b/

## 6. Validation Commands

List commands run.

## 7. Result

PASS or FAIL.

## 8. Notes

Mention limitations.

## 9. Next Step

Recommend:

Step 10 — History Tree Builder

Also mention that Step 07/08 may optionally summarize Milestone 1 before moving to full graph construction.

---

## Success Criteria

This step is complete only when:

- prompts/06b_quick_history_tree_preview.md exists and contains this full prompt
- reports/step_outputs/step_06b/history_tree_preview.md exists
- reports/step_outputs/step_06b/history_tree_preview.mmd exists
- reports/step_outputs/step_06b/history_tree_preview.json exists
- reports/step_outputs/step_06b/history_tree_preview_table.md exists
- reports/step_outputs/step_06b/report.md exists
- docs/history_tree_preview.md exists
- history_tree_preview.json is valid JSON
- history candidates are selected from examples/sample_citation_roles.json
- Mermaid preview is generated
- python3 -m pytest -q passes if run
