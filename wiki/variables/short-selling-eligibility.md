---
title: "卖空标的资格 (Short-Selling Eligibility, SSC)"
slug: "short-selling-eligibility"
construct: "卖空机制 / 融资融券标的"
role: core_explanatory
measurement: "SSC_{i,t} 为虚拟变量。若股票 i 在 2010 年 3 月 31 日以来的某一轮融资融券标的扩容名单中被纳入，则 SSC_{i,t}=1，否则为 0。配合 After_{i,t}（标的股票在被纳入两融之后的年度记为 1）构造 DID 三重交互项。"
data_sources: [CSMAR]
database_tables: [融资融券标的目录]
frequency: firm-year
source_papers: [杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

中国 A 股市场是否允许该股票被融券卖空的二值标识。中国证监会 2010 年 3 月 31 日启动融资融券试点，首批 90 只股票（上证 50 + 深成指成分股），此后多次扩容。SSC 反映股票是否进入两融标的池，After 反映"进入之后"的年度窗口。

## Measurement

- SSC_{i,t} = 1 若股票 i 截至 t 已被纳入某一轮融资融券标的扩容；否则 0。
- After_{i,t} = 1 若 t 是股票 i 进入两融名单的次年起；否则 0。
- 二者相乘 SSC × After 构成被处理组在事件后的标识，用于 DID。

## Data Source

[[csmar]] 融资融券标的目录或交易所历次扩容公告。本文以"是否成为融资融券的标的"作为 SSC 取值依据。

## Literature Variants

- 二值标的虚拟变量（本变量）：最常见，用于 DID。
- 连续测度（融券余额、做空成本）：少数文献使用。
- 标的纳入轮次（首批/二批/三批…）虚拟变量：用于事件研究。

## Construction Steps

1. 从交易所公告或 CSMAR 整理出每一轮融资融券标的名单及生效日期。
2. 与样本股票按 stkcd 匹配，标记每年是否在标的池。
3. 构造 SSC 和 After 两个 dummies，构造三重交互项 INVH × SSC × After。

## Stata Notes

```stata
* event_year_i 为股票 i 首次纳入两融的年份（缺失 = 从未纳入）
gen ssc   = !missing(event_year_i)
gen after = !missing(event_year_i) & year >= event_year_i + 1
```

## Caveats

- 标的扩容并非随机，存在"市值高 + 流动性好"的选样偏差；用 DID 需检查平行趋势或 PSM-DID 配套。
- 部分股票被剔除标的池后再重新纳入，SSC/After 应以滚动状态而非单次事件处理。
- 本文将 SSC×After 与 INVH 三重交互，识别的是"两融对机构投资者-崩盘关系的调节效应"，而非两融本身对崩盘的主效应。

## Related

- 文献：[[杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]]
- 识别：[[did-short-selling-pilot]]
- 配套变量：[[institutional-investor-holding]] · [[institutional-investor-heterogeneity-stability]] · [[stock-price-crash-risk]]
- 数据：[[csmar]]
