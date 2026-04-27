# ΩmegaWiki — Runtime Schema

> CS/AI ΩmegaWiki. 由 Claude Code 驱动。
> 本文件是 wiki 的运行时入口，定义页面结构、链接规范、workflow 约束。

---

## 仓库布局

需要完整仓库树时，再打开 `docs/runtime-directory-structure.zh.md`。

平时请优先记住这个心智地图：

### `wiki/` 是主要工作面

- `wiki/index.md` 是所有 wiki 页面的目录
- `wiki/log.md` 是 append-only 活动日志
- `wiki/papers/` 存放论文总结
- `wiki/concepts/`、`wiki/topics/`、`wiki/foundations/` 存放可复用知识结构
- `wiki/people/`、`wiki/ideas/`、`wiki/experiments/`、`wiki/claims/` 存放研究者、假设、实验和断言
- `wiki/Summary/` 存放领域级综述
- `wiki/outputs/` 存放生成产物
- `wiki/graph/` 是派生状态，禁止手动编辑

### 格式护栏

- 在新建或修复 wiki 页面结构、YAML、正文章节前，先打开 `docs/runtime-page-templates.zh.md`
- 需要 graph 派生文件细节或 `index.md` / `log.md` 格式时，打开 `docs/runtime-support-files.zh.md`
- `SKILL.md` 是 skill 的即时入口；较大的 skill 也可以在各自目录下提供按需读取的本地参考文件
- `/init` 是这一模式的第一个具体例子：先读 `skills/init/SKILL.md`，只有在需要时再打开 `skills/init/references/*`

### `raw/` 与 `config/`

- `raw/papers/`、`raw/notes/`、`raw/web/` 是用户自有输入
- `raw/discovered/` 存放 `/init` 与 `/daily-arxiv` 抓取的外部论文
- `raw/tmp/` 存放 `/init` 与直接本地 `/ingest` 使用的生成型 prepared sidecar
- `config/` 存放环境与远程服务器模板

---

## 9 类页面

`papers`、`concepts`、`topics`、`people`、`ideas`、`experiments`、`claims`、`Summary`、`foundations`。

页面模板看 `docs/runtime-page-templates.zh.md`；graph/index/log 参考看 `docs/runtime-support-files.zh.md`。

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

## Graph 规则

- `graph/` 是自动生成目录，不要手动编辑
- 核心派生文件是 `edges.jsonl`、`citations.jsonl`、`context_brief.md`、`open_questions.md`
- semantic edge type 包括 paper-paper（`same_problem_as`、`similar_method_to`、`complementary_to`、`builds_on`、`compares_against`、`improves_on`、`challenges`、`surveys`）、paper-concept（`introduces_concept`、`uses_concept`、`extends_concept`、`critiques_concept`），以及既有 claim/experiment/provenance 类型（`supports`、`contradicts`、`tested_by`、`invalidates`、`addresses_gap`、`derived_from`、`inspired_by`）
- `/ingest` 产生的 paper-paper 与 paper-concept semantic edge 必须带 `confidence: high|medium|low`
- 对称 paper-paper edge 只存一行，endpoint 按顺序排序，并写 `symmetric: true`
- bibliographic citation 存在 `citations.jsonl`，`type: cites`
- 用 `tools/research_wiki.py add-edge`、`add-citation`、`rebuild-context-brief`、`rebuild-open-questions` 维护

## log.md 格式

标准日志行：

```markdown
## [YYYY-MM-DD] skill | details
```

## Python 环境

- 有 `.venv/` 时优先用 `.venv/bin/python`（Unix/macOS）或 `.venv/Scripts/python.exe`（Windows）
- 否则使用当前激活的 conda 环境
- 再否则回退到 `python3`（Unix/macOS）或 `python`（Windows）
- Python 工具会通过 `tools/_env.py` 自动加载 `~/.env` 与项目根目录 `.env`

---

## 约束

- **`raw/papers/`、`raw/notes/`、`raw/web/` 归用户所有**：把它们当作权威输入。`/init` 与 `/daily-arxiv` 只能把外部抓取论文追加到 `raw/discovered/`。`/init` 与直接本地 `/ingest` 可以把生成的本地预处理 sidecar 写到 `raw/tmp/`（只增不改，绝不覆盖用户自有文件）。`/edit` 仅在用户明确要求时才允许新增 raw 来源。`/init` 在 INIT MODE 下 fan-out 的 `/ingest` 子代理仍必须把 `raw/` 视为严格只读，并直接消费交接的 canonical path。
- **skill 的用户可见参数归用户所有**：skill 的 `argument-hint` 中列出的 flag 与取值属于用户命令，而不是 agent 可自行决定的策略开关。不得仅根据仓库状态擅自补出、切换或删除这些参数。若用户未提供某个参数，只有在该 skill 明确写出省略时的默认或推导规则时，才可使用该默认或推导值；否则应保持未设置，必要时询问用户。不是用户可见参数的内部派生设置，skill 仍可自行推断。
- **INIT MODE 交接由 manifest 驱动**：当 `/init` 写出 `.checkpoints/init-sources.json` 后，该 manifest 就是 ingest 顺序与规范来源路径的唯一真相来源。预处理后的本地输入应指向 `raw/tmp/`；外部引入论文应指向 `raw/discovered/`。
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
| `/discover` | `skills/discover/SKILL.md` | 手动 / 内部（`/ingest --discover` 时调用） |
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
