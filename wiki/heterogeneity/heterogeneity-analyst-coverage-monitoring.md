---
title: "分析师关注度高低分组"
slug: "heterogeneity-analyst-coverage-monitoring"
grouping_variable: "Analyst = Ln(分析师跟踪人数 + 1)"
grouping_rule: "按每年度 Analyst 中位数分高低两组"
rationale: "分析师具备专业的信息搜索与处理能力；高关注度意味着更强的外部监督，会抑制管理者短视等机会主义行为"
source_papers: [胡楠-2021-管理者短视主义-长期投资-文本分析]
date_updated: 2026-05-07
---

## Grouping Logic

Analyst = Ln(当期跟踪该公司的分析师人数 + 1)。按每年度 Analyst 中位数分高低两组。

## Theoretical Rationale

- 分析师可根据海量信息对企业价值做预测和评级；一旦发现管理者机会主义行为，将下调股价与市场估值（Chauvin and Hirschey 1993）。
- 高分析师关注会增加管理者隐藏信息的暴露概率（Brennan and Hughes 1991；张纯、吕伟 2009；王菁、程博 2014）。
- 国内外文献（Graham et al. 2005；Yu 2008；王菁、程博 2014）证实分析师在中国具有抑制管理者短视的监督作用。

→ 分析师关注度越高，管理者短视对长期投资的负向影响越易受到抑制（H2c）。

## Sample Split

胡楠等 (2021) 高 Analyst 组样本量 7,023；低组 6,022。两组并非严格中位数等分（可能源于离散值并列）。

## Model

主回归模型不变（[[ols-industry-year-fe-cluster]] 同结构）：

```
Capex_it / R&D_it = α₀ + α₁·Myopia_Index_it + Controls + ΣYear + ΣIndustry + ε
```

按 Analyst 高低分组分别估计。

## Interpretation

胡楠等 (2021) 表 7 Panel C：

- 高 Analyst 组：Myopia_Index 对 Capex 系数 -0.013（不显著），对 R&D 系数 -0.012**（量级降低）。
- 低 Analyst 组：Myopia_Index 对 Capex 系数 -0.027***，对 R&D 系数 -0.016***（1% 显著）。

→ 高分析师关注下短视效应明显减弱。H2c 成立。该结论与王菁、程博 (2014) 一致：分析师关注度对解决由外部盈利压力造成的投资不足问题具有监督作用。

## Related

- 主用例：[[胡楠-2021-管理者短视主义-长期投资-文本分析]]
- 同一论文的另两类调节：[[heterogeneity-corporate-governance-myopia]] · [[heterogeneity-monitoring-institutional-investor]]
