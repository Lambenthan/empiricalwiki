---
title: "专精特新转型 (Specialized, Refinement, Differential, Innovation Transformation, TRANS)"
slug: "specialized-new-transformation"
construct: "专精特新转型"
role: core_explanatory
measurement: "包含两个互补维度：(1) 专精特新企业认定 Treat — 多时点 DID 处理变量，被工信部或地方工信厅认定为专精特新企业当年起赋 1；(2) 专精特新发展程度 Degree — 借鉴张璠等 (2022) 构建评价指标体系，标准化后熵权法合成 × 100"
data_sources: [工信部专精特新企业认定名单, 各省工信厅认定名单, 国泰安 CSMAR, Wind]
database_tables: [专精特新企业名单, 上市公司基础信息表, 财务报表]
frequency: firm-year
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

"专精特新"指中小企业在专业化、精细化、特色化、新颖化四方面的发展导向，是中国工业和信息化部 2013 年起推动的中小企业培育战略。专精特新转型指企业从一般中小企业向具备四项特征的企业演进的动态过程，含"质变"（资质认定）与"量变"（发展程度提升）两个互补维度。

政策起点：工信部 2013 年《关于促进中小企业"专精特新"发展的指导意见》（工信部企业〔2013〕264 号）。后续认定层级包括国家级（专精特新"小巨人"）、省级、市级。

## Measurement

简冠群 (2025) 将转型分解为两个维度：

- Treat（质变）— 是否完成专精特新企业认定，多时点 DID 处理变量。企业 i 在 t 年被工信部或地方工信厅认定为专精特新企业当年及以后赋 1，否则为 0。
- Degree（量变）— 专精特新发展程度，借鉴张璠等 (2022) 构建专精特新转型评价指标体系；各底层指标标准化后熵权法合成并乘以 100。

替代口径（简冠群 2025 稳健性）：

- Treat1：单期 DID 哑变量，2013 年后被认定的企业全样本年份赋 1，否则 0。
- Degree1：以创新投入绝对值（研发支出）作为发展程度的替代度量。
- Degree2：借鉴徐怀宁 (2024) 重构指标体系熵权法合成。

## Data Source

- 工信部官方网站及《工业和信息化部公告》历年发布的专精特新"小巨人"名单。
- 各省工信厅 / 工业和信息化局发布的省级、市级专精特新企业名单。
- [[csmar]] 上市公司基础信息表与财务报表（用于匹配是否上市、所属行业、Degree 子指标）。
- [[wind]] 上市公司公告系统（补充资质公告披露日期）。

## Literature Variants

- 张璠等 (2022) — 评价指标体系 + 熵权法 × 100 → Degree（简冠群 2025 主测度）。
- 简冠群 (2025) Treat — 多时点 DID（按认定年份多时点）。
- 简冠群 (2025) Treat1 — 单期 DID（2013 年统一节点）。
- 张璠等 (2022) 替代 — 创新投入绝对值衡量发展程度。
- 徐怀宁 (2024) — 重构指标体系熵权法合成。
- 焦豪、李宛蓉 (2023) — 专精特新"小巨人"名单作为准自然实验处理。

## Construction Steps

Treat 构造：

1. 抓取工信部历年公告 PDF / Excel 名单，提取企业名称与认定年份。
2. 抓取各省工信厅省级、市级名单（认定层级、认定年份）。
3. 与 CSMAR 上市公司基础信息表按企业名称（含曾用名）匹配，得到 stkcd × 认定年份对应表。
4. Treat(i, t) = I(t ≥ 认定年份(i))；未被认定企业全样本年份为 0。
5. 多时点 DID 设定：直接将 Treat 作为解释变量，配合行业 + 年份 FE，吸收不同认定时点。

Degree 构造（张璠 2022 路径）：

1. 按张璠等 (2022) 列出的子指标（专业化、精细化、特色化、新颖化四维下若干底层指标）构造企业-年指标矩阵。
2. 各指标分别标准化（min-max 或 z-score）。
3. 熵权法计算各指标权重并加权求和。
4. × 100 → Degree。

注意：原文未列张璠 (2022) 子指标全清单，需结合原文复刻。简冠群 (2025) 描述性统计 Degree 均值 1.358、SD 0.823、最大 10.07、最小 0.0021。

## Stata Notes

```stata
* Treat 多时点 DID
gen treat_year = .  // 来自外部认定名单
replace treat_year = . if missing(treat_year)
gen Treat = (year >= treat_year & !missing(treat_year))

* 单期 DID（Treat1）
gen Treat1 = (year >= 2013 & !missing(treat_year))

* 主回归
reghdfe Npro Treat $controls Market, absorb(industry year) cluster(industry)
reghdfe Npro Degree $controls Market, absorb(industry year) cluster(industry)

* PSM 1:1 最近邻匹配
psmatch2 Treat $matchvars, n(1) common
reghdfe Npro Treat $controls Market if _support == 1, absorb(industry year) cluster(industry)
```

## Caveats

- 专精特新认定层级（国家 / 省 / 市）差异显著，简冠群 (2025) 将三类层级统一处理，可能掩盖层级差异。论文亦在不足部分自我反思。
- Degree 指标体系子指标具体清单依赖张璠等 (2022) / 徐怀宁 (2024) 原文，跨研究复现性受影响。
- 多时点 DID 在 Goodman-Bacon (2021) 分解下可能存在异质处理效应偏误，本论文未做相关诊断。
- 名单匹配中曾用名、并购重组、子公司认定的归属规则需明确。
- 仅覆盖中小板、创业板、科创板、北交所上市企业，不能直接推广至沪深主板大型企业或非上市企业。

## Related

- 配套被解释变量：[[new-quality-productive-forces]]。
- 配套中介：[[venture-capital]] · [[patient-capital]]。
- 配套机制：[[venture-capital-attraction-channel]] · [[patient-capital-attraction-channel]]。
- 配套数据集：[[csmar]] · [[wind]]。
- 配套论文：[[简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]]。
