---
title: "OLS + 行业-年度固定效应 + 公司聚类标准误（含 Tobit 变体）"
slug: "ols-industry-year-fe-cluster"
model_type: baseline
dependent_variable: "INST / INST_LONG / INST_SHORT / BHAR / ΔLOAN / LCOST / ETR（按方程切换）"
core_variables: [LNENV, ENV_DUM]
controls: [VOL, TRSHARE, STATE, TOP1, ROA, DR, SGROW, SIZE, MKTB, AGE, BETA, MORTGAGE, INVINT, IDRATIO, BSIZE]
fixed_effects: [industry, year]
standard_errors: "公司层聚类（Cluster by stkcd）"
sample: "2004-2010 年 A 股 8 个重污染行业上市公司，3,843 obs；BHAR 模型 3,562 obs；LCOST 模型 3,159 obs"
source_papers: [黎文靖-2015-机构投资者-环境绩效-重污染]
stata_template: "reg INST LNENV controls i.year i.industry, cluster(stkcd)"
date_updated: 2026-05-07
---

## Equation

主方程：

$$Y_{i,t} = \beta_0 + \beta_1 LNENV_{i,t} + \boldsymbol{\beta}^\top \mathrm{Controls}_{i,t} + \sum_{t} \mathrm{Year}_t + \sum_{j} \mathrm{Industry}_j + \varepsilon_{i,t}$$

其中 Y 视方程切换：INST（持股比例）、BHAR（异常回报）、ΔLOAN（贷款增长率）、LCOST（贷款成本）、ETR（所得税率）。

Tobit 变体（用于 INST_LONG / INST_SHORT 模型）：

$$Y^*_{i,t} = \beta_0 + \beta_1 LNENV_{i,t} + \boldsymbol{\beta}^\top \mathrm{Controls}_{i,t} + \sum \mathrm{Year} + \sum \mathrm{Industry} + \varepsilon_{i,t}, \quad Y_{i,t} = \max(0, Y^*_{i,t})$$

因 INST_LONG、INST_SHORT 大量观测为 0（左截断）。

## Identification Logic

- 行业固定效应吸收行业内时不变异质性（如行业污染强度、行业政府关注度）。
- 年度固定效应吸收宏观共同冲击（如环保政策外生变化、监管力度年度波动）。
- 公司层聚类标准误处理同一公司内的序列相关。
- 1% Winsorize 控制极端值。
- **未处理**：公司层时不变不可观测因素（无公司 FE）、反向因果（无 IV）、潜在自选择偏差（无 PSM/Heckman）。这是早期文献的典型识别局限。

## Variable Roles

- 核心解释：[[environmental-performance]]（LNENV）；稳健性用 ENV_DUM 替代。
- 被解释变量随方程切换：[[institutional-ownership]]、BHAR、ΔLOAN、LCOST、ETR。
- 关键调节 / 异质性：STATE（实际控制人国有为 1，参见[[state-ownership-split]]）。
- 控制变量按 INST 方程为基准（VOL、TRSHARE、TOP1、ROA、DR、SGROW、SIZE、MKTB、AGE）；BHAR 方程加 BETA、去 VOL/TRSHARE/TOP1；ΔLOAN/LCOST 方程加 IDRATIO、BSIZE、MORTGAGE、INVINT；ETR 方程仅保留 DR、SIZE、MKTB、SGROW、MORTGAGE、INVINT。

## Fixed Effects and Standard Errors

- FE：Industry（按 8 个重污染行业代码）+ Year。
- SE：公司层聚类（cluster by stkcd），「Cluster 分析方法按照公司代码调整标准误」。
- 论文未明示是否同时聚类公司+年；通常单层公司聚类是中国实证的最常见做法。

## Expected Signs

- INST 方程：β₁(LNENV) > 0（环境绩效吸引机构投资者）。
- INST_LONG 方程：β₁ > 0（仅长期机构会响应）。
- INST_SHORT 方程：β₁ ≈ 0（短期机构不响应）。
- BHAR 方程：β₁ > 0（环境绩效带来超额回报，仅 SOE 子样本）。
- ΔLOAN 方程：β₁ > 0；LCOST 方程：β₁ < 0；ETR 方程：β₁ < 0（政府政策支持，仅 SOE 子样本）。

## Stata Skeleton

```stata
* INST 主回归
reg INST LNENV VOL TRSHARE STATE TOP1 ROA DR SGROW SIZE MKTB AGE i.year i.industry, cluster(stkcd)

* INST_LONG / INST_SHORT 用 Tobit
tobit INST_LONG LNENV VOL TRSHARE STATE TOP1 ROA DR SGROW SIZE MKTB AGE i.year i.industry, ll(0)
tobit INST_SHORT LNENV VOL TRSHARE STATE TOP1 ROA DR SGROW SIZE MKTB AGE i.year i.industry, ll(0)

* BHAR 回归
reg BHAR LNENV STATE ROA DR SGROW SIZE MKTB BETA i.industry, cluster(stkcd)

* 银行贷款 / 税收方程
reg DLOAN LNENV STATE TOP1 ID_RATIO BSIZE ROA DR SGROW SIZE MKTB AGE MORTGAGE INVINT i.year i.industry, cluster(stkcd)
reg LCOST LNENV STATE TOP1 ID_RATIO BSIZE ROA DR SGROW SIZE MKTB AGE MORTGAGE INVINT i.year i.industry, cluster(stkcd)
reg ETR LNENV STATE DR SIZE MKTB SGROW AGE MORTGAGE INVINT i.year i.industry, cluster(stkcd)

* 异质性：按 STATE 分组重复（参见 state-ownership-split）
```

## Interpretation Rules

- 主回归 LNENV 系数 0.001（INST）虽小，但因 LNENV 标度大（最大值 20.318），从最小到最大跨越对应 INST 提升约 2 个百分点（0.001 × 20 = 0.02），相对均值 0.157 是约 12% 的相对效应，经济意义可解释。
- 解释三组结果时必须强调「仅在国有企业样本中显著」这一边界条件，不要泛化到非国有企业。
- 早期文献识别策略较弱，引用本模型时建议补充 IV、公司 FE、PSM 等额外稳健性。

## Related

- [[two-way-fixed-effects-industry-year]]（结构相同的本项目内变体；本项目主方程也常用此 FE 设计）
- [[firm-fixed-effects]]（建议补充的稳健性 FE）
- [[黎文靖-2015-机构投资者-环境绩效-重污染]]（本模型主用例）
