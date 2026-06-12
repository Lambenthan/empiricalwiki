---
title: "多时点双重差分 + 行业-年度双向固定效应模型 (Multi-period DID with Industry-Year FE)"
slug: "multi-period-did-industry-year"
model_type: baseline
dependent_variable: "新质生产力 Npro（按因变量切换）"
core_variables: [specialized-new-transformation]
controls: [size, sale, dual, tobinq, board, indep, firmage, market]
fixed_effects: [industry, year]
standard_errors: "聚类至行业层"
sample: "中小板、创业板、科创板、北交所上市企业 2009-2022，剔除金融与 ST，缩尾 1%"
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
stata_template: "reghdfe Y Treat Controls Market, absorb(industry year) cluster(industry)"
date_updated: 2026-05-07
---

## Equation

多时点 DID 主形式：

$$Y_{i,t} = \alpha_0 + \alpha_1 \cdot \text{Treat}_{i,t} + \boldsymbol{\alpha} \cdot \text{Controls}_{i,t} + \alpha_3 \cdot \text{Market}_{k,t} + \mu_t + \nu_j + \varepsilon_{i,t}$$

其中 Treat(i,t) = I(t ≥ 认定年份(i))，对未被认定企业全样本年份为 0。处理时点因企业而异，构成多时点 DID。

固定效应替代形式（连续型处理）：

$$Y_{i,t} = \alpha_0 + \alpha_1 \cdot \text{Degree}_{i,t} + \boldsymbol{\alpha} \cdot \text{Controls}_{i,t} + \alpha_3 \cdot \text{Market}_{k,t} + \mu_t + \nu_j + \varepsilon_{i,t}$$

## Identification Logic

- 行业 FE（ν_j）吸收行业内不可观测的均值差异（行业景气、政策共振）。
- 年份 FE（μ_t）吸收宏观共同冲击（货币政策、疫情）。
- 多时点 DID 在不同企业认定年份上识别 Treat 的"前后差 + 处理 vs 未处理"双重差异。
- 不含企业 FE，因此样本期内被认定的企业固定特征仍可能进入残差，需通过 PSM 1:1 匹配与 IV 工具变量补充。

## Variable Roles

- 核心解释：[[specialized-new-transformation]]（Treat 多时点 DID 处理变量、Degree 连续度量）。
- 因变量：[[new-quality-productive-forces]]（本论文主因变量）；理论上可换为其他 firm-year 实证因变量。
- 控制：Size、Sale、Dual、TobinQ、Board、Indep、FirmAge、省级 Market 市场化指数。

## Fixed Effects and Standard Errors

- FE：行业（按一级或二级分类）+ 年度。
- SE：聚类至行业层。简冠群 (2025) 表 3 注明"括号中为聚类到行业层面的稳健标准误"。

## Expected Signs

- Treat：α₁ > 0（专精特新认定促进新质生产力）。
- Degree：α₁ > 0（发展程度越高 Npro 越高）。

## Stata Skeleton

```stata
* 多时点 DID（Treat）
reghdfe Npro Treat Size Sale Dual TobinQ Board Indep FirmAge Market, ///
    absorb(industry year) cluster(industry)

* 连续型 Degree
reghdfe Npro Degree Size Sale Dual TobinQ Board Indep FirmAge Market, ///
    absorb(industry year) cluster(industry)

* 平行趋势事件研究
forvalues k = -4(1)5 {
    gen pre`=abs(`k')' = (treat_year - year == `=abs(`k')') & `k' < 0
    gen post`k' = (year - treat_year == `k') & `k' >= 0
}
reghdfe Npro pre4 pre3 pre2 pre1 post0 post1 post2 post3 post4 post5 ///
    Size Sale Dual TobinQ Board Indep FirmAge Market, ///
    absorb(industry year) cluster(industry)
coefplot, keep(pre* post*) vertical yline(0)
```

## Interpretation Rules

- α₁ 显著为正即支持原假设；显著性需配合平行趋势 + 安慰剂 + IV + PSM 验证识别假设。
- 多时点 DID 在 Goodman-Bacon (2021) 分解下可能存在异质处理效应偏误，必要时改用 Callaway-Sant'Anna (2021) 或 Sun-Abraham (2021) 估计量做稳健性。
- 行业 + 年份 FE 不能吸收企业层固定特征，结果应配合企业 FE 稳健性。

## Related

- [[two-way-fixed-effects-firm-year]]（追加企业 FE 的稳健形式）。
- [[two-way-fixed-effects-industry-year]]（不带 DID 处理变量的纯 FE 形式）。
- [[parallel-trends-test]]（DID 平行趋势诊断）。
- [[placebo-randomization-treatment]]（DID 安慰剂检验）。
- [[psm-nearest-neighbor]]（与 DID 联用的 PSM 匹配）。
- [[简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]]（本模型主要用例）。
