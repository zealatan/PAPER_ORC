"""Paper parser: splits a paper PDF/text into sections and builds ParsedPaper."""

import dataclasses
import json
import re
from pathlib import Path

from papernav.models import ParsedPaper, PaperSection


# ---------------------------------------------------------------------------
# Section name normalisation
# ---------------------------------------------------------------------------

_SECTION_ALIASES: dict[str, str] = {
    "abstract": "abstract",
    "introduction": "introduction",
    "related work": "related_work",
    "related works": "related_work",
    "background": "background",
    "background and motivation": "background",
    "preliminary": "background",
    "preliminaries": "background",
    "method": "method",
    "methods": "method",
    "methodology": "method",
    "approach": "method",
    "proposed method": "method",
    "proposed approach": "method",
    "system model": "method",
    "system overview": "method",
    "problem formulation": "method",
    "experiment": "experiment",
    "experiments": "experiment",
    "experimental setup": "experiment",
    "experimental results": "experiment",
    "experimental evaluation": "experiment",
    "evaluation": "experiment",
    "results": "results",
    "discussion": "discussion",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "conclusion and future work": "conclusion",
    "conclusions and future work": "conclusion",
    "acknowledgment": "acknowledgment",
    "acknowledgments": "acknowledgment",
    "acknowledgement": "acknowledgment",
    "acknowledgements": "acknowledgment",
    "references": "references",
    "bibliography": "references",
}

# Matches headings in PDF-extracted text:
#   "I. Introduction", "1. INTRODUCTION", "Related Work", "REFERENCES"
_PDF_HEADING_RE = re.compile(
    r"(?m)^"
    r"(?:(?:\d+|[IVX]+)[\.\s]+)?"
    r"("
    r"Abstract"
    r"|Introduction"
    r"|Related\s+Works?"
    r"|Background(?:\s+and\s+\w+)?"
    r"|Preliminar(?:y|ies)"
    r"|System\s+(?:Model|Overview)"
    r"|Problem\s+Formulation"
    r"|Proposed\s+(?:Method|Approach)"
    r"|Method(?:ology)?s?"
    r"|Approach"
    r"|Experiment(?:al)?(?:\s+(?:Setup|Results|Evaluation))?s?"
    r"|Evaluation"
    r"|Results?"
    r"|Discussion"
    r"|Conclusions?(?:\s+and\s+Future\s+Work)?"
    r"|Acknowledgm?ents?"
    r"|References?"
    r"|Bibliography"
    r")"
    r"\s*:?\s*$",
    re.IGNORECASE,
)


def _normalize_key(heading: str) -> str | None:
    """Map a raw heading string to a canonical section key, or None if unrecognised."""
    raw = heading.strip().rstrip(":").strip()
    raw = re.sub(r"^(?:\d+|[IVX]+)[\.\s]+", "", raw, flags=re.IGNORECASE).strip()
    return _SECTION_ALIASES.get(raw.lower())


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

def _split_sections(text: str) -> list[PaperSection]:
    """Return PaperSection list from either --- separated or PDF-heading style text."""

    # Strategy 1: synthetic fixture uses \n---\n dividers
    if "\n---\n" in text or "\n---\r\n" in text:
        blocks = re.split(r"\n---+\n", text)
        char_pos = len(blocks[0]) + 5  # skip header block + separator length approx
        result: list[PaperSection] = []
        for block in blocks[1:]:
            block_start = char_pos
            lines = block.strip().splitlines()
            if not lines:
                char_pos += len(block) + 5
                continue
            heading_line = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            key = _normalize_key(heading_line)
            if key is None:
                key = re.sub(r"[^a-z0-9]+", "_", heading_line.rstrip(":").strip().lower())
            result.append(PaperSection(
                name=key,
                title=heading_line.rstrip(":").strip(),
                text=body,
                start_char=block_start,
                end_char=block_start + len(block),
            ))
            char_pos += len(block) + 5
        return result

    # Strategy 2: regex heading detection for PDF-extracted text
    matches = list(_PDF_HEADING_RE.finditer(text))
    if not matches:
        return [PaperSection(name="body", title="Body", text=text.strip(),
                             start_char=0, end_char=len(text))]

    result = []
    for i, m in enumerate(matches):
        heading_name = m.group(1).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        key = _normalize_key(m.group(0).strip())
        if key is None:
            key = re.sub(r"[^a-z0-9]+", "_", heading_name.lower())
        result.append(PaperSection(
            name=key,
            title=heading_name,
            text=body,
            start_char=m.start(),
            end_char=body_end,
        ))
    return result


def _parse_header(block: str) -> tuple[str | None, list[str], str | None]:
    """Extract title, authors, abstract from the first block (before first ---)."""
    title = None
    authors: list[str] = []
    abstract = None

    m = re.search(r"^Title:\s*(.+)$", block, re.MULTILINE | re.IGNORECASE)
    if m:
        title = m.group(1).strip()

    m = re.search(r"^Authors?:\s*(.+)$", block, re.MULTILINE | re.IGNORECASE)
    if m:
        authors = [a.strip() for a in m.group(1).split(",") if a.strip()]

    m = re.search(r"^Abstract\s*:?\s*\n([\s\S]+)", block, re.MULTILINE | re.IGNORECASE)
    if m:
        abstract = m.group(1).strip()

    return title, authors, abstract


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_text(
    text: str,
    paper_id: str | None = None,
    metadata: dict | None = None,
) -> ParsedPaper:
    """Parse a paper text string into a ParsedPaper."""
    if metadata is None:
        metadata = {}

    title: str | None = None
    authors: list[str] = []
    abstract: str | None = None

    if "\n---\n" in text or "\n---\r\n" in text:
        header_block = re.split(r"\n---+\n", text)[0]
        title, authors, abstract = _parse_header(header_block)
    else:
        non_empty = [line for line in text.splitlines() if line.strip()]
        if non_empty:
            title = non_empty[0].strip()

    section_objects = _split_sections(text)

    sections: dict[str, str] = {}
    for sec in section_objects:
        if sec.name not in sections:
            sections[sec.name] = sec.text

    return ParsedPaper(
        paper_id=paper_id or "unknown",
        raw_text=text,
        title=title,
        authors=authors,
        abstract=abstract,
        sections=sections,
        section_objects=section_objects,
        metadata=metadata,
    )


def parse_file(path: str, paper_id: str | None = None) -> ParsedPaper:
    """Parse a .txt or .pdf file into a ParsedPaper."""
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in (".txt", ".pdf"):
        raise ValueError(f"Unsupported file extension: {ext!r}. Expected .txt or .pdf")
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if ext == ".txt":
        text = p.read_text(encoding="utf-8")
        return parse_text(text, paper_id=paper_id or p.stem)
    return parse_pdf(path, paper_id=paper_id or p.stem)


def parse_pdf(path: str, paper_id: str | None = None) -> ParsedPaper:
    """Extract text from a PDF file and parse it into a ParsedPaper."""
    import pypdf  # deferred so non-PDF users don't need pypdf

    p = Path(path)
    pages: list[str] = []
    page_count = 0
    with open(p, "rb") as f:
        reader = pypdf.PdfReader(f)
        page_count = len(reader.pages)
        for page in reader.pages:
            pages.append(page.extract_text() or "")
    raw_text = "\n".join(pages)
    meta = {
        "source_file": str(path),
        "source_type": "pdf",
        "page_count": page_count,
    }
    return parse_text(raw_text, paper_id=paper_id or p.stem, metadata=meta)


def save_parsed_paper(parsed: ParsedPaper, output_path: str) -> None:
    """Serialise a ParsedPaper to a JSON file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = dataclasses.asdict(parsed)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Step-03 output generator
# ---------------------------------------------------------------------------

def load_parsed_paper(path: str) -> ParsedPaper:
    """Load a ParsedPaper from a JSON file produced by save_parsed_paper."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    section_objects = [PaperSection(**s) for s in data.get("section_objects", [])]
    return ParsedPaper(
        paper_id=data["paper_id"],
        raw_text=data.get("raw_text", ""),
        title=data.get("title"),
        authors=data.get("authors", []),
        abstract=data.get("abstract"),
        sections=data.get("sections", {}),
        section_objects=section_objects,
        metadata=data.get("metadata", {}),
    )


def generate_step03_outputs(
    sample_path: str = "examples/sample_paper.txt",
    output_dir: str = "reports/step_outputs/step_03",
) -> dict:
    """Generate all Step 03 visualisation and report files. Returns a status dict."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    parsed = parse_file(sample_path)

    # parsed_paper_snapshot.json
    snapshot_path = out / "parsed_paper_snapshot.json"
    save_parsed_paper(parsed, str(snapshot_path))

    # parsed_sections.md
    rows = []
    for sec in parsed.section_objects:
        has_cit = "Yes" if re.search(r"\[\d+\]", sec.text) else "No"
        preview = " ".join(sec.text.replace("\n", " ").split())[:120]
        rows.append(
            f"| `{sec.name}` | {sec.title} | {len(sec.text):,} | {has_cit} | {preview} |"
        )
    sections_md = "\n".join([
        "# Parsed Sections — Synthetic Fixture\n",
        "| Section Key | Original Title | Character Count | Has Citations | Preview |",
        "|---|---|---:|---|---|",
    ] + rows)
    (out / "parsed_sections.md").write_text(sections_md + "\n", encoding="utf-8")

    # section_split_diagram.mmd
    node_lines = []
    for sec in parsed.section_objects:
        safe_id = sec.name.replace("_", "")
        node_lines.append(f'    P --> {safe_id}["{sec.title}"]')
    mmd = (
        "flowchart TD\n"
        '    A["sample_paper.txt"] --> B[Paper Parser]\n'
        "    B --> P[ParsedPaper]\n"
        + "\n".join(node_lines)
        + "\n    P --> J[parsed_paper_snapshot.json]\n"
    )
    (out / "section_split_diagram.mmd").write_text(mmd, encoding="utf-8")

    # real_paper_parse_summary.md
    real_pdf = Path("papers/real/rtlfixer_2311_16543.pdf")
    lines = ["# Real Paper Parse Summary — Step 03\n",
             f"- **Local PDF path:** `{real_pdf}`"]
    real_status = "missing"
    real_sections: list[str] = []
    real_text_len = 0

    if real_pdf.exists():
        lines.append("- **PDF status:** PRESENT")
        try:
            rp = parse_pdf(str(real_pdf), paper_id="rtlfixer_2311_16543")
            real_text_len = len(rp.raw_text)
            real_sections = list(rp.sections.keys())
            lines.append("- **Text extraction:** SUCCESS")
            lines.append(f"- **Raw text length:** {real_text_len:,} characters")
            lines.append(f"- **Detected title:** {rp.title or '(not detected)'}")
            lines.append(f"- **Detected sections:** {', '.join(real_sections) or '(none)'}")
            lines.append(
                f"- **References detected:** {'Yes' if 'references' in rp.sections else 'No'}"
            )
            snap = out / "real_paper_parsed_snapshot.json"
            save_parsed_paper(rp, str(snap))
            lines.append(f"- **Snapshot saved:** `{snap}`")
            real_status = "success"
        except Exception as exc:
            lines.append(f"- **Text extraction:** FAILED — {exc}")
            real_status = "failed"
    else:
        lines.append("- **PDF status:** MISSING")
        lines.append("- **Text extraction:** SKIPPED")
        lines.append(
            f"\nTo download: `wget -O {real_pdf} https://arxiv.org/pdf/2311.16543`"
        )

    lines.append(
        "\n> Note: This is a smoke test only. "
        "Section detection accuracy is not semantically validated."
    )
    (out / "real_paper_parse_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "parsed_paper_id": parsed.paper_id,
        "section_keys": list(parsed.sections.keys()),
        "section_count": len(parsed.section_objects),
        "raw_text_len": len(parsed.raw_text),
        "snapshot_path": str(snapshot_path),
        "real_pdf_status": real_status,
        "real_sections": real_sections,
        "real_text_len": real_text_len,
    }
