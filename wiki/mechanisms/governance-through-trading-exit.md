---
title: "退出/交易型治理（华尔街规则）"
slug: "governance-through-trading-exit"
mechanism_type: governance
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
variables: [institutional-investor-holding, managerial-myopia, long-term-investment]
evidence: []
date_updated: 2026-06-03
---

## Mechanism Statement

无控制权的外部大股东，通过知情交易（坏消息时卖出、好消息时持有，即"用脚投票"的华尔街规则）让股价反映基本面而非当期盈利，从而激励经理做压低短期利润、提升长期价值的投资。治理经由**退出（exit）**而非**话语权（voice）**实现。

## Theoretical Logic

**理论源头（理论侧）**：[[edmans-2009-blockholder-trading-managerial-myopia]] 给出本机制的完整形式化。链条为：短卖约束（[[edmans-short-sales-constraint]]）使持股规模与知情交易激励挂钩 → 大股东付出监督努力获取私有信息 → 坏信号时卖出、好信号时持有，把信息注入价格、提升市场效率 π_X（[[edmans-prop1-market-efficiency]]）→ 价格更贴近基本面、s_b 时股价跌幅收窄 → 经理敢做正 NPV 长期投资（[[edmans-lemma3-investment-level]]、[[edmans-prop2-investment]]）。

与既有机制的分工：

- 区别于 voice/监督型（[[stable-investor-monitoring-channel]]）：本机制不需大股东干预经营，甚至不需其知晓企业的增长机会——纯靠交易行为即可发挥作用。
- 区别于收购威胁型（[[stein-1988-takeover-threats-managerial-myopia]]）：Stein 的短视来自收购市场压力，缓解经由"耐心股东不抛售"的信号；Edmans 的缓解经由"知情交易抬高价格效率"。二者是耐心资本抑制短视的两条互补理论通道。
- 反直觉推论：市场流动性促进（而非阻碍）长期投资（[[liquidity-promotes-long-term-investment]]），因为 loyalty 的力量依赖 exit 的威胁。

## Empirical Proxy

- 大股东/机构持股：[[institutional-investor-holding]]、集中持股度。
- 结果：[[long-term-investment]]、[[managerial-myopia]]、价格效率（股价同步性的反向、知情交易度量）。
- 信息不对称强度（模型里的 1/c）：分析师覆盖、买卖价差、KV/GAM 指数。

## Evidence Across Papers

- 理论侧：Edmans (2009) 形式化证明（Prop 1–4）。
- 实证侧：本 wiki 内中国耐心资本文献多走"持股期限/监督"口径，尚未直接检验"知情交易/退出威胁 → 价格效率 → 投资"链条，是可填补的实证缺口。Edmans 在原文综述的美国证据（Cronqvist-Fahlenbrach 2008 大股东提升投资；Parrino-Sias-Starks 2003、Chen-Harford-Li 2007 大股东在坏消息前卖出）支持该机制。

## Boundary Conditions

- 仅适用于无控制权、会基于信息交易的金融大股东；须排除内部人、家族、指数基金等极少交易者。
- 短卖成本须非平凡（否则持股与信息获取脱钩）。
- 持股内生（[[edmans-prop4-liquidity-endogenous-block]]），效应关于持股呈倒 U（[[block-size-concave-price-efficiency]]）。

## Open Questions

- 中国市场融券受限、机构以长期持有型为主，"退出威胁"渠道的适用性与强度待检验。
- 如何用外生流动性冲击（最小报价单位、融券试点）识别"流动性 → 价格效率 → 投资"？
- 退出型治理与 voice 型治理在中国情境下的相对重要性。
