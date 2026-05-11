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
# Raw-text reference block extraction helpers
# ---------------------------------------------------------------------------

_MIN_REFS_SECTION_LEN = 200

# Matches REFERENCES heading including the PDF extraction artifact "R\nEFERENCES"
_REFS_HEADING_RE = re.compile(
    r"(?m)"
    r"(?:^R\s*\n\s*EFERENCES\s*\n"
    r"|^REFERENCES\s*\n"
    r"|^References\s*\n"
    r")",
)

# Lines that signal the start of author biographies or legal footers
_BIOGRAPHY_STOP_RE = re.compile(
    r"received (?:the |his |her )?[A-Z]\.(?:S|E)\."
    r"|received (?:the |his |her )?B\.S\."
    r"|\bis currently\b"
    r"|\bBiography\b"
    r"|Authorized licensed use"
    r"|Downloaded on"
    r"|Restrictions apply",
    re.IGNORECASE,
)


def _trim_after_biography(text: str) -> str:
    """Trim text at the first biography or legal-footer line."""
    m = _BIOGRAPHY_STOP_RE.search(text)
    if not m:
        return text
    line_start = text.rfind("\n", 0, m.start())
    return text[:line_start] if line_start != -1 else text[: m.start()]


def _find_reference_block_in_raw_text(raw_text: str) -> str:
    """Locate the reference list block inside PDF raw text.

    Tries three strategies in order:
    1. Known REFERENCES heading (including split-line PDF artifact R\\nEFERENCES).
    2. [1] marker followed by a capital letter (author name).
    3. Densest consecutive numeric-marker sequence.
    """
    # Strategy A: REFERENCES heading
    heading_m = _REFS_HEADING_RE.search(raw_text)
    if heading_m:
        tail = raw_text[heading_m.end():]
        first_m = re.search(r"\[\d+\]", tail)
        if first_m:
            return _trim_after_biography(tail[first_m.start():])

    # Strategy B: [1] followed by an author-name capital letter
    for m in re.finditer(r"\[1\]\s+[A-Z]", raw_text):
        tail = raw_text[m.start():]
        if re.search(r"\[2\]", tail[:3000]):
            return _trim_after_biography(tail)

    # Strategy C: find the start of the longest consecutive [N] sequence
    markers = list(re.finditer(r"(?m)^\[(\d+)\]", raw_text))
    if markers:
        nums = {int(mk.group(1)): mk for mk in markers}
        for mk in markers:
            n = int(mk.group(1))
            if n + 1 in nums and n + 2 in nums:
                return _trim_after_biography(raw_text[mk.start():])

    return ""


def extract_references_text_best_effort(parsed_paper: ParsedPaper) -> str:
    """Return the best-available references text for a parsed paper.

    Tries parsed sections first; falls back to scanning raw_text when the
    references section is missing or suspiciously short (e.g., the REFERENCES
    heading was split by the PDF extractor and not detected by the parser).
    """
    for key in ("references", "bibliography", "reference"):
        text = parsed_paper.sections.get(key, "")
        if len(text.strip()) >= _MIN_REFS_SECTION_LEN:
            return text

    if parsed_paper.raw_text:
        return _find_reference_block_in_raw_text(parsed_paper.raw_text)

    return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def split_reference_entries(references_text: str) -> list[str]:
    """Split a references section into individual raw entry strings.

    Supports multi-line entries and hyphenated PDF line breaks.
    Entry boundaries are lines that start with [N].
    """
    # Rejoin hyphenated line breaks: "sys-\ntem" -> "system"
    text = re.sub(r"-\s*\n\s*", "", references_text)
    raw_blocks = re.split(r"\n(?=\[\d+\])", text)
    entries: list[str] = []
    for block in raw_blocks:
        block = block.strip()
        if block and re.match(r"\[\d+\]", block):
            entries.append(block)
    return entries


# Matches quoted titles using ASCII straight quotes OR Unicode curly/smart quotes.
# Groups: (open_quote)(title_text)(close_quote)
# IEEE references use “ (") and ” (") around the title.
_QUOTED_TITLE_RE = re.compile(
    r'[“„‟‘‚"]'   # opening quote variant
    r'(.+?)'                                 # title text (lazy)
    r'[”’"]',                      # closing quote variant
    re.DOTALL,
)

# Heuristic: reject extracted titles that look like author fragments or venue fragments.
_BAD_TITLE_RE = re.compile(
    r"^(?:"
    r"[A-Z]\w{0,6},\s*[A-Z]"           # author initial fragment: "Wen, H", "F, G"
    r"|[A-Z]\s*$"                        # single letter: "F"
    r"|\d+,?\s*(?:no|pp|vol)\b"          # volume/page fragment: "7, pp", "12, no"
    r"|(?:Cogn|Veh|Commun|Trans|Lett|Proc|Conf|IEEE)\b"  # venue abbreviation
    r")",
    re.IGNORECASE,
)


def parse_reference_entry(raw_entry: str) -> BibliographyEntry:
    """Parse a single raw reference string into a BibliographyEntry."""
    num_m = re.match(r"^\[(\d+)\]\s*", raw_entry)
    if not num_m:
        return BibliographyEntry(citation_id="ref_unknown", raw_text=raw_entry)

    citation_id = normalize_citation_id(int(num_m.group(1)))
    # Collapse all line breaks (PDF line wrapping inside entries)
    body = re.sub(r"\n+", " ", raw_entry[num_m.end():])
    body = re.sub(r"\s+", " ", body).strip()
    year = _extract_year(body)

    title: str | None = None
    authors_raw: str = ""
    venue: str | None = None
    extraction_method: str = "failed"

    # Strategy 1: quoted title (handles ASCII " and Unicode curly quotes " ")
    quoted_m = _QUOTED_TITLE_RE.search(body)
    if quoted_m:
        raw_title = quoted_m.group(1).strip()
        # Strip trailing punctuation inserted before the closing quote
        clean_title = raw_title.rstrip(",;.").strip()
        clean_title = re.sub(r"\s+", " ", clean_title).strip()
        if len(clean_title) >= 5:
            title = clean_title
            extraction_method = "quoted_title"
        authors_raw = body[: quoted_m.start()].strip().rstrip(",").strip()
        venue_tail = body[quoted_m.end():].strip().lstrip(".").lstrip(",").strip()
        if year:
            venue_tail = re.sub(rf",?\s*\b{year}\b\.?\s*$", "", venue_tail).strip().rstrip(",")
        venue = venue_tail or None

    if title is None:
        # Strategy 2: period-separated heuristic (for non-quoted references)
        boundary = _find_author_title_boundary(body)
        if boundary != -1:
            authors_raw = body[:boundary].strip()
            remainder = body[boundary + 2:]  # skip '. '
            title_end_m = re.search(r"\.\s", remainder)
            candidate = (
                remainder[: title_end_m.start()].strip()
                if title_end_m
                else remainder.strip().rstrip(".")
            )
            # Reject obvious garbage (author fragments, venue abbreviations, etc.)
            if candidate and len(candidate) >= 10 and not _BAD_TITLE_RE.match(candidate):
                title = candidate
                extraction_method = "fallback_heuristic"
                venue = _extract_venue(body, title, year) if title else None
            else:
                extraction_method = "failed"
        else:
            extraction_method = "failed"

    authors = _parse_authors(authors_raw)
    return BibliographyEntry(
        citation_id=citation_id,
        raw_text=raw_entry,
        title=title,
        authors=authors,
        year=year,
        venue=venue,
        metadata={"title_extraction_method": extraction_method},
    )


def extract_bibliography_entries_from_text(references_text: str) -> list[BibliographyEntry]:
    """Parse a references section string into BibliographyEntry objects."""
    return [parse_reference_entry(raw) for raw in split_reference_entries(references_text)]


def extract_bibliography_entries(parsed_paper: ParsedPaper) -> list[BibliographyEntry]:
    """Extract bibliography entries from a ParsedPaper.

    Uses best-effort extraction: tries the parsed references section first,
    then falls back to scanning raw_text when the section is missing.
    """
    refs_text = extract_references_text_best_effort(parsed_paper)
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
