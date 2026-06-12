---
title: "机构投资者持股比例 (Institutional Investor Holding, INVH)"
slug: "institutional-investor-holding"
construct: "机构投资者整体持股"
role: core_explanatory
measurement: "INVH_{i,t} = 年末机构投资者持股股数 / 公司总股数。本文口径包含基金、券商理财产品、QFII、保险公司、社保基金、企业年金、信托公司、财务公司及其他机构投资者。"
data_sources: [CSMAR]
database_tables: [机构投资者持股]
frequency: firm-year
source_papers: [杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

机构投资者整体持股比例。本文样本均值 0.0387，中位数 0.0001，最小值 0，最大值 0.4161，分布严重右偏，说明 A 股主板上市公司机构持股整体偏低且差异极大。

## Measurement

INVH_{i,t} = (年末所有机构投资者持有的股票总数) / (公司总股本)。

口径：基金、券商理财、QFII、保险公司、社保基金、企业年金、信托、财务公司及其他机构投资者持股之和。

## Data Source

[[csmar]] 机构投资者持股库。注意 2007 年前覆盖不全，本文样本起点 2009 年起规避此问题。

## Literature Variants

- 全口径机构持股比例（本变量）：最简单，无类型区分。
- 类型分项机构持股：基金 / 保险 / QFII / 社保等单独指标。
- 类型加权或类型异质性指标：见 [[institutional-investor-heterogeneity-stability]]（B2 框架）与 [[patient-capital]] A2 框架。

## Construction Steps

1. 从 CSMAR 机构投资者持股表按 stkcd × accper 拉取年末机构持股股数。
2. 与公司总股本表合并按 stkcd × year。
3. INVH = 机构持股股数 / 总股本。

## Stata Notes

```stata
gen invh = inst_share / total_share
winsor2 invh, replace cuts(1 99)
```

## Caveats

- INVH 在 A 股极端右偏，半数以上公司机构持股 < 0.0001。回归前不缩尾会被极少数高机构持股公司拉动系数。
- 本文滞后一期使用 INVH_{i,t-1}，缓解反向因果。
- 与 [[institutional-investor-heterogeneity-stability]] 配合时只在子样本组内回归 INVH，主效应即"在该类型机构投资者样本下，机构持股越多，崩盘风险变化方向"。

## Related

- 异质性二值化：[[institutional-investor-heterogeneity-stability]]
- 综合化操作：[[patient-capital]]
- 文献：[[杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]]
- 数据：[[csmar]]
