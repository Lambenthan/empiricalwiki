---
title: "知识产权保护程度调节"
slug: "ipr-protection-moderation"
grouping_variable: "IPP (Intellectual Property Protection)"
grouping_rule: "参考肖振红等 (2025)：IPP_{i,t} = (省专利侵权立案数 / 省 GDP) / (全国专利侵权立案数 / 全国 GDP)。比值越大说明该省份专利侵权执法相对越积极、知识产权保护程度越高。专利侵权立案数据来自国家知识产权局，GDP 数据来自中国统计年鉴。"
rationale: "知识产权保护是法治建设的重要组成部分；保护越充分，创新成果产权边界越清晰，技术外溢风险越低，越能为耐心资本提供稳定预期与制度保障，进一步发挥其长期价值发现作用。"
source_papers: [贾勇-2025-耐心资本-创新韧性-倒u型]
date_updated: 2026-05-07
---

## Grouping Logic

未做样本切分，仅以连续指标 IPP 与 PC、PC² 构造交互项后纳入主回归。指标构造步骤：

1. 取省级专利侵权立案数（国家知识产权局）与省级 GDP（中国统计年鉴）。
2. 计算省份 i 在 t 年的"侵权强度"= LE_{it} / GDP_{it}。
3. 计算全国基准 LE_{ct} / GDP_{ct}。
4. IPP_{it} = 省份比值 / 全国基准。

## Theoretical Rationale

- 投资保护：完善的知识产权制度降低投资者面对的市场不确定性，增强长期投资信心。
- 创新激励：产权边界清晰防止模仿与窃取，激发企业创新研发投入。
- 资本-创新协同：良好的创新环境支撑耐心资本的战略目标，进一步发挥其作用。

## Sample Split

未做子样本切分，N = 27 611（与基准回归一致）。

## Model

$$Res_{i,t+1} = \alpha_0 + \alpha_1 PC + \alpha_2 PC^2 + \alpha_3 IPP + \alpha_4 IPP \times PC + \alpha_5 IPP \times PC^2 + \sum \alpha_j Controls + Industry + Year + \varepsilon$$

## Interpretation

贾勇 (2025) 表 7 列 (5)：

- IPP 系数 -0.047 (1% 显著)：在控制 PC 后，IPP 主项呈负相关（解读需谨慎，可能因 IPP 与其他制度变量共线）。
- IPP × PC = 0.140（不显著）；IPP × PC² = -0.381 (1% 显著)：知识产权保护程度强化了 PC² 的负向作用，使倒 U 型曲线下降段更陡。
- 解释：知识产权保护提升时，PC 的边际负效应（过度耐心资本带来的创新惰性）放大，但峰值高度提升不显著；总体上知识产权保护"加强"耐心资本的倒 U 型关系，与作者强化效应假设一致。

## Related

- 主论文：[[贾勇-2025-耐心资本-创新韧性-倒u型]]
- 核心解释变量：[[patient-capital]]
- 被解释变量：[[innovation-resilience]]
