---
title: "公司固定效应"
slug: "firm-fixed-effects"
strategy_type: fixed_effects
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
assumptions: ["不可观测异质性是企业层面时不变的", "PC 在企业内部仍存在足够时序变异"]
threats: ["遗漏变量若随时间变化，仍偏误", "企业内 PC 时序变异不足时系数被吸收"]
implementation_notes: "在 reghdfe 的 absorb 中加入 stkcd"
date_updated: 2026-05-07
---

## Identification Problem

行业 + 年度 FE 不能吸收企业层面的不可观测异质性（如管理团队稳定性、企业文化、董事会结构的时不变维度）。这些异质性可能同时驱动 PC 配置与创新水平，造成偏误。

## Strategy

加入公司固定效应（stkcd dummy），与行业、年度 FE 共存（行业 FE 在加入企业 FE 后被吸收）。回归方程：

`Y_it = α₀ + α₁·PC_it + α·Controls_it + μ_i + λ_t + ε_it`

其中 μ_i 为企业 FE，λ_t 为年度 FE。

## Key Assumptions

- 企业级遗漏变量是时不变的（强假设；CEO 更换、治理改革等会违反）。
- PC 在企业内部存在显著时序变异（否则系数被吸收）。

## Implementation

```stata
reghdfe explore PC controls, absorb(stkcd year) cluster(stkcd)
reghdfe exploit PC PC2 controls, absorb(stkcd year) cluster(stkcd)
```

## Diagnostics

- within R² 上升幅度反映企业 FE 吸收的方差占比。
- F-test on absorbed FE。
- 与不含 FE 模型的系数比较：若大幅缩小，说明遗漏变量偏误明显。

## Limitations

- 不能处理时变遗漏变量。
- 与 PC 的低组内变异冲突时识别力受限。
- 与 IV 不互斥，二者并行可缓解不同来源的内生性。
