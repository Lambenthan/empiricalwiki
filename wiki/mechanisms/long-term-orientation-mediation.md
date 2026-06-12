---
title: "企业长期导向中介机制（治理通道）"
slug: "long-term-orientation-mediation"
mechanism_type: governance
source_papers: [温磊-2024-耐心资本-新质生产力]
variables: [patient-capital, new-quality-productive-forces]
evidence:
  - source: "温磊-2024-耐心资本-新质生产力"
    strength: moderate
    detail: "PC → LTO 系数 0.361*** (t = 6.40)，LTO 用年报中长期导向关键词词数 / 年报总词数 × 100 度量。仅做第一段 PC → Mediator，依江艇 (2022) 因果中介识别策略推断治理通道。"
date_updated: 2026-05-07
---

## Mechanism Statement

耐心资本通过塑造企业长期导向，约束管理者短视行为、引导企业关注长期目标与战略，进而推动企业新质生产力等长周期、高投入战略目标的实现。

## Theoretical Logic

- 投资理念渗透：耐心资本不追求短期收益，看重企业长期发展潜力与价值创造，这种投资理念在参与企业经营管理过程中渗透到企业决策，使企业更加关注长期目标与战略。
- 治理监督：耐心资本作为资金提供者具有较强的监管动机和监管能力，能约束管理者短视行为，使管理者更加关注企业的长期发展。
- 行为传导：长期导向引导企业关注资源优化配置、品牌建设与维护、持续学习与改进、长期风险管理等与企业长期发展有关的事项，这些经营行为支撑创新能力、生产组织升级与新质生产力提升。

## Empirical Proxy

- 自变量：[[patient-capital]]。温磊 (2024) 采用 A1 框架（换手率 3 分组）股权侧测度。
- 中介：长期导向 LTO — 借鉴陈元等 (2024)，年报中长期导向关键词词数 / 年报总词数 × 100。需要构建长期导向关键词字典（如"长远""长期""可持续""战略性""持续投入""百年"等），对企业年报全文进行词频统计。
- 因变量：[[new-quality-productive-forces]] 等长周期战略目标变量。

## Evidence Across Papers

- 温磊 (2024)：PC → LTO 系数 0.361*** (t = 6.40)，控制 14 个公司层变量 + 行业 + 年份固定效应。仅做第一段，未估计 LTO → Y 与 PC + LTO → Y。

## Boundary Conditions

- 词频法依赖关键词字典，不同字典口径会显著影响 LTO 测度强度，跨论文不可直接比较。
- 年报"长期"语境多种多样，存在样板话术风险（监管要求披露中长期战略，企业可能批量复用模板化语言），导致 LTO 测度受披露文化影响而非真实战略导向。
- 相比 [[managerial-myopia-mediation]]（管理者短视主义文本分析），LTO 是正向构念（长期导向），与短视主义构成对立两极但不完全互补。
- 与 [[innovation-persistence-mediation]] 的差异：长期导向是治理 / 战略层面的态度变量，创新持续性是行为 / 投入层面的结果变量；前者更上游、后者更下游。

## Open Questions

- 是否需要 PC → LTO → Y 的逐步回归 + Sobel / Bootstrap 中介验证？江艇 (2022) 框架仅要求第一段，但中介强度量化需要全链条数据。
- LTO 词频与 [[managerial-myopia]] 词频的相关性如何？两者是否构成同一构念的两端？是否可在同一模型中同时纳入做交叉验证？
- 不同行业（高新技术 vs 传统制造）年报"长期"话语密度差异是否需要做行业去趋势化处理？

## Related

- 上游变量：[[patient-capital]]
- 下游变量：[[new-quality-productive-forces]]、[[exploratory-innovation]]、[[high-quality-development]]
- 配套机制：[[financing-constraint-mediation]]（资金通道） · [[innovation-persistence-mediation]]（行为通道） · [[managerial-myopia-mediation]]（短视主义对立面）
- 配套论文：[[温磊-2024-耐心资本-新质生产力]]
