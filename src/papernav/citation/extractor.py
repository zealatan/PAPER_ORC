"""Extracts numeric citation markers from each section with sentence context."""

import dataclasses
import json
import re
from collections import Counter
from pathlib import Path

from papernav.models import CitationMention, ParsedPaper, normalize_citation_id

# ---------------------------------------------------------------------------
# Citation regex
# ---------------------------------------------------------------------------

# Matches single, grouped, or range citation markers:
#   [1]  [1, 2]  [1,2,3]  [1-3]  [1–3]  [1, 3-5]  [1]-[3]  [1]–[3]
_CITE_RE = re.compile(
    r"\[\d[\d\s,\-–]*\]"          # bracketed group (digits, commas, spaces, dashes)
    r"(?:\s*[\-–—]\s*\[\d+\])?"   # optionally: -[N] for inter-bracket range
)


def _parse_citation_numbers(raw: str) -> list[int]:
    """Extract individual citation numbers from a raw citation group string."""
    digits_part = raw.replace("[", " ").replace("]", " ")
    parts = [p.strip() for p in digits_part.split(",")]
    numbers: list[int] = []
    for part in parts:
        part = part.strip()
        m = re.match(r"^(\d+)\s*[\-–—]\s*(\d+)$", part)
        if m:
            numbers.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif re.match(r"^\d+$", part):
            numbers.append(int(part))
        else:
            for digit_m in re.finditer(r"\d+", part):
                numbers.append(int(digit_m.group()))
    return sorted(set(numbers))


def _extract_sentence(text: str, pos: int) -> str:
    """Return the sentence containing position pos in text (heuristic)."""
    window_start = max(0, pos - 400)
    window_end = min(len(text), pos + 400)
    window = text[window_start:window_end]
    local_pos = pos - window_start

    # Scan backwards for sentence start
    s = local_pos
    while s > 0:
        ch = window[s - 1]
        if ch in ".!?" and s < len(window) and window[s].isspace():
            break
        if ch == "\n" and s > 1 and window[s - 2] == "\n":
            break
        s -= 1

    # Scan forwards for sentence end
    e = local_pos
    while e < len(window):
        ch = window[e]
        if ch in ".!?" and (e + 1 >= len(window) or window[e + 1].isspace()):
            e += 1
            break
        if ch == "\n" and e + 1 < len(window) and window[e + 1] == "\n":
            break
        e += 1

    return " ".join(window[s:e].strip().split())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_citations_from_text(
    text: str,
    section_name: str,
    section_offset: int | None = None,
) -> list[CitationMention]:
    """Extract all numeric citation mentions from a section of text."""
    mentions: list[CitationMention] = []
    offset = section_offset or 0

    for m in _CITE_RE.finditer(text):
        raw_marker = m.group(0)
        start, end = m.start(), m.end()

        sentence = _extract_sentence(text, start)

        ctx_start = max(0, start - 100)
        ctx_end = min(len(text), end + 100)
        context_window = " ".join(text[ctx_start:ctx_end].split())

        for num in _parse_citation_numbers(raw_marker):
            mentions.append(CitationMention(
                citation_id=normalize_citation_id(num),
                marker=raw_marker,
                section_name=section_name,
                sentence=sentence,
                context_window=context_window,
                role=None,
                start_char=offset + start,
                end_char=offset + end,
            ))

    return mentions


def extract_citations(parsed_paper: ParsedPaper) -> list[CitationMention]:
    """Extract all citation mentions from a ParsedPaper, section by section."""
    all_mentions: list[CitationMention] = []

    if parsed_paper.section_objects:
        for sec in parsed_paper.section_objects:
            all_mentions.extend(
                extract_citations_from_text(
                    sec.text,
                    section_name=sec.name,
                    section_offset=sec.start_char,
                )
            )
    else:
        for sec_name, sec_text in parsed_paper.sections.items():
            all_mentions.extend(
                extract_citations_from_text(sec_text, section_name=sec_name)
            )

    return all_mentions


def save_citation_mentions(
    mentions: list[CitationMention],
    output_path: str,
) -> None:
    """Serialise a CitationMention list to a JSON file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(m) for m in mentions], f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Step-04 output generator
# ---------------------------------------------------------------------------

def generate_step04_outputs(
    parsed_paper_path: str = "examples/sample_parsed_paper.json",
    output_dir: str = "reports/step_outputs/step_04",
) -> dict:
    """Generate all Step 04 visualisation and report files."""
    from papernav.parser import load_parsed_paper

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    parsed = load_parsed_paper(parsed_paper_path)
    mentions = extract_citations(parsed)

    # Snapshots
    snap_path = out / "citation_mentions_snapshot.json"
    save_citation_mentions(mentions, str(snap_path))
    save_citation_mentions(mentions, "examples/sample_citation_mentions.json")

    body_mentions = [m for m in mentions if m.section_name != "references"]
    ref_mentions = [m for m in mentions if m.section_name == "references"]

    section_counts: dict[str, int] = {}
    section_unique: dict[str, set] = {}
    for m in mentions:
        section_counts[m.section_name] = section_counts.get(m.section_name, 0) + 1
        section_unique.setdefault(m.section_name, set()).add(m.citation_id)

    # citation_extraction_table.md
    seen_sections = list(dict.fromkeys(m.section_name for m in mentions))
    summary_rows = []
    for sec in seen_sections:
        cnt = section_counts[sec]
        uniq = len(section_unique[sec])
        markers = ", ".join(sorted({m.marker for m in mentions if m.section_name == sec})[:3])
        summary_rows.append(f"| {sec} | {cnt} | {uniq} | {markers} |")

    body_rows: list[str] = []
    seen_body: set = set()
    for m in body_mentions:
        key = (m.section_name, m.citation_id)
        if key not in seen_body:
            seen_body.add(key)
            preview = m.sentence[:80] + ("..." if len(m.sentence) > 80 else "")
            body_rows.append(
                f"| {m.section_name} | {m.citation_id} | `{m.marker}` | {preview} |"
            )
        if len(body_rows) >= 15:
            break

    ref_rows = []
    for m in ref_mentions[:13]:
        preview = m.sentence[:80] + ("..." if len(m.sentence) > 80 else "")
        ref_rows.append(f"| {m.citation_id} | `{m.marker}` | {preview} |")

    table_md = "\n".join([
        "# Citation Extraction Table\n",
        "## Summary by Section\n",
        "| Section | Citation Mention Count | Unique Citation IDs | Example Markers |",
        "|---|---:|---:|---|",
        *summary_rows,
        "\n## Body Citation Examples\n",
        "| Section | Citation ID | Marker | Sentence Preview |",
        "|---|---|---|---|",
        *body_rows,
        "\n## Reference Anchor Examples\n",
        "| Citation ID | Marker | Sentence Preview |",
        "|---|---|---|",
        *ref_rows,
    ])
    (out / "citation_extraction_table.md").write_text(table_md + "\n", encoding="utf-8")

    # citation_extraction_flow.mmd
    (out / "citation_extraction_flow.mmd").write_text(
        "flowchart TD\n"
        "    A[ParsedPaper JSON] --> B[Citation Extractor]\n"
        "    B --> C[Introduction citations]\n"
        "    B --> D[Related Work citations]\n"
        "    B --> E[Experiment citations]\n"
        "    B --> F[Results citations]\n"
        "    B --> G[Discussion citations]\n"
        "    B --> H[Reference anchors]\n"
        "    C --> I[citation_mentions.json]\n"
        "    D --> I\n"
        "    E --> I\n"
        "    F --> I\n"
        "    G --> I\n"
        "    H --> I\n"
        "    I --> J[Step 05 Bibliography Mapper]\n",
        encoding="utf-8",
    )

    # Real paper smoke test
    real_snap = Path("reports/step_outputs/step_03/real_paper_parsed_snapshot.json")
    real_lines = ["# Real Paper Citation Summary — Step 04\n"]
    real_total = 0
    real_section_counts: dict[str, int] = {}
    real_status = "missing"

    if real_snap.exists():
        real_lines.append("- **Real parsed snapshot:** PRESENT")
        try:
            real_parsed = load_parsed_paper(str(real_snap))
            real_mentions = extract_citations(real_parsed)
            real_total = len(real_mentions)
            for m in real_mentions:
                real_section_counts[m.section_name] = (
                    real_section_counts.get(m.section_name, 0) + 1
                )
            top10 = Counter(m.citation_id for m in real_mentions).most_common(10)
            real_lines += [
                "- **Extraction status:** SUCCESS",
                f"- **Total citation mentions:** {real_total}",
                "\n### Section-Level Counts\n",
                "| Section | Count |", "|---|---:|",
            ]
            for sec, cnt in sorted(real_section_counts.items()):
                real_lines.append(f"| {sec} | {cnt} |")
            real_lines += ["\n### Top 10 Citation IDs by Frequency\n",
                           "| Citation ID | Count |", "|---|---:|"]
            for cid, cnt in top10:
                real_lines.append(f"| {cid} | {cnt} |")
            real_snap_out = out / "real_paper_citation_mentions_snapshot.json"
            save_citation_mentions(real_mentions, str(real_snap_out))
            real_lines.append(f"\n- **Snapshot saved:** `{real_snap_out}`")
            real_status = "success"
        except Exception as exc:
            real_lines.append(f"- **Extraction status:** FAILED — {exc}")
            real_status = "failed"
    else:
        real_lines += [
            "- **Real parsed snapshot:** MISSING",
            "- **Extraction status:** SKIPPED",
        ]

    real_lines.append(
        "\n> Note: PDF extraction and citation detection are heuristic."
    )
    (out / "real_paper_citation_summary.md").write_text(
        "\n".join(real_lines) + "\n", encoding="utf-8"
    )

    return {
        "total_mentions": len(mentions),
        "body_mentions": len(body_mentions),
        "ref_mentions": len(ref_mentions),
        "section_counts": section_counts,
        "unique_ids": sorted({m.citation_id for m in mentions}),
        "snapshot_path": str(snap_path),
        "real_status": real_status,
        "real_total": real_total,
        "real_section_counts": real_section_counts,
    }
