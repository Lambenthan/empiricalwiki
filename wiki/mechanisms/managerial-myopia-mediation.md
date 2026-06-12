---
title: "管理者短视中介机制"
slug: "managerial-myopia-mediation"
mechanism_type: governance
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视, stein-1988-takeover-threats-managerial-myopia, edmans-2009-blockholder-trading-managerial-myopia]
variables: [patient-capital, managerial-myopia, exploratory-innovation, exploitative-innovation]
evidence: [{source: "代飞-2025-耐心资本-双元创新-管理者短视", strength: moderate, detail: "PC → myopia 系数 -0.002 (p<0.01)，myopia → explore 系数 -0.602 (p<0.05)，部分中介；myopia → exploit 倒 U 型 (myopia 系数 7.349***、myopia² 系数 -0.328***)"}]
date_updated: 2026-05-07
---

## Mechanism Statement

耐心资本通过缓解管理者短视主义重塑企业资源配置决策：长期资本属性扩展管理者决策时间跨度，将注意力从短期财务指标重新分配到长期战略，进而影响双元创新的资源配置。

## Theoretical Logic

**理论源头（理论侧）**：本机制有两条互补的形式化微观基础。

- [[stein-1988-takeover-threats-managerial-myopia]]（收购威胁通道）：信息不对称下，长期投资压低当期盈利 → 股价被低估 → 敌意收购风险上升 → 经理为保住控制权理性地选择短视。该模型进一步证明 [[stein-cs-patient-stockholders-reduce-myopia]]：股东越"耐心"（不因低当期盈利抛售），经理短视动机越弱——"耐心资本缓解管理者短视"的理论祖先。
- [[edmans-2009-blockholder-trading-managerial-myopia]]（退出/交易通道）：大股东知情交易（坏消息卖出、好消息持有）把信息注入价格、提升市场效率，s_b 时股价跌幅收窄，经理因此敢做长期投资（[[edmans-prop2-investment]]）。治理经由 exit 而非 voice，详见独立机制页 [[governance-through-trading-exit]]。两条通道共同支撑"长期/耐心资本 → 缓解短视"。

下面的实证三条传导路径是这一理论机制在中国 A 股的具体检验。

三条传导路径：

- 资源承诺机制：长期股权 + 银行长债的低流动性属性缓解管理者生存焦虑与短期业绩压力。
- 治理干预机制：耐心资本投资者深度参与治理、持续监督，纠正决策的短视倾向。
- 信号传递机制：耐心资本注入向利益相关者传递长期导向，提高对创新失败的容忍度。

## Empirical Proxy

- 自变量：[[patient-capital]]（A2 测算）。
- 中介：[[managerial-myopia]]（胡楠 2021 文本指标 ×100）。
- 因变量：[[exploratory-innovation]]、[[exploitative-innovation]]。

## Evidence Across Papers

目前仅来自 [[代飞-2025-耐心资本-双元创新-管理者短视]]。该文采用逐步回归法：

- (1) myopia 对 PC：β₁ = -0.002***（PC 缓解短视）。
- (3) explore 对 PC + myopia：γ₂ = -0.602**（短视抑制探索式）。
- (5) exploit 对 PC + PC² + myopia + myopia²：myopia² 系数 -0.328***，呈倒 U 型，拐点 8.15。

→ 部分中介效应成立，但作者未做 Sobel / Bootstrap 直接显著性检验。

## Boundary Conditions

- 中介关系成立的样本范围：PC 拐点 167.77，myopia 拐点 8.15。当前样本均值（PC=21.98, myopia=4.16）均位于拐点左侧，意味着观察到的中介效应主要落在"促进探索式 + 抑制利用式"的不对称区间。
- 拐点之后双元创新协同共生的中介结构尚未在数据内充分识别。

## Open Questions

- 中介显著性的稳健形式（Sobel / Bootstrap / Hayes PROCESS）尚未提供。
- 是否存在调节中介？例如 EPU、行业短期主义压力、CEO 任期等。
- 短视测度的反向因果（创新本身可能影响 MD&A 措辞）需用滞后或工具变量缓解。
