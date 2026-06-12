---
title: "公司治理水平高低分组（管理者短视调节）"
slug: "heterogeneity-corporate-governance-myopia"
grouping_variable: "Gover（公司治理水平主成分得分）"
grouping_rule: "对 8 个治理因素做主成分分析，取第一主成分；按每年度 Gover 中位数分高低两组"
rationale: "有效的内部治理监督可以制约管理者短视的自利性行为；若内部治理监督机制对短视起抑制作用，则在治理水平高的组中短视效应应当显著减弱"
source_papers: [胡楠-2021-管理者短视主义-长期投资-文本分析]
date_updated: 2026-05-07
---

## Grouping Logic

8 个治理因素（借鉴张会丽、陆正飞 2012；张学勇、廖理 2010）：

1. 第一大股东持股比例。
2. 独立董事比例。
3. 董事长与总经理是否兼任（兼任为 1，非兼任为 0）。
4. 监事会会议次数。
5. 管理者持股比例。
6. 第二到第十大股东持股比例（制衡度）。
7. 产权性质（国有为 1，非国有为 0）。
8. 机构持股比例。

对上述 8 项做主成分分析，取第一主成分作为 Gover；按每年度 Gover 的中位数将样本分为高低两组。

## Theoretical Rationale

公司治理机制通过股东大会、董事会与监事会三方权利分立和制衡来约束管理者：

- 股东可以"用手投票"替换不合格的管理者，制约其短视等自利性行为。
- 股东间制衡防止大股东诱导管理者短视、进行隧道挖掘。
- 独立董事和专门委员会监督管理者职权。
- 监事会监督业务活动，纠正管理者执行职务时损害股东利益的自利性行为。

→ 高治理水平下，即使管理者具有短视主义特质，其短视行为也会被抑制（H2a）。

## Sample Split

样本量 13,045 ≈ 平分；高低组各约 6,520 个观测。

## Model

主回归模型不变，分组重复（[[ols-industry-year-fe-cluster]] 同结构）：

```
Capex_it / R&D_it = α₀ + α₁·Myopia_Index_it + Controls + ΣYear + ΣIndustry + ε
```

按 Gover 高低分组分别估计。

## Interpretation

胡楠等 (2021) 表 7 Panel A：

- 高 Gover 组：Myopia_Index 对 Capex 系数 -0.011（不显著），对 R&D 系数 -0.011（不显著）→ 短视效应消失。
- 低 Gover 组：Myopia_Index 对 Capex 系数 -0.020**，对 R&D 系数 -0.015***（1% 显著）→ 短视效应显著。

→ 假设 H2a 成立，公司治理水平越高时，短视主义对企业长期投资的负向影响越易受到抑制。

## Related

- 主用例：[[胡楠-2021-管理者短视主义-长期投资-文本分析]]
- 同一论文的另两类调节：[[heterogeneity-monitoring-institutional-investor]] · [[heterogeneity-analyst-coverage-monitoring]]
