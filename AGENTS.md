# EmpiricalWiki — Agent Entry Point

> This file exists so that any coding agent (Codex, Cursor, Claude Code, ...) can operate this repo.
> The authoritative runtime schema lives in [`CLAUDE.md`](CLAUDE.md) — **read it first and follow it exactly**.
> Everything below is a minimal orientation, not a replacement.

## What this repo is

A Karpathy-style LLM wiki specialized for empirical research in accounting, finance, management, and economics. Three layers:

1. `raw/` — user-owned sources (PDF/tex). **Read-only for agents**, with two exceptions: external fetches go to `raw/discovered/`, generated sidecars go to `raw/tmp/` (append-only).
2. `wiki/` — the LLM-maintained, compounding artifact. Typed markdown pages with strict frontmatter and bidirectional `[[wikilinks]]`.
3. Schema — `CLAUDE.md` + `.claude/skills/*/SKILL.md` define how to read, write, and link.

## Hard constraints (full list in CLAUDE.md)

- `raw/papers/`, `raw/notes/`, `raw/web/` are user-owned: never modify or overwrite.
- `wiki/graph/` is derived state: never hand-edit; maintain it only through `tools/research_wiki.py` (`add-edge`, `add-citation`, `rebuild-context-brief`, `rebuild-open-questions`).
- Every forward link requires its backward link (cross-reference table in CLAUDE.md).
- `wiki/index.md` is updated on every ingest; `wiki/log.md` is append-only.
- Page templates: `docs/runtime-page-templates.zh.md`. Theory-paper skeleton: `docs/runtime-theory-skeleton.zh.md`.

## Operations

- Skills (slash commands) live in `.claude/skills/<name>/SKILL.md`. Agents without a skill runner can open the SKILL.md and follow it as a procedure. Core loop: ingest (`/empirical-ingest`, `/theory-ingest`, `/ingest`) → query (`/ask`) → lint (`/check`).
- Setup: `./setup.sh --lang zh` (Windows: `setup.ps1 -Lang zh`).
- Python: prefer `.venv/bin/python`; tools auto-load `~/.env` and project `.env` via `tools/_env.py`.
- Local website view of the wiki: `tools/view.sh` (Quartz, read-only).
