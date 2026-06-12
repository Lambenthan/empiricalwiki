---
title: "命题2：不知情收购者下福利非单调、可致事前福利损失"
slug: "stein-prop2-welfare-nonmonotonic"
proposition_type: welfare
formal_statement: "PROPOSITION 2. With uninformed raiders, (a) welfare is not monotonic in c, and (b) takeovers can lead to ex ante welfare losses, whether shareholders are patient or not."
conditions: "收购者不知情。降低 c 至临界（耐心股东 c_p、不耐心股东 c_s）时经理开始短视，事前福利离散下跌 prx₂（信号概率 × 浪费资源）。"
proof_technique: "反例构造（如 c=0、v 非随机且小于 (1+r)(x₁−x₂)）；比较有限 c 与无穷 c 的事前社会福利。"
source_papers: [stein-1988-takeover-threats-managerial-myopia]
predicts: []
date_updated: 2026-05-29
---

## Statement

> PROPOSITION 2. With uninformed raiders, (a) welfare is not monotonic in c, and (b) takeovers can lead to ex ante welfare losses, whether shareholders are patient or not.

## Conditions

当收购成本 c 下降越过临界（耐心股东在 c_p、不耐心股东在 c_s），经理开始短视，事前社会福利出现 `prx₂` 的离散下跌（信号发生概率 × 信号浪费的资源）。

## Proof Sketch

反例：设 c=0、v 非随机且 v < (1+r)(x₁−x₂)，则收购概率为 1，信号必然发生。当协同收益 v 小于信号成本 prx₂ 时，`v − prx₂ < 0`，"收购成本无穷（禁止收购）"反而优于"零收购成本"。

## Comparative Statics

直接反驳"放任收购市场总是社会最优"（Grossman-Hart 1980、Easterbrook-Fischel 1981 等的精神）。

## Testable Implications

收购压力对长期投资的净效应可能为负；不能仅凭"收购创造协同价值"推断放松收购市场是好政策。

## Related

- [[stein-1988-takeover-threats-managerial-myopia]]
- [[stein-prop5-informed-no-welfare-loss]]（知情情形对照）
