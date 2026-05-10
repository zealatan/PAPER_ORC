"""Rule-based citation role classifier using sentence-first keyword signals.

Precision patch (Step 06c): strong rules (foundational, benchmark, baseline)
now check mention.sentence first. mention.context_window is used only as a
fallback when the sentence contains fewer than _SHORT_THRESHOLD words, reducing
false positives caused by neighboring-sentence keyword bleed.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import asdict

from papernav.models import (
    CITATION_ROLE_LABELS,
    CONFIDENCE_LABELS,
    BibliographyEntry,
    CitationMention,
    CitationRole,
    is_baseline_role,
    is_history_role,
)

# Sentences with fewer than this many words may fall back to context_window.
_SHORT_THRESHOLD = 10

_SECTION_DEFAULTS: dict[str, str] = {
    "abstract": "misc",
    "introduction": "history_background",
    "related_work": "history_direct_prior",
    "background": "history_background",
    "method": "supporting_evidence",
    "experiment": "baseline_direct",
    "experiments": "baseline_direct",
    "evaluation": "baseline_direct",
    "results": "competitor",
    "discussion": "supporting_evidence",
    "conclusion": "supporting_evidence",
    "references": "misc",
}

_HISTORY_SECTIONS = frozenset({"introduction", "related_work", "background"})
_BASELINE_SECTIONS = frozenset({"experiment", "experiments", "evaluation", "results"})
_EXPERIMENT_DISCUSSION = _BASELINE_SECTIONS | {"discussion"}

# "introduced" removed: it appears too often in neighboring sentences and caused
# false history_foundational assignments via context_window bleed.
_FOUNDATIONAL_KWS = [
    "first proposed",
    "pioneering",
    "classical",
    "seminal",
    "foundation",
    "foundational",
    "standardized",
    "specification",
]

# Rule 3 additions: "deep learning", "neural", etc. in history sections signal
# that the citation is ML-era prior work rather than generic background.
_PRIOR_KWS = [
    "prior work",
    "previous work",
    "previous studies",
    "recent work",
    "recent works",
    "related work",
    "has been explored",
    "have been explored",
    "existing methods",
    "existing approaches",
    "deep learning",
    "neural network",
    "neural networks",
    "neural",
    "cnn",
    "learning-based",
    "data-driven",
]

_BASELINE_KWS = [
    "we compare",
    "compare with",
    "compare against",
    "compared with",
    "compared against",
    "comparison with",
    "baseline",
    "baselines",
    "against",
    "evaluate against",
]

_COMPETITOR_KWS = [
    "outperform",
    "outperforms",
    "outperformed",
    "state-of-the-art",
    "sota",
    "competitive",
    "competitor",
    "competing method",
    "competing approach",
]

_BENCHMARK_KWS = [
    "benchmark",
    "dataset",
    "test set",
    "evaluation protocol",
    "verilogeval",
    "suite",
    "workload",
    "corpus",
]

_METRIC_KWS = [
    "metric",
    "score",
    "measurement",
    "accuracy",
    "pass rate",
    "success rate",
    "ber",
    "latency",
    "throughput",
    "f1",
    "precision",
    "recall",
]

_SUPPORTING_KWS = [
    "shown",
    "observed",
    "reported",
    "demonstrated",
    "evidence",
    "indicates",
    "suggests",
    "according to",
]

# Sentence-level compare language that blocks history_foundational from firing.
_COMPARE_BLOCKERS = [
    "compared with",
    "compared against",
    "compare with",
    "compare against",
    "evaluate against",
    "baseline",
    "benchmark",
]


def _first_match(text: str, keywords: list[str]) -> str | None:
    for kw in keywords:
        if kw in text:
            return kw
    return None


def _ctx_match(
    sentence: str,
    context: str,
    keywords: list[str],
) -> tuple[str | None, str]:
    """Sentence-first match; context fallback only for short sentences.

    Returns (matched_keyword, source_label) where source_label is one of
    'sentence keyword' or 'context fallback'.
    """
    m = _first_match(sentence, keywords)
    if m:
        return m, "sentence keyword"
    if len(sentence.split()) < _SHORT_THRESHOLD:
        m = _first_match(context, keywords)
        if m:
            return m, "context fallback"
    return None, ""


def classify_citation_role(
    mention: CitationMention,
    bibliography_entry: BibliographyEntry | None = None,
) -> CitationRole:
    """Assign a semantic role to a single CitationMention.

    Priority order (highest first):
    1. references section -> misc
    2. benchmark_source   (sentence first)
    3. baseline_direct    (sentence first, experiment sections)
    4. competitor         (sentence first, experiment/discussion)
    5. metric_source      (sentence first, experiment/discussion)
    6. history_foundational (sentence ONLY — no context fallback)
    7. history_direct_prior (sentence first, history sections)
    8. supporting_evidence  (sentence first, outside baseline sections)
    9. section default
    10. misc
    """
    section = mention.section_name.lower()
    sentence_text = mention.sentence.lower()
    context_text = mention.context_window.lower()

    # Priority 1: bibliography anchor
    if section == "references":
        return CitationRole(
            citation_id=mention.citation_id,
            role="misc",
            confidence="high",
            evidence_sentence=mention.sentence,
            section_name=mention.section_name,
            reason="Section 'references' indicates bibliography anchor; classified as misc.",
        )

    # Priority 2: benchmark_source (sentence first, context fallback for short sentences)
    kw, src = _ctx_match(sentence_text, context_text, _BENCHMARK_KWS)
    if kw:
        confidence = "high" if kw in ("benchmark", "dataset") else "medium"
        return CitationRole(
            citation_id=mention.citation_id,
            role="benchmark_source",
            confidence=confidence,
            evidence_sentence=mention.sentence,
            section_name=mention.section_name,
            reason=f"Keyword '{kw}' ({src}) indicates a benchmark or dataset source.",
        )

    # Priority 3: baseline_direct (experiment/evaluation/results)
    if section in _BASELINE_SECTIONS:
        kw, src = _ctx_match(sentence_text, context_text, _BASELINE_KWS)
        if kw:
            return CitationRole(
                citation_id=mention.citation_id,
                role="baseline_direct",
                confidence="high",
                evidence_sentence=mention.sentence,
                section_name=mention.section_name,
                reason=f"Section '{section}' and {src} '{kw}' indicate direct baseline usage.",
            )

    # Priority 4: competitor (experiment/evaluation/results/discussion)
    if section in _EXPERIMENT_DISCUSSION:
        kw, src = _ctx_match(sentence_text, context_text, _COMPETITOR_KWS)
        if kw:
            confidence = "high" if kw in ("outperform", "outperforms", "outperformed", "state-of-the-art", "sota") else "medium"
            return CitationRole(
                citation_id=mention.citation_id,
                role="competitor",
                confidence=confidence,
                evidence_sentence=mention.sentence,
                section_name=mention.section_name,
                reason=f"Section '{section}' and {src} '{kw}' indicate a competing method.",
            )

    # Priority 5: metric_source (experiment/evaluation/results/discussion)
    if section in _EXPERIMENT_DISCUSSION:
        kw, src = _ctx_match(sentence_text, context_text, _METRIC_KWS)
        if kw:
            return CitationRole(
                citation_id=mention.citation_id,
                role="metric_source",
                confidence="medium",
                evidence_sentence=mention.sentence,
                section_name=mention.section_name,
                reason=f"Section '{section}' and {src} '{kw}' indicate a metric or evaluation source.",
            )

    # Priority 6: history_foundational — SENTENCE ONLY, no context fallback.
    # "introduced" was intentionally removed from _FOUNDATIONAL_KWS: it is
    # too common in neighboring sentences and caused context bleed errors.
    if section in _HISTORY_SECTIONS:
        kw = _first_match(sentence_text, _FOUNDATIONAL_KWS)
        if kw and not _first_match(sentence_text, _COMPARE_BLOCKERS):
            return CitationRole(
                citation_id=mention.citation_id,
                role="history_foundational",
                confidence="high",
                evidence_sentence=mention.sentence,
                section_name=mention.section_name,
                reason=f"Section '{section}' and sentence keyword '{kw}' indicate a foundational history citation.",
            )

    # Priority 7: history_direct_prior (sentence first, history sections)
    if section in _HISTORY_SECTIONS:
        kw, src = _ctx_match(sentence_text, context_text, _PRIOR_KWS)
        if kw:
            confidence = "high" if src == "sentence keyword" else "medium"
            return CitationRole(
                citation_id=mention.citation_id,
                role="history_direct_prior",
                confidence=confidence,
                evidence_sentence=mention.sentence,
                section_name=mention.section_name,
                reason=f"Section '{section}' and {src} '{kw}' indicate a direct prior work citation.",
            )

    # Priority 8: supporting_evidence (outside baseline sections)
    if section not in _BASELINE_SECTIONS:
        kw, src = _ctx_match(sentence_text, context_text, _SUPPORTING_KWS)
        if kw:
            return CitationRole(
                citation_id=mention.citation_id,
                role="supporting_evidence",
                confidence="medium",
                evidence_sentence=mention.sentence,
                section_name=mention.section_name,
                reason=f"Keyword '{kw}' ({src}) indicates supporting evidence usage.",
            )

    # Priority 9: section default
    default_role = _SECTION_DEFAULTS.get(section, "misc")
    default_conf = "medium" if default_role != "misc" else "low"
    return CitationRole(
        citation_id=mention.citation_id,
        role=default_role,
        confidence=default_conf,
        evidence_sentence=mention.sentence,
        section_name=mention.section_name,
        reason=f"Section '{section}' default role applied.",
    )


def classify_citation_roles(
    mentions: list[CitationMention],
    bibliography_map: dict[str, BibliographyEntry] | None = None,
) -> list[CitationRole]:
    """Classify all citation mentions, returning one CitationRole per mention."""
    bib = bibliography_map or {}
    return [classify_citation_role(m, bib.get(m.citation_id)) for m in mentions]


def save_citation_roles(roles: list[CitationRole], output_path: str) -> None:
    """Serialize citation roles to JSON."""
    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump([asdict(r) for r in roles], fh, indent=2)


# ---------------------------------------------------------------------------
# Deserialization helpers
# ---------------------------------------------------------------------------

def _load_mentions(path: str) -> list[CitationMention]:
    with open(path, encoding="utf-8") as fh:
        records = json.load(fh)
    return [CitationMention(**r) for r in records]


def _load_bibliography_map(path: str) -> dict[str, BibliographyEntry]:
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    return {k: BibliographyEntry(**v) for k, v in raw.items()}


# ---------------------------------------------------------------------------
# Visualization helpers (shared by step 06 and 06c generators)
# ---------------------------------------------------------------------------

def _truncate(s: str | None, n: int = 60) -> str:
    if not s:
        return ""
    return s[:n] + "…" if len(s) > n else s


def _build_citation_role_summary(
    roles: list[CitationRole],
    bibliography_map: dict[str, BibliographyEntry],
) -> str:
    from collections import Counter

    role_counts: Counter[str] = Counter(r.role for r in roles)
    section_role_counts: dict[tuple[str, str], int] = defaultdict(int)
    for r in roles:
        section_role_counts[(r.section_name, r.role)] += 1

    history_rows = [r for r in roles if is_history_role(r.role)]
    baseline_rows = [r for r in roles if is_baseline_role(r.role)]
    misc_rows = [r for r in roles if r.role == "misc"]
    misc_by_section: Counter[str] = Counter(r.section_name for r in misc_rows)

    lines = ["# Citation Role Summary", ""]
    lines += ["## Overall Role Counts", "", "| Role | Count |", "|---|---:|"]
    for label in CITATION_ROLE_LABELS:
        if role_counts[label]:
            lines.append(f"| {label} | {role_counts[label]} |")
    lines.append("")
    lines += ["## Role Counts by Section", "", "| Section | Role | Count |", "|---|---|---:|"]
    for (sec, role), cnt in sorted(section_role_counts.items()):
        lines.append(f"| {sec} | {role} | {cnt} |")
    lines.append("")
    lines += ["## History Citation Candidates", "", "| Citation ID | Title | Section | Role | Confidence | Evidence |", "|---|---|---|---|---|---|"]
    for r in history_rows:
        entry = bibliography_map.get(r.citation_id)
        title = _truncate(entry.title if entry else None, 40)
        lines.append(f"| {r.citation_id} | {title} | {r.section_name} | {r.role} | {r.confidence} | {_truncate(r.evidence_sentence, 50)} |")
    lines.append("")
    lines += ["## Baseline / Experiment Citation Candidates", "", "| Citation ID | Title | Section | Role | Confidence | Evidence |", "|---|---|---|---|---|---|"]
    for r in baseline_rows:
        entry = bibliography_map.get(r.citation_id)
        title = _truncate(entry.title if entry else None, 40)
        lines.append(f"| {r.citation_id} | {title} | {r.section_name} | {r.role} | {r.confidence} | {_truncate(r.evidence_sentence, 50)} |")
    lines.append("")
    lines += ["## Misc / Reference Anchors", "", "| Citation ID | Section | Count |", "|---|---|---:|"]
    for sec, cnt in sorted(misc_by_section.items()):
        lines.append(f"| (various) | {sec} | {cnt} |")
    lines.append("")
    return "\n".join(lines)


def _build_candidates_md(
    title: str,
    roles: list[CitationRole],
    bibliography_map: dict[str, BibliographyEntry],
) -> str:
    lines = [f"# {title}", ""]
    if not roles:
        lines.append("_No citations classified under this category._")
        return "\n".join(lines)
    lines += ["| Citation ID | Title | Year | Section | Role | Confidence | Evidence |", "|---|---|---:|---|---|---|---|"]
    for r in roles:
        entry = bibliography_map.get(r.citation_id)
        title_str = _truncate(entry.title if entry else None, 45)
        year = str(entry.year) if entry and entry.year else ""
        lines.append(f"| {r.citation_id} | {title_str} | {year} | {r.section_name} | {r.role} | {r.confidence} | {_truncate(r.evidence_sentence, 55)} |")
    lines.append("")
    return "\n".join(lines)


_MMD_FLOW = """\
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
"""


def _build_real_paper_summary(
    mentions_exist: bool,
    bib_map_exist: bool,
    roles: list[CitationRole],
) -> str:
    from collections import Counter

    lines = ["# Real Paper Citation Role Summary (RTLFixer)", ""]
    lines.append(f"- Real citation mentions: {'PRESENT' if mentions_exist else 'MISSING'}")
    lines.append(f"- Real bibliography map: {'PRESENT' if bib_map_exist else 'MISSING'}")
    if not mentions_exist or not bib_map_exist:
        lines += ["", "_Smoke test skipped: required inputs not found._"]
        return "\n".join(lines)
    lines.append(f"- Total roles classified: {len(roles)}")
    lines.append("")
    role_counts: Counter[str] = Counter(r.role for r in roles)
    lines += ["## Role Counts", "", "| Role | Count |", "|---|---:|"]
    for label in CITATION_ROLE_LABELS:
        if role_counts[label]:
            lines.append(f"| {label} | {role_counts[label]} |")
    lines.append("")
    sec_role: dict[tuple[str, str], int] = defaultdict(int)
    for r in roles:
        sec_role[(r.section_name, r.role)] += 1
    lines += ["## Role Counts by Section", "", "| Section | Role | Count |", "|---|---|---:|"]
    for (sec, role), cnt in sorted(sec_role.items()):
        lines.append(f"| {sec} | {role} | {cnt} |")
    lines.append("")
    non_misc = [r for r in roles if r.role != "misc"][:10]
    lines += ["## Top Non-Misc Citation Roles (first 10)", "", "| Citation ID | Section | Role | Confidence | Evidence |", "|---|---|---|---|---|"]
    for r in non_misc:
        lines.append(f"| {r.citation_id} | {r.section_name} | {r.role} | {r.confidence} | {_truncate(r.evidence_sentence, 55)} |")
    lines.append("")
    lines.append("_Note: rule-based classification is heuristic._")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Step 06 output generator
# ---------------------------------------------------------------------------

def generate_step06_outputs(
    citation_mentions_path: str = "examples/sample_citation_mentions.json",
    bibliography_map_path: str = "examples/sample_citation_to_bibliography_map.json",
    output_dir: str = "reports/step_outputs/step_06",
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    mentions = _load_mentions(citation_mentions_path)
    bibliography_map = _load_bibliography_map(bibliography_map_path)
    roles = classify_citation_roles(mentions, bibliography_map)

    snapshot_path = os.path.join(output_dir, "citation_roles_snapshot.json")
    save_citation_roles(roles, snapshot_path)
    save_citation_roles(roles, "examples/sample_citation_roles.json")

    with open(os.path.join(output_dir, "citation_role_flow.mmd"), "w", encoding="utf-8") as fh:
        fh.write(_MMD_FLOW)

    summary_md = _build_citation_role_summary(roles, bibliography_map)
    with open(os.path.join(output_dir, "citation_role_summary.md"), "w", encoding="utf-8") as fh:
        fh.write(summary_md)

    history_roles = [r for r in roles if is_history_role(r.role)]
    with open(os.path.join(output_dir, "history_citation_candidates.md"), "w", encoding="utf-8") as fh:
        fh.write(_build_candidates_md("History Citation Candidates", history_roles, bibliography_map))

    baseline_roles = [r for r in roles if is_baseline_role(r.role)]
    with open(os.path.join(output_dir, "baseline_citation_candidates.md"), "w", encoding="utf-8") as fh:
        fh.write(_build_candidates_md("Baseline / Experiment Citation Candidates", baseline_roles, bibliography_map))

    real_mentions_path = "reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json"
    real_bib_path = "reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json"
    real_mentions_exist = os.path.exists(real_mentions_path)
    real_bib_exist = os.path.exists(real_bib_path)
    real_roles: list[CitationRole] = []
    if real_mentions_exist and real_bib_exist:
        try:
            real_mentions = _load_mentions(real_mentions_path)
            real_bib_map = _load_bibliography_map(real_bib_path)
            real_roles = classify_citation_roles(real_mentions, real_bib_map)
            save_citation_roles(real_roles, os.path.join(output_dir, "real_paper_citation_roles_snapshot.json"))
        except Exception:
            pass

    real_summary_md = _build_real_paper_summary(real_mentions_exist, real_bib_exist, real_roles)
    with open(os.path.join(output_dir, "real_paper_citation_role_summary.md"), "w", encoding="utf-8") as fh:
        fh.write(real_summary_md)


# ---------------------------------------------------------------------------
# Step 06c output generator (precision patch diagnostic)
# ---------------------------------------------------------------------------

def _build_history_preview_mmd(
    roles: list[CitationRole],
    bibliography_map: dict[str, BibliographyEntry],
) -> str:
    HISTORY_ROLES = {"history_foundational", "history_direct_prior", "history_background"}
    ROLE_PRIORITY = {"history_foundational": 0, "history_direct_prior": 1, "history_background": 2}

    best: dict[str, CitationRole] = {}
    for r in roles:
        if r.role not in HISTORY_ROLES:
            continue
        cid = r.citation_id
        if cid not in best or ROLE_PRIORITY[r.role] < ROLE_PRIORITY[best[cid].role]:
            best[cid] = r

    def sort_key(r: CitationRole) -> tuple:
        entry = bibliography_map.get(r.citation_id)
        yr = entry.year if entry and entry.year else 9999
        num = int(r.citation_id.replace("ref_", "")) if r.citation_id.startswith("ref_") else 999
        return (ROLE_PRIORITY[r.role], yr, num)

    candidates = sorted(best.values(), key=sort_key)
    by_role: dict[str, list[CitationRole]] = defaultdict(list)
    for r in candidates:
        by_role[r.role].append(r)

    foundational = by_role["history_foundational"]
    direct_prior = by_role["history_direct_prior"]
    background = by_role["history_background"]

    def node_label(r: CitationRole) -> str:
        entry = bibliography_map.get(r.citation_id)
        parts = [r.citation_id]
        if entry and entry.title:
            parts.append(_truncate(entry.title, 45))
        if entry and entry.year:
            parts.append(str(entry.year))
        return "<br/>".join(parts)

    lines = ["flowchart LR"]
    if foundational:
        lines.append("    subgraph F[Foundational Work]")
        for r in foundational:
            lines.append(f'        {r.citation_id}["{node_label(r)}"]')
        lines.append("    end")
        lines.append("")
    if direct_prior:
        lines.append("    subgraph P[Direct Prior Work]")
        for r in direct_prior:
            lines.append(f'        {r.citation_id}["{node_label(r)}"]')
        lines.append("    end")
        lines.append("")
    if background:
        lines.append("    subgraph B[Background Context]")
        for r in background:
            lines.append(f'        {r.citation_id}["{node_label(r)}"]')
        lines.append("    end")
        lines.append("")
    lines.append('    T["Target Paper"]')
    lines.append("")

    groups = [g for g in [foundational, direct_prior, background] if g]
    for i in range(len(groups) - 1):
        tgt = groups[i + 1][0].citation_id
        for r in groups[i]:
            lines.append(f"    {r.citation_id} --> {tgt}")
    if groups:
        for r in groups[-1]:
            lines.append(f"    {r.citation_id} --> T")

    return "\n".join(lines) + "\n"


def generate_step06c_outputs(
    citation_mentions_path: str = "examples/sample_citation_mentions.json",
    bibliography_map_path: str = "examples/sample_citation_to_bibliography_map.json",
    old_roles_path: str = "examples/sample_citation_roles.json",
    output_dir: str = "reports/step_outputs/step_06c",
) -> None:
    from collections import Counter

    os.makedirs(output_dir, exist_ok=True)

    mentions = _load_mentions(citation_mentions_path)
    bibliography_map = _load_bibliography_map(bibliography_map_path)

    with open(old_roles_path, encoding="utf-8") as fh:
        old_records = json.load(fh)
    old_role_by_key = {(r["citation_id"], r["section_name"], r["evidence_sentence"]): r["role"] for r in old_records}

    new_roles = classify_citation_roles(mentions, bibliography_map)
    save_citation_roles(new_roles, os.path.join(output_dir, "reclassified_citation_roles.json"))

    # Before / after comparison
    old_counts: Counter[str] = Counter(r["role"] for r in old_records)
    new_counts: Counter[str] = Counter(r.role for r in new_roles)

    changed_rows = []
    for r in new_roles:
        key = (r.citation_id, r.section_name, r.evidence_sentence)
        old_role = old_role_by_key.get(key)
        if old_role and old_role != r.role:
            entry = bibliography_map.get(r.citation_id)
            changed_rows.append({
                "citation_id": r.citation_id,
                "section": r.section_name,
                "old_role": old_role,
                "new_role": r.role,
                "title": _truncate(entry.title if entry else None, 40),
                "evidence": _truncate(r.evidence_sentence, 55),
            })

    ba_lines = [
        "# Before / After Role Comparison (Step 06 → Step 06c)",
        "",
        "## Role Count Comparison",
        "",
        "| Role | Before | After |",
        "|---|---:|---:|",
    ]
    all_roles_seen = set(old_counts.keys()) | set(new_counts.keys())
    for role in CITATION_ROLE_LABELS:
        if role in all_roles_seen:
            ba_lines.append(f"| {role} | {old_counts.get(role, 0)} | {new_counts.get(role, 0)} |")
    ba_lines.append("")
    ba_lines += [
        "## Changed Roles",
        "",
        f"Total changed: {len(changed_rows)}",
        "",
        "| Citation ID | Section | Old Role | New Role | Title | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for row in changed_rows:
        ba_lines.append(
            f"| {row['citation_id']} | {row['section']} | {row['old_role']} | {row['new_role']} | {row['title']} | {row['evidence']} |"
        )
    ba_lines.append("")

    with open(os.path.join(output_dir, "before_after_role_comparison.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(ba_lines))

    # Mermaid after patch
    mmd = _build_history_preview_mmd(new_roles, bibliography_map)
    with open(os.path.join(output_dir, "history_tree_preview_after_patch.mmd"), "w", encoding="utf-8") as fh:
        fh.write(mmd)

    # Precision patch summary
    HISTORY_ROLES = {"history_foundational", "history_direct_prior", "history_background"}
    BASELINE_ROLES = {"baseline_direct", "baseline_extended", "competitor", "benchmark_source", "metric_source"}
    history_old = sum(old_counts.get(r, 0) for r in HISTORY_ROLES)
    history_new = sum(new_counts.get(r, 0) for r in HISTORY_ROLES)
    baseline_old = sum(old_counts.get(r, 0) for r in BASELINE_ROLES)
    baseline_new = sum(new_counts.get(r, 0) for r in BASELINE_ROLES)

    summary_lines = [
        "# Classifier Precision Patch Summary (Step 06c)",
        "",
        "## Changes Applied",
        "",
        "- **Sentence-first strategy**: all strong keyword checks now use `mention.sentence` first;",
        "  `mention.context_window` is used only when the sentence has fewer than 10 words.",
        "- **`introduced` removed** from foundational keywords: it appeared too frequently in",
        "  neighboring sentences, causing false `history_foundational` assignments.",
        "- **Rule 3 keywords added** to `_PRIOR_KWS`: `deep learning`, `neural`, `neural network`,",
        "  `neural networks`, `cnn`, `learning-based`, `data-driven` — these signal ML-era prior",
        "  work when cited in history sections.",
        "- **Reason field** now explicitly states whether the decision came from sentence keyword,",
        "  context fallback, or section default.",
        "",
        "## Role Count Summary",
        "",
        "| Metric | Before | After |",
        "|---|---:|---:|",
        f"| Total mentions | {sum(old_counts.values())} | {sum(new_counts.values())} |",
        f"| History roles total | {history_old} | {history_new} |",
        f"| history_foundational | {old_counts.get('history_foundational', 0)} | {new_counts.get('history_foundational', 0)} |",
        f"| history_direct_prior | {old_counts.get('history_direct_prior', 0)} | {new_counts.get('history_direct_prior', 0)} |",
        f"| history_background | {old_counts.get('history_background', 0)} | {new_counts.get('history_background', 0)} |",
        f"| Baseline/experiment roles total | {baseline_old} | {baseline_new} |",
        f"| baseline_direct | {old_counts.get('baseline_direct', 0)} | {new_counts.get('baseline_direct', 0)} |",
        f"| benchmark_source | {old_counts.get('benchmark_source', 0)} | {new_counts.get('benchmark_source', 0)} |",
        f"| competitor | {old_counts.get('competitor', 0)} | {new_counts.get('competitor', 0)} |",
        f"| misc | {old_counts.get('misc', 0)} | {new_counts.get('misc', 0)} |",
        f"| Changed roles | — | {len(changed_rows)} |",
        "",
    ]
    with open(os.path.join(output_dir, "classifier_precision_patch_summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(summary_lines))
