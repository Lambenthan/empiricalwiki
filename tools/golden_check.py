#!/usr/bin/env python3
"""Golden-standard checker for the ingest corridor.

Asserts two layers of structural facts that must not regress after skill edits:
  1. min edge counts per edge type emitted for the benchmark paper
  2. key construct keywords present somewhere in the expected entity directory

Slugs and wording are allowed to vary between ingest runs; counts and
construct placement are not.

Usage:
    python3 tools/golden_check.py --wiki wiki --golden tests/golden/daifei-2025.golden.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_edges(wiki: Path) -> list[dict]:
    path = wiki / "graph" / "edges.jsonl"
    if not path.exists():
        return []
    edges = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            edges.append(json.loads(line))
        except json.JSONDecodeError:
            # dedup_edges deliberately preserves malformed lines; skip them
            # here the same way every other loader does.
            continue
    return edges


def find_paper_slug(wiki: Path, title_keywords: list[str]) -> str | None:
    """Locate the benchmark paper page by keywords in its frontmatter title.

    Matching against the whole body is too loose: cross-links make unrelated
    papers mention the same constructs, and an alphabetically earlier page
    would win. The title line is the only reliable discriminator.
    """
    papers = wiki / "papers"
    if not papers.is_dir():
        return None
    for page in sorted(papers.glob("*.md")):
        title = ""
        for line in page.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("title:"):
                title = line
                break
        if title and all(kw in title for kw in title_keywords):
            return f"papers/{page.stem}"
    return None


def check(wiki: Path, golden: dict) -> int:
    failures: list[str] = []
    notes: list[str] = []

    paper = find_paper_slug(wiki, golden["paper_title_keywords"])
    if paper is None:
        print(f"FAIL  paper page not found (keywords: {golden['paper_title_keywords']})")
        return 1
    notes.append(f"paper page: {paper}")

    # Layer 1: min edge counts per type, outgoing from the benchmark paper.
    edges = load_edges(wiki)
    counts: dict[str, int] = {}
    for e in edges:
        if e.get("from") == paper or e.get("to") == paper:
            counts[e.get("type", "?")] = counts.get(e.get("type", "?"), 0) + 1
    for etype, minimum in golden.get("min_edge_counts", {}).items():
        got = counts.get(etype, 0)
        status = "ok  " if got >= minimum else "FAIL"
        line = f"{status}  edge {etype}: {got} (min {minimum})"
        (notes if got >= minimum else failures).append(line)

    # Layer 2: construct keywords must land in the expected entity directory.
    for req in golden.get("required_pages", []):
        directory = wiki / req["type"]
        keyword = req["keyword"]
        hit = None
        if directory.is_dir():
            for page in sorted(directory.glob("*.md")):
                if keyword in page.read_text(encoding="utf-8", errors="ignore"):
                    hit = page.name
                    break
        if hit:
            notes.append(f"ok    {req['type']}/ contains '{keyword}' ({hit})")
        else:
            failures.append(f"FAIL  {req['type']}/ missing construct '{keyword}'")

    for line in notes:
        print(line)
    for line in failures:
        print(line)
    print(f"\n{'PASS' if not failures else 'FAIL'}: "
          f"{len(failures)} failure(s), {len(notes)} check(s) ok")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default="wiki", help="wiki root to check")
    ap.add_argument("--golden", required=True, help="golden json file")
    args = ap.parse_args()
    golden = json.loads(Path(args.golden).read_text(encoding="utf-8"))
    return check(Path(args.wiki), golden)


if __name__ == "__main__":
    sys.exit(main())
