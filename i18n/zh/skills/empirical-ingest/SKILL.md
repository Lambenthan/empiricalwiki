---
description: 将一篇经管实证论文摄取为实证研究 wiki：论文卡片 + 变量 + 数据 + 模型 + 机制 + 识别 + 稳健性 + 异质性 + 表格线索
argument-hint: "<local-pdf-or-tex-path> [--topic <research-topic>]"
---

# /empirical-ingest

> 把一篇实证论文拆成可复用的研究设计资产。它不是普通摘要工具；优先抽取变量、数据、模型、机制、识别和稳健性，再写通用概念。

## Inputs

- `source`: 本地 `.pdf`、`.tex`，或 `/init` 预处理后的 `raw/tmp/...` 路径。
- `--topic` 可选：当前项目主题，如“耐心资本与 ESG”。

## Outputs

- `wiki/papers/{slug}.md`
- 按需新建或更新：
  - `wiki/variables/*.md`
  - `wiki/datasets/*.md`
  - `wiki/models/*.md`
  - `wiki/mechanisms/*.md`
  - `wiki/hypotheses/*.md`
  - `wiki/identification/*.md`
  - `wiki/robustness/*.md`
  - `wiki/heterogeneity/*.md`
  - `wiki/tables/*.md`
- `wiki/index.md`、`wiki/log.md`
- `wiki/graph/edges.jsonl`

## Workflow

### Step 1: Resolve Source

确认工作目录是项目根目录，包含 `wiki/`、`raw/`、`tools/`。

优先使用 `.venv`：

```bash
if [ -x .venv/bin/python ]; then PYTHON_BIN=.venv/bin/python; else PYTHON_BIN=python3; fi
```

如果输入是 PDF，先人工读取第一页标题。中文 PDF 可以用 PyMuPDF 快速抽取：

```bash
"$PYTHON_BIN" - "<source>" <<'PY'
import sys, fitz
path = sys.argv[1]
doc = fitz.open(path)
print(doc[0].get_text("text")[:2000])
PY
```

然后运行：

```bash
"$PYTHON_BIN" tools/prepare_paper_source.py --raw-root raw --source <source> --title "<confident-title>"
```

把返回的 `prepared_path` 作为正文读取入口。若标题不确定，不传 `--title`。

### Step 2: Extract Empirical Facts

从论文中抽取以下字段。没有明确证据时写“未报告”，不要猜：

- 研究问题
- 理论机制
- 研究假设
- 样本区间、样本范围、样本筛选规则
- 数据来源和数据库表
- 被解释变量、核心解释变量、中介变量、调节变量、控制变量、工具变量
- 变量测算公式、分组规则、缩尾规则
- 主模型、固定效应、标准误聚类方式
- 内生性处理
- 机制检验、异质性检验、稳健性检验
- 关键表格及结论
- 可复现线索：变量名、数据库、Stata 处理步骤

### Step 3: Write Pages

打开 `docs/runtime-page-templates.zh.md`，按模板写页面。

写 `papers/{slug}.md` 时，正文必须包含：

```markdown
## 研究问题
## 理论机制
## 研究假设
## 数据与样本
## 变量设定
## 模型设定
## 主要结果
## 机制检验
## 异质性检验
## 稳健性检验
## 内生性处理
## 可复现线索
## 对我当前选题的启发
## Related
```

对每个核心变量、数据源、模型、机制和检验方法，先查重再创建新页面：

```bash
"$PYTHON_BIN" tools/research_wiki.py slug "<title>"
```

已有等价页面时更新，不重复造近义页面。

### Step 4: Add Graph Edges

用工具写图谱关系，不手动编辑 `wiki/graph/edges.jsonl`：

```bash
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to variables/<variable> --type operationalizes --confidence high --evidence "<evidence>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to datasets/<dataset> --type uses_dataset --confidence high --evidence "<evidence>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to models/<model> --type estimates_model --confidence high --evidence "<evidence>"
```

其他边按需使用：`tests_mechanism`、`tests_hypothesis`、`addresses_endogeneity_with`、`uses_robustness_check`、`uses_heterogeneity_split`、`reports_table`。

### Step 5: Rebuild and Report

```bash
"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki
"$PYTHON_BIN" tools/lint.py --wiki-dir wiki
```

最后报告：

- 新增/更新了哪些页面
- 还缺哪些信息
- 哪些变量或模型可以直接服务当前项目

## Constraints

- 不要编造变量口径、模型公式、数据库表名。
- 中文论文没有 arXiv/Semantic Scholar 元数据时，不把这视为失败；以 PDF 正文和项目内文献为准。
- 实证论文优先抽取 `variables/`、`datasets/`、`models/`，不要只写通用 `concepts/`。
- `raw/papers/` 是用户输入，不覆盖、不移动。
