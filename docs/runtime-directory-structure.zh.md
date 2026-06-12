# 运行时目录图

> 按需读取的仓库布局参考。主 `CLAUDE.md` 只保留需要常驻上下文的 schema 与约束。

```text
CLAUDE.md              ← runtime schema（仓库根目录）
AGENTS.md              ← 任意 coding agent 的入口（指向 CLAUDE.md）

wiki/
├── index.md           ← 内容目录（YAML）
├── log.md             ← 时序日志（append-only）
├── papers/            ← 实证论文结构化卡片
├── variables/         ← 变量定义、角色、测算口径和来源文献
├── datasets/          ← 数据来源、样本范围、频率、字段
├── models/            ← 主回归、机制、异质性、稳健性模型设定
├── mechanisms/        ← 理论机制与经验证据链
├── hypotheses/        ← 研究假设与文献支持情况
├── identification/    ← 识别策略、内生性处理、关键假设
├── robustness/        ← 稳健性检验方法库
├── heterogeneity/     ← 异质性分组逻辑
├── tables/            ← 结果表格、变量表、回归表解释
├── concepts/          ← 可复用概念综述
├── topics/            ← 研究方向地图
├── people/            ← 作者与研究脉络追踪
├── ideas/             ← 研究想法（带生命周期状态）
├── experiments/       ← 保留给计算实验；经管实证优先使用 models/ 与 tables/
├── claims/            ← 可验证的理论/经验证据断言
├── Summary/           ← 领域全景综述
├── foundations/       ← 领域基础知识（终端：只接受入链，不写出链）
├── outputs/           ← 生成物（文献综述、变量表、实证方案、Stata 计划）
└── graph/             ← 自动生成（勿手动编辑）
    ├── edges.jsonl
    ├── citations.jsonl
    ├── context_brief.md
    └── open_questions.md

raw/
├── papers/            ← 用户自有 .tex / .pdf 来源
├── discovered/        ← /init 与 /daily-arxiv 抓取的外部论文
├── tmp/               ← /init 与直接本地 /ingest 生成的本地预处理来源
├── notes/             ← 用户自有 .md 笔记
└── web/               ← 用户自有 HTML / Markdown

tools/
├── research_wiki.py   ← wiki 引擎（slug / add-edge / rebuild-* / checkpoint）
├── lint.py            ← 结构校验（--fix / --suggest）
├── stata-templates/   ← 预置 do 模板（TWFE / DID / PSM / IV / RDD）
├── golden_check.py    ← ingest 质量回归断言（配 tests/golden/）
├── view.sh            ← Quartz 本地网站视图
├── update_demo.sh     ← 不切分支更新 demo 分支
└── fetch_*.py / discover.py / remote.py / reset_wiki.py / prepare_paper_source.py

tests/golden/          ← 基准论文期望抽取清单

.claude/skills/        ← 29 个 skill（每个目录一个 SKILL.md）

config/
├── server.yaml        ← 远程 GPU 服务器配置（可选，/exp-run --env remote 时需要）
├── server.yaml.example
└── settings.local.json.example

.env.example           ← 环境变量模板（仓库根目录；setup 复制为 .env）
```

## 快速提醒

- `raw/papers/`、`raw/notes/`、`raw/web/` 是用户自有输入。
- 经管实证项目建议在 `raw/notes/research-intent.md` 写清楚研究主题、潜在被解释变量、核心解释变量、数据范围和想要复现/对比的文献。
- `raw/discovered/` 用于外部抓取论文，不是用户随手放文件的目录。
- `raw/tmp/` 是 `/init` 与直接本地 `/ingest` 的生成型中间状态。
- `graph/` 是派生目录，只能通过 `tools/research_wiki.py` 维护。
