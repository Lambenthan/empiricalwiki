---
title: "企业规模分组：耐心资本对 ESG 表现的差异化影响"
slug: "heterogeneity-firm-size-split-pc-esg"
grouping_variable: "企业规模 Size（期末总资产对数）"
grouping_rule: "按 Size 中位数将样本分为大规模企业组与小规模企业组"
rationale: "大规模企业在长期 ESG 投入上拥有更厚实的资本基础与组织资源，耐心资本流入后能够直接转化为更系统性的环境治理与社会责任投入；小规模企业则受限于资源约束，耐心资本的边际效应较弱"
source_papers: [唐亮-2025-耐心资本-esg表现]
date_updated: 2026-05-07
---

## Grouping Logic

按企业规模 Size 的样本中位数把观测分为：

- 大规模企业组：Size > 中位数，n = 13,375。
- 小规模企业组：Size ≤ 中位数，n = 12,957。

分组后分别在两个子样本上跑基准模型 ESG = β₀ + β₁ PC + Controls + 行业 FE + 年份 FE + 个体 FE。组间差异通过 Bootstrap 或 Chow 类检验给出 P 值。

## Theoretical Rationale

大规模企业的资源基础与组织能力使其更能把耐心资本带来的长期资金转化为系统性的 ESG 投入：

- 资源能力：环境治理设施、绿色研发、员工福利、合规体系等都需要大额、长期的资本支出，规模较大的企业有更强的承受能力。
- 政策响应能力：大规模企业是政策导向（"双碳"、绿色金融、可持续披露）的重点对象，耐心资本流入后可以更快响应监管要求。
- 信息披露透明度：大规模企业披露规范度更高，耐心资本投资者对其经营状况掌握更充分，监督治理机制更为有效。

小规模企业则可能因资源稀缺而把耐心资本优先用于经营周转或核心业务扩张，挤出 ESG 投入。

## Sample Split

- 大规模企业组（n = 13,375）：PC 系数 0.041***（t = 7.662）。
- 小规模企业组（n = 12,957）：PC 系数 0.023***（t = 3.641）。
- 组间差异检验统计量 2.174，P 值 = 0.015，差异在 5% 显著水平下成立。

两组样本量略低于全样本 27,203，差额（约 871 个观测）来自于 Size 计算缺失或边界值剔除。

## Model

```stata
* 大规模子样本
reghdfe ESG PC $controls if size > size_median, absorb(industry year firmid) cluster(firmid)

* 小规模子样本
reghdfe ESG PC $controls if size <= size_median, absorb(industry year firmid) cluster(firmid)

* 组间系数差异检验（Bootstrap）
bootstrap "reghdfe ESG c.PC##i.large $controls, absorb(industry year firmid) cluster(firmid)" ///
    e(b)[1, 2], reps(500)
```

## Interpretation

- 大规模组系数显著大于小规模组（0.041 vs 0.023），且差异检验 P = 0.015 通过 5% 阈值，提示企业规模在 PC → ESG 路径中起放大作用。
- 这与 [[high-quality-development]]、[[green-transformation]] 类研究中"规模异质性"普遍发现一致：规模较大企业的 ESG 投入响应度更高。
- 实务含义：政策制定者若希望通过培育耐心资本提升整体市场 ESG 表现，对大规模企业边际收益更高；对小规模企业则需要配套的 ESG 配套资源（绿色信贷、ESG 咨询）才能放大耐心资本效应。

## Related

- 来源论文：[[唐亮-2025-耐心资本-esg表现]]。
- 配套异质性维度（同文表 7）：[[heterogeneity-leverage-risk-split-pc-esg]] · [[state-ownership-split]] · [[heterogeneity-listing-tenure-split-pc-esg]]。
- 同样按规模做异质性切分的相关论文：[[李季鹏-2025-耐心资本-高质量发展]] · [[谢婷婷-2025-耐心资本-动态能力-绿色转型]]。
