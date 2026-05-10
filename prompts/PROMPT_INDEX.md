# PaperNav Prompt Index

This file is the authoritative index of all Claude Code step prompts for the PaperNav project.

Each prompt file records the full instruction set given to Claude for one development step.
Prompts are the trace between the paper reproduction goal and the code produced.

---

## Index

| File | Step | Title | Status | Lines |
|---|---|---|---|---:|
| `00_bootstrap_repository.md` | 00 | Bootstrap Repository | COMPLETE | 67 |
| `01_define_common_models.md` | 01 | Define Common Data Models | COMPLETE | 107 |
| `01b_complete_common_models_and_visual_outputs.md` | 01b | Complete Common Models and Visual Outputs | **MISSING** | — |
| `01c_add_required_step01_visual_outputs.md` | 01c | Add Required Step 01 Visual Outputs | **MISSING** | — |
| `02_add_sample_paper_fixture.md` | 02 | Add Sample Paper Fixture | COMPLETE | 59 |
| `02b_complete_sample_fixture_docs_and_visual_outputs.md` | 02b | Complete Sample Fixture Docs and Visual Outputs | COMPLETE | 307 |
| `02c_add_real_paper_smoke_fixture.md` | 02c | Add Real Paper Smoke Fixture | COMPLETE | 234 |
| `03_build_paper_parser.md` | 03 | Build Paper Parser | COMPLETE | 599 |
| `04_build_citation_extractor.md` | 04 | Build Citation Extractor | COMPLETE | 583 |
| `05_build_bibliography_mapper.md` | 05 | Build Bibliography Mapper | COMPLETE | 654 |
| `06_build_citation_role_classifier.md` | 06 | Build Citation Role Classifier | COMPLETE | 573 |
| `06b_quick_history_tree_preview.md` | 06b | Quick History Tree Preview | COMPLETE | 318 |
| `06c_citation_role_classifier_precision_patch.md` | 06c | Citation Role Classifier Precision Patch | COMPLETE | 304 |
| `00z_archive_and_validate_claude_prompts.md` | 00z | Prompt Archive Audit | INCOMPLETE (message cut off) | 83 |

---

## Status Summary

| Status | Count |
|---|---:|
| COMPLETE | 11 |
| MISSING | 2 |
| INCOMPLETE | 1 |
| **Total expected** | **12** |

---

## Missing Prompts

The following prompt files were listed in the audit spec but do not exist on disk.
They appear to be patch prompts for Step 01 (analogous to 02b/02c for Step 02)
that were not pasted during the development session.

- `prompts/01b_complete_common_models_and_visual_outputs.md`
- `prompts/01c_add_required_step01_visual_outputs.md`

These prompts should be pasted and saved when available.

---

## Incomplete Prompts

- `prompts/00z_archive_and_validate_claude_prompts.md` — received with message cut off after the expected file list. The audit proceeds on available information.

---

## Notes

- Prompts 03–05 are the longest (500–650 lines) and were pasted in full, verified complete.
- Prompt 00 uses Python `>= 3.11` in the spec; the actual `pyproject.toml` uses `>= 3.10` (implementation decision taken during bootstrap).
- All prompts from 02b onward include a "FIRST ACTION — Save This Prompt" rule, which was followed in every subsequent step.
