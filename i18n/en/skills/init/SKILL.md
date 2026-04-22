---
description: Bootstrap ΩmegaWiki from user sources plus optional discovery, then ingest the final paper set in parallel
argument-hint: "[topic] [--no-introduction]"
---

# /init

> Build a wiki from `raw/` with a deterministic discovery plan, an LLM trim step, provisional pages from `raw/notes/` and `raw/web/`, and parallel `/ingest` fan-out/fan-in.

## Inputs

- `topic` (optional): research direction keywords; omit it when `raw/papers/` already defines the seed set or when notes/web already capture the intent
- `--no-introduction` (optional): disable external paper discovery; use only user-owned `raw/papers/`, `raw/notes/`, and `raw/web/`
- parameter guardrail: treat `topic` and `--no-introduction` as user inputs, not agent strategy knobs; do not infer `--no-introduction` from repository state alone. A non-empty `raw/papers/`, empty `raw/notes/` or `raw/web/`, or an omitted `topic` is not by itself a reason to enable local-only mode. Use `--no-introduction` only when the user explicitly asked to disable external discovery.
- `raw/papers/`: user-owned paper sources (`.tex`, `.pdf`, archives)
- `raw/notes/`: user-owned notes that express goals, hypotheses, exclusions, and preferred sub-directions
- `raw/web/`: user-owned saved web pages that express goals, hypotheses, exclusions, and preferred sub-directions

## Outputs

- `wiki/` scaffold via `tools/research_wiki.py init`
- `raw/tmp/` — `/init`-generated prepared local sources
- `raw/discovered/` — newly downloaded papers selected by `/init` (only when discovery is enabled)
- `wiki/Summary/{area}.md`, `wiki/topics/{topic}.md`, provisional `wiki/ideas/{slug}.md`, `wiki/concepts/{slug}.md`, `wiki/claims/{slug}.md`
- `wiki/papers/*.md` plus paper-derived concepts/claims/people via parallel `/ingest`
- updated `wiki/index.md`, `wiki/log.md`, `wiki/graph/edges.jsonl`, `wiki/graph/context_brief.md`, `wiki/graph/open_questions.md`
- `.checkpoints/init-prepare.json`, `.checkpoints/init-plan.json`, `.checkpoints/init-sources.json`

## Wiki Interaction

### Reads

- `raw/papers/`, `raw/notes/`, `raw/web/`
- `.checkpoints/init-prepare.json` and `.checkpoints/init-sources.json` for resume / fan-out
- `wiki/index.md` plus existing `wiki/topics/`, `wiki/ideas/`, `wiki/concepts/`, `wiki/claims/` for resume and duplicate avoidance

### Writes

- `wiki/` scaffold and provisional pages
- `raw/tmp/` and `raw/discovered/`
- `wiki/index.md`, `wiki/log.md`, `wiki/graph/*`
- `.checkpoints/init-prepare.json`, `.checkpoints/init-plan.json`, `.checkpoints/init-sources.json`, and `init-session` checkpoint metadata

### Graph edges created

- `/init` itself creates only scaffold-level edges when provisional pages need them
- all paper-driven edges are delegated to `/ingest`

## Workflow

**Pre-condition**: working directory is the project root containing `wiki/`, `raw/`, `tools/`. Set `WIKI_ROOT=wiki/`. Resolve `PYTHON_BIN` once and reuse it for every Python command during `/init` so the workflow stays on the same interpreter that `setup.sh` populated:

```bash
if [ -x .venv/bin/python ]; then
  PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PYTHON_BIN=.venv/Scripts/python.exe
else
  PYTHON_BIN=python3
fi
export PYTHON_BIN
```

### Step 1: Initialize wiki structure

```bash
"$PYTHON_BIN" tools/research_wiki.py init wiki/
```

Create the standard wiki directories, `graph/`, `outputs/`, `index.md`, and `log.md`. Do not add a second init log entry here.

### Step 2: Prepare local inputs into `raw/tmp/`

```bash
"$PYTHON_BIN" tools/init_discovery.py prepare --raw-root raw --output-manifest .checkpoints/init-prepare.json
```

- decode local PDFs into synthetic `.tex` under `raw/tmp/` when possible
- for PDFs that lack an embedded arXiv ID, attempt title-based recovery via Semantic Scholar search; when an arXiv ID is recovered successfully, prefer the fetched raw TeX source from arXiv (`raw/tmp/papers/...-arxiv-src/`) over the synthetic `.tex`
- keep notes/web on their original source paths; `/init` reads them directly during planning
- set each local paper's `canonical_ingest_path` to a prepared `raw/tmp/` path when available; otherwise fall back to the original `raw/papers/...` path
- record warnings for failed decode / arXiv source fetch rather than aborting `/init`
- save the manifest to `.checkpoints/init-prepare.json`

### Step 3: Build the discovery plan, trim it, and write the final source manifest

```bash
"$PYTHON_BIN" tools/init_discovery.py plan [--topic "<topic>"] --mode auto --raw-root raw --wiki-root wiki --prepared-manifest .checkpoints/init-prepare.json --allow-introduction <true|false> --output-plan .checkpoints/init-plan.json
```

- `mode=seeded` when the prepare manifest contains at least one parseable local paper; otherwise `mode=bootstrap`
- `plan` must read `.checkpoints/init-prepare.json` instead of rescanning `raw/`
- `raw/notes/` and `raw/web/` signals are read directly from the original source files
- if multiple local copies of the same paper exist, prefer better local sources in this order: original local `.tex` > archive-extracted source `.tex` or fetched arXiv source directory > PDF-derived synthetic `.tex` > raw `.pdf`
- if Chinese note or web content is detected, preserve a planner warning that extraction/ranking may be less reliable and treat provisional outputs as lower-confidence
- when `topic` is omitted in seeded mode, derive discovery and ranking cues from local paper titles/abstracts plus notes/web signals instead of refusing to plan
- if seeded discovery adds no external papers, proceed with the user-owned paper set instead of treating that as a fatal planner error
- when both `topic` and notes/web keywords are absent, bootstrap discovery has no query to search with, so it must surface that as a planner error instead of issuing an empty search
- over-pick a shortlist of **10-12** candidates
- use S2 citations/references/search plus optional DeepXiv search
- when DeepXiv search is available, explicitly use returned `relevance_score` inside tool scoring rather than merely noting it in prose
- if `SEMANTIC_SCHOLAR_API_KEY` is unset, continue anyway but record the slower public-rate-limit discovery path as a planner warning
- planner output, warnings, and errors must be saved to `.checkpoints/init-plan.json`

Planner policy:

- relevance = 30
- freshness = 20
- anchor/connectivity bonus = 20
- survey/benchmark/overview bonus = 15
- citation/centrality = 15
- prefer a survey if one is available
- allow at most one older canonical anchor slot, and only in bootstrap or very roomy seeded cases
- in seeded mode with limited introduced capacity, do not reserve an older anchor up front; freshness should dominate and older external non-survey papers must not pile up via citation advantage
- otherwise freshness wins close decisions
- seeded mode computes anchor bonus from user papers first, then notes/web priorities
- bootstrap mode searches first, then expands citations/references from the strongest initial candidates

LLM trim policy:

- read `.checkpoints/init-plan.json` and explicitly trim the over-picked `shortlist` to a final **8-10** papers total before `fetch`
- do not skip the trim step even if the shortlist already looks reasonable
- keep all parseable user-owned papers by default, then use the remaining slots for introduced papers
- if the user already provided more than 10 parseable papers, add no new papers
- prefer one survey/overview when available, at most one older canonical anchor when it is actually useful, and fresh representatives across distinct clusters
- when the user already supplied a substantial seed set, freshness should dominate and older canonical papers should be further deprioritized
- "`at most one` older canonical anchor" is a ceiling, not a requirement
- before `fetch`, emit an explicit final selection artifact in the workflow/response that includes: `shortlist_count`, `final_count`, and the exact final `candidate_id` list in shortlist order
- if `final_count` is outside **8-10**, stop and revise the final selection before `fetch`, unless `--no-introduction` is active or the user already supplied more than 10 parseable papers
- call `fetch` only with the exact final selected `candidate_id`s; never forward the whole shortlist implicitly or pass all shortlist IDs by default

If `--no-introduction` is present:

- only use this branch when the user explicitly requested local-only behavior
- final paper set = all parseable user papers from `.checkpoints/init-prepare.json`
- still run `fetch` with zero external IDs so it writes `.checkpoints/init-sources.json`

Otherwise run:

```bash
"$PYTHON_BIN" tools/init_discovery.py fetch --raw-root raw --plan-json .checkpoints/init-plan.json --prepared-manifest .checkpoints/init-prepare.json --output-sources .checkpoints/init-sources.json --id <candidate-id> --id <candidate-id>
```

- external papers downloaded by `/init` go to `raw/discovered/`, never `raw/papers/`
- never fetch a paper that is already represented by a prepared local source from `raw/tmp/`
- `.checkpoints/init-sources.json` is the single source of truth for Step 5 ingest order
- user-owned papers appear in `init-sources.json` with `origin=user_local` and their canonical prepared path when available
- introduced papers appear in `init-sources.json` with `origin=introduced` and their canonical `raw/discovered/` path

### Step 4: Create scaffold pages before paper ingest

Create one `wiki/Summary/{area}.md`, the needed `wiki/topics/{slug}.md`, and provisional `ideas/`, `concepts/`, and `claims/` from notes/web when warranted.

Rules:

- notes/web are authoritative for user intent, not for literature confidence
- every notes/web-derived page must include this exact line immediately after frontmatter:

```markdown
Provisional note: seeded from raw/notes or raw/web during /init; pending validation from ingested papers.
```

- `topics/`: create when a direction is explicit or repeated
- `ideas/`: create when the user states or strongly implies a research direction or hypothesis
- `concepts/`: create only when the mechanism recurs across notes/web, or appears once in notes/web and once in the final paper set
- `claims/`: create only from explicit assertive statements, never by inference

For notes/web-derived claims, use:

```yaml
status: proposed
confidence: 0.2
source_papers: []
evidence: []
```

Do not create `people/` pages or `foundations/` pages from `/init`. Update `wiki/index.md` for scaffold pages created directly in this step.

### Step 4.5: Commit scaffold, stash unrelated dirty files, verify merge safety

Before spawning subagents:

- run `git status --short`
- treat files under `wiki/`, `raw/papers/`, `raw/tmp/`, `raw/discovered/`, and `.checkpoints/init-*.json` as scaffold files
- stash unrelated dirty files outside those paths:

```bash
UNRELATED=$(git status --short | awk '{print $2}' | grep -Ev '^(wiki/|raw/papers/|raw/tmp/|raw/discovered/|\.checkpoints/init-)' || true)
if [ -n "$UNRELATED" ]; then
  git stash push -u -m "init-unrelated-dirty-$(date +%Y%m%d-%H%M%S)" -- $UNRELATED
fi
```

- save the stash ref:

```bash
STASH_REF=$(git stash list | head -1 | cut -d: -f1)
"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session stash_ref "$STASH_REF"
```

- capture the current branch before worktree fan-out; `/init` worktree mode must run from a named branch, not detached HEAD:

```bash
BASE_BRANCH=$(git branch --show-current)
if [ -z "$BASE_BRANCH" ]; then
  echo "/init worktree mode requires a named branch; switch to or create one before continuing." >&2
  exit 1
fi
"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session base_branch "$BASE_BRANCH"
```

- save final selected paper IDs (post-trim, not the over-picked shortlist) and planner mode into checkpoint metadata
- verify `.gitattributes` contains `merge=union` for `wiki/log.md`, `wiki/graph/edges.jsonl`, and `wiki/index.md`
- commit the scaffold:

```bash
git add wiki/ raw/papers/ raw/tmp/ raw/discovered/ .checkpoints/init-prepare.json .checkpoints/init-plan.json .checkpoints/init-sources.json
git commit -m "init: scaffold before parallel ingest" --no-gpg-sign
BASE_COMMIT=$(git rev-parse HEAD)
"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session base_commit "$BASE_COMMIT"
```

### Step 5: Parallel paper ingest with worktree isolation

Paper sources for this step come strictly from `.checkpoints/init-sources.json`:

- `origin=user_local`: canonical prepared `.tex` under `raw/tmp/` when available, otherwise fallback `raw/papers/...`
- `origin=introduced`: fetched dirs or PDFs under `raw/discovered/`

Order papers by `shortlist_rank` from `init-sources.json`, not by rescanning raw folders or by raw citation count.

Spawn one Agent subagent per paper with:

- `run_in_background: true`
- worktree isolation
- a fresh temp branch created from `BASE_COMMIT`, never the already-checked-out `BASE_BRANCH`
- a prompt that uses **relative paths only**
- explicit INIT MODE skips

For each paper, create the worktree from the scaffold commit on the current branch:

```bash
WT_BRANCH="init-${BASE_BRANCH//\//-}-<rank>-<paper-slug>"
WT_PATH="../.worktrees/$WT_BRANCH"
git worktree add -b "$WT_BRANCH" "$WT_PATH" "$BASE_COMMIT"
```

Do not run `git worktree add` against the current branch name itself; Git will refuse because that branch is already checked out in the main workspace.

Subagent prompt requirements:

- execute `/ingest` for exactly one relative source path
- do not bypass `/ingest`
- in INIT MODE, consume the handed-off canonical path exactly as provided
- skip `fetch_s2.py citations`
- skip `fetch_s2.py references`
- skip per-subagent `rebuild-index`
- skip per-subagent `rebuild-context-brief`
- skip per-subagent `rebuild-open-questions`
- skip conflict-prone topic writes
- still run `find-similar-claim` and `find-similar-concept`
- commit the result inside the worktree before exiting

After all agents complete:

1. switch the main workspace back to `BASE_BRANCH` if needed, then merge worktree branches sequentially there in planner order
2. resolve true concept/claim conflicts conservatively — merge, do not multiply near-duplicates
3. run:

```bash
git switch "$BASE_BRANCH"
git merge --no-ff "$WT_BRANCH" --no-edit
git worktree remove "$WT_PATH"
git branch -d "$WT_BRANCH"
"$PYTHON_BIN" tools/research_wiki.py dedup-edges wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/
"$PYTHON_BIN" tools/lint.py wiki/ --fix
```

### Step 6: Final report and cleanup

Report separately:

- user-provided papers ingested through prepared `raw/tmp/` paths
- user-provided papers that fell back to original `raw/papers/` paths
- discovered papers from `raw/discovered/`
- provisional pages seeded from notes/web
- pages created by `/ingest`
- pages updated by `/ingest`
- any skipped or failed papers

If `stash_ref` exists, pop it at the end. If stash pop fails, keep the checkpoint and report the failure.

Also note explicitly:

- `/prefill` was not used by `/init`
- no foundations were auto-created
- current people-page and claim-volume tightening remains a follow-up task for `/ingest`

## Constraints

- `raw/papers/`, `raw/notes/`, and `raw/web/` are user-owned inputs
- `raw/tmp/` and `raw/discovered/` are `/init`-generated handoff areas
- `/init` may write external papers only to `raw/discovered/`, and generated prepared local sources only to `raw/tmp/`
- `/prefill` is optional background seeding, not part of `/init`
- no skill other than `/prefill` may auto-create foundations
- `/init` must not create `people/` pages directly
- notes/web-derived pages are provisional and must carry the exact notice line above
- no new frontmatter fields are introduced for provisional status
- paper evidence outranks notes/web for claim confidence and concept consolidation
- all paper ingest must run through parallel `/ingest` subagents with worktree isolation
- Step 5 must read paper inputs from `.checkpoints/init-sources.json`, not by ad hoc folder scanning
- subagent prompts must use relative paths only

## Error Handling

- **No parseable paper in `raw/papers/`**: enter bootstrap mode
- **`raw/notes/` and `raw/web/` empty**: skip provisional seeding, continue
- **PDF decode fails during prepare**: keep the local source, record the warning in `.checkpoints/init-prepare.json`, and fall back to the original path if needed
- **Chinese content is detected in `raw/notes/` or `raw/web/`**: keep going, but preserve a planner warning that note/web extraction and ranking may be less reliable and treat rankings plus provisional pages as lower-confidence
- **S2 or DeepXiv unavailable**: planner falls back to the remaining sources; preserve the warning in the checkpointed plan and note degraded discovery in the report
- **arXiv ID recovery or TeX source fetch failure for a local PDF**: record a warning in `.checkpoints/init-prepare.json`, fall back to synthetic `.tex` or the original PDF path, and continue
- **External fetch fails for one paper**: keep the remaining final set and report the failed download
- **Single paper ingest fails**: record it via checkpoint, skip it, continue the rest, and list it in the report
- **Current checkout is detached HEAD**: stop before worktree fan-out and ask the user to switch to or create a named branch first
- **Worktree branch has no commit**: stop and recover that worktree before merge
- **stash pop fails**: keep checkpoint metadata and report the manual recovery step

## Dependencies

### Tools (via Bash)

- `"$PYTHON_BIN" tools/research_wiki.py init wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session <key> <value>`
- `"$PYTHON_BIN" tools/research_wiki.py checkpoint-save/load/clear wiki/ init-session ...`
- `"$PYTHON_BIN" tools/research_wiki.py dedup-edges wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py log wiki/ "<message>"`
- `"$PYTHON_BIN" tools/init_discovery.py prepare --raw-root raw --output-manifest .checkpoints/init-prepare.json`
- `"$PYTHON_BIN" tools/init_discovery.py plan [--topic "<topic>"] --mode auto --raw-root raw --wiki-root wiki --prepared-manifest .checkpoints/init-prepare.json --allow-introduction <true|false> --output-plan .checkpoints/init-plan.json`
- `"$PYTHON_BIN" tools/init_discovery.py fetch --raw-root raw --plan-json .checkpoints/init-plan.json --prepared-manifest .checkpoints/init-prepare.json --output-sources .checkpoints/init-sources.json --id <candidate-id>`
- `"$PYTHON_BIN" tools/lint.py wiki/ --fix`

### Skills

- `/ingest` — one paper per subagent, INIT MODE

### External APIs used by `init_discovery.py`

- Semantic Scholar
- DeepXiv (optional)
- arXiv download endpoints
