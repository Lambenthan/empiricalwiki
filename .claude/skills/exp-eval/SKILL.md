---
description: 实验判决门：Review LLM 独立评判实验结果 → 4 种判决路径 → 自动更新 claims confidence、ideas status、graph edges
argument-hint: <experiment-slug> [--auto]
---

# /exp-eval

> 将已完成实验的结果转化为 wiki 知识更新。
> Review LLM 作为 impartial judge（遵循 cross-model-review），独立评估实验结果对目标 claim 的影响。
> 4 种判决路径：supported → claim↑ + idea validated / partially_supported → 补充实验 /
> not_supported → claim↓ + idea failed / inconclusive → debug。
> 自动更新 claims 的 confidence 和 evidence、ideas 的 status、graph edges。

## Inputs

- `experiment`：wiki/experiments/ 中的 slug（status 必须为 `completed`）
- `--auto`（可选）：自动模式，不暂停等待用户确认 wiki 更新（用于 /research 调用）

## Outputs

- `wiki/claims/{slug}.md` — 更新 confidence、status、evidence 列表
- `wiki/ideas/{slug}.md` — 更新 status（validated/failed）、pilot_result、failure_reason
- `wiki/experiments/{slug}.md` — 填充 `## Claim updates` section
- `wiki/graph/edges.jsonl` — 新增 supports/invalidates 边
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加日志
- **VERDICT_REPORT**（输出到终端）— 判决结果、wiki 变更摘要、下一步建议

## Wiki Interaction

### Reads
- `wiki/experiments/{slug}.md` — 实验结果：outcome、key_result、metrics、Results section
- `wiki/claims/{target-claim}.md` — 目标 claim 当前状态：status、confidence、evidence 列表
- `wiki/ideas/{linked-idea}.md` — 关联 idea 当前状态
- `wiki/experiments/*.md` — 同一 claim 的其他实验结果（综合评估）
- `wiki/graph/context_brief.md` — 全局上下文
- `.claude/skills/shared-references/cross-model-review.md` — 审稿独立性原则

### Writes
- `wiki/claims/{target-claim}.md` — 更新 status、confidence、evidence、date_updated
- `wiki/ideas/{linked-idea}.md` — 更新 status、pilot_result、failure_reason、date_resolved
- `wiki/experiments/{slug}.md` — 填充 `## Claim updates` section
- `wiki/graph/edges.jsonl` — 新增 supports 或 invalidates 边
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加操作日志

### Graph edges created
- `supports`：experiment → claim（实验支持该 claim）— verdict = supported 或 partially_supported
- `invalidates`：experiment → claim（实验否定该 claim）— verdict = not_supported

## Workflow

**前置**：
1. 确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）
2. 确认实验 status == `completed`（未完成的实验不能评判）

### Step 1: 加载上下文

1. **读取实验页面** `wiki/experiments/{slug}.md`：
   - outcome（succeeded/failed/inconclusive）
   - key_result
   - target_claim slug
   - linked_idea slug
   - metrics 和完整 Results section
   - hypothesis

2. **读取目标 claim** `wiki/claims/{target-claim}.md`：
   - 当前 status 和 confidence
   - 现有 evidence 列表
   - conditions and scope

3. **读取关联 idea** `wiki/ideas/{linked-idea}.md`（若存在）：
   - 当前 status
   - hypothesis

4. **加载同一 claim 的其他实验**：
   - Glob: `wiki/experiments/*.md`，过滤 target_claim == 同一 claim
   - 汇总已有实验结果（用于综合评估 claim confidence）

5. **读取全局上下文**：
   - `wiki/graph/context_brief.md`

6. **读取 cross-model-review.md**：确认 Review LLM 独立性原则

### Step 2: Review LLM 判决（Cross-Model Verdict）

**遵循 cross-model-review.md**：不向 Review LLM 发送 Claude 的预判。

```
mcp__llm-review__chat:
  system: "You are an impartial scientific judge evaluating whether experimental
           results support or refute a research claim. Be rigorous and objective.
           Consider: statistical significance, effect size, experimental validity,
           potential confounds, and whether the results generalize beyond the
           specific setup tested."
  message: |
    ## Claim Under Test
    Title: {claim title}
    Statement: {claim statement from ## Statement section}
    Current status: {status}
    Current confidence: {confidence}
    Conditions: {conditions and scope}

    ## Experiment
    Title: {experiment title}
    Hypothesis: {hypothesis}
    Setup: {model, dataset, hardware, framework}
    Metrics: {metrics list}

    ## Results
    {full Results section from experiment page}

    ## Key Finding
    {key_result}

    ## Other Experiments on This Claim
    {summary of other experiments' outcomes on the same claim, if any}

    ## Your Task
    Provide your verdict:
    1. **Verdict**: One of: supported / partially_supported / not_supported / inconclusive
    2. **Confidence adjustment**: Suggest new confidence value (0.0-1.0) with reasoning
    3. **Evidence strength**: weak / moderate / strong
    4. **Key reasoning**: 2-3 sentences explaining your verdict
    5. **Concerns**: Any methodological concerns or limitations
    6. **Suggested next steps**: What would strengthen or clarify this result?
```

记录 Review LLM 的判决。

### Step 3: Claude 综合评估

1. **独立形成 Claude 的判决**（在读取 Review LLM 判决后，Claude 也独立分析）：
   - 基于实验结果、claim 上下文、其他实验的综合证据
   - 形成 Claude 自己的 verdict 和 confidence 建议

2. **综合两个判决**（遵循 cross-model-review.md composing rules）：
   - **两者一致**（verdict 相同）：采用该 verdict，confidence 取均值，高置信度
   - **两者不一致**：
     - 明确标注分歧
     - 取更保守的 verdict（supported > partially_supported > not_supported）
     - confidence 取较低值
     - 在报告中详述分歧原因
   - **致命发现优先**：若任一方发现方法论问题（数据泄露、不公平比较），该发现优先

3. **确定最终判决**：verdict + new_confidence + evidence_strength

### Step 4: 根据判决更新 Wiki

**若 `--auto` 未设置**：先展示判决结果和计划变更，等待用户确认。

#### 路径 A: SUPPORTED（实验支持 claim）

1. **更新 claim**：
   - confidence: ↑ 调整到新值（通常 +0.1~0.3）
   - status: 根据新 confidence 调整
     - confidence >= 0.7 → `supported`
     - confidence 0.4-0.7 → `weakly_supported`
   - evidence: 追加新条目 `{source: experiment-slug, type: supports, strength: strong/moderate, detail: key_result}`
   - date_updated: 今天日期

2. **更新 idea**（若存在且 status 为 in_progress/tested）：
   - 若所有关联 claims 都 supported/weakly_supported：
     - status: `validated`
     - pilot_result: key_result 摘要
     - date_resolved: 今天日期

3. **添加 graph edge**：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "experiments/{slug}" --to "claims/{target-claim}" \
     --type supports --evidence "{key_result}"
   ```

4. **建议下一步**：`/paper-plan` 或继续 ablation/robustness 实验

#### 路径 B: PARTIALLY_SUPPORTED（部分支持）

1. **更新 claim**：
   - confidence: 小幅调整（+0.05~0.15）
   - evidence: 追加 `{type: supports, strength: weak, detail: ...}`
   - date_updated: 今天日期

2. **添加 graph edge**：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "experiments/{slug}" --to "claims/{target-claim}" \
     --type supports --evidence "Partially supported: {limitation}"
   ```

3. **建议补充实验**：
   - 明确缺少什么证据
   - 建议用 `/exp-design` 设计补充实验
   - 若 Review LLM 指出的 concern 可通过实验解决，具体建议实验方向

4. **idea status 不变**：保持 in_progress，等待更多证据

#### 路径 C: NOT_SUPPORTED（实验不支持 claim）

1. **更新 claim**：
   - confidence: ↓ 显著下调（通常 -0.2~0.4）
   - status: 若 confidence < 0.3 → `challenged`
   - evidence: 追加 `{type: invalidates, strength: strong/moderate, detail: ...}`
   - date_updated: 今天日期

2. **更新 idea**（若存在）：
   - status: `failed`
   - failure_reason: 具体失败原因（从实验结果和 Review LLM 分析中提取）
   - date_resolved: 今天日期
   - 注意：failure_reason 是 anti-repetition memory，必须写清楚为什么失败

3. **添加 graph edge**：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "experiments/{slug}" --to "claims/{target-claim}" \
     --type invalidates --evidence "{failure_reason}"
   ```

4. **建议下一步**：
   - 分析失败原因
   - 考虑 pivot（新 idea 解决同一 gap，避开已知失败原因）
   - 建议 `/ideate` 生成替代方案

#### 路径 D: INCONCLUSIVE（结果不确定）

1. **不修改 claim status/confidence**：证据不足以做判断

2. **更新实验页面**：outcome 已为 inconclusive（/exp-run 设置）

3. **建议 debug**：
   - 数据问题？实现 bug？错误的 metric？
   - 方差过大？需要更多 seeds？
   - 实验设置与 claim 不对齐？

4. **idea status 不变**：保持当前状态

#### 所有路径通用

1. **更新实验页面的 `## Claim updates` section**：
   ```markdown
   ## Claim updates
   - **Verdict**: {supported/partially_supported/not_supported/inconclusive}
   - **Claim**: [[{target-claim}]] confidence {old} → {new}
   - **Judge agreement**: {Claude and Review LLM agreed / disagreed on ...}
   - **Date**: YYYY-MM-DD
   ```

2. **更新 index.md**（若 claim status 变化）

3. **重建派生数据**：
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

4. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-eval | {slug} → {target-claim} | verdict: {verdict} | confidence: {old}→{new}"
   ```

5. **输出 VERDICT_REPORT 到终端**：
   ```markdown
   # Verdict Report: {experiment title}

   ## Verdict: {SUPPORTED / PARTIALLY_SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE}

   ## Judge Assessment
   | | Claude | Review LLM | Final |
   |---|-------|------|-------|
   | Verdict | {verdict} | {verdict} | {verdict} |
   | Confidence | {value} | {value} | {value} |
   | Evidence strength | {strength} | {strength} | {strength} |

   ## Key Reasoning
   {2-3 sentences from Review LLM + Claude synthesis}

   ## Wiki Changes
   | Entity | Field | Before | After |
   |--------|-------|--------|-------|
   | claims/{slug} | confidence | {old} | {new} |
   | claims/{slug} | status | {old} | {new} |
   | ideas/{slug} | status | {old} | {new} |

   ## Graph Edges Added
   - experiments/{slug} → claims/{target} (supports/invalidates)

   ## Concerns
   {methodological concerns from Review LLM}

   ## Next Steps
   - {path-specific suggestions}

   ## Wiki Growth
   | Metric | Before | After | Delta |
   |--------|--------|-------|-------|
   | Claims updated | — | — | {N} |
   | Edges | {before} | {after} | +{delta} |
   | Maturity | {level} | {level} | {unchanged/upgraded} |
   （数据来自 Step 1 开始时和 Step 4 结束后分别调用 `python3 tools/research_wiki.py maturity wiki/ --json` 的对比。）
   ```

## Constraints

- **只处理 completed 实验**：status != completed 的实验拒绝处理，提示用 /exp-run 先完成
- **审稿独立性**：严格遵循 cross-model-review.md，不向 Review LLM 发送 Claude 的预判
- **confidence 区间 0.0-1.0**：更新后的 confidence 不得超出此范围
- **failure_reason 必须具体**：not_supported 路径的 failure_reason 不能是空话（如 "实验失败"），必须写明具体原因
- **不直接删除 claims**：即使 not_supported，也只是 challenge 或降低 confidence，不删除 claim 页面。极端情况下（多次实验一致否定、confidence → 0），状态设为 deprecated 而非删除
- **graph edges 使用 tools/research_wiki.py**：不手动编辑 edges.jsonl
- **保守原则**：当 Claude 和 Review LLM 判决不一致时，取更保守的判决
- **idea 状态只前进**：proposed → in_progress → tested → validated/failed，不可逆
- **综合所有实验评估 claim**：不仅看当前实验，还要参考同一 claim 的其他实验结果

## Error Handling

- **experiment 找不到**：提示用户检查 slug，列出 wiki/experiments/ 中 status=completed 的候选
- **experiment 未完成**：提示 status，建议先运行 `/exp-run {slug}` 或 `/exp-run {slug} --check`
- **target claim 不存在**：创建新 claim 页面（status: proposed, confidence: 0.3），标注「auto-created by exp-eval」
- **linked idea 不存在**：跳过 idea 更新，仅更新 claim，在报告中标注
- **Review LLM 不可用**：降级为 Claude 单模型判决，在报告中标注「single-model verdict, cross-model verification unavailable」，建议用户稍后确认
- **claim 已被其他实验修改**：读取最新状态，基于当前 confidence 做调整（不覆盖其他实验的贡献）
- **结果数据缺失**：若实验页面的 Results section 为空，提示用户先运行 `/exp-run {slug} --check`

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建 query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建 gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志

### MCP Servers
- `mcp__llm-review__chat` — Step 2 Review LLM 独立判决

### Claude Code Native
- `Read` — 读取 wiki 页面
- `Glob` — 查找同一 claim 的其他实验
- `Edit` — 更新 wiki 页面

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Review LLM 独立性原则（必读）

### Called by
- `/research` Stage 4（判决与迭代阶段）
- 用户手动调用
