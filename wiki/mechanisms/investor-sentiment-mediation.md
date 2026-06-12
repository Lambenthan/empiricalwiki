---
title: "投资者情绪中介机制"
slug: "investor-sentiment-mediation"
mechanism_type: information
source_papers: [唐亮-2025-耐心资本-esg表现]
variables: [patient-capital, esg-performance]
evidence:
  - source: "唐亮-2025-耐心资本-esg表现"
    type: supports
    strength: moderate
    detail: "PC → Sent 系数 0.221***（t = 3.985），耐心资本显著抬升企业层面非理性定价残差代表的投资者情绪指标，配合 PC 对 ESG 系数 0.030***，表征信号传递机制成立"
date_updated: 2026-05-07
---

## Mechanism Statement

耐心资本投入向资本市场传递企业未来经营前景良好的信号，吸引更多长期资金跟随进入，并稳定既有投资者的预期与情绪，进而约束管理层短期主义、推动企业在 ESG 维度的长期投入。

## Theoretical Logic

唐亮 (2025) 沿用 Goyal 与 Yamada (2004)、谭跃与夏芳 (2011) 的"托宾 Q 分解"思路：将托宾 Q 拆为内在价值（理性部分）与市场错误定价（投资者情绪驱动的非理性部分），残差作为投资者情绪的可观测代理。耐心资本作为长期、稳定的资金来源，通过两条路径影响投资者情绪：

- 信号机制：耐心资本注入向市场传递企业可持续发展信号，提升市场对未来现金流的乐观预期，正向推动情绪指标。
- 锚定机制：耐心资本投资者对短期波动不敏感，降低短期投机性交易频率，使股价噪声减少、情绪波动收窄。

下游：稳定且偏正的投资者情绪 → 公司可以在更宽松的资本市场约束下持续做长期投资 → 提高 ESG 表现。

## Empirical Proxy

- 自变量：[[patient-capital]]（A1 经典版：稳定型股权占比 + 关系型债权占比）。
- 中介：投资者情绪 (Sent)，构造步骤：
  1. 第一阶段回归：托宾 Q ~ ROE + Grow + Lev + Size + 行业 FE + 年份 FE。
  2. 取残差 ε。
  3. 标准化：Sent = (ε − ε̄) / σ_ε。
- 因变量：[[esg-performance]]。

## Evidence Across Papers

来自 [[唐亮-2025-耐心资本-esg表现]]（表 6 第 3 列）：

- PC → Sent 系数 0.221***（t = 3.985），R² = 0.554。
- 控制变量：ROE、Hindex、Age、Soe、Grow、MP；行业 + 年度 + 个体三向固定效应。

需要注意：作者在正文中表述为"稳定投资者情绪"，但回归系数显示耐心资本上升伴随情绪指标 Sent 上升，方向是把情绪从负向区间推向正向区间。在解读时应理解为"耐心资本提升市场对企业的情绪面评价"，而非简单"降低情绪波动"。

## Boundary Conditions

- Sent 测度依赖于"托宾 Q 定价无效部分 = 投资者情绪"的假设；若市场存在系统性错估或行业层面信息冲击，残差可能掺杂非情绪噪声。
- 投资者情绪与 ESG 之间存在反向因果：ESG 高的公司更受 ESG 主题基金追捧，本身就抬升估值偏离。本机制需配合 IV 处理（[[iv-firm-life-cycle-dickinson]]）。
- 在投资者类型异质（散户主导 vs 机构主导）的市场分段中，Sent 的可测度性差异较大；本文未做异质性切分。

## Open Questions

- Sent 中介的显著性是否经过 Sobel / Bootstrap 检验？原文采用逐步回归法，未提供正式中介显著性检验。
- 投资者情绪与代理成本（[[agency-cost-mediation]]）、非效率投资（[[inefficient-investment-mediation]]）三条机制之间是否存在交互或链式中介？
- 不同的情绪测度（CICSI、股吧文本、调查问卷）下，PC → Sent → ESG 路径的稳健性如何？
