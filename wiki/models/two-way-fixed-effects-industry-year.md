---
title: "行业-时间双向固定效应回归"
slug: "two-way-fixed-effects-industry-year"
model_type: baseline
dependent_variable: "explore / exploit / myopia (按因变量切换)"
core_variables: [patient-capital]
controls: [size, lev, age, roe, cash, top10, RD]
fixed_effects: [industry, year]
standard_errors: "未明示聚类（论文未报告 cluster），代飞 2025 表注仅给 t 值"
sample: "沪深 A 股 2008-2023，剔除金融与 ST，缩尾 1%"
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
stata_template: "reghdfe Y PC PC2 controls, absorb(industry year)"
date_updated: 2026-05-07
---

## Equation

主形式（线性）：

$$Y_{i,t} = \alpha_0 + \alpha_1 \cdot PC_{i,t} + \boldsymbol{\alpha} \cdot \mathrm{Controls}_{i,t} + \sum \mathrm{Ind} + \sum \mathrm{Year} + \varepsilon_{i,t}$$

二次形式（U 型 / 倒 U 型）：

$$Y_{i,t} = \xi_0 + \xi_1 \cdot PC_{i,t} + \xi_2 \cdot PC_{i,t}^2 + \boldsymbol{\xi} \cdot \mathrm{Controls}_{i,t} + \sum \mathrm{Ind} + \sum \mathrm{Year} + \varepsilon_{i,t}$$

## Identification Logic

行业 FE 吸收行业内不可观测的均值差异；年度 FE 吸收宏观共同冲击。但企业层面不可观测的时不变异质性未被吸收 → 需追加公司 FE（[[firm-fixed-effects]]）作为稳健性。

## Variable Roles

- 核心解释：[[patient-capital]]（含其平方项）。
- 因变量：[[exploratory-innovation]] / [[exploitative-innovation]] / [[managerial-myopia]]。
- 控制：企业规模 (size, ln 资产)、杠杆 (lev)、上市年限 (age)、ROE、现金流动负债比 (cash)、前十大股东持股 (top10)、研发投入强度 (RD)。

## Fixed Effects and Standard Errors

- FE：行业（按一级或二级分类）+ 年度。
- SE：代飞 2025 未明确聚类，仅报 t 值。本项目复现时建议至少在企业层聚类。

## Expected Signs

- explore：α₁ > 0（耐心资本促进探索式创新）。
- exploit：ξ₁ < 0、ξ₂ > 0（U 型，先抑后促）。
- myopia：β₁ < 0（耐心资本缓解短视）。

## Stata Skeleton

```stata
* 一次项
reghdfe explore PC size lev age roe cash top10 RD, absorb(industry year) cluster(stkcd)

* 含二次项的 U 型
gen PC2 = PC^2
reghdfe exploit PC PC2 size lev age roe cash top10 RD, absorb(industry year) cluster(stkcd)

* Sasabuchi U 型显著性检验
utest PC PC2
```

## Interpretation Rules

- 二次项系数 ξ₂ > 0 + Sasabuchi p < 0.05 + 拐点位于样本范围内（Fieller CI）→ 可断定 U 型。
- 仅看二次项系数符号不足以判定，必须做 Sasabuchi 检验（[[sasabuchi-shape-test]]）。

## Related

- [[firm-fixed-effects]]（追加 FE 维度的稳健形式）。
- [[instrumental-variable-2sls]]（处理反向因果的 IV 形式）。
- [[代飞-2025-耐心资本-双元创新-管理者短视]]（本模型主要用例）。
