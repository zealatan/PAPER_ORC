# Step 06 — Citation Role Classifier

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/06_build_citation_role_classifier.md

If the file already exists, overwrite it with this full prompt.

Every Claude Code prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Implement the PaperNav Citation Role Classifier.

This step takes:

- CitationMention list from Step 04
- BibliographyEntry mapping from Step 05
- section names
- sentence-level citation context

and assigns a semantic role to each citation mention.

This is the first step where PaperNav starts to understand why each reference appears in the paper.

Do not implement History Tree or Baseline Graph in this step.
Do not implement final importance scoring in this step.

This step only classifies citation roles.

---

## Current Pipeline

Paper
  -> Step 03 Paper Parser
  -> ParsedPaper
  -> Step 04 Citation Extractor
  -> CitationMention list
  -> Step 05 Bibliography Mapper
  -> BibliographyEntry mapping
  -> Step 06 Citation Role Classifier
  -> CitationRole list

Later steps will use this output:

- Step 10 History Tree Builder
- Step 12 Baseline Graph Builder
- Step 15 Topic Relevance Agent
- Step 20 Final Importance Judge

---

## Input Files

Synthetic fixture inputs:

examples/sample_parsed_paper.json
examples/sample_citation_mentions.json
examples/sample_bibliography_entries.json
examples/sample_citation_to_bibliography_map.json

Real paper smoke inputs:

reports/step_outputs/step_03/real_paper_parsed_snapshot.json
reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json
reports/step_outputs/step_05/real_paper_bibliography_entries_snapshot.json
reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json

Synthetic fixture expected behavior:

- introduction citations should become history roles
- related_work citations should become history roles
- experiment citations should become baseline / competitor / benchmark / metric roles
- results citations should become competitor / metric / supporting evidence roles
- discussion citations should become supporting evidence roles
- references section anchors should become misc

---

## Do Not Modify

Do not overwrite or delete:

README.md
assets/
prompts/00_bootstrap_repository.md
prompts/01_define_common_models.md
prompts/02_add_sample_paper_fixture.md
prompts/02b_complete_sample_fixture_docs_and_visual_outputs.md
prompts/02c_add_real_paper_smoke_fixture.md
prompts/03_build_paper_parser.md
prompts/04_build_citation_extractor.md
prompts/05_build_bibliography_mapper.md

Do not modify sample input files:

examples/sample_paper.txt
examples/sample_parsed_paper.json
examples/sample_citation_mentions.json
examples/sample_bibliography_entries.json
examples/sample_citation_to_bibliography_map.json

Do not implement graph building in this step.

---

## Files to Create or Modify

Modify:

src/papernav/citation/classifier.py

Create or update:

tests/test_citation_role_classifier.py
docs/citation_role_classifier.md

Create:

examples/sample_citation_roles.json
reports/step_outputs/step_06/citation_role_summary.md
reports/step_outputs/step_06/citation_role_flow.mmd
reports/step_outputs/step_06/citation_roles_snapshot.json
reports/step_outputs/step_06/history_citation_candidates.md
reports/step_outputs/step_06/baseline_citation_candidates.md
reports/step_outputs/step_06/real_paper_citation_role_summary.md
reports/step_outputs/step_06/report.md

Optional:

reports/step_outputs/step_06/real_paper_citation_roles_snapshot.json

---

## Required Public Functions

Implement these functions in:

src/papernav/citation/classifier.py

Functions:

classify_citation_role(
    mention: CitationMention,
    bibliography_entry: BibliographyEntry | None = None
) -> CitationRole

classify_citation_roles(
    mentions: list[CitationMention],
    bibliography_map: dict[str, BibliographyEntry] | None = None
) -> list[CitationRole]

save_citation_roles(
    roles: list[CitationRole],
    output_path: str
) -> None

generate_step06_outputs(
    citation_mentions_path: str = "examples/sample_citation_mentions.json",
    bibliography_map_path: str = "examples/sample_citation_to_bibliography_map.json",
    output_dir: str = "reports/step_outputs/step_06"
) -> None

Use existing models from:

src/papernav/models.py

Use:

CitationMention
BibliographyEntry
CitationRole
CITATION_ROLE_LABELS
CONFIDENCE_LABELS
is_history_role
is_baseline_role

---

## Allowed Citation Role Labels

Use only these role labels:

history_foundational
history_direct_prior
history_background
baseline_direct
baseline_extended
competitor
benchmark_source
metric_source
supporting_evidence
misc

Allowed confidence labels:

low
medium
high

---

## Rule-Based Classification Requirements

This MVP classifier should be deterministic and rule-based.

Do not call external LLM APIs.

Use section name and sentence-level keyword signals.

Normalize section_name to lowercase before classification.

---

## Section-Based Default Rules

Default role by section:

abstract:
  misc

introduction:
  history_background

related_work:
  history_direct_prior

background:
  history_background

method:
  supporting_evidence

experiment:
  baseline_direct

experiments:
  baseline_direct

evaluation:
  baseline_direct

results:
  competitor

discussion:
  supporting_evidence

conclusion:
  supporting_evidence

references:
  misc

If section is unknown:

misc

---

## Keyword-Based Override Rules

Keyword matching should be case-insensitive.

Use the citation sentence and context_window.

History foundational keywords:

first proposed
pioneering
classical
seminal
introduced
foundation
foundational
standardized
specification

If found in introduction, related_work, or background:
  role = history_foundational
  confidence = high

History direct prior keywords:

prior work
previous work
previous studies
recent work
recent works
related work
has been explored
have been explored
existing methods
existing approaches

If found in introduction, related_work, or background:
  role = history_direct_prior
  confidence = high or medium

Baseline direct keywords:

we compare
compare with
compared with
compared against
comparison with
baseline
baselines
against
evaluate against

If found in experiment, experiments, evaluation, or results:
  role = baseline_direct
  confidence = high

Competitor keywords:

outperform
outperforms
outperformed
state-of-the-art
sota
competitive
competitor
competing method
competing approach

If found in experiment, evaluation, results, or discussion:
  role = competitor
  confidence = high or medium

Benchmark source keywords:

benchmark
dataset
test set
evaluation protocol
verilogeval
suite
workload
corpus

If found:
  role = benchmark_source
  confidence = high or medium

Metric source keywords:

metric
score
measurement
accuracy
pass rate
success rate
ber
latency
throughput
f1
precision
recall

If found in experiment, evaluation, results, or discussion:
  role = metric_source
  confidence = medium

Supporting evidence keywords:

shown
observed
reported
demonstrated
evidence
indicates
suggests
according to

If found outside experiment baseline contexts:
  role = supporting_evidence
  confidence = medium

---

## Precedence Rules

When multiple rules match, use this priority order:

1. references section -> misc
2. benchmark_source
3. baseline_direct
4. competitor
5. metric_source
6. history_foundational
7. history_direct_prior
8. supporting_evidence
9. section default
10. misc

Reason: experiment-related benchmark/baseline relations are more specific than generic history terms.

However, history_foundational should win in introduction/related_work/background if the sentence has strong foundational keywords and does not include compare/baseline/benchmark language.

Keep implementation simple and documented.

---

## CitationRole Output Requirements

Each CitationRole must include:

citation_id
role
confidence
evidence_sentence
section_name
reason

The reason field should be a short sentence such as:

"Section 'experiment' and keyword 'baseline' indicate direct baseline usage."

or:

"Section 'introduction' and keyword 'classical' indicate foundational history citation."

---

## Reference Section Handling

Citations in the references section are bibliography anchors.

Classify them as:

role = misc
confidence = high
reason = "Reference-section anchor, not an in-text citation role."

This is important because Step 06 should classify semantic citation roles in the body, while leaving bibliography anchors as misc.

---

## Synthetic Fixture Expectations

When running on the synthetic fixture:

examples/sample_citation_mentions.json
examples/sample_citation_to_bibliography_map.json

Expected high-level behavior:

- total CitationRole count should match CitationMention count
- references section anchors should be misc
- introduction and related_work should produce history roles
- experiment should produce baseline / competitor / benchmark / metric roles
- results should produce competitor / metric / supporting evidence roles
- discussion should produce supporting_evidence or misc
- at least one history_foundational role should exist
- at least one baseline_direct role should exist
- at least one competitor or benchmark_source role should exist

Do not make exact role counts too brittle unless the synthetic fixture is stable enough.

---

## Real Paper Smoke Test

If these files exist:

reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json
reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json

Then run citation role classification on the real paper.

Create:

reports/step_outputs/step_06/real_paper_citation_role_summary.md

The summary must include:

- whether real citation mentions exist
- whether real bibliography map exists
- total roles classified
- role count table
- section-level role count table
- top 10 non-misc citation roles
- note that rule-based classification is heuristic

Optional:

Create:

reports/step_outputs/step_06/real_paper_citation_roles_snapshot.json

Do not fail the entire step if real paper classification is imperfect.

---

## Intermediate Visualization Outputs

Create:

reports/step_outputs/step_06/citation_role_summary.md

It must include:

# Citation Role Summary

## Overall Role Counts

| Role | Count |
|---|---:|

## Role Counts by Section

| Section | Role | Count |
|---|---|---:|

## History Citation Candidates

| Citation ID | Title | Section | Role | Confidence | Evidence |
|---|---|---|---|---|---|

## Baseline / Experiment Citation Candidates

| Citation ID | Title | Section | Role | Confidence | Evidence |
|---|---|---|---|---|---|

## Misc / Reference Anchors

| Citation ID | Section | Count |
|---|---|---:|

Create:

reports/step_outputs/step_06/citation_role_flow.mmd

Use this Mermaid flowchart:

flowchart TD
    A[Citation Mentions] --> B{Section}
    B --> C[Introduction / Related Work / Background]
    B --> D[Experiment / Evaluation / Results]
    B --> E[References]
    C --> F[History Roles]
    D --> G[Baseline / Competitor / Metric Roles]
    E --> H[Misc Reference Anchors]
    F --> I[History Tree Candidates]
    G --> J[Baseline Graph Candidates]
    H --> K[Ignored for Role Graphs]
    I --> L[Step 10 History Tree Builder]
    J --> M[Step 12 Baseline Graph Builder]

Create valid JSON:

reports/step_outputs/step_06/citation_roles_snapshot.json

Also create:

examples/sample_citation_roles.json

Create:

reports/step_outputs/step_06/history_citation_candidates.md

It should list citations whose roles are:

history_foundational
history_direct_prior
history_background

Create:

reports/step_outputs/step_06/baseline_citation_candidates.md

It should list citations whose roles are:

baseline_direct
baseline_extended
competitor
benchmark_source
metric_source

---

## Documentation Requirements

Create or update:

docs/citation_role_classifier.md

Include:

# Citation Role Classifier

## Purpose

Explain that this module classifies why each citation appears in a paper.

## Inputs

- CitationMention list
- BibliographyEntry mapping

## Outputs

- CitationRole list
- citation_roles.json
- role summary tables

## Role Labels

Explain all role labels.

## Rule-Based MVP

Explain section-based and keyword-based rules.

## Reference Section Handling

Explain why references section anchors are classified as misc.

## Synthetic Fixture

Explain expected roles in the synthetic paper.

## Real Paper Smoke Test

Explain heuristic behavior on RTLFixer.

## Limitations

Mention:

- rule-based only
- no LLM reasoning yet
- no semantic similarity yet
- exact role classification can be imperfect
- multi-purpose citations may need richer classification later

---

## Test Requirements

Create or update:

tests/test_citation_role_classifier.py

Tests must cover:

1. introduction + "classical" -> history_foundational
2. introduction + "recent works" -> history_direct_prior
3. introduction default -> history_background
4. experiment + "baseline" -> baseline_direct
5. experiment + "compare against" -> baseline_direct
6. results + "outperform" -> competitor
7. sentence with "benchmark" -> benchmark_source
8. sentence with "metric" or "accuracy" -> metric_source
9. discussion + "reported" -> supporting_evidence
10. references section -> misc
11. classify_citation_roles returns same length as mentions
12. all returned roles are valid CITATION_ROLE_LABELS
13. all confidence values are valid CONFIDENCE_LABELS
14. synthetic fixture produces at least one history role
15. synthetic fixture produces at least one baseline or competitor role
16. save_citation_roles writes valid JSON
17. generate_step06_outputs creates required visualization files
18. real paper role classification smoke test:
    - If real mentions exist, classification runs and returns a list
    - If missing, skip with pytest.skip

Use pytest.

Do not make real paper exact role counts brittle.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_citation_role_classifier.py -v
python3 -m pytest -q
python3 -m json.tool examples/sample_citation_roles.json > /tmp/sample_citation_roles_check.json
python3 -m json.tool reports/step_outputs/step_06/citation_roles_snapshot.json > /tmp/citation_roles_snapshot_check.json
ls -l reports/step_outputs/step_06/

---

## Final Report Format

At the end, report exactly:

# Step 06 — Citation Role Classifier — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/06_build_citation_role_classifier.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files.

## 4. Classifier Functions Implemented

List:

- classify_citation_role
- classify_citation_roles
- save_citation_roles
- generate_step06_outputs

## 5. Synthetic Fixture Role Result

Report:

- total roles
- role counts
- section-level role counts
- history candidate count
- baseline/experiment candidate count
- misc/reference anchor count
- output JSON paths

## 6. Real Paper Smoke Result

Report:

- real citation mention status
- real bibliography map status
- classification status
- role count summary if available

## 7. Visualization Outputs

List files under:

reports/step_outputs/step_06/

## 8. Tests Run

List validation commands.

## 9. Result

PASS or FAIL.

## 10. Notes

Mention limitations.

## 11. Next Step

Recommend:

Step 10 — History Tree Builder

But also note:

Step 07-08 may optionally produce final Milestone 1 report before moving to graph construction.

---

## Success Criteria

This step is complete only when:

- prompts/06_build_citation_role_classifier.md exists and contains this full prompt
- src/papernav/citation/classifier.py implements classify_citation_role
- src/papernav/citation/classifier.py implements classify_citation_roles
- src/papernav/citation/classifier.py implements save_citation_roles
- src/papernav/citation/classifier.py implements generate_step06_outputs
- tests/test_citation_role_classifier.py exists
- docs/citation_role_classifier.md exists
- examples/sample_citation_roles.json exists
- reports/step_outputs/step_06/citation_role_summary.md exists
- reports/step_outputs/step_06/citation_role_flow.mmd exists
- reports/step_outputs/step_06/citation_roles_snapshot.json exists
- reports/step_outputs/step_06/history_citation_candidates.md exists
- reports/step_outputs/step_06/baseline_citation_candidates.md exists
- reports/step_outputs/step_06/real_paper_citation_role_summary.md exists
- all JSON outputs are valid
- synthetic fixture role classification works
- real paper smoke classification is handled as success or skipped
- python3 -m compileall src passes
- python3 -m pytest tests/test_citation_role_classifier.py -v passes
- python3 -m pytest -q passes
