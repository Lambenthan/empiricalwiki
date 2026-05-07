---
description: 基于已摄取文献和本地数据，生成经管实证研究设计：问题、机制、变量、模型、识别、机制、异质性、稳健性
argument-hint: "<research-question-or-topic>"
---

# /empirical-design

> 从 wiki 知识库生成一份可落地的实证研究方案。它连接文献阅读和数据处理，不负责替用户发明 idea。

## Workflow

### Step 1: Read Project Context

读取：

- `wiki/graph/context_brief.md`
- `wiki/papers/*.md`
- `wiki/variables/*.md`
- `wiki/datasets/*.md`
- `wiki/models/*.md`
- `wiki/mechanisms/*.md`
- `wiki/identification/*.md`
- `wiki/robustness/*.md`
- `wiki/heterogeneity/*.md`
- 项目根目录和上级目录中的 `README.md`
- `raw/notes/research-intent.md`（如果存在）

### Step 2: Produce the Design

输出结构：

```markdown
# 实证研究设计

## 1. 研究问题
## 2. 文献定位
## 3. 理论机制
## 4. 研究假设
## 5. 变量设计
## 6. 数据来源与样本构造
## 7. 基准模型
## 8. 识别策略与内生性风险
## 9. 机制检验
## 10. 异质性检验
## 11. 稳健性检验
## 12. 预期表格结构
## 13. 数据缺口清单
## 14. 下一步操作
```

每个关键判断都要引用 wiki 页面，如 `[[耐心资本]]`、`[[耐心资本对企业esg表现的影响研究]]`。

### Step 3: Archive

写入：

```text
wiki/outputs/empirical-design-{slug}-{YYYY-MM-DD}.md
```

追加日志并建议是否继续运行 `/stata-plan`。

## Constraints

- 明确区分“文献已有做法”和“本项目建议做法”。
- 对内生性风险要具体，不写空泛的“可能存在内生性问题”。
- 如果本地数据不足，要列出缺口，不要假装可做。
- 不生成最终论文段落；这里输出的是研究设计和执行方案。
