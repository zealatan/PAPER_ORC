# Citation Role Classifier

## Purpose

This module classifies **why** each citation appears in a paper. A citation mention from Step 04 carries raw context (sentence, section name); the classifier turns that context into a semantic role label that downstream steps use to build the History Tree and Baseline Graph.

## Inputs

- `CitationMention` list — produced by Step 04 Citation Extractor
- `BibliographyEntry` mapping — produced by Step 05 Bibliography Mapper (optional; not used in the MVP rule-based classifier but accepted for future enrichment)

## Outputs

- `CitationRole` list — one role object per citation mention
- `citation_roles.json` — serialized role list
- Role summary Markdown tables
- History and baseline candidate Markdown files

## Role Labels

| Role | Meaning |
|---|---|
| `history_foundational` | Seminal or pioneering work that established the field |
| `history_direct_prior` | Direct prior work that the paper builds on or extends |
| `history_background` | Background context reference, not directly extended |
| `baseline_direct` | System or method used as a direct comparison baseline |
| `baseline_extended` | Extended baseline or ablation variant |
| `competitor` | Competing state-of-the-art method that the paper outperforms |
| `benchmark_source` | Source of a dataset, benchmark, or evaluation protocol |
| `metric_source` | Source of an evaluation metric or scoring convention |
| `supporting_evidence` | Reference cited to support a claim without being a baseline |
| `misc` | Uncategorized or reference-section anchor |

## Rule-Based MVP

Classification is deterministic — no external LLM calls. Two signal types are combined:

### Section-Based Defaults

Each section has a default role applied when no keyword rule fires:

| Section | Default Role |
|---|---|
| `introduction` | `history_background` |
| `related_work` | `history_direct_prior` |
| `background` | `history_background` |
| `method` | `supporting_evidence` |
| `experiment` / `experiments` / `evaluation` | `baseline_direct` |
| `results` | `competitor` |
| `discussion` / `conclusion` | `supporting_evidence` |
| `references` | `misc` |

### Keyword Overrides (Precedence Order)

1. **References section** — always `misc` (bibliography anchor)
2. **Benchmark source** — keywords: `benchmark`, `dataset`, `test set`, `evaluation protocol`, `corpus`, ...
3. **Baseline direct** — keywords: `baseline`, `compared with`, `compare against`, `against`, ... (experiment sections only)
4. **Competitor** — keywords: `outperform`, `state-of-the-art`, `sota`, ... (experiment + discussion)
5. **Metric source** — keywords: `metric`, `accuracy`, `ber`, `f1`, ... (experiment + discussion)
6. **History foundational** — keywords: `seminal`, `classical`, `pioneering`, `foundational`, ... (history sections, no comparison blockers)
7. **History direct prior** — keywords: `prior work`, `previous work`, `previous studies`, ... (history sections)
8. **Supporting evidence** — keywords: `shown`, `reported`, `demonstrated`, `suggests`, ... (outside baseline sections)
9. **Section default**
10. **`misc`**

Keyword matching is case-insensitive and searches both `sentence` and `context_window`.

## Reference Section Handling

Citations that appear in the references section are bibliography anchors — they list the full reference entry, not an in-text semantic use. These are classified as `misc` with `confidence = high` so that downstream history/baseline graph builders can safely ignore them.

## Synthetic Fixture

The synthetic paper (`examples/sample_paper.txt`) contains 41 citation mentions across 7 sections:

| Section | Expected Roles |
|---|---|
| `introduction` | `history_foundational`, `history_direct_prior`, `history_background` |
| `related_work` | `history_foundational`, `history_direct_prior`, `supporting_evidence` |
| `method` | `supporting_evidence` |
| `experiment` | `benchmark_source`, `baseline_direct`, `metric_source` |
| `results` | `baseline_direct`, `competitor` |
| `discussion` | `supporting_evidence` |
| `references` | `misc` (13 anchors) |

## Real Paper Smoke Test

The RTLFixer paper (`rtlfixer_2311_16543.pdf`) is run through the classifier using the snapshots from Steps 03–05. Because RTLFixer's PDF text extraction uses heuristic section detection, some citations may receive imprecise section labels. The smoke test is considered a pass if the classifier runs without error and returns one role per mention.

## Precision Patch Notes (Step 06c)

- **Sentence-first**: the classifier now uses `mention.sentence` as the primary text for all keyword checks. `mention.context_window` is used only as a fallback when the sentence has fewer than 10 words.
- **`introduced` removed from foundational keywords**: this word appeared too frequently in neighboring sentences and caused false `history_foundational` assignments. A citation whose sentence says "Smith et al. [X] introduced a method" now falls back to section default (e.g., `history_direct_prior`) rather than being promoted to foundational.
- **Rule 3 direct-prior keywords**: `deep learning`, `neural`, `neural network`, `cnn`, `learning-based`, `data-driven` were added to `_PRIOR_KWS`. When these appear in the sentence of a citation in a history section, the citation is classified as `history_direct_prior`.
- **Result**: the patch corrected 7 roles in the synthetic fixture — most notably, ref_5 and ref_8 in `related_work` changed from `history_foundational` to `history_direct_prior`.

## Limitations

- **Rule-based only**: keyword coverage is incomplete; niche phrasing will fall back to section defaults.
- **No LLM reasoning**: semantic nuances (e.g., a reference cited for methodology that also happened to be influential historically) cannot be resolved by keyword matching.
- **No semantic similarity**: title or abstract similarity between the paper and cited work is not used.
- **Multi-purpose citations**: a single citation may serve multiple roles across different sentences; only one role per mention is assigned.
- **Residual context bleed**: for very short sentences (< 10 words), context_window is still used as a fallback; this is intentional to handle fragment-style citations like "[8] and the recurrent approach...".
