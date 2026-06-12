---
title: "双向固定效应 TWFE（基准面板设定）"
slug: "two-way-fixed-effects"
strategy_type: fixed_effects
source_papers: []
assumptions: ["不可观测混杂可分解为个体时不变部分与共同时间冲击", "解释变量在个体内有足够时序变异", "严格外生：误差与各期解释变量不相关"]
threats: ["时变遗漏变量（个体 × 时间交互的混杂）完全不设防", "动态效应（滞后被解释变量）下 FE 估计有 Nickell 偏误", "测量误差在组内变换后被放大"]
implementation_notes: "reghdfe y x controls, absorb(stkcd year) vce(cluster stkcd)；行业×年度高维 FE 用 absorb(stkcd ind#year)。模板见 tools/stata-templates/twfe.do"
date_updated: 2026-06-12
---

## Identification Problem

公司面板的默认威胁：时不变的公司特质（文化、创始人风格）与宏观共同冲击（年度景气）同时影响 X 与 Y。TWFE 用组内变换把这两层吸掉，是经管实证的基准设定——它本身不是完整的识别策略，而是后续一切设计的地板。

## Strategy

`Y_it = β·X_it + γ·Controls_it + μ_i + λ_t + ε_it`

μ_i 吸收个体时不变异质性，λ_t 吸收共同时间冲击。β 由**个体内、相对年度均值**的变异识别。

常用增强：行业 × 年度 FE（吸收行业级时变冲击，识别变异收窄到"同年同行业内"）、省份 × 年度 FE。每加一层交互 FE，都要自问剩余变异还剩多少、来自谁。

## Key Assumptions

- 时变混杂不存在或已被控制——这正是 TWFE 不能回答因果的原因，需要 [[difference-in-differences]]、[[instrumental-variables]] 等接力。
- X 在个体内有足够变异：组内标准差太小则系数被吸收，先 `xtsum` 看 within 变异。
- 聚类标准误：面板序列相关下必须按个体聚类（约定 cluster 在处理 / 政策变异的层级）。

## Implementation

- `reghdfe y x controls, absorb(stkcd year) vce(cluster stkcd)`。
- 行业 × 年度：`absorb(stkcd ind#year)`；注意被交互 FE 吸收的变量不能再放主项。
- 报告时写明 FE 结构、聚类层级、单元数与组内 R²。
- 模板：`tools/stata-templates/twfe.do`。

## Diagnostics

- FE 逐层加入的系数轨迹表（pooled → 年度 FE → +个体 FE → +行业×年度 FE）：系数大幅漂移说明遗漏变量敏感。
- Oster (2019) δ 界：用可观测选择推断不可观测选择的威胁程度。
- 动态面板嫌疑（Y 自相关高、T 短）转 [[gmm-dynamic-panel]]。

## Limitations

- 对时变混杂零防御；审稿人问"内生性怎么处理"时 TWFE 不构成回答。
- 交错处理情形下 TWFE 的 DID 系数有负权重问题，见 [[difference-in-differences]]。
- 高维 FE 吃掉大量变异后，剩余识别变异可能主要是噪声与测量误差。
