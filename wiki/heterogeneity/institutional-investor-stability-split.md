---
title: "稳定型 vs 交易型机构投资者样本切分"
slug: "institutional-investor-stability-split"
grouping_variable: "INVW（[[institutional-investor-heterogeneity-stability]] 哑变量）"
grouping_rule: "INVW=1（稳定型，SD ≥ 行业-年中位数）vs INVW=0（交易型，SD < 行业-年中位数）"
rationale: "持股稳定性差异决定机构投资者监督上市公司的边际收益与意愿，进而决定其对股价崩盘风险的方向性影响。稳定型监督而交易型合谋/羊群，因此切分能识别两条异质性路径。"
source_papers: [杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]
date_updated: 2026-05-07
---

## Grouping Logic

依据 [[institutional-investor-heterogeneity-stability]] 中 SD 比指标与行业-年中位数门槛得到 INVW 哑变量：

- INVW = 1：稳定型机构投资者样本组，n = 2128（H2 OLS）/ 2020（H3 DID）。
- INVW = 0：交易型机构投资者样本组，n = 2036（H2 OLS）/ 1669（H3 DID）。
- 切分后样本合计 4164，约占全样本 8025 的一半（无机构投资者持股的样本被切分阶段排除）。

## Theoretical Rationale

- 稳定型机构投资者持股期长 + 持股比例高 → 监督收益 > 监督成本 → 主动治理 → 降低崩盘风险。
- 交易型机构投资者持股期短 → 追求短期价差 → 与管理层合谋 / 羊群行为 → 增加崩盘风险。
- 卖空机制对两类机构投资者的影响方向预期相反但结果方向一致：均使崩盘风险下降，但作用机制不同（稳定型加强治理 vs 交易型被价格效率约束）。

## Sample Split

- 切分变量：INVW_{i,t-1}（滞后一期）。
- 切分时点：每个公司-年根据当年-行业 SD 中位数独立判定。同一公司在不同年份可在两组之间切换。
- 子样本独立估计：对每个组分别跑模型 (6) 和模型 (7)，比较核心系数符号和显著性。

## Model

子样本 OLS：

```
Crash_{i,t} = α0 + α1 INVH_{i,t-1} + 控制变量 + Year + Ind + ε
   under {INVW=1} 与 {INVW=0}
```

子样本 DID：

```
Crash_{i,t} = γ0 + γ1 INVH×SSC×After + ... + 控制变量 + Year + Ind + ε
   under {INVW=1} 与 {INVW=0}
```

## Interpretation

两类样本下系数方向相反 → 验证机构投资者异质性对崩盘风险的方向性影响差异，支持 H2。
两类样本下三重交互项均显著为负 → 验证卖空机制对两类机构投资者-崩盘风险关系的调节方向，支持 H3。

切分而非加交互 INVH × INVW 的好处：允许除主效应外所有控制变量系数也在两组间不同，更灵活。代价是损失自由度，且无法直接做"两组系数差异是否显著"的检验。

## Related

- 文献：[[杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]]
- 切分变量：[[institutional-investor-heterogeneity-stability]]
- 配套机制：[[stable-investor-monitoring-channel]]
- 配套识别：[[did-short-selling-pilot]]
