---
title: "国家大数据综合试验区分组 (Big Data Pilot Zone Heterogeneity)"
slug: "heterogeneity-big-data-pilot-zone"
grouping_variable: "企业是否处于国家大数据综合试验区"
grouping_rule: "按发改委 2016 / 2017 年批复名单（贵州、京津冀、珠三角、内蒙古、河南、辽宁、上海等）将企业按注册地划分；处于试验区赋 1，否则 0"
rationale: "国家大数据综合试验区依托数据要素构建数字化生产关系，对企业创新活力及数字化转型具有外部支撑，从而放大专精特新转型对新质生产力的促进作用"
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
date_updated: 2026-05-07
---

## Grouping Logic

将企业按注册地是否处于国家大数据综合试验区划分为两组：

- 试验区组：注册地位于国家大数据综合试验区的企业。
- 非试验区组：其余企业。

国家大数据综合试验区由发改委等部委 2016 年起批复，包括贵州、京津冀（北京、天津、河北）、珠三角、内蒙古、河南、辽宁、上海等省市区，旨在打造数据要素市场、数字化基础设施与配套政策环境。

## Theoretical Rationale

新质生产力的"数字"属性使其发展高度依赖外部数据基础设施与制度环境。在试验区内：

- 数据要素流通成本更低，企业更易获取大数据资源支撑研发与运营。
- 配套数字化转型支持政策（财政补贴、税收优惠、产业基金）密集落地。
- 数据治理框架更清晰，企业数据合规与安全成本下降。

因此试验区内企业专精特新转型对新质生产力的促进作用应更显著，论文用此异质性验证"数字化生产关系"对新质生产力的支撑作用。

## Sample Split

- 试验区组：4644 个企业-年观测。
- 非试验区组：6047 个企业-年观测。

按注册地省份与发改委批复名单匹配，子样本各自独立回归。

## Model

子样本独立回归，模型与基准一致：

$$\text{Npro}_{i,t} = \alpha_0 + \alpha_1 \cdot \text{Treat}_{i,t} + \boldsymbol{\alpha} \cdot \text{Controls} + \alpha_3 \cdot \text{Market} + \mu_t + \nu_j + \varepsilon$$

$$\text{Npro}_{i,t} = \alpha_0 + \alpha_1 \cdot \text{Degree}_{i,t} + \boldsymbol{\alpha} \cdot \text{Controls} + \alpha_3 \cdot \text{Market} + \mu_t + \nu_j + \varepsilon$$

组间系数差异采用经验 p 值（Bootstrap 1000 次）检验。

## Interpretation

简冠群 (2025) 表 9 列 (1)–(4)：

- 试验区内：Treat 0.1813***（SE 0.0610）；Degree 0.3261***（SE 0.1069）。
- 非试验区：Treat 0.1021（SE 0.0749，不显著）；Degree 0.0322（SE 0.0466，不显著）。
- 经验 p 值 0.0000，组间差异显著。

试验区内专精特新转型对新质生产力的促进作用显著大于非试验区，验证了数字基础设施与数据要素环境对新质生产力发展的放大作用。非试验区组系数不显著说明数字化外部条件对新质生产力的发展具有重要的边际贡献。

## Related

- 配套被解释变量：[[new-quality-productive-forces]]。
- 配套核心解释变量：[[specialized-new-transformation]]。
- 互补异质性：[[heterogeneity-green-transformation-degree]]（绿色化转型程度分组）。
- 配套论文：[[简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]]。
