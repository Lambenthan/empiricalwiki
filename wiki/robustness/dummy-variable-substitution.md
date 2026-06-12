---
title: "虚拟变量替代连续变量稳健性（ENV_DUM 替代 LNENV）"
slug: "dummy-variable-substitution"
check_type: alternative_variable
purpose: "排除核心解释变量测算口径（连续 vs 虚拟）对结论的潜在影响"
source_papers: [黎文靖-2015-机构投资者-环境绩效-重污染]
implementation_notes: "用 ENV_DUM = 1[环境资本支出 > 0] 替代 LNENV = ln(1+环境资本支出)，重复跑全部主回归（INST、INST_LONG/SHORT、BHAR、ΔLOAN/LCOST、ETR）；论文声称结果与表 4-表 8 类似，未列具体表"
date_updated: 2026-05-07
---

## Purpose

当核心解释变量同时存在「极端右偏」和「大量零值」时，连续测度（取对数）与虚拟测度（是否大于 0）反映的信息不同：

- 连续测度回答「投入越多、效果越大」的强度问题。
- 虚拟测度回答「是否进行了任何投入」的离散问题。

替代检验的目的是确认结论不依赖于测度选择，二者方向一致即说明核心因变量响应于「投入有无」而非仅响应于「投入额大小」。

## When To Use

- 核心解释变量为高度右偏分布、大量零值的财务或政策投入指标。
- 论文采用对数化或 Winsorize 处理时，需补充虚拟变量稳健性以隔离「分布形状」假设的影响。
- 同等地，本检验也可反向使用：若主测度为虚拟变量，可补充连续测度。

## Implementation

```stata
* 主回归（连续）
gen LNENV = ln(1 + env_capex)
reg INST LNENV controls i.year i.industry, cluster(stkcd)

* 替代（虚拟）
gen ENV_DUM = (env_capex > 0)
reg INST ENV_DUM controls i.year i.industry, cluster(stkcd)

* 重复 INST_LONG (tobit)、INST_SHORT (tobit)、BHAR、ΔLOAN、LCOST、ETR 6 个方程
```

## Expected Table Pattern

替代结果应与主结果在以下三方面一致：

1. 系数符号一致。
2. 显著性方向一致（都显著或都不显著）。
3. 子样本分组的显著性边界一致（如本论文「仅 SOE 子样本显著」需在 ENV_DUM 替代下也成立）。

如果虚拟变量回归显著而连续变量不显著，提示存在阈值效应（任何环境投入都触发反应，但反应不随投入额线性递增），需在解释中讨论。

## Interpretation

黎文靖 (2015) 仅以一句话报告本稳健性结果：「结果与表 4–表 8 类似，表明本文结果不受变量定义的影响」。未列具体表格意味着读者无法判断系数大小、显著性分布是否完全一致；这是早期论文常见做法，后续期刊一般要求附录中完整披露。

如果在本项目内复现，需：

- 完整呈现替代回归结果。
- 比较系数大小：ENV_DUM 系数代表「从无到有」的离散跳跃，与 LNENV 系数（边际效应）不直接可比，但方向应一致。

## Caveats

- 「类似」一词模糊；后续审稿要求作者明确披露具体替代系数。
- 虚拟变量丢失了投入强度信息，统计功效低于连续变量。
- 当样本中 ENV_DUM = 1 的子集偏小（论文中 25.2%）时，虚拟变量的估计精度会下降，p 值可能因功效不足而上升。
- 不能替代更核心的稳健性（公司 FE、IV、PSM 等），仅排除测度形状这一具体威胁。

## Related

- [[environmental-performance]]：被替代的变量
- [[黎文靖-2015-机构投资者-环境绩效-重污染]]：稳健性的源头论文
- 相邻稳健性思路：替代样本（剔除特殊年份）、替代模型（公司 FE）、替代标准误（双向聚类）等
