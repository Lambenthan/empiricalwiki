# 运行时辅助文件

> 按需读取的 graph 派生文件，以及非页面型运行时文件 `index.md` 与 `log.md`。

## Graph 文件

| 文件 | 内容 | 生成命令 |
|------|------|----------|
| `edges.jsonl` | 语义关系：paper-paper、paper-variable、paper-model、claim/experiment/idea/provenance edge | `python3 tools/research_wiki.py add-edge` |
| `citations.jsonl` | bibliographic paper citation（`type: cites`） | `python3 tools/research_wiki.py add-citation` |
| `context_brief.md` | 压缩上下文：claims + gaps + failed ideas + papers + edges（≤8000字符） | `python3 tools/research_wiki.py rebuild-context-brief` |
| `open_questions.md` | 开放问题：under-supported claims + open questions from papers/topics | `python3 tools/research_wiki.py rebuild-open-questions` |

semantic edge 格式：`{"from": "node_id", "to": "node_id", "type": "edge_type", "evidence": "...", "confidence": "high|medium|low", "date": "..."}`

citation 格式：`{"from": "papers/citing", "to": "papers/cited", "type": "cites", "source": "semantic_scholar|parsed_bib|manual", "date": "..."}`

## index.md 格式

```yaml
papers:
  - slug: 耐心资本对企业esg表现的影响研究
variables:
  - slug: 耐心资本
datasets:
  - slug: csmar上市公司年度数据
models:
  - slug: 耐心资本影响esg基准模型
mechanisms:
  - slug: 长期治理机制
hypotheses:
  - slug: 耐心资本提升企业esg表现
identification:
  - slug: 企业和年份固定效应
robustness:
  - slug: 替换耐心资本测算口径
heterogeneity:
  - slug: 国有企业与非国有企业分组
tables:
  - slug: 基准回归表
concepts:
  - slug: 耐心资本
topics:
  - slug: 耐心资本与esg
people:
  - slug: tang-liang
ideas:
  - slug: 耐心资本与管理者短视
experiments:
  - slug: optional-computational-experiment
claims:
  - slug: 耐心资本缓解短期主义
```

## log.md 格式

```markdown
## [2026-04-07] empirical-ingest | added papers/耐心资本对企业esg表现的影响研究 | updated: variables/耐心资本, models/耐心资本影响esg基准模型
## [2026-04-07] lint | report: 0 🔴, 2 🟡, 1 🔵
## [2026-04-08] daily-arxiv | 3 papers ingested from RSS
```
