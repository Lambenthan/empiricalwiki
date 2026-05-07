# /discover wiki dedup

传入 `--wiki-root wiki` 时，`tools/discover.py` 会对已存在于 wiki 的论文做 dedup。本文说明这一层能抓到什么、抓不到什么，方便 user-facing report 准确反映情况。

## 能抓到的情况

对每条候选，`tools/discover.py` 从候选记录里抽出 `arxiv_id`（S2 的 `externalIds.ArXiv`、DeepXiv 的 `arxiv_id` 等），然后检查是否存在某个 `wiki/papers/*.md` 页面 frontmatter 中 `arxiv`（或旧版 `arxiv_id`）与之匹配。命中的候选在打分前被剔除，数量以 `wiki_dedup_count` 字段汇报。

这覆盖典型场景：某篇已 ingest 的论文又被当推荐冒上来。把它继续展示给用户是浪费 review 时间，剔掉是对的。

## 抓不到的情况

- **仅标题匹配**：wiki 里一篇没有 `arxiv` 或 `arxiv_id` 的论文（如通过 `/edit` ingest 的期刊文章）不会与同标题候选匹配。这是有意为之 —— 模糊标题匹配会引入假阳，反而遮蔽合法候选。
- **arXiv 版本号差异**：`2106.09685` 与 `2106.09685v3` 应视为同一篇。frontmatter 解析器会剥 `arxiv:`/`ARXIV:` 前缀，但目前不剥 `vN` 后缀。如果发现重复漏过，需要在候选的 `arxiv_id` 比对前先规范化掉版本后缀。
- **候选集内部的跨源重复**：wiki 过滤前的 dedup pass 使用 `_candidate_key`（arxiv → S2 paperId → title-slug 顺序），能抓住 S2 与 DeepXiv 之间的大多数跨源重复。完全缺失 ID 与 title 的记录会被静默丢弃。

## 遇到 "高 dedup" 如何处理

若 `wiki_dedup_count` 相对 `candidates_total` 偏高（例如 50 里有 30），说明这个 anchor / topic 附近 wiki 已经覆盖得差不多了。两种解读：

1. 用户是在找广度，应该换个 seed（另一个 anchor、更宽的 topic，或用 `--from-wiki` 去探索邻近论文）。
2. 推荐通道本身已经饱和 —— 这个邻域确实没什么可新增的。

skill 应该在给用户的 report 里提及高 dedup，不要隐藏。

## dedup 不做的事

`/discover` 从不为了 "修" 某个 duplicate 而修改 wiki。如果候选的 metadata 看起来比 wiki 现有版本更丰富，那属于 `/edit` 或 `/check` 的职责，不属于 `/discover`。
