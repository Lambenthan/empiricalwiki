---
title: "企业创新中介（联合申请专利数路径）"
slug: "innovation-mediation-joint-patents"
mechanism_type: innovation
source_papers: [杨芳-2025-耐心资本-制造业-新质生产力-营商环境]
variables: [patient-capital, stable-institutional-investors-turnover, relational-debt-total-long-debt-ratio, new-quality-productive-forces]
evidence:
  - source: "杨芳-2025-耐心资本-制造业-新质生产力-营商环境"
    type: tested_by
    strength: moderate
    detail: "稳定型股权 Wd → 企业创新 EI 系数 247.9703***（t = 2.7334），Sobel p = 0.0346；关系型债权 Pc → EI 系数 55.7405***（t = 3.3916），Sobel p = 0.0137。两路径中介均显著，假设 H3 通过。"
date_updated: 2026-05-07
---

## Mechanism Statement

耐心资本通过提高企业创新水平（以制造业企业当年联合申请专利总数衡量），进而提升制造业企业新质生产力。耐心资本以长期投资属性为创新活动提供长期稳定的资金保障，使创新成果在投入、产出和要素配置三方面共同支撑新质生产力的形成与发展。

## Theoretical Logic

杨芳 (2025) 将耐心资本通过企业创新影响新质生产力的链路拆为两条平行子机制：

- 稳定型股权 → 企业创新：稳定型机构投资者具备信息优势（深度参与创新过程、获取私有信息）、监督优势（长期契约 + 激励约束机制规避管理层短视）、战略优势（识别潜力创新项目并提供策略性指导）三重作用。
- 关系型债权 → 企业创新：关系型债权投资者通过资金支持（引入信誉良好的会计师事务所与信用评级机构作担保）、信息支持（长期合作下信息优势方向劣势方主动传递创新讯息）、机制支持（商业银行固定收益索取权对经理人私利产生"挤出"效应；银行风险对冲机制提高对创新风险的包容性）支撑创新。

企业创新到新质生产力的传导分三层：

- 创新投入：耐心资本加持下企业加大研发投入，研发符合时代发展趋势的前沿技术与新型产品，提高生产效率与质量。
- 创新产出：科学发明、专利与技术开发、市场化应用构成链式过程，是颠覆性、前沿性技术创新的源泉，与应用场景结合后推动新质生产力长足发展。
- 创新要素：创新活动意味着各类要素资源的高效组合与顺畅流动，推动全要素生产率提升，与新质生产力的核心标志一致。

## Empirical Proxy

- 自变量：[[patient-capital]] —— 操作化为两路平行：[[stable-institutional-investors-turnover]]（Wd）+ [[relational-debt-total-long-debt-ratio]]（Pc）。
- 中介变量 EI：制造业企业当年联合申请专利总数。
- 因变量：[[new-quality-productive-forces]]（Npro，熵权法合成）。

杨芳 (2025) 借鉴江艇 (2022) 机制检验思路：仅估计第一阶段 IV → M 系数，并报告 Sobel 检验 p 值，不再做第二阶段 IV + M → Y 联合估计。

## Evidence Across Papers

目前来自 [[杨芳-2025-耐心资本-制造业-新质生产力-营商环境]]（表 5 列 3-4）：

- 稳定型股权 Wd → EI：系数 247.9703***（t = 2.7334），Sobel p = 0.0346 < 0.05；样本 N = 10119，adj. R² = 0.0052。
- 关系型债权 Pc → EI：系数 55.7405***（t = 3.3916），Sobel p = 0.0137 < 0.05；样本 N = 10119，adj. R² = 0.0060。
- 控制变量、行业 FE、年份 FE 均纳入模型。

## Boundary Conditions

- 联合申请专利数的代理优势在于"联合申请"反映企业创新合作（相对于单独申请更能体现资源整合），但缺点是无法区分发明、实用新型、外观设计的质量差异。
- 与单纯专利数量（[[new-quality-productive-forces]] 中"科技劳动资料"的 Ln(授权专利+1)）口径不同：本中介使用"联合申请总数"绝对值（表 5 R² 极低 0.005-0.006，提示数据噪声大），而 Npro 子指标用 Ln 转换后的授权专利数。
- 适用于制造业子样本；对服务业、金融业的代理度未经检验。
- Sobel 检验对中介路径的统计推断敏感于样本量与系数估计精度，建议复现时同时使用 Bootstrap 自助法做稳健性。

## Open Questions

- 中介路径在耐心资本不同维度（股权侧 vs 债权侧）下的系数差异是否反映"机构投资者信息优势"与"银行监督优势"的相对强度？股权侧系数 247.97 vs 债权侧系数 55.74，差异显著。
- 本机制与 [[financing-constraint-mediation]] 的相对重要性如何区分？两者可能存在前后链路（融资约束缓解 → 研发资金充足 → 创新产出增加），需要联合中介模型识别。
- 联合申请专利与独立申请专利的差异是否在异质性子样本（东部 vs 中西部、内控强 vs 内控弱）中表现出不同模式？

## Related

- 自变量：[[patient-capital]] · [[stable-institutional-investors-turnover]] · [[relational-debt-total-long-debt-ratio]]
- 因变量：[[new-quality-productive-forces]]
- 互补机制：[[financing-constraint-mediation]]（杨芳 2025 同时检验的另一中介路径）
- 主用论文：[[杨芳-2025-耐心资本-制造业-新质生产力-营商环境]]
