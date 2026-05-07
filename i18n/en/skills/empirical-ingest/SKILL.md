---
description: Ingest an empirical social-science paper into the wiki: paper card plus variables, datasets, models, mechanisms, identification, robustness, heterogeneity, and tables
argument-hint: "<local-pdf-or-tex-path> [--topic <research-topic>]"
---

# /empirical-ingest

> Convert one empirical paper into reusable research-design assets. This is not a generic summary command: extract variables, data, model specification, mechanisms, identification, robustness, and heterogeneity before writing generic concepts.

## Workflow

1. Confirm the cwd contains `wiki/`, `raw/`, and `tools/`.
2. Resolve the source. For PDFs, inspect the first page for a confident title, then run `tools/prepare_paper_source.py --raw-root raw --source <source> [--title "<title>"]`.
3. Extract only text-supported empirical facts: research question, mechanisms, hypotheses, sample period, data sources, variables, measurement formulas, baseline model, fixed effects, clustered standard errors, endogeneity handling, mechanism tests, heterogeneity tests, robustness checks, key tables, and reproduction notes.
4. Open `docs/runtime-page-templates.en.md` and create or update the relevant pages under `papers/`, `variables/`, `datasets/`, `models/`, `mechanisms/`, `hypotheses/`, `identification/`, `robustness/`, `heterogeneity/`, and `tables/`.
5. Add graph edges through `tools/research_wiki.py add-edge`, using empirical edge types such as `operationalizes`, `uses_dataset`, `estimates_model`, `tests_mechanism`, `addresses_endogeneity_with`, `uses_robustness_check`, and `uses_heterogeneity_split`.
6. Rebuild `index.md`, `context_brief.md`, and `open_questions.md`; then run `tools/lint.py --wiki-dir wiki`.

## Constraints

- Do not invent formulas, database table names, variable names, or identification strategies.
- If a paper does not report a detail, write `not reported`.
- Local Chinese-language PDFs without arXiv/Semantic Scholar metadata are valid sources; rely on the paper text and the local project.
- Never overwrite or move user-owned files under `raw/papers/`.
