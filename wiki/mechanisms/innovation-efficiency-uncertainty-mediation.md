---
title: "创新效率与不确定性感知双中介"
slug: "innovation-efficiency-uncertainty-mediation"
mechanism_type: innovation
source_papers: [邱蓉-2024-耐心资本-全要素生产率]
variables: [patient-capital, innovation-efficiency, uncertainty-perception, total-factor-productivity]
evidence:
  - "邱蓉等 (2024) 表 7：Pat → Ineff = 0.159***，Ineff → TFP = 0.609***，Pat → Uncer = -0.144***，Uncer → TFP = -0.231***，Bootstrap 1000 次 95% CI 不含 0，Sobel 22.46***、5.55***。"
date_updated: 2026-05-07
---

## Mechanism Statement

耐心资本通过两条并行渠道提升企业全要素生产率：(1) 提高创新效率渠道，把长期、稳定的资金转化为更高的专利产出与研发产出比；(2) 抑制不确定性感知渠道，让管理层在外部宏观、市场、技术不确定性下仍维持长期投资决策。

## Theoretical Logic

- **创新效率渠道**：耐心资本的长期、低周转特征缓冲了短期财务压力，使企业可以容忍创新失败、坚持长周期高风险研发。表现为单位研发投入产出更多专利。在邱蓉等 (2024) 的模型 A = exp(γI − δU) 中，I 越大，A 越大，TFP 越高。
- **不确定性感知渠道**：耐心资本的持续资本投入向管理层与利益相关者传递长期承诺信号，对冲外部不确定性带来的"推迟投资"反应。在模型中表现为 U 下降，A 上升。

两条渠道在数学上加性独立，但在公司治理层面存在互补：稳定资金本身就降低了管理层对外部冲击的过度反应。

## Empirical Proxy

- 创新效率：[[innovation-efficiency]] (Ineff) — ln(发明 + 实用新型 + 外观设计 + 1) / 研发投入。
- 不确定性感知：[[uncertainty-perception]] (Uncer) — 年报 MD&A 不确定性词频 / MD&A 总词频。
- 上游：[[patient-capital]]（C 框架熵值法综合得分）。
- 下游：[[total-factor-productivity]]（LP 法估计）。

## Evidence Across Papers

邱蓉等 (2024) 表 7：

- 列 (1)：Pat → Ineff，系数 0.159***（t = 7.92）。
- 列 (2)：Ineff → TFP，系数 0.609***（t = 6.76）。
- 列 (3)：Pat + Ineff → TFP，Pat 1.218***、Ineff 0.589***，Pat 系数较列 4 基准 1.827 显著下降，部分中介。
- 列 (4)：Pat → Uncer，系数 -0.144***（t = -3.99）。
- 列 (5)：Uncer → TFP，系数 -0.231***。
- 列 (6)：Pat + Uncer → TFP，Pat 1.796***、Uncer -0.221***。
- Bootstrap 1000 次：Ineff 路径 95% CI [1.73386, 2.09952]，Uncer 路径 [0.08903, 0.20104]，均不含 0。
- Sobel：Ineff 路径 22.46***，Uncer 路径 5.55***。

## Boundary Conditions

- 创新效率渠道在颠覆式（AI）创新主导的企业更显著（Pat × AI_In = 1.172**），在传统创新主导的企业反向（Pat × Tr_In = -0.429***）。
- 在外部风险承担水平 Risk 较高时，Pat → Uncer 渠道被削弱（表 11 列 4：用拟合 Pat 对 Uncer 系数为 -0.104，不显著），创新效率渠道虽仍正向但系数下降。
- 国有企业的双中介更显著；金融化较低行业的双中介更显著。

## Open Questions

- 双渠道是否在不同行业（高科技 vs 传统制造）存在权重差异？
- Uncer 是企业理性认知还是管理层有意披露策略？文本测度无法识别。
- 是否存在第三条渠道（如管理者短视）？这正是 [[managerial-myopia-mediation]] 路线的研究内容；本机制与之并非互斥。
