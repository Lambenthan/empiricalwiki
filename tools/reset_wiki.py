#!/usr/bin/env python3
"""Reset wiki state to a clean scaffold (used by /reset skill).

Scopes:
    wiki         delete all .md content under wiki/<entity>/, regenerate
                 index.md, regenerate empty graph/ files. Preserves .gitkeep,
                 wiki/CLAUDE.md, and wiki/log.md.
    raw          delete all files under raw/<sub>/ except .gitkeep.
    log          reset wiki/log.md to empty header.
    checkpoints  call `research_wiki.py checkpoint-clear` to drop batch state.
    all          all of the above.

Usage:
    python3 tools/reset_wiki.py --scope wiki --yes
    python3 tools/reset_wiki.py --scope all --dry-run

Without --yes the tool prints the plan and exits without touching the filesystem.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ENTITY_DIRS = [
    "papers", "concepts", "topics", "people",
    "ideas", "experiments", "claims", "Summary",
    "foundations",
]
RAW_SUBDIRS = ["papers", "notes", "web"]
ALL_SCOPES = ["wiki", "raw", "log", "checkpoints"]

INDEX_TEMPLATE = "# Wiki Index\n\n" + "\n".join(f"{e}:" for e in ENTITY_DIRS) + "\n"
LOG_TEMPLATE = "# OmegaWiki Log\n\n"


def _list_md(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [p for p in directory.glob("*.md") if p.is_file()]


def _list_raw(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [p for p in directory.iterdir() if p.is_file() and p.name != ".gitkeep"]


def plan(project_root: Path, scopes: list[str]) -> dict:
    """Return a structured plan of what will be deleted/reset."""
    p: dict = {"scopes": scopes, "delete_files": [], "reset_files": [], "actions": []}
    wiki = project_root / "wiki"

    if "wiki" in scopes:
        for entity in ENTITY_DIRS:
            for f in _list_md(wiki / entity):
                p["delete_files"].append(str(f.relative_to(project_root)))
        for f in _list_md(wiki / "outputs"):
            p["delete_files"].append(str(f.relative_to(project_root)))
        p["reset_files"].append("wiki/index.md")
        p["reset_files"].append("wiki/graph/edges.jsonl")
        p["reset_files"].append("wiki/graph/context_brief.md")
        p["reset_files"].append("wiki/graph/open_questions.md")

    if "raw" in scopes:
        for sub in RAW_SUBDIRS:
            for f in _list_raw(project_root / "raw" / sub):
                p["delete_files"].append(str(f.relative_to(project_root)))

    if "log" in scopes:
        p["reset_files"].append("wiki/log.md")

    if "checkpoints" in scopes:
        p["actions"].append("research_wiki.py checkpoint-clear")

    return p


def execute(project_root: Path, scopes: list[str]) -> dict:
    """Apply the plan. Returns counts of what was actually changed."""
    deleted = 0
    reset = 0
    wiki = project_root / "wiki"

    if "wiki" in scopes:
        for entity in ENTITY_DIRS + ["outputs"]:
            for f in _list_md(wiki / entity):
                f.unlink()
                deleted += 1
            # Ensure .gitkeep exists so the directory survives commits
            keep = wiki / entity / ".gitkeep"
            if not keep.parent.exists():
                keep.parent.mkdir(parents=True, exist_ok=True)
            if not keep.exists():
                keep.touch()
        (wiki / "index.md").write_text(INDEX_TEMPLATE, encoding="utf-8")
        reset += 1
        graph = wiki / "graph"
        graph.mkdir(parents=True, exist_ok=True)
        (graph / "edges.jsonl").write_text("", encoding="utf-8")
        (graph / "context_brief.md").write_text(
            "# Query Pack\n\n_Auto-generated compressed context. Do not edit._\n",
            encoding="utf-8",
        )
        (graph / "open_questions.md").write_text(
            "# Gap Map\n\n_Auto-generated open questions. Do not edit._\n",
            encoding="utf-8",
        )
        reset += 3

    if "raw" in scopes:
        for sub in RAW_SUBDIRS:
            for f in _list_raw(project_root / "raw" / sub):
                f.unlink()
                deleted += 1
            keep = project_root / "raw" / sub / ".gitkeep"
            if not keep.parent.exists():
                keep.parent.mkdir(parents=True, exist_ok=True)
            if not keep.exists():
                keep.touch()

    if "log" in scopes:
        (wiki / "log.md").write_text(LOG_TEMPLATE, encoding="utf-8")
        reset += 1

    if "checkpoints" in scopes:
        rw = project_root / "tools" / "research_wiki.py"
        if rw.exists():
            try:
                subprocess.run(
                    [sys.executable, str(rw), "checkpoint-clear", "--wiki-root", str(wiki)],
                    check=False, capture_output=True,
                )
            except OSError:
                pass

    return {"deleted_files": deleted, "reset_files": reset}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scope", required=True,
                   help="Comma-separated list, or one of: wiki, raw, log, checkpoints, all")
    p.add_argument("--project-root", default=".", help="Project root (default: cwd)")
    p.add_argument("--yes", action="store_true", help="Apply changes (default: dry-run plan only)")
    p.add_argument("--dry-run", action="store_true", help="Print plan and exit (default behavior)")
    args = p.parse_args()

    if args.scope == "all":
        scopes = list(ALL_SCOPES)
    else:
        scopes = [s.strip() for s in args.scope.split(",") if s.strip()]
        for s in scopes:
            if s not in ALL_SCOPES:
                print(json.dumps({"status": "error",
                                  "message": f"unknown scope: {s}",
                                  "valid": ALL_SCOPES}))
                sys.exit(1)

    root = Path(args.project_root).resolve()
    the_plan = plan(root, scopes)

    if not args.yes or args.dry_run:
        print(json.dumps({"status": "plan", **the_plan}, ensure_ascii=False, indent=2))
        return

    result = execute(root, scopes)
    print(json.dumps({"status": "ok", "scopes": scopes, **result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
