# Prompt Archive Audit — Save and Validate All Claude Step Prompts

## FIRST ACTION — Save This Prompt

Before doing any work, save this entire prompt as:

prompts/00z_archive_and_validate_claude_prompts.md

If the file already exists, overwrite it with this full prompt.

This project rule is mandatory:

Every Claude Code command prompt must be saved as a Markdown file under prompts/.

After saving this prompt, continue with the audit.

---

## Working Directory

/home/zealatan/PAPER_ORC

---

## Objective

Audit and organize all Claude Code prompt files created so far for the PaperNav project.

The goal is to make sure the development process is prompt-traceable.

This audit must not implement new PaperNav functionality.

It should only:

1. Check which prompt files exist.
2. Detect missing prompt files.
3. Detect incomplete prompt files.
4. Create a clean prompt index.
5. Create a prompt archive status report.
6. Do not delete or overwrite existing valid prompt files.

---

## Do Not Modify

Do not modify source code:

src/

Do not modify tests:

tests/

Do not modify generated step outputs:

reports/step_outputs/

Do not modify README.md unless explicitly needed.

Do not delete any existing prompt files.

---

## Expected Prompt Files So Far

Check for these files:

```text
prompts/00_bootstrap_repository.md
prompts/01_define_common_models.md
prompts/01b_complete_common_models_and_visual_outputs.md
prompts/01c_add_required_step01_visual_outputs.md
prompts/02_add_sample_paper_fixture.md
prompts/02b_complete_sample_fixture_docs_and_visual_outputs.md
prompts/02c_add_real_paper_smoke_fixture.md
prompts/03_build_paper_parser.md
prompts/04_build_citation_extractor.md
prompts/05_build_bibliography_mapper.md
prompts/00z_archive_and_validate_claude_prompts.md
```

Note: This prompt was received incomplete (message cut off after the file list).
The audit proceeds on the basis of the objective and file list provided above.
