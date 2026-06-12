---
title: "机构投资者异质性（持股稳定性中位数法，B2 框架）"
slug: "institutional-investor-heterogeneity-stability"
construct: "机构投资者异质性 / 异质机构投资者"
role: core_explanatory
measurement: "牛建波等 (2013)、李争光等 (2014, 2015) 提出的二步法。Step1：SD_{i,t} = INVH_{i,t} / STD(INVH_{i,t-3}, INVH_{i,t-2}, INVH_{i,t-1})（持股波动比指标，分母是过去三年机构投资者持股比例的标准差）。Step2：INVW_{i,t} = 1 if SD_{i,t} ≥ MEDIAN_{i,t}(SD_{i,t})（年-行业中位数门槛），否则 INVW=0。INVW=1 表示稳定型机构投资者，INVW=0 表示交易型机构投资者。"
data_sources: [CSMAR]
database_tables: [机构投资者持股]
frequency: firm-year
source_papers: [杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

理论构念："机构投资者异质性"——同样是机构投资者，因投资期限、监督意愿、交易策略不同对公司治理与股价稳定的作用方向不同。本变量将机构投资者切分为稳定型（持股期长、注重长期价值、积极参与治理）与交易型（持股期短、追求价差、倾向短视）。

操作化构念："基于持股稳定性 + 行业中位数门槛"得到的二值机构投资者类型变量。

## Measurement

两步法（B2 框架）：

1. 持股波动比指标 SD_{i,t}：
   - SD_{i,t} = INVH_{i,t} / STD(INVH_{i,t-3}, INVH_{i,t-2}, INVH_{i,t-1})
   - 分子是当期机构投资者持股比例，分母是过去三年（含 t-3, t-2, t-1）机构投资者持股比例的标准差。
   - SD 越大代表"持股水平相对其历史波动率越高"，即持股越稳定（注意：这是论文 (4)(5) 式的写法，与 patient-capital A2 框架的"稳定型股权 = 比例 / sd"思路一致）。
2. 行业-年中位数门槛：
   - INVW_{i,t} = 1 if SD_{i,t} ≥ MEDIAN_{i,t}(SD_{i,t})
   - INVW_{i,t} = 0 otherwise
   - MEDIAN_{i,t}(SD_{i,t}) 为同年行业内 SD 的中位数。INVW=1 即稳定型机构投资者样本组，INVW=0 为交易型。

## Data Source

[[csmar]] 机构投资者持股表。本文界定的机构投资者持股口径包括基金、券商理财产品、QFII、保险公司、社保基金、企业年金、信托公司、财务公司及其他。

## Literature Variants

- A2 框架（标准差变体 + 银行长债）：稳定型股权连续测度（持股比例 / 三年标准差），与债权侧关系型债务相加得到 [[patient-capital]] 综合得分。代表：代飞 2025。
- B1 框架（持股时长法）：以机构持股最长持续期度量稳定性。
- **B2 框架（本变量）**：在 SD 比值基础上以年-行业中位数二值化，输出哑变量 INVW。代表：[[杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]]、李争光等 (2014, 2015)、牛建波等 (2013)。
- C 框架（综合熵值法）：结合多个机构投资者指标合成单一得分。
- D 框架（基金视角）：从基金重仓股稳定性切入。

## Variant Notes — 与 patient-capital 的关系

本文术语为"机构投资者异质性 / 稳定型机构投资者"，并不直接使用"耐心资本"措辞。但稳定型机构投资者在**持股期长、注重长期价值、积极参与治理**这三个本质属性上完全契合 [[patient-capital]] 的股权侧操作化变体之一。在耐心资本文献综述里，本变量属于 B2（持股稳定性中位数法）框架，与 A2（标准差比连续测度）只差"是否过中位数二值化"一步。本项目把稳定型机构投资者视为 patient capital 的一种二值化操作化变体，链接到 [[patient-capital]] 但保留独立变量页以记录 B2 框架特有的中位数门槛。

## Construction Steps

1. 从 CSMAR 拉取年末机构投资者持股股数与总股数，计算 INVH_{i,t}。
2. 按 firm 排序，构造 INVH_{i,t-3}, INVH_{i,t-2}, INVH_{i,t-1} 滚动窗口，计算其样本标准差。
3. SD_{i,t} = INVH_{i,t} / sd_3y。
4. 按行业-年（CSRC 2001 行业分类）分组取 SD 中位数。
5. 与各公司 SD 比较，生成 INVW 哑变量。
6. 注意 sd_3y = 0 的极端样本需处理（剔除或加 ε）。

## Stata Notes

```stata
xtset stkcd year
gen invh = inst_share / total_share
* 三年滚动标准差（不含本期）
bysort stkcd (year): gen sd_3y = .
bysort stkcd (year): replace sd_3y = sqrt( ///
    ((invh[_n-3]-mean(invh[_n-3..._n-1]))^2 + ///
     (invh[_n-2]-mean(invh[_n-3..._n-1]))^2 + ///
     (invh[_n-1]-mean(invh[_n-3..._n-1]))^2) / 2)
gen sd_ratio = invh / sd_3y
* 行业-年中位数
bysort industry year: egen sd_med = median(sd_ratio)
gen invw = (sd_ratio >= sd_med) if !missing(sd_ratio, sd_med)
```

## Caveats

- 当 sd_3y → 0（连续多年持股比例不变的小公司）时，SD_ratio 不稳定，需要稳健化处理。
- 行业-年中位数门槛对 SD 分布尾部敏感，行业内观测过少时易抖动。
- 二值化丢失连续信息：A2 框架可保留连续 SD，B2 框架只保留 0/1 哑变量。
- SD 这一指标本身名为 "stability" 但分母为标准差，方向上是越大越稳定，命名容易让读者误解，需在论文中明示。
- 与 A2 框架数值上不可直接换算；同一公司在 A2 和 B2 下的"稳定/耐心"判定可能不同。

## Related

- 上游构念：[[patient-capital]]（耐心资本，B2 是其股权侧二值化变体）
- 同 paper 配套变量：[[institutional-investor-holding]] · [[stock-price-crash-risk]] · [[short-selling-eligibility]]
- 异质性切分：[[institutional-investor-stability-split]]
- 数据：[[csmar]]
