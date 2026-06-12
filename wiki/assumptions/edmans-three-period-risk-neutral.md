---
title: "三期、风险中性、公开信号不完全揭示基本面"
slug: "edmans-three-period-risk-neutral"
assumption_type: timing
formal_statement: "I consider a firm with one share outstanding. A blockholder (B) owns α units and atomistic shareholders collectively own the remaining 1 − α. All agents are risk-neutral and the risk-free rate is normalized to zero. There are three periods. At t = 1, a public signal s ∈ {s_g, s_b} is released, such as an earnings announcement. It is imperfectly informative about the firm's fundamental value V, which is revealed at t = 3. If s = s_g, V = X > 0 with certainty; if s = s_b, V = 0 or X with equal probability."
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
relaxed_in: []
date_updated: 2026-06-03
---

## Statement

企业有 1 单位流通股，大股东 B 持 α、小股东持 1−α；所有参与人风险中性，无风险利率为零。三期结构：t=1 释放公开信号 s∈{s_g, s_b}（如盈余公告），对 t=3 才揭晓的基本面 V 不完全 informative。好信号 s_g → V=X 确定；坏信号 s_b → V=0 或 X 各半。

## Role in Model

风险中性 + 信号不完全揭示，给"知情交易能改善价格效率"留出空间：s_b 之后市场不能确定企业是低质量还是做了长期投资，B 的私有信息因此有价值。三期时序把"t=2 交易/定价"与"t=3 基本面实现"分开，使 t=2 股价可以偏离基本面，从而 t=0 的经理投资决策会受 t=2 股价（即市场效率）影响。

## Why It Matters

若信号完全揭示 V（s_g 情形），做市商直接定价 P=X，B 无监督与交易激励——模型显式聚焦 s=s_b 的有趣情形。风险中性简化了支付，引入经理风险厌恶只会强化结论（大股东降低高质量企业 s_b 时的价格方差）。

## Variants Across Papers

Stein (1988) [[stein-asymmetric-information]] 同样用"经理/外部人信息不对称 + 长期资产时序"搭建短视，但其信号渠道是 t=1 卖油抬当期盈利；Edmans 把不对称放进 Kyle 式市场微观结构，信号经由大股东交易注入价格。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[kyle-1985-informed-trading]]
