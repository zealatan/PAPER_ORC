## 🗺️ PaperNav Roadmap

PaperNav is built step by step.  
Every Claude Code prompt used to build the system must be saved as a Markdown file under `prompts/`.

<p align="center">
  <img src="assets/papernav_project_roadmap_overview.png" alt="PaperNav Project Roadmap" width="100%">
</p>

---

## 📌 Prompt Archive Rule

> **Rule:** Every step prompt must be saved as a Markdown file under `prompts/`.

This repository follows a strict prompt-traceable development workflow:

```text
prompts/
├── 00_bootstrap_repository.md
├── 01_define_common_models.md
├── 02_add_sample_paper_fixture.md
├── 03_build_paper_parser.md
├── 04_build_citation_extractor.md
├── 05_build_bibliography_mapper.md
├── 06_build_citation_role_classifier.md
├── 07_build_citation_report_writer.md
└── 08_add_milestone1_pipeline.md
```

Each prompt should include:

```text
- Working directory
- Objective
- Context
- Allowed modifications
- Files to create or modify
- Implementation requirements
- Tests
- Documentation updates
- Final report format
```

---

## ✅ Milestone 1 — Section-Aware Citation Extraction

The first milestone builds the foundation for section-aware reference analysis.

The goal is to convert a paper into structured citation-role information:

```text
Paper
  ↓
Section Parsing
  ↓
Citation Extraction
  ↓
Bibliography Mapping
  ↓
Citation Role Classification
  ↓
citation_roles.json / citation_roles.md
```

<p align="center">
  <img src="assets/milestone_1_citation_extraction_workflow.png" alt="Milestone 1 Citation Extraction Workflow" width="100%">
</p>

### Milestone 1 Steps

| Step | Prompt File | Purpose |
|---:|---|---|
| 00 | `prompts/00_bootstrap_repository.md` | Create repository structure, `pyproject.toml`, tests, and `prompts/` |
| 01 | `prompts/01_define_common_models.md` | Define shared data models |
| 02 | `prompts/02_add_sample_paper_fixture.md` | Create sample paper fixture with introduction and experiment citations |
| 03 | `prompts/03_build_paper_parser.md` | Split paper into sections and build `ParsedPaper` JSON |
| 04 | `prompts/04_build_citation_extractor.md` | Extract numeric citations from each section with sentence context |
| 05 | `prompts/05_build_bibliography_mapper.md` | Map citation markers to reference entries |
| 06 | `prompts/06_build_citation_role_classifier.md` | Classify history vs. baseline roles using section and keywords |
| 07 | `prompts/07_build_citation_report_writer.md` | Generate `citation_roles.md` and summary tables |
| 08 | `prompts/08_add_milestone1_pipeline.md` | Run the end-to-end Milestone 1 pipeline and export sample outputs |

### Milestone 1 Done When

- [ ] Paper sections are parsed
- [ ] Citations are extracted from each section
- [ ] Bibliography entries are mapped
- [ ] Citation roles are classified
- [ ] `citation_roles.json` is generated
- [ ] `citation_roles.md` is generated
- [ ] End-to-end sample pipeline passes
