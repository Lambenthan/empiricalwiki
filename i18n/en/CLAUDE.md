# ΩmegaWiki — Runtime Schema

> CS/AI ΩmegaWiki. Powered by Claude Code.
> This file is the wiki's runtime entry point: defines page structure, link conventions, and workflow constraints.

> **Maintenance note**: Managed under `i18n/`. Edit `i18n/en/CLAUDE.md` (not the active copy at the root). Run `./setup.sh --lang <current>` to sync.

---

## Directory Structure

```
wiki/
├── CLAUDE.md          ← this file
├── index.md           ← content catalog (YAML)
├── log.md             ← chronological log (append-only)
├── papers/            ← structured paper summaries
├── concepts/          ← cross-paper technical concepts
├── topics/            ← research direction maps
├── people/            ← researcher profiles
├── ideas/             ← research ideas (with lifecycle status)
├── experiments/       ← experiment records (wiki pages)
├── claims/            ← testable research claims
├── Summary/           ← domain-wide surveys
├── outputs/           ← generated artifacts (Related Work, paper drafts)
└── graph/             ← auto-generated (do not edit)
    ├── edges.jsonl    ← typed relationship graph
    ├── context_brief.md  ← compressed context (≤8000 chars)
    └── open_questions.md     ← open questions and knowledge gaps

raw/
├── papers/            ← .tex / .pdf (read-only)
├── notes/             ← .md notes (read-only)
└── web/               ← HTML / Markdown (read-only)

config/
├── server.yaml        ← remote GPU server config (optional, needed for /exp-run --env remote)
├── server.yaml.example
├── .env.example
└── settings.local.json.example
```

---

## 8 Page Types

| Directory | Filename | Purpose |
|-----------|----------|---------|
| `papers/` | `{slug}.md` | structured paper summary |
| `concepts/` | `{concept-name}.md` | cross-paper technical concept |
| `topics/` | `{topic-name}.md` | research direction map |
| `people/` | `{firstname-lastname}.md` | researcher profile |
| `ideas/` | `{idea-slug}.md` | research idea (proposed → tested → validated/failed) |
| `experiments/` | `{experiment-slug}.md` | experiment record (hypothesis → setup → results → claim updates) |
| `claims/` | `{claim-slug}.md` | testable research claim linking papers, experiments, and reviews |
| `Summary/` | `{area-name}.md` | domain-wide survey |

---

## Link Syntax

All internal links use Obsidian wikilinks:

```markdown
[[slug]]                    ← link to any page in this wiki
[[lora-low-rank-adaptation]] ← links to papers/lora-low-rank-adaptation.md
[[flash-attention]]          ← links to concepts/flash-attention.md
```

**Naming convention**: all lowercase, hyphen-separated, no spaces.

---

## Cross-Reference Rules

When writing a forward link, **always write the reverse link simultaneously**:

| Forward action | Required reverse action |
|----------------|------------------------|
| papers/A writes `Related: [[concept-B]]` | concepts/B appends A to `key_papers` |
| papers/A writes `[[researcher-C]]` | people/C appends A to `Key papers` |
| papers/A writes `supports: [[claim-D]]` | claims/D appends `{source: A, type: supports}` to `evidence` |
| topics/T writes `key_people: [[person-D]]` | people/D appends T to `Research areas` |
| concepts/K writes `key_papers: [[paper-E]]` | papers/E appends K to `Related` |
| concepts/K writes part_of `[[topic-F]]` | topics/F appends K to overview paragraph |
| ideas/I writes `origin_gaps: [[claim-C]]` | claims/C appends I to `## Linked ideas` |
| experiments/E writes `target_claim: [[claim-C]]` | claims/C appends `{source: E, type: tested_by}` to `evidence` |
| claims/C writes `source_papers: [[paper-P]]` | papers/P appends C to `## Related` |

---

## Page Templates

### papers/{slug}.md

```yaml
---
title: ""
slug: ""
arxiv: ""
venue: ""
year:
tags: []
importance: 3           # 1-5
date_added: YYYY-MM-DD
source_type: tex         # tex | pdf
s2_id: ""
keywords: []
domain: ""               # NLP / CV / ML Systems / Robotics
code_url: ""
cited_by: []
---
```

Body sections: `## Problem` / `## Key idea` / `## Method` / `## Results` / `## Limitations` / `## Open questions` / `## My take` / `## Related`

### concepts/{concept-name}.md

```yaml
---
title: ""
aliases: []              # alias list (for dedup matching, e.g. ["scaled dot-product attention", "SDPA"])
tags: []
maturity: active         # stable | active | emerging | deprecated
key_papers: []
first_introduced: ""
date_updated: YYYY-MM-DD
related_concepts: []
---
```

Body sections: `## Definition` / `## Intuition` / `## Formal notation` / `## Variants` / `## Comparison` / `## When to use` / `## Known limitations` / `## Open problems` / `## Key papers` / `## My understanding`

### topics/{topic-name}.md

```yaml
---
title: ""
tags: []
my_involvement: none     # none | reading | side-project | main-focus
sota_updated: YYYY-MM-DD
key_venues: []
related_topics: []
key_people: []
---
```

Body sections: `## Overview` / `## Timeline` / `## Seminal works` / `## SOTA tracker` / `## Open problems` / `## My position` / `## Research gaps` / `## Key people`

### people/{firstname-lastname}.md

```yaml
---
name: ""
affiliation: ""
tags: []
homepage: ""
scholar: ""
date_updated: YYYY-MM-DD
---
```

Body sections: `## Research areas` / `## Key papers` / `## Recent work` / `## Collaborators` / `## My notes`

### Summary/{area-name}.md

```yaml
---
title: ""
scope: ""
key_topics: []
paper_count:
date_updated: YYYY-MM-DD
---
```

Body sections: `## Overview` / `## Core areas` / `## Evolution` / `## Current frontiers` / `## Key references` / `## Related`

### ideas/{idea-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed          # proposed | in_progress | tested | validated | failed
origin: ""                # source description: which paper's gap, which claim's weak evidence, etc.
origin_gaps: []           # related claim/topic slugs (knowledge gap sources)
tags: []
domain: ""                # NLP / CV / ML Systems / Robotics
priority: 3               # 1-5 (1=low, 5=critical)
pilot_result: ""          # brief pilot experiment summary (fill after tested)
failure_reason: ""        # failure reason (fill after failed — anti-repetition memory)
linked_experiments: []    # linked experiment slugs
date_proposed: YYYY-MM-DD
date_resolved: ""         # validated/failed date
---
```

Body sections: `## Motivation` / `## Hypothesis` / `## Approach sketch` / `## Expected outcome` / `## Risks` / `## Pilot results` / `## Lessons learned`

### experiments/{experiment-slug}.md

```yaml
---
title: ""
slug: ""
status: planned           # planned | running | completed | abandoned
target_claim: ""          # target claim slug
hypothesis: ""            # hypothesis being tested
tags: []
domain: ""                # NLP / CV / ML Systems / Robotics
setup:
  model: ""
  dataset: ""
  hardware: ""
  framework: ""
metrics: []               # evaluation metrics, e.g. [accuracy, F1, latency]
baseline: ""              # comparison baseline description
outcome: ""               # succeeded | failed | inconclusive
key_result: ""            # one-sentence core finding
linked_idea: ""           # source idea slug
date_planned: YYYY-MM-DD
date_completed: ""
run_log: ""               # run log path (optional)
started: ""              # start time (ISO format, written by /exp-run)
estimated_hours: 0        # estimated runtime in hours (auto-estimated by /exp-run)
remote:                   # remote deployment info (written by /exp-run --env remote)
  server: ""              # server host
  gpu: ""                 # GPU index
  session: ""             # screen session name
  started: ""             # deployment time (ISO format)
  completed: ""           # completion time
---
```

Body sections: `## Objective` / `## Setup` / `## Procedure` / `## Results` / `## Analysis` / `## Claim updates` / `## Follow-up`

### claims/{claim-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed          # proposed | weakly_supported | supported | challenged | deprecated
confidence: 0.5           # 0.0-1.0
tags: []
domain: ""                # NLP / CV / ML Systems / Robotics
source_papers: []         # slugs of papers that proposed this claim
evidence:                 # evidence list
  - source: ""            # paper/experiment slug
    type: supports        # supports | contradicts | tested_by | invalidates
    strength: moderate    # weak | moderate | strong
    detail: ""
conditions: ""            # preconditions and scope under which the claim holds
date_proposed: YYYY-MM-DD
date_updated: YYYY-MM-DD
---
```

Body sections: `## Statement` / `## Evidence summary` / `## Conditions and scope` / `## Counter-evidence` / `## Linked ideas` / `## Open questions`

### graph/ (auto-generated — do not edit)

The `graph/` directory is maintained automatically by `tools/research_wiki.py`, derived from wiki page content.

| File | Content | Generated by |
|------|---------|-------------|
| `edges.jsonl` | typed relationships (extends, contradicts, supports, inspired_by, tested_by, invalidates, supersedes, addresses_gap, derived_from) | `python3 tools/research_wiki.py add-edge` |
| `context_brief.md` | compressed context: claims + gaps + failed ideas + papers + edges (≤8000 chars) | `python3 tools/research_wiki.py rebuild-context-brief` |
| `open_questions.md` | open questions: under-supported claims + open questions from papers/topics | `python3 tools/research_wiki.py rebuild-open-questions` |

Each edge format: `{"from": "node_id", "to": "node_id", "type": "edge_type", "evidence": "...", "date": "..."}`

---

## index.md format

```yaml
papers:
  - slug: lora-low-rank-adaptation
    title: "LoRA: Low-Rank Adaptation of Large Language Models"
    tags: [fine-tuning, efficiency]
    importance: 5

concepts:
  - slug: parameter-efficient-fine-tuning
    tags: [fine-tuning, efficiency]
    maturity: stable

topics:
  - slug: efficient-llm-adaptation
    tags: [fine-tuning, efficiency, llm]

people:
  - slug: tri-dao
    affiliation: "Princeton / Together AI"

ideas:
  - slug: sparse-lora-for-edge-devices
    status: proposed
    domain: ML Systems
    priority: 4

experiments:
  - slug: sparse-lora-latency-benchmark
    status: planned
    target_claim: lora-preserves-quality-at-low-rank
    domain: ML Systems

claims:
  - slug: lora-preserves-quality-at-low-rank
    status: weakly_supported
    confidence: 0.6
    domain: NLP
```

---

## log.md format (append-only)

```markdown
## [2026-04-07] ingest | added papers/lora-low-rank-adaptation | updated: concepts/parameter-efficient-fine-tuning
## [2026-04-07] lint | report: 0 🔴, 2 🟡, 1 🔵
## [2026-04-08] daily-arxiv | 3 papers ingested from RSS
```

---

## Python Environment

Before running any Python tool, ensure the correct environment is active. Detection priority:

1. **Check for `.venv/`**: if present, prefix Bash commands with `source .venv/bin/activate &&`
2. **Check for conda**: if no venv but conda is active, use `conda run -n <env>` or confirm env is activated
3. **System Python**: if neither exists, use `python3` directly

**Example — calling a tool:**
```bash
# If .venv/ exists
source .venv/bin/activate && python3 tools/fetch_arxiv.py --hours 24

# If no venv
python3 tools/fetch_arxiv.py --hours 24
```

**Environment variables**: all Python tools auto-load API keys from `~/.env` and the project root `.env` via `tools/_env.py` — no manual `export` needed.

---

## Constraints

- **raw/ is read-only**: never modify files under `raw/`.
- **graph/ is auto-generated**: never manually edit files in `graph/` — only via `tools/research_wiki.py`.
- **Bidirectional links**: always write the reverse link when writing a forward link.
- **tex priority**: .tex > .pdf; fallback chain: tex fails → PDF parse, PDF fails → vision API.
- **index.md updated on every ingest**; log.md is append-only.
- **lint default is report-only**: `--fix` auto-fixes deterministic issues (xref backlinks, missing field defaults); `--suggest` outputs suggestions for non-deterministic issues; `--fix --dry-run` previews fixes.
- **Slug generation rule**: paper title keywords, hyphen-joined, all lowercase.
- **Importance scoring**: 1 = niche, 2 = useful, 3 = field-standard, 4 = influential, 5 = seminal.
- **Failed ideas must record reason**: `failure_reason` is anti-repetition memory — prevents re-exploring known dead ends.
- **Claim confidence range**: 0.0-1.0; re-evaluate every time evidence changes.
- **Experiments must link to a claim**: every experiment requires `target_claim`; results must be written back to the claim's evidence.
- **Experiment code goes in experiments/code/{slug}/**: `/exp-run` writes code to this path (`train.py`, `config.yaml`, `run.sh`, `requirements.txt`) — not to the project root or elsewhere.
- **DeepXiv token**: `DEEPXIV_TOKEN` env variable. If unset, the SDK auto-registers (writes to `~/.env`). Free tier: 10,000 requests/day. When DeepXiv is unavailable, all skills fall back to S2+RSS mode.

---

## Skills

| Skill | File | Trigger |
|-------|------|---------|
| `/setup` | `skills/setup/SKILL.md` | manual (first-time config) |
| `/init` | `skills/init/SKILL.md` | manual |
| `/ingest` | `skills/ingest/SKILL.md` | manual |
| `/ask` | `skills/ask/SKILL.md` | manual |
| `/edit` | `skills/edit/SKILL.md` | manual |
| `/check` | `skills/check/SKILL.md` | biweekly/manual |
| `/daily-arxiv` | `skills/daily-arxiv/SKILL.md` | cron 08:00 / manual |
| `/novelty` | `skills/novelty/SKILL.md` | manual |
| `/review` | `skills/review/SKILL.md` | manual |
| `/ideate` | `skills/ideate/SKILL.md` | manual |
| `/exp-design` | `skills/exp-design/SKILL.md` | manual |
| `/exp-run` | `skills/exp-run/SKILL.md` | manual (`<slug> [--collect] [--full] [--env local\|remote]`) |
| `/exp-status` | `skills/exp-status/SKILL.md` | manual (`[--pipeline <slug>] [--collect-ready] [--auto-advance]`) |
| `/exp-eval` | `skills/exp-eval/SKILL.md` | manual |
| `/refine` | `skills/refine/SKILL.md` | manual |
| `/paper-plan` | `skills/paper-plan/SKILL.md` | manual |
| `/paper-draft` | `skills/paper-draft/SKILL.md` | manual |
| `/paper-compile` | `skills/paper-compile/SKILL.md` | manual |
| `/survey` | `skills/survey/SKILL.md` | manual |
| `/research` | `skills/research/SKILL.md` | manual |
| `/rebuttal` | `skills/rebuttal/SKILL.md` | manual |
