---
title: "管理者耐心程度调节（管理者短视取负值）"
slug: "managerial-patience-moderation"
grouping_variable: "managerial_patience (MP)"
grouping_rule: "MP = -1 × 管理者短视；管理者短视参考虞义华 (2018)，采用短期投资 / 期初总资产度量。MP 越大表示管理者越耐心。以交互项形式纳入主回归，并未做样本切分。"
rationale: "高阶理论 (Hambrick & Mason, 1984)：管理者特质渗透决策过程；耐心管理者更注重未来创新发展，与耐心资本的长期投资理念形成耦合，增强企业创新战略一致性，进而强化耐心资本的倒 U 型效应。"
source_papers: [贾勇-2025-耐心资本-创新韧性-倒u型]
date_updated: 2026-05-07
---

## Grouping Logic

文中未做样本切分，以连续调节变量 MP 与 PC、PC² 构造交互项。MP 的连续度量方式：

1. 取虞义华 (2018) 的管理者短视指标：短期投资 / 期初总资产；
2. 取负数得 MP（管理者短视取负 = 管理者耐心程度）；
3. MP 与 PC、PC² 分别相乘形成交互项 MP×PC、MP×PC²。

## Theoretical Rationale

- 时间视域：耐心管理者将注意力投向未来创新发展，决策视域宽广。
- 风险偏好：缺乏耐心的管理者偏好"短平快"低风险项目，与耐心资本长期激励相冲突。
- 战略一致性：耐心管理者与耐心资本投资者形成长期价值导向耦合，提升创新战略稳定性。

## Sample Split

未做子样本切分，仅以交互项检验调节效应；样本量 N = 7 893（受短期投资数据可得性限制）。

## Model

$$Res_{i,t+1} = \alpha_0 + \alpha_1 PC_{i,t} + \alpha_2 PC_{i,t}^2 + \alpha_3 MP_{i,t} + \alpha_4 MP_{i,t} \times PC_{i,t} + \alpha_5 MP_{i,t} \times PC_{i,t}^2 + \sum \alpha_j Controls + Industry + Year + \varepsilon$$

## Interpretation

贾勇 (2025) 表 7 列 (1)：

- MP 系数 1.318（1% 显著）：管理者越耐心，创新韧性越强。
- MP × PC = 10.437（5% 显著），MP × PC² = -20.606（5% 显著）。
- 解释：管理者耐心程度强化了 PC 与 Res 的倒 U 型关系——上升段更陡、下降段更陡。

## Related

- 主论文：[[贾勇-2025-耐心资本-创新韧性-倒u型]]
- 相关变量：[[managerial-myopia]]（管理者短视，本文取负数得到 MP）
- 相关机制：[[managerial-myopia-mediation]]
- 核心解释变量：[[patient-capital]]
