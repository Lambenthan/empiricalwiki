---
title: "企业绿色转型 (Green Transformation, Green)"
slug: "green-transformation"
construct: "企业绿色转型"
role: dependent
measurement: "LN(年报中绿色转型关键词词频数 + 1)；关键词字典覆盖宣传倡议、战略理念、技术创新、排污治理、监测管理 5 个方面共 113 个词（解学梅、朱琪玮 2021）"
data_sources: [国泰安 CSMAR, 上市公司年报文本]
database_tables: [上市公司年报全文表]
frequency: firm-year
source_papers: [谢婷婷-2025-耐心资本-动态能力-绿色转型]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

企业绿色转型指企业树立绿色发展理念、以资源集约利用与环境友好为指引、以绿色创新能力为核心、坚持生产全过程绿色化、并兼顾经济绩效与环境绩效双重目标的发展模式（方慧等, 2024）。绿色转型包括绿色化方向转型、绿色化行动转型与绿色化保障转型三个层面，是实现"双碳"目标的关键载体。

## Measurement

谢婷婷 (2025) 借鉴解学梅、朱琪玮 (2021) 的文本分析法：

1. 构造关键词字典：从宣传倡议、战略理念、技术创新、排污治理、监测管理 5 个方面选取 113 个绿色转型关键词。
2. 抽取上市公司年报全文。
3. 统计年报中各关键词出现频次，加总得到企业-年度绿色转型词频数 freq。
4. 取自然对数：Green = LN(freq + 1)。

样本中 Green 均值 1.95，标准差 0.84，最小值 0，最大值 4.04。

## Data Source

主要来自 [[csmar]] 上市公司年报全文表或国泰安年报数据库。关键词字典需自行复刻或参考解学梅、朱琪玮 (2021) 论文附录。

## Literature Variants

- 文本词频法（解学梅、朱琪玮 2021；方慧等 2024）：本文主测度。优点是可直接从年报抽取，覆盖广；缺点是依赖关键词字典质量，且年报文本存在表述风格差异。
- 绿色全要素生产率：用非径向 SBM-ML 指数测算的绿色 TFP（崔兴华、林明裕 2019）。本文作为稳健性检验替代被解释变量（lngtfp）。
- 绿色专利申请数：以企业绿色发明 / 实用新型专利数衡量绿色技术创新维度，未在本文使用。
- ESG 评级：第三方评级机构（华证 / Wind / 商道融绿）数据，多用于绿色绩效衡量，本文未采用。

## Construction Steps

1. 抽取上市公司年报正文文本（CSMAR 年报全文表或上市公司巨潮资讯网披露）。
2. 加载 113 词字典（按解学梅、朱琪玮 2021 复刻）。
3. 对每份年报，使用分词工具（jieba/THULAC）切词后匹配字典或直接子串匹配。
4. 统计企业-年度词频：`bysort firmid year: egen freq = total(matched_count)`。
5. 生成因变量：`gen green = ln(freq + 1)`。

## Stata Notes

```
* 假设已经从 Python 端落盘 firm_year_freq.dta：firmid year freq
use firm_year_freq.dta, clear
gen green = ln(freq + 1)
sum green, detail
* 复现表 3 列 (2)
reghdfe green PC size firmage roe quick growth lev indep dual top1, absorb(firmid year) cluster(firmid)
```

## Caveats

- 关键词字典是否包含 113 词全集决定可比性；不同论文同名指标系数不可直接比较。
- 词频法对年报披露策略（"漂绿"行为）敏感，需与绿色 TFP、绿色专利等口径互为稳健性。
- 早期年报披露不规范，2012 年前样本词频可能系统性低估。
- 取对数前加 1 处理零词频；若样本零比例过高需考虑改用 Tobit 或两部模型。

## Related

- 核心配套解释变量：[[patient-capital]]（耐心资本）。
- 中介通道：[[dynamic-capability]]（动态能力，吸收/创新/适应三维度）。
- 稳健性替代度量：绿色全要素生产率（lngtfp）。
- 来源论文：[[谢婷婷-2025-耐心资本-动态能力-绿色转型]]。
