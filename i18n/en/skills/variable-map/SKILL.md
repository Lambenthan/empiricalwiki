---
description: Compare how an empirical variable or construct is measured across papers, including data sources, model roles, and local-project availability
argument-hint: "<variable-or-construct> [--role dependent|core_explanatory|mediator|moderator|control|all]"
---

# /variable-map

Read `wiki/variables/*.md`, `wiki/papers/*.md`, `wiki/datasets/*.md`, `wiki/models/*.md`, project READMEs, and `raw/notes/research-intent.md` when present.

Produce a comparison table with: construct, variable role, measurement, data source, sample frequency, source papers, advantages, risks, and project availability.

Archive the result to `wiki/outputs/variable-map-{slug}-{YYYY-MM-DD}.md` and log it with `tools/research_wiki.py log`.

Constraints:

- Do not merge genuinely different measurement choices into one row.
- Do not invent database tables or project paths.
- Mark fields that exist in the literature but are missing locally as `missing from project`.
