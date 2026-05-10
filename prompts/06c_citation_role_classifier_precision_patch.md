# Step 06c — Citation Role Classifier Precision Patch

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/06c_citation_role_classifier_precision_patch.md

If the file already exists, overwrite it with this full prompt.

Every Claude Code prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Patch the Step 06 Citation Role Classifier to reduce false role assignments caused by context-window keyword bleed.

The current Step 06b report found this issue:

- Some citations were classified as history_foundational because keywords such as "introduced" appeared in the neighboring context_window.
- ref_5 and ref_8 were classified as history_foundational, but they are more accurately history_direct_prior.
- The classifier should rely primarily on the citation sentence, not the broader context window, for strong role decisions.

This patch should improve citation role precision before the full History Tree Builder is implemented.

Do not implement the full History Tree Builder in this step.
Do not implement Baseline Graph in this step.
Do not change the parser, citation extractor, or bibliography mapper unless absolutely necessary.

---

## Current Inputs

Use existing Step 04/05/06 outputs:

examples/sample_citation_mentions.json
examples/sample_citation_to_bibliography_map.json
examples/sample_citation_roles.json

Existing Step 06b preview:

reports/step_outputs/step_06b/history_tree_preview.json
reports/step_outputs/step_06b/history_tree_preview.md
reports/step_outputs/step_06b/report.md

---

## Problem to Fix

The current classifier uses citation sentence plus context_window too broadly.

This can cause role misclassification.

Example issue:

A citation's own sentence may indicate "recent deep learning work", but a neighboring sentence in context_window contains "introduced" or "classical".

The classifier then incorrectly assigns:

history_foundational

instead of:

history_direct_prior

or:

history_background

---

## Desired Behavior

Use a two-level text signal strategy:

1. Primary text:
   mention.sentence

2. Secondary text:
   mention.context_window

Strong role classification must primarily use mention.sentence.

context_window may be used only as weak supporting evidence.

---

## Files to Modify

Modify:

src/papernav/citation/classifier.py
tests/test_citation_role_classifier.py

Create or update:

reports/step_outputs/step_06c/classifier_precision_patch_summary.md
reports/step_outputs/step_06c/before_after_role_comparison.md
reports/step_outputs/step_06c/reclassified_citation_roles.json
reports/step_outputs/step_06c/history_tree_preview_after_patch.mmd
reports/step_outputs/step_06c/report.md

Update if useful:

docs/citation_role_classifier.md
prompts/PROMPT_INDEX.md

Do not delete old Step 06 or Step 06b outputs.

---

## Required Classifier Changes

Update classify_citation_role() in:

src/papernav/citation/classifier.py

### Rule 1 — Sentence-first classification

Create normalized strings:

sentence_text = mention.sentence.lower()
context_text = mention.context_window.lower()

Strong keyword rules should check sentence_text first.

Only use context_text as fallback when sentence_text is empty or too short.

---

### Rule 2 — Foundational keyword tightening

Currently "introduced" can cause too many false history_foundational classifications.

Change foundational logic:

The role history_foundational should require:

- section is introduction, related_work, or background
- sentence contains one of the strong foundational keywords:

classical
seminal
pioneering
first proposed
foundation
foundational
standardized
specification

The word "introduced" alone should NOT be enough to assign history_foundational.

If "introduced" appears without stronger foundational keywords, classify as history_direct_prior or history_background depending on section.

---

### Rule 3 — Recent / deep learning work should be direct prior

If the sentence contains:

recent work
recent works
deep learning
neural
cnn
learning-based
data-driven
existing methods
existing approaches
has been explored
have been explored

and the section is introduction, related_work, or background:

role = history_direct_prior

confidence = medium or high depending on keyword strength

---

### Rule 4 — References section remains misc

If section_name == references:

role = misc
confidence = high
reason = Reference-section anchor, not an in-text citation role.

This must remain the highest-priority rule.

---

### Rule 5 — Benchmark and baseline rules should use sentence, not context bleed

For benchmark_source, baseline_direct, competitor, and metric_source:

- use sentence_text first
- avoid assigning benchmark_source only because "dataset" or "benchmark" appears in neighboring context_window
- context_window can be used only if the sentence is very short or lacks useful words

---

### Rule 6 — Add reason clarity

The reason field should mention whether the decision came from:

- sentence keyword
- section default
- context fallback

Example:

"Section 'introduction' and sentence keyword 'recent work' indicate direct prior work."

or:

"Section 'references' indicates bibliography anchor; classified as misc."

---

## Expected Synthetic Fixture Effect

After the patch:

- history_foundational count should likely decrease
- history_direct_prior count should likely increase
- ref_5 and ref_8 should no longer be history_foundational if their own sentence does not contain strong foundational keywords
- history candidates should still exist
- baseline / experiment candidates should still exist
- reference anchors should still be misc

Do not force exact counts unless tests can check specific known examples robustly.

---

## Required Helper / Diagnostic Output

Create a before/after comparison using:

Old roles:
examples/sample_citation_roles.json

New roles:
new classification generated by patched classifier

Save new roles to:

reports/step_outputs/step_06c/reclassified_citation_roles.json

Create:

reports/step_outputs/step_06c/before_after_role_comparison.md

Include:

| Citation ID | Section | Old Role | New Role | Title | Evidence |
|---|---|---|---|---|---|

Only include changed roles.

Also include a role count comparison table:

| Role | Before | After |
|---|---:|---:|

---

## Quick History Preview After Patch

Create:

reports/step_outputs/step_06c/history_tree_preview_after_patch.mmd

Use the same simple preview logic as Step 06b, but based on the patched roles.

It can be implemented inside this patch or generated inline in a script/helper.

It should show:

Foundational Work
  -> Direct Prior Work
  -> Background Context
  -> Target Paper

Do not overwrite Step 06b output.

---

## Documentation Update

Update docs/citation_role_classifier.md with a short section:

## Precision Patch Notes

Explain:

- classifier now prioritizes citation sentence over context_window
- context_window is fallback evidence only
- "introduced" alone no longer triggers history_foundational
- this reduces false history_foundational assignments caused by neighboring text

---

## Test Requirements

Update tests/test_citation_role_classifier.py.

Add or update tests for:

1. sentence with "classical" in introduction -> history_foundational
2. sentence with "introduced" alone in introduction -> not history_foundational
3. sentence with "recent works" in introduction -> history_direct_prior
4. sentence with "deep learning" in related_work/background -> history_direct_prior
5. context_window has "classical" but sentence does not -> should not become history_foundational
6. experiment sentence with "baseline" -> baseline_direct
7. context_window has "benchmark" but sentence does not -> should not automatically become benchmark_source
8. references section -> misc
9. synthetic fixture still produces at least one history role
10. synthetic fixture still produces at least one baseline or benchmark role
11. generate Step 06c outputs creates required files

Do not make real paper exact role counts brittle.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_citation_role_classifier.py -v
python3 -m pytest -q
python3 -m json.tool reports/step_outputs/step_06c/reclassified_citation_roles.json > /tmp/reclassified_citation_roles_check.json
ls -l reports/step_outputs/step_06c/

---

## Final Report Format

At the end, report exactly:

# Step 06c — Citation Role Classifier Precision Patch — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/06c_citation_role_classifier_precision_patch.md

## 2. Files Created

List created files.

## 3. Files Modified

List modified files.

## 4. Classifier Changes

Summarize the rule changes.

## 5. Before / After Result

Report:

- old role counts
- new role counts
- number of changed citation roles
- whether ref_5 and ref_8 changed
- history_foundational before/after count
- history_direct_prior before/after count

## 6. Visualization Outputs

List files under:

reports/step_outputs/step_06c/

## 7. Tests Run

List validation commands.

## 8. Result

PASS or FAIL.

## 9. Notes

Mention remaining limitations.

## 10. Next Step

Recommend:

Step 10 — History Tree Builder

or optionally:

Step 08 — Milestone 1 Summary Report

---

## Success Criteria

This patch is complete only when:

- prompts/06c_citation_role_classifier_precision_patch.md exists
- src/papernav/citation/classifier.py is patched
- tests/test_citation_role_classifier.py includes precision tests
- reports/step_outputs/step_06c/classifier_precision_patch_summary.md exists
- reports/step_outputs/step_06c/before_after_role_comparison.md exists
- reports/step_outputs/step_06c/reclassified_citation_roles.json exists
- reports/step_outputs/step_06c/history_tree_preview_after_patch.mmd exists
- reports/step_outputs/step_06c/report.md exists
- reclassified_citation_roles.json is valid JSON
- pytest passes
