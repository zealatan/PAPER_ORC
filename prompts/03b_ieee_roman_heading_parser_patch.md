# Step 03b — IEEE Roman Heading Parser Patch

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/03b_ieee_roman_heading_parser_patch.md

If the file already exists, overwrite it with this full prompt.

Every Claude Code prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Patch the PaperNav parser so it correctly detects IEEE-style Roman numeral section headings in real papers.

The current failure case is:

papers/real/my_paper.pdf

Current bad result:

Sections detected:
- abstract
- references

Expected better result should include sections such as:

- abstract
- introduction
- system_model or method
- relu_dnn_mechanism or background
- analysis or method
- robustness or discussion
- experiment or results
- conclusion
- references

The uploaded paper uses headings such as:

I. INTRODUCTION
II. SYSTEM MODEL AND CHANNEL ESTIMATION
III. INTERNAL MECHANISM OF RELU DNNS
IV. ANALYSIS ON DL BASED CHANNEL ESTIMATION
V. ROBUSTNESS OF CHANNEL ESTIMATION TO MISMATCHED INFORMATION
VI. SIMULATION RESULTS
VII. CONCLUSIONS
REFERENCES

The parser must detect these headings and split the paper accordingly.

Do not implement citation extraction, bibliography mapping, classifier, or graph changes in this patch.

---

## Files to Modify

Modify:

src/papernav/parser.py
tests/test_parser.py
docs/parser.md

Create:

reports/step_outputs/step_03b/ieee_heading_parser_patch_summary.md
reports/step_outputs/step_03b/my_paper_section_check.md
reports/step_outputs/step_03b/my_paper_parsed_snapshot.json
reports/step_outputs/step_03b/report.md

Optional:

reports/step_outputs/step_03b/my_paper_section_split_diagram.mmd

Update if useful:

prompts/PROMPT_INDEX.md

---

## Required Parser Improvements

### 1. Support Roman numeral headings

Detect headings like:

I. INTRODUCTION
II. SYSTEM MODEL AND CHANNEL ESTIMATION
III. INTERNAL MECHANISM OF RELU DNNS
IV. ANALYSIS ON DL BASED CHANNEL ESTIMATION
V. ROBUSTNESS OF CHANNEL ESTIMATION TO MISMATCHED INFORMATION
VI. SIMULATION RESULTS
VII. CONCLUSIONS

Regex should support:

- uppercase roman numerals
- optional dot
- heading text in uppercase
- leading/trailing whitespace
- page number noise nearby if possible

Examples to match:

I. INTRODUCTION
II. SYSTEM MODEL AND CHANNEL ESTIMATION
III. INTERNAL MECHANISM OF RELU DNNS
VI. SIMULATION RESULTS
VII. CONCLUSIONS

### 2. Support generic unknown section headings

Do not discard unknown headings.

If a heading is not in the standard map, normalize it into a snake_case key.

Example:

INTERNAL MECHANISM OF RELU DNNS
-> internal_mechanism_of_relu_dnns

ANALYSIS ON DL BASED CHANNEL ESTIMATION
-> analysis_on_dl_based_channel_estimation

ROBUSTNESS OF CHANNEL ESTIMATION TO MISMATCHED INFORMATION
-> robustness_of_channel_estimation_to_mismatched_information

### 3. Improve heading normalization

Map common section titles:

INTRODUCTION -> introduction
RELATED WORK -> related_work
BACKGROUND AND RELATED WORK -> related_work
SYSTEM MODEL -> system_model
SYSTEM MODEL AND CHANNEL ESTIMATION -> system_model
METHOD -> method
METHODOLOGY -> method
PROPOSED METHOD -> method
ANALYSIS -> analysis
ANALYSIS ON DL BASED CHANNEL ESTIMATION -> analysis
EXPERIMENT -> experiment
EXPERIMENTS -> experiment
EXPERIMENTAL SETUP -> experiment
EVALUATION -> experiment
SIMULATION RESULTS -> experiment
RESULTS -> results
DISCUSSION -> discussion
CONCLUSION -> conclusion
CONCLUSIONS -> conclusion
REFERENCES -> references
BIBLIOGRAPHY -> references

### 4. Preserve original heading title

Each PaperSection should preserve the original title.

Example:

name = "system_model"
title = "II. SYSTEM MODEL AND CHANNEL ESTIMATION"

### 5. Do not break existing fixtures

The synthetic fixture must still parse correctly.

RTLFixer smoke test must still parse at least as well as before.

---

## Test Requirements

Update tests/test_parser.py.

Add tests for:

1. Roman heading "I. INTRODUCTION" is detected as introduction
2. Roman heading "II. SYSTEM MODEL AND CHANNEL ESTIMATION" is detected as system_model
3. Roman heading "VI. SIMULATION RESULTS" is detected as experiment
4. Roman heading "VII. CONCLUSIONS" is detected as conclusion
5. Unknown Roman heading is preserved as snake_case key
6. Synthetic fixture still detects introduction, related_work, experiment, results, discussion, references
7. my_paper.pdf smoke test:
   - if papers/real/my_paper.pdf exists, parse_file detects more than 2 sections
   - it must detect introduction
   - it must detect references
   - it should detect either experiment or results or simulation_results
   - if missing, skip with pytest.skip

Do not make exact full section list too brittle.

---

## Step Output Requirements

Create:

reports/step_outputs/step_03b/my_paper_section_check.md

It must include:

# my_paper Section Check

## Before Problem

Explain that previous parser detected only abstract and references.

## After Patch

Show detected section keys.

## Section Table

| Section Key | Original Title | Character Count | Preview |
|---|---|---:|---|

Create:

reports/step_outputs/step_03b/my_paper_parsed_snapshot.json

This must be valid JSON generated by parsing:

papers/real/my_paper.pdf

If file is missing, create a summary explaining it was skipped.

Create:

reports/step_outputs/step_03b/ieee_heading_parser_patch_summary.md

Explain what was patched.

Create:

reports/step_outputs/step_03b/report.md

Include final patch result.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_parser.py -v
python3 -m pytest -q
python3 -m json.tool reports/step_outputs/step_03b/my_paper_parsed_snapshot.json > /tmp/my_paper_parsed_snapshot_check.json
ls -l reports/step_outputs/step_03b/

Then rerun the custom paper pipeline:

python3 scripts/analyze_one_paper.py papers/real/my_paper.pdf --paper-id my_paper --title "My Target Paper" --output-dir reports/my_paper

After rerun, check:

python3 - <<'EOF'
import json
with open("reports/my_paper/parsed_paper.json") as f:
    data = json.load(f)
print("sections:", list(data.get("sections", {}).keys()))
with open("reports/my_paper/history_tree.json") as f:
    tree = json.load(f)
print("history nodes:", len(tree.get("nodes", [])))
print("history edges:", len(tree.get("edges", [])))
EOF

Expected:

- sections should include more than abstract and references
- introduction should be present
- references should be present
- history tree should have non-zero nodes if classification works

---

## Final Report Format

At the end, report exactly:

# Step 03b — IEEE Roman Heading Parser Patch — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/03b_ieee_roman_heading_parser_patch.md

## 2. Files Modified

List modified files.

## 3. Files Created

List created files.

## 4. Parser Patch Summary

Summarize the heading detection improvements.

## 5. my_paper Reparse Result

Report:

- detected section keys
- section count
- whether introduction was detected
- whether references was detected
- whether experiment/results/simulation section was detected

## 6. Pipeline Rerun Result

Report after rerunning analyze_one_paper.py:

- citation mentions
- bibliography entries
- mapped citations
- citation roles
- history tree nodes
- history tree edges

## 7. Tests Run

List validation commands.

## 8. Result

PASS or FAIL.

## 9. Next Step

Recommend:

Rerun Step 10 History Tree output check or proceed to Step 12 Baseline Graph Builder.

---

## Success Criteria

This patch is complete only when:

- prompts/03b_ieee_roman_heading_parser_patch.md exists
- parser detects IEEE Roman headings
- tests/test_parser.py includes Roman heading tests
- my_paper.pdf parses into more than abstract and references
- my_paper parse includes introduction
- my_paper parse includes references
- reports/step_outputs/step_03b/my_paper_parsed_snapshot.json is valid JSON
- python3 -m pytest -q passes
- analyze_one_paper.py rerun on my_paper produces non-empty history tree nodes or clearly explains why no history roles were found
