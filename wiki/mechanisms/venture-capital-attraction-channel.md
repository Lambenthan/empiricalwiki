---
title: "风险投资吸引通道 (Venture Capital Attraction Channel)"
slug: "venture-capital-attraction-channel"
mechanism_type: financing
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
variables: [venture-capital, specialized-new-transformation, new-quality-productive-forces]
evidence:
  - source: 简冠群-2025-专精特新-新质生产力-风险投资-耐心资本
    type: supports
    strength: strong
    detail: "TRANS → VC 第一阶段 Treat 0.1734***、Degree 0.2829***；TRANS + VC → Npro 第二阶段 VC 0.1557*** 显著为正，TRANS 主项相比基准减小，部分中介模式成立"
date_updated: 2026-05-07
---

## Mechanism Statement

企业专精特新转型通过吸引风险投资进入，缓解创新研发的资金约束并引入治理与资源支持，从而促进企业新质生产力发展。该机制对"正在进行专精特新转型"（Degree 维度）的企业更为显著，对应风险投资偏好早期高成长、高潜力标的的特征。

## Theoretical Logic

理论基础整合科技金融与风险投资文献：

- 信号传递：专精特新认定与发展程度是中小企业创新能力与市场前景的可观察信号，降低 VC 与企业间的信息不对称。
- 投资偏好匹配：IVC 关注财务回报与高成长；CVC 关注战略服务能力。专精特新企业聚焦细分市场、提供特色化服务，符合两类 VC 的偏好。
- 增值服务：VC 介入后参与经营管理、利用资源网络与信息优势，提升创新韧性（梁婧姝、刘涛雄 2024），并引导企业研发国际化（李梦雅等 2021）。
- 产业升级：VC 通过推动技术从研发走向主导技术（钱燕、范从来 2021），加快附加值低 → 高的产业结构升级，进而支撑新质生产力。

## Empirical Proxy

- 中介变量：[[venture-capital]] (VC) — 风险投资持股比例，借鉴周冲、袁经发 (2023)。
- 处理变量：[[specialized-new-transformation]] (Treat / Degree)。
- 因变量：[[new-quality-productive-forces]] (Npro)。

两阶段中介检验：

- 第一阶段：VC = λ₀ + λ₁·TRANS + Controls + Market + FE + ε
- 第二阶段：Npro = α₀ + α₁·TRANS + α₂·VC + Controls + Market + FE + ε

## Evidence Across Papers

简冠群 (2025) 表 6 列 (1)、(4)：

- Treat → VC：系数 0.1734***（SE 0.0576）。
- Degree → VC：系数 0.2829***（SE 0.0164）。

Degree 系数明显大于 Treat（组间差异检验经验 p = 0.0000），表明处于转型过程中的企业更易吸引 VC，与"VC 偏好早期高潜力"的理论预期一致。

简冠群 (2025) 表 7 列 (1)、(4)：

- Treat + VC → Npro：Treat 0.0792*** + VC 0.1557***。
- Degree + VC → Npro：Degree 0.3069*** + VC 0.2163**。

加入 VC 后处理变量主项相比基准减小（Treat 0.1062 → 0.0792；Degree 0.3681 → 0.3069），符合部分中介模式。

后续耐心资本相关论文若涉及 VC 中介路径，将在本页累积证据。

## Boundary Conditions

- 转型阶段差异：风险投资吸引通道在"量变"阶段（Degree）作用强于"质变"阶段（Treat），与耐心资本通道（[[patient-capital-attraction-channel]]）形成镜像。
- 资金协同：与耐心资本结合后存在协同效应（VC×SD、VC×DE 交乘项显著为正），二者非完全替代关系。
- 行业差异：本论文样本为中小板、创业板、科创板与北交所，对沪深主板大型企业的外推性需谨慎。
- IVC vs CVC 区分：本论文未做区分，若进一步研究可能呈现差异化效应。

## Open Questions

- 该通道在不同行业（高科技 vs 传统制造）是否存在异质？
- VC 持股占比与持有期长短的交互效应？
- 政府引导基金作为"准 VC"是否走类似通道？
- VC 通过董事会席位等治理参与的细化测度是否能进一步分解机制？
