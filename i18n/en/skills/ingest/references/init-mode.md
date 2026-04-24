# /ingest INIT MODE and Parallel Safety

Open this reference when `/ingest` is invoked by `/init` as a parallel subagent, or any time you need to understand what concurrent ingests may be doing to shared files.

## When INIT MODE is active

INIT MODE is active for any `/ingest` invocation whose source path originates from `.checkpoints/init-sources.json`. The parent `/init` runs one `/ingest` per paper in an isolated `git worktree`, following the contract in `skills/init/references/parallel-ingest.md`.

In INIT MODE:

- the source is always a `canonical_ingest_path` already prepared by `/init` (a `raw/tmp/...` path for user-owned papers, or a `raw/discovered/...` path for introduced papers)
- `raw/` is strictly read-only — do not write to `raw/tmp/`, `raw/discovered/`, or anywhere else under `raw/`
- `fetch_s2.py citations <arxiv-id>` and `fetch_s2.py references <arxiv-id>` are **skipped** — the parent `/init` does a unified citation sweep at fan-in
- `rebuild-context-brief` and `rebuild-open-questions` are **skipped** — the parent runs them once after all subagents merge
- conflict-prone topic writes are **skipped** — if multiple parallel ingests all try to append to the same topic, they will merge-conflict. Let the parent handle topic updates after fan-in, or defer them to `/edit`.

Everything else — paper page creation, concept/claim dedup via `find-similar-*`, people page creation, paper `## Related` links, graph edges for concept/claim/foundation — still runs per subagent.

## Detecting INIT MODE

`/init` passes the canonical path in the subagent prompt. A `/ingest` invocation can recognize INIT MODE by either of:

- the source path starts with `raw/tmp/` or `raw/discovered/` **and** the `.checkpoints/init-sources.json` manifest references it
- the subagent prompt explicitly states "INIT MODE"

When both signals are absent, treat the invocation as a direct user call and run the full workflow (including citations, rebuilds, and any `raw/tmp/` preparation needed).

## Parallel-safe writes

Even outside INIT MODE, assume another `/ingest` may be running concurrently — batch ingest is already on the roadmap. Three rules make concurrent writes safe:

1. **Every shared-file write goes through a tool.** `graph/edges.jsonl`, `graph/citations.jsonl`, `index.md`, and `log.md` are written via `tools/research_wiki.py add-edge`, `add-citation`, index updates, and `log`. The tool layer uses append semantics and the repository's `.gitattributes` declares `merge=union` for these paths, so parallel worktrees can merge without conflict.
2. **Slugs are allocated deterministically.** `tools/research_wiki.py slug "<title>"` produces the same slug from the same title regardless of which worktree runs it. Collisions are resolved by numeric suffix via the tool, not by ad-hoc renaming.
3. **Never lock or in-place-rewrite a shared file.** Rewriting `wiki/index.md`, `wiki/graph/edges.jsonl`, or `wiki/graph/citations.jsonl` as a block replaces parallel peers' work when the worktrees merge. Use the tool commands, which append.

## Creating a new page in parallel

When two sibling `/ingest` subagents both need a new concept page with the same slug, both will try to create it and the fan-in merge will fail. Mitigations:

- the per-paper creation limit (`references/dedup-policy.md`) keeps the collision surface small
- the `/init` parent merges worktree branches sequentially; when the second worktree's ingest writes the same slug, the sequential merge resolves it as a conflict that the parent handles by picking the earlier write and re-running `find-similar-concept` on the later one at fan-in
- do not try to coordinate across worktrees during ingest — worktrees are isolated by design

If you do notice a slug collision during a direct (non-INIT) ingest — i.e. the paper page already exists with a different arXiv ID — stop and report, per `references/error-handling.md`. Do not write through.

## What `/ingest` does not do for `/init`

- It does not commit. Committing the worktree is the parent's responsibility (see `skills/init/references/parallel-ingest.md`).
- It does not stash or switch branches.
- It does not merge worktrees or run `dedup-edges`, `rebuild-index`, or `lint.py --fix`. Those are fan-in operations owned by `/init`.
