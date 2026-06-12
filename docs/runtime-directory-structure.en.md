# Runtime Directory Chart

> On-demand reference for the repo layout. The main `CLAUDE.md` keeps only the schema and rules that should stay in immediate context.

```text
CLAUDE.md              ← runtime schema (repo root)
AGENTS.md              ← entry point for any coding agent (points to CLAUDE.md)

wiki/
├── index.md           ← content catalog (YAML)
├── log.md             ← chronological log (append-only)
├── papers/            ← structured empirical paper cards
├── variables/         ← variable definitions, roles, measurements, source papers
├── datasets/          ← data sources, sample coverage, units, fields
├── models/            ← baseline, mechanism, heterogeneity, and robustness specifications
├── mechanisms/        ← theory mechanisms and empirical evidence chains
├── hypotheses/        ← hypotheses and literature support
├── identification/    ← identification strategies, endogeneity handling, assumptions
├── robustness/        ← robustness-check library
├── heterogeneity/     ← heterogeneity grouping logic
├── tables/            ← result tables, variable tables, regression-table interpretations
├── concepts/          ← reusable cross-paper concepts
├── topics/            ← research direction maps
├── people/            ← author and research-lineage profiles
├── ideas/             ← research ideas (with lifecycle status)
├── experiments/       ← retained for computational experiments; empirical work should prefer models/ and tables/
├── claims/            ← testable theoretical or empirical claims
├── Summary/           ← domain-wide surveys
├── foundations/       ← background knowledge (terminal: receives inward links, writes none)
├── outputs/           ← generated artifacts (literature reviews, variable maps, empirical plans, Stata plans)
└── graph/             ← auto-generated (do not edit)
    ├── edges.jsonl
    ├── citations.jsonl
    ├── context_brief.md
    └── open_questions.md

raw/
├── papers/            ← user-owned .tex / .pdf sources
├── discovered/        ← externally fetched papers from /init and /daily-arxiv
├── tmp/               ← generated prepared local sources for /init and direct local /ingest
├── notes/             ← user-owned .md notes
└── web/               ← user-owned HTML / Markdown

tools/
├── research_wiki.py   ← wiki engine (slug / add-edge / rebuild-* / checkpoint)
├── lint.py            ← structural validation (--fix / --suggest)
├── stata-templates/   ← preset .do skeletons (TWFE / DID / PSM / IV / RDD)
├── golden_check.py    ← ingest-quality regression checker (with tests/golden/)
├── view.sh            ← local website view via Quartz
├── update_demo.sh     ← refresh the demo branch without switching branches
└── fetch_*.py / discover.py / remote.py / reset_wiki.py / prepare_paper_source.py

tests/golden/          ← benchmark papers with expected-extraction checklists

.claude/skills/        ← 29 skills (one SKILL.md per directory)

config/
├── server.yaml        ← remote GPU server config (optional, needed for /exp-run --env remote)
├── server.yaml.example
└── settings.local.json.example

.env.example           ← environment template (repo root; setup copies it to .env)
```

## Fast Reminders

- `raw/papers/`, `raw/notes/`, and `raw/web/` are user-owned inputs.
- For empirical projects, write `raw/notes/research-intent.md` with the research topic, likely dependent variable, core explanatory variable, data scope, and anchor papers to replicate or compare against.
- `raw/discovered/` is for fetched external papers, not user drop-ins.
- `raw/tmp/` is generated intermediate state for `/init` and direct local `/ingest`.
- `graph/` is derived and should be maintained only through `tools/research_wiki.py`.
