---
description: Ingest a paper into the wiki — creates pages (papers + concepts + people + claims) and builds all cross-references and graph edges
argument-hint: <local-path-or-arXiv-URL>
---

# /ingest

> Fully absorb a paper into the wiki: create the paper page, extract/create concepts, people, and claims,
> establish all bidirectional cross-references, maintain graph edges, update index.md and log.md.
> This is the wiki's core skill — all knowledge flows in through ingest.

## Inputs

- `source`: local .tex / .pdf path, or arXiv URL (e.g. `https://arxiv.org/abs/2106.09685`)

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
   - **local .pdf**: extract text (PyMuPDF or vision API fallback)
2. Extract metadata: title, abstract, author list (with affiliations), publication date, venue
3. Extract reference list (BibTeX entries or reference section)
4. If arXiv ID is present, save source file to `raw/papers/`

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

### Step 4: Extract Claims

Extract 1-3 core claims from the paper (the paper's main contribution assertions).

For each claim:
1. Generate claim slug: `python3 tools/research_wiki.py slug "<claim-title>"`
2. Check `wiki/claims/` for a semantically matching claim (semantic match, not just slug match)
3. **If claim already exists**:
   - Append a new evidence entry to the claim's `evidence` list:
     ```yaml
     - source: <paper-slug>
       type: supports    # supports | contradicts
       strength: moderate  # weak | moderate | strong (based on paper's evidence strength)
       detail: "..."
     ```
   - Re-evaluate `confidence` and `status` based on new evidence
   - Add graph edge:
     ```bash
     python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to claims/<claim-slug> --type supports --evidence "<detail>"
     ```
4. **If claim does not exist**:
   - Create `wiki/claims/{claim-slug}.md` per the CLAUDE.md claim template
   - status: proposed or weakly_supported (based on paper's evidence strength)
   - source_papers: [<paper-slug>]
   - initialize evidence with the paper's evidence entry
   - Add graph edge: same as above
5. Append claim link to the paper page's `## Related`: `supports: [[claim-slug]]`

### Step 5: Cross-References

**Part A — Concept matching and creation (with semantic dedup):**

1. Read `wiki/index.md`, extract all existing concept slugs and tags
2. Read each existing concept's frontmatter for `title` and `aliases`
3. **Also scan `wiki/foundations/*.md`** for `title`, `slug`, and `aliases`. Foundations are background-knowledge pages seeded by `/prefill` — they take precedence over creating new concepts for textbook material.
4. For each candidate concept from the paper, **check for duplicates first**:
   - **Foundation match** (slug, title, or alias): the candidate is foundational background. **Do not create a concept page.** Reference the foundation directly: append `[[foundation-slug]]` to the paper's `## Related`. Foundations are terminal — do not modify the foundation page (no reverse link).
   - Exact slug match with an existing concept → same concept
   - Semantically equivalent to an existing concept's title or any alias (alternative name, subclass, concrete implementation) → same concept
   - A **variant or subclass** of an existing concept (e.g. "scaled dot-product attention" vs "attention-mechanism") → do not create a new page; append to existing concept's `## Variants` and add candidate name to `aliases`
   - Only create a new page if it is **genuinely a new concept** and not already covered by a foundation
4. For each matched concept:
   - If this paper is a core paper for the concept: append slug to concept's `key_papers`
   - If introducing a new variant: append to concept's `## Variants`, add variant name to `aliases`
   - If contradicting: record contradiction note on the concept page
   - Reverse: append `[[concept-slug]]` to paper's `## Related`
   - Add graph edge:
     ```bash
     python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to concepts/<concept-slug> --type supports --evidence "..."
     ```
5. If the paper introduces a genuinely new concept (confirmed by the dedup check above):
   - Create `wiki/concepts/{concept-slug}.md` per the CLAUDE.md concept template
   - maturity: emerging
   - key_papers: [<paper-slug>]
   - aliases: [known alternative names] (collect on creation)
   - Append `[[concept-slug]]` to paper's `## Related`

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

- **raw/ is read-only**: do not modify files under `raw/`
- **graph/ via tools only**: do not manually edit files in `graph/` — use `python3 tools/research_wiki.py` only
- **Bidirectional links**: always write the reverse link when writing a forward link (see CLAUDE.md Cross-Reference Rules table)
- **tex priority**: .tex > .pdf > vision API fallback
- **Slug via tool**: always use `python3 tools/research_wiki.py slug` to generate slugs — never hand-craft
- **index.md updated immediately**: index.md must be updated before ingest completes
- **log.md append-only**: append via `python3 tools/research_wiki.py log`
- **Importance scoring**: 1=niche, 2=useful, 3=field-standard, 4=influential, 5=seminal
- **Conservative claim extraction**: extract only claims the paper explicitly asserts — do not over-infer
- **Deduplication check**: check for existing pages before creating any new page

## Error Handling

- **Source parse failure**: tex fails → PDF parse → vision API → report to user for manual handling
- **S2 API unavailable**: skip S2 steps (citations backfill, default importance to 3); note in report
- **DeepXiv API unavailable**: skip DeepXiv enrichment (TLDR, structure verification, social metrics); fall back to S2 + source file parsing
- **Slug conflict**: if generated slug already exists but content differs, append numeric suffix (e.g. `attention-mechanism-2`)
- **wiki directory missing**: run `python3 tools/research_wiki.py init wiki/` to initialize, then retry
- **Partial step failure**: preserve completed steps; list incomplete steps in report for manual follow-up

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — slug generation
- `python3 tools/research_wiki.py add-edge wiki/ --from <id> --to <id> --type <type> --evidence "<text>"` — add graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild compressed context
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — rebuild knowledge gap map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log entry
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
