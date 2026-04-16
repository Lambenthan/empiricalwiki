#!/usr/bin/env python3
"""Semantic Scholar API wrapper.

Usage:
    python3 tools/fetch_s2.py search "low rank adaptation"
    python3 tools/fetch_s2.py paper 2106.09685
    python3 tools/fetch_s2.py citations 2106.09685
    python3 tools/fetch_s2.py references 2106.09685
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import _env  # noqa: F401 — load .env files for API keys

import requests

BASE_URL = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,title,abstract,authors,year,citationCount,venue,externalIds,url"
S2_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
RATE_LIMIT_DELAY = 1.0 if S2_API_KEY else 3.0  # faster with API key
MAX_RETRIES = 3

_HEADERS = {"x-api-key": S2_API_KEY} if S2_API_KEY else {}


def _bare_arxiv_id(arxiv_id: str) -> str:
    """Strip optional ARXIV:/arxiv: prefix so callers can pass either form."""
    return arxiv_id.removeprefix("ARXIV:").removeprefix("arxiv:")


def _get(endpoint: str, params: dict | None = None) -> dict | list:
    """Make a GET request to S2 API with basic rate limiting."""
    time.sleep(RATE_LIMIT_DELAY)
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(MAX_RETRIES):
        resp = requests.get(url, params=params or {}, headers=_HEADERS, timeout=30)
        if resp.status_code == 429:
            wait = 60 * (attempt + 1)  # 60s, 120s, 180s
            print(f"Rate limited, waiting {wait}s... (attempt {attempt+1}/{MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"S2 API rate limited after {MAX_RETRIES} retries")


def search(query: str, limit: int = 10) -> list[dict]:
    """Search papers by query string."""
    data = _get("/paper/search", {
        "query": query,
        "limit": limit,
        "fields": FIELDS,
    })
    return data.get("data", [])


def paper(arxiv_id: str) -> dict:
    """Get paper details by arXiv ID."""
    return _get(f"/paper/ARXIV:{_bare_arxiv_id(arxiv_id)}", {"fields": FIELDS})


def citations(arxiv_id: str, limit: int = 100) -> list[dict]:
    """Get papers that cite the given paper."""
    data = _get(f"/paper/ARXIV:{_bare_arxiv_id(arxiv_id)}/citations", {
        "limit": limit,
        "fields": FIELDS,
    })
    return [item.get("citingPaper", {}) for item in data.get("data", [])]


def references(arxiv_id: str, limit: int = 100) -> list[dict]:
    """Get papers referenced by the given paper."""
    data = _get(f"/paper/ARXIV:{_bare_arxiv_id(arxiv_id)}/references", {
        "limit": limit,
        "fields": FIELDS,
    })
    return [item.get("citedPaper", {}) for item in data.get("data", [])]


def main():
    parser = argparse.ArgumentParser(description="Semantic Scholar API wrapper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search papers")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("n", nargs="?", type=int, default=10, help="Number of results")

    p_paper = sub.add_parser("paper", help="Get paper details")
    p_paper.add_argument("arxiv_id", help="arXiv ID (e.g., 2106.09685)")

    p_cite = sub.add_parser("citations", help="Get citations")
    p_cite.add_argument("arxiv_id", help="arXiv ID")

    p_refs = sub.add_parser("references", help="Get references")
    p_refs.add_argument("arxiv_id", help="arXiv ID")

    args = parser.parse_args()

    if args.command == "search":
        result = search(args.query, args.n)
    elif args.command == "paper":
        result = paper(args.arxiv_id)
    elif args.command == "citations":
        result = citations(args.arxiv_id)
    elif args.command == "references":
        result = references(args.arxiv_id)
    else:
        result = {}

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
