---
title: "工具变量：剔除本企业后的同行业同期耐心资本均值（iv_mean）"
slug: "iv-industry-mean-pc-excluding-self"
strategy_type: iv
source_papers: [谢婷婷-2025-耐心资本-动态能力-绿色转型]
assumptions:
  - "相关性：行业内其他企业的耐心资本水平与本企业 PC 高度相关"
  - "外生性：剔除本企业后的行业 PC 均值不通过 PC 以外的渠道直接影响本企业绿色转型"
threats:
  - "行业内技术外溢与政策共振仍可能让 iv_mean 直接影响本企业绿色转型"
  - "若同一行业受同一外部冲击驱动，外生性假设可能不成立"
implementation_notes: "第一阶段 iv_mean 系数 0.253（t = 20.74），第二阶段 PC 系数 0.695（t = 3.32），均在 1% 水平显著（谢婷婷 2025 表 5 列 1-2）"
date_updated: 2026-05-07
---

## Identification Problem

PC 与企业绿色转型之间可能存在反向因果：绿色转型表现良好的企业可能更易吸引战略型机构投资者（耐心资本流入），使 OLS 估计存在内生性偏误。

## Strategy

构造剔除本企业后同行业、同年的耐心资本平均持股比例作为工具变量（iv_mean）。借鉴姜广省等 (2021) 在绿色投资者研究中的做法，将"自身所在行业其他企业的处理变量均值"作为对自身处理变量的工具，是经管实证常见的"行业同行均值 IV"思路。

二阶段最小二乘 (2SLS)：

- 第一阶段：PC(it) = π₀ + π₁·iv_mean(it) + Controls + Firm + Year + u(it)
- 第二阶段：Green(it) = α₀ + α₁·PĈ(it) + Controls + Firm + Year + ε(it)

## Key Assumptions

- 相关性：iv_mean 显著影响本企业 PC，第一阶段系数显著且 F 统计量大于 10。
- 外生性 / 排他性：iv_mean 仅通过 PC 影响 Green，不存在通过技术外溢、政策共振、行业需求冲击等其它通道的直接影响。
- 实务上需通过控制变量（Size、Lev、行业层面差异等）尽可能阻断潜在外溢路径。

## Implementation

```stata
* 构造行业同行均值 IV（按 2 位证监会行业代码）
bysort industry year: egen pc_ind_sum = sum(PC)
bysort industry year: egen pc_ind_n = count(PC)
gen iv_mean = (pc_ind_sum - PC) / (pc_ind_n - 1)

* 2SLS（表 5 列 1-2）
ivreghdfe green (PC = iv_mean) size firmage roe quick growth lev indep dual top1, ///
    absorb(firmid year) cluster(firmid) first
estat firststage
```

## Diagnostics

- 第一阶段：iv_mean 对 PC 的系数 0.253***（t = 20.74），通过相关性要求。
- 弱工具：原文未报告 Cragg-Donald F 或 Kleibergen-Paap rk F，仅给出 t 统计量；按 t² ≈ 430 推算等价 F 远超弱工具阈值 10。
- 过度识别：单一工具，无法做 Sargan / Hansen 检验。
- 第二阶段 PĈ 系数 0.695***（t = 3.32），方向与基准回归一致，量级放大约 3 倍。

## Limitations

- 行业同行均值的外生性强假设：技术、政策、需求冲击在行业内同时影响 PC 与 Green，IV 失效。
- 未与第二组工具变量（PC 滞后一期 iv2）做联合估计，只是分别给出两套 2SLS 结果。
- 第二阶段 PC 系数显著大于基准 OLS（0.212 vs 0.695），可能反映 IV 估计的局部平均处理效应（LATE）相对一般 OLS 的差异，也可能反映工具内生残留。
- 行业划分粒度（证监会 2 位 vs 3 位）会显著影响 iv_mean 的方差与相关性。
