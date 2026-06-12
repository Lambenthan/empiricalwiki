---
title: "工具变量 2SLS（行业耐心资本均值 + 滞后一期）"
slug: "instrumental-variable-2sls"
strategy_type: iv
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
assumptions: ["相关性：行业耐心资本均值与企业 PC 高度相关；PC 滞后一期与当期 PC 高度相关", "外生性：行业 PC 均值不直接影响企业当期创新决策；滞后 PC 通过控制变量隔绝其它路径"]
threats: ["行业内技术外溢可能让行业 PC 均值直接影响企业创新", "滞后 PC 与同期不可观测冲击相关时仍会内生"]
implementation_notes: "Cragg-Donald F = 280000 通过弱工具阈值；Sargan p = 0.590 (代飞 2025 正文，与表中 P-val 0.000 不符；以正文为准)"
date_updated: 2026-05-07
---

## Identification Problem

PC 与企业创新结果之间存在双向因果：高创新企业可能更易吸引耐心资本，使 OLS 估计偏误。

## Strategy

构造两个工具变量：

- IV1 = 各行业 PC 均值（同行业其他企业的耐心资本平均水平）；
- IV2 = PC 滞后一期。

二阶段最小二乘 (2SLS)，第一阶段 PC 对 IV1+IV2 + Controls + FE 回归，得到拟合值；第二阶段 explore/exploit 对拟合 PC + Controls + FE 回归。

## Key Assumptions

- 相关性：第一阶段系数显著 + Cragg-Donald F > 临界值。
- 外生性 / 排他性：IV 仅通过 PC 影响创新；行业均值需排除技术外溢的直接影响（强假设，作者用控制变量隔断）。
- 过度识别检验：Sargan / Hansen 检验不拒绝零假设。

## Implementation

```stata
ivreghdfe explore (PC = IV1 IV2) size lev age roe cash top10 RD, absorb(industry year) cluster(stkcd) first
ivreghdfe exploit (PC PC2 = IV1 IV2 IV1_sq IV2_sq) size lev age roe cash top10 RD, absorb(industry year) cluster(stkcd)
estat firststage
estat overid
```

## Diagnostics

- 弱工具：Cragg-Donald Wald F、Kleibergen-Paap rk F；本文 F=280000 远超 10% maximal IV size 临界值。
- 过度识别：Sargan / Hansen J 统计量 p > 0.1。
- 一阶段 R² 与系数显著性。

## Limitations

- 行业 PC 均值的外生性仍可疑：技术、政策、需求冲击在行业内同时影响 PC 与创新。
- 滞后 PC 的外生性受一阶自相关挑战；如不可观测冲击 AR(1)，IV2 失效。
- 二阶段 PC² 的 IV 构造需要 IV1²/IV2² 等额外工具，强相关性更难满足。
