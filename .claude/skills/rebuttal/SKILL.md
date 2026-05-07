---
description: 解析审稿意见 → 原子化 concerns (Rvx-Cy) → 映射到 wiki claims → 检查 evidence → Review LLM stress-test → 生成 rebuttal
argument-hint: <review-file-or-path> [--paper-slug <slug>] [--venue <venue>] [--stress-test] [--format formal|rich]
---

# /rebuttal

> 解析审稿意见，将每条 concern 原子化（Rvx-Cy 编号）并映射到 wiki claim，
> 检查 evidence 是否充分（追溯到 wiki experiments），
> 用 Review LLM 模拟审稿人追问（stress-test，评分 1-5），生成正式版（纯文本）和富文本版 rebuttal。
> 安全检查确保 no fabrication, no overpromise, full coverage。

## Inputs

- `review`：审稿意见来源，以下之一：
  - 文件路径（如 `raw/reviews/reviewer1.txt`、`raw/reviews/meta-review.md`）
  - 多个文件路径（逗号分隔：`raw/reviews/R1.txt,raw/reviews/R2.txt,raw/reviews/R3.txt`）
  - 直接粘贴的审稿文本
- `--paper-slug`（可选）：关联论文在 wiki/outputs/ 中的 slug，用于定位 PAPER_PLAN
- `--venue`（可选）：目标会议/期刊（ICLR / NeurIPS / ICML / ACL / CVPR），影响 rebuttal 格式和字数限制
- `--stress-test`（可选，默认开启）：Review LLM 模拟审稿人追问，关闭用 `--no-stress-test`
- `--format`（可选，默认 `formal`）：输出格式
  - `formal`：正式 rebuttal 纯文本版（适合直接粘贴到 submission system）
  - `rich`：富文本版（含 wiki [[links]]、详细分析、改进计划）

## Outputs

- **wiki/outputs/rebuttal-{slug}.md** — 富文本版 rebuttal（含 [[wikilinks]]、evidence 追溯、分析表格）
- **wiki/outputs/rebuttal-{slug}.txt** — 正式版 rebuttal（plain text，适合 submission system 粘贴）
- **wiki/claims/*.md** — 若 concern 暴露 evidence gap，在 `## Open questions` 追加建议
- **wiki/log.md** — 追加日志

## Wiki Interaction

### Reads
- `wiki/claims/*.md` — 映射 concerns 到 claims，检查 evidence 充分性
- `wiki/experiments/*.md` — 查找支持 claim 的实验 result
- `wiki/papers/*.md` — 查找引用的论文上下文
- `wiki/concepts/*.md` — 理解 method 相关 concerns 的概念背景
- `wiki/ideas/*.md` — 查找 idea 的 motivation 和 pilot results
- `wiki/outputs/PAPER_PLAN.md` — 了解论文结构（来自 /paper-plan，若有 --paper-slug）
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/edges.jsonl` — claim-experiment-paper 关系
- `.claude/skills/shared-references/cross-model-review.md` — Review LLM stress-test 独立性

### Writes
- `wiki/outputs/rebuttal-{slug}.md` — 富文本版
- `wiki/outputs/rebuttal-{slug}.txt` — formal 纯文本版
- `wiki/claims/*.md` — 在 `## Open questions` 追加 reviewer 发现的 gap（不直接修改 confidence/status，仅建议）
- `wiki/log.md` — 追加日志

### Graph edges created
- 无新 edges（rebuttal 是查询操作，不修改知识图谱）

## Workflow

**前置**：
1. 确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）
2. 读取 `cross-model-review.md` 确认 stress-test 独立性原则
3. 生成 slug：`python3 tools/research_wiki.py slug "{paper-slug}-rebuttal"`

### Step 1: 解析审稿意见

1. **读取审稿文本**：
   - 若为文件路径：读取所有指定文件
   - 若为直接文本：直接使用
   - 合并多个 reviewer 的意见，标注来源（Reviewer 1/2/3/Meta）

2. **识别结构**：
   - 提取每个 reviewer 的：overall score（Accept/Reject/Borderline）、confidence、summary、Strengths、Weaknesses、questions
   - 若格式不标准（纯文本），用 LLM 解析为结构化格式

3. **输出**：每个 reviewer 的结构化意见

### Step 2: 原子化 Concerns

将每条 weakness 和 question 拆分为独立的 atomic concern：

1. **拆分规则**：
   - 一个 weakness 可能是复合句，包含多个独立 concern（"方法缺少消融实验，且没有与 X 比较" → 拆分为 2 个 concerns）
   - 每个 atomic concern 分配 ID：`Rvx-Cy` 格式（Rv1-C1 = Reviewer 1, Concern 1；Rv1-C2 = Reviewer 1, Concern 2）
   - 保留 reviewer 编号，确保追溯到原始意见

2. **分类每个 concern**：
   - **evidence**：关于实验数据、result 解读的事实性质疑
   - **method**：关于方法设计、算法正确性的方法论问题
   - **missing**：缺少某些实验/分析/比较/引用
   - **clarity**：表达不清、符号混乱、图表问题
   - **scope**：贡献不够显著、适用范围质疑
   - **novelty**：与已有工作重叠、创新性不足
   - **minor**：格式、typo 等小问题

3. **评估严重性**：critical / major / minor

4. **输出**：原子化 concern 列表，每个包含 {id (Rvx-Cy), reviewer, type, severity, text}

### Step 3: 映射 Concerns 到 Wiki Claims

对每个 concern：

1. **查找关联 claim**：
   - 从 concern 文本提取关键词
   - 在 `wiki/claims/*.md` 中搜索匹配的 claim
   - 读取 `wiki/graph/edges.jsonl` 查找 claim-experiment 关系
   - 若找不到直接匹配：标注 "unmapped"（无直接 claim 对应）

2. **检查 Evidence Status**：
   - 读取 claim 的 evidence 列表
   - 统计 strong/moderate/weak evidence 数量
   - 查找关联 experiments 的 results
   - **判断**：
     - 充分（sufficient）：strong >= 1 或 moderate >= 2
     - 部分充分（partial）：有 evidence 但强度不够
     - 不足（insufficient）：无 evidence 或只有 weak
     - 矛盾：有 invalidates 类型 evidence

3. **输出**：

| Concern ID | Reviewer | Type | Severity | Claim mapped | Evidence Status | Strategy |
|------------|----------|------|----------|--------------|-----------------|----------|
| Rv1-C1 | R1 | method | critical | [[claim-slug]] | sufficient | A |
| Rv1-C2 | R1 | missing | major | [[claim-slug]] | insufficient | B |
| Rv2-C1 | R2 | novelty | major | unmapped | — | D |

### Step 4: 起草 Rebuttal 回应

对每个 concern 按 strategy 起草回应：

**Strategy A — Evidence 充分（直接回应）：**
- 引用具体实验 result 和数据（标注来源，确保追溯到 wiki/experiments/）
- 指向 wiki 中的 evidence（转化为论文引用）
- 若 concern 基于误解：礼貌澄清，指出论文中相关 Section

**Strategy B — Evidence 不足（承认 + 具体计划）：**
- 诚实承认当前 evidence 不够充分
- 提出具体的补充实验计划（可链接到 /exp-design）
- 说明具体时间线和资源需求
- 不使用模糊承诺，只承诺具体可执行的补充实验

**Strategy C — Clarity 问题（修改承诺）：**
- 承认表达不清
- 提供改进后的描述（直接在 rebuttal 中展示修改后的文本）
- 列出具体的 Paper Edit 计划

**Strategy D — Scope/Novelty 质疑（论证）：**
- 强调与现有工作的本质区别
- 引用 novelty-check 结果（若有）
- 指出 reviewer 可能遗漏的差异点

**每条回应的格式**：
```markdown
**[Rvx-Cy]** {concern summary}

{response text, 2-5 sentences，标注来源确保可追溯}
```

**安全检查（每条回应）**：
- [ ] No fabrication：不伪造数据或实验结果
- [ ] No overpromise：只承诺具体可执行的补充实验
- [ ] 引用的数据在 wiki/experiments/ 中有记录
- [ ] 若 claim 已 challenged/deprecated，不假装它是 supported

### Step 5: Review LLM Stress-Test

**遵循 cross-model-review.md**：不向 Review LLM 发送 Claude 的 rebuttal 策略分析。

若 `--stress-test` 开启（默认）：

```
mcp__llm-review__chat:
  system: "You are a critical reviewer who has just read a rebuttal to your review
           comments. You are skeptical and will push back on weak responses.
           For each rebuttal response, assess on a scale of 1-5:
           1 = unconvincing (deflection or fabrication suspected)
           2 = weak (vague, no concrete evidence)
           3 = acceptable (addresses concern but could be stronger)
           4 = strong (concrete evidence, clear reasoning)
           5 = fully convincing (compelling evidence, thorough response)
           Also check for overpromise: are commitments specific and feasible?
           Provide a follow-up question for any response scoring <= 3."
  message: |
    ## Original Review Concerns
    {atomic concerns list with Rvx-Cy IDs}

    ## Author Rebuttal
    {drafted rebuttal responses}

    ## Please assess each response (score 1-5) and provide follow-up questions.
```

**处理 Review LLM 反馈**：
- **score 4-5（convincing）**：保持原回应
- **score 3（acceptable）**：加强回应，补充 Review LLM 建议的细节
- **score 1-2（unconvincing/weak）**：重写回应，考虑是否需要更换 strategy（A→B，承认不足）

**第二轮（若有 score <= 2 的回应）**：

```
mcp__llm-review__chat-reply:
  threadId: {previous thread}
  message: |
    We've revised the following responses:
    {revised responses}
    Please re-assess (score 1-5).
```

最多 2 轮 stress-test。处理 follow-up 追问并更新回应。

### Step 6: 格式化输出 + 安全检查

**6a. 格式化正式版 rebuttal-{slug}.txt**（plain text，适合 submission system）：

```
We thank the reviewers for their constructive feedback. We address each concern below.

Reviewer 1:

[Rv1-C1] {concern summary}
{response}

[Rv1-C2] {concern summary}
{response}

Reviewer 2:
...

Summary of Revisions:
- {bulleted list of planned changes}

Additional Experiments (if applicable):
- {new experiments committed to, with timeline}
```

**6b. 格式化富文本版 rebuttal-{slug}.md**：

```markdown
# Rebuttal Analysis: {paper title}

## Coverage Summary
| Concern ID | Type | Severity | Claim | Evidence Status | Review LLM Score | Strategy |
|------------|------|----------|-------|-----------------|------------|----------|
| Rv1-C1 | method | critical | [[claim-slug]] | sufficient | 4/5 | A |
| Rv1-C2 | missing | major | [[claim-slug]] | insufficient | 3/5 | B |

## Responses
### Reviewer 1
**[Rv1-C1]** ...
**[Rv1-C2]** ...

## Evidence Gap Analysis
| Claim | Confidence | Gap | Needed |
|-------|-----------|-----|--------|
| [[claim-slug]] | 0.5 | No ablation on dataset X | Run ablation experiment |

## Action Items

### Paper Edits
| Section | Change | Reason |
|---------|--------|--------|
| Section 3.2 | Clarify notation | Rv1-C3 clarity concern |

### Wiki Updates
| Page | Update | Reason |
|------|--------|--------|
| claims/{slug} | Add open question | Rv2-C1 evidence gap |

### Suggested Experiments
| Experiment | Target Claim | Suggested by |
|-----------|-------------|--------------|
| ablation-dataset-x | [[claim-slug]] | Rv1-C2 |

→ Run `/exp-design ablation-dataset-x` to design follow-up

## Review LLM Stress-Test Summary
- Average score: {N}/5
- Scores 4-5: {N}/{total}
- Scores 1-3: {N}/{total} (all revised)

## Safety Checklist
- [x] No fabrication: all cited data exists in wiki/experiments
- [x] No overpromise: all committed experiments are specific and feasible
- [x] Full coverage: {N}/{N} concerns addressed (no omissions)
- [x] Challenged claims not presented as supported
```

**6c. 最终安全检查**：
- **Full coverage**：确认每个 concern 都有回应（无遗漏）
- **No fabrication**：每个引用的数据点在 wiki/experiments/ 中有记录（可追溯）
- **No overpromise**：补充实验的承诺是具体可行的
- **Honesty on weak claims**：若 claim confidence < 0.4，不假装 evidence 充分

**6d. 更新 wiki**：
- 若有 evidence gap 的 claims：在 `wiki/claims/{slug}.md` 的 `## Open questions` 追加 reviewer 指出的 gap
- 追加日志：
  ```bash
  python3 tools/research_wiki.py log wiki/ \
    "rebuttal | {N} concerns addressed | {M} evidence gaps | stress-test avg: {score}/5"
  ```

## Constraints

- **No fabrication**：绝不编造实验数据或 result。每个引用的数字必须可追溯到 wiki/experiments/，标注来源
- **No overpromise**：只承诺具体可执行的补充实验。用 "we will run ablation on X with setup Y" 而非 "we will investigate"
- **Full coverage**：每个 reviewer concern (Rvx-Cy) 必须有回应，不得遗漏。coverage 不足时阻止输出
- **Evidence 追溯**：每条回应引用的 evidence 必须可追溯到 wiki 页面，标注来源 slug
- **不直接修改 wiki claims**：rebuttal 只在 claims 的 Open questions 追加建议，不修改 confidence/status
- **Review LLM 独立性**：stress-test 时遵循 cross-model-review.md，不向 Review LLM 透露回应策略
- **Concern ID 格式**：严格使用 Rvx-Cy 格式（Rv1-C1, Rv1-C2, Rv2-C1），确保可追溯
- **具体承诺**：所有修改承诺和实验计划必须具体（specific Section、具体 dataset、明确 metric）
- **输出到 wiki/outputs/**：rebuttal 文件统一存放在 wiki/outputs/ 目录

## Error Handling

- **审稿文件找不到**：报错，列出 raw/reviews/ 下可用文件
- **审稿格式无法解析**：降级为纯文本处理，由 LLM 提取 concerns，在报告中标注
- **concern 映射不到 claim（unmapped）**：标注 "unmapped"，仍然回应（基于论文内容而非 wiki claim）
- **Review LLM stress-test 不可用**：跳过 Step 5，在报告中标注 "stress-test skipped: Review LLM unavailable"
- **evidence 严重不足**：若 >50% concerns 的 evidence 为 insufficient，警告用户并建议先补充实验
- **wiki 为空**：警告 wiki 知识库为空，建议先运行 /ingest 填充 claims 和 experiments
- **所有回应被 Review LLM 评为 1-2 分**：终止输出，报告需要重新分析，建议先补充实验

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "{title}"` — 生成 rebuttal slug
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志

### MCP Servers
- `mcp__llm-review__chat` — Step 5 stress-test 首轮
- `mcp__llm-review__chat-reply` — Step 5 stress-test 后续轮

### Claude Code Native
- `Read` — 读取审稿意见、wiki 页面、shared references
- `Write` — 写入 rebuttal-{slug}.md、rebuttal-{slug}.txt
- `Glob` — 查找 claims、experiments
- `Grep` — 在 wiki 中搜索 concern 关键词

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Review LLM stress-test 独立性原则

### Suggested follow-up skills
- `/exp-design` — 为 evidence 不足的 concerns 设计补充实验
- `/paper-draft` — 准备修订版论文（基于 Paper Edits 清单）
