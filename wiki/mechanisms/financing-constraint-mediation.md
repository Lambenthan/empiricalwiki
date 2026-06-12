---
title: "融资约束中介机制（资本赋能）"
slug: "financing-constraint-mediation"
mechanism_type: financing
source_papers: [储佩佩-2025-耐心资本-企业韧性]
variables: [patient-capital, enterprise-resilience]
evidence:
  - source: "储佩佩-2025-耐心资本-企业韧性"
    strength: moderate
    detail: "Equity 对 WW 系数 -0.1180***、Debt 对 WW 系数 -0.2591***（PC 显著降低融资约束），第二步 Med→Y 未单独估计。"
date_updated: 2026-05-07
---

## Mechanism Statement

耐心资本通过缓解信息不对称、释放价值信号吸引接续投资，降低企业融资约束程度，进而为企业以充沛资金应对外部冲击、实现韧性塑造提供资金基础。

## Theoretical Logic

- 信号传递：耐心资本投资者通过基本面分析与长期承诺向外界释放企业可持续增长的"背书"，吸引其他外部投资者跟进。
- 资本接续：稳定型机构持股 + 关系型长期债务直接增加企业可获取资金规模，缓解资金存量短缺。
- 韧性传导：融资约束下降 → 企业有能力整合内部资源、调整结构、创造新增长路径 → 韧性提升。

## Empirical Proxy

- 自变量：[[patient-capital]]（A1 测算：稳定型股权 Equity + 关系型债务 Debt）。
- 中介：融资约束 WW 指数（鞠晓生等 2013）。WW = -0.091×CF -0.062×DIVPOS +0.021×TLTD -0.044×LNTA +0.102×ISG -0.035×SG。
- 因变量：[[enterprise-resilience]]。

## Evidence Across Papers

目前来自 [[储佩佩-2025-耐心资本-企业韧性]]：

- 表 9 列 (1)：Equity 对 WW 系数 -0.1180***（标准误 0.0206）。
- 表 9 列 (2)：Debt 对 WW 系数 -0.2591***（标准误 0.0417）。
- 第二步 Med → Resilience 与 Sobel/Bootstrap 显著性检验未提供。

## Boundary Conditions

- WW 指数对小型企业敏感度较高，对大型央企可能体现不足；样本剔除金融保险房地产后此问题部分缓解。
- 关系型债务侧的"长期借款 / (长期借款 + 应付债券 + 应付票据)"分母小时方差大，可能放大 Debt → WW 的边际系数。

## Open Questions

- 中介强度的可验证性：是否需补 Bootstrap、Sobel 或 Hayes PROCESS 给中介效应一个直接的显著性指标。
- WW 之外的融资约束代理（KZ、SA 指数）是否得到一致结论。
- 与"创新持续性中介"是否存在结构性序贯（先缓解融资 → 再支持创新 → 再形成韧性）。
