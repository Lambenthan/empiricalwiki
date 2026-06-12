---
title: "命题4（流动性·内生持股）：α_P*<α*，投资随流动性单调上升"
slug: "edmans-prop4-liquidity-endogenous-block"
proposition_type: comparative_statics
formal_statement: "PROPOSITION 4 (Liquidity, Endogenous Block Size): The privately optimal block size α_P* is strictly less than the firm value optimum α*, and monotonically increasing in liquidity ν. Allowing for the endogeneity of block size, investment θ is monotonically increasing in ν."
conditions: "持股内生：α_P* 最大化 B 的交易利润净额（毛利润 Θ(α) 减监督成本 Ψ(α)，eq 12），即对再交易稳健、或 B 在 t=0 不可观测买入会选的持股。"
proof_technique: "刻画私有最优 α_P*（最大化 eq 12 的净利润函数）；证其严格小于企业价值最优 α* 并关于 ν 单调；再代回投资函数。"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
predicts: [liquidity-promotes-long-term-investment]
date_updated: 2026-06-03
---

## Statement

> PROPOSITION 4 (Liquidity, Endogenous Block Size): The privately optimal block size α_P* is strictly less than the firm value optimum α*, and monotonically increasing in liquidity ν. Allowing for the endogeneity of block size, investment θ is monotonically increasing in ν.

## Conditions

- 持股内生：α_P* 最大化 B 的净交易利润 Θ(α)−Ψ(α)=Pr(s_b)·X²/(8c)·β²·(e^(−λβ)/(1+e^(−λβ))−¼)（eq 12）。
- α_P* 是对再交易稳健的唯一初始持股，也是 B 若在 t=0 不可观测买入会选的持股（之后经 Section 13 申报变为公开）。

## Proof Sketch

两股力量把 α_P* 压到企业价值最优 α* 以下：其一，更大持股抬高监督成本（由 B 承担、不计入企业目标）；其二，更大持股压低流动性、减少交易利润，而流动性下降对企业价值有直接正效应（伪装效应）。持股内生时，α 随流动性上升，伪装效应被削弱（更高 ν 让 B 能交易更多、故选更大持股），于是投资关于流动性由倒 U 转为单调上升。

## Comparative Statics

- α_P*<α*：私人最优持股低于企业价值最优——大股东"投资不足"于治理。
- 投资随流动性单调上升（内生持股）。呼应 Maug (1998)"持股内生时流动性总是可取"，但本文新增一层：即便持股外生（[[edmans-prop3-liquidity-exogenous-block]]），从低位增流动性也提升企业价值，因为流动交易本身是大股东创造价值的机制（干预模型里流动交易反而有害）。
- 政策含义：监管/披露要求（如 5% 触发 13(d)、10% 内部人界定）可能阻止 B 内生增持，使 Maug 的"流动性 → 更集中持股"渠道失效；但本文表明此时流动性仍可取。

## Testable Implications

市场流动性促进长期投资 → [[liquidity-promotes-long-term-investment]]。实证须正视持股内生（α_P* 内生于流动性），需外生变动识别。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-prop3-liquidity-exogenous-block]]
- [[liquidity-promotes-long-term-investment]]
