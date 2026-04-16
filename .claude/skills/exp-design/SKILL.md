---
description: Claim-driven experiment design — scope target claims → design experiment blocks (baseline/validation/ablation/robustness) → build run order → optional Review LLM review → write to wiki
argument-hint: <idea-slug-or-hypothesis> [--review] [--budget <gpu-hours>]
---

# /exp-design

> Given an idea (or a free-text hypothesis), design a complete experiment plan.
> Claims are the core: scope the claims to validate across three dimensions — Target, Decomposition, and Threats.
> Design four types of experiment blocks: baseline (reproduce baseline), validation (core verification), ablation (factor isolation), and robustness (stress testing).
> Experiments are ordered by dependency with decision gates between stages (sanity fail → early stop).
> Optional Review LLM review checks experiment plan completeness. All experiments are written to wiki/experiments/ with graph edges.

## Inputs

- `idea`: one of:
  - A slug from wiki/ideas/ (e.g. `sparse-lora-for-edge-devices`)
  - A free-text hypothesis description (provide the experiment goal directly)
- `--review` (optional): enable Review LLM review to check experiment plan completeness
- `--budget <gpu-hours>` (optional): total compute budget cap (GPU hours), affects robustness experiment scope

## Outputs

- `wiki/experiments/{slug}.md` — one page per experiment block (status: planned)
- `wiki/graph/edges.jsonl` — new tested_by edges: experiment → claim
- `wiki/ideas/{slug}.md` — updated linked_experiments field
- `wiki/graph/context_brief.md` — rebuilt
- `wiki/graph/open_questions.md` — rebuilt
- `wiki/log.md` — appended log entry
- **EXPERIMENT_PLAN_REPORT** (printed to terminal) — experiment block summary, run order, compute budget

## Wiki Interaction

### Reads
- `wiki/ideas/{slug}.md` — idea's hypothesis, approach, risks, origin_gaps
- `wiki/claims/*.md` — target claims' current status, existing evidence, confidence
- `wiki/experiments/*.md` — existing experiments (avoid duplicate designs, reference setup configs)
- `wiki/papers/*.md` — related papers' baselines and experiment setups
- `wiki/concepts/*.md` — relevant technical concepts (guide experiment design)
- `wiki/graph/context_brief.md` — global context
- `wiki/graph/open_questions.md` — knowledge gaps (guide experiment priority)

### Writes
- `wiki/experiments/{slug}.md` — create experiment pages (one per experiment block)
- `wiki/ideas/{slug}.md` — update linked_experiments field
- `wiki/graph/edges.jsonl` — add tested_by edges
- `wiki/graph/context_brief.md` — rebuild
- `wiki/graph/open_questions.md` — rebuild
- `wiki/log.md` — append operation log

### Graph edges created
- `tested_by`: claim → experiment (the claim is validated by this experiment)

## Workflow

**Precondition**: confirm working directory is the wiki project root (directory containing `wiki/`, `raw/`, `tools/`).

### Step 1: Load Context

1. **Parse idea input**:
   - If slug: read `wiki/ideas/{slug}.md`, extract `## Motivation`, `## Hypothesis`, `## Approach sketch`, `## Risks`, and the frontmatter fields `origin_gaps`, `tags`, `domain`, `priority` (per CLAUDE.md ideas template)
   - If free text: use directly as the hypothesis description
2. **Load relevant wiki context**:
   - Read `wiki/graph/context_brief.md` (global context)
   - Read `wiki/graph/open_questions.md` (knowledge gaps)
   - From the idea's `origin_gaps`, read the corresponding `wiki/claims/*.md` (target claims)
   - From each target claim's `source_papers` field, read the corresponding `wiki/papers/*.md` for baseline setups and prior experiment protocols — this is the canonical path from idea → claim → paper (ideas do **not** carry a `linked_papers` field; use `origin_gaps` → `source_papers` instead)
   - Read existing `wiki/experiments/*.md` to check for similar experiments
3. **If idea has no origin_gaps**: extract implied claims from the hypothesis description; search wiki/claims/ or flag as needing new claim creation

### Step 2: Scope Claims

Scope the claims for this experiment plan across three dimensions. For each dimension, search wiki/claims/ for existing claims first; if none exist, create a new claim (status: proposed, confidence: 0.3).

1. **Target** (what to validate):
   - The claim corresponding to the idea's core hypothesis — the primary target this experiment plan directly validates
   - Typically 1, at most 2
2. **Decomposition** (what to decompose):
   - Individual contribution claims for each independent factor in the method
   - One claim per factor, used to design isolation experiments
3. **Threats** (what could falsify us):
   - Known risks, alternative explanations, boundary conditions
   - Sources: counter-evidence in wiki, paper limitations, open questions in claims
   - Guides robustness experiment design

Output: scoped claims list (slug list + dimension annotation + current status/confidence for each claim)

### Step 3: Design Experiment Blocks

Design experiment blocks for each scoped claim. Four types:

**A. Baseline experiments (reproduce baseline)**:
- Purpose: confirm the problem exists and the baseline is reproducible
- Reproduce the core experiment from the most relevant paper
- Success criterion: baseline results deviate < 5% from reported paper values (this threshold is the same one used by the Stage 1 decision gate below — do not introduce a different number elsewhere)
- Compute: typically minimal

**B. Validation experiments (validate Target claim)**:
- Purpose: validate the core contribution on top of the baseline
- Metrics: statistically significant improvement over baseline
- Requires sufficient seed/run count for reliability (recommend >= 3 seeds)
- Compute: moderate

**C. Ablation experiments (validate Decomposition claims)**:
- Purpose: isolate the contribution of each independent factor
- Each ablation removes one factor and validates the resulting performance drop
- N factors → N ablation experiments
- Compute: similar to validation × N

**D. Robustness experiments (rule out Threats)**:
- Purpose: rule out known risks and alternative explanations; verify the method holds under varied conditions
- Variation dimensions: model size, dataset, hyperparameters, domain
- Test at least 2 variation dimensions
- Compute: depends on --budget

Each experiment block includes:
- `title`: descriptive title
- `target_claim`: corresponding claim slug
- `hypothesis`: specific hypothesis the experiment tests
- `type`: baseline / validation / ablation / robustness
- `setup`: model, dataset, hardware, framework
- `metrics`: list of evaluation metrics
- `baseline`: comparison baseline
- `success_criterion`: explicit pass/fail criterion
- `estimated_gpu_hours`: estimated compute time
- `seeds`: number of random seeds (recommend >= 3)

### Step 4: Build Run Order

Sort experiments by dependency and set decision gates:

```
Stage 0: Sanity check
  └── Small-scale run (1 epoch / 100 steps) to verify no code bugs, data loads, GPU available, loss decreasing
  └── Gate: sanity fails → stop, fix code

Stage 1: Baseline (reproduce baseline)
  └── Reproduce baseline results
  └── Gate: baseline deviation > 5% → stop, check implementation (same threshold as Step 3 success criterion)

Stage 2: Validation (core verification)
  └── Validate core method on top of baseline
  └── Gate: no improvement → stop, analyze reason (idea may not hold)

Stage 3: Ablation (factor isolation)
  └── Multiple ablations can run in parallel
  └── Gate: if a factor ablation shows no effect → record it, but continue other ablations

Stage 4: Robustness (robustness verification)
  └── Only execute after Stage 2 succeeds
  └── Scope determined by remaining --budget
```

Output:
- Ordered experiment list (with dependencies)
- Decision gate conditions for each stage
- Total compute budget estimate (if exceeding --budget, adjust Stage 4 scope)

### Step 5: Optional Review LLM Review (--review)

If `--review` is specified:

```
mcp__llm-review__chat:
  system: "You are a senior ML researcher reviewing an experiment plan.
           Focus on: missing baselines, missing ablations, unfair comparisons,
           statistical rigor (enough seeds?), and dataset selection.
           For every issue found, suggest a concrete fix."
  message: |
    ## Experiment Plan
    {complete experiment plan: claims, blocks, run order, budgets}

    ## Context
    {target claims with current status, related papers' experiment setups}

    ## Review Questions
    1. Are any critical experiments missing?
    2. Are the baselines fair and comprehensive?
    3. Is the ablation design sufficient to isolate each contribution?
    4. Are the success criteria well-defined and reasonable?
    5. Any statistical concerns (sample size, variance, seeds)?
```

Revise the experiment plan based on Review LLM feedback (add missing experiments, correct unreasonable criteria).

### Step 6: Write to Wiki

1. **Create experiment pages**:
   For each experiment block:
   ```bash
   python3 tools/research_wiki.py slug "<experiment-title>"
   ```
   Create `wiki/experiments/{slug}.md`:
   Create `wiki/experiments/{slug}.md` following the **CLAUDE.md experiments template exactly** — every field below must be present even if empty, because `/exp-run` later uses `tools/research_wiki.py set-meta` to update them, and `set-meta` refuses to create fields that don't already exist in the frontmatter (it only updates existing keys):
   ```yaml
   ---
   title: ""
   slug: ""
   status: planned
   target_claim: ""          # claim slug
   hypothesis: ""
   tags: []
   domain: ""
   setup:
     model: ""
     dataset: ""
     hardware: ""
     framework: ""
   metrics: []
   baseline: ""
   outcome: ""                # empty until /exp-run Phase 4 — succeeded | failed | inconclusive
   key_result: ""             # empty until /exp-run Phase 4
   linked_idea: "{idea-slug}" # MANDATORY: the source idea slug (reverse link to wiki/ideas/{idea-slug}.md linked_experiments)
   date_planned: YYYY-MM-DD
   date_completed: ""         # empty until /exp-run Phase 4
   run_log: ""                # empty until /exp-run Phase 2
   started: ""                # empty until /exp-run Phase 2 (ISO timestamp, set via set-meta)
   estimated_hours: 0         # 0 until /exp-run Phase 2 (set via set-meta)
   remote:                    # full block must exist so /exp-run --env remote can populate sub-fields via Edit
     server: ""
     gpu: ""
     session: ""
     started: ""
     completed: ""
   ---

   ## Objective
   {what this experiment proves}

   ## Setup
   {detailed setup: model, dataset, hardware, hyperparameters}

   ## Procedure
   {step-by-step execution plan}

   ## Results
   (to be filled after /exp-run)

   ## Analysis
   (to be filled after /exp-run)

   ## Claim updates
   (to be filled after /exp-eval)

   ## Follow-up
   {contingency plans: what to do if success / failure}
   ```

2. **Create new claims (if missing claims were identified in Step 2)**:
   ```bash
   python3 tools/research_wiki.py slug "<claim-title>"
   ```
   Create `wiki/claims/{slug}.md` (status: proposed, confidence: 0.3)

3. **Add graph edges**:
   ```bash
   # For each experiment → target claim
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "claims/{target-claim}" --to "experiments/{slug}" \
     --type tested_by --evidence "Designed by /exp-design"
   ```

4. **Update idea page** (if idea came from wiki):
   - Append all new experiment slugs to `linked_experiments` in `wiki/ideas/{idea-slug}.md`
   - If idea status is `proposed`, update to `in_progress`

5. **Update index.md**: append entries under the experiments and claims (if new) categories

6. **Rebuild derived data**:
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

7. **Append log**:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-design | {N} experiments designed for idea {slug} | claims: {claim-list}"
   ```

8. **Print EXPERIMENT_PLAN_REPORT to terminal**:
   ```markdown
   # Experiment Plan Report

   ## Target Idea
   - Idea: [[idea-slug]]
   - Hypothesis: {hypothesis}

   ## Scoped Claims
   | Claim | Current status | Confidence | Dimension |
   |-------|---------------|------------|-----------|
   | [[claim-slug]] | proposed | 0.3 | target |
   | [[claim-slug]] | weakly_supported | 0.5 | decomposition |

   ## Experiment Blocks
   | # | Experiment | Type | Claim | GPU-hrs | Stage |
   |---|-----------|------|-------|---------|-------|
   | 1 | [[baseline-slug]] | baseline | — | 2 | 1 |
   | 2 | [[validation-slug]] | validation | target | 8 | 2 |
   | 3 | [[ablation-1-slug]] | ablation | decomposition-1 | 8 | 3 |
   | 4 | [[robustness-slug]] | robustness | target | 16 | 4 |

   ## Run Order
   Stage 0: Sanity → Stage 1: Baseline → Stage 2: Validation → Stage 3: Ablation → Stage 4: Robustness
   Decision gates at each stage boundary.

   ## Budget
   - Total estimated: {N} GPU-hours
   - Budget limit: {--budget or "unlimited"}

   ## Next Steps
   - Run `/exp-run [[baseline-slug]]` to start Stage 1
   - After each stage, run `/exp-eval` to update wiki
   ```

## Constraints

- **Every experiment must be linked to a claim**: `target_claim` cannot be empty (baseline experiments may link to the Target claim)
- **No duplicate experiments**: before creating, check wiki/experiments/ for existing experiments with the same target_claim + hypothesis
- **Scoped claims are not modified**: claims scoped in Step 2 are not updated for status/confidence during this plan — only /exp-eval may update them
- **Success criteria must be quantified**: each experiment block's success criterion must include a specific number (e.g. "> 2% accuracy improvement")
- **At least 3 seeds**: experiments requiring statistical reliability (validation, ablation) must specify >= 3 random seeds
- **Graph edges via tools/research_wiki.py**: do not manually edit edges.jsonl
- **Idea status advances only forward**: proposed → in_progress, irreversible
- **Slug uniqueness**: check for existing slug before creating

## Error Handling

- **Idea not found**: prompt user to check slug, list candidates in wiki/ideas/
- **Target claim does not exist**: auto-create new claim page (status: proposed, confidence: 0.3), flag in report
- **Similar experiment already exists**: list existing experiments, ask user whether to add or skip
- **Review LLM unavailable** (--review mode): skip Step 5, note "unreviewed — Review LLM unavailable" in report
- **Budget insufficient**: reduce Stage 4 robustness experiment scope, note actual budget allocation in report
- **Slug conflict**: append numeric suffix (e.g. `sparse-lora-ablation-v2`)
- **Wiki is empty**: proceed normally but baseline experiments have no prior results to reference; recommend running /ingest for relevant papers first

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — generate slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — add graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — rebuild gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log

### MCP Servers
- `mcp__llm-review__chat` — Step 5 experiment plan review (optional)

### Claude Code Native
- `Read` — read wiki pages
- `Glob` — find existing experiments and claims

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Step 5 Review LLM review independence (if enabled)

### Called by
- `/research` Stage 2 (experiment design stage)
- User directly
