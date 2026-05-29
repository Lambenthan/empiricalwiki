---
description: Ingest a theory-modeling paper into the wiki: paper card plus assumptions/primitives, propositions/theorems, solution concept, and testable implications, bridged to the empirical layer on one shared graph
argument-hint: "<local-pdf-or-tex-path> [--topic <research-topic>]"
---

# /theory-ingest

> Convert one theory-modeling paper into reusable research assets. Extract along the 6 fixed slots of the theory-modeling skeleton: environment/primitives, solution concept, results, proofs, comparative statics, testable implications. Quote formal statements verbatim; never paraphrase.

## Inputs

- `source`: local `.pdf`, `.tex`, or an `/init`-prepared `raw/tmp/...` path.
- `--topic` (optional): current project topic, e.g. "managerial myopia and patient capital".

## Outputs

- `wiki/papers/{slug}.md` (`paper_kind: theory`)
- created or updated as needed:
  - `wiki/assumptions/*.md`
  - `wiki/propositions/*.md`
  - `wiki/hypotheses/*.md` (testable implications the model yields)
  - `wiki/mechanisms/*.md` (fill `## Theoretical Logic`; shared with the empirical layer)
  - `wiki/foundations/*.md` (reusable canonical knowledge: solution concepts, proof frameworks)
- `wiki/index.md`, `wiki/log.md`
- `wiki/graph/edges.jsonl`

## Workflow

### Step 1: Resolve Source

Confirm the cwd is the project root containing `wiki/`, `raw/`, and `tools/`.

Prefer `.venv`:

```bash
if [ -x .venv/bin/python ]; then PYTHON_BIN=.venv/bin/python; else PYTHON_BIN=python3; fi
```

Theory papers are formula-dense, so **`.tex` is strongly preferred**: use the source when available so equations survive. With a PDF only, read the first page for the title:

```bash
"$PYTHON_BIN" - "<source>" <<'PY'
import sys, fitz
doc = fitz.open(sys.argv[1])
print(doc[0].get_text("text")[:2000])
PY
```

Then run:

```bash
"$PYTHON_BIN" tools/prepare_paper_source.py --raw-root raw --source <source> --title "<confident-title>"
```

Use the returned `prepared_path` as the reading entrypoint.

### Step 2: Extract Along the 6-Slot Skeleton

Open `docs/runtime-theory-skeleton.en.md` first and extract against the 6 fixed slots. Write "未报告" (not reported) when there is no explicit evidence; do not guess:

1. **Environment / primitives**: players, action/strategy spaces, preferences/payoffs, information structure, timing, technology/constraints
2. **Solution concept**: equilibrium notion (Nash / subgame perfect / perfect Bayesian / competitive equilibrium ...)
3. **Results**: the formal statement and conditions of each proposition/theorem/lemma
4. **Proofs**: the proof technique behind each result
5. **Comparative statics**: how endogenous variables move with parameters
6. **Testable implications**: sign predictions the model yields that can be taken to data

**Theory papers have no variables/datasets/identification/robustness — those blocks do not exist, they are not "未报告". This is the fundamental fork from `/empirical-ingest`.**

### Step 3: Write Pages

Open `docs/runtime-page-templates.en.md` and write pages by the templates.

Set `paper_kind: theory` on `papers/{slug}.md`, fill the `theory` block, and use the theory body sections:

```markdown
## Research Question
## Model Environment
## Core Assumptions
## Solution Concept
## Propositions and Proofs
## Comparative Statics
## Testable Implications
## Implications for Empirics
## Related
```

- Each core assumption → `assumptions/`, with `formal_statement` quoted **verbatim**
- Each proposition/theorem → `propositions/`, `formal_statement` verbatim, `conditions` explicit, `proof_technique` filled (write "未报告" if not found)
- Each testable implication → `hypotheses/` (`status: literature_supported`)
- The economic mechanism the model formalizes → after dedup, update an existing `mechanisms/` page's `## Theoretical Logic`; do not create a near-duplicate of an empirical mechanism page
- Solution concepts and proof frameworks (reusable canonical knowledge) → `foundations/` (terminal nodes, no reverse links)

Dedup before creating anything:

```bash
"$PYTHON_BIN" tools/research_wiki.py slug "<title>"
```

### Step 4: Add Graph Edges

Use the tool; never hand-edit `wiki/graph/edges.jsonl`:

```bash
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to assumptions/<a> --type assumes --evidence "<location in text>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to propositions/<p> --type proves --evidence "<proposition number>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to mechanisms/<m> --type formalizes_mechanism --confidence high --evidence "<evidence>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from propositions/<p> --to hypotheses/<h> --type predicts --confidence high --evidence "<evidence>"
```

- `assumes`, `proves`: structural facts, **no** `--confidence`
- `formalizes_mechanism`, `predicts`: judgments, **must** carry `--confidence high|medium|low`
- `derived_from` (paper → foundation) as needed
- When an empirical paper tests this theory's implications, its `tests_hypothesis` / `tests_mechanism` reverse edges are written by `/empirical-ingest`; this skill only writes the theory-side forward edges and keeps bidirectional links in sync

### Step 5: Rebuild and Report

```bash
"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki
"$PYTHON_BIN" tools/lint.py --wiki-dir wiki
```

Then report:

- which pages were created/updated (grouped by the 6 slots)
- whether the extracted testable implications already bridge to existing empirical papers/mechanisms
- which propositions or mechanisms can serve the current project

## Constraints

- **Quote formal statements verbatim; never paraphrase**: the conditions of a proposition or assumption must not be altered (turning "for all concave utility functions" into "for utility functions" is a disaster).
- Never fabricate proof techniques, parameter signs, or equilibrium results; write "未报告" when not found.
- `propositions/` holds proven formal results; do not mix with `claims/` (confidence-weighted empirical assertions).
- `mechanisms/` and `hypotheses/` are shared with the empirical layer: dedup first, prefer updating the theory side of an existing page, do not spawn near-duplicates.
- Pure computational/simulation (agent-based) models are experiment-like; route them to `experiments/`, not `propositions/`.
- `.tex` priority. `raw/papers/` is user input — never overwrite or move it.
- A theory paper with no arXiv/S2 metadata is not a failure; rely on the body text.
