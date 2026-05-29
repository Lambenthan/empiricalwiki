# Runtime Page Templates

> On-demand reference for full wiki page templates only. See `docs/runtime-support-files.en.md` for graph-derived files plus `index.md` and `log.md`.

## Page Types

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
paper_kind: empirical    # empirical | theory | both — routes ingest to /empirical-ingest vs /theory-ingest; treated as empirical when omitted
date_added: YYYY-MM-DD
source_type: tex         # tex | pdf
s2_id: ""
keywords: []
domain: ""               # empirical accounting / finance / management / economics
code_url: ""
cited_by: []
empirical:               # fill when paper_kind includes empirical
  sample_period: ""
  sample_scope: ""
  data_sources: []
  dependent_variables: []
  core_explanatory_variables: []
  mechanisms: []
  identification: ""
theory:                  # fill when paper_kind includes theory, otherwise omit the whole block
  model_class: ""        # e.g. signaling game / principal-agent / general equilibrium / DSGE / mechanism design
  solution_concept: ""   # e.g. perfect Bayesian equilibrium + intuitive criterion / subgame perfection / competitive equilibrium
  key_propositions: []   # list of propositions/ slugs
  predictions: []        # list of hypotheses/ slugs (testable implications the model yields)
---
```

Empirical body sections: `## Research Question` / `## Theory Mechanism` / `## Hypotheses` / `## Data and Sample` / `## Variable Design` / `## Model Specification` / `## Main Results` / `## Mechanism Tests` / `## Heterogeneity Tests` / `## Robustness Checks` / `## Endogeneity Handling` / `## Reproduction Notes` / `## Implications for My Project` / `## Related`

Theory body sections (`paper_kind: theory`): `## Research Question` / `## Model Environment` / `## Core Assumptions` / `## Solution Concept` / `## Propositions and Proofs` / `## Comparative Statics` / `## Testable Implications` / `## Implications for Empirics` / `## Related`

### variables/{slug}.md

```yaml
---
title: ""
slug: ""
construct: ""
role: other              # dependent | core_explanatory | mediator | moderator | control | instrument | fixed_effect | sample_filter | other
measurement: ""
data_sources: []
database_tables: []
frequency: ""
source_papers: []
available_in_project: false
project_paths: []
date_updated: YYYY-MM-DD
---
```

Body sections: `## Definition` / `## Measurement` / `## Data Source` / `## Literature Variants` / `## Construction Steps` / `## Stata Notes` / `## Caveats` / `## Related`

### datasets/{slug}.md

```yaml
---
title: ""
slug: ""
provider: ""
coverage: ""
unit: ""
fields: []
project_paths: []
source_papers: []
date_updated: YYYY-MM-DD
---
```

Body sections: `## Scope` / `## Fields` / `## Merge Keys` / `## Cleaning Rules` / `## Missingness` / `## Project Files` / `## Related Variables`

### models/{slug}.md

```yaml
---
title: ""
slug: ""
model_type: ""
dependent_variable: ""
core_variables: []
controls: []
fixed_effects: []
standard_errors: ""
sample: ""
source_papers: []
stata_template: ""
date_updated: YYYY-MM-DD
---
```

Body sections: `## Equation` / `## Identification Logic` / `## Variable Roles` / `## Fixed Effects and Standard Errors` / `## Expected Signs` / `## Stata Skeleton` / `## Interpretation Rules` / `## Related`

### mechanisms/{slug}.md

```yaml
---
title: ""
slug: ""
mechanism_type: ""
source_papers: []
variables: []
evidence: []
date_updated: YYYY-MM-DD
---
```

Body sections: `## Mechanism Statement` / `## Theoretical Logic` / `## Empirical Proxy` / `## Evidence Across Papers` / `## Boundary Conditions` / `## Open Questions`

### hypotheses/{slug}.md

```yaml
---
title: ""
slug: ""
status: proposed          # proposed | literature_supported | tested | rejected
mechanism: ""
expected_sign: ""
source_papers: []
date_updated: YYYY-MM-DD
---
```

Body sections: `## Hypothesis` / `## Literature Basis` / `## Testable Model` / `## Evidence` / `## Risks`

### identification/{slug}.md

```yaml
---
title: ""
slug: ""
strategy_type: other
source_papers: []
assumptions: []
threats: []
implementation_notes: ""
date_updated: YYYY-MM-DD
---
```

Body sections: `## Identification Problem` / `## Strategy` / `## Key Assumptions` / `## Implementation` / `## Diagnostics` / `## Limitations`

### robustness/{slug}.md

```yaml
---
title: ""
slug: ""
check_type: other
purpose: ""
source_papers: []
implementation_notes: ""
date_updated: YYYY-MM-DD
---
```

Body sections: `## Purpose` / `## When To Use` / `## Implementation` / `## Expected Table Pattern` / `## Interpretation` / `## Caveats`

### heterogeneity/{slug}.md

```yaml
---
title: ""
slug: ""
grouping_variable: ""
grouping_rule: ""
rationale: ""
source_papers: []
date_updated: YYYY-MM-DD
---
```

Body sections: `## Grouping Logic` / `## Theoretical Rationale` / `## Sample Split` / `## Model` / `## Interpretation` / `## Related`

### tables/{slug}.md

```yaml
---
title: ""
slug: ""
table_type: ""
source_paper: ""
variables: []
model: ""
interpretation: ""
date_updated: YYYY-MM-DD
---
```

Body sections: `## Table Purpose` / `## Columns` / `## Key Coefficients` / `## Interpretation` / `## Reproduction Notes` / `## Caveats`

### assumptions/{slug}.md

Model primitives of a theory paper: players, preferences/payoffs, information structure, timing, technology/constraints. `formal_statement` must quote the original setup verbatim — never paraphrase the conditions.

```yaml
---
title: ""
slug: ""
assumption_type: other   # information | timing | payoff | agent_behavior | technology | constraint | other
formal_statement: ""     # verbatim quote of the original setup
source_papers: []
relaxed_in: []           # which paper/section relaxes or generalizes this assumption
date_updated: YYYY-MM-DD
---
```

Body sections: `## Statement` / `## Role in Model` / `## Why It Matters` / `## Variants Across Papers` / `## Related`

### propositions/{slug}.md

Formal results of a theory paper: propositions/theorems/lemmas. `claims/` holds confidence-weighted empirical assertions; `propositions/` holds proven formal results — different semantics, do not mix. Quote `formal_statement` verbatim and state `conditions` explicitly.

```yaml
---
title: ""
slug: ""
proposition_type: other  # existence | characterization | comparative_statics | welfare | uniqueness | efficiency | other
formal_statement: ""     # verbatim quote of the proposition/theorem
conditions: ""           # conditions for the result to hold, e.g. "c ≤ c_s"
proof_technique: ""      # e.g. backward induction / fixed point / intuitive-criterion construction / counterexample; write "未报告" if not found
source_papers: []
predicts: []             # list of hypotheses/ slugs this result yields
date_updated: YYYY-MM-DD
---
```

Body sections: `## Statement` / `## Conditions` / `## Proof Sketch` / `## Comparative Statics` / `## Testable Implications` / `## Related`

### concepts/{concept-name}.md

```yaml
---
title: ""
aliases: []
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

### foundations/{slug}.md

```yaml
---
title: ""
slug: ""
domain: ""
status: mainstream       # mainstream | historical
aliases: []
first_introduced: ""
date_updated: YYYY-MM-DD
source_url: ""
---
```

Body sections: `## Definition` / `## Intuition` / `## Formal notation` / `## Key variants` / `## Known limitations` / `## Open problems` / `## Relevance to active research`

Foundations have **no outward link fields**. Other pages may link to a foundation; foundations write no reverse link.

### ideas/{idea-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed          # proposed | in_progress | tested | validated | failed
origin: ""
origin_gaps: []
tags: []
domain: ""
priority: 3               # 1-5
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: YYYY-MM-DD
date_resolved: ""
---
```

Body sections: `## Motivation` / `## Hypothesis` / `## Approach sketch` / `## Expected outcome` / `## Risks` / `## Pilot results` / `## Lessons learned`

### experiments/{experiment-slug}.md

```yaml
---
title: ""
slug: ""
status: planned           # planned | running | completed | abandoned
target_claim: ""
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
outcome: ""               # succeeded | failed | inconclusive
key_result: ""
linked_idea: ""
date_planned: YYYY-MM-DD
date_completed: ""
run_log: ""
started: ""
estimated_hours: 0
remote:
  server: ""
  gpu: ""
  session: ""
  started: ""
  completed: ""
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
domain: ""
source_papers: []
evidence:
  - source: ""
    type: supports        # supports | contradicts | tested_by | invalidates
    strength: moderate    # weak | moderate | strong
    detail: ""
conditions: ""
date_proposed: YYYY-MM-DD
date_updated: YYYY-MM-DD
---
```

Body sections: `## Statement` / `## Evidence summary` / `## Conditions and scope` / `## Counter-evidence` / `## Linked ideas` / `## Open questions`
