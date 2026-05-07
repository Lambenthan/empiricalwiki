# EmpiricalWiki 适配说明

这是从 OmegaWiki 克隆后做的经管实证研究适配版。原项目适合通用科研知识库，尤其偏 AI/CS 论文；本地版本把核心工作流改成“文献阅读 → 变量字典 → 数据来源 → 模型设定 → 识别策略 → 稳健性 → Stata 计划”。

## 适合谁用

- 做会计、金融、管理、经济学等经管实证研究的人。
- 已经有一批 PDF 文献、数据字典、Stata 代码或 `.dta/.xlsx` 数据的人。
- 想把文献阅读结果沉淀成项目知识库，而不是只留在一次性聊天记录里的人。

## 新增核心目录

```text
wiki/
├── papers/            实证论文卡片
├── variables/         变量定义、测算口径、数据来源
├── datasets/          数据库、字段、样本范围
├── models/            基准模型、机制模型、异质性模型、稳健性模型
├── mechanisms/        理论机制与经验证据链
├── hypotheses/        研究假设
├── identification/    识别策略与内生性处理
├── robustness/        稳健性检验方法
├── heterogeneity/     异质性分组
└── tables/            表格解释与复现线索
```

## 新增命令

```text
/empirical-ingest <pdf-or-tex>
```

把单篇实证论文拆成论文卡片、变量、数据、模型、机制、识别、稳健性和异质性页面。

```text
/variable-map "耐心资本"
```

汇总某个变量或构念在不同文献里的测算方式、数据来源、优缺点和本地项目可用性。

```text
/empirical-design "耐心资本与企业ESG表现"
```

基于已读文献和本地数据，生成研究问题、变量设计、模型设定、机制检验、异质性、稳健性和数据缺口。

```text
/stata-plan <design-path-or-topic>
```

把实证方案转成 Stata 执行计划；加 `--write-do` 时生成 `.do` 骨架。

## 推荐用法

1. 把论文放进 `raw/papers/`，或像当前项目一样用软链接接入已有文献目录：`raw/papers/patient-capital-literature`。
2. 在 `raw/notes/research-intent.md` 写清楚当前项目想研究什么。
3. 先挑 3-5 篇核心文献运行 `/empirical-ingest`。
4. 对核心变量运行 `/variable-map`。
5. 运行 `/empirical-design`，得到可执行的实证方案。
6. 运行 `/stata-plan`，进入数据清洗和回归阶段。

## 对“耐心资本”项目的建议

可以先从这些本地文献开始：

- A1 经典口径下的 ESG 文献
- 管理者短视机制相关文献
- 创新韧性、新质生产力、企业韧性相关文献

第一轮目标不是读完全部 PDF，而是先把“耐心资本如何测算”“ESG/创新/韧性如何测算”“主模型怎么设”“稳健性怎么做”沉淀到 `variables/` 和 `models/`。

## 与原 OmegaWiki 的区别

- 保留原来的论文摄取、问答、综述、图谱能力。
- 弱化 AI/CS 式的 experiment lifecycle。
- 强化经管实证研究真正需要的变量、数据、模型、识别和 Stata 执行链。
