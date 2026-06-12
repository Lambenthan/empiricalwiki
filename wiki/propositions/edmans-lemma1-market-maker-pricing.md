---
title: "引理1：做市商定价、监督努力与卖出量"
slug: "edmans-lemma1-market-maker-pricing"
proposition_type: characterization
formal_statement: "LEMMA 1. Upon observing s_b and total demand d, the market maker sets the following prices: P = π_b·X if d ≤ 0; P = π_m·X if d > 0, where π_m = Pr(X|d > 0) = [1 + e^(−λβ) + μ(1 − e^(−λβ))] / [2(1 + e^(−λβ))]. B exerts monitoring effort μ = βX/(4c). If and only if she observes signal i_b, B sells β = min(1/λ, α)."
conditions: "聚焦坏信号 s = s_b（s_g 时价格充分揭示，B 不监督不交易）。假设 X ≤ 8c 以保证均衡努力 μ 不超过上限 1。短卖约束 β ≤ α。"
proof_technique: "Kyle (1985) 式竞争性做市商理性预期均衡构造：给定定价函数求 B 的最优努力与交易，给定 B 决策令做市商零利润，联立求不动点。完整证明在附录。"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
predicts: []
date_updated: 2026-06-03
---

## Statement

> LEMMA 1. Upon observing s_b and total demand d, the market maker sets the following prices: P = π_b·X if d ≤ 0; P = π_m·X if d > 0, where π_m = Pr(X|d > 0) = [1 + e^(−λβ) + μ(1 − e^(−λβ))] / [2(1 + e^(−λβ))]. B exerts monitoring effort μ = βX/(4c). If and only if she observes signal i_b, B sells β = min(1/λ, α).

## Conditions

- 仅分析坏信号 s=s_b：好信号 s_g 下做市商知企业高质量、定价 P=X，B 无监督与交易激励。
- X≤8c，确保均衡努力 μ=βX/4c≤1。
- 短卖约束 β≤α；λ=1/(ν(1−α))。

## Proof Sketch

若总需求 d≤0，做市商推断 B 已卖出（收到 i_b），按后验 π_b 定价；d>0 与"卖/不卖"皆相容，按 π_m=Pr(X|d>0) 定价。B 收到 i_b 才卖：在无短卖约束的 Kyle (1985) 中其最优交易为有限的 1/λ（顾忌价格冲击），有约束时至多卖 α，故 β=min(1/λ, α)。监督努力对收益最大化的一阶条件给出 μ=βX/4c。

## Comparative Statics

均衡努力 μ=βX/4c 随可卖量 β 上升、随信息成本 c 下降、随质量差 X 上升。β 关于 α 的非单调性见 [[edmans-lemma2-finite-optimal-block]]。

## Testable Implications

大股东卖出（d≤0）压低股价至 π_b·X，价格冲击随卖出量 β 而非初始持股 α 而增（Mikkelson-Partch 1985 与之一致）。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-short-sales-constraint]]
- [[kyle-1985-informed-trading]]
