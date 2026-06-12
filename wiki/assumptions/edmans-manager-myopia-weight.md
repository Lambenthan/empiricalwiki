---
title: "经理对当期股价赋权 ω>0（短视动机外生）"
slug: "edmans-manager-myopia-weight"
assumption_type: payoff
formal_statement: "The risk-neutral manager (M) places weight ω on the t = 2 stock price and 1 − ω on the t = 3 firm value, where 0 < ω < 1. Since this paper focuses on the solution to myopia rather than its cause, the concern with current stock price (ω > 0) is taken as exogenous. This is a standard assumption in the literature and can be motivated by a number of underlying factors, such as takeover threat (Stein (1988)), concern for managerial reputation (Narayanan (1985), Scharfstein and Stein (1990)), or the manager expecting to sell his own shares at t = 2 (Stein (1989))."
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
relaxed_in: []
date_updated: 2026-06-03
---

## Statement

风险中性经理 M 对 t=2 股价赋权 ω、对 t=3 企业价值赋权 1−ω，0<ω<1。由于本文研究短视的"解"而非"成因"，对当期股价的关注（ω>0）被外生给定，可由收购威胁（Stein 1988）、声誉关注（Narayanan 1985、Scharfstein-Stein 1990）或经理预期 t=2 出售自身持股（Stein 1989）等微观因素支撑。

## Role in Model

ω>0 是产生短视的"需求侧"前提：经理在 t=0 选投资 θ 时（[[edmans-lemma3-investment-level]]），会因 θ 抬高 t=3 价值但以概率 θ² 触发 s_b、压低 t=2 股价而欠投资。大股东通过提升市场效率 π_X 削弱"s_b 压价"的力度，从而放松这一短视约束——这是 Edmans 给出的"解"。

## Why It Matters

把 ω 外生化，正是 Edmans 与 Stein (1988) 的分工：Stein 内生地推导短视为何作为理性均衡出现（收购威胁下的信号传递），Edmans 把"为何短视"接受为既定，专注"如何缓解"。模型显示 ω 过大时即便有大股东仍欠投资（∂²θ/∂α∂ω<0），ω 适中时大股东作用最大。股权激励若可立即行权会抬高 ω、加剧短视。

## Variants Across Papers

实证中 ω 的代理包括高管薪酬的股价敏感度、可立即行权的期权比例等；Stein (1988) 的 [[stein-managers-maximize-shareholder-return]] 假设经理与股东利益一致（§IV 放松），与本文"经理直接对股价赋权"是两种刻画短视动机的方式。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[stein-1988-takeover-threats-managerial-myopia]]
- [[managerial-myopia-mediation]]
