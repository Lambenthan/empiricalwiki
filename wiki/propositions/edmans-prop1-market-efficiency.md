---
title: "命题1（市场效率）：π_X 在有限持股 α* 处最大化"
slug: "edmans-prop1-market-efficiency"
proposition_type: comparative_statics
formal_statement: "PROPOSITION 1 (Market Efficiency): Market efficiency π_X is maximized at α = α*. It is increasing in α for α < α*, and decreasing in α for α > α*."
conditions: "市场效率度量 π_X = ½(μ²·(1−e^(−λβ))/(1+e^(−λβ)) + 1)，π_X = 1 表示价格等于基本面、市场完全有效。α* = ν/(ν+1)（见引理2）。"
proof_technique: "对 π_X 关于 α 求导，分解为三项：trading effect（α 直接抬高卖量，α<α* 时为正）、camouflage effect（α 降低流动性、增强价格冲击，恒正）、effort effect（α 经由 μ，α<α* 时为正）。α<α* 三效应皆正；α>α* 时负交易效应恰好抵消正伪装效应，仅余负努力效应。Q.E.D."
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
predicts: [block-size-concave-price-efficiency]
date_updated: 2026-06-03
---

## Statement

> PROPOSITION 1 (Market Efficiency): Market efficiency π_X is maximized at α = α*. It is increasing in α for α < α*, and decreasing in α for α > α*.

## Conditions

- 市场效率 π_X=½(μ²·(1−e^(−λβ))/(1+e^(−λβ))+1)（eq 7），度量高质量企业期望价格与基本面 X 的接近程度；π_X=1 即完全有效。
- α*=ν/(ν+1)。

## Proof Sketch

∂π_X/∂α 分解为三项（eq 8）：

- **trading effect**：α 直接抬高 B 的卖量 β，使其交易（或不交易）向价格注入更多信息——当 α<α* 时为正。
- **camouflage effect**：α 通过降低流动性增强 B 的价格冲击——对所有 α 恒正。
- **effort effect**：α 经由 μ 起作用，μ 更高 → 信号更精——当 ∂μ/∂α>0 即 α<α* 时为正。

α<α* 时三效应皆正；α>α* 时（β=1/λ）负的交易效应恰好抵消正的伪装效应，只剩负的努力效应（eq 9）。故 π_X 在 α* 处唯一达峰。

## Comparative Statics

价格效率关于持股呈倒 U，峰值在 α*=ν/(ν+1)。与 Holmstrom-Tirole (1993)、Bolton-von Thadden (1998)（效率在零持股处最大）相反——本文即便只看价格效率，最优持股也是有限正值。

## Testable Implications

集中持股的私有信息含量、价格效率随 block size 呈凹形 → [[block-size-concave-price-efficiency]]；Bushee-Goodman (2007) 发现机构交易的私有信息含量随持股上升，与之一致。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-lemma2-finite-optimal-block]]
- [[edmans-prop2-investment]]
