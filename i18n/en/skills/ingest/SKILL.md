---
description: Ingest a paper into the wiki — creates pages (papers + concepts + people + claims) and builds all cross-references and graph edges
argument-hint: <local-path-or-arXiv-URL>
---

# /ingest

> Fully absorb a paper into the wiki: create the paper page, extract/create concepts, people, and claims,
> establish all bidirectional cross-references, maintain graph edges, update index.md and log.md.
> This is the wiki's core skill — all knowledge flows in through ingest.

## Inputs

- `source`: local `.tex` / `.pdf` path, a canonical path handed off by `/init` (for example `raw/tmp/...` synthetic `.tex`, or `raw/discovered/...` fetched source dirs / PDFs), or an arXiv URL (e.g. `https://arxiv.org/abs/2106.09685`)

## Outputs

- `wiki/papers/{slug}.md` — paper page
- `wiki/concepts/{slug}.md` — new concept pages (if not already in wiki)
- `wiki/people/{slug}.md` — key author pages (importance >= 4 and not already in wiki)
- `wiki/claims/{slug}.md` — core claims from the paper (if not already in wiki)
- updated cross-reference pages (backlinks in concepts, topics, people, claims)
- updated `wiki/graph/edges.jsonl`
- updated `wiki/graph/context_brief.md` and `wiki/graph/open_questions.md`
- updated `wiki/index.md` and `wiki/log.md`

## Wiki Interaction

### Reads
- `wiki/index.md` — get all existing page slugs and tags for matching
- `wiki/papers/*.md` — check if paper is already ingested
- `wiki/concepts/*.md` — match existing concepts, append key_papers
- `wiki/topics/*.md` — match research directions, append paper
- `wiki/people/*.md` — match existing authors
- `wiki/claims/*.md` — match existing claims, append evidence
- `wiki/graph/open_questions.md` — check if paper fills known knowledge gaps

### Writes
- `wiki/papers/{slug}.md` — CREATE
- `wiki/concepts/{slug}.md` — CREATE (new concept) or EDIT (append key_papers)
- `wiki/topics/{slug}.md` — EDIT (append seminal_works / recent_work)
- `wiki/people/{slug}.md` — CREATE (new author) or EDIT (append Key papers)
- `wiki/claims/{slug}.md` — CREATE (new claim) or EDIT (append evidence)
- `wiki/graph/edges.jsonl` — APPEND (via tools/research_wiki.py add-edge)
- `wiki/graph/context_brief.md` — REBUILD
- `wiki/graph/open_questions.md` — REBUILD
- `wiki/index.md` — EDIT
- `wiki/log.md` — APPEND

### Graph edges created
- `paper → concept`: `supports` / `extends`
- `paper → paper`: `extends` / `contradicts` / `supersedes`
- `paper → claim`: `supports` / `contradicts`
- `concept → topic`: (if new concept discovered under existing topic)

## Workflow

**Prerequisites**: confirm working directory is the wiki project root (contains `wiki/`, `raw/`, `tools/`).
Set `WIKI_ROOT=wiki/`.

### Step 1: Parse Source

1. Detect source type:
   - **arXiv URL**: fetch tex source (ar5iv HTML or direct .tex download); fall back to PDF if unavailable
   - **local .tex**: read directly
   - **local .pdf**: inspect the PDF to recover a confident title when possible, and if the agent already recovered a confident arXiv ID keep that too; then run `python3 tools/prepare_paper_source.py --raw-root raw --source <local-path> [--title "<recovered-title>"] [--arxiv-id "<recovered-arxiv-id>"]`; the helper uses handed-off or filename/path arXiv IDs first, then agent-title Semantic Scholar recovery, and otherwise falls back directly to synthetic `.tex`. When a title was supplied by the agent, keep it authoritative; fetched/source titles are sanitized fallback metadata only.
   - **INIT MODE canonical handoff path**: if `/init` passes a path from `.checkpoints/init-sources.json`, ingest that exact `canonical_ingest_path` rather than rescanning sibling raw folders
2. Extract metadata: title, abstract, author list (with affiliations), publication date, venue
3. Extract reference list (BibTeX entries or reference section)
4. Raw-source persistence rule:
   - if the handed-off source already lives under `raw/discovered/` or `raw/tmp/`, treat that path as canonical and do not duplicate it into `raw/papers/`
   - if the source is a direct arXiv URL, save the fetched source artifact under `raw/discovered/` and ingest from there; do not write fetched sources into `raw/papers/`

### Step 2: Preprocessing and Annotation

1. **Generate slug**:
   ```bash
   python3 tools/research_wiki.py slug "<paper-title>"
   ```
2. **Deduplication check**: search `wiki/papers/` for an existing page with the same slug or arXiv ID. If found, notify user and stop.
3. **Extract keywords**: pull 3-8 core keywords from title and abstract
4. **Assign domain**: determine research domain (NLP / CV / ML Systems / Robotics, etc.)
5. **Query Semantic Scholar** (if arXiv ID is available):
   ```bash
   python3 tools/fetch_s2.py paper <arxiv_id>
   ```
   Retrieve citation count and s2_id; assess importance (1-5) from venue prestige and relevance.
6. **DeepXiv enrichment** (if arXiv ID is available, optional):
   ```bash
   python3 tools/fetch_deepxiv.py brief <arxiv_id>
   ```
   Use TLDR to seed the Key idea section; use keywords to supplement tags.
   ```bash
   python3 tools/fetch_deepxiv.py head <arxiv_id>
   ```
   Use paper structure (section names + TLDRs) to verify/supplement parsing from tex/pdf.
   ```bash
   python3 tools/fetch_deepxiv.py social <arxiv_id>
   ```
   Social impact metrics as an auxiliary signal for importance scoring (high tweet count → high community attention).
   **If DeepXiv unavailable**: skip all DeepXiv steps; rely on S2 + source file parsing only.
7. **Extract figure/table descriptions**: figure and table captions; key figures can be sent to vision API for interpretation
8. **Appendix summary** (summary extraction, not full text)

### Step 3: Create Paper Page

Fill all fields per the CLAUDE.md paper template and write `wiki/papers/{slug}.md`:

- frontmatter: title, slug, arxiv, venue, year, tags, importance, date_added, source_type, s2_id, keywords, domain, code_url, cited_by
- body sections: Problem, Key idea, Method, Results, Limitations, Open questions, My take, Related

### Step 4: Identify Claims (FIND existing first, CREATE only as last resort)

> 🚨 **CRITICAL — read this before doing anything in Step 4.**
> Claims are **shared** across papers. Multiple papers usually support the **same proposition** with different evidence. Your job is to find the existing claim each paper supports, not to create a new claim per paper. In production (test6 OmegaWiki, 15 papers), this step was previously done casually and produced 45 claims — including 4 separate claims all expressing "method X produces prompts that beat human/manual prompts". This wasted everyone's time and broke claim-graph reasoning. **The dedup tool below was built specifically to prevent this. Use it.**

**Hard limit per paper:**
- importance < 5: **at most 1 new claim**
- importance == 5 (seminal): **at most 2 new claims**
- All other claims this paper supports MUST be matched against existing claims (Branch A or B below)

#### Step 4.1: Identify candidate claims

Read the paper's contributions section and abstract. List 1-3 propositions the paper explicitly asserts as its main empirical or conceptual claims. Each candidate has:
- A short title (the proposition itself, e.g. "LLM-optimized prompts outperform human-written prompts")
- A few tags (e.g. `prompt-optimization,llm`)

#### Step 4.2: For each candidate, search for an existing equivalent — MANDATORY tool call

```bash
python3 tools/research_wiki.py find-similar-claim wiki/ "<candidate claim title>" --tags "<comma-separated tags>"
```

This is a deterministic tool that uses canonicalized token matching plus tag-aware Jaccard. It returns a JSON list of existing claims sorted by similarity score, e.g.:

```json
[
  {
    "slug": "llm-prompts-beat-human",
    "title": "LLM-optimized prompts outperform human-written prompts",
    "tags": ["prompt-optimization", "llm"],
    "status": "weakly_supported",
    "confidence": 0.7,
    "source_papers": ["opro"],
    "score": 0.62,
    "match_reason": "canonicalized token Jaccard 0.56; tags shared: ['prompt-optimization']"
  }
]
```

An empty list `[]` means no similar claim exists; you may proceed to Branch C.

#### Step 4.3: Branch on the JSON result

**Branch A — top result has score >= 0.80** (or exact title match, score == 1.0):
This is the **same claim**. Do NOT create a new file. Instead:
1. Read the existing claim file: `wiki/claims/<top-slug>.md`
2. Append a new entry to its `evidence` list:
   ```yaml
   - source: <paper-slug>
     type: supports        # or contradicts
     strength: moderate    # weak | moderate | strong
     detail: "<one-sentence evidence summary from this paper>"
   ```
3. Append `<paper-slug>` to the claim's `source_papers` list (if not already there)
4. Re-evaluate `confidence` and `status`: more strong evidence ⇒ higher confidence; mixed evidence ⇒ `weakly_supported`
5. Add graph edge:
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to claims/<top-slug> --type supports --evidence "<detail>"
   ```
6. Append `supports: [[<top-slug>]]` to the paper page's `## Related`

**Branch B — top result has score 0.40-0.80** (similar but not identical):
Read the existing claim's title and `## Statement` section. Make the call:
- If both express the **same proposition** with different wording → treat as Branch A
- If they express **genuinely different propositions** that just share vocabulary → treat as Branch C

**Default to Branch A when uncertain.** Over-merging is a much smaller mistake than over-creating: a wrongly-merged claim can be split later, but a sea of near-duplicate claims poisons every downstream reasoning step. If you choose Branch C here, your reasoning must mention what specific aspect of the proposition is genuinely novel.

**Branch C — top result has score < 0.40, OR list is empty**:
No existing claim covers this proposition.
1. **Check the hard limit first.** Count how many new claims you have already created for this paper. If you are at the limit (1 for importance < 5, 2 for importance == 5), **STOP creating new claims**. Force the remaining candidates into Branch A by picking the closest existing match from your earlier `find-similar-claim` results, even with score < 0.40.
2. Otherwise, create `wiki/claims/{claim-slug}.md` per the CLAUDE.md template:
   - Generate slug: `python3 tools/research_wiki.py slug "<claim-title>"`
   - status: `proposed` or `weakly_supported` (based on this paper's evidence strength)
   - source_papers: `[<paper-slug>]`
   - initialize `evidence` with this paper's entry
3. Add graph edge + paper `## Related` append (same as Branch A steps 5-6)

#### Step 4.4: Self-check at end of Step 4 — MANDATORY

Log how many claims this ingest created vs. matched:
```bash
python3 tools/research_wiki.py log wiki/ "ingest | claims for <paper-slug>: N matched existing, M new"
```

**If M > the hard limit**, you violated the constraint. STOP, undo the extra new claim files, convert them to Branch A appends.

#### Anti-patterns (do NOT do these)

- ❌ **Skipping `find-similar-claim`** because "I already know this is a new claim" — you don't, and the test6 incident proves it
- ❌ **Creating one new claim per main contribution** without checking if existing claims already cover it
- ❌ **Slug-only matching** ("the slugs are different so they must be different claims") — slugs are autogenerated from titles, paraphrases get different slugs even when the proposition is identical
- ❌ **Treating Branch B as "default to create"** — the default is merge, not split

### Step 5: Cross-References

**Part A — Concept matching and creation (FIND existing first, CREATE only as last resort)**

> 🚨 **CRITICAL — read this before creating any concept page.**
> Concepts are **shared** across papers. Multiple papers usually deepen the same concept rather than introducing new ones. Your job is to find the existing concept each paper extends and append this paper to its `key_papers`, not to create a new concept per paper. In production (test6 OmegaWiki, 15 papers), this step previously produced 37 concepts including 3 separate concepts for "LLM as gradient" (`textual-gradient-descent`, `textual-gradient-optimization`, `verbal-gradient`) and 2 separate concepts for "LLM as evolutionary operator" (`llm-driven-evolutionary-operators`, `llms-evolutionary-operators`). **The dedup tool below was built specifically to prevent this. Use it.**

**Hard limit per paper (counts NEW concept pages only):**
- importance < 5: **at most 1 new concept**
- importance == 5 (seminal): **at most 3 new concepts**
- All other concepts this paper relates to MUST be matched to an existing concept OR referenced from an existing foundation (Branch 0 / Branch A / Branch B below)
- Foundation references (Branch 0) do **not** count against the limit — referencing background knowledge is zero-cost

#### Step 5.A.1: Identify candidate concepts

Read the paper's method/approach sections. List 1-3 technical concepts the paper either introduces or substantially extends. Each candidate has:
- A title (e.g. "Textual Gradient Descent")
- A few alternative names / aliases the paper uses (e.g. `["natural language gradient", "text gradient", "APO gradient"]`)

#### Step 5.A.2: For each candidate, search for an existing equivalent — MANDATORY tool call

```bash
python3 tools/research_wiki.py find-similar-concept wiki/ "<candidate concept title>" --aliases "<comma-separated alternative names>"
```

This is a deterministic tool that matches by exact title, alias overlap, phrase containment, and token Jaccard. It scans **both `wiki/concepts/` and `wiki/foundations/`** and tags each result with `entity_type: "concept"` or `entity_type: "foundation"`. Results are returned as a JSON list sorted so that foundation hits come first, then concepts by score. Example:

```json
[
  {
    "entity_type": "foundation",
    "slug": "attention-mechanism",
    "title": "Attention Mechanism",
    "aliases": ["scaled dot-product attention", "self-attention"],
    "score": 0.85,
    "match_reason": "phrase containment: 'self-attention' ↔ 'attention mechanism'"
  },
  {
    "entity_type": "concept",
    "slug": "textual-gradient-descent",
    "title": "Textual Gradient Descent",
    "aliases": ["natural language gradient", "text gradient"],
    "key_papers": ["protegi"],
    "maturity": "emerging",
    "score": 1.0,
    "match_reason": "exact normalized match: 'Natural Language Gradient' == 'natural language gradient'"
  }
]
```

An empty list `[]` means no similar concept or foundation exists; you may proceed to Branch C.

#### Step 5.A.3: Branch on the JSON result

**Branch 0 — any result has `entity_type: "foundation"` and score >= 0.80** (evaluate this FIRST, before Branch A):
The candidate is foundational background knowledge. **Do not create a concept page, and do not modify the foundation page (foundations are terminal — no reverse link).**
1. Append `[[<foundation-slug>]]` to the paper page's `## Related` (reference the foundation directly)
2. Add a graph edge:
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to foundations/<foundation-slug> --type derived_from --evidence "<one-line summary>"
   ```
3. Do NOT add the paper to the foundation's frontmatter — foundations write no reverse links.
4. This candidate does **not** count toward the per-paper hard limit.

If the top result is a foundation with score 0.40-0.80, read the foundation's `## Definition`. If it's truly the same textbook concept, treat as Branch 0. If the paper is proposing a specifically new technical mechanism on top of that background, fall through to Branch A/B/C — but link `derived_from` to the foundation in addition to whatever concept you end up referencing.

**Branch A — top concept result (entity_type "concept") has score >= 0.85** (exact, alias, or phrase containment):
This is the **same concept**. Do NOT create a new file. Instead:
1. Read the existing concept file: `wiki/concepts/<top-slug>.md`
2. Append `<paper-slug>` to its `key_papers` list (skip if already present)
3. If the paper uses a new alternative name not in the concept's `aliases`, append it
4. If the paper introduces a notable variant, append a bullet to the concept's `## Variants` section
5. Add graph edge:
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to concepts/<top-slug> --type supports --evidence "<one-line summary>"
   ```
6. Append `[[<top-slug>]]` to the paper page's `## Related`

**Branch B — top concept result has score 0.40-0.85** (similar but not identical):
Read the existing concept's `## Definition` and `## Intuition` sections. Make the call:
- If both refer to the **same technical idea** (one is a more specific name, alternative phrasing, or subclass) → treat as Branch A. If the candidate is a meaningful subclass, also append it to the existing concept's `## Variants`.
- If they are **genuinely distinct technical ideas** that share vocabulary → treat as Branch C.

**Default to Branch A when uncertain.** Over-merging is a much smaller mistake than over-creating: a wrongly-merged concept can be split later (with `## Variants` history preserved), but a sea of near-duplicate concepts poisons gap detection, citation graphs, and survey generation. If you choose Branch C here, your reasoning must point to a specific technical distinction (different mechanism, different mathematical formulation, different application class).

**Branch C — top result has score < 0.40, OR list is empty**:
No existing concept or foundation covers this idea.
1. **Check the hard limit first.** Count how many NEW concept pages you have already created for this paper (Branch 0 foundation references do not count). If you are at the limit (1 for importance < 5, 3 for importance == 5), **STOP creating new concepts**. Force the remaining candidates into Branch A using the closest existing concept from `find-similar-concept`, even at score < 0.40.
2. Otherwise, create `wiki/concepts/{concept-slug}.md` per the CLAUDE.md template:
   - Generate slug: `python3 tools/research_wiki.py slug "<concept-title>"`
   - maturity: `emerging`
   - key_papers: `[<paper-slug>]`
   - aliases: list of all alternative names you found in the paper (be generous — this list is what future ingests will match against)
3. Append `[[<concept-slug>]]` to the paper page's `## Related`
4. Add graph edge (same as Branch A step 5)

#### Step 5.A.4: Self-check at end of Part A — MANDATORY

Log how many concepts this ingest created vs. matched vs. referenced-as-foundation:
```bash
python3 tools/research_wiki.py log wiki/ "ingest | concepts for <paper-slug>: N matched existing, M new, F foundation-refs"
```

**If M > the hard limit**, you violated the constraint. STOP, undo the extra new concept files, convert them to Branch A appends.

#### Anti-patterns (do NOT do these)

- ❌ **Skipping `find-similar-concept`** because "I already read all the concept pages at the start of /ingest" — even if you did, the test6 incident proves human-eye dedup misses paraphrases; and you also need the foundations scan
- ❌ **Creating one new concept per technical idea in the paper** without checking if existing concepts or foundations already cover them
- ❌ **Slug-only matching** — slugs are autogenerated from titles, the same idea phrased differently gets different slugs (test6: `llm-driven-evolutionary-operators` vs `llms-evolutionary-operators`)
- ❌ **Treating Branch B as "default to create"** — the default is merge, not split
- ❌ **Creating a "more general" or "more specific" version of an existing concept as a new page** — extend the existing concept with `## Variants` instead
- ❌ **Writing back to a foundation page** — foundations are terminal; their `key_papers`-style fields do not exist, and any reverse link violates the invariant. Only paper → foundation edges in `edges.jsonl` and `[[foundation-slug]]` in the paper's `## Related` are allowed.

**Part B — Topic matching:**

1. Match paper's domain/tags against existing topics
2. For each matched topic:
   - importance >= 4: append to `## Seminal works`
   - importance < 4: append to `## SOTA tracker` or `## Recent work` (by year)
3. If the paper directly addresses a topic's `## Open problems` or `## Research gaps`: annotate on the topic page

**Part C — Semantic Scholar external citations:**

1. If arXiv ID is available, query citations and references:
   ```bash
   python3 tools/fetch_s2.py citations <arxiv_id>
   python3 tools/fetch_s2.py references <arxiv_id>
   ```
2. For papers in citations that already exist in wiki: auto-backfill `cited_by`
3. For high-citation papers in references not yet in wiki: list as ingestion suggestions in the report

### Step 6: Handle Authors

1. Extract first author and corresponding author
2. For each key author:
   - **If `wiki/people/{author-slug}.md` exists**: append this paper to `## Key papers`; add `[[author-slug]]` to paper
   - **If not found and importance >= 4**: create page per the CLAUDE.md people template
3. For matched topics, if the author is a key figure in that domain: append to topic's `key_people`; reverse: append topic to people's `## Research areas`

### Step 7: Update Navigation and Graph

1. **index.md**: append all new/modified page entries under their respective categories
   ```bash
   # Format per CLAUDE.md index.md format section
   ```
2. **log.md**:
   ```bash
   python3 tools/research_wiki.py log wiki/ "ingest | added papers/<slug> | updated: <list-of-updated-pages>"
   ```
3. **Rebuild graph derived files**:
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

### Step 8: Report to User

Output a summary including:
- list of pages created (papers, concepts, people, claims)
- list of pages updated (pages that received cross-reference appends)
- extracted claims and their status
- number of graph edges added
- contradictions discovered (if any)
- S2 high-citation uningest papers suggested for follow-up (if any)

### Step 9: Wiki Growth Report

```bash
python3 tools/research_wiki.py maturity wiki/ --json
```

Append a one-line wiki status summary to the report:

```
Wiki: +1 paper, +{N} claims, +{M} concepts, +{K} edges | Maturity: {level} ({coverage}% coverage)
```

## Constraints

- **raw/ is read-only except canonical source prep**: treat `raw/papers/`, `raw/notes/`, and `raw/web/` as user-owned inputs. Direct local `/ingest` may write generated prepared local sidecars only under `raw/tmp/`, and direct arXiv ingests may write fetched source artifacts only under `raw/discovered/`. INIT MODE `/ingest` remains read-only and must consume the handed-off canonical path directly.
- **INIT MODE source handoff is authoritative**: when `/init` passes a `canonical_ingest_path` from `.checkpoints/init-sources.json`, ingest that exact path rather than rescanning `raw/papers/`, `raw/tmp/`, or `raw/discovered/`
- **graph/ via tools only**: do not manually edit files in `graph/` — use `python3 tools/research_wiki.py` only
- **Bidirectional links**: always write the reverse link when writing a forward link (see CLAUDE.md Cross-Reference Rules table)
- **tex priority**: .tex > .pdf > vision API fallback
- **Slug via tool**: always use `python3 tools/research_wiki.py slug` to generate slugs — never hand-craft
- **index.md updated immediately**: index.md must be updated before ingest completes
- **log.md append-only**: append via `python3 tools/research_wiki.py log`
- **Importance scoring**: 1=niche, 2=useful, 3=field-standard, 4=influential, 5=seminal
- **Conservative claim extraction**: extract only claims the paper explicitly asserts — do not over-infer
- **Deduplication is mandatory, not optional**: BEFORE creating any new claim or concept page, you MUST run `find-similar-claim` / `find-similar-concept` and follow Step 4 / Step 5.A's branching logic. `find-similar-concept` scans both `concepts/` and `foundations/`; a foundation match routes to Branch 0 (reference only, never create). Skipping the dedup tool is the single most common cause of wiki bloat.
- **Hard limits per paper**: at most 1 new claim and 1 new concept (or 2 claims and 3 concepts if importance == 5). All other claims/concepts must be matched to existing entries via Branch A, or referenced from a foundation via Branch 0. When in doubt, merge.
- **Foundations are terminal**: never write a reverse link from a paper to a foundation's frontmatter. Foundation references live only in the paper's `## Related` and in `edges.jsonl`.

## Error Handling

- **Source parse failure**: tex fails → PDF parse → vision API → report to user for manual handling. For direct local PDFs, if no confident title is recovered, call `tools/prepare_paper_source.py` without `--title`; that means filename/path arXiv-ID recovery only, then immediate synthetic-`.tex` fallback. Metadata or filename titles are display-only and must not drive title-based lookup. In INIT MODE, synthetic `.tex` under `raw/tmp/` and fetched source dirs / PDFs under `raw/discovered/` are valid inputs and should be consumed as handed off.
- **S2 API unavailable**: skip S2 steps (citations backfill, default importance to 3); note in report
- **DeepXiv API unavailable**: skip DeepXiv enrichment (TLDR, structure verification, social metrics); fall back to S2 + source file parsing
- **Slug conflict**: if generated slug already exists but content differs, append numeric suffix (e.g. `attention-mechanism-2`)
- **wiki directory missing**: run `python3 tools/research_wiki.py init wiki/` to initialize, then retry
- **Partial step failure**: preserve completed steps; list incomplete steps in report for manual follow-up

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — slug generation
- `python3 tools/research_wiki.py find-similar-concept wiki/ "<title>" --aliases "<a,b,c>"` — **MANDATORY before creating any concept** (Step 5 Part A). Scans both `concepts/` and `foundations/`; tag-ranked foundations first.
- `python3 tools/research_wiki.py find-similar-claim wiki/ "<title>" --tags "<a,b,c>"` — **MANDATORY before creating any claim** (Step 4). Canonicalized token Jaccard with tag-aware threshold.
- `python3 tools/research_wiki.py add-edge wiki/ --from <id> --to <id> --type <type> --evidence "<text>"` — add graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild compressed context
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — rebuild knowledge gap map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log entry
- `python3 tools/prepare_paper_source.py --raw-root raw --source <local-path> [--title "<recovered-title>"]` — normalize a local source into a canonical ingest path
- `python3 tools/fetch_s2.py paper <arxiv_id>` — query Semantic Scholar
- `python3 tools/fetch_s2.py citations <arxiv_id>` — query citations
- `python3 tools/fetch_s2.py references <arxiv_id>` — query references
- `python3 tools/fetch_deepxiv.py brief <arxiv_id>` — fetch TLDR + keywords
- `python3 tools/fetch_deepxiv.py head <arxiv_id>` — fetch paper structure
- `python3 tools/fetch_deepxiv.py social <arxiv_id>` — fetch social impact metrics

### Shared References
- `.claude/skills/shared-references/citation-verification.md`

### External APIs
- Semantic Scholar API (via tools/fetch_s2.py)
- DeepXiv API (via tools/fetch_deepxiv.py, optional — graceful fallback when unavailable)
- arXiv (source download)
- ar5iv (HTML source)
