# Prompt 00 — Bootstrap Repository

## Working directory

`/home/zealatan/PAPER_ORC`

## Objective

Create the full PaperNav repository scaffold: package structure, `pyproject.toml`, empty module stubs, and a passing test suite skeleton. No business logic yet — only structure and imports.

## Context

PaperNav is a section-aware paper intelligence system. It parses scientific papers, extracts citation mentions per section, maps them to bibliography entries, classifies their roles (history vs. baseline), and builds visual maps (History Tree, Baseline Graph) plus an importance report.

The full design is documented in `README.md`.

## Allowed modifications

- Create any file listed in the Recommended Repository Structure (Section 15 of README)
- Create `pyproject.toml`
- Create `tests/` scaffold
- Create `prompts/00_bootstrap_repository.md` (this file)

## Files to create

```
pyproject.toml
src/papernav/__init__.py
src/papernav/models.py
src/papernav/parser.py
src/papernav/pipeline.py
src/papernav/report_writer.py
src/papernav/citation/__init__.py
src/papernav/citation/extractor.py
src/papernav/citation/bibliography.py
src/papernav/citation/classifier.py
src/papernav/graph/__init__.py
src/papernav/graph/history_tree.py
src/papernav/graph/baseline_graph.py
src/papernav/graph/visualizer.py
src/papernav/agents/__init__.py
src/papernav/agents/topic_relevance.py
src/papernav/agents/citation_value.py
src/papernav/agents/experiment_value.py
src/papernav/agents/strategic_value.py
src/papernav/agents/weakness_risk.py
src/papernav/agents/final_judge.py
tests/__init__.py
tests/test_bootstrap.py
examples/
papers/
reports/
```

## Implementation requirements

- `pyproject.toml`: use `[project]` table, name = `papernav`, Python >= 3.11, dev dependencies include `pytest`
- All `__init__.py` files: empty or minimal
- All stub modules: module-level docstring only, no logic
- `tests/test_bootstrap.py`: import every module and assert it can be imported without error

## Final report format

```
PASS/FAIL: all imports succeed
Files created: N
```
