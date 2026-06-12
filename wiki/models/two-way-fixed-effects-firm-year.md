---
title: "企业 + 年份双向固定效应回归（Firm × Year FE）"
slug: "two-way-fixed-effects-firm-year"
model_type: baseline
dependent_variable: green-transformation
core_variables: [patient-capital]
controls: [Size, FirmAge, ROE, Quick, Growth, Lev, Indep, Dual, Top1]
fixed_effects: [firm, year]
standard_errors: "聚类至企业层面（论文未在表注明确聚类方式，按经管面板惯例假设企业聚类）"
sample: "2012—2023 年沪深 A 股上市公司，30084 个企业-年度观测"
source_papers: [谢婷婷-2025-耐心资本-动态能力-绿色转型]
stata_template: "reghdfe green PC controls, absorb(firmid year) cluster(firmid)"
date_updated: 2026-05-07
---

## Equation

Green(it) = α₀ + α₁·PC(it) + Σ α_k·Control_k(it) + δ_i + λ_t + ε(it)

其中 δ_i 为企业固定效应，λ_t 为年份固定效应，Control_k 为 9 个企业层面控制变量。

## Identification Logic

通过企业固定效应吸收所有企业层面不随时间变化的不可观测异质性（行业、产权、地理位置等若不随时间变化均被吸收）。年份固定效应吸收宏观共同冲击（"双碳"政策、绿色金融政策、疫情等共同时间趋势）。在剩余的"企业×年度"两维变化中识别 PC 对 Green 的影响。

与代飞 (2025) 的 [[two-way-fixed-effects-industry-year]] 不同：本文使用更严格的 firm FE 而非 industry FE，能吸收企业层面所有时不变特征，但代价是无法识别仅由企业内部时间变化驱动的、稳定的截面差异。

## Variable Roles

- 因变量：Green（绿色转型词频指标）。
- 核心变量：PC（耐心资本，战略型机构投资者持股比例）。
- 控制变量（9 个）：
  - Size：期末总资产对数。
  - FirmAge：LN(年份 − 成立年 + 1)。
  - ROE：净资产收益率。
  - Quick：速动比率。
  - Growth：营收增长率。
  - Lev：资产负债率。
  - Indep：独立董事占比。
  - Dual：两职合一虚拟变量。
  - Top1：第一大股东持股比例。
- 固定效应：Firm + Year。

## Fixed Effects and Standard Errors

- 固定效应：absorb(firmid year)。
- 表 4 列 (3) 在此基础上额外加控城市固定效应 absorb(firmid year city)。
- 标准误聚类：原文未明确，常规做法聚类到企业（cluster(firmid)）。

## Expected Signs

- α₁（PC 系数）：预期为正（H1）。
- Size：可正可负，规模与绿色转型关系混合证据。
- Lev：负向（高负债企业短期压力大，绿色投入受限）。
- Top1：负向或不显著（股权集中度对绿色行为预期不一致）。

## Stata Skeleton

```stata
* 主回归（表 3 列 2）
reghdfe green PC size firmage roe quick growth lev indep dual top1, ///
    absorb(firmid year) cluster(firmid)

* 加控城市固定效应（表 4 列 3）
reghdfe green PC size firmage roe quick growth lev indep dual top1, ///
    absorb(firmid year city) cluster(firmid)
```

## Interpretation Rules

- 单位：PC 在 [0, 0.91]，Green 在 [0, 4.04]，均无量纲化处理；α₁ = 0.212 表示 PC 上升 1 个单位（即从 0% 战略型机构持股到 100% 战略型机构持股），Green 增加 0.212。结合样本 PC 标准差 0.24，1 个标准差变化对应 Green 提高 0.05，约为 Green 标准差 0.84 的 6%。
- 显著性 1% 水平为正即支持 H1。
- 中介效应、调节效应、异质性分析均在此基准模型基础上扩展。

## Related

- 来源论文：[[谢婷婷-2025-耐心资本-动态能力-绿色转型]]。
- 因变量：[[green-transformation]]。
- 核心变量：[[patient-capital]]。
- 中介通道：[[dynamic-capability-mediation]]。
- 内生性策略：[[iv-industry-mean-pc-excluding-self]]。
- 对照模型：[[two-way-fixed-effects-industry-year]]（代飞 2025，使用 industry FE 而非 firm FE）。
