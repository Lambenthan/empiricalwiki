---
title: "工具变量：剔除本企业后同行业同年份专精特新发展程度均值 (IV_Degree)"
slug: "iv-industry-mean-trans-excluding-self"
strategy_type: iv
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
assumptions:
  - "相关性：基于场域理论，同行业其他企业转型加剧行业内竞争，倒逼本企业转型"
  - "外生性：本企业新质生产力主要依赖企业内部因素，同行业其他企业转型很难直接影响本企业 Npro"
threats:
  - "行业内技术外溢与政策共振仍可能让 IV_Degree 通过非 TRANS 渠道直接影响本企业 Npro"
  - "若同一行业受同一外部冲击驱动（如行业政策、产业链共振），外生性假设可能不成立"
implementation_notes: "第一阶段 IV_Degree 系数 0.9429***（SE 0.0132），弱工具变量检验 F = 5084.13；第二阶段 Degree 系数 1.1591***（SE 0.0223），不可识别检验 p = 0.0000（简冠群 2025 表 4 列 1-2）"
date_updated: 2026-05-07
---

## Identification Problem

专精特新转型与企业新质生产力之间可能存在反向因果：新质生产力发展水平较高的企业可能更易完成专精特新转型（创新基础好、更易申请认定）。同时不可观测的企业层面创新文化、地方政府支持力度等遗漏变量可能同时影响 TRANS 与 Npro，使 OLS 估计存在内生性偏误。

## Strategy

构造剔除本企业后同行业、同年份其他企业的专精特新发展程度均值（IV_Degree）作为工具变量。借鉴经管实证常见的"行业同行均值 IV"思路，同时基于场域理论提供外生性论证：同一场域中其他企业的行动会通过竞争压力间接影响本企业，但本企业新质生产力的形成更多依赖企业内部研发投入与人才储备。

二阶段最小二乘 (2SLS)：

- 第一阶段：Degree(i,t) = π₀ + π₁·IV_Degree(i,t) + Controls + Industry + Year + u(i,t)
- 第二阶段：Npro(i,t) = α₀ + α₁·D̂egree(i,t) + Controls + Industry + Year + ε(i,t)

## Key Assumptions

- 相关性：IV_Degree 显著影响本企业 Degree，第一阶段 F 远超弱工具阈值 10。
- 外生性 / 排他性：IV_Degree 仅通过本企业 Degree 影响 Npro，不存在通过技术外溢、行业政策共振等其他通道的直接影响。
- 行业层面遗漏变量需通过控制变量与行业 FE 部分阻断，但仍是该 IV 设计的主要风险源。

## Implementation

```stata
* 构造行业同行均值 IV（按 2 位 / 3 位证监会行业代码）
bysort industry year: egen degree_ind_sum = sum(Degree)
bysort industry year: egen degree_ind_n = count(Degree)
gen IV_Degree = (degree_ind_sum - Degree) / (degree_ind_n - 1)

* 2SLS（表 4 列 1-2）
ivreghdfe Npro (Degree = IV_Degree) Size Sale Dual TobinQ Board Indep FirmAge Market, ///
    absorb(industry year) cluster(industry) first
estat firststage
```

## Diagnostics

- 第一阶段：IV_Degree 对 Degree 的系数 0.9429***（SE 0.0132），通过相关性要求。
- 弱工具变量：F = 5084.13，远超 10 的弱工具阈值。
- 不可识别检验：p = 0.0000，拒绝"模型不可识别"原假设。
- 过度识别：单一工具，无法做 Sargan / Hansen 检验。
- 第二阶段：D̂egree 系数 1.1591***（SE 0.0223），方向与基准回归一致，量级放大约 3 倍。

## Limitations

- 行业同行均值的外生性强假设：技术、政策、需求冲击在行业内同时影响 TRANS 与 Npro，IV 失效风险高。
- 单一工具，无法做过度识别检验。
- 第二阶段系数显著大于基准 OLS（0.3681 vs 1.1591），可能反映 IV 的局部平均处理效应（LATE）相对一般 OLS 的差异，也可能反映工具内生残留。
- 行业划分粒度（证监会 2 位 vs 3 位）会显著影响 IV_Degree 的方差与相关性，应做敏感性分析。
- 与同主题 [[iv-industry-mean-pc-excluding-self]]（用于 PC 而非 TRANS）思路类似，但工具针对的处理变量不同，不能互换。

## Related

- 模板模式参考：[[iv-industry-mean-pc-excluding-self]]（同行业均值 IV 用于 PC）。
- 本论文配套：[[简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]]。
