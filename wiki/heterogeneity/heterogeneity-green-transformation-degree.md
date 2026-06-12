---
title: "绿色化转型程度分组 (Green Transformation Degree Heterogeneity)"
slug: "heterogeneity-green-transformation-degree"
grouping_variable: "企业绿色化转型程度（年报绿色化转型词频 + 1 取自然对数）"
grouping_rule: "按绿色化转型词频中位数将样本分为高 / 低两组"
rationale: "新质生产力的'绿色'子维度使其发展高度依赖企业绿色化转型水平。政府对绿色化发展企业给予更多关注，绿色化转型程度高的企业更可能将专精特新转型转化为新质生产力提升"
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
date_updated: 2026-05-07
---

## Grouping Logic

按企业绿色化转型程度的中位数将样本分为两组：

- 高绿色化转型组：绿色化转型程度 ≥ 中位数。
- 低绿色化转型组：绿色化转型程度 < 中位数。

绿色化转型程度的度量：从企业年报全文统计"绿色 / 节能 / 减排 / 环保 / 低碳 / 清洁生产"等关键词词频，加 1 后取自然对数。原文未公开词典明细，需结合相关绿色转型文献复刻。

## Theoretical Rationale

新质生产力的"绿色发展"子维度（含绿色专利、绿色投资者数量、持续绿色创新水平等指标）使其发展直接受企业绿色化进程影响。绿色化转型程度高的企业：

- 对绿色技术与产品已积累一定基础，更容易将专精特新创新动力转化为绿色创新成果。
- 更可能享受绿色金融、生态文明示范区等政策支持，获取额外资源。
- 更可能吸引绿色投资者与 ESG 偏好的耐心资本。
- 内部 ESG 治理体系更完善，能将专精特新管理优化与绿色生产方式结合。

因此论文预期高绿色化转型组中 TRANS 对 Npro 的促进作用更强。

## Sample Split

- 高绿色化转型组：5487 个企业-年观测。
- 低绿色化转型组：5204 个企业-年观测。

子样本各自独立回归。组间系数差异采用经验 p 值（Bootstrap 1000 次）检验。

## Model

子样本独立回归，模型与基准一致：

$$\text{Npro}_{i,t} = \alpha_0 + \alpha_1 \cdot \text{Treat}_{i,t} + \boldsymbol{\alpha} \cdot \text{Controls} + \alpha_3 \cdot \text{Market} + \mu_t + \nu_j + \varepsilon$$

$$\text{Npro}_{i,t} = \alpha_0 + \alpha_1 \cdot \text{Degree}_{i,t} + \boldsymbol{\alpha} \cdot \text{Controls} + \alpha_3 \cdot \text{Market} + \mu_t + \nu_j + \varepsilon$$

## Interpretation

简冠群 (2025) 表 9 列 (5)–(8)：

- 高绿色化转型：Treat 0.3261***（SE 0.1069）；Degree 0.3831***（SE 0.0379）。
- 低绿色化转型：Treat 0.0322（SE 0.0466，不显著）；Degree 0.1659**（SE 0.0684）。
- 经验 p 值 0.0000，组间差异显著。

高绿色化转型组中专精特新转型对新质生产力的促进作用显著大于低组。Treat 在低组不显著，说明在缺乏绿色化基础的企业中，仅靠专精特新认定难以撬动新质生产力发展；专精特新转型与绿色化转型在新质生产力发展中存在互补关系。

## Related

- 配套被解释变量：[[new-quality-productive-forces]]。
- 配套核心解释变量：[[specialized-new-transformation]]。
- 互补异质性：[[heterogeneity-big-data-pilot-zone]]（国家大数据综合试验区分组）。
- 相关变量：[[green-transformation]]。
- 配套论文：[[简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]]。
