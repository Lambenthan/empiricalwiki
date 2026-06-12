---
title: "引理2：有限最优持股 α*=ν/(ν+1)，监督与卖量非单调"
slug: "edmans-lemma2-finite-optimal-block"
proposition_type: comparative_statics
formal_statement: "LEMMA 2. The maximum sale volume β is given by β = α* = ν/(ν + 1). Blockholder effort μ is also maximized when α = α*. Both β and μ are increasing in α if α < α*, and decreasing in α if α > α*."
conditions: "短卖约束 β ≤ α；λ = 1/(ν(1−α))。当 α ≤ 1/λ 时 β = α（流动性足够高，B 卖光持股）；当 α > α* 时 β = 1/λ（流动性过低，B 仅卖 1/λ）。"
proof_technique: "对 β = min(1/λ, α) 分段求极值：α 较小段 β = α 随 α 升；α 较大段流动性 λ = 1/(ν(1−α)) 随 α 升导致 1/λ 随 α 降。两段交点 α* = ν/(ν+1)。"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
predicts: [block-size-concave-price-efficiency]
date_updated: 2026-06-03
---

## Statement

> LEMMA 2. The maximum sale volume β is given by β = α* = ν/(ν + 1). Blockholder effort μ is also maximized when α = α*. Both β and μ are increasing in α if α < α*, and decreasing in α if α > α*.

## Conditions

- α<α*=ν/(ν+1)：流动性相对充足（α≤1/λ），B 可卖光持股，β=α 随 α 上升。
- α>α*：流动性过低，B 只卖 1/λ；进一步增持反而压低流动性、减少可交易量，β=1/λ 随 α 下降。
- 监督努力 μ=βX/4c 与 β 同向，故也在 α* 处达峰。

## Proof Sketch

β=min(1/λ, α) 的两支在 α*=ν/(ν+1) 相交（代入 λ=1/(ν(1−α)) 解 α=1/λ）。α<α* 段，更大持股抬高坏消息时的可卖量、从而抬高事前信息收集激励；α>α* 段，增持的负流动性效应主导，可交易量与监督努力双双下降。故信息获取在有限持股处最大化。

## Comparative Statics

最优持股 α*=ν/(ν+1) 随流动性参数 ν 上升而上升。重要的不是持股本身，而是引致的最优交易量 min(1/λ, α)——大股东持股对企业的影响因此关于 α 呈倒 U 型。

## Testable Implications

- 私有信息含量、交易利润随持股呈凹形（倒 U）→ [[block-size-concave-price-efficiency]]。
- 有限最优持股与"美国大股东普遍存在但巨型大股东罕见"（La Porta et al. 1999、Holderness 2008）的事实一致：大持股不仅非必要，甚至可能有害。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-short-sales-constraint]]
- [[edmans-prop1-market-efficiency]]
