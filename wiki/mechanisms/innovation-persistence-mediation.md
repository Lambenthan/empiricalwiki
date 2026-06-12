---
title: "创新持续性中介机制（创新赋能）"
slug: "innovation-persistence-mediation"
mechanism_type: innovation
source_papers: [储佩佩-2025-耐心资本-企业韧性]
variables: [patient-capital, enterprise-resilience]
evidence:
  - source: "储佩佩-2025-耐心资本-企业韧性"
    strength: moderate
    detail: "Equity 对 Innov 系数 1.5981***、Debt 对 Innov 系数 2.1749***（PC 显著提升创新持续性），第二步 Med→Y 未单独估计。"
date_updated: 2026-05-07
---

## Mechanism Statement

耐心资本对创新失败具备较高风险容忍度，能够提供稳定资金供给、降低创新过程中实际生产力的波动，提升企业创新持续性，进而为企业培育韧性、应对危机提供动态能力支撑。

## Theoretical Logic

- 资源容忍：耐心资本鼓励探索、宽容失败，使企业能够以较长投资视域处理"长期能力建设 vs 短期业绩压力"。
- 投入平滑：稳定资本注入降低 R&D 投入的年度波动，避免在外部冲击时被迫削减创新支出。
- 韧性激活：持续创新沉淀关键技术 → 危机情境下企业可凭借技术储备激活韧性，将危机引发的市场洗牌转化为竞争优势。

## Empirical Proxy

- 自变量：[[patient-capital]]（A1 测算）。
- 中介：创新持续性 Innov（余芬和樊霞 2022）。公式：Innov_t = Ln[(IN_t + IN_{t-1}) / (IN_{t-1} + IN_{t-2})] × (IN_t + IN_{t-1})，IN 为研发投入。
- 因变量：[[enterprise-resilience]]。

## Evidence Across Papers

目前来自 [[储佩佩-2025-耐心资本-企业韧性]]：

- 表 9 列 (3)：Equity 对 Innov 系数 1.5981***（标准误 0.4498）。
- 表 9 列 (4)：Debt 对 Innov 系数 2.1749***（标准误 0.7136）。
- N = 13413（小于全样本 16874，研发投入数据缺失导致样本损失）。

## Boundary Conditions

- 公式包含 Ln 与乘法两段，Innov 的尺度与 R&D 投入水平正相关，对小型企业方差大。
- 需要 t-2、t-1、t 三期 R&D 数据，IPO 早期与并购重组样本可能缺失。

## Open Questions

- 创新持续性是否在 PC 高水平时出现"创新过度持续"的过度专注效应（即是否存在非线性中介）。
- 与双元创新（探索式 vs 利用式）框架的兼容性：本机制度量的是 R&D 投入的年间平滑，未区分探索 vs 利用。
- 与代飞 (2025) 报告的"PC → 双元创新"路径如何与本机制衔接。
