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

The `init` command already appends `init | wiki initialized` to `log.md` automatically — do not add a second log call here.

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

#### Phase D — Download selected papers (additions only)

For each paper selected in Phase B + C:

**Skip-if-exists guard (mandatory)** — before downloading, check that neither `raw/papers/<slug>/` nor `raw/papers/<slug>.pdf` already exists. If either is present, SKIP the download entirely. `/init` is forbidden from overwriting anything already under `raw/` (see the Constraints section); the user's existing materials are authoritative.

```bash
if [ -d "raw/papers/<slug>" ] || [ -f "raw/papers/<slug>.pdf" ]; then
  echo "skip: raw/papers/<slug> already exists"
else
  # Prefer tex source (arXiv e-print)
  curl -sL -o raw/papers/<slug>.tar.gz "https://arxiv.org/e-print/<arxiv_id>"
  if [ -s raw/papers/<slug>.tar.gz ]; then
    mkdir -p raw/papers/<slug> && tar -xzf raw/papers/<slug>.tar.gz -C raw/papers/<slug>/
    rm raw/papers/<slug>.tar.gz
  else
    rm -f raw/papers/<slug>.tar.gz
    # Fall back to PDF
    curl -sL -o raw/papers/<slug>.pdf "https://arxiv.org/pdf/<arxiv_id>"
    [ -s raw/papers/<slug>.pdf ] || { rm -f raw/papers/<slug>.pdf; echo "download failed: <slug>"; }
  fi
fi
```

After each download, verify the artifact is non-empty (`test -s`) and of the expected content type; if the check fails, delete the partial file and log the failure — never leave a zero-byte stub in `raw/papers/`.

#### Phase E — Compile final source list

Merge `local_papers` + downloaded papers into `raw_source_list` (in memory, no file written).

Log what was expanded:
```bash
python3 tools/research_wiki.py log wiki/ "init | source expansion: <N> local + <M> discovered via citation chains and search"
```

**Transparency**: papers downloaded in Phase D become permanent additions to the user's `raw/papers/`. Step 8's report MUST list them under a separate "papers we discovered and downloaded" section (distinct from "papers you provided") so the user can review and `git rm` any they reject.

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

### Step 4.5: Commit skeleton + stash unrelated dirty files (MANDATORY before fan-out)

Before spawning any subagent, the working tree must be in a state where (a) everything `/init` produced so far is committed, and (b) anything `/init` did NOT produce is out of the working tree entirely. This is a hard requirement for the Phase B sequential merge — git refuses to merge into a dirty working tree, and `git stash` is the only safe way to get an unrelated user edit out of the way temporarily.

#### 4.5.a — Inspect the working tree

```bash
git status --short
```

Sort what you see into two buckets:

- **Scaffold files** — anything under `wiki/` or `raw/papers/`. These were either created by Step 1 (`research_wiki.py init`) or Step 4 (Summary / topics / initial index.md), or they are user-provided source papers under `raw/papers/`. They MUST be in the scaffold commit so that worktree branches inherit them.
- **Unrelated dirty files** — anything outside `wiki/` and `raw/papers/`. Common cases: an unfinished SKILL.md edit from a previous session, in-progress changes to `tools/`, `i18n/`, `tests/`. These have nothing to do with `/init` and MUST NOT be in the scaffold commit, but they ALSO must not be left in the working tree, because Phase B merges will be blocked by them.

#### 4.5.b — Stash unrelated dirty files (if any)

If `git status --short` showed anything outside `wiki/` and `raw/papers/`, stash it before proceeding:

```bash
UNRELATED=$(git status --short | awk '{print $2}' | grep -Ev '^(wiki/|raw/papers/)' || true)

if [ -n "$UNRELATED" ]; then
  echo "Unrelated dirty files detected — stashing before /init:"
  echo "$UNRELATED"
  git stash push -u -m "init-unrelated-dirty-$(date +%Y%m%d-%H%M%S)" -- $UNRELATED
fi
```

**Record the stash ref** into the `init-session` checkpoint metadata so Step 8 can pop it back at the end, even if `/init` is interrupted and resumed later:

```bash
STASH_REF=$(git stash list | head -1 | cut -d: -f1)
python3 tools/research_wiki.py checkpoint-set-meta wiki/ init-session stash_ref "$STASH_REF"
```

This writes `{"metadata": {"stash_ref": "stash@{0}"}}` into `.checkpoints/init-session.json`; Step 8 reads it back via `checkpoint-get-meta` before clearing the checkpoint. If the stash step in 4.5.b produced no stash (nothing unrelated was dirty), skip this command — Step 8 will see an empty `stash_ref` and simply not pop.

**Why stash and not "ask the user"**: a previous version of this step asked the user instead of stashing automatically. That left dirty files in the working tree, and Phase B's first `git merge` then failed with `your local changes ... would be overwritten by merge` even when those files had nothing to do with the merge — git's safety check is conservative and refuses any merge while the work tree is dirty. Stash → init → pop is the standard workflow; the user's work is never lost.

#### 4.5.c — Commit the scaffold

After 4.5.b, the only dirty files left should be under `wiki/` and `raw/papers/`. Verify, then commit:

```bash
git status --short
git add wiki/ raw/papers/
git commit -m "init: scaffold wiki skeleton (Summary, topics, index, graph stubs)" --no-gpg-sign
```

If `git status --short` still shows files outside `wiki/` / `raw/papers/`, the stash in 4.5.b was incomplete — investigate and re-stash before committing. NEVER use `git add -A` here; it would defeat the whole point of the stash step.

After this commit, every subagent worktree will branch from a clean base where the skeleton already exists, so agents will only add new files (`wiki/papers/{slug}.md`, new concepts/claims/people) and Phase B merges will only conflict on genuine concept/claim overlaps (which Phase B handles via union).

#### 4.5.d — Verify `.gitattributes` is in place

The repo ships with a `.gitattributes` file at the project root that declares `merge=union` for `wiki/log.md`, `wiki/graph/edges.jsonl`, and `wiki/index.md`. These are append-only files that every parallel agent writes to; without `merge=union`, every Phase B merge would conflict on them. Verify the file exists and contains all three entries:

```bash
test -f .gitattributes && grep -E '^wiki/(log\.md|graph/edges\.jsonl|index\.md)' .gitattributes
```

If the file is missing or any entry is absent, **STOP** and create it before proceeding — Phase B will fail without it. The expected content is:

```
wiki/log.md             merge=union
wiki/graph/edges.jsonl  merge=union
wiki/index.md           merge=union
```

### Step 5: Ingest Papers via Parallel Subagents with Worktree Isolation

All paper ingest agents run **simultaneously** using git worktrees for filesystem isolation. Total time ≈ slowest single paper (not sum of all papers).

**Load checkpoint** (supports `--resume`):
```bash
python3 tools/research_wiki.py checkpoint-load wiki/ "init-session"
```
If a checkpoint exists, exclude already-completed papers from the parallel batch and resume with the remaining ones.

**Ordering for merge**: rank `raw_source_list` by estimated importance (citation count, venue tier). The highest-importance paper is merged first — its concept definitions become the canonical base that later merges extend.

#### 🚨 CRITICAL: Prompt Construction Rules (read before Phase A)

When constructing each subagent's prompt, **the orchestrator MUST NOT include any absolute path to the project root**. Worktree isolation works by giving the subagent its own cwd (the worktree), but if the prompt contains a line like `Working directory: /home/user/project/...`, the subagent will use that absolute path for all `Read`/`Write`/`Edit` calls and **silently bypass the worktree**, writing directly to the main repo. This was a real production bug — every parallel ingest then writes to main, Phase B has nothing to merge, and concept/claim conflicts go unresolved.

**Anti-pattern (NEVER do this)**:
```
prompt: "Execute /ingest for ...
    Working directory: /home/user/project/OmegaWiki    ← BUG: bypasses worktree
    ..."
```

**Correct pattern**:
- Use only relative paths in the prompt (e.g., `raw/papers/...`, `wiki/`, `tools/`)
- Include an explicit reminder that the agent is in an isolated worktree
- Trust that the subagent's cwd is set correctly by Claude Code's worktree mechanism

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
  prompt: "🚨 ISOLATION NOTICE: You are running in a temporary git worktree
    of the project — your cwd is YOUR OWN worktree, NOT the main repo.
    Use ONLY relative paths in every Read/Write/Edit call (e.g. wiki/papers/foo.md,
    raw/papers/<slug>/main.tex, tools/fetch_s2.py). NEVER prepend an absolute
    path like /home/... — that bypasses worktree isolation and corrupts the
    parallel merge phase. If you find yourself about to use an absolute path,
    stop and rewrite it as a path relative to your cwd.

    Execute /ingest for the paper at raw/papers/<source-relative-path>.

    INIT MODE — run ingest in fast-bootstrap mode.
    Citation discovery was already done by /init Step 2, so skip those API calls.

    1. Read .claude/skills/ingest/SKILL.md for the complete workflow
    2. Follow the workflow with these INIT MODE overrides:
         SKIP — fetch_s2.py citations <arxiv_id>            (citation-chain expansion done in /init Step 2)
         SKIP — fetch_s2.py references <arxiv_id>           (same reason)
         SKIP — fetch_deepxiv.py head <arxiv_id>            (section structure not needed for batch bootstrap)
         SKIP — updating wiki/index.md                       (orchestrator runs rebuild-index after merge)
         SKIP — updating wiki/topics/*.md                    (orchestrator runs `topic-backfill` + `lint --fix` after merge to repair all xrefs)
         SKIP — research_wiki.py rebuild-context-brief       (graph/ files are derived; orchestrator rebuilds ONCE after all merges. Parallel rebuilds in worktrees create guaranteed merge conflicts on context_brief.md / open_questions.md.)
         SKIP — research_wiki.py rebuild-open-questions      (same reason — never touch wiki/graph/*.md inside a subagent)
         DO   — read .tex/.pdf source thoroughly
         DO   — fetch_s2.py paper <arxiv_id>                 (metadata: venue, year, citation count, s2_id)
         DO   — fetch_deepxiv.py brief <arxiv_id>            (fast TLDR for key idea draft)
         DO   — create paper page, claims/concepts within hard limits, key people (importance >= 4)
         DO   — call find-similar-concept and find-similar-claim for every candidate (mandatory dedup — see /ingest Step 4 / Step 5 Part A; scans both concepts/ and foundations/)
         DO   — add all graph edges via add-edge, append to log.md
    3. Wiki root: wiki/   Tools dir: tools/   (both relative to your cwd)
    4. Activate venv first: source .venv/bin/activate
    5. Topics already created (do not recreate): <comma-separated topic slugs>
    6. **MANDATORY FINAL STEP — commit your work to the worktree branch before reporting back**:
       ```bash
       git add wiki/
       git status --short
       git commit -m \"ingest: <paper-slug>\" --no-gpg-sign
       ```
       Without this commit, the orchestrator's Phase B merge has nothing to merge — your
       entire ingest result will be lost. If `git status --short` shows nothing under wiki/,
       something is wrong (you may have written to absolute paths bypassing the worktree);
       report this in your final message instead of committing an empty result.
    7. After committing, report back:
       - Pages created (papers, concepts, people, claims)
       - Graph edges added
       - Commit hash from step 6
       - Any issues encountered"
})
```

**How this achieves parallelism**: spawn each agent sequentially, but `run_in_background: true` means each agent runs immediately without waiting for the previous one to finish. All N agents run concurrently. After spawning all N, wait until you receive completion notifications for every agent before proceeding to Phase B.

#### Phase B — Fan-in: sequential merge

After all agents complete, merge their worktree branches into main **one by one**, in importance order (highest citation count first).

**Sanity check before merging**: confirm the worktree branches exist AND each one has at least one commit beyond `HEAD`:
```bash
git branch -a | grep worktree
git worktree list
# For each branch, verify it actually has an ingest commit (not empty):
for b in $(git branch --list 'worktree-agent-*' | tr -d ' *+'); do
  echo "=== $b ==="
  git log --oneline "$(git merge-base HEAD "$b")".."$b" | head -5
done
```

**Two failure modes to detect here:**

1. **No worktree branches at all**, but `wiki/` is already populated → the agents bypassed worktree isolation (likely the prompt contained an absolute path, see CRITICAL section above). STOP and investigate — do NOT proceed to the merge loop.
2. **Worktree branches exist but show 0 commits** beyond `HEAD` → the agents wrote files but never committed. The Phase B merges will appear to "succeed" but bring in nothing. STOP — re-spawn the affected agents, OR manually commit each worktree before merging: `for w in .claude/worktrees/agent-*; do (cd "$w" && git add wiki/ && git commit -m "ingest: recovered" --no-gpg-sign); done`.

Only proceed to the merge loop after both checks pass.

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
- **Prompt must contain only relative paths** — never include absolute paths to the project root in the agent prompt; absolute paths silently bypass worktree isolation and break the merge phase (see 🚨 CRITICAL section above)
- **Subagents must commit before reporting back** — every agent prompt mandates a final `git add wiki/ && git commit` step. Without it, Phase B merges produce empty results. Verify each branch has a commit during the Phase B sanity check.
- **Wait for all N completion notifications** before starting Phase B
- **Never bypass subagents** — all paper ingestion goes through subagents running the /ingest workflow
- **Enforce init-mode skips** — the SKIP list above eliminates redundant API calls. Step 7 runs `topic-backfill` (to populate topic seminal_works / SOTA tracker from merged papers) followed by `lint --fix` (to repair concept↔paper, claim↔paper, idea↔claim, experiment↔claim reverse links). Together they cover every xref a subagent skipped.

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
   # Backfill topic seminal_works / SOTA tracker from merged papers
   # (subagents skipped wiki/topics/*.md updates in INIT MODE)
   python3 tools/research_wiki.py topic-backfill wiki/
   # Rebuild graph context and open questions
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```
2. Auto-repair the deterministic xrefs the subagents skipped, then re-run lint
   for a clean health report:
   ```bash
   # --fix repairs concept↔paper, claim↔paper, idea↔claim, experiment↔claim
   # reverse links (the bidirectional rules from CLAUDE.md). Topic xrefs are
   # NOT in this set — those are handled by `topic-backfill` in step 1.
   python3 tools/lint.py --wiki-dir wiki/ --fix
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

### Step 8: Restore stash, Report to User

**Before reporting, restore the pre-init working tree state.** Read the stash ref recorded in 4.5.b back from checkpoint metadata and pop it:

```bash
STASH_REF=$(python3 tools/research_wiki.py checkpoint-get-meta wiki/ init-session stash_ref)
if [ -z "$STASH_REF" ]; then
  # Nothing was stashed in 4.5.b (working tree was clean) — just clear the checkpoint.
  python3 tools/research_wiki.py checkpoint-clear wiki/ init-session
elif git stash pop "$STASH_REF"; then
  python3 tools/research_wiki.py checkpoint-clear wiki/ init-session
else
  echo "⚠ stash pop failed — checkpoint preserved at .checkpoints/init-session.json"
  echo "  Run 'git stash list' and resolve manually, then:"
  echo "    python3 tools/research_wiki.py checkpoint-clear wiki/ init-session"
fi
```

`checkpoint-get-meta` with a key prints the raw value (empty string if absent), so `[ -z "$STASH_REF" ]` cleanly distinguishes "nothing to pop" from "pop succeeded" from "pop failed". Only clear the checkpoint after a successful pop — a failed pop MUST leave the checkpoint (and its `stash_ref` metadata) intact so the user can recover manually. Do not collapse this into `pop || echo`: `echo` always exits 0, which would swallow the pop failure and run `checkpoint-clear` unconditionally, losing the stash ref.

Then output a summary including:
- Page creation counts (broken down by all 8 entity types)
- Domain overview (topics and Summary digest)
- Overview of extracted claims
- Number of graph edges
- Issues found by lint (if any)
- Initial ideas generated (if any)
- **Papers we discovered and downloaded** in Step 2 Phase D (listed separately from papers the user provided, so the user can `git rm` any they reject)
- Whether the pre-init stash was popped cleanly (and how to recover if not)
- Suggested next steps:
  - Manually `/ingest` more papers
  - Read `wiki/Summary/` for the domain landscape
  - Run `/lint` for a detailed health report
  - Run `/ideate` to generate more research ideas

## Constraints

- **raw/ is append-only for `/init`, read-only for everything else**: Step 2 Phase D is the one sanctioned place where `raw/papers/` receives new files (discovered via citation-chain / keyword search). Only additions are allowed — never overwrite or delete an existing `raw/papers/*` entry. All `/ingest` subagents spawned in Step 5 treat `raw/` as strictly read-only (they consume `raw/papers/<slug>/` but never write back)
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
- **Interrupted mid-run**: next time `/init` runs, it automatically detects the checkpoint and resumes from where it left off (skipping already-completed papers). The `stash_ref` recorded in 4.5.b persists across restarts via checkpoint metadata, so Step 8 of the resumed run will still pop it — do NOT pop the stash at the start of a resumed run, only at Step 8 as usual.
- **wiki/ already has content**: detect existing pages, skip entities that already exist, only supplement new content (idempotent)
- **Topic generation uncertain**: prefer fewer and more precise; 2–3 high-quality topics beats 5 vague ones
- **Worktree isolation appears to have failed** (no worktree branches after Phase A, but `wiki/` is already populated): the subagent prompts likely contained absolute paths. Stop, audit the prompts, fix the orchestrator behavior, and re-run from a clean checkpoint. Do NOT proceed to Phase C without Phase B merge — the wiki will end up with many duplicate concepts and claims.
- **Worktree branches exist but contain no commits** (Phase B sanity check shows 0 commits beyond merge-base): the subagents skipped the mandatory final commit step. Either re-spawn the affected agents (cheap if they support resume) or recover by manually committing each worktree before merging: `for w in .claude/worktrees/agent-*; do (cd "$w" && git add wiki/ && git commit -m "ingest: recovered" --no-gpg-sign); done`. Then proceed with Phase B as normal.

## Dependencies

### Tools (via Bash)
- `python3 tools/research_wiki.py init wiki/` — initialize directory structure
- `python3 tools/research_wiki.py slug "<title>"` — slug generation
- `python3 tools/research_wiki.py add-edge wiki/ ...` — add graph edge
- `python3 tools/research_wiki.py dedup-edges wiki/` — remove duplicate edges after parallel ingest merge (Step 5, Phase C)
- `python3 tools/research_wiki.py rebuild-index wiki/` — regenerate index.md from entity frontmatter (Step 7, after all subagents complete)
- `python3 tools/research_wiki.py topic-backfill wiki/` — append matching papers to topic seminal_works / SOTA tracker (Step 7, repairs the wiki/topics/*.md updates that subagents skipped in INIT MODE)
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild compressed context
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — rebuild knowledge gap map
- `python3 tools/research_wiki.py stats wiki/` — wiki statistics
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log
- `python3 tools/research_wiki.py checkpoint-save/load/clear wiki/ init-session ...` — resume support for Step 5 parallel ingest
- `python3 tools/research_wiki.py checkpoint-set-meta wiki/ init-session <key> <value>` — persist cross-step state (e.g. the Step 4.5.b stash ref) in checkpoint metadata
- `python3 tools/research_wiki.py checkpoint-get-meta wiki/ init-session [<key>]` — read a metadata value (raw) or the whole metadata dict (JSON) in Step 8
- `python3 tools/fetch_s2.py search "<topic>" 20` — Semantic Scholar keyword search
- `python3 tools/fetch_s2.py references <arxiv_id>` — citation-chain expansion (references)
- `python3 tools/fetch_s2.py citations <arxiv_id>` — citation-chain expansion (citations)
- `python3 tools/fetch_deepxiv.py search "<topic>" --mode hybrid --limit 10` — DeepXiv semantic search (optional)
- `python3 tools/lint.py --wiki-dir wiki/ --fix` — structural check + auto-repair (Step 7, repairs concept↔paper, claim↔paper, idea↔claim, experiment↔claim reverse links that subagents skipped)
- `curl` — download arXiv e-print (tex) or PDF to raw/papers/

### Skills (via Agent subagent)
- `/ingest` — each paper ingested by an independent Agent subagent (Step 5)

### External APIs
- arXiv (e-print download via curl)
- Semantic Scholar API (via tools/fetch_s2.py — search, references, citations)
- DeepXiv API (via tools/fetch_deepxiv.py, optional; graceful fallback when unavailable)
