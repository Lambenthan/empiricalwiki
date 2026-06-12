---
title: "股价崩盘风险 (Stock Price Crash Risk)"
slug: "stock-price-crash-risk"
construct: "股价崩盘风险"
role: dependent
measurement: "Hutton et al. (2009) 标准做法：先按 Dimson 修正 5 项回归提取个股周特有收益率 W_{i,t}=ln(1+ε_{i,t})，再分别构造 Ncskew（负收益偏态系数）和 Duvol（收益上下波动率）。Ncskew = -[n(n-1)^{3/2} ΣW^3] / [(n-1)(n-2)(ΣW^2)^{3/2}]；Duvol = log{[(n_up-1) Σ_{Down} W^2] / [(n_down-1) Σ_{Up} W^2]}。稳健性变量 IsCrash：W_{i,t} ≤ Average(W_{i,t}) − 3.09 σ_{i,t} 至少满足一次记为 1。"
data_sources: [CSMAR]
database_tables: [周个股回报率, 周市场加权回报率]
frequency: firm-year
source_papers: [杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

刻画个股一年内出现极端负收益（"崩盘"）的可能性。理论上对应"管理层囤积坏消息一旦释放即触发股价骤降"这一结果变量。

## Measurement

三个常用度量，文献以 Ncskew、Duvol 为主指标，以 IsCrash 作为稳健性补充：

1. 第一阶段：估计公司特有周收益率 W_{i,t}
   - 估计 r_{i,t} = α_i + β1 r_{m,t-2} + β2 r_{m,t-1} + β3 r_{m,t} + β4 r_{m,t+1} + β5 r_{m,t+2} + ε_{i,t}
   - r_{i,t} 为个股 i 第 t 周收益率，r_{m,t} 为流通市值加权市场周收益率，5 项 lead-lag 控制非同步交易（Dimson 修正）。
   - W_{i,t} = ln(1 + ε_{i,t}) 作为公司特有周收益率。
2. 负收益偏态系数 Ncskew：
   - Ncskew_{i,t} = − [ n(n-1)^{3/2} ΣW^3_{i,t} ] / [ (n-1)(n-2) (ΣW^2_{i,t})^{3/2} ]
   - n 为该年股票 i 的有效交易周数。前置负号使 Ncskew 越大代表负偏越严重，崩盘风险越高。
3. 收益上下波动率 Duvol：
   - Duvol_{i,t} = log { [(n_up - 1) Σ_{Down} W^2_{i,t}] / [(n_down - 1) Σ_{Up} W^2_{i,t}] }
   - 上行组：W_{i,t} 高于年平均收益率；下行组：低于年平均收益率。Duvol 越大代表左尾越厚。
4. 崩盘哑变量 IsCrash（稳健性）：
   - W_{i,t} ≤ Average(W_{i,t}) − 3.09 σ_{i,t} 至少满足一次，则 IsCrash_{i,t} = 1，对应标准正态 0.0001 概率区间。

## Data Source

[[csmar]] 周个股收盘价 / 周市场指数（流通市值加权）。年交易周数 < 30 的样本通常剔除以保证 Ncskew/Duvol 的统计稳定。

## Literature Variants

- 主流 Ncskew + Duvol 双指标：[[杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]]、Hutton et al. (2009)、Kim et al. (2011) 等。
- IsCrash（事件型 0/1 变量）：作为稳健性测度，配合 Logistic 回归。
- 月度版本：少数文献用月度而非周收益，但 A 股研究多沿用周频。

## Construction Steps

1. 拉取个股日/周收益与流通市值加权市场周收益，要求年内有效交易周数 ≥ 30。
2. 按 firm-year 分组跑 Dimson 5 项回归，提取残差 ε_{i,t}。
3. 构造 W_{i,t} = ln(1 + ε_{i,t})。
4. 按 firm-year 聚合 W_{i,t} 计算 Ncskew、Duvol、IsCrash。
5. 上下 1% Winsorize 连续变量。

## Stata Notes

```stata
* 假设已有 stkcd week year ret_w mkt_w
xtset stkcd_week  // 按周
* Dimson 5 项回归，按 firm-year 分组
gen ret_lag2 = mkt_w[_n-2]
gen ret_lag1 = mkt_w[_n-1]
gen ret_ld1  = mkt_w[_n+1]
gen ret_ld2  = mkt_w[_n+2]
statsby _b _se, by(stkcd year) saving(dimson, replace): ///
    regress ret_w ret_lag2 ret_lag1 mkt_w ret_ld1 ret_ld2
* 取残差
predict eps, residuals
gen w = ln(1 + eps)

* Ncskew, Duvol 按 firm-year 聚合（自定义 collapse / mata）
* 详见 An and Zhang (2013) 与 Hutton et al. (2009) 复现脚本
```

## Caveats

- 第一阶段必须使用 Dimson 修正，否则薄交易股票残差有结构性偏差。
- 对周交易数据要求严格：交易周数 < 30 的小样本年份不应纳入。
- Ncskew 与 Duvol 高度相关（本文 ρ ≈ 0.64），同时报告两个指标已成惯例。
- IsCrash 的 3.09σ 阈值对正态假设敏感，A 股残差呈胖尾，Logistic 回归时需注意稀有事件偏差。

## Related

- 数据：[[csmar]]
- 文献：[[杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]]
- 与崩盘风险相关的核心解释变量：[[institutional-investor-holding]] · [[institutional-investor-heterogeneity-stability]] · [[short-selling-eligibility]]
