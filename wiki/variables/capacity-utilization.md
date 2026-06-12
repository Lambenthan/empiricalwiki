---
title: "产能利用率 (Capacity Utilization, CU)"
slug: "capacity-utilization"
construct: "产能利用率"
role: dependent
measurement: "理论上为企业实际产出与潜在最大产出之比；实证常见三类口径：随机前沿生产函数 SFA、数据包络分析 DEA、简单比率法（如总资产周转率）。何文彬 (2025) 采用 SFA Cobb-Douglas 法，CU = TE = exp(-μ)。"
data_sources: [国泰安 CSMAR, Wind]
database_tables: [资产负债表, 利润表, 公司基本信息表, 应付职工薪酬]
frequency: firm-year
source_papers: [何文彬-2025-耐心资本-产能利用率]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

产能利用率衡量企业产出占其可达最大产出的比例，是评估企业是否存在产能过剩的微观核心指标。理论值范围 (0, 1]，越靠近 1 表示产能利用越充分；中国上市公司样本均值多在 0.7–0.8 之间。

## Measurement

实证文献至少有三类操作化路径，各有数据可得性与识别假设差异。本卡片不锁定单一公式，由各论文按场景选择：

- **SFA 法（随机前沿生产函数，Stochastic Frontier Analysis）**：拟合 Cobb-Douglas 生产函数，把误差分解为对称随机噪声 v 与单边无效率项 μ；CU = TE = exp(-μ)。需要资本、劳动、产出三类投入产出数据。何文彬 (2025) 借鉴李雪松等 (2017) 采用此法。
- **DEA 法（数据包络分析）**：构造非参数效率前沿，CU = 实际产出向量在前沿面上的径向距离。常配合 SBM、ML 指数等变体；适合多产出多投入情形。
- **简单比率法**：如总资产周转率（营业收入 / 总资产）、设备利用率、行业层产能利用率指数等；门槛低但识别力弱，常作为稳健性替代变量。

## Data Source

[[csmar]] 与 Wind 数据库提供企业层财务数据：

- 资本投入 K：常用总资产（账面值）或固定资产净额。
- 劳动投入 L：理想字段为"职工人数"，但 CSMAR 该字段缺失率较高，可用"应付职工薪酬"或"工资支出"作为代理。
- 产出 Y：主营业务收入。

宏观行业层产能利用率（如国家统计局工业产能利用率季度数据）可作为外生工具或对照基准。

## Literature Variants

- **SFA Cobb-Douglas（何文彬 2025）**：ln(Y) = α + β₁·ln(K) + β₂·ln(L) + v - μ；MLE 估计，TE = exp(-μ)。投入：K = 总资产、L = 企业人数、Y = 主营业务收入。
- **总资产周转率（何文彬 2025 稳健性）**：CU_adj = 营业收入 / 总资产。
- **DEA-SBM 效率法**：见后续文献变体；本项目尚未 ingest。
- **行业产能利用率（国家统计局）**：宏观季度指标，常作为分组依据或外生冲击。

## Construction Steps

SFA 操作化（何文彬 2025 路径）：

1. 取企业 i 在 t 年的总资产 K_it（CSMAR 资产负债表）。
2. 取企业 i 在 t 年的劳动投入 L_it（CSMAR 公司基本信息表"职工总数"或代理变量）。
3. 取企业 i 在 t 年的主营业务收入 Y_it（CSMAR 利润表）。
4. 对 ln(Y)、ln(K)、ln(L) 做面板 SFA 估计：`xtfrontier ln_y ln_k ln_l, ti`（Battese-Coelli 1992 时变模型）。
5. 预测技术效率：`predict te, te`。
6. 直接令 CU_it = TE_it = exp(-μ_it)。

总资产周转率口径：`gen CU_adj = revenue / total_asset`。

## Stata Notes

```stata
* SFA 估计 — 时变无效率 Cobb-Douglas
xtset stkcd year
gen ln_y = ln(revenue)
gen ln_k = ln(total_asset)
gen ln_l = ln(employees)
xtfrontier ln_y ln_k ln_l, ti
predict cu_sfa, te

* 简单比率法
gen cu_simple = revenue / total_asset

* 缩尾
winsor2 cu_sfa cu_simple, cuts(1 99) replace
```

## Caveats

- SFA 对函数形式与无效率分布假设敏感（半正态 vs 截尾正态）；模型设定误判会扭曲 TE。
- 劳动投入数据可得性差时改用代理变量会引入测量误差。
- DEA 与 SFA 结果不一定线性相关，论文需明确口径并互为稳健性。
- CU 取值有理论上界 1；做对数变换前需检查样本是否真的小于 1。
- 不同测算方法间相关性中等，禁止把不同口径直接当作同一变量替换使用。

## Related

- 主回归被解释变量见 [[何文彬-2025-耐心资本-产能利用率]]。
- 配套核心解释变量：[[patient-capital]]（PC_Sd、PC_Rl 两维度）。
- 数据底座：[[csmar]]。
