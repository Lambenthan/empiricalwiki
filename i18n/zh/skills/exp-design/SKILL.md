---
description: Claim-driven 实验设计：界定目标 claims → 设计实验块（baseline/validation/ablation/robustness）→ 构建执行顺序 → 可选 Review LLM review → 写入 wiki
argument-hint: <idea-slug-or-hypothesis> [--review] [--budget <gpu-hours>]
---

# /exp-design

> 根据一个 idea（或自由文本假设），设计完整的实验计划。
> 以 claims 为核心：从 Target / Decomposition / Threats 三个维度界定要验证的 claims，
> 设计 baseline（基线复现）、validation（核心验证）、ablation（因素隔离）、robustness（鲁棒性）四种实验块。
> 实验按依赖关系排序，阶段间设决策门（sanity fail → 提前停止）。
> 可选 Review LLM review 检查实验完整性。所有实验写入 wiki/experiments/ 并添加 graph edges。

## Inputs

- `idea`：以下之一：
  - wiki/ideas/ 中的 slug（如 `sparse-lora-for-edge-devices`）
  - 自由文本假设描述（直接提供实验目标）
- `--review`（可选）：启用 Review LLM review 审查实验计划完整性
- `--budget <gpu-hours>`（可选）：总计算预算上限（GPU 小时），影响 robustness 实验规模

## Outputs

- `wiki/experiments/{slug}.md` — 每个实验块一个页面（status: planned）
- `wiki/graph/edges.jsonl` — 新增 experiment → claim 的 tested_by 边
- `wiki/ideas/{slug}.md` — 更新 linked_experiments 字段
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加日志
- **EXPERIMENT_PLAN_REPORT**（输出到终端）— 实验块总览、执行顺序、计算预算

## Wiki Interaction

### Reads
- `wiki/ideas/{slug}.md` — 获取 idea 的 hypothesis、approach、risks、origin_gaps
- `wiki/claims/*.md` — 目标 claims 的当前状态、已有 evidence、confidence
- `wiki/experiments/*.md` — 已有实验（避免重复设计、参考 setup 配置）
- `wiki/papers/*.md` — 相关论文的 baselines 和实验设置
- `wiki/concepts/*.md` — 涉及的技术概念（指导实验设计）
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/open_questions.md` — 知识缺口（指导实验优先级）

### Writes
- `wiki/experiments/{slug}.md` — 创建实验页面（每个实验块一个）
- `wiki/ideas/{slug}.md` — 更新 linked_experiments 字段
- `wiki/graph/edges.jsonl` — 添加 tested_by 边
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加操作日志

### Graph edges created
- `tested_by`：claim → experiment（claim 被该实验验证）

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。

### Step 1: 加载上下文

1. **解析 idea 输入**：
   - 若为 slug：读取 `wiki/ideas/{slug}.md`，提取 `## Motivation`、`## Hypothesis`、`## Approach sketch`、`## Risks`,以及 frontmatter 字段 `origin_gaps`、`tags`、`domain`、`priority`（遵循 CLAUDE.md 的 ideas template）
   - 若为自由文本：直接作为假设描述使用
2. **加载相关 wiki 上下文**：
   - 读取 `wiki/graph/context_brief.md`（全局上下文）
   - 读取 `wiki/graph/open_questions.md`（知识缺口）
   - 从 idea 的 `origin_gaps` 读取对应的 `wiki/claims/*.md`（目标 claims）
   - 从每个目标 claim 的 `source_papers` 字段读取对应的 `wiki/papers/*.md`,获取 baseline setup 和已有实验协议 —— 这是 idea → claim → paper 的规范路径(ideas **不带** `linked_papers` 字段,改用 `origin_gaps` → `source_papers`)
   - 读取已有 `wiki/experiments/*.md`,检查是否已有类似实验
3. **若 idea 无 origin_gaps**：从假设描述中提取隐含的 claims，在 wiki/claims/ 中查找或标注需要新建

### Step 2: 界定 Claims（Scope Claims）

从三个维度界定本次实验计划涉及的 claims。对于每个维度，先在 wiki/claims/ 中查找已有 claim；若不存在，创建新 claim（status: proposed, confidence: 0.3）。

1. **Target**（验证什么）：
   - idea 的核心假设对应的 claim——本次实验计划要直接验证的目标
   - 通常 1 个，最多 2 个
2. **Decomposition**（拆解什么）：
   - 方法中各独立因素各自的贡献 claim
   - 每个因素对应一个 claim，用于设计隔离验证实验
3. **Threats**（什么会推翻我们）：
   - 已知的风险、替代解释、边界条件
   - 来源：wiki 中的 counter-evidence、papers 的 limitations、claim 的 open questions
   - 指导鲁棒性实验的设计

输出：界定的 claims 清单（slug 列表 + 维度标注 + 每个 claim 的当前 status/confidence）

### Step 3: 设计实验块（Design Experiment Blocks）

为每个界定的 claim 设计实验块，4 种类型：

**A. Baseline 实验（基线复现）**：
- 目的：确认问题存在、基线可复现
- 复现最相关论文的核心实验
- 成功标准：基线结果与论文报告的差异 < 5%（此阈值与下方 Stage 1 decision gate 一致 —— 不要在别处使用不同的数字）
- 计算量：通常最小

**B. Validation 实验（验证 Target claim）**：
- 目的：在基线之上验证核心贡献
- 指标：比 baseline 有统计显著提升
- 需要足够的 seed/run 数量确保可靠性（建议 >= 3 seeds）
- 计算量：中等

**C. Ablation 实验（验证 Decomposition claims）**：
- 目的：隔离各独立因素的贡献
- 每个 ablation 移除一个因素，验证性能下降
- N 个因素 → N 个 ablation 实验
- 计算量：与 validation 类似 × N

**D. Robustness 实验（排除 Threats）**：
- 目的：排除已知风险和替代解释，验证方法在不同条件下仍然有效
- 变化维度：模型大小、数据集、超参数、domain
- 至少测试 2 个变化维度
- 计算量：取决于 --budget

每个实验块包含：
- `title`：描述性标题
- `target_claim`：对应的 claim slug
- `hypothesis`：实验验证的具体假设
- `type`：baseline / validation / ablation / robustness
- `setup`：model、dataset、hardware、framework
- `metrics`：评估指标列表
- `baseline`：对比基线
- `success_criterion`：明确的成功/失败标准
- `estimated_gpu_hours`：预估计算时间
- `seeds`：随机种子数量（建议 >= 3）

### Step 4: 构建执行顺序（Build Run Order）

按依赖关系排序实验，设置决策门：

```
Stage 0: Sanity check
  └── 小规模运行（1 epoch / 100 steps）验证代码无 bug、数据可加载、GPU 可用
  └── 门：若 sanity 失败 → 停止，修复代码

Stage 1: Baseline（基线复现）
  └── 复现基线结果
  └── 门：若基线偏差 > 5% → 停止，检查实现（与 Step 3 成功标准同阈值）

Stage 2: Validation（核心验证）
  └── 在基线之上验证核心方法
  └── 门：若无提升 → 停止，分析原因（可能是 idea 不成立）

Stage 3: Ablation（因素隔离）
  └── 可并行执行多个 ablation
  └── 门：若某因素 ablation 无影响 → 记录，但继续其他 ablation

Stage 4: Robustness（鲁棒性验证）
  └── 仅在 Stage 2 成功后执行
  └── 范围由 --budget 剩余额度决定
```

输出：
- 有序实验列表（含依赖关系）
- 每阶段的决策门条件
- 总计算预算估算（若超过 --budget 则调整 Stage 4 范围）

### Step 5: 可选 Review LLM Review（--review）

若指定 `--review`：

```
mcp__llm-review__chat:
  system: "You are a senior ML researcher reviewing an experiment plan.
           Focus on: missing baselines, missing ablations, unfair comparisons,
           statistical rigor (enough seeds?), and dataset selection.
           For every issue found, suggest a concrete fix."
  message: |
    ## Experiment Plan
    {complete experiment plan: claims, blocks, run order, budgets}

    ## Context
    {target claims with current status, related papers' experiment setups}

    ## Review Questions
    1. Are any critical experiments missing?
    2. Are the baselines fair and comprehensive?
    3. Is the ablation design sufficient to isolate each contribution?
    4. Are the success criteria well-defined and reasonable?
    5. Any statistical concerns (sample size, variance, seeds)?
```

根据 Review LLM 反馈调整实验计划（添加遗漏的实验、修正不合理的标准）。

### Step 6: 写入 Wiki

1. **创建实验页面**：
   对每个实验块：
   ```bash
   python3 tools/research_wiki.py slug "<experiment-title>"
   ```
   创建 `wiki/experiments/{slug}.md`：
   ```yaml
   创建 `wiki/experiments/{slug}.md`，**严格遵循 CLAUDE.md experiments template** —— 下方所有字段都必须存在（即使为空），因为 `/exp-run` 稍后会用 `tools/research_wiki.py set-meta` 来更新它们，而 `set-meta` 拒绝创建 frontmatter 中不存在的字段（它只更新已存在的 key）：
   ```yaml
   ---
   title: ""
   slug: ""
   status: planned
   target_claim: ""          # claim slug
   hypothesis: ""
   tags: []
   domain: ""
   setup:
     model: ""
     dataset: ""
     hardware: ""
     framework: ""
   metrics: []
   baseline: ""
   outcome: ""                # 留空，由 /exp-run Phase 4 填写 — succeeded | failed | inconclusive
   key_result: ""             # 留空，由 /exp-run Phase 4 填写
   linked_idea: "{idea-slug}" # 必填：源 idea slug（与 wiki/ideas/{idea-slug}.md 的 linked_experiments 互为双向链接）
   date_planned: YYYY-MM-DD
   date_completed: ""         # 留空，由 /exp-run Phase 4 填写
   run_log: ""                # 留空，由 /exp-run Phase 2 填写
   started: ""                # 留空，由 /exp-run Phase 2 填写（ISO 时间戳，通过 set-meta）
   estimated_hours: 0         # 0，由 /exp-run Phase 2 更新（通过 set-meta）
   remote:                    # 完整 block 必须存在，以便 /exp-run --env remote 通过 Edit 填充子字段
     server: ""
     gpu: ""
     session: ""
     started: ""
     completed: ""
   ---

   ## Objective
   {what this experiment proves}

   ## Setup
   {detailed setup: model, dataset, hardware, hyperparameters}

   ## Procedure
   {step-by-step execution plan}

   ## Results
   (to be filled after /exp-run)

   ## Analysis
   (to be filled after /exp-run)

   ## Claim updates
   (to be filled after /exp-eval)

   ## Follow-up
   {contingency plans: what to do if success / failure}
   ```

2. **创建新 claims（若 Step 2 中发现缺失的 claims）**：
   ```bash
   python3 tools/research_wiki.py slug "<claim-title>"
   ```
   创建 `wiki/claims/{slug}.md`（status: proposed, confidence: 0.3）

3. **添加 graph edges**：
   ```bash
   # 对每个实验 → 目标 claim
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "claims/{target-claim}" --to "experiments/{slug}" \
     --type tested_by --evidence "Designed by /exp-design"
   ```

4. **更新 idea 页面**（若 idea 来自 wiki）：
   - 在 `wiki/ideas/{idea-slug}.md` 的 `linked_experiments` 追加所有新建实验的 slugs
   - 若 idea status 为 `proposed`，更新为 `in_progress`

5. **更新 index.md**：在 experiments 和 claims（若新建）类别下追加条目

6. **重建派生数据**：
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

7. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-design | {N} experiments designed for idea {slug} | claims: {claim-list}"
   ```

8. **输出 EXPERIMENT_PLAN_REPORT 到终端**：
   ```markdown
   # Experiment Plan Report

   ## Target Idea
   - Idea: [[idea-slug]]
   - Hypothesis: {hypothesis}

   ## Scoped Claims
   | Claim | Current status | Confidence | Dimension |
   |-------|---------------|------------|-----------|
   | [[claim-slug]] | proposed | 0.3 | target |
   | [[claim-slug]] | weakly_supported | 0.5 | decomposition |

   ## Experiment Blocks
   | # | Experiment | Type | Claim | GPU-hrs | Stage |
   |---|-----------|------|-------|---------|-------|
   | 1 | [[baseline-slug]] | baseline | — | 2 | 1 |
   | 2 | [[validation-slug]] | validation | target | 8 | 2 |
   | 3 | [[ablation-1-slug]] | ablation | decomposition-1 | 8 | 3 |
   | 4 | [[robustness-slug]] | robustness | target | 16 | 4 |

   ## Run Order
   Stage 0: Sanity → Stage 1: Baseline → Stage 2: Validation → Stage 3: Ablation → Stage 4: Robustness
   Decision gates at each stage boundary.

   ## Budget
   - Total estimated: {N} GPU-hours
   - Budget limit: {--budget or "unlimited"}

   ## Next Steps
   - Run `/exp-run [[baseline-slug]]` to start Stage 1
   - After each stage, run `/exp-eval` to update wiki
   ```

## Constraints

- **每个实验必须关联 claim**：`target_claim` 不能为空（baseline 实验可关联 Target claim）
- **实验不可重复**：创建前检查 wiki/experiments/ 中是否已存在相同 target_claim + hypothesis 的实验
- **claims 界定后不修改**：Step 2 界定的 claims 在本次计划中不修改 status/confidence，只有 /exp-eval 可以修改
- **success criterion 必须量化**：每个实验块的成功标准必须包含具体数值（如 "> 2% accuracy improvement"）
- **至少 3 个 seeds**：需要统计可靠性的实验（validation, ablation）必须指定 >= 3 个 random seeds
- **graph edges 使用 tools/research_wiki.py**：不手动编辑 edges.jsonl
- **idea status 只能前进**：proposed → in_progress，不可逆
- **slug 唯一性**：创建前检查是否存在相同 slug

## Error Handling

- **idea 找不到**：提示用户检查 slug，列出 wiki/ideas/ 中的候选
- **目标 claim 不存在**：自动创建新 claim 页面（status: proposed, confidence: 0.3），在报告中标注
- **已有相似实验**：列出已有实验，询问用户是继续追加还是跳过
- **Review LLM 不可用**（--review 模式）：跳过 Step 5，在报告中标注「unreviewed — Review LLM unavailable」
- **budget 不足**：削减 Stage 4 robustness 实验范围，在报告中标注实际预算分配
- **slug 冲突**：追加数字后缀（如 `sparse-lora-ablation-v2`）
- **wiki 为空**：正常执行但 baseline 实验无法参考已有结果，在报告中建议先 /ingest 相关论文

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — 生成 slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建 query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建 gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志

### MCP Servers
- `mcp__llm-review__chat` — Step 5 实验计划审查（可选）

### Claude Code Native
- `Read` — 读取 wiki 页面
- `Glob` — 查找已有实验和 claims

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Step 5 Review LLM 审查独立性（若启用）

### Called by
- `/research` Stage 2（实验设计阶段）
- 用户手动调用
