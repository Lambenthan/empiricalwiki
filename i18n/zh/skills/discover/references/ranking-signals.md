# /discover ranking 信号

确定性 ranking 住在 `tools/discover.py`，本文件记录它权衡什么、以及**为什么与 `/init` 不同**，防止后续修改不小心把二者收敛到一起。

## Anchor 模式的三个候选通道

anchor 模式每个 anchor 默认从 **三个** S2 通道抓取，因为任何单通道都有其特征偏差：

- **`recommend`**（S2 语义推荐端点）—— 返回语义相似论文，但端点明显偏向最新工作。单用它会退化成 "这个 topic 附近的最新论文"，与 `/daily-arxiv` 严重重合。
- **`references`**（anchor 引用的论文）—— 暴露 anchor 站在其肩膀上的**老 canonical 工作**，是文献综述通道。
- **`citations`**（引用 anchor 的论文）—— 暴露在 anchor 之上的**高影响后续工作**。

三者合起来才是一次真正的文献图游走：语义邻居 + 祖先 + 后代。去掉任何一个通道都是明显的质量倒退。只有在 API 成本确实是约束时（例如 anchor 太多而 recommend 已经够用），才通过 `--no-citation-expand` 砍掉 references+citations 通道。

## discovery 的打分依据

Anchor 模式（按大致权重排序）：

1. **聚合 influential citation count** —— 对数缩放，反映候选在整个领域的声望。权重高于原始 `citationCount`。
2. **Anchor-influence edge** —— S2 的 per-edge `isInfluential` 标记，从 `references`/`citations` envelope 抽到候选上作为 `is_influential_edge`。为 True 时，意味着 S2 的引用分析模型判断：anchor 实质性地构建在这个候选之上（references 通道）或这个候选实质性地构建在 anchor 之上（citations 通道）。比聚合计数尖锐得多：它告诉你 "这一篇对 anchor 具体有意义"，而不是 "这一篇对领域有意义"。S2 的这个标记比较严格，大多数情况为 False；但一旦为 True，就应该起主导作用。
3. **Anchor overlap** —— 候选被几个 anchor 同时命中。两个 anchor 都指向同一篇论文，说明它正在它们的交集上。
4. **Channel diversity** —— 同一候选出现在多个通道（如同时出现在 `recommend` 与 `references`）时给 bonus。三通道全中的候选罕见，通常是 anchor 邻域里的核心论文。
5. **Freshness** —— 对较新的年份给轻微 bonus。新 ≠ 更好，曲线较平（1.0 / 0.85 / 0.6 / 0.4 / 0.25，按年龄分桶）。
6. **Author h-index**（作者最大值）—— 有上限的 tiebreaker。list endpoint 不返回 `authors.hIndex`，因此这个信号主要在 topic 模式下通过 `/paper/{id}` 单点 API 才会点亮。

Topic / wiki 模式：相同信号，去掉 anchor overlap 与 anchor-influence edge（topic 模式没有 anchor；wiki 模式的派生 anchor 仍有 edge 信号）。influence 与 freshness 权重相应抬高以补偿。

### 为什么同时使用聚合 influence 和 per-edge influence？

它们回答不同问题：

- `influentialCitationCount` = "领域里的论文有没有实质性地引用这篇？" —— 一般重要性的代理
- anchor edge 上的 `isInfluential` = "**这个 anchor** 是不是实质性地构建在这篇之上 / 被这篇实质性地构建？" —— anchor-specific 相关性的代理

一篇论文可能一个高一个低。例如：一个著名 benchmark 论文聚合计数很高（谁都在引用它）但很少在 method paper 的 anchor 边上标为 True（benchmark 是被使用，不是被构建之上）。我们的 ranking 同时用两者 —— 这样 benchmark 在没有更好信号时仍会浮上来，但 anchor 真正构建之上的论文会压过它们。

## discovery **不**打分的东西

这里是 `/discover` 有意与 `/init` planner（`tools/init_discovery.py`）分道扬镳之处：

- **不偏 survey**。`/init` 偏爱 survey/review 论文，因为空白 wiki 需要它们做 anchor 覆盖。`/discover` 被调用时用户通常已熟悉领域（anchor 模式）或在探索中（topic 模式），很少还需要再一篇 survey；把 survey 抬到新工作之前只会制造噪音。
- **不给 "older canonical anchor" 加 bonus**。`/init` bootstrap 模式会抬升一篇老的高被引论文以拓宽覆盖面。`/discover` 的用户通常想要前瞻性的推荐，而不是再做一次基础面 anchor。
- **不读 notes/web priority terms**。`/init` 会读 `raw/notes/` 与 `raw/web/` 抽取用户意图。`/discover` 不读 —— 它的输入是显式的（anchor、topic 或 wiki 状态）。

如果将来出现一个看起来 `/init` 和 `/discover` 可以共享的 ranking 信号，**优先保持两份实现**，而不是抽出共享 scorer。目标确实不同，共享 scorer 会迫使其中一方妥协。

## list endpoint 的字段限制

`tools/fetch_s2.py` 使用两套字段集：

- `FIELDS` —— 完整 rich 字段集，仅 `/paper/{id}` 接受。包含 `authors.hIndex`、`tldr`。
- `FLAT_FIELDS` —— 扁平 authors，无 `tldr`，无嵌套 selector。其余所有 endpoint 都用这套：`/paper/search`、`/paper/{id}/citations`、`/paper/{id}/references`、recommendations endpoints。

list endpoints 会对嵌套 selector 返回 400 Bad Request —— 开发期间真实踩过这个坑，所以留下两套字段集。不要把它们合并回去。

实际影响：从 list 通道进来的候选，rationale 里不带 `hIndex` 与 `tldr`。理论上对每个候选再 `fetch_s2.paper(arxiv_id)` 一次可以 enrich，但 discovery 工具有意不做 —— 这会把每次运行的成本乘以 (shortlist_size × latency)，只为了让 rationale 看起来更丰富一点。用户选中某个候选去 `/ingest` 时再 enrich 就够了。
