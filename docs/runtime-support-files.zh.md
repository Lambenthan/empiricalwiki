# 运行时辅助文件

> 按需读取的 graph 派生文件，以及非页面型运行时文件 `index.md` 与 `log.md`。

## Graph 文件

| 文件 | 内容 | 生成命令 |
|------|------|----------|
| `edges.jsonl` | 语义关系：paper-paper、paper-concept、claim/experiment/idea/provenance edge | `python3 tools/research_wiki.py add-edge` |
| `citations.jsonl` | bibliographic paper citation（`type: cites`） | `python3 tools/research_wiki.py add-citation` |
| `context_brief.md` | 压缩上下文：claims + gaps + failed ideas + papers + edges（≤8000字符） | `python3 tools/research_wiki.py rebuild-context-brief` |
| `open_questions.md` | 开放问题：under-supported claims + open questions from papers/topics | `python3 tools/research_wiki.py rebuild-open-questions` |

semantic edge 格式：`{"from": "node_id", "to": "node_id", "type": "edge_type", "evidence": "...", "confidence": "high|medium|low", "date": "..."}`

citation 格式：`{"from": "papers/citing", "to": "papers/cited", "type": "cites", "source": "semantic_scholar|parsed_bib|manual", "date": "..."}`

## index.md 格式

```yaml
papers:
  - slug: lora-low-rank-adaptation
concepts:
  - slug: parameter-efficient-fine-tuning
topics:
  - slug: efficient-llm-adaptation
people:
  - slug: tri-dao
ideas:
  - slug: sparse-lora-for-edge-devices
experiments:
  - slug: sparse-lora-latency-benchmark
claims:
  - slug: lora-preserves-quality-at-low-rank
```

## log.md 格式

```markdown
## [2026-04-07] ingest | added papers/lora-low-rank-adaptation | updated: concepts/parameter-efficient-fine-tuning
## [2026-04-07] lint | report: 0 🔴, 2 🟡, 1 🔵
## [2026-04-08] daily-arxiv | 3 papers ingested from RSS
```
