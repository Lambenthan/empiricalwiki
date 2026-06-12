---
title: "机构投资者持股比例（Institutional Ownership / Shareholding）"
slug: "institutional-ownership"
construct: "机构投资者持股"
role: dependent
measurement: "INST = 年末所有机构投资者持股比例之和（基金、券商、保险、社保基金、QFII 及其他机构）；INST_LONG / INST_SHORT 按 Yan and Zhang (2009) 流动率（churn rate）三分位划分"
data_sources: [CSMAR, Wind]
database_tables: ["CSMAR 机构投资者持股表", "Wind 十大流通股东"]
frequency: "firm-year"
source_papers: [黎文靖-2015-机构投资者-环境绩效-重污染]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

机构投资者持股比例是机构投资者作为整体在某上市公司的持股比例之和。中国情境下机构投资者通常包括：证券投资基金、券商自营、保险公司、社保基金、QFII、信托、私募基金等。可进一步按投资期限或换手率划分为长期机构投资者与短期机构投资者。

## Measurement

总机构持股：

$$INST_{i,t} = \sum_{k \in \mathrm{Inst}} \mathrm{Shr}_{k,i,t}$$

其中 Shr_{k,i,t} 是机构 k 在公司 i 在 t 年末的持股比例。

按期限划分（Yan and Zhang, 2009 流动率法）：

第 1 步：每家机构 k 在 t 期的总买入与总卖出金额（黎文靖 2015 公式）：

$$CR\_buy_{k,t} = \sum_{i: S_{k,i,t} > S_{k,i,t-1}} \left| S_{k,i,t} P_{i,t} - S_{k,i,t-1} P_{i,t-1} - S_{k,i,t} \Delta P_{i,t} \right|$$

$$CR\_sell_{k,t} = \sum_{i: S_{k,i,t} \leq S_{k,i,t-1}} \left| S_{k,i,t} P_{i,t} - S_{k,i,t-1} P_{i,t-1} - S_{k,i,t} \Delta P_{i,t} \right|$$

第 2 步：流动率（churn rate）：

$$CR_{k,t} = \frac{\min(CR\_buy_{k,t}, CR\_sell_{k,t})}{\sum_i (S_{k,i,t} P_{i,t} + S_{k,i,t-1} P_{i,t-1})/2}$$

第 3 步：过去一年平均流动率 AVG_CR_{k,t} = (CR_{k,t} + CR_{k,t-1})/2。

第 4 步：将所有机构按 AVG_CR 排序三分位：

- AVG_CR 最低 1/3：长期机构投资者（INST_LONG）。
- AVG_CR 最高 1/3：短期机构投资者（INST_SHORT）。
- 中间 1/3：未分类。

INST_LONG / INST_SHORT 是被这两类机构持有的股票占公司总股本的比例。

## Data Source

- CSMAR 机构投资者持股表（最早 2003 年起，2007 年起覆盖较全）。
- Wind 十大流通股东模块（季度披露，可用于补全短窗口）。
- 注意：早期年份（2007 前）机构投资者细分类别披露不完整，导致 INST_LONG/INST_SHORT 的零值偏高。

## Literature Variants

| 文献 | 测度 | 说明 |
|------|------|------|
| Yan and Zhang (2009) | INST_LONG/INST_SHORT 三分位流动率法 | 国际标准方法 |
| 黎文靖 (2015) [[黎文靖-2015-机构投资者-环境绩效-重污染]] | INST、INST_LONG、INST_SHORT 同时使用 | 中国情境复现 |
| Bushee (1998) | dedicated / transient / quasi-indexer 三类 | 因子分析法 |
| Cox and Wicks (2011) | 专注 vs 临时机构 | 与黎文靖结论一致 |

## Construction Steps

1. 从 CSMAR 机构持股库提取年末持股快照（机构-公司-年观测）。
2. 对每家机构计算季度或半年度持仓变动，构造 CR_buy / CR_sell 与流动率 CR_{k,t}。
3. 滚动平均得 AVG_CR_{k,t}，按当年所有机构 AVG_CR 三分位标记 LONG / SHORT。
4. 把 LONG / SHORT 类别回填到机构-公司-年表，按公司-年聚合得 INST_LONG_{i,t} 与 INST_SHORT_{i,t}。
5. 注意：黎文靖 2015 的 INST_LONG 均值仅 0.020、INST_SHORT 均值 0.035，绝大多数机构未被分类（剩 INST 总量在 0.157）。

## Stata Notes

```stata
* 第一步：构造每家机构每年的换手率（需先合并机构-公司-年-持仓 panel）
bysort instcd year: egen tot_buy = total(cond(delta_shares > 0, abs(delta_value), 0))
bysort instcd year: egen tot_sell = total(cond(delta_shares <= 0, abs(delta_value), 0))
bysort instcd year: egen avg_holding = mean((shares*price + L.shares*L.price)/2)
gen CR = min(tot_buy, tot_sell)/avg_holding

* 滚动两期平均
xtset instcd year
gen AVG_CR = (CR + L.CR)/2

* 当年三分位
bysort year: xtile CR_tile = AVG_CR, nq(3)
gen LONG_FLAG = (CR_tile == 1)
gen SHORT_FLAG = (CR_tile == 3)

* 聚合到公司-年
bysort stkcd year: egen INST_LONG = total(holding_pct * LONG_FLAG)
bysort stkcd year: egen INST_SHORT = total(holding_pct * SHORT_FLAG)
```

## Caveats

- **左截断**：INST_LONG/INST_SHORT 大量为 0，OLS 估计有偏；需用 Tobit（lower limit 0）。
- **流动率法对季度数据敏感**：Yan and Zhang (2009) 原文用季度数据，CSMAR 部分公司只有半年度披露，会改变三分位的临界值。
- **三分位是相对划分**：每年的「长期机构」临界点不同，跨年比较系数大小需谨慎。
- **机构身份穿透**：QFII、信托等通道账户可能掩盖真实持有人；保险/社保更接近耐心资本，而券商自营/私募基金接近短期。
- **本变量并非耐心资本本身**：耐心资本是更宽口径的构念，包括稳定型股权 + 长期债务，机构投资者持股仅是其股权侧的代理。

## Related

- [[黎文靖-2015-机构投资者-环境绩效-重污染]]（操作化源头）
- [[patient-capital]]（耐心资本，本项目核心变量；INST_LONG 可视为其早期单维度代理）
- [[csmar]]、[[wind]]（数据来源）
