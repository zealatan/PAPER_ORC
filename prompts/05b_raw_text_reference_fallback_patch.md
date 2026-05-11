# Step 05b — Raw-Text Reference Fallback Patch

## FIRST ACTION — Save This Full Prompt

Before doing any implementation work, save this entire prompt as:

prompts/05b_raw_text_reference_fallback_patch.md

If the file already exists, overwrite it with this full prompt.

Every Claude Code prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the implementation.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Patch the bibliography mapper so it can parse references from raw_text when the parser fails to isolate a clean references section.

Current failure case:

papers/real/my_paper.pdf

The pipeline currently produces:

- bibliography_entries.json: empty
- citation_to_bibliography_map.json: empty
- history tree labels like ref_4 / ref_4 / ?

However, parsed_paper.raw_text clearly contains IEEE references near the tail:

[44] B. Zhu, J. Wang, ...
[45] F. A. Aoudia and J. Hoydis, ...
...
[61] S. Chen and Q. Zhao, ...

Therefore, the issue is not PDF extraction. The issue is that bibliography.py relies too heavily on sections["references"] and does not robustly recover the reference list from raw_text.

Do not modify citation role classifier or history tree builder unless absolutely necessary.

---

## Files to Modify

Modify:

src/papernav/citation/bibliography.py
tests/test_bibliography_mapper.py
docs/bibliography_mapper.md

Create:

reports/step_outputs/step_05b/my_paper_bibliography_diagnostics.md
reports/step_outputs/step_05b/raw_text_reference_fallback_summary.md
reports/step_outputs/step_05b/my_paper_bibliography_entries.json
reports/step_outputs/step_05b/my_paper_citation_to_bibliography_map.json
reports/step_outputs/step_05b/report.md

Update if useful:

prompts/PROMPT_INDEX.md

---

## Required Fix

Implement a fallback function in bibliography.py:

extract_references_text_best_effort(parsed_paper: ParsedPaper) -> str

Behavior:

1. First try parsed_paper.sections["references"].
2. If missing or too short, search parsed_paper.raw_text.
3. In raw_text, locate the reference list by finding a dense block of numeric reference entries:
   - [1]
   - [2]
   - [10]
   - [44]
4. Prefer the earliest marker that begins a long sequential reference list.
5. Extract from the first detected reference marker to the end.
6. Trim non-reference material after the reference list.

---

## Stop Conditions for Reference Block

When extracting from raw_text, stop before author biography / footers.

Stop if a line matches or contains:

- "received the B.S."
- "received his B.S."
- "received her B.S."
- "is currently"
- "Biography"
- "Authorized licensed use"
- "Downloaded on"
- "Restrictions apply"
- "IEEE TRANSACTIONS"
- "VOL."
- "NO."

But be careful:

- Do not stop at journal text inside a reference unless it appears after the reference list block.
- It is acceptable for MVP to stop at the first biography-like paragraph after the final numeric reference.

---

## Reference Entry Splitting

Update split_reference_entries() to support IEEE references from raw text:

[1] Author, "Title," Venue, year.
[44] Author, "Title," Venue, year.

It must support:

- multi-line references
- curly quotes
- hyphenated line breaks such as "com-\nmunication" -> "communication"
- whitespace cleanup
- entries numbered beyond [9], e.g. [44], [61]

Do not drop entries if title extraction fails.

A BibliographyEntry must be created as long as citation_id and raw_text are available.

---

## Title Extraction

Keep the existing curly quote patch.

Ensure these title formats are supported:

"Title,"
"Title"
"Title,"
"Title"

If quoted title exists, use it.

If no quoted title exists, use fallback heuristic conservatively.

If uncertain, title = None, but still create the entry.

---

## Year Extraction

Extract the last year between 1900 and 2099.

Examples:

2019
2021
1972

---

## Mapping

After entries are extracted, map existing CitationMention IDs to BibliographyEntry IDs.

For my_paper, expected:

- bibliography_entries count > 0
- citation_to_bibliography_map count > 0
- ideally dozens of entries if references are available

Do not require exact 61 entries because PDF extraction may be imperfect.

---

## Diagnostics

Create:

reports/step_outputs/step_05b/my_paper_bibliography_diagnostics.md

Include:

# my_paper Bibliography Diagnostics

## Parsed Sections

List section keys and lengths.

## References Section Status

Report whether sections["references"] exists and its length.

## Raw Text Reference Detection

Report:

- raw_text length
- first reference marker found
- last reference marker found
- extracted reference block length
- estimated entry count

## First 10 Extracted Entries

| Citation ID | Year | Title | Raw Preview |
|---|---:|---|---|

---

## Regeneration Requirements

After patching, rerun:

python3 scripts/analyze_one_paper.py papers/real/my_paper.pdf --paper-id my_paper --title "My Target Paper" --output-dir reports/my_paper

Then copy or create:

reports/step_outputs/step_05b/my_paper_bibliography_entries.json
reports/step_outputs/step_05b/my_paper_citation_to_bibliography_map.json

from the regenerated reports/my_paper outputs.

---

## Test Requirements

Update tests/test_bibliography_mapper.py.

Add tests for:

1. extract_references_text_best_effort uses sections["references"] when available.
2. extract_references_text_best_effort falls back to raw_text when references section is missing.
3. raw_text fallback detects [1] and [2].
4. raw_text fallback supports [44] and [61].
5. raw_text fallback stops before "received the B.S."
6. split_reference_entries handles multi-line IEEE entries.
7. split_reference_entries handles hyphenated line breaks.
8. parse_reference_entry creates BibliographyEntry even if title is None.
9. parse_reference_entry extracts curly quote title.
10. my_paper smoke test: after fallback, bibliography entry count > 0 if raw_text contains numeric references.

Do not make exact entry count too brittle.

---

## Validation Commands

Run:

python3 -m compileall src
python3 -m pytest tests/test_bibliography_mapper.py -v
python3 -m pytest -q

Then rerun:

python3 scripts/analyze_one_paper.py papers/real/my_paper.pdf --paper-id my_paper --title "My Target Paper" --output-dir reports/my_paper

Then verify:

python3 - <<'EOF'
import json

with open("reports/my_paper/bibliography_entries.json") as f:
    entries = json.load(f)

with open("reports/my_paper/citation_to_bibliography_map.json") as f:
    mapping = json.load(f)

print("bibliography entries:", len(entries))
print("mapped citations:", len(mapping))

for e in entries[:10]:
    print(e.get("citation_id"), e.get("year"), e.get("title"), e.get("raw_text", "")[:100])
EOF

Expected:

- bibliography entries > 0
- mapped citations > 0
- titles should be extracted when curly quoted titles are present

---

## Final Report Format

At the end, report exactly:

# Step 05b — Raw-Text Reference Fallback Patch — Final Report

## 1. Prompt Saved

Confirm saved to:

prompts/05b_raw_text_reference_fallback_patch.md

## 2. Files Modified

List modified files.

## 3. Files Created

List created files.

## 4. Root Cause

Explain that raw_text contained references but sections["references"] was not usable by bibliography mapper.

## 5. Patch Summary

Summarize:

- best-effort references extraction
- raw_text fallback
- biography/footer trimming
- multi-line IEEE reference splitting

## 6. my_paper Result

Report:

- bibliography entry count before / after
- mapped citation count before / after
- first 5 extracted titles
- history tree nodes / edges after rerun

## 7. Tests Run

List validation commands.

## 8. Result

PASS or FAIL.

## 9. Next Step

Recommend:

Rerun Step 10b full-label history tree view or proceed to Step 11 recursive frontier.

---

## Success Criteria

This patch is complete only when:

- prompts/05b_raw_text_reference_fallback_patch.md exists
- extract_references_text_best_effort exists
- raw_text fallback can recover references when sections["references"] is missing/short
- my_paper bibliography_entries count > 0
- my_paper citation_to_bibliography_map count > 0
- tests pass
