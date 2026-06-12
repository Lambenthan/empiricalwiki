---
title: "命题2（投资·全文核心）：投资在有限持股 α* 处最大化"
slug: "edmans-prop2-investment"
proposition_type: comparative_statics
formal_statement: "PROPOSITION 2 (Investment): Define X1 = (1−ω)g/ω and X2 = (1−ω)g/ω · (1+e^(−1))/(2e^(−1)). For all X, investment θ is weakly increasing in π_X. It is therefore maximized at α = α*, weakly increasing in α for α < α*, and weakly decreasing in α if α > α*. If X ≥ X2, these directional effects are strict and θ is uniquely maximized at α = α*. If X ≤ X1, M invests efficiently (θ = 1) regardless of π_X and thus α. The magnitude of the block-sensitivity of investment |∂θ/∂α| is weakly increasing in g and weakly decreasing in c and ω."
conditions: "X1 = (1−ω)g/ω 与 X2 = (1−ω)g/ω·(1+e^(−1))/(2e^(−1))。X ≥ X2 时方向效应严格、θ 在 α* 处唯一最大化；X ≤ X1 时 M 无条件充分投资（θ=1），大股东无增量作用。"
proof_technique: "对引理3 的 θ 关于 α 求导（经由 π_X，命题1），并对 g、c、ω 求交叉偏导确定 block-sensitivity 的方向。"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
predicts: [pc-attenuates-managerial-myopia, block-size-concave-price-efficiency]
date_updated: 2026-06-03
---

## Statement

> PROPOSITION 2 (Investment): Define X1 = (1−ω)g/ω and X2 = (1−ω)g/ω · (1+e^(−1))/(2e^(−1)). For all X, investment θ is weakly increasing in π_X. It is therefore maximized at α = α*, weakly increasing in α for α < α*, and weakly decreasing in α if α > α*. If X ≥ X2, these directional effects are strict and θ is uniquely maximized at α = α*. If X ≤ X1, M invests efficiently (θ = 1) regardless of π_X and thus α. The magnitude of the block-sensitivity of investment |∂θ/∂α| is weakly increasing in g and weakly decreasing in c and ω.

## Conditions

- X1=(1−ω)g/ω；X2=(1−ω)g/ω·(1+e^(−1))/(2e^(−1))。
- X≥X2：方向效应严格，θ 在 α=α* 处唯一最大化。
- X≤X1：经理无条件充分投资（θ=1），大股东无增量作用（∂θ/∂α=0）。

## Proof Sketch

由引理3，θ 弱增于 π_X；由命题1，π_X 在 α* 处最大化、α<α* 段增、α>α* 段减。复合即得 θ 关于 α 的倒 U。对 g、c、ω 求交叉偏导给出 block-sensitivity 方向：|∂θ/∂α| 弱增于 g（项目越值钱、价格效率改善的回报越大）、弱减于 c（信息不对称越强、大股东作用越大）、弱减于 ω。

## Comparative Statics

**全文核心结果**：大股东即便不存在 effort conflict、也无干预能力，仅靠为自身投机利润而知情交易，就能促进长期投资。α<α* 时增持抬高 π_X、使股价更贴近基本面，经理更敢做"压低当期盈利但提升基本面"的正 NPV 投资。推论：分散持股的一项关键成本是放大短视——与传统聚焦的"偷懒（shirking）"成本不同，政策含义相反（若问题是短视，股权激励与活跃收购市场反而加剧之）。

## Testable Implications

- 大股东/耐心资本促进长期投资、抑制短视 → [[pc-attenuates-managerial-myopia]]（理论侧来源，机制为退出/交易）。
- 投资关于 block size 呈凹形 → [[block-size-concave-price-efficiency]]。
- ∂²θ/∂α∂c<0：信息不对称越强，大股东作用越大——与实证的信息不对称机制检验一致。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-lemma3-investment-level]]
- [[edmans-prop1-market-efficiency]]
- [[governance-through-trading-exit]]
