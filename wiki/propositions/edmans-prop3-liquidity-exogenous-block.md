---
title: "命题3（流动性·外生持股）：效率与投资在有限流动性 ν* 处最大化"
slug: "edmans-prop3-liquidity-exogenous-block"
proposition_type: comparative_statics
formal_statement: "PROPOSITION 3 (Liquidity, Exogenous Block Size): Holding α constant, market efficiency and investment are maximized at ν* = α/(1−α). They are increasing (decreasing) in ν for ν < (>) ν*."
conditions: "持股 α 外生（固定）。流动性参数 ν；λ = 1/(ν(1−α))。ν* = α/(1−α)。"
proof_technique: "在 α 固定下对市场效率（及经由命题2 的投资）关于 ν 求导，权衡两股反向力量：流动性抬高 B 的交易利润与信息收集，但也伪装其交易、削弱价格冲击。"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
predicts: [liquidity-promotes-long-term-investment]
date_updated: 2026-06-03
---

## Statement

> PROPOSITION 3 (Liquidity, Exogenous Block Size): Holding α constant, market efficiency and investment are maximized at ν* = α/(1−α). They are increasing (decreasing) in ν for ν < (>) ν*.

## Conditions

- 持股 α 外生固定。
- 流动性参数 ν，λ=1/(ν(1−α))；ν*=α/(1−α)。

## Proof Sketch

由命题2 投资增于市场效率；市场效率取决于两点：B 收集多少信息、信息多大程度进入价格。流动性一方面经由抬高交易利润促进信息收集，另一方面伪装 B 的交易、削弱价格冲击。低（高）效率水平下第一（第二）效应主导：零流动性 B 不交易不监督；无限流动性她不影响价格。两者权衡给出有限最优 ν*=α/(1−α)。

## Comparative Statics

效率与投资关于流动性呈倒 U（持股外生时），峰值 ν*=α/(1−α)。与 Holmstrom-Tirole (1993)、Faure-Grimaud-Gromb (2004)（流动性总是抬高价格信息含量）相反——根源在于本文 B 的最大卖量被短卖约束封顶在 α，故存在伪装效应。

## Testable Implications

即便持股外生，从低位提高流动性也能促进长期投资 → [[liquidity-promotes-long-term-investment]]，反驳 Porter (1992)、Thurow (1993)"流动市场阻碍长期投资"的传统观点。关键机制：loyalty 的力量依赖 exit 的威胁——若市场缺乏流动性逼得大股东只能长期持有，她"未卖出"就不再是基本面良好的信号。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-prop4-liquidity-endogenous-block]]
- [[liquidity-promotes-long-term-investment]]
