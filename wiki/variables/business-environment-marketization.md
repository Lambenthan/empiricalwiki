---
title: "营商环境（市场化指数, BE）"
slug: "business-environment-marketization"
construct: "营商环境"
role: moderator
measurement: "省级市场化指数（王小鲁等《中国分省份市场化指数报告 2019》）"
data_sources: [中国分省份市场化指数报告 2019]
database_tables: []
frequency: province-year
source_papers: [谢婷婷-2025-耐心资本-动态能力-绿色转型]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

营商环境作为企业外部制度环境的核心构成（夏后学等, 2019），通过影响交易成本、政策支持与市场准入等渠道塑造企业战略行为。本文采用市场化指数衡量营商环境强度，并作为耐心资本与企业绿色转型关系的调节变量。

## Measurement

谢婷婷 (2025) 借鉴宋清、杨雪 (2021) 的做法，使用王小鲁、樊纲、胡李鹏《中国分省份市场化指数报告 (2019)》中的省级市场化总指数，按企业注册地省份-年份合并到企业-年度面板中。

样本中 BE 均值 0.33，标准差 0.15，[0.08, 0.73]。

## Data Source

王小鲁等《中国分省份市场化指数报告 (2019)》，可从社会科学文献出版社网站或中国研究数据服务平台 [[cnrds]] 获取。报告数据截止年份 2019，2020 年后样本需说明外推或锁定策略，原文未明确。

## Literature Variants

- 王小鲁市场化指数（本文采用）：覆盖政府与市场关系、非国有经济发展、产品市场发育、要素市场发育、市场中介组织发育等 5 个一级指标。
- 世界银行营商环境指数：仅有省会城市数据，时间序列短。
- 各类府级营商环境指数（粤港澳大湾区、长三角等）：覆盖范围窄。
- 主成分法自构指数：使用政府效率、法制水平、经济自由度等多维数据合成，未在本文使用。

## Construction Steps

1. 从市场化指数报告 (2019) 抽取省份-年度面板数据（含 2008—2016 年总指数，部分年份需外推）。
2. 与企业基础信息表按 province × year 合并。
3. 调节效应模型中需构造交互项：`gen pc_be = PC * BE`。
4. PC、BE 在交互前最好做去均值处理以缓解多重共线性。

## Stata Notes

```
merge m:1 province year using marketization_index.dta, keep(3) nogen

* 调节效应（表 7）
gen pc_be = PC * BE
reghdfe green PC BE pc_be controls, absorb(firmid year) cluster(firmid)
```

## Caveats

- 报告数据时间截止 2019 年，使用 2020—2023 年样本时需明确外推策略。
- 省级层面口径较粗，无法捕捉同省内部地市差异。
- 与控制变量（地区 GDP、城市固定效应）共线性较强，需注意识别。
- 调节效应解释时需考虑 PC 与 BE 的内生关系（高市场化省份可能本就吸引更多耐心资本）。

## Related

- 与 [[patient-capital]] 构成调节效应组合。
- 被调节的 outcome：[[green-transformation]]。
- 来源论文：[[谢婷婷-2025-耐心资本-动态能力-绿色转型]]。
