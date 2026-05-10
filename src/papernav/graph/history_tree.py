"""Builds the History Tree from introduction and related-work citations."""

from __future__ import annotations

import json
import os
import re
import textwrap
from dataclasses import asdict
from pathlib import Path
from typing import Any

from papernav.models import (
    BibliographyEntry,
    CitationRole,
    HistoryTreeNode,
    is_history_role,
)

_ROLE_PRIORITY: dict[str, int] = {
    "history_foundational": 0,
    "history_direct_prior": 1,
    "history_background": 2,
}

_TARGET_NODE_TEMPLATE: dict[str, Any] = {
    "node_id": "target_paper",
    "citation_id": None,
    "title": "Target Paper",
    "year": None,
    "role": "target",
    "citation_frequency": 1,
    "parent_id": None,
    "metadata": {},
}

_MAX_GROUP_FOR_FULL_BIPARTITE = 4


def load_citation_roles(path: str) -> list[CitationRole]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [
        CitationRole(
            citation_id=r["citation_id"],
            role=r["role"],
            confidence=r["confidence"],
            evidence_sentence=r["evidence_sentence"],
            section_name=r["section_name"],
            reason=r.get("reason", ""),
        )
        for r in raw
    ]


def load_bibliography_map(path: str) -> dict[str, BibliographyEntry]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    result: dict[str, BibliographyEntry] = {}
    for cid, entry in raw.items():
        result[cid] = BibliographyEntry(
            citation_id=entry["citation_id"],
            raw_text=entry.get("raw_text", ""),
            title=entry.get("title"),
            authors=entry.get("authors", []),
            year=entry.get("year"),
            venue=entry.get("venue"),
        )
    return result


def select_history_roles(roles: list[CitationRole]) -> list[CitationRole]:
    return [r for r in roles if is_history_role(r.role)]


def _citation_id_sort_key(cid: str) -> int:
    m = re.search(r"\d+", cid)
    return int(m.group()) if m else 9999


def _resolve_strongest_role(roles_for_cid: list[CitationRole]) -> CitationRole:
    return min(roles_for_cid, key=lambda r: _ROLE_PRIORITY.get(r.role, 99))


def _node_to_dict(
    node: HistoryTreeNode,
    metadata: dict,
) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "citation_id": node.citation_id,
        "title": node.title,
        "year": node.year,
        "role": node.role,
        "citation_frequency": node.citation_frequency,
        "parent_id": node.parent_id,
        "metadata": metadata,
    }


def build_history_tree(
    roles: list[CitationRole],
    bibliography_map: dict[str, BibliographyEntry] | None = None,
    target_title: str = "Target Paper",
    paper_id: str = "sample_paper",
) -> dict:
    bib = bibliography_map or {}
    history = select_history_roles(roles)

    # Collect all mentions per citation_id
    mentions_by_cid: dict[str, list[CitationRole]] = {}
    for r in history:
        mentions_by_cid.setdefault(r.citation_id, []).append(r)

    # Build deduplicated nodes
    nodes: list[dict[str, Any]] = []
    for cid, cid_roles in mentions_by_cid.items():
        representative = _resolve_strongest_role(cid_roles)
        bib_entry = bib.get(cid)
        title = (bib_entry.title if bib_entry and bib_entry.title else None) or cid
        year = bib_entry.year if bib_entry else None

        evidence_sentences = list(
            dict.fromkeys(r.evidence_sentence for r in cid_roles)
        )

        node = HistoryTreeNode(
            node_id=cid,
            citation_id=cid,
            title=title,
            role=representative.role,
            citation_frequency=len(cid_roles),
            year=year,
            parent_id=None,
        )
        meta = {
            "section_name": representative.section_name,
            "confidence": representative.confidence,
            "evidence_sentence": representative.evidence_sentence,
            "evidence_sentences": evidence_sentences,
            "reason": representative.reason,
        }
        nodes.append(_node_to_dict(node, meta))

    # Sort nodes: role priority, then year (None last), then citation_id numeric
    def _sort_key(n: dict) -> tuple:
        rp = _ROLE_PRIORITY.get(n["role"], 99)
        yr = n["year"] if n["year"] is not None else 9999
        num = _citation_id_sort_key(n["node_id"])
        return (rp, yr, num)

    nodes.sort(key=_sort_key)

    # Group by role
    groups: dict[str, list[dict]] = {
        "history_foundational": [],
        "history_direct_prior": [],
        "history_background": [],
    }
    for n in nodes:
        if n["role"] in groups:
            groups[n["role"]].append(n)

    # Build edges using group-to-group heuristic
    edges: list[dict[str, Any]] = []
    ordered_roles = ["history_foundational", "history_direct_prior", "history_background"]
    active_groups = [r for r in ordered_roles if groups[r]]

    reasons = {
        ("history_foundational", "history_direct_prior"): "Foundational work precedes direct prior work in the history path.",
        ("history_foundational", "history_background"): "Foundational work provides the field context for background citations.",
        ("history_foundational", "target_paper"): "Foundational work leads directly to the target paper.",
        ("history_direct_prior", "history_background"): "Direct prior work connects to background supporting context.",
        ("history_direct_prior", "target_paper"): "Direct prior work provides immediate context for the target paper.",
        ("history_background", "target_paper"): "Background citation connects to the target paper as supporting context.",
    }

    def _get_representatives(group_nodes: list[dict]) -> list[dict]:
        if len(group_nodes) <= _MAX_GROUP_FOR_FULL_BIPARTITE:
            return group_nodes
        # For large groups, pick first two (highest priority by existing sort)
        return group_nodes[:2]

    for i, src_role in enumerate(active_groups):
        if i + 1 < len(active_groups):
            dst_role = active_groups[i + 1]
        else:
            dst_role = "target_paper"

        src_nodes = _get_representatives(groups[src_role])
        dst_nodes = (
            _get_representatives(groups[dst_role])
            if dst_role != "target_paper"
            else [{"node_id": "target_paper"}]
        )

        reason = reasons.get((src_role, dst_role), f"{src_role} -> {dst_role}")
        for s in src_nodes:
            for d in dst_nodes:
                edges.append({
                    "source": s["node_id"],
                    "target": d["node_id"],
                    "edge_type": "history_flow",
                    "reason": reason,
                    "weight": 1.0,
                })

    # If there are no history nodes at all, leave edges empty
    # reading_path: all nodes in sort order, then target_paper
    reading_path = [n["node_id"] for n in nodes] + ["target_paper"]

    target_node: dict[str, Any] = {
        "node_id": "target_paper",
        "citation_id": None,
        "title": target_title,
        "year": None,
        "role": "target",
        "citation_frequency": 1,
        "parent_id": None,
        "metadata": {"paper_id": paper_id},
    }

    summary = {
        "history_candidate_mentions": len(history),
        "unique_history_nodes": len(nodes),
        "history_foundational_count": len(groups["history_foundational"]),
        "history_direct_prior_count": len(groups["history_direct_prior"]),
        "history_background_count": len(groups["history_background"]),
        "edge_count": len(edges),
    }

    return {
        "paper_id": paper_id,
        "target_node": target_node,
        "summary": summary,
        "nodes": nodes,
        "edges": edges,
        "reading_path": reading_path,
    }


def save_history_tree(tree: dict, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)


def _truncate(text: str, max_len: int = 55) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def render_history_tree_markdown(tree: dict) -> str:
    summary = tree["summary"]
    nodes = tree["nodes"]
    edges = tree["edges"]
    reading_path = tree["reading_path"]

    lines: list[str] = []
    lines.append("# History Tree\n")
    lines.append("## Purpose\n")
    lines.append(
        "This tree shows the historical learning path behind the target paper. "
        "It traces how foundational works, direct prior contributions, and background "
        "citations collectively position the target paper within its field. "
        "The graph is section-aware: only citations drawn from Introduction, "
        "Related Work, and Background sections are included.\n"
    )

    lines.append("## Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| History candidate mentions | {summary['history_candidate_mentions']} |")
    lines.append(f"| Unique history nodes | {summary['unique_history_nodes']} |")
    lines.append(f"| Foundational works | {summary['history_foundational_count']} |")
    lines.append(f"| Direct prior works | {summary['history_direct_prior_count']} |")
    lines.append(f"| Background citations | {summary['history_background_count']} |")
    lines.append(f"| Edges | {summary['edge_count']} |")
    lines.append("")

    lines.append("## Suggested Reading Path\n")
    lines.append("| Order | Citation ID | Role | Year | Title | Evidence |")
    lines.append("|---:|---|---|---:|---|---|")
    node_by_id = {n["node_id"]: n for n in nodes}
    for i, nid in enumerate(reading_path, 1):
        if nid == "target_paper":
            lines.append(f"| {i} | target_paper | target | — | {tree['target_node']['title']} | — |")
        elif nid in node_by_id:
            n = node_by_id[nid]
            yr = str(n["year"]) if n["year"] else "—"
            title = _truncate(n["title"] or nid, 60)
            ev = _truncate(n["metadata"].get("evidence_sentence", ""), 80)
            lines.append(f"| {i} | {nid} | {n['role']} | {yr} | {title} | {ev} |")
    lines.append("")

    lines.append("## Tree Edges\n")
    lines.append("| Source | Target | Reason |")
    lines.append("|---|---|---|")
    for e in edges:
        lines.append(f"| {e['source']} | {e['target']} | {e['reason']} |")
    lines.append("")

    lines.append("## Mermaid Graph\n")
    lines.append("See: `reports/step_outputs/step_10/history_tree.mmd`\n")

    lines.append("## Notes\n")
    lines.append(
        "This History Tree is heuristic and section-aware. "
        "Edge connections are based on role group ordering, not on true citation dependencies. "
        "Role classification accuracy directly affects tree quality."
    )

    return "\n".join(lines)


def render_history_tree_mermaid(tree: dict) -> str:
    nodes = tree["nodes"]
    edges = tree["edges"]
    target_title = tree["target_node"]["title"]

    groups: dict[str, list[dict]] = {
        "history_foundational": [],
        "history_direct_prior": [],
        "history_background": [],
    }
    for n in nodes:
        if n["role"] in groups:
            groups[n["role"]].append(n)

    lines: list[str] = ["flowchart LR"]

    def _node_label(n: dict) -> str:
        nid = n["node_id"]
        title = _truncate(n["title"] or nid, 55)
        yr = str(n["year"]) if n["year"] else "?"
        return f'{nid}["{nid}<br/>{title}<br/>{yr}"]'

    if groups["history_foundational"]:
        lines.append("  subgraph F[Foundational Work]")
        for n in groups["history_foundational"]:
            lines.append(f"    {_node_label(n)}")
        lines.append("  end")

    if groups["history_direct_prior"]:
        lines.append("  subgraph P[Direct Prior Work]")
        for n in groups["history_direct_prior"]:
            lines.append(f"    {_node_label(n)}")
        lines.append("  end")

    if groups["history_background"]:
        lines.append("  subgraph B[Background Context]")
        for n in groups["history_background"]:
            lines.append(f"    {_node_label(n)}")
        lines.append("  end")

    lines.append("  subgraph T[Target]")
    lines.append(f'    target_paper["{target_title}"]')
    lines.append("  end")

    for e in edges:
        lines.append(f"  {e['source']} --> {e['target']}")

    return "\n".join(lines)


def render_history_tree_html(mermaid_text: str, output_path: str) -> None:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>History Tree</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
  <h1>History Tree</h1>
  <div class="mermaid">
{mermaid_text}
  </div>
  <script>mermaid.initialize({{startOnLoad: true}});</script>
</body>
</html>"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def _render_history_tree_table(tree: dict) -> str:
    nodes = tree["nodes"]
    lines: list[str] = []
    lines.append("# History Tree Candidate Table\n")
    lines.append(
        "| Citation ID | Role | Year | Citation Frequency | Title | Section | Confidence | Evidence Preview |"
    )
    lines.append("|---|---|---:|---:|---|---|---|---|")
    for n in nodes:
        yr = str(n["year"]) if n["year"] else "—"
        title = _truncate(n["title"] or n["node_id"], 50)
        section = n["metadata"].get("section_name", "—")
        conf = n["metadata"].get("confidence", "—")
        ev = _truncate(n["metadata"].get("evidence_sentence", ""), 70)
        freq = n["citation_frequency"]
        lines.append(
            f"| {n['node_id']} | {n['role']} | {yr} | {freq} | {title} | {section} | {conf} | {ev} |"
        )
    return "\n".join(lines)


def _render_history_tree_summary(tree: dict) -> str:
    summary = tree["summary"]
    nodes = tree["nodes"]
    reading_path = tree["reading_path"]
    node_by_id = {n["node_id"]: n for n in nodes}

    lines: list[str] = []
    lines.append("# History Tree Summary\n")

    lines.append("## Candidate Counts\n")
    lines.append(f"- Total history role mentions: {summary['history_candidate_mentions']}")
    lines.append(f"- Unique history nodes: {summary['unique_history_nodes']}")
    lines.append(f"- Edges in tree: {summary['edge_count']}")
    lines.append("")

    lines.append("## Role Distribution\n")
    lines.append(f"- `history_foundational`: {summary['history_foundational_count']} node(s)")
    lines.append(f"- `history_direct_prior`: {summary['history_direct_prior_count']} node(s)")
    lines.append(f"- `history_background`:   {summary['history_background_count']} node(s)")
    lines.append("")

    lines.append("## Reading Path\n")
    for i, nid in enumerate(reading_path, 1):
        if nid == "target_paper":
            lines.append(f"{i}. **target_paper** — {tree['target_node']['title']} _(target)_")
        elif nid in node_by_id:
            n = node_by_id[nid]
            yr = f" ({n['year']})" if n["year"] else ""
            lines.append(f"{i}. **{nid}** — {_truncate(n['title'] or nid, 70)}{yr} `[{n['role']}]`")
    lines.append("")

    lines.append("## Interpretation\n")
    if summary["unique_history_nodes"] == 0:
        lines.append(
            "_Warning: No history role candidates were found. "
            "The tree contains only the target node. "
            "Check that citation role classification produced history roles._"
        )
    else:
        lines.append(
            "The History Tree suggests the following field narrative:\n"
        )
        if summary["history_foundational_count"] > 0:
            lines.append(
                "- **Foundational works** established the core timing synchronization "
                "and signal processing methods that define the problem space."
            )
        if summary["history_direct_prior_count"] > 0:
            lines.append(
                "- **Direct prior works** introduced AI and deep-learning approaches "
                "to physical-layer tasks, including channel estimation and timing correction."
            )
        if summary["history_background_count"] > 0:
            lines.append(
                "- **Background citations** provide supporting technical context "
                "such as OFDM standards and recurrent network applications."
            )
        lines.append(
            "- **Target paper** extends these prior contributions using a lightweight "
            "cascaded CNN architecture for timing synchronization in OFDM systems."
        )
        lines.append(
            "\n_Note: Role classification and section detection are heuristic. "
            "Tree quality depends on the accuracy of prior pipeline steps._"
        )

    return "\n".join(lines)


def generate_step10_outputs(
    roles_path: str = "reports/step_outputs/step_06c/reclassified_citation_roles.json",
    bibliography_map_path: str = "examples/sample_citation_to_bibliography_map.json",
    output_dir: str = "reports/step_outputs/step_10",
) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load inputs, fall back to sample_citation_roles.json if 06c missing
    if not Path(roles_path).exists():
        fallback = "examples/sample_citation_roles.json"
        if Path(fallback).exists():
            roles_path = fallback
        else:
            raise FileNotFoundError(f"Citation roles not found: {roles_path}")

    roles = load_citation_roles(roles_path)
    bib_map = load_bibliography_map(bibliography_map_path) if Path(bibliography_map_path).exists() else {}

    tree = build_history_tree(roles, bib_map, paper_id="sample_paper")

    # Core JSON
    json_path = os.path.join(output_dir, "history_tree.json")
    save_history_tree(tree, json_path)

    # Markdown
    md_path = os.path.join(output_dir, "history_tree.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_history_tree_markdown(tree))

    # Mermaid
    mmd_path = os.path.join(output_dir, "history_tree.mmd")
    mmd_text = render_history_tree_mermaid(tree)
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mmd_text)

    # Table
    table_path = os.path.join(output_dir, "history_tree_table.md")
    with open(table_path, "w", encoding="utf-8") as f:
        f.write(_render_history_tree_table(tree))

    # Summary
    summary_path = os.path.join(output_dir, "history_tree_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(_render_history_tree_summary(tree))

    # HTML
    html_path = os.path.join(output_dir, "history_tree.html")
    render_history_tree_html(mmd_text, html_path)

    # Save sample fixture
    sample_path = "examples/sample_history_tree.json"
    save_history_tree(tree, sample_path)

    # Real paper smoke test
    real_roles_path = "reports/step_outputs/step_06/real_paper_citation_roles_snapshot.json"
    real_bib_path = "reports/step_outputs/step_05/real_paper_citation_to_bibliography_map_snapshot.json"
    _generate_real_paper_outputs(real_roles_path, real_bib_path, output_dir)


def _generate_real_paper_outputs(
    real_roles_path: str,
    real_bib_path: str,
    output_dir: str,
) -> None:
    real_roles_exists = Path(real_roles_path).exists()
    real_bib_exists = Path(real_bib_path).exists()

    lines: list[str] = []
    lines.append("# Real Paper History Tree Summary\n")
    lines.append(f"- Real citation roles file: `{real_roles_path}` — {'**found**' if real_roles_exists else '_missing_'}")
    lines.append(f"- Real bibliography map file: `{real_bib_path}` — {'**found**' if real_bib_exists else '_missing_'}")
    lines.append("")

    if real_roles_exists:
        real_roles = load_citation_roles(real_roles_path)
        real_bib = load_bibliography_map(real_bib_path) if real_bib_exists else {}
        real_tree = build_history_tree(real_roles, real_bib, paper_id="real_paper")
        s = real_tree["summary"]

        lines.append(f"- History role mentions: {s['history_candidate_mentions']}")
        lines.append(f"- Unique history nodes: {s['unique_history_nodes']}")
        lines.append(f"- Edges: {s['edge_count']}")
        lines.append("")
        lines.append("## Role Distribution\n")
        lines.append(f"- `history_foundational`: {s['history_foundational_count']}")
        lines.append(f"- `history_direct_prior`: {s['history_direct_prior_count']}")
        lines.append(f"- `history_background`:   {s['history_background_count']}")
        lines.append("")
        lines.append(
            "_Note: Role classification and PDF text extraction are heuristic. "
            "Real paper results may differ from synthetic fixture due to parsing quality._"
        )

        # Save optional real outputs
        real_json_path = os.path.join(output_dir, "real_paper_history_tree.json")
        save_history_tree(real_tree, real_json_path)

        real_mmd_path = os.path.join(output_dir, "real_paper_history_tree.mmd")
        with open(real_mmd_path, "w", encoding="utf-8") as f:
            f.write(render_history_tree_mermaid(real_tree))
    else:
        lines.append("_Real paper role file not found. Smoke test skipped._")
        lines.append("")
        lines.append(
            "_Note: Role classification and PDF text extraction are heuristic. "
            "Run Steps 03-06c on the real paper to generate real outputs._"
        )

    summary_path = os.path.join(output_dir, "real_paper_history_tree_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
