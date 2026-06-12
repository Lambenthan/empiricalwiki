---
title: "两阶段残差介入法 (Two-stage Residual Inclusion)"
slug: "two-stage-residual-inclusion"
strategy_type: other
source_papers: [胡楠-2021-管理者短视主义-长期投资-文本分析]
assumptions:
  - "其他短视代理变量与环境因素能充分捕获短视的可观测部分"
  - "第一阶段残差代表短视文本指标的『增量信息』"
  - "残差与第二阶段方程的扰动项不相关"
threats:
  - "第一阶段控制变量遗漏会污染残差含义"
  - "若文本指标本身被遗漏变量驱动，残差仍残留偏误"
implementation_notes: "Chen et al. (2013) 思路；先回归 Myopia_Index 在其他短视代理变量与环境因素上，再以残差替代 Myopia_Index 进入主回归"
date_updated: 2026-05-07
---

## Identification Problem

短视文本指标可能与其他短视代理（短期投资比例、股东换手率、盈余公告频率）以及环境因素（薪酬、亏损、机构投资者持股、分析师关注度）共变。直接进入主回归时，无法判断回归系数捕获的是文本指标本身的特质信息还是这些可观测代理的混合。

## Strategy

两阶段残差介入法（Chen et al. 2013）：

阶段 1：

```
Myopia_Index_it = α₀ + α₁·Short_Invest_it + α₂·Turnover_it + α₃·MF_it
                + Controls_it + ΣYear + ΣIndustry + ε_it
```

控制其他短视代理变量与环境因素后，取残差 Residual_it。

阶段 2：将主回归中的 Myopia_Index 替换为 Residual：

```
Capex_it / R&D_it = α₀ + α₁·Residual_it + Controls_it + ΣYear + ΣIndustry + ε_it
```

若 α₁ 仍显著为负，说明文本指标包含其他代理变量未捕获的"管理者特质增量信息"，并且这部分增量信息独立地预测长期投资减少。

## Key Assumptions

- 第一阶段控制变量充分：包含 Short_Invest（短期投资比例）、Turnover（股东换手率）、MF（管理层盈余公告次数）、Loss、Gpay、IO、Analyst 等。
- 残差是文本指标的"特质信息"代理：依赖于第一阶段方程 R² 的差距能反映方差分解结论。
- 残差外生于第二阶段方程的扰动项：本质是工具变量条件的变体。

## Implementation

胡楠等 (2021) 表 10：

- 第 (1)、(4) 列：第一阶段回归。
- 第 (2)、(3)、(5)、(6) 列：第二阶段以 Residual 替代 Myopia_Index。
- 结果：Residual(t) → Capex 系数 -0.014（10% 显著），Residual(t) → R&D 系数 -0.012（1% 显著）；滞后版同样显著。

```stata
* 第一阶段
reg Myopia_Index Short_Invest Turnover MF controls i.year i.industry, cluster(stkcd)
predict Residual, residuals

* 第二阶段
reghdfe Capex Residual controls, absorb(industry year) cluster(stkcd)
reghdfe RD Residual controls, absorb(industry year) cluster(stkcd)
```

## Diagnostics

- 第一阶段 R² 差距：用以验证文本指标主要由管理者特质而非可观测代理驱动。胡楠等 (2021) 结合 Hassan et al. (2019) 方差分解（环境因素 0.7%、管理者 FE 56.4%）佐证。
- 系数稳定性：Residual 与原 Myopia_Index 系数在符号、显著性上保持一致。

## Limitations

- 第一阶段控制变量必须充分；否则残差仍含被遗漏的可观测信号。
- 不能解决与第一阶段方程同时遗漏的不可观测变量造成的偏误。
- 与传统 IV 不同：残差并非外生工具，仅是"减去可观测部分"的算术构造。

## Related

- 主用例：[[胡楠-2021-管理者短视主义-长期投资-文本分析]]
- 强化方向：可与 [[firm-fixed-effects]]、[[instrumental-variable-2sls]] 并行使用，三者从不同维度处理内生性。
