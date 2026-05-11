from pathlib import Path
import argparse

from papernav.parser import parse_file, save_parsed_paper
from papernav.citation.extractor import extract_citations, save_citation_mentions
from papernav.citation.bibliography import (
    extract_bibliography_entries,
    map_mentions_to_bibliography,
    save_bibliography_entries,
    save_citation_to_bibliography_map,
)
from papernav.citation.classifier import classify_citation_roles, save_citation_roles
from papernav.graph.history_tree import (
    build_history_tree,
    save_history_tree,
    render_history_tree_markdown,
    render_history_tree_mermaid,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paper_path")
    parser.add_argument("--paper-id", default="custom_paper")
    parser.add_argument("--title", default="Target Paper")
    parser.add_argument("--output-dir", default="reports/custom_paper")
    args = parser.parse_args()

    paper_path = Path(args.paper_path)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[1] Parsing paper...")
    parsed = parse_file(str(paper_path), paper_id=args.paper_id)
    save_parsed_paper(parsed, str(out_dir / "parsed_paper.json"))

    print("[2] Extracting citations...")
    mentions = extract_citations(parsed)
    save_citation_mentions(mentions, str(out_dir / "citation_mentions.json"))

    print("[3] Extracting bibliography...")
    entries = extract_bibliography_entries(parsed)
    save_bibliography_entries(entries, str(out_dir / "bibliography_entries.json"))

    print("[4] Mapping citations to bibliography...")
    bib_map = map_mentions_to_bibliography(mentions, entries)
    save_citation_to_bibliography_map(
        bib_map,
        str(out_dir / "citation_to_bibliography_map.json"),
    )

    print("[5] Classifying citation roles...")
    roles = classify_citation_roles(mentions, bib_map)
    save_citation_roles(roles, str(out_dir / "citation_roles.json"))

    print("[6] Building history tree...")
    tree = build_history_tree(
        roles,
        bib_map,
        target_title=args.title,
        paper_id=args.paper_id,
    )
    save_history_tree(tree, str(out_dir / "history_tree.json"))

    history_md = render_history_tree_markdown(tree)
    (out_dir / "history_tree.md").write_text(history_md, encoding="utf-8")

    history_mmd = render_history_tree_mermaid(tree)
    (out_dir / "history_tree.mmd").write_text(history_mmd, encoding="utf-8")

    print()
    print("[DONE]")
    print(f"Output directory: {out_dir}")
    print(f"Sections: {list(parsed.sections.keys())}")
    print(f"Citation mentions: {len(mentions)}")
    print(f"Bibliography entries: {len(entries)}")
    print(f"Mapped citations: {len(bib_map)}")
    print(f"Citation roles: {len(roles)}")
    print(f"History tree nodes: {len(tree.get('nodes', []))}")
    print(f"History tree edges: {len(tree.get('edges', []))}")


if __name__ == "__main__":
    main()
