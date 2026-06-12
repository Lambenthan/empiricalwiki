---
title: "流动性交易需求服从指数分布"
slug: "edmans-exponential-liquidity-demand"
assumption_type: information
formal_statement: "Also at t = 2, liquidity traders demand u, where u is exponentially distributed, i.e. f(u) = 0 if u ≤ 0, λe^(−λu) if u > 0, where λ = 1/(ν(1−α)) and ν ≤ 1 is a liquidity parameter. The competitive market maker sees total demand d = b + u and sets a price P equal to the conditional expectation of V given d and s, similar to Kyle (1985)."
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
relaxed_in: []
date_updated: 2026-06-03
---

## Statement

t=2 流动性交易者需求 u 服从指数分布，f(u)=λe^(−λu)（u>0），其中 λ=1/(ν(1−α))，ν≤1 为流动性参数。竞争性做市商观察总需求 d=b+u，定价 P=E[V|d,s]（Kyle 1985 式）。

## Role in Model

指数分布是为可解性服务的关键设定：它让 B 的卖出量能闭式求解为持股的函数。Edmans 指出，在多数把 Kyle 模型用于公司金融的文献里，企业价值是二元的，知情者的订单无法求解，只能外生限定其交易量；指数分布的"无记忆"性质恰好让交易量内生化为 β=min(1/λ, α)。均值 E(u)=1/λ=ν(1−α)，自然刻画了"流动性交易量随小股东持股 1−α 上升"。

## Why It Matters

流动性参数 ν 是后半篇比较静态的核心：ν 既影响 B 的可交易量（交易效应），又影响其交易被噪声掩盖的程度（伪装效应），二者反向，产生流动性对投资的非单调影响（[[edmans-prop3-liquidity-exogenous-block]]）。作者强调，"block size 影响在坏消息时的卖出能力、从而影响监督激励"这一核心思想不依赖 u 的具体函数形式，指数分布只为闭式解。注意 λ 同时含 α，故持股通过 λ 影响流动性。

## Variants Across Papers

Kyle (1985) 用正态流动性需求 + 正态企业价值获得可解性；Barlevy-Veronesi (2000) 亦用指数分布。本文是"二元企业价值 + 指数流动性需求"的组合。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[kyle-1985-informed-trading]]
