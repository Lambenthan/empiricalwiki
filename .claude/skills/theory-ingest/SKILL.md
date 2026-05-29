---
description: 将一篇理论建模论文摄取为理论研究 wiki：论文卡片 + 假设/原语 + 命题/定理 + 解概念 + 可检验推论，并与实证层在同一张 graph 上接桥
argument-hint: "<local-pdf-or-tex-path> [--topic <research-topic>]"
---

# /theory-ingest

> 把一篇理论建模论文拆成可复用的研究资产。对着「理论建模通用骨架」的 6 个固定槽位抽取：环境/原语、解概念、结果、论证、比较静态、可检验推论。形式化陈述逐字引用，禁止释义。

## Inputs

- `source`: 本地 `.pdf`、`.tex`，或 `/init` 预处理后的 `raw/tmp/...` 路径。
- `--topic` 可选：当前项目主题，如“管理者短视与耐心资本”。

## Outputs

- `wiki/papers/{slug}.md`（`paper_kind: theory`）
- 按需新建或更新：
  - `wiki/assumptions/*.md`
  - `wiki/propositions/*.md`
  - `wiki/hypotheses/*.md`（模型导出的可检验推论）
  - `wiki/mechanisms/*.md`（填 `## Theoretical Logic`，与实证层共享）
  - `wiki/foundations/*.md`（解概念、证明框架等可复用规范知识）
- `wiki/index.md`、`wiki/log.md`
- `wiki/graph/edges.jsonl`

## Workflow

### Step 1: Resolve Source

确认工作目录是项目根目录，包含 `wiki/`、`raw/`、`tools/`。

优先使用 `.venv`：

```bash
if [ -x .venv/bin/python ]; then PYTHON_BIN=.venv/bin/python; else PYTHON_BIN=python3; fi
```

理论论文公式密集，**`.tex` 优先**：有 `.tex` 源码就用源码，公式不会被 PDF 解析毁掉。只有 PDF 时先人工读第一页标题：

```bash
"$PYTHON_BIN" - "<source>" <<'PY'
import sys, fitz
doc = fitz.open(sys.argv[1])
print(doc[0].get_text("text")[:2000])
PY
```

然后运行：

```bash
"$PYTHON_BIN" tools/prepare_paper_source.py --raw-root raw --source <source> --title "<confident-title>"
```

把返回的 `prepared_path` 作为正文读取入口。

### Step 2: Extract Along the 6-Slot Skeleton

先打开 `docs/runtime-theory-skeleton.zh.md`，对着 6 个固定槽位抽取。没有明确证据写“未报告”，不猜：

1. **环境 / 原语**：参与人、行动/策略空间、偏好/支付函数、信息结构、时序、技术/约束
2. **解概念**：均衡概念（Nash / 子博弈精炼 / 贝叶斯精炼 / 竞争均衡 …）
3. **结果**：每个命题/定理/引理的形式化陈述 + 成立条件
4. **论证**：每个结果的证明技术
5. **比较静态**：内生量随参数怎么动
6. **可检验推论**：模型导出的、可拿去实证的符号关系

**理论论文没有 variables/datasets/identification/robustness——这些不是填“未报告”，而是整块不存在。这是与 `/empirical-ingest` 的根本分流。**

### Step 3: Write Pages

打开 `docs/runtime-page-templates.zh.md`，按模板写页面。

`papers/{slug}.md` 设 `paper_kind: theory`，填 `theory` block，正文用理论段落：

```markdown
## 研究问题
## 模型环境
## 核心假设
## 解概念
## 命题与证明
## 比较静态
## 可检验推论
## 对实证的启发
## Related
```

- 每条核心假设 → `assumptions/`，`formal_statement` **逐字引用原文**
- 每个命题/定理 → `propositions/`，`formal_statement` 逐字引用，`conditions` 写清成立条件，`proof_technique` 查不到写“未报告”
- 每条可检验推论 → `hypotheses/`（`status: literature_supported`）
- 模型形式化的经济机制 → 查重后更新 `mechanisms/` 的 `## Theoretical Logic` 段；不要新造与实证侧重复的机制页
- 解概念、证明框架等可复用规范知识 → `foundations/`（终端节点，不写反向链接）

每次新建前先查重：

```bash
"$PYTHON_BIN" tools/research_wiki.py slug "<title>"
```

### Step 4: Add Graph Edges

用工具写图谱关系，不手动编辑 `wiki/graph/edges.jsonl`：

```bash
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to assumptions/<a> --type assumes --evidence "<原文位置>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to propositions/<p> --type proves --evidence "<命题编号>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from papers/<paper> --to mechanisms/<m> --type formalizes_mechanism --confidence high --evidence "<evidence>"
"$PYTHON_BIN" tools/research_wiki.py add-edge wiki --from propositions/<p> --to hypotheses/<h> --type predicts --confidence high --evidence "<evidence>"
```

- `assumes`、`proves`：结构事实，**不带** `--confidence`
- `formalizes_mechanism`、`predicts`：判断，**必须带** `--confidence high|medium|low`
- `derived_from`（论文 → foundation）按需使用
- 实证论文检验本理论的推论时，实证侧的 `tests_hypothesis` / `tests_mechanism` 反向边由 `/empirical-ingest` 写；本 skill 只负责理论侧的正向边与双向链接同步

### Step 5: Rebuild and Report

```bash
"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki
"$PYTHON_BIN" tools/lint.py --wiki-dir wiki
```

最后报告：

- 新增/更新了哪些页面（按 6 槽位分组）
- 抽出的可检验推论是否已与既有实证论文/机制接上桥
- 哪些命题或机制可服务当前选题

## Constraints

- **形式化陈述逐字引用，禁止释义**：命题、假设的成立条件不得改写（把“对所有凹效用函数”写成“对效用函数”是灾难）。
- 不编造证明技术、参数符号、均衡结果；查不到写“未报告”。
- `propositions/` 装被证明的形式化结果，不与 `claims/`（带置信度的实证断言）混用。
- `mechanisms/`、`hypotheses/` 与实证层共享：先查重，优先更新既有页面的理论侧，不另造近义页。
- 纯计算/仿真（agent-based）模型偏实验性质，落 `experiments/`，不进 `propositions/`。
- `.tex` 优先。`raw/papers/` 是用户输入，不覆盖、不移动。
- 中文/英文理论论文没有 arXiv/S2 元数据时不视为失败，以正文为准。
