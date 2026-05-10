"""Maps citation markers to bibliography entries."""

import dataclasses
import json
import re
from pathlib import Path

from papernav.models import BibliographyEntry, CitationMention, ParsedPaper, normalize_citation_id


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _find_author_title_boundary(body: str) -> int:
    """Return index of the '.' that ends the authors segment, or -1."""
    for m in re.finditer(r"\. ", body):
        start = m.start()
        word_start = start
        while word_start > 0 and body[word_start - 1] not in " ,\t\n":
            word_start -= 1
        word = body[word_start:start]
        # Accept boundary only if preceding word is >= 3 chars (not an initial like "T.")
        if len(word) >= 3:
            return start
    return -1


def _parse_authors(authors_raw: str) -> list[str]:
    """Split an author string into individual author names."""
    if not authors_raw:
        return []
    and_parts = re.split(r"\s+and\s+", authors_raw)
    result: list[str] = []
    for part in and_parts:
        for segment in re.split(r",\s*", part.strip()):
            segment = segment.strip().rstrip(",")
            if segment:
                result.append(segment)
    return result


def _extract_year(text: str) -> int | None:
    """Return the last 4-digit year (1900–2099) in text, or None."""
    hits = re.findall(r"\b(1[9]\d{2}|20\d{2})\b", text)
    return int(hits[-1]) if hits else None


def _extract_venue(body: str, title: str, year: int | None) -> str | None:
    """Extract venue text appearing after the title."""
    title_pos = body.find(title)
    if title_pos == -1:
        return None
    remainder = body[title_pos + len(title):].strip().lstrip(".").lstrip(",").strip()
    if year:
        remainder = re.sub(rf",?\s*\b{year}\b\.?\s*$", "", remainder).strip().rstrip(",").strip()
    return remainder or None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def split_reference_entries(references_text: str) -> list[str]:
    """Split a references section into individual raw entry strings.

    Handles multi-line entries: continuation lines start with whitespace,
    so only lines beginning with [N] are treated as entry boundaries.
    """
    raw_blocks = re.split(r"\n(?=\[\d+\])", references_text)
    entries: list[str] = []
    for block in raw_blocks:
        block = block.strip()
        if block and re.match(r"\[\d+\]", block):
            entries.append(block)
    return entries


def parse_reference_entry(raw_entry: str) -> BibliographyEntry:
    """Parse a single raw reference string into a BibliographyEntry."""
    num_m = re.match(r"^\[(\d+)\]\s*", raw_entry)
    if not num_m:
        return BibliographyEntry(citation_id="ref_unknown", raw_text=raw_entry)

    citation_id = normalize_citation_id(int(num_m.group(1)))
    # Join continuation lines
    body = re.sub(r"\n\s+", " ", raw_entry[num_m.end():]).strip()
    year = _extract_year(body)

    # Strategy 1: quoted title
    quoted_m = re.search(r'"([^"]{3,})"', body)
    if quoted_m:
        title: str | None = quoted_m.group(1).strip()
        authors_raw = body[: quoted_m.start()].strip().rstrip(",").strip()
        venue_tail = body[quoted_m.end():].strip().lstrip(".").lstrip(",").strip()
        if year:
            venue_tail = re.sub(rf",?\s*\b{year}\b\.?\s*$", "", venue_tail).strip().rstrip(",")
        venue: str | None = venue_tail or None
    else:
        # Strategy 2: period-separated heuristic
        boundary = _find_author_title_boundary(body)
        if boundary != -1:
            authors_raw = body[:boundary].strip()
            remainder = body[boundary + 2:]  # skip '. '
            title_end_m = re.search(r"\.\s", remainder)
            if title_end_m:
                title = remainder[: title_end_m.start()].strip()
            else:
                title = remainder.strip().rstrip(".")
            venue = _extract_venue(body, title, year) if title else None
        else:
            authors_raw = ""
            title = None
            venue = None

    authors = _parse_authors(authors_raw)
    return BibliographyEntry(
        citation_id=citation_id,
        raw_text=raw_entry,
        title=title,
        authors=authors,
        year=year,
        venue=venue,
    )


def extract_bibliography_entries_from_text(references_text: str) -> list[BibliographyEntry]:
    """Parse a references section string into BibliographyEntry objects."""
    return [parse_reference_entry(raw) for raw in split_reference_entries(references_text)]


def extract_bibliography_entries(parsed_paper: ParsedPaper) -> list[BibliographyEntry]:
    """Extract bibliography entries from a ParsedPaper's references section."""
    refs_text = parsed_paper.sections.get("references", "")
    if not refs_text:
        for key in ("bibliography", "reference"):
            if key in parsed_paper.sections:
                refs_text = parsed_paper.sections[key]
                break
    return extract_bibliography_entries_from_text(refs_text)


def map_mentions_to_bibliography(
    mentions: list[CitationMention],
    entries: list[BibliographyEntry],
) -> dict[str, BibliographyEntry]:
    """Map unique citation IDs from mentions to matching BibliographyEntry objects."""
    entry_by_id = {e.citation_id: e for e in entries}
    mapping: dict[str, BibliographyEntry] = {}
    for m in mentions:
        if m.citation_id not in mapping and m.citation_id in entry_by_id:
            mapping[m.citation_id] = entry_by_id[m.citation_id]
    return mapping


def save_bibliography_entries(entries: list[BibliographyEntry], output_path: str) -> None:
    """Serialise a BibliographyEntry list to a JSON file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(e) for e in entries], f, indent=2, ensure_ascii=False)


def save_citation_to_bibliography_map(
    mapping: dict[str, BibliographyEntry],
    output_path: str,
) -> None:
    """Serialise a citation_id → BibliographyEntry mapping to a JSON file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {k: dataclasses.asdict(v) for k, v in mapping.items()},
            f, indent=2, ensure_ascii=False,
        )


# ---------------------------------------------------------------------------
# Step-05 output generator
# ---------------------------------------------------------------------------

def generate_step05_outputs(
    parsed_paper_path: str = "examples/sample_parsed_paper.json",
    citation_mentions_path: str = "examples/sample_citation_mentions.json",
    output_dir: str = "reports/step_outputs/step_05",
) -> dict:
    """Generate all Step 05 visualisation and report files."""
    from papernav.parser import load_parsed_paper

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    parsed = load_parsed_paper(parsed_paper_path)
    entries = extract_bibliography_entries(parsed)

    with open(citation_mentions_path, encoding="utf-8") as f:
        mentions = [CitationMention(**d) for d in json.load(f)]

    mapping = map_mentions_to_bibliography(mentions, entries)

    # Snapshots
    entries_snap = out / "bibliography_entries_snapshot.json"
    map_snap = out / "citation_to_bibliography_map_snapshot.json"
    save_bibliography_entries(entries, str(entries_snap))
    save_bibliography_entries(entries, "examples/sample_bibliography_entries.json")
    save_citation_to_bibliography_map(mapping, str(map_snap))
    save_citation_to_bibliography_map(mapping, "examples/sample_citation_to_bibliography_map.json")

    mention_ids = {m.citation_id for m in mentions}
    mapped_ids = set(mapping.keys())
    unmapped_ids = mention_ids - mapped_ids
    mention_counts: dict[str, int] = {}
    for m in mentions:
        mention_counts[m.citation_id] = mention_counts.get(m.citation_id, 0) + 1

    # bibliography_mapping_table.md
    summary_rows = [
        f"| Bibliography entries | {len(entries)} |",
        f"| Citation IDs in mentions | {len(mention_ids)} |",
        f"| Mapped citation IDs | {len(mapped_ids)} |",
        f"| Unmapped citation IDs | {len(unmapped_ids)} |",
    ]
    entry_rows = []
    for e in entries:
        t = (e.title or "")[:40] + ("..." if e.title and len(e.title) > 40 else "")
        a = ", ".join(e.authors[:2]) + ("..." if len(e.authors) > 2 else "")
        raw_p = e.raw_text.replace("\n", " ")[:50] + "..."
        entry_rows.append(f"| {e.citation_id} | {t} | {e.year or ''} | {a} | {raw_p} |")
    map_rows = []
    for cid in sorted(mapped_ids, key=lambda x: int(x.split("_")[1])):
        e = mapping[cid]
        t = (e.title or "")[:40] + ("..." if e.title and len(e.title) > 40 else "")
        map_rows.append(f"| {cid} | {mention_counts.get(cid, 0)} | {t} | {e.year or ''} |")

    table_md = "\n".join([
        "# Bibliography Mapping Table\n",
        "## Summary\n",
        "| Metric | Value |", "|---|---:|", *summary_rows,
        "\n## Bibliography Entries\n",
        "| Citation ID | Title | Year | Authors | Raw Preview |",
        "|---|---|---:|---|---|", *entry_rows,
        "\n## Citation to Bibliography Mapping\n",
        "| Citation ID | Mention Count | Title | Year |",
        "|---|---:|---|---:|", *map_rows,
    ])
    (out / "bibliography_mapping_table.md").write_text(table_md + "\n", encoding="utf-8")

    # citation_to_reference_map.mmd
    (out / "citation_to_reference_map.mmd").write_text(
        "flowchart TD\n"
        "    A[Citation Mentions] --> B[Unique Citation IDs]\n"
        "    C[References Section] --> D[Bibliography Entries]\n"
        "    B --> E[Citation ID Matching]\n"
        "    D --> E\n"
        "    E --> F[citation_to_bibliography_map.json]\n"
        "    F --> G[Step 06 Citation Role Classifier]\n"
        "    E --> R1[ref_1]\n"
        "    E --> R5[ref_5]\n"
        "    E --> R13[ref_13]\n",
        encoding="utf-8",
    )

    # Real paper smoke test
    real_snap_path = Path("reports/step_outputs/step_03/real_paper_parsed_snapshot.json")
    real_mentions_path = Path("reports/step_outputs/step_04/real_paper_citation_mentions_snapshot.json")
    real_lines = ["# Real Paper Bibliography Summary — Step 05\n"]
    real_entry_count = 0
    real_mapped_count = 0
    real_status = "missing"

    if real_snap_path.exists():
        real_lines.append("- **Real parsed snapshot:** PRESENT")
        try:
            real_parsed = load_parsed_paper(str(real_snap_path))
            has_refs = "references" in real_parsed.sections
            real_lines.append(f"- **References section detected:** {'Yes' if has_refs else 'No'}")
            real_entries = extract_bibliography_entries(real_parsed)
            real_entry_count = len(real_entries)
            real_lines.append(f"- **Bibliography entry count:** {real_entry_count}")
            if real_mentions_path.exists():
                with open(real_mentions_path, encoding="utf-8") as f:
                    real_mentions_list = [CitationMention(**d) for d in json.load(f)]
                real_mapping = map_mentions_to_bibliography(real_mentions_list, real_entries)
                real_mapped_count = len(real_mapping)
                real_lines.append(f"- **Mapped citation IDs:** {real_mapped_count}")
                save_bibliography_entries(
                    real_entries, str(out / "real_paper_bibliography_entries_snapshot.json")
                )
                save_citation_to_bibliography_map(
                    real_mapping, str(out / "real_paper_citation_to_bibliography_map_snapshot.json")
                )
            if real_entries:
                real_lines += [
                    "\n### First 10 Bibliography Entries\n",
                    "| Citation ID | Title | Year |", "|---|---|---:|",
                ]
                for e in real_entries[:10]:
                    t = (e.title or "")[:50] + ("..." if e.title and len(e.title) > 50 else "")
                    real_lines.append(f"| {e.citation_id} | {t} | {e.year or ''} |")
            real_status = "success"
        except Exception as exc:
            real_lines.append(f"- **Extraction status:** FAILED — {exc}")
            real_status = "failed"
    else:
        real_lines += [
            "- **Real parsed snapshot:** MISSING",
            "- **Extraction status:** SKIPPED",
        ]
    real_lines.append("\n> Note: Real PDF extraction and reference parsing are heuristic.")
    (out / "real_paper_bibliography_summary.md").write_text(
        "\n".join(real_lines) + "\n", encoding="utf-8"
    )

    return {
        "entry_count": len(entries),
        "mapped_count": len(mapped_ids),
        "unmapped_count": len(unmapped_ids),
        "mapped_ids": sorted(mapped_ids),
        "entries_snapshot": str(entries_snap),
        "map_snapshot": str(map_snap),
        "real_status": real_status,
        "real_entry_count": real_entry_count,
        "real_mapped_count": real_mapped_count,
    }
