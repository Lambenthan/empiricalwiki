# /ingest 交叉引用

在任何 wiki 页面上写链接时，打开此参考。每一条正向链接都有反向义务（指向 foundation 的除外）。下表是合同。

## 正向 → 反向义务

对应根 `CLAUDE.md`（"Cross-Reference 规则"）中的矩阵，裁剪到 `/ingest` 实际写入的 edge：

| 正向操作（你在页面 A 上写什么） | 必须同步的反向操作（在同一 turn 里你在页面 B 上写什么） |
|--------------------------------|--------------------------------------------------------|
| `papers/P` 写 `Related: [[concept-K]]` | `concepts/K` 的 `key_papers` 追加 `P` |
| `papers/P` 写 `[[person-R]]`（Key authors 段） | `people/R` 的 `Key papers` 追加 `P` |
| `papers/P` 写 `supports: [[claim-C]]` | `claims/C` 的 `evidence` 追加 `{source: P, type: supports}` |
| `papers/P` 写 `supports: [[claim-C]]` 但论文实际反驳该 claim | 在 evidence 条目里用 `type: contradicts` |
| `claims/C` 写 `source_papers: [[paper-P]]` | `papers/P` 的 `## Related` 追加 `C` |
| `concepts/K` 写 `key_papers: [[paper-P]]` | `papers/P` 的 `## Related` 追加 `K` |
| 任意页面写 `[[foundation-X]]` | **不写反向链接** —— foundation 是终端节点 |

写了正向却没写反向，是 `/check` 报 `missing-field` 的最常见来源。把两边放在同一 turn 内做，整类错误就被消灭。

## Foundation 是终端节点

`/ingest` 不得修改 foundation 页面。没有 `key_papers` 字段，也没有任何形式的反向引用。一篇论文链到 foundation，只留下两处痕迹：

- 论文页面 `## Related` 中的 `[[foundation-slug]]`
- `wiki/graph/edges.jsonl` 中一条 `paper → foundation`、type 为 `derived_from` 的 edge

foundation 仅由 `/prefill` 创建。`/ingest` 永远不新建 foundation —— 即便某个 concept 候选看起来像是 foundational 却没有匹配。这种情况下，走普通 concept 路径（必要时新建 concept 页面），让用户日后需要时自行 seed foundation。

## paper-to-paper edge

只有当被引用的论文已经在 `wiki/papers/` 下有页面时，才写出 paper-to-paper edge。不要臆测：若引用尚未 ingest，就跳过该 edge，并在最终报告中把它列为后续 `/ingest` 候选。

edge 类型选择（按信号）：

- **`extends`** —— 论文明确在被引论文的方法之上构建。如 "we extend"、"building on"、"we follow X but"。
- **`supersedes`** —— 论文在相同任务上以相同术语系统声称取代被引 baseline（更强结果或更干净的形式化），并把它定位为应被替换对象。仅用于显式主张；不得仅凭 benchmark 表格推断。
- **`inspired_by`** —— 论文把先前工作作为动机或概念渊源引用，但并不直接在其方法之上构建。常见于综述式或跨领域借鉴。
- **`contradicts`** —— 论文显式反驳被引发现，要么复现失败，要么给出直接反例。必须有论文中明确语句作为依据。
- **无 / 跳过** —— 以上都不能干净对应时，跳过。graph 噪声比缺一条 edge 更糟。

每一对有序的 paper 之间一条 edge 即可。两种类型之间犹豫时，选较弱的那个（`inspired_by` 优于 `extends`，`extends` 优于 `supersedes`）。

## 正反两侧原子写入

`/ingest` 写的每一条链接，反向都应在同一 turn 内落地。具体做法：

1. 决定建立此链接。
2. 在源页面写正向条目。
3. 在目标页面写反向条目。
4. 若该链接对应一条 graph edge（paper↔concept、paper↔claim、paper↔paper、paper→foundation），通过 `tools/research_wiki.py add-edge` 写出。

这种做法让 `/check` 下一轮不会报半吊子链接。也让回滚变简单：若某篇论文 ingest 被中止，直接撤销该论文的编辑就能把两侧同时撤销。

## `/ingest` 在此处不做的检查

`/ingest` 边写边写反向链接，但不会审计 wiki 中既有链接是否仍有反向。那是全图审计，属于 `/check`。不要在 ingest 过程中全量读 `wiki/` 去查已有的反向缺失 —— 时间与 token 成本都不小，而且与 `/check` 做重复工作。
