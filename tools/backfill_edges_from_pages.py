#!/usr/bin/env python3
"""Backfill graph semantic edges from existing page wikilinks.

Recovery utility for wikis whose papers were authored in bulk (not via
`/ingest` or `/empirical-ingest`), so `graph/edges.jsonl` never received the
empirical-extraction edges. The relationships are still present on the pages —
in the body `[[wikilinks]]` — so we reconstruct the edges deterministically:
for each empirical paper, every body wikilink is resolved to a target page,
and the edge type is inferred from that page's directory (page type).

This reads only page wikilinks; it does NOT re-read PDFs or call an LLM, and it
never modifies page content. Output is a JSON array on stdout suitable for
`research_wiki.py batch-edges` (which dedups and validates each edge).

Theory papers (`paper_kind: theory`) are skipped: their relationship to a
mechanism is `formalizes_mechanism`, not the empirical `tests_mechanism`, so
mechanical empirical inference would mislabel them. Their edges are written by
`/theory-ingest` instead.

Usage:
    python tools/backfill_edges_from_pages.py wiki | \
        python tools/research_wiki.py batch-edges wiki
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Target page type -> (edge type, whether confidence is required).
# Mirrors the empirical-extraction edges in tools/_schemas.py.
TYPE_TO_EDGE = {
    "variables": ("operationalizes", True),
    "datasets": ("uses_dataset", True),
    "models": ("estimates_model", True),
    "mechanisms": ("tests_mechanism", True),
    "hypotheses": ("tests_hypothesis", True),
    "identification": ("addresses_endogeneity_with", True),
    "robustness": ("uses_robustness_check", True),
    "heterogeneity": ("uses_heterogeneity_split", True),
    "tables": ("reports_table", False),
}

# When a slug exists under more than one directory, prefer the empirical types
# above over generic knowledge types (concepts etc.).
TYPE_PRIORITY = list(TYPE_TO_EDGE) + [
    "concepts", "foundations", "assumptions", "propositions",
    "people", "topics", "ideas", "claims", "experiments", "Summary", "papers",
]

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
BACKFILL_EVIDENCE = "backfilled from page wikilink (not ingest-verified)"


def _entity_dirs(wiki: Path) -> list[Path]:
    return [p for p in wiki.iterdir() if p.is_dir() and p.name != "graph"
            and p.name != "outputs"]


def build_slug_index(wiki: Path) -> dict[str, str]:
    """Map page slug (filename stem) -> page type, resolving collisions by priority."""
    index: dict[str, str] = {}
    rank = {t: i for i, t in enumerate(TYPE_PRIORITY)}
    for d in _entity_dirs(wiki):
        ptype = d.name
        for f in d.glob("*.md"):
            slug = f.stem
            if slug in index:
                # Keep the higher-priority (lower rank) type.
                if rank.get(ptype, 999) < rank.get(index[slug], 999):
                    index[slug] = ptype
            else:
                index[slug] = ptype
    return index


def paper_kind(text: str) -> str:
    m = re.search(r"^paper_kind:\s*([A-Za-z]+)", text, re.MULTILINE)
    return m.group(1).strip() if m else "empirical"


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: backfill_edges_from_pages.py <wiki_dir>", file=sys.stderr)
        sys.exit(2)
    wiki = Path(sys.argv[1])
    papers_dir = wiki / "papers"
    if not papers_dir.is_dir():
        print(f"no papers/ under {wiki}", file=sys.stderr)
        sys.exit(2)

    index = build_slug_index(wiki)
    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    skipped_theory = 0
    unresolved: set[str] = set()
    per_paper: dict[str, int] = {}

    for f in sorted(papers_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if paper_kind(text) == "theory":
            skipped_theory += 1
            continue
        from_id = f"papers/{f.stem}"
        count = 0
        for raw in WIKILINK.findall(text):
            target = raw.strip()
            ptype = index.get(target)
            if ptype is None:
                unresolved.add(target)
                continue
            if ptype not in TYPE_TO_EDGE:
                continue  # paper-paper, concept, foundation, etc. -> not mechanical
            edge_type, needs_conf = TYPE_TO_EDGE[ptype]
            to_id = f"{ptype}/{target}"
            key = (from_id, to_id, edge_type)
            if key in seen:
                continue
            seen.add(key)
            edge = {"from": from_id, "to": to_id, "type": edge_type,
                    "evidence": BACKFILL_EVIDENCE}
            if needs_conf:
                edge["confidence"] = "medium"
            edges.append(edge)
            count += 1
        if count:
            per_paper[from_id] = count

    json.dump(edges, sys.stdout, ensure_ascii=False, indent=2)
    print(file=sys.stdout)
    # Human-readable summary to stderr (does not pollute the JSON on stdout).
    print(f"[backfill] empirical papers processed: {len(per_paper)}; "
          f"theory papers skipped: {skipped_theory}; "
          f"edges proposed: {len(edges)}; "
          f"unresolved wikilinks: {len(unresolved)}", file=sys.stderr)
    if unresolved:
        sample = ", ".join(sorted(unresolved)[:8])
        print(f"[backfill] unresolved (likely dead links / paper-paper): {sample}"
              + (" ..." if len(unresolved) > 8 else ""), file=sys.stderr)


if __name__ == "__main__":
    main()
