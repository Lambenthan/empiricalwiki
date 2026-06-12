---
title: "并购事件横截面 OLS（被解释变量为剔除行业 ROE 变化量）"
slug: "ols-cross-section-ma-event"
model_type: baseline
dependent_variable: "state-soe-ma-performance"
core_variables: [stable-institutional-investors-turnover, transactional-institutional-investors-turnover]
controls: [SH1, ID, LEV, CASH, ROA, SIZE, RMA, PT, YEAR]
fixed_effects: [year]
standard_errors: "未明示聚类（论文表 4 仅报 t 值，未指明 cluster）"
sample: "2010-2014 年 A 股国有上市公司并购事件 530 起，剔除金融、ST、上市年限不足、小并购等"
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
stata_template: "reg adj_dROE STABLEINS TRANSINS SH1 ID LEV CASH RMA PT SIZE ROA i.year, robust"
date_updated: 2026-05-07
---

## Equation

```
ΔADJ_ROE_{deal} = β₀ + β₁·STABLEINS + β₂·TRANSINS
                 + γ₁·SH1 + γ₂·ID + γ₃·LEV + γ₄·CASH + γ₅·ROA + γ₆·SIZE
                 + γ₇·RMA + γ₈·PT
                 + Σ_y δ_y·YEAR_y
                 + ε
```

观测单位为 deal-event；同一公司可对应多起并购，每起并购作为独立观测。

## Identification Logic

并购事件在时间维度上零散发生，不构成完整面板，故采用横截面 OLS 而非双向固定效应。识别策略依赖：

1. 被解释变量为差分形式（前后一年 ROE 差），消除并购前公司基本面对绝对绩效的影响；
2. 被解释变量再剔除行业均值，消除行业景气共同冲击；
3. 控制变量取 t-1 期值（公司治理与财务特征滞后），缓解反向因果；
4. 加入年度虚拟变量吸收 5 年研究窗口的宏观共同冲击。

行业 FE 已通过 ADJ 步骤间接吸收，故未单独加入行业虚拟变量。

## Variable Roles

- 核心解释：[[stable-institutional-investors-turnover]] (STABLEINS)、[[transactional-institutional-investors-turnover]] (TRANSINS)，配对呈现，分别检验 H1 与 H2。
- 因变量：[[state-soe-ma-performance]] (ΔADJ_ROE)。
- 公司治理控制：第一大股东持股 (SH1)、独立董事比例 (ID)。
- 公司财务控制：资产负债率 (LEV)、自由现金流 / 总资产 (CASH)、总资产收益率 (ROA)、公司规模 SIZE = ln 总资产。
- 并购事件控制：[[related-party-ma]] (RMA)、支付方式 (PT, 现金 = 1)。
- 时间控制：4 个年度虚拟变量。

## Fixed Effects and Standard Errors

- FE：仅年度（行业已在 ADJ 步骤剔除）。
- SE：周绍妮 (2017) 表 4 仅报 t 值，未明确聚类设置；本项目复现时建议至少在公司层聚类（同公司多起并购观测相关）。

## Expected Signs

- β₁ > 0（H1：稳定型机构投资者促进国企并购绩效）。
- β₂ > 0（H2：交易型机构投资者促进国企并购绩效）。
- 论文实证：β₁ ≈ −0.002 (n.s., H1 不支持)、β₂ ≈ 0.004*** (1%, H2 支持)。

## Stata Skeleton

```stata
* 全样本基准（表 4 列 1）
reg adj_dROE STABLEINS TRANSINS SH1 ID LEV CASH RMA PT SIZE ROA i.year, robust

* 关联并购组（表 4 列 2）
reg adj_dROE STABLEINS TRANSINS SH1 ID LEV CASH PT SIZE ROA i.year if RMA == 1, robust

* 非关联并购组（表 4 列 3）
reg adj_dROE STABLEINS TRANSINS SH1 ID LEV CASH PT SIZE ROA i.year if RMA == 0, robust
```

注：子样本回归中 RMA 已在样本筛选中固定，需从控制变量中剔除（避免完全共线）。

## Interpretation Rules

- β₁ 与 β₂ 同时显著为正才支持双重股东积极主义假设；
- 若仅 β₂ 显著、β₁ 不显著，需引入"被动 vs 主动投资"假设解释（见 [[周绍妮-2017-机构投资者-国企-并购绩效]] 理论机制）；
- 子样本回归中两类机构投资者均不显著，需结合政府干预假说解释（参见 [[related-party-ma-split]]）。

## Related

- 主用论文：[[周绍妮-2017-机构投资者-国企-并购绩效]]
- 配套异质性切分：[[related-party-ma-split]]
- 内生性稳健性：[[iv-industry-mean-stable-region-mean-trans]]
- 替代被解释变量稳健性：[[alternative-ma-performance-measures]]
