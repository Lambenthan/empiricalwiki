#!/usr/bin/env python3
"""Discovery tool — assemble a ranked shortlist of candidate papers.

This is the deterministic core behind the /discover skill. It produces a
recommendation shortlist from one of three seed modes:

    from-anchors  — given one or more anchor paper IDs (post-/ingest case)
    from-topic    — given a topic/query string (lighter alternative to /init)
    from-wiki     — derive anchors from the wiki's most recent papers

Output is a JSON shortlist on stdout (and optionally a checkpoint file).
Dedupes against papers already in wiki/. Ranking is *not* the same as
init_discovery.py — discovery does not favor surveys; it weights anchor
similarity, influential citations, author h-index, and freshness.

Usage:
    python3 tools/discover.py from-anchors --id 2106.09685 [--id 2305.14314] \\
        [--negative 1810.04805] [--wiki-root wiki/] [--limit 10]
    python3 tools/discover.py from-topic "diffusion model fine-tuning" \\
        [--wiki-root wiki/] [--limit 10]
    python3 tools/discover.py from-wiki --wiki-root wiki/ [--limit 10]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import _env  # noqa: F401 — load .env files

import fetch_s2

# DeepXiv is optional; degrade silently if unavailable.
try:
    import fetch_deepxiv  # type: ignore
except Exception:  # pragma: no cover — defensive
    fetch_deepxiv = None  # type: ignore


# ---------- candidate normalization ----------------------------------------

def _arxiv_id_from_external(external_ids: dict[str, Any] | None) -> str:
    if not external_ids:
        return ""
    for key in ("ArXiv", "arXiv", "ARXIV"):
        if external_ids.get(key):
            return str(external_ids[key])
    return ""


def _normalize_candidate(raw: dict[str, Any], *, source: str, anchor: str = "") -> dict[str, Any]:
    """Flatten an S2/DeepXiv paper record into the discover shortlist schema."""
    if not raw:
        return {}
    external_ids = raw.get("externalIds") or {}
    arxiv_id = raw.get("arxiv_id") or _arxiv_id_from_external(external_ids)
    authors = raw.get("authors") or []
    h_indexes = [a.get("hIndex") for a in authors if isinstance(a, dict) and a.get("hIndex")]
    tldr = raw.get("tldr")
    tldr_text = tldr.get("text") if isinstance(tldr, dict) else (tldr or "")
    return {
        "paperId": raw.get("paperId") or raw.get("s2_id") or "",
        "arxiv_id": arxiv_id,
        "title": raw.get("title") or "",
        "abstract": raw.get("abstract") or "",
        "tldr": tldr_text,
        "year": raw.get("year"),
        "venue": raw.get("venue") or "",
        "authors": [a.get("name", "") for a in authors if isinstance(a, dict)],
        "max_h_index": max(h_indexes) if h_indexes else 0,
        "citation_count": raw.get("citationCount") or 0,
        "influential_citation_count": raw.get("influentialCitationCount") or 0,
        "fields_of_study": raw.get("fieldsOfStudy") or [],
        "publication_types": raw.get("publicationTypes") or [],
        "url": raw.get("url") or "",
        # True when S2's per-edge `isInfluential` flag fired on the anchor↔candidate
        # citation/reference. Stronger signal than the aggregate `influentialCitationCount`:
        # it means the candidate specifically matters to (or was built on by) the anchor,
        # not just that it has many influential citers in general.
        "is_influential_edge": bool(raw.get("_is_influential_edge")),
        "_sources": [source],
        "_anchors": [anchor] if anchor else [],
    }


def _candidate_key(c: dict[str, Any]) -> str:
    """Stable dedup key — prefer arxiv_id, fall back to S2 paperId, then title."""
    if c.get("arxiv_id"):
        return f"arxiv:{c['arxiv_id']}"
    if c.get("paperId"):
        return f"s2:{c['paperId']}"
    title = re.sub(r"\s+", " ", (c.get("title") or "").strip().lower())
    return f"title:{title}" if title else ""


def _merge_candidate(existing: dict[str, Any], incoming: dict[str, Any]) -> None:
    """Union sources/anchors; keep richer field values from either side."""
    for src in incoming.get("_sources", []):
        if src not in existing["_sources"]:
            existing["_sources"].append(src)
    for anchor in incoming.get("_anchors", []):
        if anchor and anchor not in existing["_anchors"]:
            existing["_anchors"].append(anchor)
    for key in ("abstract", "tldr", "venue", "url"):
        if not existing.get(key) and incoming.get(key):
            existing[key] = incoming[key]
    if not existing.get("authors") and incoming.get("authors"):
        existing["authors"] = incoming["authors"]
    if not existing.get("fields_of_study") and incoming.get("fields_of_study"):
        existing["fields_of_study"] = incoming["fields_of_study"]
    # Numeric fields: prefer the larger reading (S2 is authoritative; DeepXiv often lacks them).
    for key in ("max_h_index", "citation_count", "influential_citation_count"):
        existing[key] = max(existing.get(key) or 0, incoming.get(key) or 0)
    # Influential-edge is a union: if any anchor↔candidate edge was flagged influential,
    # the candidate keeps the flag even when other channels surfaced it without the flag.
    existing["is_influential_edge"] = bool(existing.get("is_influential_edge") or incoming.get("is_influential_edge"))
    if not existing.get("year") and incoming.get("year"):
        existing["year"] = incoming["year"]


def _dedupe(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for c in candidates:
        key = _candidate_key(c)
        if not key:
            continue
        if key in out:
            _merge_candidate(out[key], c)
        else:
            out[key] = c
    return list(out.values())


# ---------- wiki dedup -----------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_ARXIV_LINE_RE = re.compile(r"^arxiv_id\s*:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


def _extract_arxiv_id_from_paper(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return ""
    fm = m.group(1)
    am = _ARXIV_LINE_RE.search(fm)
    return (am.group(1).strip() if am else "")


def _wiki_known_arxiv_ids(wiki_root: Path | None) -> set[str]:
    """Scan wiki/papers/*.md for arxiv_id frontmatter values."""
    if not wiki_root or not wiki_root.exists():
        return set()
    papers_dir = wiki_root / "papers"
    if not papers_dir.exists():
        return set()
    seen: set[str] = set()
    for path in papers_dir.glob("*.md"):
        aid = _extract_arxiv_id_from_paper(path)
        if aid:
            # Strip arXiv prefixes for match consistency.
            seen.add(aid.removeprefix("arXiv:").removeprefix("ARXIV:").removeprefix("arxiv:").strip())
    return seen


def _filter_against_wiki(candidates: list[dict[str, Any]], known: set[str]) -> list[dict[str, Any]]:
    if not known:
        return candidates
    return [c for c in candidates if c.get("arxiv_id", "").strip() not in known]


# ---------- ranking --------------------------------------------------------

def _influence_score(infl: int, total: int) -> float:
    """Reward influential citations more than raw count.

    Uses log scaling to keep mega-cited papers from saturating.
    """
    infl = max(0, int(infl or 0))
    total = max(0, int(total or 0))
    return 0.7 * math.log1p(infl) / math.log1p(50) + 0.3 * math.log1p(total) / math.log1p(1000)


def _hindex_score(h: int) -> float:
    """Mild bonus from author credibility — cap so it can't dominate."""
    h = max(0, int(h or 0))
    return min(1.0, h / 60.0)


def _freshness_score(year: int | None) -> float:
    if not year:
        return 0.4
    now = _dt.date.today().year
    age = max(0, now - int(year))
    if age <= 1:
        return 1.0
    if age <= 3:
        return 0.85
    if age <= 6:
        return 0.6
    if age <= 10:
        return 0.4
    return 0.25


def _anchor_overlap_score(c: dict[str, Any]) -> float:
    """How many anchors surfaced this candidate (more anchors = stronger signal)."""
    n = len(c.get("_anchors") or [])
    if n == 0:
        return 0.0
    return min(1.0, 0.5 + 0.25 * (n - 1))


def _channel_diversity_score(c: dict[str, Any]) -> float:
    """Bonus when the same candidate was surfaced by multiple channels.

    A paper appearing from recommend + references + citations is a
    stronger signal than one appearing only from recommend — it means
    the paper is semantically similar AND part of the citation graph.
    """
    return min(1.0, 0.4 * len(set(c.get("_sources") or [])))


def _anchor_influence_edge_score(c: dict[str, Any]) -> float:
    """S2's per-edge `isInfluential` flag for this anchor↔candidate citation.

    When True, S2's citation-analysis model judged that the anchor substantively
    built on this candidate (references channel) or this candidate substantively
    built on the anchor (citations channel). That is a much sharper "this matters
    to the anchor" signal than the aggregate `influential_citation_count`, which
    reflects the candidate's influence in general.
    """
    return 1.0 if c.get("is_influential_edge") else 0.0


def _score(c: dict[str, Any], *, anchor_mode: bool) -> float:
    influence = _influence_score(c.get("influential_citation_count", 0), c.get("citation_count", 0))
    h = _hindex_score(c.get("max_h_index", 0))
    fresh = _freshness_score(c.get("year"))
    diversity = _channel_diversity_score(c)
    if anchor_mode:
        # With three channels plus the per-edge isInfluential flag:
        #   - influence: aggregate prestige (candidate's general importance)
        #   - anchor_influence_edge: specific anchor↔candidate significance (sharp, often 0)
        #   - anchor overlap: how many anchors surfaced the candidate
        #   - channel diversity: how many channels surfaced the candidate
        #   - freshness + h-index: supporting signals
        anchor = _anchor_overlap_score(c)
        edge = _anchor_influence_edge_score(c)
        return (
            0.25 * influence
            + 0.20 * edge
            + 0.15 * anchor
            + 0.15 * diversity
            + 0.15 * fresh
            + 0.10 * h
        )
    # Topic / wiki mode: no anchor signal — lean harder on influence and freshness.
    # `is_influential_edge` is always False here (no anchor edge exists), so skip it.
    return 0.45 * influence + 0.25 * fresh + 0.15 * h + 0.15 * diversity


def _rationale(c: dict[str, Any], *, anchor_mode: bool) -> str:
    bits: list[str] = []
    if anchor_mode and c.get("is_influential_edge"):
        # Lead with this — it is the sharpest signal we have.
        bits.append("influential edge with anchor")
    if anchor_mode and c.get("_anchors"):
        bits.append(f"from {len(c['_anchors'])} anchor(s)")
    if c.get("influential_citation_count"):
        bits.append(f"{c['influential_citation_count']} influential citations")
    elif c.get("citation_count"):
        bits.append(f"{c['citation_count']} citations")
    if c.get("max_h_index"):
        bits.append(f"top author h-index {c['max_h_index']}")
    if c.get("year"):
        bits.append(str(c["year"]))
    return "; ".join(bits) if bits else "candidate"


# ---------- candidate gathering --------------------------------------------

def _gather_from_anchors(
    positive: list[str],
    negative: list[str],
    per_anchor_limit: int,
    *,
    citation_expand: bool = True,
    citation_limit: int = 30,
) -> list[dict[str, Any]]:
    """Three-channel anchor gather: recommend + references + citations.

    Each channel fills a different gap:
      - recommend:  semantic neighbors (S2 tends toward recent work)
      - references: what the anchor cites — surfaces older canonical work
      - citations:  what cites the anchor — surfaces high-impact follow-ups

    Without references/citations, anchor mode collapses into "recent papers
    near the topic", which overlaps with /daily-arxiv. With them, anchor mode
    becomes a genuine literature-graph walk from the anchor.
    """
    candidates: list[dict[str, Any]] = []
    # One call-set per anchor preserves which anchor surfaced which candidate;
    # this matters for the anchor-overlap signal in ranking.
    for anchor in positive:
        # Channel 1: semantic recommendations
        try:
            recs = fetch_s2.recommend([anchor], negative_ids=negative, limit=per_anchor_limit)
        except Exception as exc:
            print(f"warn: S2 recommend failed for {anchor}: {exc}", file=sys.stderr)
            recs = []
        for raw in recs:
            norm = _normalize_candidate(raw, source="s2_recommend", anchor=anchor)
            if norm:
                candidates.append(norm)

        if not citation_expand:
            continue

        # Channel 2: what the anchor cites (older canonical work)
        try:
            refs = fetch_s2.references(anchor, limit=citation_limit)
        except Exception as exc:
            print(f"warn: S2 references failed for {anchor}: {exc}", file=sys.stderr)
            refs = []
        for raw in refs:
            norm = _normalize_candidate(raw, source="s2_reference", anchor=anchor)
            if norm:
                candidates.append(norm)

        # Channel 3: what cites the anchor (high-impact follow-ups). S2 returns
        # citations in reverse-chronological order, so capping at citation_limit
        # keeps costs bounded without losing the most recent impactful work.
        try:
            cits = fetch_s2.citations(anchor, limit=citation_limit)
        except Exception as exc:
            print(f"warn: S2 citations failed for {anchor}: {exc}", file=sys.stderr)
            cits = []
        for raw in cits:
            norm = _normalize_candidate(raw, source="s2_citation", anchor=anchor)
            if norm:
                candidates.append(norm)
    return candidates


def _gather_from_topic(topic: str, limit: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    try:
        s2_results = fetch_s2.search(topic, limit=limit)
    except Exception as exc:
        print(f"warn: S2 search failed for {topic!r}: {exc}", file=sys.stderr)
        s2_results = []
    for raw in s2_results:
        norm = _normalize_candidate(raw, source="s2_search")
        if norm:
            candidates.append(norm)

    if fetch_deepxiv is not None:
        try:
            dx_results = fetch_deepxiv.search(topic, limit=limit)
        except Exception:
            dx_results = []
        for raw in dx_results or []:
            norm = _normalize_candidate(raw, source="deepxiv_search")
            if norm:
                candidates.append(norm)
    return candidates


def _wiki_recent_anchors(wiki_root: Path, k: int) -> list[str]:
    """Pick the K most recently modified paper pages and return their arxiv IDs."""
    papers_dir = wiki_root / "papers"
    if not papers_dir.exists():
        return []
    paths = sorted(papers_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    anchors: list[str] = []
    for path in paths:
        aid = _extract_arxiv_id_from_paper(path)
        if aid:
            anchors.append(aid.removeprefix("arXiv:").removeprefix("ARXIV:").removeprefix("arxiv:").strip())
            if len(anchors) >= k:
                break
    return anchors


# ---------- shortlist assembly ---------------------------------------------

def build_shortlist(
    *,
    mode: str,
    positive_ids: list[str] | None = None,
    negative_ids: list[str] | None = None,
    topic: str = "",
    wiki_root: Path | None = None,
    limit: int = 10,
    per_anchor_limit: int = 50,
    citation_expand: bool = True,
    citation_limit: int = 30,
) -> dict[str, Any]:
    """Run the discovery pipeline and return a structured shortlist payload."""
    positive_ids = positive_ids or []
    negative_ids = negative_ids or []
    anchor_mode = mode in ("anchors", "wiki")

    if mode == "anchors":
        if not positive_ids:
            raise ValueError("from-anchors requires at least one --id")
        candidates = _gather_from_anchors(
            positive_ids,
            negative_ids,
            per_anchor_limit,
            citation_expand=citation_expand,
            citation_limit=citation_limit,
        )
        seed_summary = {
            "mode": "anchors",
            "positive_ids": positive_ids,
            "negative_ids": negative_ids,
            "citation_expand": citation_expand,
        }
    elif mode == "topic":
        if not topic:
            raise ValueError("from-topic requires a query string")
        candidates = _gather_from_topic(topic, max(20, limit * 4))
        seed_summary = {"mode": "topic", "topic": topic}
    elif mode == "wiki":
        if not wiki_root:
            raise ValueError("from-wiki requires --wiki-root")
        derived = _wiki_recent_anchors(wiki_root, k=3)
        if not derived:
            raise ValueError("from-wiki found no anchorable papers under wiki/papers/")
        candidates = _gather_from_anchors(
            derived,
            negative_ids,
            per_anchor_limit,
            citation_expand=citation_expand,
            citation_limit=citation_limit,
        )
        seed_summary = {
            "mode": "wiki",
            "derived_anchors": derived,
            "citation_expand": citation_expand,
        }
    else:
        raise ValueError(f"unknown mode: {mode}")

    candidates = _dedupe(candidates)
    known = _wiki_known_arxiv_ids(wiki_root) if wiki_root else set()
    candidates = _filter_against_wiki(candidates, known)

    for c in candidates:
        c["_score"] = round(_score(c, anchor_mode=anchor_mode), 4)
        c["_rationale"] = _rationale(c, anchor_mode=anchor_mode)

    candidates.sort(key=lambda c: c["_score"], reverse=True)
    shortlist = candidates[:limit]

    return {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "seed": seed_summary,
        "wiki_dedup_count": len(known),
        "candidates_total": len(candidates),
        "shortlist_count": len(shortlist),
        "shortlist": shortlist,
    }


# ---------- output formatting ---------------------------------------------

def _format_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    seed = payload.get("seed") or {}
    mode = seed.get("mode", "?")
    if mode == "anchors":
        seed_desc = f"anchors: {', '.join(seed.get('positive_ids', []))}"
        if seed.get("negative_ids"):
            seed_desc += f" | negatives: {', '.join(seed['negative_ids'])}"
    elif mode == "topic":
        seed_desc = f'topic: "{seed.get("topic", "")}"'
    elif mode == "wiki":
        seed_desc = f"derived from wiki anchors: {', '.join(seed.get('derived_anchors', []))}"
    else:
        seed_desc = mode

    lines.append(f"# Discover shortlist ({mode})")
    lines.append(f"_Seed_: {seed_desc}")
    lines.append(
        f"_Stats_: {payload.get('shortlist_count', 0)} shown / "
        f"{payload.get('candidates_total', 0)} candidates / "
        f"{payload.get('wiki_dedup_count', 0)} already in wiki"
    )
    lines.append("")
    for i, c in enumerate(payload.get("shortlist") or [], start=1):
        title = c.get("title") or "(untitled)"
        aid = c.get("arxiv_id") or c.get("paperId") or ""
        rationale = c.get("_rationale") or ""
        score = c.get("_score", 0)
        lines.append(f"{i}. **{title}**  ")
        lines.append(f"   `{aid}` — score {score} — {rationale}")
        if c.get("tldr"):
            lines.append(f"   > {c['tldr']}")
        lines.append("")
    return "\n".join(lines)


# ---------- CLI ------------------------------------------------------------

def _slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return text[:48] or "discover"


def main() -> None:
    parser = argparse.ArgumentParser(description="OmegaWiki discovery shortlist builder")
    sub = parser.add_subparsers(dest="command", required=True)

    common_args: list[tuple[str, dict[str, Any]]] = [
        ("--wiki-root", {"type": Path, "default": None, "help": "Wiki root for dedup against existing papers"}),
        ("--limit", {"type": int, "default": 10, "help": "Max shortlist size (default 10)"}),
        ("--per-anchor-limit", {"type": int, "default": 50, "help": "Recs requested per anchor (default 50)"}),
        ("--output-checkpoint", {"type": Path, "default": None, "help": "Also write JSON to this path"}),
        ("--markdown", {"action": "store_true", "help": "Print human-readable markdown instead of JSON"}),
    ]

    # Citation-expansion flags apply only to anchor and wiki modes.
    anchor_expand_args: list[tuple[str, dict[str, Any]]] = [
        ("--no-citation-expand", {"dest": "citation_expand", "action": "store_false", "help": "Skip references/citations fan-out (recommend channel only; faster but narrower)"}),
        ("--citation-limit", {"type": int, "default": 30, "help": "Per-anchor cap for references and citations channels (default 30 each)"}),
    ]

    p_anchors = sub.add_parser("from-anchors", help="Recommend from one or more anchor papers")
    p_anchors.add_argument("--id", dest="positive_ids", action="append", default=[], required=True, help="Anchor paper ID (repeatable)")
    p_anchors.add_argument("--negative", dest="negative_ids", action="append", default=[], help="Push recommendations away from this ID (repeatable)")
    for flag, kwargs in common_args:
        p_anchors.add_argument(flag, **kwargs)
    for flag, kwargs in anchor_expand_args:
        p_anchors.add_argument(flag, **kwargs)

    p_topic = sub.add_parser("from-topic", help="Recommend from a topic / query string")
    p_topic.add_argument("topic", help="Topic or query string")
    for flag, kwargs in common_args:
        p_topic.add_argument(flag, **kwargs)

    p_wiki = sub.add_parser("from-wiki", help="Derive seeds from the wiki's recent papers")
    for flag, kwargs in common_args:
        p_wiki.add_argument(flag, **kwargs)
    for flag, kwargs in anchor_expand_args:
        p_wiki.add_argument(flag, **kwargs)

    args = parser.parse_args()

    if args.command == "from-anchors":
        payload = build_shortlist(
            mode="anchors",
            positive_ids=args.positive_ids,
            negative_ids=args.negative_ids,
            wiki_root=args.wiki_root,
            limit=args.limit,
            per_anchor_limit=args.per_anchor_limit,
            citation_expand=args.citation_expand,
            citation_limit=args.citation_limit,
        )
        seed_slug = _slugify("-".join(args.positive_ids[:2]))
    elif args.command == "from-topic":
        payload = build_shortlist(
            mode="topic",
            topic=args.topic,
            wiki_root=args.wiki_root,
            limit=args.limit,
            per_anchor_limit=args.per_anchor_limit,
        )
        seed_slug = _slugify(args.topic)
    elif args.command == "from-wiki":
        if not args.wiki_root:
            parser.error("from-wiki requires --wiki-root")
        payload = build_shortlist(
            mode="wiki",
            wiki_root=args.wiki_root,
            limit=args.limit,
            per_anchor_limit=args.per_anchor_limit,
            citation_expand=args.citation_expand,
            citation_limit=args.citation_limit,
        )
        seed_slug = "wiki"
    else:
        parser.error(f"unknown command: {args.command}")
        return

    if args.output_checkpoint:
        out_path = args.output_checkpoint
        if out_path.is_dir() or str(out_path).endswith("/"):
            today = _dt.date.today().isoformat()
            out_path = out_path / f"discover-{seed_slug}-{today}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"checkpoint written: {out_path}", file=sys.stderr)

    if args.markdown:
        print(_format_markdown(payload))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
