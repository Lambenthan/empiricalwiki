# ΩmegaWiki — Runtime Schema

> CS/AI ΩmegaWiki. 由 Claude Code 驱动。
> 本文件是 wiki 的运行时入口，定义页面结构、链接规范、workflow 约束。

---

## 目录结构

```
wiki/
├── CLAUDE.md          ← 本文件
├── index.md           ← 内容目录（YAML）
├── log.md             ← 时序日志（append-only）
├── papers/            ← 论文结构化摘要
├── concepts/          ← 技术概念综述
├── topics/            ← 研究方向地图
├── people/            ← 研究者追踪
├── ideas/             ← 研究想法（带生命周期状态）
├── experiments/       ← 实验记录（wiki 页面）
├── claims/            ← 可验证的研究断言
├── Summary/           ← 领域全景综述
├── foundations/       ← 领域基础知识（终端：只接受入链，不写出链）
├── outputs/           ← 生成物（Related Work, 论文草稿）
└── graph/             ← 自动生成（勿手动编辑）
    ├── edges.jsonl    ← 类型化关系图谱
    ├── context_brief.md  ← 压缩上下文（≤8000字符）
    └── open_questions.md     ← 开放问题与知识缺口

raw/
├── papers/            ← .tex / .pdf（只读）
├── notes/             ← .md 笔记（只读）
└── web/               ← HTML / Markdown（只读）

config/
├── server.yaml        ← 远程 GPU 服务器配置（可选，/exp-run --env remote 时需要）
├── server.yaml.example
├── .env.example
└── settings.local.json.example
```

---

## 9 类页面

| 目录 | 文件名 | 职责 |
|------|--------|------|
| `papers/` | `{slug}.md` | 论文结构化摘要 |
| `concepts/` | `{concept-name}.md` | 跨论文技术概念综述 |
| `topics/` | `{topic-name}.md` | 研究方向地图 |
| `people/` | `{firstname-lastname}.md` | 研究者追踪 |
| `ideas/` | `{idea-slug}.md` | 研究想法（proposed → tested → validated/failed） |
| `experiments/` | `{experiment-slug}.md` | 实验记录（hypothesis → setup → results → claim updates） |
| `claims/` | `{claim-slug}.md` | 可验证的研究断言，连接论文、实验与综述 |
| `Summary/` | `{area-name}.md` | 领域全景综述 |
| `foundations/` | `{slug}.md` | 领域基础知识（其他页面链入；foundations 不写反向链接） |

---

## 链接语法

所有内部链接使用 Obsidian wikilink：

```markdown
[[slug]]                    ← 链接到本 wiki 内任意页面
[[lora-low-rank-adaptation]] ← 链接到 papers/lora-low-rank-adaptation.md
[[flash-attention]]          ← 链接到 concepts/flash-attention.md
```

**命名规范**：全小写，连字符分隔，无空格。

---

## Cross Reference 规则

写正向链接时**必须同步写反向链接**：

| 正向操作 | 必须同步的反向操作 |
|----------|-------------------|
| papers/A 写 `Related: [[concept-B]]` | concepts/B 的 `key_papers` 追加 `A` |
| papers/A 写 `[[researcher-C]]` | people/C 的 `Key papers` 追加 `A` |
| papers/A 写 `supports: [[claim-D]]` | claims/D 的 `evidence` 追加 `{source: A, type: supports}` |
| topics/T 写 `key_people: [[person-D]]` | people/D 的 `Research areas` 追加 T |
| concepts/K 写 `key_papers: [[paper-E]]` | papers/E 的 `Related` 追加 `K` |
| concepts/K 写 part_of `[[topic-F]]` | topics/F 的概述段落追加 `K` |
| ideas/I 写 `origin_gaps: [[claim-C]]` | claims/C 的 `## Linked ideas` 追加 I |
| experiments/E 写 `target_claim: [[claim-C]]` | claims/C 的 `evidence` 追加 `{source: E, type: tested_by}` |
| claims/C 写 `source_papers: [[paper-P]]` | papers/P 的 `## Related` 追加 C |
| 任意页面链接到 `[[foundation-X]]` | **不写反向链接** — foundations 是终端节点：接收来自 papers/concepts 等页面的入链，但不写 `key_papers` 或任何反向引用字段 |

---

## 页面模板

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

正文：`## Problem` / `## Key idea` / `## Method` / `## Results` / `## Limitations` / `## Open questions` / `## My take` / `## Related`

### concepts/{concept-name}.md

```yaml
---
title: ""
aliases: []              # 别名列表（用于去重匹配，如 ["scaled dot-product attention", "SDPA"]）
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
domain: ""               # general / NLP / CV / ML Systems / Robotics
status: mainstream       # mainstream | historical
aliases: []              # 别名列表（用于 /ingest 去重匹配）
first_introduced: ""
date_updated: YYYY-MM-DD
source_url: ""           # Wikipedia URL 或留空
---
```

正文：`## Definition` / `## Intuition` / `## Formal notation` / `## Key variants` / `## Known limitations` / `## Open problems` / `## Relevance to active research`

Foundations **没有外向链接字段**（无 `key_papers`、无 `related_concepts`）。其他页面可链接到 foundation；foundation 不写反向链接。

### ideas/{idea-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed          # proposed | in_progress | tested | validated | failed
origin: ""                # 来源描述：哪篇论文的 gap、哪个 claim 的弱证据等
origin_gaps: []           # 关联的 claim/topic slugs（知识缺口来源）
tags: []
domain: ""                # NLP / CV / ML Systems / Robotics
priority: 3               # 1-5（1=low, 5=critical）
pilot_result: ""          # 初步实验结果摘要（tested 后填写）
failure_reason: ""        # 失败原因（failed 后填写，anti-repetition memory）
linked_experiments: []    # 关联的 experiment slugs
date_proposed: YYYY-MM-DD
date_resolved: ""         # validated/failed 日期
---
```

正文：`## Motivation` / `## Hypothesis` / `## Approach sketch` / `## Expected outcome` / `## Risks` / `## Pilot results` / `## Lessons learned`

### experiments/{experiment-slug}.md

```yaml
---
title: ""
slug: ""
status: planned           # planned | running | completed | abandoned
target_claim: ""          # 目标 claim slug
hypothesis: ""            # 实验验证的假设
tags: []
domain: ""                # NLP / CV / ML Systems / Robotics
setup:
  model: ""
  dataset: ""
  hardware: ""
  framework: ""
metrics: []               # 评估指标列表，如 [accuracy, F1, latency]
baseline: ""              # 对比基线描述
outcome: ""               # succeeded | failed | inconclusive
key_result: ""            # 核心结论一句话
linked_idea: ""           # 来源 idea slug
date_planned: YYYY-MM-DD
date_completed: ""
run_log: ""               # 运行日志路径（可选）
started: ""              # 开始运行时间（ISO 格式，由 /exp-run 自动填写）
estimated_hours: 0        # 预计运行时长（小时，由 /exp-run 根据 setup 自动估算）
remote:                   # 远程部署信息（仅 --env remote 时由 /exp-run 自动填写）
  server: ""              # 服务器 host
  gpu: ""                 # GPU index
  session: ""             # screen session 名
  started: ""             # 部署时间（ISO 格式）
  completed: ""           # 完成时间
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
domain: ""                # NLP / CV / ML Systems / Robotics
source_papers: []         # 提出该 claim 的论文 slugs
evidence:                 # 证据列表
  - source: ""            # paper/experiment slug
    type: supports        # supports | contradicts | tested_by | invalidates
    strength: moderate    # weak | moderate | strong
    detail: ""
conditions: ""            # claim 成立的前提条件/适用范围
date_proposed: YYYY-MM-DD
date_updated: YYYY-MM-DD
---
```

正文：`## Statement` / `## Evidence summary` / `## Conditions and scope` / `## Counter-evidence` / `## Linked ideas` / `## Open questions`

### graph/（自动生成 — 勿手动编辑）

`graph/` 目录由 `tools/research_wiki.py` 自动维护，从 wiki 页面内容派生。

| 文件 | 内容 | 生成命令 |
|------|------|----------|
| `edges.jsonl` | 类型化关系（extends, contradicts, supports, inspired_by, tested_by, invalidates, supersedes, addresses_gap, derived_from） | `python3 tools/research_wiki.py add-edge` |
| `context_brief.md` | 压缩上下文：claims + gaps + failed ideas + papers + edges（≤8000字符） | `python3 tools/research_wiki.py rebuild-context-brief` |
| `open_questions.md` | 开放问题：under-supported claims + open questions from papers/topics | `python3 tools/research_wiki.py rebuild-open-questions` |

每条 edge 格式：`{"from": "node_id", "to": "node_id", "type": "edge_type", "evidence": "...", "date": "..."}`

---

## index.md 格式

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

## log.md 格式（append-only）

```markdown
## [2026-04-07] ingest | added papers/lora-low-rank-adaptation | updated: concepts/parameter-efficient-fine-tuning
## [2026-04-07] lint | report: 0 🔴, 2 🟡, 1 🔵
## [2026-04-08] daily-arxiv | 3 papers ingested from RSS
```

---

## Python 环境

运行任何 Python 工具之前，必须确保使用正确的 Python 环境。按以下优先级检测并激活：

1. **检查 `.venv/` 是否存在**：若存在，直接调用 venv 内的解释器 —— 跨平台最安全。
   - Unix/macOS：存在 `.venv/bin/python` → 用 `.venv/bin/python tools/X.py`
   - Windows：存在 `.venv/Scripts/python.exe` → 用 `.venv/Scripts/python.exe tools/X.py`
2. **检查 `conda` 环境**：若当前无 venv 但有 conda，使用 `conda run -n <env>` 或确认 conda env 已激活
3. **系统 Python**：若以上都不存在，Unix/macOS 用 `python3`，Windows 用 `python`

**示例：调用工具时**
```bash
# Unix/macOS，存在 .venv/
.venv/bin/python tools/fetch_arxiv.py --hours 24

# Windows，存在 .venv/（Git Bash 与 PowerShell 都支持正斜杠）
.venv/Scripts/python.exe tools/fetch_arxiv.py --hours 24

# 无 venv
python3 tools/fetch_arxiv.py --hours 24      # Unix/macOS
python tools/fetch_arxiv.py --hours 24       # Windows
```

直接调用 venv 内的解释器，可以避免在 Unix 上 `source activate` 与 Windows 上 `Activate.ps1` 的差异，跨平台行为完全一致。

**环境变量**：所有 Python 工具会自动从 `~/.env` 和项目根目录 `.env` 加载 API Key（通过 `tools/_env.py`），无需手动 export。

---

## 约束

- **raw/ 仅 `/init` 可追加写，其它一律只读**：`/init` Step 2 可以把新发现的源文件下载到 `raw/papers/`（只允许新增，绝不覆盖已有文件）。其它所有 skill、tool、subagent（包括 `/ingest`、`/daily-arxiv`、以及 `/init` 在 INIT MODE 下 fan-out 的 `/ingest` subagents）都必须把 `raw/` 视为严格只读：不得修改、覆盖或删除 `raw/` 下的任何内容。
- **graph/ 自动生成**：不得手动编辑 `graph/` 下的文件，仅通过 `tools/research_wiki.py` 维护。
- **双向链接**：写正向链接时同步写反向链接。
- **tex 优先**：.tex > .pdf，fallback 链：tex 失败 → PDF 解析，PDF 失败 → vision API。
- **index.md 每次 ingest 立即更新**，log.md append-only。
- **lint 默认只报告**：`--fix` 自动修复确定性问题（xref 反向链接、缺失字段默认值）；`--suggest` 输出非确定性问题的建议供用户批准；`--fix --dry-run` 预览修复。
- **slug 生成规则**：论文标题关键词，连字符连接，全小写。
- **importance 评分**：1 = niche, 2 = useful, 3 = field-standard, 4 = influential, 5 = seminal。
- **idea 失败必须记录原因**：`failure_reason` 字段是反重复记忆，防止重复探索已知死路。
- **claim confidence 区间**：0.0-1.0，evidence 每次变动时重新评估。
- **experiment 必须关联 claim**：每个 experiment 必须有 `target_claim`，结果必须回写 claim 的 evidence。
- **实验代码统一在 experiments/code/{slug}/**：`/exp-run` 生成的代码写入此目录（`train.py`, `config.yaml`, `run.sh`, `requirements.txt`），不写到项目根或其他位置。
- **DeepXiv token**：`DEEPXIV_TOKEN` 环境变量。未设置时 SDK 自动注册（写入 `~/.env`）。免费额度 10,000 请求/天。DeepXiv 不可用时所有 skill 自动回退到 S2+RSS 模式。

---

## Skills

| Skill | 文件 | 触发 |
|-------|------|------|
| `/setup` | `skills/setup/SKILL.md` | 手动（首次配置） |
| `/reset` | `skills/reset/SKILL.md` | 手动（`--scope wiki\|raw\|log\|checkpoints\|all`） |
| `/init` | `skills/init/SKILL.md` | 手动 |
| `/prefill` | `skills/prefill/SKILL.md` | 手动（`[domain] [--add concept]`） |
| `/ingest` | `skills/ingest/SKILL.md` | 手动 |
| `/ask` | `skills/ask/SKILL.md` | 手动 |
| `/edit` | `skills/edit/SKILL.md` | 手动 |
| `/check` | `skills/check/SKILL.md` | 每两周/手动 |
| `/daily-arxiv` | `skills/daily-arxiv/SKILL.md` | cron 08:00 / 手动 |
| `/novelty` | `skills/novelty/SKILL.md` | 手动 |
| `/review` | `skills/review/SKILL.md` | 手动 |
| `/ideate` | `skills/ideate/SKILL.md` | 手动 |
| `/exp-design` | `skills/exp-design/SKILL.md` | 手动 |
| `/exp-run` | `skills/exp-run/SKILL.md` | 手动（`<slug> [--collect] [--full] [--env local\|remote]`） |
| `/exp-status` | `skills/exp-status/SKILL.md` | 手动（`[--pipeline <slug>] [--collect-ready] [--auto-advance]`） |
| `/exp-eval` | `skills/exp-eval/SKILL.md` | 手动 |
| `/refine` | `skills/refine/SKILL.md` | 手动 |
| `/paper-plan` | `skills/paper-plan/SKILL.md` | 手动 |
| `/paper-draft` | `skills/paper-draft/SKILL.md` | 手动 |
| `/paper-compile` | `skills/paper-compile/SKILL.md` | 手动 |
| `/survey` | `skills/survey/SKILL.md` | 手动 |
| `/research` | `skills/research/SKILL.md` | 手动 |
| `/rebuttal` | `skills/rebuttal/SKILL.md` | 手动 |
