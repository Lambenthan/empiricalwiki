---
description: 汇总某个经管实证变量在文献中的测算口径、数据来源、模型角色和项目可用性
argument-hint: "<variable-or-construct> [--role dependent|core_explanatory|mediator|moderator|control|all]"
---

# /variable-map

> 把分散在文献卡片里的变量信息整理成可执行的变量字典。适合回答“耐心资本怎么测算”“管理者短视有哪些口径”“ESG 用哪个数据源”。

## Workflow

### Step 1: Locate Relevant Pages

读取：

- `wiki/variables/*.md`
- `wiki/papers/*.md`
- `wiki/datasets/*.md`
- `wiki/models/*.md`
- 当前项目的 `README.md`、`raw/notes/research-intent.md`（如果存在）

按变量名称、别名、构念、角色、标签和 `source_papers` 匹配。

### Step 2: Build the Comparison Table

输出表格至少包含：

| 字段 | 含义 |
|---|---|
| 变量/构念 | 如耐心资本、ESG、管理者短视 |
| 模型角色 | 被解释变量、核心解释变量、中介、调节、控制等 |
| 测算口径 | 公式或文本描述 |
| 数据来源 | 数据库、表名、项目路径 |
| 样本频率 | firm-year、quarter 等 |
| 来源文献 | wiki paper slug |
| 优点 | 为什么可用 |
| 风险 | 内生性、口径争议、缺失值、复现难点 |
| 项目可用性 | 已有 / 缺失 / 需要手工整理 |

### Step 3: Archive

生成：

```text
wiki/outputs/variable-map-{slug}-{YYYY-MM-DD}.md
```

并追加日志：

```bash
python3 tools/research_wiki.py log wiki "variable-map | <variable> | output: outputs/<file>"
```

## Constraints

- 只比较 wiki 或本地项目中已有证据，不凭常识补数据库表名。
- 不把不同口径强行合并；口径不同就分行。
- 如果信息来自论文但本地数据没有，明确写“项目暂缺”。
