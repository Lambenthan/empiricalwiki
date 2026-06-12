---
title: "双重差分 DID（经典 2×2 与多期交错）"
slug: "difference-in-differences"
strategy_type: did
source_papers: []
assumptions: ["平行趋势：无处理时，处理组与控制组的结果变量走势相同", "无预期效应：政策宣布前个体不提前调整行为", "SUTVA：个体间无溢出，处理无强度差异（或已建模）"]
threats: ["平行趋势不可直接检验，只能用前期趋势做旁证", "交错处理下 TWFE 估计量含负权重，处理效应异质时可能符号颠倒", "政策内生择时：试点名单本身与结果相关"]
implementation_notes: "经典 2×2 用 reghdfe；交错 DID 用 csdid / eventstudyinteract / did_multiplegt 之一并报告 Goodman-Bacon 分解。模板见 tools/stata-templates/did_staggered.do"
date_updated: 2026-06-12
---

## Identification Problem

政策或事件冲击下，简单前后对比混入时间趋势，简单组间对比混入选择差异。DID 用"控制组的前后变化"剔除共同时间趋势，识别处理的因果效应。

## Strategy

**经典 2×2**（一次性政策、处理时点统一）：

`Y_it = β·(Treat_i × Post_t) + μ_i + λ_t + ε_it`

个体与时间固定效应吸收 Treat 与 Post 主项，β 即 ATT。

**多期交错（staggered）**：不同个体在不同年份接受处理（试点分批扩容是经管最常见形态）。此时直接跑 [[two-way-fixed-effects]] 的 `Treat×Post` 已被证明有问题——早处理组会被当成晚处理组的"控制组"，处理效应随时间变化时权重可为负。2025 年前后的审稿惯例是：TWFE 作基准 + 至少一种异质性稳健估计量。

## Key Assumptions

- 平行趋势（核心，不可直接检验）：用事件研究图（处理前各期系数不显著、无趋势）旁证。
- 无预期效应：宣布期与实施期分开检查；有预期就把事件时点前移。
- 控制组干净：控制组未受溢出影响（地理或产业链相邻个体要警惕）。

## Implementation

- 经典：`reghdfe y i.treat##i.post controls, absorb(stkcd year) vce(cluster stkcd)`。
- 交错（任选其一并交代理由）：
  - Callaway & Sant'Anna：`csdid y controls, ivar(stkcd) time(year) gvar(first_treat_year)`
  - Sun & Abraham：`eventstudyinteract`
  - de Chaisemartin & D'Haultfœuille：`did_multiplegt`
- 诊断必报：事件研究图（前 3–5 期 + 后若干期）、Goodman-Bacon 分解（`bacondecomp`，看负权重占比）。
- 模板：`tools/stata-templates/did_staggered.do`。

## Diagnostics

- 事件研究系数图：处理前系数联合不显著。
- 安慰剂：随机打乱处理时点 / 处理身份重复抽样，真实系数应落在安慰剂分布尾部。
- PSM-DID：处理组与控制组可比性差时先匹配再差分（见 [[propensity-score-matching]]）。

## Limitations

- 平行趋势是信念不是检验结果；前期平行不保证后期反事实平行。
- 政策择时内生（先试点的地区本来就在改善）是 DID 最常见的死穴，需要制度细节论证试点名单的准外生性。
- 长面板下处理效应动态化，单一 β 掩盖时变效应，事件研究图应作为主要呈现。
