---
title: "工具变量 IV / 2SLS（通用设计）"
slug: "instrumental-variables"
strategy_type: iv
source_papers: []
assumptions: ["相关性：IV 与内生变量第一阶段强相关", "排他性：IV 只通过内生变量影响结果，无其他通道", "独立性：IV 与误差项（不可观测混杂）不相关"]
threats: ["弱工具：第一阶段 F 不足时 2SLS 偏向 OLS 且推断失真", "排他性不可检验，叙事不硬时审稿人一票否决", "行业/地区均值类 IV 受同群溢出与共同冲击威胁"]
implementation_notes: "ivreghdfe / ivreg2，必报第一阶段系数、KP rk Wald F、过度识别 Hansen J。模板见 tools/stata-templates/iv_2sls.do"
date_updated: 2026-06-12
---

## Identification Problem

解释变量与误差项相关（双向因果、遗漏变量、测量误差）时 OLS 不一致。IV 用一个"只推动 X、不直接碰 Y"的外生变量切出 X 的外生变异。

## Strategy

第一阶段：`X = π·Z + γ·Controls + FE + v`；第二阶段：`Y = β·X̂ + γ·Controls + FE + ε`。β 解释为 LATE——被工具推动的那部分个体的因果效应，写结论时不要悄悄外推成 ATE。

经管文献的常见 IV 套路与各自命门：

- **行业 / 地区均值（leave-one-out）**：同行业其他企业的 X 均值。命门是行业共同冲击与同群效应直接进 Y。
- **滞后项**：X 滞后一到两期。命门是序列相关的不可观测冲击；审稿人接受度持续走低。
- **地理 / 历史变量**：距离、地形、历史制度。命门是"历史影响现在的通道太多"，排他性叙事要做足。
- **政策冲击 Bartik / shift-share**：份额 × 总量增长。命门是初始份额本身内生。

## Key Assumptions

- 相关性可检验：第一阶段 t 值、Kleibergen-Paap rk Wald F（约定俗成对照 Stock-Yogo 临界值或 F > 10 的粗规则；弱时改报 AR 置信区间）。
- 排他性**不可检验**，只能靠制度细节论证 + 安慰剂旁证。这是 IV 设计的全部难点。
- 多 IV 时过度识别检验（Hansen J）不拒绝——注意它检验的是"IV 彼此一致"，不是"IV 有效"。

## Implementation

- `ivreghdfe y controls (x = z1 z2), absorb(stkcd year) cluster(stkcd)`。
- 必报三件套：第一阶段完整结果、KP F、Hansen J（多 IV 时）；2SLS 与 OLS 系数并排呈现并解释差异方向。
- 模板：`tools/stata-templates/iv_2sls.do`。

## Diagnostics

- 弱工具：KP rk Wald F；弱时用 Anderson-Rubin 检验做对弱工具稳健的推断。
- 排他性旁证：把 Z 直接放进 Y 方程的 reduced form 子样本检验、安慰剂结果变量。
- 内生性本身：Durbin-Wu-Hausman 检验 OLS 与 IV 是否系统性偏离。

## Limitations

- LATE 不等于 ATE：政策含义部分只对 complier 成立。
- 第一阶段很强、排他性叙事很弱的 IV 比没有 IV 更危险——给了错误结论一个"已处理内生性"的外衣。
- 与 [[difference-in-differences]]、[[heckman-treatment-effects]] 等互补使用时，明确各自针对哪一种内生性来源，不要堆砌。
- 模糊断点（[[regression-discontinuity]] 的 fuzzy 形态）本质是"越线"作 IV 的特例，弱第一阶段的诊断逻辑与本卡相同。
