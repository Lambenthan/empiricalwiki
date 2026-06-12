---
title: "短卖约束：大股东只能卖出已持份额（β ≤ α）"
slug: "edmans-short-sales-constraint"
assumption_type: constraint
formal_statement: "B either demands nothing (b = 0) or sells β units (b = −β). B sells if she receives signal i_b and holds otherwise. I assume β ≤ α owing to short-sales constraints, since this paper's focus is non-interventionist financial blockholders such as mutual funds, pension funds and insurance companies, the vast majority of which are unable to sell short."
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
relaxed_in: ["Edmans (2009) Section I.A 与 Online Appendix：允许非平凡短卖成本，结论不变"]
date_updated: 2026-06-03
---

## Statement

大股东 B 只能"不交易"或"卖出 β 单位"，且受短卖约束 β≤α——她至多卖光初始持股。理由是本文聚焦非干预型金融大股东（共同基金、养老金、保险），其绝大多数无法卖空。

## Role in Model

这是把**持股规模 α 与信息获取激励挂钩**的核心建模手法。在标准 Kyle (1985) 类无约束模型里，投资者卖空能力与持股无关，故监督激励独立于初始持股。加上短卖约束后：α 越大，B 在坏消息时能卖的越多，事前收集信息的激励越强（α<α* 段）。这正是大量实证研究"用持股规模代理投资者知情程度"的理论支撑（Boehmer-Kelley 2008、Rubin 2007）。

## Why It Matters

去掉短卖约束，"block size → 信息 → 价格效率"的整条链断裂，倒 U 型最优持股（[[edmans-lemma2-finite-optimal-block]]）也不复存在。约束的另一面是：α 过大反而压低流动性、减少可交易量，于是激励先升后降，产生有限最优持股 α*。Section I.A 表明，对冲基金式"有成本短卖"下结论依然成立。

## Variants Across Papers

干预型大股东模型（Shleifer-Vishny 1986、Maug 1998、Kahn-Winton 1998）不需此约束，因为它们的价值创造来自 voice 而非 exit；Edmans 的短卖约束正是"退出型治理"区别于"干预型治理"的建模分水岭。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-lemma2-finite-optimal-block]]
- [[governance-through-trading-exit]]
