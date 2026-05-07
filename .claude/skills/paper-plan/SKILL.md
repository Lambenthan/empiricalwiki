---
description: 从 claim graph 编译论文大纲：编译 evidence map → 叙事结构 → 章节计划 + figure plan + citation plan，Review LLM review 必选
argument-hint: <claim-slugs...> --venue <ICLR|NeurIPS|ICML|ACL|CVPR|IEEE> [--title <working-title>]
---

# /paper-plan

> 从 wiki 的 claim graph 编译论文大纲。
> 输入 target claims（status: supported 或 weakly_supported），指定目标会议/期刊，
> 从 wiki 编译 evidence map → 确定叙事结构 → 生成章节大纲 + figure plan + citation plan。
> Review LLM review 是必选步骤（作为 area chair 审查大纲说服力）。
> 输出 PAPER_PLAN.md 到 wiki/outputs/。
>
> 关键差异：大纲由 claim graph 驱动 — 每个 section 存在是因为它支撑某个 claim，
> 而非因为论文惯例要求有该 section。

## Inputs

- `claims`：目标 claims 的 slug 列表（空格分隔）
  - 每个 claim 应为 `supported` 或 `weakly_supported` 状态
  - 若包含 `proposed` 或 `challenged` 状态的 claim，发出警告但继续
- `--venue`（必选）：目标会议/期刊，决定页数限制和格式要求
  - 支持：`ICLR` / `NeurIPS` / `ICML` / `ACL` / `CVPR` / `IEEE`
- `--title`（可选）：工作标题，若不提供则从 target claim 生成

## Outputs

- `wiki/outputs/paper-plan-{slug}-{date}.md` — 完整论文计划（PAPER_PLAN.md）
- `wiki/graph/edges.jsonl` — 新增 derived_from 边（plan → source claims/papers）
- `wiki/graph/context_brief.md` — 重建
- `wiki/log.md` — 追加日志
- **PAPER_PLAN_REPORT**（输出到终端）— 计划摘要

## Wiki Interaction

### Reads
- `wiki/claims/*.md` — 目标 claims 的 status、confidence、evidence 列表、conditions
- `wiki/experiments/*.md` — claims 的 supporting experiments（结果、metrics、key_result）
- `wiki/papers/*.md` — evidence 来源论文（Method、Results、Related）
- `wiki/concepts/*.md` — 涉及的技术概念（支持 Method 章节撰写）
- `wiki/topics/*.md` — 研究方向上下文（支持 Introduction 定位）
- `wiki/ideas/*.md` — 原始 idea 的 motivation 和 hypothesis
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/open_questions.md` — 知识缺口（标注论文 limitation）
- `wiki/graph/edges.jsonl` — 关系图谱（构建叙事逻辑链）
- `.claude/skills/shared-references/academic-writing.md` — 写作原则
- `.claude/skills/shared-references/citation-verification.md` — 引用纪律

### Writes
- `wiki/outputs/paper-plan-{slug}-{date}.md` — 论文计划文件
- `wiki/graph/edges.jsonl` — derived_from 边
- `wiki/graph/context_brief.md` — 重建
- `wiki/log.md` — 追加操作日志

### Graph edges created
- `derived_from`：paper-plan → claims（计划从哪些 claims 派生）
- `derived_from`：paper-plan → papers（计划引用哪些论文）

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。

### Step 1: 加载 Claim Graph

1. 读取所有 target claims 的 `wiki/claims/{slug}.md`
2. 对每个 claim，收集其 evidence 列表：
   - 每条 evidence 的 source（paper slug 或 experiment slug）
   - evidence type（supports / contradicts / tested_by / invalidates）
   - evidence strength（weak / moderate / strong）
3. 对每条 evidence source，读取对应的 wiki 页面：
   - `wiki/experiments/{source}.md` → key_result、metrics、outcome
   - `wiki/papers/{source}.md` → Method、Results
4. 从 `wiki/graph/edges.jsonl` 加载相关边，构建 claims 之间的关系
5. 读取 `wiki/graph/context_brief.md` 获取全局上下文
6. 读取 `wiki/graph/open_questions.md` 标注 known limitations

**验证**：
- 若任何 target claim 的 status 为 `proposed`：警告「claim 尚未验证，论文可能缺乏证据支撑」
- 若任何 target claim 的 confidence < 0.5：警告「claim confidence 较低，建议先运行更多实验」
- 若无 experiment evidence 支撑任何 claim：错误「至少需要一个实验结果才能规划论文」

### Step 2: 从 Wiki 编译 Evidence Map

生成一个结构化矩阵，映射 claims → evidence → sections：

```markdown
| Claim | Status | Confidence | Evidence Sources | Strength | Paper Section |
|-------|--------|-----------|-----------------|----------|---------------|
| [[primary-claim]] | supported | 0.85 | exp-main, paper-A | strong | Method + Exp 5.2 |
| [[supporting-claim-1]] | supported | 0.75 | exp-ablation-1 | moderate | Exp 5.3 (Ablation) |
| [[supporting-claim-2]] | weakly_supported | 0.55 | exp-scaling | weak | Exp 5.4 (Scaling) |
```

按维度映射 claims 到论文结构：
- **Target claim** → 核心贡献，驱动 Abstract + Introduction + Method
- **Decomposition claims** → 各因素贡献，驱动 Ablation subsections
- **Contextual claims** → 背景知识，驱动 Related Work + Introduction

### Step 3: 确定叙事结构

遵循 `shared-references/academic-writing.md` 的 hourglass 原则：

1. **确定 paper 的核心故事线**：
   - Gap（从 ideas/ 的 motivation 或 gap_map 提取）
   - Solution（从 target claim 的 approach 提取）
   - Evidence（从 experiments 的 results 提取）
   - Impact（从 claim confidence + scope 推断）

2. **确定叙事角度**：
   - 论文解决什么问题？（问题驱动 vs 方法驱动 vs 数据驱动）
   - 主要读者是谁？（理论/系统/应用）
   - 与最近最相关的 3 篇论文如何区分？

3. **建立 section → claim 映射**：
   每个 section 必须至少支撑一个 claim。没有 claim 支撑的 section 是填充，应删除。

### Step 4: 生成章节大纲

按 venue 格式要求生成大纲，每个 section 包含：

```markdown
## 1. Introduction (1.5 pages)

### Claims addressed
- Gap claim: {existing approaches lack X because Y}
- Contribution claim: [[primary-claim]]

### Paragraph plan
1. Broad context: {field importance, recent progress}
2. Specific problem: {what's missing, why it matters}
3. Our approach: "In this work, we propose..." + contributions list
4. Results preview: {headline numbers}
5. Paper structure: "The rest of this paper..."

### Key citations
- [[paper-A]] — establishes the problem
- [[paper-B]] — closest prior work (we improve upon)
- [[paper-C]] — our baseline

---

## 2. Related Work (1 page)

### Groupings
- Direction A: {papers, our position}
- Direction B: {papers, our position}
- Direction C: {papers, our position}

### Claims addressed
- Contextual claims distinguishing from prior work

---

## 3. Method (2-3 pages)

### Claims addressed
- [[primary-claim]]: section 3.1-3.2
- [[supporting-claim-1]]: section 3.3

### Subsection plan
- 3.1 Problem formulation: notation, objective
- 3.2 Core approach: intuition → formalism
- 3.3 Component X: design decision + justification
- 3.4 Training/inference details

### Figures
- Figure 1: Overall architecture (mandatory)
- Figure 2: Component X detail (if complex)

---

## 4. Experiments (2-3 pages)

### Claims addressed
- [[primary-claim]]: section 4.2 (main results)
- [[supporting-claim-1]]: section 4.3 (ablation)
- [[supporting-claim-2]]: section 4.4 (scaling)

### Subsection plan
- 4.1 Setup: datasets, baselines, metrics, implementation details
- 4.2 Main results: Table 1 (main comparison), [[exp-main]]
- 4.3 Ablation study: Table 2 (component analysis), [[exp-ablation-*]]
- 4.4 Analysis: scaling, robustness, qualitative examples

### Figures/Tables
- Table 1: Main comparison vs baselines
- Table 2: Ablation results
- Figure 3: Scaling curves / qualitative examples

---

## 5. Conclusion (0.5 page)

### Key takeaway
- {one sentence the reader should remember}

### Limitations
- {from gap_map or claim conditions}

### Future work
- {from gap_map open questions}
```

**Page budget**：根据 `--venue` 分配（参考 academic-writing.md 的 venue 表），总 section 页数 <= venue 主文限制。

### Step 5: Figure Plan

为每个计划中的 figure/table 设计：

```markdown
## Figure Plan

### Figure 1: System Architecture
- Type: diagram
- Source: Method section description
- Style: block diagram with labeled components
- Size: full width (1 column = text width)

### Table 1: Main Results
- Type: comparison table
- Source: [[exp-main]] key_result + baselines
- Columns: Method | Metric-1 | Metric-2 | ...
- Rows: baselines + ours (ours in bold)
- Notes: best bold, second underline, ↑/↓ arrows for direction

### Figure 3: Scaling Analysis
- Type: line plot
- Source: [[exp-scaling]] results
- X-axis: scale dimension (model size / data size)
- Y-axis: performance metric
- Lines: ours vs baseline, with error bands
```

### Step 6: Citation Plan

参照 `shared-references/citation-verification.md`：

1. 列出大纲中所有 `[[slug]]` 引用的 wiki papers
2. 对每篇论文，pre-fetch BibTeX：
   - 先 DBLP，再 CrossRef，再 S2
   - 成功：记录 BibTeX key + 来源
   - 失败：标记 `[UNCONFIRMED]`
3. 生成 citation coverage 报告：
   ```
   Citations: 15 total, 12 verified (DBLP: 8, CrossRef: 3, S2: 1), 3 [UNCONFIRMED]
   ```
4. 对 [UNCONFIRMED] 条目，提供建议的手动检查 URL

### Step 7: Review LLM Review（必选）

```
mcp__llm-review__chat:
  system: "You are an area chair at {venue} reviewing a paper outline.
           Assess: Is the narrative convincing? Does every section serve a clear purpose?
           Are the experiments sufficient to support the claims?
           Is the related work coverage adequate?
           Are there obvious gaps that reviewers will attack?
           Provide specific suggestions for strengthening the outline."
  message: |
    ## Paper Outline
    {complete outline from Step 4}

    ## Evidence Map
    {evidence map from Step 2}

    ## Figure/Table Plan
    {plan from Step 5}

    ## Citation Coverage
    {report from Step 6}

    ## Questions for Review
    1. Is the narrative arc (gap → solution → evidence → impact) convincing?
    2. Are any claims under-supported? Which experiments are missing?
    3. Is the related work grouping appropriate? Missing directions?
    4. Will the page budget work? Any section too long/short?
    5. Are the figures/tables sufficient to tell the story?
```

根据 Review LLM 反馈修改大纲（补充 section、调整 page budget、添加 figure/table、修正叙事结构）。

### Step 8: 输出到 Wiki

1. **生成 slug**：
   ```bash
   python3 tools/research_wiki.py slug "<working-title>"
   ```

2. **写入 PAPER_PLAN.md**：
   创建 `wiki/outputs/paper-plan-{slug}-{date}.md`，包含：
   - 元信息（venue、title、date、target claims）
   - Evidence Map（Step 2）
   - 完整章节大纲（Step 4，含 Review LLM 修改）
   - Figure/Table Plan（Step 5）
   - Citation Plan + coverage report（Step 6）
   - Review LLM Review Summary（Step 7 关键反馈和修改记录）

3. **添加 graph edges**：
   ```bash
   # plan → target claim
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "outputs/paper-plan-{slug}-{date}" --to "claims/{primary-claim}" \
     --type derived_from --evidence "Paper plan built from this claim"

   # plan → key papers
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "outputs/paper-plan-{slug}-{date}" --to "papers/{paper-slug}" \
     --type derived_from --evidence "Paper plan cites this paper"
   ```

4. **重建派生数据**：
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   ```

5. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "paper-plan | {venue} paper outline for [[{slug}]] | claims: {claim-list} | citations: {verified}/{total}"
   ```

6. **输出 PAPER_PLAN_REPORT 到终端**：
   ```markdown
   # Paper Plan Report

   ## Meta
   - Title: {working title}
   - Venue: {venue}
   - Page limit: {N} pages
   - Date: {date}

   ## Claims → Sections
   | Claim | Confidence | Section |
   |-------|-----------|---------|
   | [[primary]] | 0.85 | Method + Exp 5.2 |
   | [[supporting-1]] | 0.75 | Exp 5.3 |

   ## Page Budget
   | Section | Pages | Claims |
   |---------|-------|--------|
   | Introduction | 1.5 | gap, contribution |
   | Related Work | 1.0 | context |
   | Method | 2.5 | primary, supporting |
   | Experiments | 2.5 | all |
   | Conclusion | 0.5 | — |

   ## Figures/Tables: {N} planned
   ## Citations: {verified}/{total} verified, {verify_count} [UNCONFIRMED]
   ## Review LLM Review: score {X}/10, verdict: {verdict}

   ## Next Steps
   - Run `/paper-draft wiki/outputs/paper-plan-{slug}-{date}.md` to draft the paper
   - Resolve {verify_count} [UNCONFIRMED] citations before /paper-compile
   ```

## Constraints

- **--venue 必选**：不同会议的页数限制、格式要求差异大，不可省略
- **至少一个 experiment evidence**：纯理论 claim 不足以支撑实验性论文，需至少一个实验结果
- **page budget 必须可行**：总 section 页数 <= venue 主文限制，否则调整（压缩或移至 appendix）
- **Review LLM review 必选**：不可跳过。大纲阶段发现问题成本最低
- **所有引用来自 wiki**：citation plan 中的每篇论文必须在 wiki/papers/ 中存在
- **claim → section 映射完整**：每个 target claim 必须出现在至少一个 section 中
- **每个 section 必须有 claim**：无 claim 支撑的 section 视为填充，应删除或合并
- **graph edges 使用 tools/research_wiki.py**：不手动编辑 edges.jsonl
- **引用使用 [[slug]]**：大纲中所有引用使用 wikilink 语法

## Error Handling

- **claim 状态不足**：若所有 claims 均为 proposed，报错「claims 尚未验证，建议先运行实验」
- **无 experiment evidence**：报错「至少需要一个实验结果」，建议先运行 /exp-design + /exp-run
- **wiki papers 不足**：若 citation plan 中 wiki 论文 < 5 篇，警告「相关工作覆盖不足，建议先 /ingest 更多论文」
- **page budget 超限**：自动将低优先级 section 移至 appendix 计划，报告调整
- **Review LLM 不可用**：降级为 Claude 自审，报告标注「single-model review — cross-model verification unavailable」
- **BibTeX 获取失败**：标记 [UNCONFIRMED]，在 citation plan 报告中汇总
- **slug 冲突**：追加日期后缀
- **target claim 找不到**：报错，列出 wiki/claims/ 中候选

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — 生成 slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建 query_pack
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/fetch_s2.py search "<title>"` — Semantic Scholar 搜索（citation plan fallback）

### MCP Servers
- `mcp__llm-review__chat` — Step 7 大纲审查（必选）

### Claude Code Native
- `Read` — 读取 wiki 页面
- `Glob` — 查找 claims、experiments、papers
- `WebFetch` — DBLP / CrossRef BibTeX 获取（Step 6）

### Shared References
- `.claude/skills/shared-references/academic-writing.md` — 叙事结构和章节设计原则
- `.claude/skills/shared-references/citation-verification.md` — 引用获取和验证规则

### Called by
- `/research` Stage 5（论文写作阶段）
- 用户手动调用
