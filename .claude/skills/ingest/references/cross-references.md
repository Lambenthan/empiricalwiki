# /ingest Cross-References

Open this reference when you are writing a link on any wiki page. Every forward link has a reverse obligation (except to foundations). The table below is the contract.

## Forward → reverse obligation

Mirrors the matrix in the root `CLAUDE.md` ("Cross-Reference Rules"), trimmed to the edges `/ingest` actually writes:

| Forward action (what you write on page A) | Required reverse action (what you also write on page B in the same turn) |
|-------------------------------------------|--------------------------------------------------------------------------|
| `papers/P` writes `Related: [[concept-K]]` | `concepts/K` appends `P` to `key_papers` |
| `papers/P` writes `[[person-R]]` (in Key authors) | `people/R` appends `P` to `Key papers` |
| `papers/P` writes `supports: [[claim-C]]` | `claims/C` appends `{source: P, type: supports}` to `evidence` |
| `papers/P` writes `supports: [[claim-C]]` but paper contradicts claim | use `type: contradicts` in the evidence entry |
| `claims/C` writes `source_papers: [[paper-P]]` | `papers/P` appends `C` to `## Related` |
| `concepts/K` writes `key_papers: [[paper-P]]` | `papers/P` appends `K` to `## Related` |
| any page writes `[[foundation-X]]` | **no reverse link** — foundations are terminal |

Writing a forward link without its reverse is the most common way `/check` surfaces `missing-field` errors. Doing both together eliminates the class entirely.

## Foundations are terminal

Never modify a foundation page from `/ingest`. No `key_papers` field, no back-reference of any kind. A paper linking to a foundation leaves a trace only in two places:

- the paper page's `## Related` contains `[[foundation-slug]]`
- `wiki/graph/edges.jsonl` contains the `paper → foundation` edge with type `derived_from`

Foundations are created only by `/prefill`. `/ingest` never creates foundations, even when a concept candidate looks foundational and has no match. In that case, route the candidate through the ordinary concept path (possibly creating a new concept page), and let the user seed a foundation later if they want to.

## Paper-to-paper edges

Emit a paper-to-paper edge only when the cited paper already has a page under `wiki/papers/`. Do not speculate: if the reference is not yet in the wiki, skip the edge and surface the reference in the final report as a follow-up suggestion.

Edge-type selection, by cue:

- **`extends`** — the paper explicitly builds its method on top of the cited paper's method. Phrases in the paper like "we extend", "building on", "we follow X but".
- **`supersedes`** — the paper claims to replace the cited baseline on its own terms (same task, stronger results or cleaner formulation) and positions it as the thing to replace. Reserve this for explicit claims; do not infer from benchmark tables alone.
- **`inspired_by`** — the paper cites the earlier work as motivation or conceptual lineage but does not build on its method directly. Common for survey-style or cross-domain borrowings.
- **`contradicts`** — the paper explicitly disputes a cited finding, either by replicating and failing, or by presenting a direct counterexample. Must be grounded in a specific sentence in the paper.
- **none / skip** — if none of the above cleanly fits, skip the edge. Graph noise is worse than a missing edge.

One edge per ordered paper pair is enough. If you are uncertain between two types, pick the weaker claim (`inspired_by` over `extends`, `extends` over `supersedes`).

## Writing both sides atomically

For every link `/ingest` writes, the reverse should land in the same turn. In practice that means:

1. Decide on the link.
2. Write the forward entry on the originating page.
3. Write the reverse entry on the target page.
4. If the link also corresponds to a graph edge (paper↔concept, paper↔claim, paper↔paper, paper→foundation), emit it via `tools/research_wiki.py add-edge`.

This pattern keeps `/check` from flagging half-written links in its next run. It also makes rollbacks straightforward: if a paper ingest is aborted, you can undo both sides together by reverting the paper's edits.

## What `/ingest` does not check here

`/ingest` writes forward and reverse links as it goes, but it does not verify that every pre-existing link in the wiki still has its reverse. That is a full-graph audit and belongs to `/check`. Do not read the entire `wiki/` to look for broken back-references during ingest — the time and token cost is large and the work is redundant with `/check`.
