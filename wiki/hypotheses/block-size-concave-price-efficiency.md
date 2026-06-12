---
title: "大股东持股对私有信息与价格效率的影响呈凹形（倒 U）"
slug: "block-size-concave-price-efficiency"
status: literature_supported
mechanism: "governance-through-trading-exit"
expected_sign: "倒 U（先增后减），峰值在 α*=ν/(ν+1)"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
date_updated: 2026-06-03
---

## Hypothesis

大股东持股规模对其私有信息含量、知情交易利润与股价效率的影响呈凹形（倒 U），而非单调递增；起作用的是引致的最优交易量 min(1/λ, α) 而非持股本身。

## Literature Basis

- **理论基础**：[[edmans-2009-blockholder-trading-managerial-myopia]] 的 [[edmans-lemma2-finite-optimal-block]] 与 [[edmans-prop1-market-efficiency]] 形式化证明价格效率在有限持股 α*=ν/(ν+1) 处最大化，源于短卖约束 [[edmans-short-sales-constraint]] 把可卖量与持股挂钩、又因增持压低流动性而反转。
- 这是"大股东作为知情交易者"框架独有、区别于干预模型（持股越大价值越高）与标准 Kyle 模型（持股不影响信息获取）的预测。

## Testable Model

横截面上，机构投资者交易的私有信息含量 / 价格冲击对 block size 回归，期望系数呈倒 U（需含 block² 项）：`info_content = β₀ + β₁·block + β₂·block² + ...`，期望 β₁>0、β₂<0。

## Evidence

- Bushee-Goodman (2007)：机构投资者交易的私有信息含量随 block size 上升（与凹形的上升段一致）。
- Mikkelson-Partch (1985)：负价格冲击随**卖出量**而非初始持股而增——支持"重要的是交易量而非持股本身"。
- 中国情境下尚缺对"耐心资本（长期机构持股）—效应"非线性（倒 U）的系统检验；[[贾勇-2025-耐心资本-创新韧性-倒u型]] 发现 PC 对创新韧性的倒 U，是相关但不同结果变量的旁证。

## Risks

- block size 内生（[[edmans-prop4-liquidity-endogenous-block]]），需外生变动识别。
- 实证须排除内部人、极少交易的大股东（家族、指数基金），并聚焦短卖成本非平凡的情形。
- 倒 U 的拐点 α*=ν/(ν+1) 依赖流动性 ν，跨股票异质，混合样本可能掩盖非线性。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[governance-through-trading-exit]]
