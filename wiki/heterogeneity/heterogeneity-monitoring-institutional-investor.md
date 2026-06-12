---
title: "监督型机构投资者持股高低分组"
slug: "heterogeneity-monitoring-institutional-investor"
grouping_variable: "IO（监督型机构投资者持股比例 = (证券投资基金 + 社保基金 + QFII 持股) / 总股数）"
grouping_rule: "按每年度 IO 中位数分高低两组"
rationale: "监督型机构投资者奉行价值投资理念，有更强动机关注企业长期价值信息；其持股越多，对管理者短视的抑制作用越强"
source_papers: [胡楠-2021-管理者短视主义-长期投资-文本分析]
date_updated: 2026-05-07
---

## Grouping Logic

监督型机构投资者特指三类独立机构（杨海燕等 2012）：

- 证券投资基金。
- 社保基金。
- QFII（合格境外机构投资者）。

排除保险公司、信托公司、一般法人机构（这三类与上市公司常存在商业关系，监督动机弱）。

按每年度 IO 中位数分高低两组。

## Theoretical Rationale

- 机构投资者资金规模大、专业知识强，对管理者影响力强。
- 奉行价值投资理念，关注长期价值而非短期业绩（Stein 1989）。
- Brickley et al. (1988)、Almazan et al. (2005)、杨海燕等 (2012)：仅当机构投资者与上市公司属于纯投资关系时才有监督动机；业务依赖关系会削弱监督动机。
- 因此只统计独立机构（基金、社保、QFII）作为"监督型"代理。

→ 监督型机构投资者持股越高，管理者短视的负向行为越被抑制（H2b）。

## Sample Split

样本约平分，高低组各约 6,520 个观测。

## Model

主回归模型不变（[[ols-industry-year-fe-cluster]] 同结构）：

```
Capex_it / R&D_it = α₀ + α₁·Myopia_Index_it + Controls + ΣYear + ΣIndustry + ε
```

按 IO 高低分组分别估计。注意：IO 仍作为控制变量保留在主回归中；分组检验额外捕获其调节效应。

## Interpretation

胡楠等 (2021) 表 7 Panel B：

- 高 IO 组：Myopia_Index 对 Capex 系数 -0.007（不显著），对 R&D 系数 -0.015**（5% 显著但量级低）。
- 低 IO 组：Myopia_Index 对 Capex 系数 -0.027***，对 R&D 系数 -0.014**（1%–5% 显著）。

→ 高监督型机构持股下，短视对长期投资的负向影响明显减弱。H2b 成立。

## Related

- 主用例：[[胡楠-2021-管理者短视主义-长期投资-文本分析]]
- 同一论文的另两类调节：[[heterogeneity-corporate-governance-myopia]] · [[heterogeneity-analyst-coverage-monitoring]]
- 概念近邻：[[institutional-investor-heterogeneity-stability]] · [[heterogeneous-institutional-investors-stable]]
