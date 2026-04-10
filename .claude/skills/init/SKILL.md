---
description: Bootstrap a complete ΩmegaWiki from the raw/ directory, including papers, concepts, topics, and people pages, and initialize ideas/experiments/claims and the graph
argument-hint: "[topic]"
---

# /init

> Bootstrap a ΩmegaWiki from scratch. Scans the raw/ directory and external sources, creates a complete wiki skeleton
> with all 8 entity directories and graph initialization. Each paper is ingested one by one via `/ingest`,
> ensuring cross-references and graph edges are complete from day one.

## Inputs

- `topic`: research direction keywords (e.g. "efficient fine-tuning for LLMs")
- `.tex` / `.pdf` files in `raw/papers/`
- Optional: notes and web pages in `raw/notes/`, `raw/web/`

## Outputs

- Complete wiki skeleton: all 8 entity directories + `graph/` + `outputs/`
- `wiki/papers/*.md` — structured summary for each paper (created via /ingest)
- `wiki/concepts/*.md` — core technical concept pages (created via /ingest)
- `wiki/topics/*.md` — research direction maps
- `wiki/people/*.md` — key researcher pages (created via /ingest)
- `wiki/claims/*.md` — core claims (extracted via /ingest)
- `wiki/ideas/*.md` — initial research ideas (generated from gap_map if available)
- `wiki/Summary/{area}.md` — domain-wide landscape survey
- `wiki/index.md`, `wiki/log.md`
- `wiki/graph/edges.jsonl`, `context_brief.md`, `open_questions.md`

## Wiki Interaction

### Reads
- `raw/papers/` — source papers to ingest
- `raw/notes/` — user research notes
- `raw/web/` — saved web pages
- `wiki/index.md` — check for existing pages to avoid duplication (during Step 4 batch ingest)

### Writes
- `wiki/` full directory structure (via `tools/research_wiki.py init`)
- `wiki/CLAUDE.md` — runtime schema (copied from template)
- `wiki/index.md` — content catalog
- `wiki/log.md` — chronological log
- `wiki/Summary/{area}.md` — domain survey
- `wiki/topics/{topic}.md` — research direction page
- `wiki/ideas/{idea}.md` — initial research ideas (if gap_map has content)
- All other entities are written by `/ingest` (papers, concepts, people, claims)

### Graph edges created
- All edges created in bulk via `/ingest`
- `concept → topic`: `supports` (manually created topic-concept associations)

## Workflow

**Pre-conditions**: confirm the working directory is the wiki project root (directory containing `wiki/`, `raw/`, `tools/`).
Set `WIKI_ROOT=wiki/`.

### Step 1: Initialize Wiki Directory Structure

Run the init command to create all 8 entity directories + graph/ + outputs/ + seed files:

```bash
python3 tools/research_wiki.py init wiki/
```

This creates:
- `wiki/papers/`, `wiki/concepts/`, `wiki/topics/`, `wiki/people/`
- `wiki/ideas/`, `wiki/experiments/`, `wiki/claims/`
- `wiki/Summary/`, `wiki/outputs/`
- `wiki/graph/` (with empty `edges.jsonl`)
- `wiki/index.md`, `wiki/log.md`

If `wiki/CLAUDE.md` does not exist, copy from the product template.

Append log:
```bash
python3 tools/research_wiki.py log wiki/ "init | initialized wiki directory structure"
```

### Step 2: Collect Raw Sources + Smart Expansion

This step scans what the user provided, then **selectively expands** via citation chains and keyword search. The goal is to add enough papers to make the wiki useful without making init unreasonably slow.

**Budget**: add at most **5–8 papers** beyond what the user provided. Prefer quality over quantity.

#### Phase A — Scan local sources

1. Scan `raw/papers/` and identify all files:
   - Archives (`.tar.gz` / `.zip`): extract to `raw/papers/{slug}/`
   - `.tex` present: prefer it (tex > PDF)
   - PDF only: extract text with PyMuPDF
2. Scan `raw/notes/`, `raw/web/` for user notes and web pages
3. Record as `local_papers` list (title, arxiv_id if known, path)

#### Phase B — Citation-chain expansion (primary discovery method)

For each paper in `local_papers` that has an arXiv ID (pick the 3–5 highest-importance ones):

```bash
python3 tools/fetch_s2.py references <arxiv_id>
python3 tools/fetch_s2.py citations <arxiv_id>
```

From the combined results:
1. Filter out papers already in `local_papers` (by arxiv_id or title match)
2. Rank by: `citation_count × relevance_to_topic` (relevance judged by title/abstract overlap with `<topic>`)
3. Select the **top 3–5** that are clearly central to the field but missing from the user's collection
4. These are typically seminal works the user assumed, or important follow-ups they missed

#### Phase C — Keyword search supplement (fill coverage gaps)

Only if Phase B yields fewer than 3 papers, or if there's an obvious sub-direction not covered:

```bash
python3 tools/fetch_s2.py search "<topic>" 20
```

Optionally (if DeepXiv is available):
```bash
python3 tools/fetch_deepxiv.py search "<topic>" --mode hybrid --limit 10
```

From the combined results:
1. Deduplicate against `local_papers` + Phase B selections
2. Select **1–3 papers** that cover a gap (e.g., a different approach, a survey, or a very recent paper)
3. **Skip if all top results overlap** with what we already have — do not add marginal papers

**If DeepXiv is unavailable**: rely on S2 search only.

#### Phase D — Download selected papers

For each paper selected in Phase B + C:

```bash
# Prefer tex source (arXiv e-print)
curl -sL -o raw/papers/<slug>.tar.gz "https://arxiv.org/e-print/<arxiv_id>"
mkdir -p raw/papers/<slug> && tar -xzf raw/papers/<slug>.tar.gz -C raw/papers/<slug>/
rm raw/papers/<slug>.tar.gz

# If e-print fails or no arXiv ID, fall back to PDF
curl -sL -o raw/papers/<slug>.pdf "https://arxiv.org/pdf/<arxiv_id>"
```

After download, verify the file is valid (not empty, correct content type).

#### Phase E — Compile final source list

Merge `local_papers` + downloaded papers into `raw_source_list` (in memory, no file written).

Log what was expanded:
```bash
python3 tools/research_wiki.py log wiki/ "init | source expansion: <N> local + <M> discovered via citation chains and search"
```

**Transparency**: when reporting to the user (Step 8), clearly separate "papers you provided" from "papers we discovered" so the user can verify relevance.

### Step 3: Domain Analysis

1. LLM reads `raw_source_list` and extracts core themes
2. Identifies 3–8 sub-directions (concepts) → to be created in /ingest
3. Identifies 2–5 core research directions (topics)
4. Identifies key researchers (people) → to be created in /ingest
5. Extracts domain landscape information for the Summary page

### Step 4: Create Skeleton Pages

Create the following pages per the CLAUDE.md templates (the parts not handled by /ingest):

**4a — Summary page:**
- Create `wiki/Summary/{area}.md` based on domain analysis
- Fill in frontmatter and body sections per the CLAUDE.md Summary template

**4b — Topics pages:**
- Create `wiki/topics/{topic}.md` based on domain analysis
- Fill in per the CLAUDE.md topics template, including initial open_problems and research_gaps content
- seminal_works and key_people will be populated incrementally during Step 5 /ingest

**4c — Update index.md:**
- Write Summary and topics page entries into the corresponding sections of index.md

### Step 5: Ingest Papers via Parallel Subagents with Worktree Isolation

All paper ingest agents run **simultaneously** using git worktrees for filesystem isolation. Total time ≈ slowest single paper (not sum of all papers).

**Load checkpoint** (supports `--resume`):
```bash
python3 tools/research_wiki.py checkpoint-load wiki/ "init-session"
```
If a checkpoint exists, exclude already-completed papers from the parallel batch and resume with the remaining ones.

**Ordering for merge**: rank `raw_source_list` by estimated importance (citation count, venue tier). The highest-importance paper is merged first — its concept definitions become the canonical base that later merges extend.

#### Phase A — Fan-out: background agents

Read current wiki state once before spawning (topics already created):
```bash
python3 tools/research_wiki.py find wiki/ --entity topic --field title
```

For each paper in `raw_source_list`, spawn a **background** agent with worktree isolation:

```
Agent({
  description: "ingest <paper-short-name>",
  isolation: "worktree",
  run_in_background: true,
  prompt: "Execute /ingest for the paper at <path-to-source>.

    INIT MODE — run ingest in fast-bootstrap mode.
    Citation discovery was already done by /init Step 2, so skip those API calls.

    1. Read .claude/skills/ingest/SKILL.md for the complete workflow
    2. Follow the workflow with these INIT MODE overrides:
         SKIP — fetch_s2.py citations <arxiv_id>   (citation-chain expansion done in /init Step 2)
         SKIP — fetch_s2.py references <arxiv_id>  (same reason)
         SKIP — fetch_deepxiv.py head <arxiv_id>   (section structure not needed for batch bootstrap)
         SKIP — updating wiki/index.md              (orchestrator runs rebuild-index at end of Step 7)
         SKIP — updating wiki/topics/*.md           (orchestrator runs lint --fix after merge to repair all xrefs)
         DO   — read .tex/.pdf source thoroughly
         DO   — fetch_s2.py paper <arxiv_id>        (metadata: venue, year, citation count, s2_id)
         DO   — fetch_deepxiv.py brief <arxiv_id>   (fast TLDR for key idea draft)
         DO   — create paper page, up to 3 claims, up to 3 concepts, key people (importance >= 4)
         DO   — add all graph edges, append to log.md
    3. Wiki root: wiki/   Tools: tools/
    4. Activate venv first: source .venv/bin/activate
    5. Topics already created (do not recreate): <comma-separated topic slugs>
    6. After completion, report back:
       - Pages created (papers, concepts, people, claims)
       - Graph edges added
       - Any issues encountered"
})
```

**How this achieves parallelism**: spawn each agent sequentially, but `run_in_background: true` means each agent runs immediately without waiting for the previous one to finish. All N agents run concurrently. After spawning all N, wait until you receive completion notifications for every agent before proceeding to Phase B.

#### Phase B — Fan-in: sequential merge

After all agents complete, merge their worktree branches into main **one by one**, in importance order (highest citation count first).

For each completed agent branch:
```bash
git merge --no-ff <worktree-branch> --no-edit 2>&1
```

**When git reports merge conflicts** (expected for concept/claim files referenced by multiple papers):
- **concept files**: union `key_papers`, `aliases`, `related_concepts`; take the more complete `## Definition` and `## Intuition` body sections
- **claim files**: union `evidence` list; average `confidence`; union `source_papers`
- After resolving each file: `git add <file> && git merge --continue`

Record checkpoint after each successfully merged paper:
```bash
python3 tools/research_wiki.py checkpoint-save wiki/ "init-session" "<paper-slug>"
```

If a merge fails irrecoverably, abort and skip that branch:
```bash
git merge --abort
python3 tools/research_wiki.py checkpoint-save wiki/ "init-session" "<paper-slug>" --failed
```

#### Phase C — Post-merge cleanup

After all branches are merged:
```bash
# Remove duplicate edges introduced by parallel agents writing the same edge
python3 tools/research_wiki.py dedup-edges wiki/
```

**Clear checkpoint after all done**:
```bash
python3 tools/research_wiki.py checkpoint-clear wiki/ "init-session"
```

**IMPORTANT constraints**:
- **`run_in_background: true` on every agent** — required for parallel execution; agents may be spawned one by one but must all run concurrently
- **Each agent uses `isolation: "worktree"`** — required to prevent filesystem conflicts during parallel execution
- **Wait for all N completion notifications** before starting Phase B
- **Never bypass subagents** — all paper ingestion goes through subagents running the /ingest workflow
- **Enforce init-mode skips** — the SKIP list above eliminates redundant API calls; `lint --fix` in Step 7 repairs all skipped xrefs

### Step 6: Generate Initial Ideas (optional)

After all papers are ingested:

1. Read gap_map:
   ```bash
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```
2. If `wiki/graph/open_questions.md` contains clear knowledge gaps, create `wiki/ideas/{idea}.md` for the 1–3 most prominent gaps:
   - status: proposed
   - origin: automatically extracted from gap_map
   - origin_gaps: associated claim/topic slugs
3. Update the ideas section of index.md
4. Add graph edges:
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from ideas/<idea-slug> --to claims/<claim-slug> --type addresses_gap
   ```

### Step 7: Final Graph Rebuild and Validation

1. Rebuild all derived files:
   ```bash
   # Rebuild index.md from entity frontmatter (subagents skipped this step)
   python3 tools/research_wiki.py rebuild-index wiki/
   # Rebuild graph context and open questions
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```
2. Run lint for a basic health check:
   ```bash
   python3 tools/lint.py --wiki-dir wiki/
   ```
3. Get statistics:
   ```bash
   python3 tools/research_wiki.py stats wiki/
   ```
4. Append completion log:
   ```bash
   python3 tools/research_wiki.py log wiki/ "init | completed: N papers, M concepts, K claims, L topics"
   ```

### Step 8: Report to User

Output a summary including:
- Page creation counts (broken down by all 8 entity types)
- Domain overview (topics and Summary digest)
- Overview of extracted claims
- Number of graph edges
- Issues found by lint (if any)
- Initial ideas generated (if any)
- Suggested next steps:
  - Manually `/ingest` more papers
  - Read `wiki/Summary/` for the domain landscape
  - Run `/lint` for a detailed health report
  - Run `/ideate` to generate more research ideas

## Constraints

- **raw/ is read-only**: do not modify files under `raw/`
- **graph/ maintained via tools only**: do not manually edit files under `graph/`; use `tools/research_wiki.py` exclusively
- **Bidirectional links**: when writing a forward link, simultaneously write the reverse link (follow the Cross Reference rules in CLAUDE.md)
- **tex preferred**: .tex > .pdf > vision API fallback
- **Slugs generated via tool**: always use `python3 tools/research_wiki.py slug` to generate slugs
- **Page templates follow CLAUDE.md**: all pages are created strictly following the templates in the product CLAUDE.md
- **importance scoring**: 1=niche, 2=useful, 3=field-standard, 4=influential, 5=seminal
- **Ideas start as proposed**: init only creates ideas with status=proposed
- **Do not create empty experiments**: experiments are created by /exp-design, not by init

## Error Handling

- **raw/ is empty**: fetch papers via arXiv/S2 search only; note in report
- **arXiv/S2/DeepXiv search fails**: skip the failing external source, use the remaining available sources + files already in raw/
- **Single paper ingest fails**: record to checkpoint (`--failed`), skip that paper and continue; list failures in the final report
- **Interrupted mid-run**: next time `/init` runs, it automatically detects the checkpoint and resumes from where it left off (skipping already-completed papers)
- **wiki/ already has content**: detect existing pages, skip entities that already exist, only supplement new content (idempotent)
- **Topic generation uncertain**: prefer fewer and more precise; 2–3 high-quality topics beats 5 vague ones

## Dependencies

### Tools (via Bash)
- `python3 tools/research_wiki.py init wiki/` — initialize directory structure
- `python3 tools/research_wiki.py slug "<title>"` — slug generation
- `python3 tools/research_wiki.py add-edge wiki/ ...` — add graph edge
- `python3 tools/research_wiki.py dedup-edges wiki/` — remove duplicate edges after parallel ingest merge (Step 5, Phase C)
- `python3 tools/research_wiki.py rebuild-index wiki/` — regenerate index.md from entity frontmatter (Step 7, after all subagents complete)
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild compressed context
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — rebuild knowledge gap map
- `python3 tools/research_wiki.py stats wiki/` — wiki statistics
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log
- `python3 tools/fetch_s2.py search "<topic>" 20` — Semantic Scholar keyword search
- `python3 tools/fetch_s2.py references <arxiv_id>` — citation-chain expansion (references)
- `python3 tools/fetch_s2.py citations <arxiv_id>` — citation-chain expansion (citations)
- `python3 tools/fetch_deepxiv.py search "<topic>" --mode hybrid --limit 10` — DeepXiv semantic search (optional)
- `python3 tools/lint.py --wiki-dir wiki/` — structural check
- `curl` — download arXiv e-print (tex) or PDF to raw/papers/

### Skills (via Agent subagent)
- `/ingest` — each paper ingested by an independent Agent subagent (Step 5)

### External APIs
- arXiv (e-print download via curl)
- Semantic Scholar API (via tools/fetch_s2.py — search, references, citations)
- DeepXiv API (via tools/fetch_deepxiv.py, optional; graceful fallback when unavailable)
