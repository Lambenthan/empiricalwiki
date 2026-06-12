---
title: "市场流动性促进（而非阻碍）长期投资"
slug: "liquidity-promotes-long-term-investment"
status: literature_supported
mechanism: "governance-through-trading-exit"
expected_sign: "+（内生持股下单调为正；外生持股下从低位为正、倒 U）"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
date_updated: 2026-06-03
---

## Hypothesis

更高的股票市场流动性会促进企业长期投资、抑制管理者短视，而非如传统观点（Porter 1992、Thurow 1993）所言加剧短视。

## Literature Basis

- **理论基础**：[[edmans-2009-blockholder-trading-managerial-myopia]] 的 [[edmans-prop3-liquidity-exogenous-block]]（持股外生：从低位增流动性提升投资，倒 U）与 [[edmans-prop4-liquidity-endogenous-block]]（持股内生：投资随流动性单调上升）。
- 核心逻辑：loyalty 的力量依赖 exit 的威胁。流动性让退出可行，从而使大股东"未卖出"成为基本面良好的可信信号；缺乏流动性则其忠诚无信息含量。这把"流动 + 频繁换手的美国市场加剧短视"的传统担忧反转。

## Testable Model

企业长期投资（R&D、无形资产投入）对股票流动性（换手率、Amihud 非流动性的反向、买卖价差的反向）回归，控制持股与公司特征，期望流动性系数为正：`LT_invest = β₀ + β₁·liquidity + ...`，期望 β₁>0。

## Evidence

- 与"耐心资本/长期机构投资者促进创新与长期投资"的中国实证（[[温磊-2024-耐心资本-新质生产力]]、[[贾勇-2025-耐心资本-创新韧性-倒u型]]）方向一致，但后者度量的是持股期限而非市场流动性，二者在 Edmans 框架下经由"退出威胁"统一。
- 直接检验"流动性 → 长期投资"为正的中国证据尚缺，是可填补的实证缺口。

## Risks

- 流动性与投资可能同受第三因素（信息环境、公司治理）驱动，需识别外生流动性冲击（如最小报价单位改革、融券试点）。
- 外生 vs 内生持股下符号不同（倒 U vs 单调），实证需区分情形。
- 与 Fang-Tian-Tice (2014) 等"流动性抑制创新"的发现存在张力，结论可能依情境而异。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[governance-through-trading-exit]]
