# 运行时页面模板

> 仅按需读取的 wiki 页面模板。graph 派生文件以及 `index.md`、`log.md` 请看 `docs/runtime-support-files.zh.md`。

## 页面类型

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
domain: ""
code_url: ""
cited_by: []
empirical:
  sample_period: ""
  sample_scope: ""
  data_sources: []
  dependent_variables: []
  core_explanatory_variables: []
  mechanisms: []
  identification: ""
---
```

正文：`## 研究问题` / `## 理论机制` / `## 研究假设` / `## 数据与样本` / `## 变量设定` / `## 模型设定` / `## 主要结果` / `## 机制检验` / `## 异质性检验` / `## 稳健性检验` / `## 内生性处理` / `## 可复现线索` / `## 对我当前选题的启发` / `## Related`

### variables/{slug}.md

```yaml
---
title: ""
slug: ""
construct: ""            # 理论构念，如耐心资本、ESG、管理者短视
role: other              # dependent | core_explanatory | mediator | moderator | control | instrument | fixed_effect | sample_filter | other
measurement: ""          # 操作化定义或公式
data_sources: []
database_tables: []
frequency: ""            # annual | quarterly | firm-year 等
source_papers: []
available_in_project: false
project_paths: []
date_updated: YYYY-MM-DD
---
```

正文：`## Definition` / `## Measurement` / `## Data Source` / `## Literature Variants` / `## Construction Steps` / `## Stata Notes` / `## Caveats` / `## Related`

### datasets/{slug}.md

```yaml
---
title: ""
slug: ""
provider: ""             # CSMAR / Wind / WRDS / 手工整理 / 外购数据
coverage: ""             # 年份、市场、行业、样本范围
unit: ""                 # firm-year / firm-quarter / individual 等
fields: []
project_paths: []
source_papers: []
date_updated: YYYY-MM-DD
---
```

正文：`## Scope` / `## Fields` / `## Merge Keys` / `## Cleaning Rules` / `## Missingness` / `## Project Files` / `## Related Variables`

### models/{slug}.md

```yaml
---
title: ""
slug: ""
model_type: ""           # baseline / mechanism / heterogeneity / robustness / endogeneity
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

正文：`## Equation` / `## Identification Logic` / `## Variable Roles` / `## Fixed Effects and Standard Errors` / `## Expected Signs` / `## Stata Skeleton` / `## Interpretation Rules` / `## Related`

### mechanisms/{slug}.md

```yaml
---
title: ""
slug: ""
mechanism_type: ""       # financing / governance / innovation / information / risk / other
source_papers: []
variables: []
evidence: []
date_updated: YYYY-MM-DD
---
```

正文：`## Mechanism Statement` / `## Theoretical Logic` / `## Empirical Proxy` / `## Evidence Across Papers` / `## Boundary Conditions` / `## Open Questions`

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

正文：`## Hypothesis` / `## Literature Basis` / `## Testable Model` / `## Evidence` / `## Risks`

### identification/{slug}.md

```yaml
---
title: ""
slug: ""
strategy_type: other      # ols | fixed_effects | did | iv | psm | rd | heckman | event_study | system_gmm | text_analysis | machine_learning | other
source_papers: []
assumptions: []
threats: []
implementation_notes: ""
date_updated: YYYY-MM-DD
---
```

正文：`## Identification Problem` / `## Strategy` / `## Key Assumptions` / `## Implementation` / `## Diagnostics` / `## Limitations`

### robustness/{slug}.md

```yaml
---
title: ""
slug: ""
check_type: other         # alternative_variable | alternative_sample | alternative_model | winsorization | lagged_variable | placebo | psm | iv | fixed_effects | cluster_se | other
purpose: ""
source_papers: []
implementation_notes: ""
date_updated: YYYY-MM-DD
---
```

正文：`## Purpose` / `## When To Use` / `## Implementation` / `## Expected Table Pattern` / `## Interpretation` / `## Caveats`

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

正文：`## Grouping Logic` / `## Theoretical Rationale` / `## Sample Split` / `## Model` / `## Interpretation` / `## Related`

### tables/{slug}.md

```yaml
---
title: ""
slug: ""
table_type: ""           # descriptive | correlation | baseline | mechanism | heterogeneity | robustness | endogeneity
source_paper: ""
variables: []
model: ""
interpretation: ""
date_updated: YYYY-MM-DD
---
```

正文：`## Table Purpose` / `## Columns` / `## Key Coefficients` / `## Interpretation` / `## Reproduction Notes` / `## Caveats`

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

正文：`## Definition` / `## Intuition` / `## Formal notation` / `## Variants` / `## Comparison` / `## When to use` / `## Known limitations` / `## Open problems` / `## Key papers` / `## My understanding`

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

正文：`## Overview` / `## Timeline` / `## Seminal works` / `## SOTA tracker` / `## Open problems` / `## My position` / `## Research gaps` / `## Key people`

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

正文：`## Research areas` / `## Key papers` / `## Recent work` / `## Collaborators` / `## My notes`

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

正文：`## Overview` / `## Core areas` / `## Evolution` / `## Current frontiers` / `## Key references` / `## Related`

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

正文：`## Definition` / `## Intuition` / `## Formal notation` / `## Key variants` / `## Known limitations` / `## Open problems` / `## Relevance to active research`

Foundations **没有外向链接字段**。其他页面可链接到 foundation；foundation 不写反向链接。

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

正文：`## Motivation` / `## Hypothesis` / `## Approach sketch` / `## Expected outcome` / `## Risks` / `## Pilot results` / `## Lessons learned`

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

正文：`## Objective` / `## Setup` / `## Procedure` / `## Results` / `## Analysis` / `## Claim updates` / `## Follow-up`

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

正文：`## Statement` / `## Evidence summary` / `## Conditions and scope` / `## Counter-evidence` / `## Linked ideas` / `## Open questions`
