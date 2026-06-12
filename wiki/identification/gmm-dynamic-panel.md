---
title: "动态面板 GMM (Dynamic Panel GMM)"
slug: "gmm-dynamic-panel"
strategy_type: system_gmm
source_papers: [何文彬-2025-耐心资本-产能利用率]
assumptions:
  - "被解释变量自身存在动态调整路径，可用其滞后项作为工具变量。"
  - "解释变量与误差项当期相关，但与滞后期误差不相关（弱外生）。"
  - "差分后扰动项无序列相关（AR(2) 检验通过）。"
  - "工具变量整体过度识别有效（Sargan / Hansen 检验通过）。"
threats:
  - "L1.Y 的工具有效性依赖 AR(1) 但不存在 AR(2) 的假设；样本短时容易失败。"
  - "弱工具问题：当被解释变量持久性极高时，差分 GMM 的滞后水平工具弱。"
  - "工具数量过多（instrument proliferation）会过度拟合并削弱 Hansen J 的统计功效。"
implementation_notes: "何文彬 (2025) 采用 GMM 引入 L1.CU 处理产能利用率自相关与潜在双向因果；估计后 L1.CU 系数显著为负（-0.149、-0.209），呈现均值回归特征；PC_Sd、PC_Rl 系数符号与基准一致。"
date_updated: 2026-05-07
---

## Identification Problem

耐心资本与产能利用率之间存在三重内生性威胁：

- 反向因果：CU 高的企业更易吸引长期投资者，PC 反过来被 CU 决定。
- 遗漏变量：管理者偏好、行业景气度等同时影响 PC 与 CU。
- 测量误差：CU 的 SFA 估计本身含噪声，与 PC 测量误差叠加产生偏误。

## Strategy

引入被解释变量的滞后项 L1.CU 作为内生工具，以差分 GMM 或系统 GMM（Arellano-Bond / Blundell-Bond）估计。核心方程：

$$CU_{i,t} = \rho \cdot CU_{i,t-1} + \beta \cdot PC_{i,t} + \gamma \cdot \mathrm{Controls}_{i,t} + \alpha_i + \varepsilon_{i,t}$$

差分 GMM 用 t-2 及更早的水平 CU 作为工具；系统 GMM 同时用一阶差分和水平方程，能解决持久性高时的弱工具问题。

## Key Assumptions

- 误差项无序列相关（差分后允许 AR(1)，但禁止 AR(2)）。
- 工具变量整体外生（Sargan / Hansen 过度识别检验不拒绝）。
- 解释变量为预定（弱外生）：当期 PC 可能与当期 ε 相关，但与滞后 ε 不相关。
- 个体效应 α_i 为时不变，差分后被消除。

## Implementation

Stata：

```stata
xtset stkcd year

* 差分 GMM (Arellano-Bond)
xtabond CU PC_Sd controls, lags(1) noconstant vce(robust)

* 系统 GMM (Blundell-Bond) — 推荐
xtdpdsys CU PC_Sd controls, lags(1) twostep vce(robust)
* 或使用 xtabond2 (ssc install xtabond2)
xtabond2 CU L.CU PC_Sd controls i.year, ///
    gmm(L.CU PC_Sd, lag(2 4)) iv(controls i.year) ///
    twostep robust small
```

何文彬 (2025) 表 5 报告样本量 32660 / 33260，L1.CU 系数 -0.149*** / -0.209***，PC_Sd = 0.0469***，PC_Rl = 0.0105***；论文未报告 AR(1)、AR(2) 与 Hansen 检验值，复现时需补齐。

## Diagnostics

必查清单：

- AR(1) p < 0.05、AR(2) p > 0.10。
- Hansen J p > 0.10（或 Sargan p > 0.10，但 Hansen 更稳健）。
- 工具数量 < 截面单元数（否则需用 collapse 或 lag(2 4)）。
- 滞后阶数选择：通常 lag(2) 或 lag(2 4)；过长会引入过多工具。
- 系数 ρ ∈ (0, 1) 表示稳定动态。

何文彬 (2025) 表 5 中 L1.CU 系数为负（-0.149、-0.209），与 ρ 应在 (0, 1) 的常规预期不符；作者解释为"均值回归"现象（CU 高的企业下期主动减产）。复现时需关注 SFA-CU 是否平稳。

## Limitations

- L1.CU 作为唯一识别工具仍是弱外生假设；若存在与 ε_t 同期相关的省略变量未被滞后吸收，估计仍有偏。
- GMM 对小样本敏感，本文样本期 16 年但部分子样本观测数偏少。
- 系数解释不再是"长期均衡效应"而是"短期调整效应"，与基准 OLS / 高维 FE 估计不可直接比较。
- 论文未做 AR(2) 与 Hansen 检验汇报，外部读者难以判断工具有效性，复现时建议补全诊断。
