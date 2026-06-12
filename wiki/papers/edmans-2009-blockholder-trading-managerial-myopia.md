---
title: "Blockholder Trading, Market Efficiency, and Managerial Myopia"
slug: "edmans-2009-blockholder-trading-managerial-myopia"
arxiv: ""
venue: "Journal of Finance 64(6): 2481-2513"
year: 2009
tags: [theory, managerial-myopia, blockholder, governance-through-exit, market-microstructure, kyle-model, corporate-governance, patient-capital]
importance: 5
paper_kind: theory
date_added: 2026-06-03
source_type: pdf
s2_id: ""
keywords: [blockholder, informed trading, Wall Street Rule, exit, managerial myopia, market efficiency, liquidity, short-sales constraint]
domain: "公司金融理论 / 市场微观结构"
code_url: ""
cited_by: []
theory:
  model_class: "三期理性预期市场微观结构博弈（Kyle 1985 式，含知情大股东与实体投资决策）"
  solution_concept: "竞争性做市商理性预期均衡（Nash）；私有最优持股 α_P* 对再交易稳健"
  key_propositions: [edmans-lemma1-market-maker-pricing, edmans-lemma2-finite-optimal-block, edmans-prop1-market-efficiency, edmans-lemma3-investment-level, edmans-prop2-investment, edmans-prop3-liquidity-exogenous-block, edmans-prop4-liquidity-endogenous-block]
  predictions: [pc-attenuates-managerial-myopia, block-size-concave-price-efficiency, liquidity-promotes-long-term-investment]
---

## 研究问题

无法干预企业经营（没有控制权）的外部大股东，能否仅通过"用脚投票"式的知情交易给企业创造价值？这种"退出/交易"型治理能否构成管理者短视的一个解？与传统观点相反——美国流动的市场和频繁换手的股东究竟加剧还是抑制了短视？大股东持股规模对价格效率、实体投资和企业价值的影响是单调的吗？

## 模型环境

三期（t=1, 2, 3）理性预期市场微观结构博弈，叠加 t=0 的经理投资决策。一家企业有 1 单位流通股：大股东 B 持有 α，分散的小股东持有 1−α。所有参与人风险中性，无风险利率归零。

- t=1：释放公开信号 s∈{s_g, s_b}（如盈余公告），对基本面价值 V 不完全 informative。s=s_g → V=X>0 确定（高质量企业）；s=s_b → V=0 或 X 各半。
- t=2：B 付出监督努力 μ∈[0,1]，成本 ½cμ²，获得精度随 μ 上升的私有信号 i∈{i_g, i_b}。随后一轮交易：B 收到 i_b 时卖出 β 单位，否则持有；受短卖约束 β≤α。流动性交易者需求 u 服从指数分布 f(u)=λe^(−λu)，其中 λ=1/(ν(1−α))，ν≤1 为流动性参数。竞争性做市商观察总需求 d=b+u，按 Kyle (1985) 定价 P=E[V|d,s]。
- t=3：V 揭晓。
- 经理 M：风险中性，对 t=2 股价赋权 ω、对 t=3 企业价值赋权 1−ω，0<ω<1。ω>0（短视动机）外生给定。t=0 时高质量企业的经理可投资长期项目 θ∈[0,1]，把 t=3 价值抬到 V=X+gθ，但以概率 θ² 触发坏信号 s_b；g 为项目生产率。投资机会不为做市商和 B 所知（凸显 B 无须知晓增长机会即可促进投资）。

## 核心假设

- [[edmans-three-period-risk-neutral]]：风险中性、三期、信号 s 不完全揭示 V 的时序与支付结构。
- [[edmans-short-sales-constraint]]：β≤α，B 只能卖出已持有的份额——把"持股规模"与"信息获取激励"挂钩的核心建模手法。
- [[edmans-costly-monitoring-precision]]：监督努力 μ 成本 ½cμ²，信号精度随 μ 上升。
- [[edmans-exponential-liquidity-demand]]：流动性交易需求服从指数分布，使 B 的卖出量可闭式求解。
- [[edmans-manager-myopia-weight]]：经理对当期股价赋权 ω>0，外生（本文研究短视的解而非成因）。

## 解概念

竞争性做市商的理性预期（Nash）均衡：给定做市商定价函数，B 的交易与监督决策最优；给定 B 的决策，做市商定价令其零利润（[[kyle-1985-informed-trading]] 框架）。在内生持股分析中，进一步用"对再交易稳健"筛选出私有最优持股 α_P*——即 B 若在 t=0 不可观测地买入会选择的持股。

## 命题与证明

- [[edmans-lemma1-market-maker-pricing]]：做市商定价、B 的监督努力 μ=βX/4c、卖出量 β=min(1/λ, α)。
- [[edmans-lemma2-finite-optimal-block]]：最大卖出量与监督在有限持股 α*=ν/(ν+1) 处最大化，β 与 μ 关于 α 非单调（先增后减）。
- [[edmans-prop1-market-efficiency]]：市场效率 π_X 在 α=α* 处最大化（交易效应 + 伪装效应 + 努力效应）。
- [[edmans-lemma3-investment-level]]：经理最优投资 θ=min((1−ω)g/(2ωX(1−π_X)), 1)，随 g、π_X 升而随 X、ω 降。
- [[edmans-prop2-investment]]（**全文核心结果**）：实体投资 θ 弱增于市场效率 π_X，故在 α=α* 处最大化——大股东即使不能干预也能促进长期投资。
- [[edmans-prop3-liquidity-exogenous-block]]：持股外生时，市场效率与投资在有限流动性 ν*=α/(1−α) 处最大化（非单调）。
- [[edmans-prop4-liquidity-endogenous-block]]：持股内生时 α_P*<α* 且随流动性单调上升，投资随流动性单调上升。

## 比较静态

- **持股规模 α**：价格效率与实体投资关于 α 呈倒 U 型，在有限的 α*=ν/(ν+1) 处达峰。重要的不是持股本身，而是其引致的最优交易量 min(1/λ, α)——这与美国"大股东普遍存在但巨型大股东罕见"的事实一致。
- **流动性 ν**：持股外生时，投资关于流动性非单调（ν*=α/(1−α) 处达峰），因过高流动性会伪装 B 的交易；持股内生时（α 随流动性上升），伪装效应被抵消，投资随流动性单调上升。两种情形都推翻"流动市场加剧短视"的传统观点。
- **信息不对称 1/c**：大股东对投资的边际作用 ∂θ/∂α 随 c 下降（信息不对称上升）而增强——可供 B 注入价格的信息越多，其增量作用越大。
- **项目生产率 g 与短视权重 ω**：|∂θ/∂α| 弱增于 g、弱减于 c 与 ω。若 g 高到 X≤X1，经理无须大股东也充分投资（θ=1）；若 ω 过大，即便有大股东仍欠投资。

## 可检验推论

模型导出、可拿去实证的符号关系：

- **大股东/耐心资本促进长期投资、抑制短视** → 落 [[pc-attenuates-managerial-myopia]]（Edmans 提供第二条理论微观基础，机制为"退出/交易"而非 Stein 1988 的"收购威胁/信号"）。
- **持股规模对私有信息含量、交易利润与价格效率的影响呈凹形（倒 U）** → 落 [[block-size-concave-price-efficiency]]；这是"大股东作为知情交易者"框架独有、区别于干预模型的预测。
- **市场流动性促进（而非阻碍）长期投资** → 落 [[liquidity-promotes-long-term-investment]]，反驳 Porter (1992)、Thurow (1993)。
- 集中持股（block 大小）比机构总持股更能度量投资者的知情程度。
- 大股东卖出应传递负面信息、压低股价，且价格冲击随卖出量而非初始持股而增（Mikkelson-Partch 1985）。
- 检验挑战：持股内生（Prop 4），需找持股的外生变动；须排除内部人与极少交易的大股东（家族、指数基金），并聚焦短卖成本非平凡的情形。

## 对实证的启发

本文是耐心资本/机构投资者实证文献的第三个理论锚点（与 [[stein-1988-takeover-threats-managerial-myopia]]、[[yoon-2021-dynamic-mechanism-design]] 并列），但给出一条**与 Stein 互补的独立机制**：Stein 1988 是"收购威胁 → 短视，耐心股东经由信号缓解"；Edmans 2009 是"大股东知情交易（退出/华尔街规则）→ 价格反映基本面 → 经理敢做长期投资"——治理通过**退出**而非**话语权**实现。这为本项目区分两类机制提供了理论依据：

- [[governance-through-trading-exit]] 机制的形式化源头，区别于 voice/监督型机制 [[stable-investor-monitoring-channel]]。
- 为 [[managerial-myopia-mediation]] 补一条"退出威胁/价格效率"的理论传导，与 Stein 的"收购威胁"并列。
- "持股—价格效率倒 U"提醒本项目：耐心资本（长期机构持股）的效应未必随持股比例单调，应检验非线性设定（呼应 [[贾勇-2025-耐心资本-创新韧性-倒u型]] 的倒 U 发现）。
- 模型把"信息不对称越强、大股东作用越大"形式化（∂²θ/∂α∂c<0），与 [[李思飞-2025-耐心资本-esg表现]]、[[杨芳-2024-耐心资本-新质生产力-内部控制-信息不对称]] 的信息不对称机制检验在理论上一致。
- 内生性警示：Edmans 明确指出持股内生（Prop 4），实证需外生变动——与本项目各篇用 IV/PSM/Heckman 处理 PC 内生性的做法对应。

## Related

- 机制：[[governance-through-trading-exit]]、[[managerial-myopia-mediation]]
- 假设（可检验推论）：[[pc-attenuates-managerial-myopia]]、[[block-size-concave-price-efficiency]]、[[liquidity-promotes-long-term-investment]]
- 同问题理论（互补机制）：[[stein-1988-takeover-threats-managerial-myopia]]
- 理论基础：[[kyle-1985-informed-trading]]
