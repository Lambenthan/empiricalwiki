---
title: "代价高昂的监督：努力 μ 成本 ½cμ²，信号精度随 μ 上升"
slug: "edmans-costly-monitoring-precision"
assumption_type: technology
formal_statement: "At t = 2, B exerts monitoring effort μ ∈ [0, 1], at cost ½cμ². Monitoring gives B a private signal i ∈ {i_g, i_b} of V, the precision of which rises with μ as follows: Pr(i_g|X) = Pr(i_b|0) = ½ + ½μ, Pr(i_g|0) = Pr(i_b|X) = ½ − ½μ. The posterior probabilities that the firm is of high quality are thus given by: Pr(X|i_g) = (1+μ)/2, Pr(X|i_b) = (1−μ)/2 = π_b. If μ = 0, private information is completely uninformative and the posterior equals the prior ½; if μ = 1, B knows V with certainty."
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
relaxed_in: []
date_updated: 2026-06-03
---

## Statement

t=2 大股东选择监督努力 μ∈[0,1]，成本 ½cμ²；努力换来对 V 的私有信号 i∈{i_g, i_b}，其精度随 μ 线性上升：Pr(i_g|X)=Pr(i_b|0)=½+½μ。后验 Pr(X|i_g)=(1+μ)/2、Pr(X|i_b)=(1−μ)/2=π_b。μ=0 时信号无信息（后验=先验½），μ=1 时 B 完全知晓 V。

## Role in Model

把"信息获取"内生化为一个有成本的努力选择，是 Edmans 区别于 Admati-Pfleiderer (2008)（外生知情、监督水平固定）的关键。内生监督让模型能给出"持股规模 → 监督努力 → 价格效率"的比较静态：均衡努力 μ=βX/4c（[[edmans-lemma1-market-maker-pricing]]）随可卖量 β 上升，从而随持股 α 非单调。

## Why It Matters

成本参数 c 是"信息不对称"的反向度量：c 越低（信息不对称越高），B 获取增量信息越便宜、价值越大，故大股东对投资的边际作用 ∂θ/∂α 随 c 下降而增强。c 也吸收了分析师、对冲基金等其他价格发现者的活跃度——它们越活跃，大部分价值相关信息已在价上，B 的增量作用越小。

## Variants Across Papers

实证里"信息不对称"常用分析师人数、买卖价差、KV/GAM 指数等度量（如 [[李思飞-2025-耐心资本-esg表现]] 用 GAM 指数 Asy）；它们对应模型里的 1/c——可供知情者注入价格的信息量。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-lemma1-market-maker-pricing]]
