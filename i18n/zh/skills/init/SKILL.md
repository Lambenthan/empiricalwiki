---
description: 从 raw/ 目录搭建完整的 ΩmegaWiki，包括论文、概念、方向、人物页面，并初始化 ideas/experiments/claims 和 graph
argument-hint: "[topic]"
---

# /init

> 从零搭建一个 ΩmegaWiki。扫描 raw/ 目录和外部来源，创建完整的 wiki 骨架，
> 包含所有 8 种 entity 目录和 graph 初始化。每篇论文通过 `/ingest` 逐一消化，
> 确保 cross-references 和 graph edges 从第一天就完整。

## Inputs

- `topic`：研究方向关键词（如 "efficient fine-tuning for LLMs"）
- `raw/papers/` 中的 .tex / .pdf 文件
- 可选：`raw/notes/`、`raw/web/` 中的笔记和网页

## Outputs

- 完整的 wiki 骨架：所有 8 种 entity 目录 + `graph/` + `outputs/`
- `wiki/papers/*.md` — 每篇论文的结构化摘要（通过 /ingest 创建）
- `wiki/concepts/*.md` — 核心技术概念页面（通过 /ingest 创建）
- `wiki/topics/*.md` — 研究方向地图
- `wiki/people/*.md` — 关键人物页面（通过 /ingest 创建）
- `wiki/claims/*.md` — 核心 claims（通过 /ingest 提取）
- `wiki/ideas/*.md` — 初始研究想法（基于 gap_map 生成，若有）
- `wiki/Summary/{area}.md` — 领域全景综述
- `wiki/index.md`、`wiki/log.md`
- `wiki/graph/edges.jsonl`、`context_brief.md`、`open_questions.md`

## Wiki Interaction

### Reads
- `raw/papers/` — 待消化的论文来源
- `raw/notes/` — 用户研究笔记
- `raw/web/` — 保存的网页
- `wiki/index.md` — 检查已有页面避免重复（Step 4 批量 ingest 时）

### Writes
- `wiki/` 全目录结构（通过 `tools/research_wiki.py init`）
- `wiki/CLAUDE.md` — 运行时 schema（从模板复制）
- `wiki/index.md` — 内容目录
- `wiki/log.md` — 时序日志
- `wiki/Summary/{area}.md` — 领域综述
- `wiki/topics/{topic}.md` — 研究方向页面
- `wiki/ideas/{idea}.md` — 初始研究想法（若 gap_map 有内容）
- 其余 entity 由 `/ingest` 负责写入（papers, concepts, people, claims）

### Graph edges created
- 通过 `/ingest` 批量创建的所有 edges
- `concept → topic`: `supports`（手动创建的 topic-concept 关联）

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。
设 `WIKI_ROOT=wiki/`。

### Step 1: 初始化 wiki 目录结构

运行 init 命令，创建全部 8 种 entity 目录 + graph/ + outputs/ + seed 文件：

```bash
python3 tools/research_wiki.py init wiki/
```

这将创建：
- `wiki/papers/`, `wiki/concepts/`, `wiki/topics/`, `wiki/people/`
- `wiki/ideas/`, `wiki/experiments/`, `wiki/claims/`
- `wiki/Summary/`, `wiki/outputs/`
- `wiki/graph/` (含空 `edges.jsonl`)
- `wiki/index.md`, `wiki/log.md`

若 `wiki/CLAUDE.md` 不存在，从产品模板复制。

记录日志：
```bash
python3 tools/research_wiki.py log wiki/ "init | initialized wiki directory structure"
```

### Step 2: 收集 Raw Sources + 智能扩展

本步扫描用户已提供的论文，然后**有选择地扩展**——通过引用链和关键词搜索补充。目标：让 wiki 足够丰富，同时不让 init 耗时过长。

**预算**：在用户提供的论文之外，最多额外添加 **5–8 篇**。宁缺毋滥。

#### Phase A — 扫描本地来源

1. 扫描 `raw/papers/`，识别所有文件：
   - 压缩包（`.tar.gz` / `.zip`）：解压到 `raw/papers/{slug}/`
   - `.tex` 存在：优先使用（tex > PDF）
   - 仅 `.pdf`：使用 PyMuPDF 提取文本
2. 扫描 `raw/notes/`、`raw/web/` 中的用户笔记和网页
3. 记录为 `local_papers` 列表（标题、arxiv_id（如有）、路径）

#### Phase B — 引用链扩展（主要发现方式）

对 `local_papers` 中有 arXiv ID 的论文（选 importance 最高的 3–5 篇）：

```bash
python3 tools/fetch_s2.py references <arxiv_id>
python3 tools/fetch_s2.py citations <arxiv_id>
```

从合并结果中：
1. 过滤掉已在 `local_papers` 中的论文（按 arxiv_id 或标题匹配）
2. 按 `引用量 × 与 topic 的相关度` 排序（相关度通过标题/摘要与 `<topic>` 的语义重叠判断）
3. 选出 **top 3–5** 篇明显属于该领域核心但用户未收录的论文
4. 这些通常是用户默认了解的奠基性工作，或其遗漏的重要后续研究

#### Phase C — 关键词搜索补充（填补覆盖空白）

仅当 Phase B 选出不足 3 篇、或存在明显未覆盖的子方向时执行：

```bash
python3 tools/fetch_s2.py search "<topic>" 20
```

可选（若 DeepXiv 可用）：
```bash
python3 tools/fetch_deepxiv.py search "<topic>" --mode hybrid --limit 10
```

从合并结果中：
1. 与 `local_papers` + Phase B 已选结果去重
2. 选出 **1–3 篇** 能填补空白的论文（例如：不同方法路线、综述、或非常新的论文）
3. **如果头部结果都与已有论文重叠，则不添加**——不凑数

**若 DeepXiv 不可用**：仅依赖 S2 搜索。

#### Phase D — 下载已选论文

对 Phase B + C 选出的每篇论文：

```bash
# 优先下载 tex source（arXiv e-print）
curl -sL -o raw/papers/<slug>.tar.gz "https://arxiv.org/e-print/<arxiv_id>"
mkdir -p raw/papers/<slug> && tar -xzf raw/papers/<slug>.tar.gz -C raw/papers/<slug>/
rm raw/papers/<slug>.tar.gz

# 若 e-print 失败或无 arXiv ID，回退到 PDF
curl -sL -o raw/papers/<slug>.pdf "https://arxiv.org/pdf/<arxiv_id>"
```

下载后验证文件有效（非空、内容类型正确）。

#### Phase E — 汇总最终来源列表

合并 `local_papers` + 已下载论文为 `raw_source_list`（内存中，不写文件）。

记录扩展情况：
```bash
python3 tools/research_wiki.py log wiki/ "init | source expansion: <N> local + <M> discovered via citation chains and search"
```

**透明度**：在最终报告（Step 8）中，明确区分"用户提供的论文"和"系统发现的论文"，方便用户核实相关性。

### Step 3: 领域分析

1. LLM 阅读 `raw_source_list`，提取核心主题
2. 识别 3-8 个子方向（concepts）→ 将在 /ingest 中创建
3. 识别 2-5 个核心研究方向（topics）
4. 识别关键人物（people）→ 将在 /ingest 中创建
5. 提取领域全景信息用于 Summary 页面

### Step 4: 创建骨架页面

按 CLAUDE.md 模板创建以下页面（/ingest 不负责的部分）：

**4a — Summary 页面：**
- 按领域分析结果创建 `wiki/Summary/{area}.md`
- 按 CLAUDE.md Summary 模板填写 frontmatter 和正文各节

**4b — Topics 页面：**
- 按领域分析结果创建 `wiki/topics/{topic}.md`
- 按 CLAUDE.md topics 模板填写，含 open_problems 和 research_gaps 初始内容
- 将在 Step 5 的 /ingest 过程中逐步填充 seminal_works 和 key_people

**4c — 更新 index.md：**
- 将 Summary 和 topics 页面条目写入 index.md 对应分类

### Step 5: 通过并行子代理 Ingest 论文（Worktree 隔离）

所有论文 ingest agent **同时运行**，通过 git worktree 实现文件系统隔离。总耗时 ≈ 最慢的单篇论文耗时（而非所有论文之和）。

**加载 checkpoint**（支持 `--resume`）：
```bash
python3 tools/research_wiki.py checkpoint-load wiki/ "init-session"
```
若 checkpoint 存在，从剩余未完成的论文继续并行处理。

**合并顺序**：将 `raw_source_list` 按预估 importance 降序排列（高引用量、顶会优先）。重要性最高的论文最先合并，其 concept 定义成为后续合并的"标准基底"。

#### Phase A — Fan-out：后台 agent

spawn 前读取一次当前 wiki 状态（已创建的 topics）：
```bash
python3 tools/research_wiki.py find wiki/ --entity topic --field title
```

对 `raw_source_list` 中的每篇论文，spawn 一个**后台** agent（带 worktree 隔离）：

```
Agent({
  description: "ingest <论文简称>",
  isolation: "worktree",
  run_in_background: true,
  prompt: "对位于 <论文路径> 的论文执行 /ingest。

    INIT 模式 — 以快速批量引导模式运行 ingest。
    引用发现已在 /init Step 2 完成，因此跳过对应 API 调用。

    1. 读取 .claude/skills/ingest/SKILL.md 获取完整工作流
    2. 按以下 INIT 模式覆盖执行工作流：
         跳过 — fetch_s2.py citations <arxiv_id>   （引用链扩展已在 /init Step 2 完成）
         跳过 — fetch_s2.py references <arxiv_id>  （同上）
         跳过 — fetch_deepxiv.py head <arxiv_id>   （批量引导不需要章节结构）
         跳过 — 更新 wiki/index.md                 （主流程在 Step 7 末尾执行 rebuild-index）
         跳过 — 更新 wiki/topics/*.md              （主流程在合并后执行 lint --fix 修复所有 xref）
         执行 — 完整阅读 .tex/.pdf 来源
         执行 — fetch_s2.py paper <arxiv_id>        （元数据：venue, year, 引用量, s2_id）
         执行 — fetch_deepxiv.py brief <arxiv_id>   （快速 TLDR，用于草拟 Key idea）
         执行 — 创建 paper 页面、最多 3 个 claims、最多 3 个 concepts、关键 people（importance >= 4）
         执行 — 添加所有 graph edges，追加 log.md
    3. Wiki 根目录：wiki/   工具目录：tools/
    4. 先激活 venv：source .venv/bin/activate
    5. 已创建的 topics（不要重复创建）：<逗号分隔的 topic slugs>
    6. 完成后汇报：
       - 创建的页面（papers, concepts, people, claims）
       - 添加的 graph edges
       - 遇到的任何问题"
})
```

**并行的实现方式**：逐一 spawn 每个 agent，但 `run_in_background: true` 使每个 agent 立即开始运行而无需等待前一个完成。所有 N 个 agent 并发运行。spawn 完所有 N 个 agent 后，等待收到每个 agent 的完成通知，再进入 Phase B。

#### Phase B — Fan-in：顺序合并

所有 agent 完成后，按 importance 顺序（高引用量优先）逐一将各自的 worktree branch 合并到 main。

对每个已完成的 agent branch：
```bash
git merge --no-ff <worktree-branch> --no-edit 2>&1
```

**当 git 报告合并冲突时**（多篇论文引用同一 concept/claim 文件时属预期行为）：
- **concept 文件**：union `key_papers`、`aliases`、`related_concepts`；取更完整的 `## Definition` 和 `## Intuition` 正文段落
- **claim 文件**：union `evidence` 列表；对 `confidence` 取平均；union `source_papers`
- 解决每个文件冲突后：`git add <file> && git merge --continue`

每成功合并一篇论文后记录 checkpoint：
```bash
python3 tools/research_wiki.py checkpoint-save wiki/ "init-session" "<paper-slug>"
```

若合并彻底失败，放弃该 branch：
```bash
git merge --abort
python3 tools/research_wiki.py checkpoint-save wiki/ "init-session" "<paper-slug>" --failed
```

#### Phase C — 合并后清理

所有 branch 合并完成后：
```bash
# 删除并行 agent 写入的重复 edges
python3 tools/research_wiki.py dedup-edges wiki/
```

**全部完成后清理 checkpoint**：
```bash
python3 tools/research_wiki.py checkpoint-clear wiki/ "init-session"
```

**重要约束**：
- **每个 agent 必须设置 `run_in_background: true`** — 并行执行的前提；可以逐一 spawn，但所有 agent 必须并发运行
- **每个 agent 使用 `isolation: "worktree"`** — 防止并行执行期间的文件系统冲突
- **spawn 完所有 N 个 agent 后，等待所有 N 个完成通知**，再进入 Phase B
- **绝不绕过子代理** — 所有论文 ingest 必须通过子代理运行 /ingest 工作流
- **强制执行 init 模式跳过项** — SKIP 列表不得移除；`lint --fix`（Step 7）负责修复所有跳过的 xref

### Step 6: 生成初始 Ideas（可选）

在所有论文 ingest 完成后：

1. 读取 gap_map：
   ```bash
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```
2. 若 `wiki/graph/open_questions.md` 中有明确的知识缺口，为最突出的 1-3 个 gap 创建 `wiki/ideas/{idea}.md`：
   - status: proposed
   - origin: 自动从 gap_map 提取
   - origin_gaps: 关联的 claim/topic slugs
3. 更新 index.md 中的 ideas 分类
4. 添加 graph edges：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from ideas/<idea-slug> --to claims/<claim-slug> --type addresses_gap
   ```

### Step 7: 最终 Graph 重建与验证

1. 重建全部派生文件：
   ```bash
   # 从 entity frontmatter 重建 index.md（子代理已跳过此步骤）
   python3 tools/research_wiki.py rebuild-index wiki/
   # 重建 graph 上下文与开放问题
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```
2. 运行 lint 检查基本健康：
   ```bash
   python3 tools/lint.py --wiki-dir wiki/
   ```
3. 获取统计信息：
   ```bash
   python3 tools/research_wiki.py stats wiki/
   ```
4. 记录完成日志：
   ```bash
   python3 tools/research_wiki.py log wiki/ "init | completed: N papers, M concepts, K claims, L topics"
   ```

### Step 8: 报告给用户

输出摘要，包含：
- 创建的页面统计（按 8 种 entity 分类）
- 领域概况（topics 和 Summary 摘要）
- 提取的 claims 总览
- graph edges 数量
- lint 发现的问题（若有）
- 生成的初始 ideas（若有）
- 建议下一步：
  - 手动 `/ingest` 更多论文
  - 阅读 `wiki/Summary/` 查看领域全景
  - 运行 `/lint` 查看详细健康报告
  - 运行 `/ideate` 生成更多研究想法

## Constraints

- **raw/ 只读**：不得修改 `raw/` 下的文件
- **graph/ 仅通过 tools 维护**：不得手动编辑 `graph/` 下的文件
- **双向链接**：写正向链接时同步写反向链接（参照 CLAUDE.md Cross Reference 规则表）
- **tex 优先**：.tex > .pdf > vision API fallback
- **slug 通过工具生成**：必须使用 `python3 tools/research_wiki.py slug` 生成 slug
- **页面模板遵循 CLAUDE.md**：所有页面严格按照产品 CLAUDE.md 中的模板创建
- **importance 评分标准**：1=niche, 2=useful, 3=field-standard, 4=influential, 5=seminal
- **idea 初始状态为 proposed**：init 阶段只创建 proposed 状态的 ideas
- **不创建空 experiments**：experiments 由 /exp-design 创建，init 不生成

## Error Handling

- **raw/ 为空**：仅通过 arXiv/S2 搜索获取论文，在报告中注明
- **arXiv/S2/DeepXiv 搜索失败**：跳过失败的外部搜索源，使用其余可用源 + raw/ 中已有文件
- **单篇论文 ingest 失败**：记录到 checkpoint（`--failed`），跳过该论文继续处理，在最终报告中列出失败项
- **中途中断**：下次运行 `/init` 时自动检测 checkpoint，从断点继续（跳过已完成的论文）
- **wiki/ 已存在内容**：检测已有页面，跳过已存在的 entity，仅补充新内容（幂等性）
- **topic 生成不确定**：优先少而准，2-3 个高质量 topic 优于 5 个模糊 topic

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py init wiki/` — 初始化目录结构
- `python3 tools/research_wiki.py slug "<title>"` — slug 生成
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py dedup-edges wiki/` — 删除并行 ingest 合并后的重复 edges（Step 5，Phase C）
- `python3 tools/research_wiki.py rebuild-index wiki/` — 从 entity frontmatter 重建 index.md（Step 7，所有子代理完成后）
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建压缩上下文
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建知识缺口地图
- `python3 tools/research_wiki.py stats wiki/` — wiki 统计
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/fetch_s2.py search "<topic>" 20` — Semantic Scholar 关键词搜索
- `python3 tools/fetch_s2.py references <arxiv_id>` — 引用链扩展（参考文献）
- `python3 tools/fetch_s2.py citations <arxiv_id>` — 引用链扩展（被引用）
- `python3 tools/fetch_deepxiv.py search "<topic>" --mode hybrid --limit 10` — DeepXiv 语义搜索（可选）
- `python3 tools/lint.py --wiki-dir wiki/` — 结构检查
- `curl` — 下载 arXiv e-print（tex）或 PDF 到 raw/papers/

### Skills（via Agent 子代理）
- `/ingest` — 每篇论文由独立 Agent 子代理执行 ingest（Step 5）

### External APIs
- arXiv（通过 curl 下载 e-print）
- Semantic Scholar API（via tools/fetch_s2.py — 搜索、references、citations）
- DeepXiv API（via tools/fetch_deepxiv.py，可选，不可用时 graceful fallback）
