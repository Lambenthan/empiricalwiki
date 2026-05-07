# /ingest 去重策略

准备新建或更新一个 concept、claim，或 foundation 链接前，打开此参考。

## 心智模型

一个健康的 ΩmegaWiki 里，claim 与 concept 的数量远少于 paper。每个 concept 由许多深化或扩展它的 paper 共享；每个 claim 由许多提供 evidence 的 paper 支持。如果 `/ingest` 默认为每篇论文都新建 concept / claim，wiki 会迅速沦为一堆近似重复的页面 —— 综述生成、gap 检测、idea novelty、citation 推理全部会被这种噪声破坏。

默认动作是**合并**。例外才是**新建**，并且每次新建都必须有清晰的理由。

## 何时打开此参考

- `/ingest` Step 4：识别论文支持的 claims 时。
- `/ingest` Step 4：识别论文引入或扩展的 concepts 时。
- 任何想"为保险起见"新建 concept / claim 却没先查重的时刻。

## 强制工具调用

新建 concept 或 claim 前，先调用对应的去重工具：

```bash
"$PYTHON_BIN" tools/research_wiki.py find-similar-concept wiki/ "<candidate title>" --aliases "<a,b,c>"
"$PYTHON_BIN" tools/research_wiki.py find-similar-claim   wiki/ "<candidate title>" --tags    "<a,b,c>"
```

两个工具都返回按相似度排序的 JSON 列表。`find-similar-concept` 同时扫描 `wiki/concepts/` 与 `wiki/foundations/`，并给每条结果打 `entity_type` 标签。工具是相似度的真相来源；不要用肉眼重新估算分数。

跳过这两个工具是 wiki 膨胀最常见的原因。即便你觉得本 session 早些时候已经读过相关页面，也仍要调用工具 —— 换句话说的近似重复很容易从人工扫描里滑过。

## 决策规则

读取 top 结果的 `score`。

- **top 结果是 foundation 且 score ≥ 0.40** —— 走 foundation link 路径。候选是教科书级背景知识，不是新机制。在 `edges.jsonl` 写一条 `derived_from` edge，在 paper 的 `## Related` 里写 `[[foundation-slug]]`。不得修改 foundation 页面（foundation 是终端节点，见 `references/cross-references.md`）。foundation link 不计入每篇论文的新建上限。
- **score ≥ 0.80** —— 合并。候选与 top 是同一概念 / 主张。在 top 的 `key_papers` 或 `evidence` 上追加本论文，补 graph edge，写反向链接。concept 默认用 `uses_concept`；只有论文实质修改、泛化或特化该 concept 时才用 `extends_concept`；只有明确批评时才用 `critiques_concept`。不要新建文件。
- **score 0.40–0.80** —— 阅读 top 的 `## Definition` / `## Statement` 再决定。默认合并。只有当你能指出具体的技术差异时才新建：不同机制、不同数学形式、真正不同的命题。若候选是已有 concept 的有意义子类，合并并在 `## Variants` 追加一条 bullet，而不是拆分。
- **score < 0.40 或结果为空** —— 无已有匹配。允许新建，但要遵守下面的每篇上限。

过度合并代价低：合并错了的页面可以日后拆分，历史保留。过度新建代价高：近似重复会静默污染所有下游 skill，事后难以察觉。

## 每篇论文的新建上限

上限的目的是让默认行为保守。它不是要填满的配额。

- importance < 4：最多 **1** 个新 concept、**1** 个新 claim
- importance ≥ 4：最多 **3** 个新 concept、**2** 个新 claim
- foundation link 不计入。

后续候选若会超过上限，就合并到最接近的 `find-similar-*` 结果 —— 即使其分数低于通常的合并阈值。若确实没有可安全合并的候选，就整体跳过该实体 —— `/check` 会在后续扫描里把缺口暴露出来，用户可决定是否 `/edit` 补齐。

## 只做形状检查，不做语义审计

确实要新建或编辑 concept / claim 页面时，对它跑与 paper 页面相同的狭窄形状检查：

- 每个必需 frontmatter 字段存在且非空
- concept：`maturity` ∈ {`stable`, `active`, `emerging`, `deprecated`}
- claim：`status` ∈ {`proposed`, `weakly_supported`, `supported`, `challenged`, `deprecated`}，`confidence` ∈ [0,1]
- YAML 可解析

该检查能避免 `/check` 下一轮把明显残缺的页面全部捞出。超出这个范围的一切 —— 反向链接对称性、claim evidence 是否足以支撑 status、concept 的 `part_of` topic 是否被对向引用 —— 属于 `/check`。把这些审计搬进 `/ingest` 只会拖慢 skill 并与 `/check` 做重复工作。

## `/check` 负责的、`/ingest` 不负责的

- 跨实体反向链接对称性（A 链接到 B ⇒ B 是否链回 A）
- dangling node 检测（被引用但缺失的页面，或存在但不可达的页面）
- claim 与 experiment 的 status / confidence 一致性
- edge 类型合法性与 edge 去重
- 上述一切的分级修复建议

你可以信任 `/check` 去发现这些并产出修复报告。`/ingest` 聚焦在**写入点**做出 well-shaped 的实体与正确的正向/反向链接即可。
