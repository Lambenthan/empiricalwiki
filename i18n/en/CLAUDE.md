# ΩmegaWiki — Runtime Schema

> CS/AI ΩmegaWiki. Powered by Claude Code.
> This file is the wiki's runtime entry point: defines page structure, link conventions, and workflow constraints.

> **Maintenance note**: Managed under `i18n/`. Edit `i18n/en/CLAUDE.md` (not the active copy at the root). Run `./setup.sh --lang <current>` to sync.

---

## Repository Layout

Open `docs/runtime-directory-structure.en.md` only when you need the full repo tree.

Keep this mental map in immediate context:

### `wiki/` is the main product surface

- `wiki/index.md` is the catalog of all wiki pages
- `wiki/log.md` is the append-only activity log
- `wiki/papers/` holds paper summaries
- `wiki/concepts/`, `wiki/topics/`, and `wiki/foundations/` hold reusable knowledge structure
- `wiki/people/`, `wiki/ideas/`, `wiki/experiments/`, and `wiki/claims/` hold research actors, hypotheses, tests, and assertions
- `wiki/Summary/` holds area-level syntheses
- `wiki/outputs/` holds generated artifacts
- `wiki/graph/` is derived state; do not edit it manually

### Formatting guardrail

- Open `docs/runtime-page-templates.en.md` before drafting or repairing wiki page structure, YAML, or body sections
- Open `docs/runtime-support-files.en.md` when you need graph-derived file details or `index.md` / `log.md` format

### `raw/` and `config/`

- `raw/papers/`, `raw/notes/`, and `raw/web/` are user-owned inputs
- `raw/discovered/` stores externally fetched papers from `/init` and `/daily-arxiv`
- `raw/tmp/` stores `/init`-generated prepared local sidecars
- `config/` holds environment and remote-server templates

---

## 9 Page Types

`papers`, `concepts`, `topics`, `people`, `ideas`, `experiments`, `claims`, `Summary`, `foundations`.

Open `docs/runtime-page-templates.en.md` for page templates and `docs/runtime-support-files.en.md` for graph/index/log references.

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
| any page links to `[[foundation-X]]` | **no reverse link** — foundations are terminal: they receive inward links from papers/concepts/etc. but never write `key_papers` or any back-reference field |

---

## Graph Rules

- `graph/` is auto-generated; do not edit it manually
- core derived files are `edges.jsonl`, `context_brief.md`, and `open_questions.md`
- valid edge types are `extends`, `contradicts`, `supports`, `inspired_by`, `tested_by`, `invalidates`, `supersedes`, `addresses_gap`, and `derived_from`
- use `tools/research_wiki.py add-edge`, `rebuild-context-brief`, and `rebuild-open-questions`

## log.md Format

Standard log line:

```markdown
## [YYYY-MM-DD] skill | details
```

---

## Python Environment

- prefer `.venv/bin/python` (Unix/macOS) or `.venv/Scripts/python.exe` (Windows) when `.venv/` exists
- otherwise use the active conda env if present
- otherwise fall back to `python3` (Unix/macOS) or `python` (Windows)
- Python tools auto-load API keys from `~/.env` and project-root `.env` via `tools/_env.py`

---

## Constraints

- **`raw/papers/`, `raw/notes/`, `raw/web/` are user-owned**: treat them as authoritative inputs. `/init` and `/daily-arxiv` may add externally fetched papers only under `raw/discovered/`, and only `/init` may add generated prepared local sidecars under `raw/tmp/` (additions only — never overwrite an existing user-owned file). `/edit` may add raw sources only when the user explicitly asked for it. All other skills, tools, and `/init` subagents running `/ingest` in INIT MODE treat `raw/` as strictly read-only.
- **User-facing skill parameters are user-owned**: flags and values shown in a skill's `argument-hint` belong to the user's command, not to agent strategy. Do not invent, flip, or drop those parameters from repository state alone. If the user omitted a parameter, only use a default or derived value when that skill explicitly documents omission behavior; otherwise leave it unset or ask the user. Internal derived settings that are not user-facing parameters may still be inferred by the skill.
- **INIT MODE handoff is manifest-driven**: when `/init` writes `.checkpoints/init-sources.json`, that manifest becomes the single source of truth for ingest order and canonical source paths. Prepared local inputs should point to `raw/tmp/`; introduced external papers should point to `raw/discovered/`.
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
| `/reset` | `skills/reset/SKILL.md` | manual (`--scope wiki\|raw\|log\|checkpoints\|all`) |
| `/init` | `skills/init/SKILL.md` | manual |
| `/prefill` | `skills/prefill/SKILL.md` | manual (`[domain] [--add concept]`) |
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
