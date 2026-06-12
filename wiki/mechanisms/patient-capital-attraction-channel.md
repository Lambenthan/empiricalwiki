---
title: "耐心资本吸引通道 (Patient Capital Attraction Channel)"
slug: "patient-capital-attraction-channel"
mechanism_type: financing
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
variables: [patient-capital, specialized-new-transformation, new-quality-productive-forces]
evidence:
  - source: 简冠群-2025-专精特新-新质生产力-风险投资-耐心资本
    type: supports
    strength: strong
    detail: "TRANS → SD/DE 第一阶段 Treat 2.1224**/0.1851***、Degree 0.2358***/0.1352***；TRANS + SD/DE → Npro 第二阶段 SD 0.0098***、DE 0.2971*** 均显著为正"
date_updated: 2026-05-07
---

## Mechanism Statement

企业专精特新转型通过吸引耐心资本（含债权型关系型债权 DE 与股权型稳定型股权 SD），获取长期、稳定的资金与治理支持，缓解风险投资短期注入的不确定性，从而支撑新质生产力的长周期发展。该通道对"已完成专精特新转型"（Treat 维度）的企业更为显著，与耐心资本偏好成熟稳定标的的特征一致。

## Theoretical Logic

耐心资本以长期视角分配资金，可分两类：

- 债权型耐心资本（关系型债权 DE）：以银行等金融机构为主体的长期负债。专精特新企业稳定的市场地位与产业链关键位置使其更易获得银行长期合作；银行不仅提供资金，还提供后续创新配套资金（王满四、王旭东 2020），形成"资金效应 + 配套效应"。
- 股权型耐心资本（稳定型股权 SD）：以机构投资者长期持股为主体。机构投资者通过价值投资理念、复杂社会网络获取的资源、参与企业决策发挥监督与治理作用（谭红阳等 2024），促使管理层增加创新投资（梁上坤 2018）；机构投资者退出威胁还能激发绿色创新动力（李强等 2024）。
- 间接通道：耐心资本可向 VC 机构注资，间接向企业注入长期资本。

## Empirical Proxy

简冠群 (2025) A3 操作化（标准差变体 + 非流动负债明细）—— 不对 SD 与 DE 求和合成单一 PC 指标，而是作为两条平行机制变量。

- 稳定型股权 SD = 企业 i 在 t 年投资者持股比例 / 其过去 3 年持股比例标准差。
- 关系型债权 DE = (长期借款 + 应付债券 + 长期应付款 + 其他非流动负债) / 负债总额。

中介检验：

- 第一阶段：SD / DE = λ₀ + λ₁·TRANS + Controls + Market + FE + ε
- 第二阶段：Npro = α₀ + α₁·TRANS + α₂·SD（或 α₃·DE）+ Controls + Market + FE + ε

## Evidence Across Papers

简冠群 (2025) 表 6 列 (2)(3)(5)(6)：

- Treat → SD：2.1224**（SE 0.9113）。
- Treat → DE：0.1851***（SE 0.0626）。
- Degree → SD：0.2358***（SE 0.0783）。
- Degree → DE：0.1352***（SE 0.0336）。

Treat 系数大于 Degree（组间差异 p = 0.0000 / 0.0020），表明已完成转型的企业更易吸引耐心资本，与"耐心资本偏好成熟稳定标的"预期一致。

简冠群 (2025) 表 7 列 (2)(3)(5)(6)：

- Treat + SD → Npro：Treat 0.0854*** + SD 0.0098***。
- Treat + DE → Npro：Treat 0.0512*** + DE 0.2971***。
- Degree + SD → Npro：Degree 0.2552*** + SD 0.4788***。
- Degree + DE → Npro：Degree 0.2779*** + DE 0.6672***。

加入耐心资本中介后 TRANS 主项相比基准减小，符合部分中介模式。

资金协同（表 8）：VC×SD、VC×DE 交乘项显著为正，证明短期 VC 与长期 PC 协同促进新质生产力发展，分散投资风险并平衡短长期收益预期。

## Boundary Conditions

- 转型阶段差异：耐心资本吸引通道在"质变"阶段（Treat）作用强于"量变"阶段（Degree），与风险投资通道（[[venture-capital-attraction-channel]]）形成镜像。
- 测度路径敏感：A2（代飞 2025，关系型债务 = 银行长期贷款 / 银行长贷+应付债券+应付票据）与 A3（本文，关系型债权 = 全部非流动负债明细 / 负债总额）口径差异显著，结论可能因 PC 操作化路径不同而偏移。
- 行业范围：仅适用于中小板、创业板、科创板与北交所中小企业，不能直接推广。
- 与企业生命周期、产权性质的交互：本论文未做相关分析。

## Open Questions

- A2 vs A3 vs B1（持股时长法）vs B2（持股稳定性中位数法）等多种 PC 操作化路径在专精特新研究框架下，哪种最契合？
- 银行长期贷款（A2 路径）与"全部长期负债"（A3 路径）对中小企业的支持效果是否一致？
- 政府引导基金类耐心资本是否走类似通道？
- 耐心资本撤资 / 退出威胁（exit threat）对绿色创新的激发效应在本框架下能否复用？
