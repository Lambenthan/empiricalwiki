---
title: "处理效应模型（Heckman 两阶段自选择修正）"
slug: "heckman-treatment-effects"
strategy_type: heckman
source_papers: [李心武-2025-耐心资本-数字化转型-价值发现]
assumptions:
  - "排他性变量（exclusion restriction）：同年度同城市除自身外的数字化转型企业数量影响该企业是否进行数字化转型，但不直接影响基金持仓比例"
  - "第一阶段误差与第二阶段误差服从联合正态分布"
  - "选择方程（Probit）参数化函数形式正确"
threats:
  - "若排他性变量不严格外生，IMR 估计将存在偏误"
  - "正态性假设若被违反，IMR 系数解释会失真"
  - "排他性变量在面板数据中可能内生于时间趋势"
implementation_notes: "第一阶段 Probit 估计企业进行数字化转型的概率；第二阶段在原方程中加入 IMR；Stata 用 heckman 或 movestay 命令"
date_updated: 2026-05-07
---

## Identification Problem

李心武 (2025) 检验耐心资本对企业数字化转型的认同效应（H2）时存在自选择偏差：进行数字化转型的企业并非随机抽样，可能在治理结构、行业特征等不可观测维度上与未转型企业系统性不同，导致基金持仓比例的差异被错误归因于数字化转型本身。

## Strategy

采用 Heckman 两阶段处理效应模型修正自选择：

- **第一阶段（Probit）**：把企业是否数字化转型的虚拟变量 IfDigital（依据 Digital 是否为 0 构造）作为被解释变量，把同年度同城市除自身外进行数字化转型的企业数量 Exclusion 作为排他性变量纳入第一阶段，估计每个观测点的逆米尔斯比率（IMR）。
- **第二阶段**：在原回归方程基础上加入 IMR，重新估计 Digital 对 Proportion 的系数。

## Key Assumptions

- **排他性**：Exclusion 影响 IfDigital 但不直接进入第二阶段方程。同城市同年度其他企业转型数量反映本地数字化氛围，与基金对单一企业的持仓决策的直接关系较弱。
- **联合正态**：两阶段的误差项服从联合正态分布。
- **函数形式**：Probit 假设的累积分布函数正确反映了选择行为。

## Implementation

李心武 (2025) 报告：

- 第一阶段：Exclusion 与 IfDigital 显著相关，验证排他性变量有效性。
- 第二阶段：IMR 系数显著为负，说明确实存在自选择偏差；Digital 系数显著为正，主结论稳健。

## Diagnostics

- IMR 系数的显著性：若显著则确认存在自选择偏差。
- 排他性变量 Exclusion 在第一阶段的系数显著性。
- 残差正态性检验。

## Limitations

- 排他性假设难以严格检验，文献中存在争议。
- 与 IV 法相比，Heckman 对正态性假设更敏感。
- 该方法主要修正样本选择，未直接解决遗漏变量与双向因果，需与 IV、固定效应等方法结合使用。

## Related

- identification：[[iv-fiber-cable-government-report]] · [[instrumental-variable-2sls]] · [[firm-fixed-effects]]
- papers：[[李心武-2025-耐心资本-数字化转型-价值发现]]
