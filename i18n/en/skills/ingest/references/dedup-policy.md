# /ingest Dedup Policy

Open this reference when you are about to create or update a concept, claim, or foundation link.

## The mental model

A healthy ΩmegaWiki has far fewer claims and concepts than papers. Each concept is shared by many papers that deepen or extend it; each claim is supported by many papers that present evidence. When `/ingest` creates a new concept or claim per paper by default, the wiki quickly devolves into a pile of near-duplicates that breaks every downstream skill — survey generation, gap detection, idea novelty, citation reasoning.

The default action is **merge**. The exception is **create**, and it needs a clear reason every time.

## When to open this reference

- Step 4 of `/ingest`: identifying claims the paper supports.
- Step 4 of `/ingest`: identifying concepts the paper introduces or extends.
- Any time you are tempted to create a new concept or claim "for safety" without checking.

## Required tool call

Before creating a new concept or claim, call the matching dedup tool:

```bash
"$PYTHON_BIN" tools/research_wiki.py find-similar-concept wiki/ "<candidate title>" --aliases "<a,b,c>"
"$PYTHON_BIN" tools/research_wiki.py find-similar-claim   wiki/ "<candidate title>" --tags    "<a,b,c>"
```

Both tools return a JSON list sorted by similarity. `find-similar-concept` scans `wiki/concepts/` and `wiki/foundations/` together and tags each hit with `entity_type`. The tool is the source of truth for the similarity score; do not re-estimate it by eye.

Skipping these tools is the single most common cause of wiki bloat. If you think you already have the answer from reading pages earlier in the session, you still call the tool — paraphrases slip past human scanning.

## Decision rule

Read the top result's `score`.

- **Top result is a foundation with score ≥ 0.40** — route to foundation linking. The candidate is textbook background, not a new mechanism. Write a `paper → foundation` edge of type `derived_from` and a `[[foundation-slug]]` entry in the paper's `## Related`. Do not modify the foundation page (foundations are terminal; see `references/cross-references.md`). Foundation links do not count against the per-paper creation limit.
- **Score ≥ 0.80** — merge. The candidate is the same concept or claim as the top result. Append this paper to the existing page's `key_papers` or `evidence` list, add the relevant graph edge, and write the reverse link on the paper page. For concepts, use `uses_concept` by default, `extends_concept` only when the paper materially modifies/generalizes/specializes the concept, and `critiques_concept` only for explicit critique. Do not create a new file.
- **Score 0.40–0.80** — read the existing page's `## Definition` / `## Statement` and decide. Default to merge. Create only when you can point to a specific technical distinction: different mechanism, different formulation, or a genuinely different proposition. If the candidate is a meaningful subclass of the existing concept, merge and add a bullet under `## Variants` instead of splitting.
- **Score < 0.40 or empty list** — no existing match. Creation is allowed, subject to the per-paper creation limit below.

Over-merging is cheap to undo: a wrongly-merged entry can be split later with its history preserved. Over-creating is expensive: a sea of near-duplicates silently poisons every downstream skill and is hard to detect post-hoc.

## Per-paper creation limit

The purpose of the limit is to keep the default behavior conservative. It is not a quota to fill.

- importance < 4: at most **1** new concept and **1** new claim
- importance ≥ 4: at most **3** new concepts and **2** new claims
- Foundation references do not count.

When further candidates would exceed the limit, merge them into the nearest `find-similar-*` result even if its score is below the usual merge threshold. If no candidate is close enough to merge safely, skip writing that entity — `/check` will surface the resulting gaps, and the user can decide whether to `/edit` them in.

## Write shape, not semantics

When you do create or edit a concept or claim page, run the same narrow shape check you run on paper pages:

- every required frontmatter key present and non-empty
- `maturity` ∈ {`stable`, `active`, `emerging`, `deprecated`} for concepts
- `status` ∈ {`proposed`, `weakly_supported`, `supported`, `challenged`, `deprecated`} and `confidence` ∈ [0,1] for claims
- YAML parses

This check keeps `/check` from flagging trivially malformed pages on its next run. Anything beyond this — backlink symmetry, whether the claim's evidence is actually sufficient to justify its status, whether the concept's `part_of` topic is reciprocated — is `/check`'s job. Running those audits inside `/ingest` slows the skill down and duplicates work.

## What `/check` owns, not `/ingest`

- cross-entity backlink symmetry (A links to B ⇒ B links back to A)
- dangling-node detection (pages referenced but missing, or existing but unreachable)
- status / confidence consistency across claims and experiments
- edge-type validity and edge dedup
- tiered fix recommendations for any of the above

You can trust `/check` to find these and produce a fix report. Focus `/ingest` on emitting well-shaped entities and correct forward/reverse links at the point of writing.
