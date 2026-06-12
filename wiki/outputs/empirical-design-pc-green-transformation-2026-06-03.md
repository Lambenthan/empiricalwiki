---
title: "实证研究设计：耐心资本对企业绿色化转型的影响"
slug: "empirical-design-pc-green-transformation-2026-06-03"
topic: "patient-capital → green transformation"
date: 2026-06-03
generated_by: "/empirical-design"
key_anchor_papers:
  - 谢婷婷-2025-耐心资本-动态能力-绿色转型
  - 邱蓉-2024-耐心资本-全要素生产率
  - 强国令-2025-耐心资本-漂绿
  - 代飞-2025-耐心资本-双元创新-管理者短视
---

# 实证研究设计：耐心资本对企业绿色化转型的影响

> 本设计区分两类来源。凡标注「文献已有」的判断，均来自已 ingest 的 wiki 论文卡片；凡标注「本项目建议」的判断，是在现有证据基础上为本课题做的设定，尚无单篇文献完全照此执行。第 13 节诚实列出 wiki 当前缺乏支撑、本设计不予采用或需先补文献的设定。

## 1. 研究问题

核心问题：耐心资本（[[patient-capital]]）能否促进中国 A 股上市公司的绿色化转型（[[green-transformation]]），其传导机制是什么，在何种企业属性与行业环境下效应被放大？

子问题：
- Q1（主效应）：耐心资本是否显著提升企业绿色化转型水平？
- Q2（结构差异）：耐心资本的股权侧（稳定型 / 战略型机构持股）与债权侧（关系型债权）对绿色化转型的拉动是否对称？
- Q3（机制）：耐心资本是否通过缓解管理者短视主义（[[managerial-myopia-mediation]]）与降低融资约束（[[financing-constraint-mediation]]）传导到绿色化转型？
- Q4（异质性 / 调节）：在不同污染属性、产权性质、行业竞争度与企业规模的企业之间，效应是否存在差异？

口径说明（本项目建议，与项目根 `CLAUDE.md` 第一节"主回归口径待指定"对接）：
- 被解释变量主口径：绿色化转型词频法（[[green-transformation]]，谢婷婷 2025 路线）。
- 核心解释变量主口径：熵值法 C 框架（[[patient-capital]] 的 C 变体，邱蓉 2024 路线）；替换口径用换手率法 A4（强国令 2025）与持股时长法 B1（谢婷婷 2025 战略型）。
- 机制主口径：管理者短视主义 MD&A 版（[[managerial-myopia]]，胡楠 2021）。

## 2. 文献定位

wiki 内已有一篇直接做"耐心资本 → 绿色化转型"的论文，以及多篇可提供 PC 测算、机制、识别模板的相邻论文。

| 文献 | PC 测度 | 被解释变量 | 机制 | 识别策略 | 与本设计关系 |
|---|---|---|---|---|---|
| [[谢婷婷-2025-耐心资本-动态能力-绿色转型]] | B1 持股时长法（战略型机构持股比例） | 绿色化转型词频（113 词，LN(freq+1)） | 动态能力三维（[[dynamic-capability-mediation]]） | 企业+年份双向 FE；行业均值 IV + 滞后 IV | 唯一同因变量论文，提供被解释变量构造与异质性模板 |
| [[邱蓉-2024-耐心资本-全要素生产率]] | C 熵值法（3 维 7 指标） | 全要素生产率 | 创新效率 + 不确定性感知 | 双向 FE；滞后 IV + 金融中心距离 IV | 提供本设计 PC 主口径（熵值法 C 框架）范本 |
| [[强国令-2025-耐心资本-漂绿]] | A4 换手率 2 分组 + 总长债 | 漂绿（言行差距） | 信息透明度 / 代理冲突 / 绿色投资 | 行业-年份 + 省份-年份高维 FE；养老金 IV + 城市金融 IV | 提供 PC 替换口径与绿色场景识别；漂绿可作绿色化转型对照 |
| [[代飞-2025-耐心资本-双元创新-管理者短视]] | A2 标准差变体 + 银行长债 | 双元创新 | 管理者短视（[[managerial-myopia-mediation]]） | 公司 FE；行业均值 IV + 滞后 IV 双工具 | 提供本设计机制主口径与管理者短视测度 |

文献已有做法的关键观察：
- 谢婷婷（2025）已证 PC 对绿色化转型显著为正（基准 0.212***，IV 二阶段 0.695***/0.088***），但其机制走"动态能力"路径，未检验管理者短视与融资约束这两条更基础的公司金融通道。
- 谢婷婷（2025）的 PC 用 B1 持股时长法（战略型机构持股比例），未做跨框架（熵值法 C / 换手率 A4）的稳健性矩阵。

研究空白（本项目可填补，本项目建议）：
1. 在同一因变量（绿色化转型）下，引入管理者短视（[[managerial-myopia-mediation]]，对应假设 [[pc-attenuates-managerial-myopia]]）与融资约束（[[financing-constraint-mediation]]）两条机制，与谢婷婷（2025）的动态能力机制形成互补而非重叠的解释；
2. 用熵值法 C 框架（邱蓉 2024）作主测度，B1 / A4 作稳健性，补齐 PC 测度跨框架矩阵；
3. 把强国令（2025）的漂绿测度纳入稳健性，区分"实质绿色化转型"与"象征性披露"，回应"词频法是否只是漂绿"的潜在批评。

## 3. 理论机制

被解释变量是绿色化转型，机制变量必须与该构念有清晰的概念边界，不能与绿色化转型本身同义反复。本设计选取两条公司金融基础通道：

- 管理者认知通道（管理者短视主义机制 → [[managerial-myopia-mediation]]）：绿色化转型属于"高前置成本、长回报周期"的战略投入，与管理者对短期业绩的过度偏好天然冲突。耐心资本通过资源承诺（长期股权 + 银行长债缓解短期业绩焦虑）、治理干预（长期持有 + 深度参与纠正短视）与信号传递（提高对失败的容忍度）三条路径降低管理者短视，使管理层将注意力从短期财务指标重新分配到长期绿色能力建设。该机制的理论祖先为 [[stein-1988-takeover-threats-managerial-myopia]]（耐心股东削弱经理短视动机）与 [[edmans-2009-blockholder-trading-managerial-myopia]]（大股东退出威胁通道），实证模板见 [[代飞-2025-耐心资本-双元创新-管理者短视]]。
- 资本赋能通道（融资约束机制 → [[financing-constraint-mediation]]）：绿色技术研发与污染治理投入需要持续、稳定的长期资金。耐心资本以稳定型 / 战略型机构持股与关系型长期债务直接增加企业可获取资金规模，并通过长期承诺向外部释放"可持续增长"信号吸引接续投资，缓解融资约束，为绿色化转型提供资金基础。证据见 [[储佩佩-2025-耐心资本-企业韧性]]（PC → WW 指数显著为负）。

机制选取的边界说明（本项目建议）：管理者短视刻画的是"认知-决策时间偏好"层面的偏差，融资约束刻画的是"资金可得性"层面的约束，二者与绿色化转型（年报绿色词频度量的转型行为强度）在构念上不重叠，理论上可叠加。代理成本（[[agency-cost-mediation]]）与信息不对称（[[information-asymmetry-mediation]]）作为可选第三、四通道备查，但二者已有论文（李季鹏 2025）的因变量是 TFP 而非绿色化转型，纳入需额外论证。

## 4. 研究假设

```
H1（主效应）：耐心资本显著促进企业绿色化转型。
H1a：稳定型 / 战略型机构持股（股权侧）对绿色化转型具有正向显著作用。
H1b：关系型债权（债权侧）对绿色化转型具有正向显著作用。

H2（机制：管理者短视）：耐心资本通过缓解管理者短视主义促进绿色化转型。
  对应 wiki 假设 [[pc-attenuates-managerial-myopia]]（PC → myopia，预期系数为负）+ myopia → 绿色化转型（预期为负）。

H3（机制：融资约束）：耐心资本通过缓解融资约束促进绿色化转型。
  PC → 融资约束（预期为负）+ 融资约束 → 绿色化转型（预期为负）。

H4（异质性）：PC → 绿色化转型效应在重污染 / 重点污染监控、国有、行业竞争度高、绿色化转型程度高的企业中更强。
```

文献已有锚定：H1 已被 [[谢婷婷-2025-耐心资本-动态能力-绿色转型]] 在 B1 框架下验证；H2 的 PC → myopia 段已被 [[代飞-2025-耐心资本-双元创新-管理者短视]] 验证（系数 -0.002***），但 myopia → 绿色化转型 段尚无直接证据，属本项目待检验；H3 的 PC → 融资约束 段已被 [[储佩佩-2025-耐心资本-企业韧性]] 验证（Equity → WW -0.118***、Debt → WW -0.259***），融资约束 → 绿色化转型 段属本项目待检验。

## 5. 变量设计

### 5.1 被解释变量

| 变量 | 含义 | 测度 | 数据源 | wiki 页面 |
|---|---|---|---|---|
| Green（主） | 绿色化转型 | LN(年报绿色化转型关键词词频 + 1)，113 词字典（解学梅、朱琪玮 2021） | [[csmar]] 年报全文 + [[cnrds]] | [[green-transformation]] |
| lngtfp（稳健 1） | 绿色全要素生产率 | 非径向 SBM-ML 指数 | [[csmar]] | [[green-transformation]]（稳健性变体） |
| GWS（稳健 2 / 对照） | 漂绿（言行差距） | 彭博 ESG 减华证 ESG 行业内标准化差分 | [[wind]]（华证 ESG） | [[greenwashing]] |

说明（本项目建议）：词频法是主测度（与谢婷婷 2025 可比）；绿色 TFP 作度量稳健性；漂绿作对照——若 PC 提升 Green 同时降低 GWS，可排除"词频上升只是漂绿"的批评。

### 5.2 核心解释变量（耐心资本，多框架矩阵）

参考 [[outputs/variable-map-patient-capital-2026-05-09]]，本设计采用如下测度矩阵：

| 测度 | 框架 | 来源 | 角色 |
|---|---|---|---|
| Pat（主） | C 熵值法：长期导向 / 风险承受力 / 战略性关系性 3 维 7 指标，熵权法合成 | [[邱蓉-2024-耐心资本-全要素生产率]] | 主回归核心解释变量 |
| PC_B1（稳健 1） | B1 持股时长法：战略型机构持股比例（持有时长 ≥ 机构跨公司平均时长） | [[谢婷婷-2025-耐心资本-动态能力-绿色转型]] | 稳健性（与同因变量论文对齐） |
| Debt / Invest（稳健 2 + 分项） | A4 换手率 2 分组 + 总长债：关系型债权 = 长期负债/总负债；稳定型股权 = 换手率均值二分组后稳定型持股比例 | [[强国令-2025-耐心资本-漂绿]] | 股权 vs 债权分项识别 + 经典口径对照 |

注：熵值法 C 框架中已含"短视主义"作为一个负向二级指标（邱蓉 2024 权重 9.7%）。本设计把管理者短视同时用作机制变量时，应在主测度的熵值合成中剔除该指标，避免自变量与中介变量同源造成机械相关（本项目建议，关键技术细节）。

### 5.3 中介变量

| 变量 | 含义 | 测度 | wiki 页面 |
|---|---|---|---|
| Myopia（主机制） | 管理者短视主义 | 胡楠等（2021）MD&A 文本 43 个短期视域词词频占比 × 100 | [[managerial-myopia]] · [[managerial-myopia-mediation]] |
| WW（机制 2） | 融资约束 | Whited & Wu（2006）/ 鞠晓生等（2013）WW 指数 | [[financing-constraint-mediation]] |
| Acost / Asy（备选） | 代理成本 / 信息不对称 | 管理费用率 / 流动性指标 PCA | [[agency-cost-mediation]] · [[information-asymmetry-mediation]] |

管理者短视主义在本项目数据中可直接获取（项目路径 `03_原始数据/管理者短视主义_2007-2024`，含 MDA 版与年报版两套，见 [[managerial-myopia]] frontmatter 的 `available_in_project: true`）。

### 5.4 控制变量

合并 [[谢婷婷-2025-耐心资本-动态能力-绿色转型]] 与 [[邱蓉-2024-耐心资本-全要素生产率]] 的控制变量集合：

| 变量 | 含义 | 计算公式 | 数据源 |
|---|---|---|---|
| Size | 企业规模 | LN(期末总资产) | [[csmar]] |
| FirmAge | 企业 / 上市年龄 | LN(当年 − 成立年 + 1) | [[csmar]] |
| Lev | 资产负债率 | 总负债 / 总资产 | [[csmar]] |
| ROE / ROA | 盈利能力 | 净利润 / 所有者权益（或总资产） | [[csmar]] |
| Growth | 营收增长率 | 本年营收 / 上年营收 − 1 | [[csmar]] |
| Quick | 速动比率 | (流动资产 − 存货) / 流动负债 | [[csmar]] |
| Indep | 独立董事比例 | 独立董事人数 / 董事总人数 | [[csmar]] |
| Dual | 两职合一 | 董事长 = 总经理取 1 否则 0 | [[csmar]] |
| Top1 | 第一大股东持股比例 | 第一大股东持股数 / 总股数 | [[csmar]] |

### 5.5 异质性 / 调节变量

| 变量 | 含义 | 来源 |
|---|---|---|
| KeyPollution | 是否重点污染监控单位（CSMAR 环境子库逐企业认定） | [[heterogeneity-key-pollution-monitoring]] |
| Pollution_ind | 行业污染属性（生态环境部重污染目录） | [[ownership-pollution-split]] |
| STATE | 产权性质（国有 vs 非国有） | [[state-ownership-split]] · [[ownership-pollution-split]] |
| HHI | 行业竞争度（赫芬达尔指数中位数分组 / 连续交互） | [[industry-competition-hhi-split]] · [[heterogeneity-market-competition-moderator-pc-nqpf]] |
| Size_mod | 企业规模（连续交互调节） | [[heterogeneity-firm-size-moderator-pc-nqpf]] |
| Green_degree | 绿色化转型程度（词频中位数分组） | [[heterogeneity-green-transformation-degree]] |

## 6. 数据来源与样本构造

### 6.1 数据源对照

| 数据源 | wiki 页面 | 用途 | 项目可用性 |
|---|---|---|---|
| CSMAR | [[csmar]] | 财务、治理、机构投资者持股、年报全文、控制变量、IV | 完全可得（项目演示数据底座） |
| 管理者短视主义数据 | [[managerial-myopia]] | 机制变量（MDA 版 / 年报版两套） | 完全可得（`03_原始数据/管理者短视主义_2007-2024`） |
| CNRDS | [[cnrds]] | 年报文本词频辅助、绿色转型词频构造 | 部分可得，需申请子库 |
| 华证 ESG | [[hua-zheng-esg]] / [[wind]] | 漂绿稳健性的实绩端评分 | 部分可得，仅稳健性用 |

### 6.2 样本构造（本项目建议）

- 样本区间：2012—2023 年（与谢婷婷 2025 对齐，便于主效应可比；下界受绿色化转型词频法 2012 年前披露不规范约束，见 [[green-transformation]] caveats）。若主测度改用熵值法 C 框架且不强求与谢婷婷对齐，可上溯至 2009 年（邱蓉 2024 起点）。
- 样本范围：沪深 A 股上市公司。
- 样本筛选（标准做法）：剔除金融保险（行业代码 J）；剔除 ST/*ST；剔除上市不足 2 年与关键变量缺失样本；连续变量上下 1% 缩尾。熵值法 C 框架的"过去 3 年持股标准差"项要求剔除上市不足 3 年的前期观测。
- 预期最终样本：约 25000—30000 公司年度观测（谢婷婷 2025 为 30084）。

### 6.3 数据加工流程

1. CSMAR 年报全文表 → 113 词绿色化转型字典词频统计 → LN(freq + 1) 得 Green。
2. CSMAR 机构投资者持股表 + 长期借款 / 应付债券 / 应付票据 + 所有者权益 + MD&A 短视词 → 7 个二级指标标准化 → 熵权法合成 Pat（主测度，剔除短视指标版另存供机制检验用）。
3. 直接合并 `03_原始数据/管理者短视主义_2007-2024` 得 Myopia。
4. CSMAR 财务报表 → WW 指数输入项 → 融资约束中介变量。
5. 全部按 stkcd × year 合并为面板，行业 / 污染 / 产权属性按 CSMAR 公司基本资料表回填。

## 7. 基准模型

主回归 → [[two-way-fixed-effects-firm-year]]（企业 + 年份双向固定效应，与谢婷婷 2025 一致）：

```
Green_{it} = β₀ + β₁ · Pat_{it} + Σ γ_k · Control_{k,it}
           + μ_i (Firm FE) + θ_t (Year FE) + ε_{it}        …… 式 (1)
```

Pat 在不同列分别替换为：(a) Pat（C 熵值法主）、(b) PC_B1（持股时长法）、(c) Debt 与 Invest 分项同时纳入（识别股权 vs 债权侧贡献）。

标准误：企业层聚类（cluster at firmid）。预期 β₁ > 0 且显著（参考谢婷婷 2025 基准 0.212***）。

PC 内部分解（式 2，参考强国令 2025 的 Debt / Invest 分别建模）：

```
Green_{it} = β₀ + β₁ · Invest_{it} + β₂ · Debt_{it} + Σ γ_k · Control + μ_i + θ_t + ε_{it}
```

## 8. 识别策略与内生性风险

### 8.1 内生性来源（具体）

1. 反向因果：绿色化转型水平高的企业更易吸引长期机构投资者增持（ESG 偏好型资金流入），Pat ↑；银行也更愿意为绿色转型良好的企业提供长期信贷，Debt ↑。这使 OLS 的 PC → Green 估计向上偏误。这是本课题最直接的内生性威胁，因为绿色化转型本身具有声誉与政策红利，对长期资本有正向"吸引"作用。
2. 遗漏变量：管理团队的长期导向、企业绿色文化、所在地环保政策力度等不可观测变量同时驱动 Pat 与 Green。企业固定效应可吸收时不变部分，时变部分（如 CEO 更替、地方环保督察）仍是威胁。
3. 测量误差：词频法对年报披露策略敏感（"漂绿"型披露会虚高 Green）；熵值法 C 框架对"过去 3 年持股标准差 → 0"的小公司敏感，二者叠加产生系统性测量误差。

### 8.2 识别策略

基线 = 企业 FE + 年份 FE + 企业层聚类标准误（[[firm-fixed-effects]]），叠加工具变量矩阵：

| IV 策略 | 工具变量 | 出处 | wiki 页面 |
|---|---|---|---|
| IV1（主） | 前十大股东持股比例之和 | 李思飞 2025 | [[iv-top10-shareholder-ratio]] |
| IV2 | 同行业（剔除自身）同年份绿色化转型 / PC 均值 | 简冠群 2025 / 谢婷婷 2025 | [[iv-industry-mean-trans-excluding-self]] |
| IV3 | Dickinson（2011）现金流分类企业生命周期 | 唐亮 2025 | [[iv-firm-life-cycle-dickinson]] |

补充识别：
- 动态面板系统 GMM（[[gmm-dynamic-panel]]）：引入 Green 滞后项处理绿色化转型的路径依赖与潜在双向因果，报告 AR(1)/AR(2) 与 Hansen J。
- Heckman + PSM（[[heckman-psm-restatement]]）：以 PC 中位数构造处理组，处理"长期资本非随机配置"的自选择偏差。
- 滞后处理：Pat_{t-1} 解释 Green_t，缓解同期反向因果（谢婷婷 2025 IV2 模板）。

IV 选择说明（本项目建议）：主 IV 用前十大股东持股之和（[[iv-top10-shareholder-ratio]]），相关性强（耐心资本必落入前十大股东）；但其排他性争议在于股权集中度可能直接影响治理质量，故需配 IV2（行业均值，[[iv-industry-mean-trans-excluding-self]]）与 IV3（生命周期，[[iv-firm-life-cycle-dickinson]]）交叉验证符号一致性。注意三套 IV 均为单工具，单独估计时无法做过度识别检验；若并入两个以上工具则报告 Hansen J。

## 9. 机制检验

采用江艇（2022）两步法 + Sobel + Bootstrap 三套并报（参考邱蓉 2024 的 Bootstrap 1000 次做法）。

```
Mediator_{it} = α₀ + α₁ · Pat_{it} + Σ γ_k · Control + μ_i + θ_t + ε_{it}    …… 式 (3)
Green_{it}    = β₀ + β₁ · Pat_{it} + β₂ · Mediator_{it} + Σ γ_k · Control + μ_i + θ_t + ε_{it}  …… 式 (4)
```

Mediator 依次替换：
- Myopia（管理者短视，主机制，预期 α₁ < 0）→ [[managerial-myopia-mediation]]，对应假设 [[pc-attenuates-managerial-myopia]]。PC → myopia 段有代飞 2025 证据（-0.002***）；myopia → Green 段为本项目新检验。
- WW（融资约束，预期 α₁ < 0）→ [[financing-constraint-mediation]]。PC → WW 段有储佩佩 2025 证据；WW → Green 段为本项目新检验。
- 备选：Acost（[[agency-cost-mediation]]）/ Asy（[[information-asymmetry-mediation]]），仅在主机制稳健后补充。

技术注意（本项目建议）：当主测度 Pat 用熵值法 C 框架且机制变量为 Myopia 时，必须使用"剔除短视指标"的 Pat 版本，否则自变量内含中介变量会造成机械中介。

## 10. 异质性检验

按以下维度做样本切分或连续交互项检验，分子样本估计基准模型 (1)，组间差异用 Bootstrap 1000 次经验 p 值或 Chow 检验：

| 维度 | 分组 / 交互方式 | 预期 | wiki 页面 |
|---|---|---|---|
| 重点污染监控单位 | CSMAR 环境子库 0/1 | 重点污染组 > 非重点污染组 | [[heterogeneity-key-pollution-monitoring]] |
| 行业污染属性 | 生态环境部重污染目录 | 重污染组更强（谢婷婷 2025：0.328*** vs 0.159***） | [[ownership-pollution-split]] |
| 产权性质 | 国有 vs 非国有 | 谢婷婷 2025 报国企更强；强国令 2025 报非国企更强——方向存争议，需实证定夺 | [[state-ownership-split]] |
| 行业竞争度 | HHI 中位数分组 | 高竞争组更强 | [[industry-competition-hhi-split]] |
| 市场竞争（调节） | HHI 连续交互 Pat × HHI | 按取向定符号 | [[heterogeneity-market-competition-moderator-pc-nqpf]] |
| 企业规模（调节） | Size 连续交互 Pat × Size | 大规模更强 | [[heterogeneity-firm-size-moderator-pc-nqpf]] |
| 绿色化转型程度 | 词频中位数分组 | 高绿色化组更强 | [[heterogeneity-green-transformation-degree]] |

文献已有冲突点（需在跨论文综合时讨论）：产权性质方向上，[[谢婷婷-2025-耐心资本-动态能力-绿色转型]]（国企组系数更大）与 [[强国令-2025-耐心资本-漂绿]]（非国企组显著、国企不显著）结论相反；行业竞争度方向上，[[industry-competition-hhi-split]]（温磊 2024，高竞争更强）与 [[heterogeneity-market-competition-moderator-pc-nqpf]]（杨芳 2024，低竞争更强，且 HHI 取向相反）也相反。本项目须在结果中明确 HHI 取向并对方向分歧给出解释，不可直接照搬单篇预期。

## 11. 稳健性检验

| 类别 | 具体做法 | wiki 页面 |
|---|---|---|
| 被解释变量替换 | 绿色 TFP（SBM-ML，lngtfp）；漂绿对照（PC → GWS 预期负） | [[green-transformation]] · [[greenwashing]] |
| PC 测度替换 | C 熵值法 ↔ B1 持股时长法 ↔ A4 换手率 2 分组 | [[patient-capital]] · [[stable-institutional-investors-turnover]] |
| 追加固定效应 | 叠加城市 FE（谢婷婷 2025 模板，PC 0.205***） | [[two-way-fixed-effects-firm-year]] |
| 样本剔除 | 剔除 2017 年后绿色金融改革创新试验区企业；剔除 2020—2022 疫情样本 | 谢婷婷 2025 模板 |
| 缩尾敏感性 | 上下 1% / 2% / 5% 缩尾 | 邱蓉 2024 模板 |
| 改聚类层级 | 企业 → 行业 / 地区聚类 | 邱蓉 2024 模板 |
| 滞后被解释变量 | Green 滞后一期 / 两期 | 强国令 2025 模板 |
| 安慰剂 | 1000 次随机分配 Pat | [[placebo-random-pc-assignment]] |

## 12. 预期表格结构

| 表号 | 内容 |
|---|---|
| 表 1 | 描述性统计（N、均值、SD、min、max） |
| 表 2 | 相关性矩阵 |
| 表 3 | 基准回归：Pat（C 主）/ PC_B1 / Invest + Debt 分项 共 3—4 列 |
| 表 4 | 内生性：IV1 前十大股东 / IV2 行业均值 / IV3 生命周期 + 系统 GMM |
| 表 5 | 机制检验：Myopia（主）+ WW（融资约束）+ Sobel p 值 + Bootstrap CI |
| 表 6 | 异质性：污染监控 / 行业污染 / 产权 / 行业竞争 / 规模调节 / 绿色化程度 |
| 表 7 | 稳健性矩阵：被解释变量替换（绿色 TFP / 漂绿）× PC 测度替换 |

预期论文主体约 9000—11000 字（不含文献综述）。

## 13. 数据缺口清单

本节诚实列出 wiki 当前缺乏文献支撑、本设计不予采用或需先 `/ingest` 补文献的设定，以及数据可得性分级。

### A. 若要纳入以下设定，wiki 目前缺乏文献支撑，需先 /ingest 补文献

1. ESG 作中介——wiki 没有 esg-mediation 节点，且 ESG 的 E 维度与绿色化转型构念高度重叠，纳入会造成同义反复。本设计不采用。若坚持纳入，需先 ingest "ESG → 绿色转型"的中介文献，并正式论证 ESG 与绿色化转型的构念边界（否则属机制变量与因变量同源）。
2. 研发投入作调节变量——wiki 无研发投入调节节点（研发投入在邱蓉 2024 / 谢婷婷 2025 中是创新效率 / 动态能力的构造分子，不是独立调节框架）。若要做研发投入调节，需先 ingest 相应文献并新建 heterogeneity 节点。
3. 制造业 / 非制造业异质性——wiki 仅有 [[high-tech-industry-split]]（高新技术行业 19 大类划分，温磊 2024），无制造业 / 非制造业分组节点。若要做制造业异质性，需先 ingest 制造业分组文献并新建节点；当前只能用高新技术行业划分近似。
4. 两权分离异质性——wiki 无两权分离（控制权与所有权分离率）的异质性或调节节点。若要纳入，需先 ingest 相应文献并新建节点。
5. 动态能力机制（[[dynamic-capability-mediation]]）虽有节点，但与绿色化转型构念部分重叠（创新能力 → 绿色技术创新本身就是绿色化转型的一个维度），本设计将其列为可选补充机制而非主机制，使用前需论证边界。
6. [[green-transformation-mediation]] 节点存在，但其因变量是产能利用率、绿色 TFP 作中介——方向与本课题相反（本课题绿色化转型是因变量而非中介），不可作为本设计的中介机制。

### B. 数据缺口分级

必需（缺 → 主分析无法做）：

| 数据 | 用途 | 项目可得性 |
|---|---|---|
| CSMAR 年报全文 | 绿色化转型词频被解释变量 | 项目演示数据底座，基本可得；113 词字典需自行复刻（解学梅、朱琪玮 2021 附录） |
| CSMAR 机构投资者持股 + 财务明细 | 熵值法 C 框架 7 个二级指标 | 完全可得 |
| 管理者短视主义数据 | 主机制变量 | 完全可得（`03_原始数据/管理者短视主义_2007-2024`，MDA / 年报两版） |

可选（缺 → 部分稳健性受限，主分析可做）：

| 数据 | 用途 | 替代方案 |
|---|---|---|
| 华证 ESG（[[hua-zheng-esg]] / [[wind]]） | 漂绿对照稳健性 | 仅作稳健性替换被解释变量，缺失不影响主分析；列为可选 |
| CNRDS 年报文本子库 | 绿色化转型词频辅助 | 可用 CSMAR 年报全文自行分词替代 |
| 绿色 TFP 的能源 / 工业三废微观数据 | lngtfp 稳健性 | 缺失则放弃绿色 TFP 稳健性，保留漂绿对照即可 |

暂不可得：

| 数据 | 用途 | 备注 |
|---|---|---|
| 银行长期贷款银行 vs 非银拆分明细 | A2 框架关系型债务 | 本设计 PC 主口径用熵值法 C，债权侧用 A4 总长债（长期负债/总负债，CSMAR 可直接算），不依赖银行明细，故无影响 |

## 14. 下一步操作

1. 立即可做：用 Stata 合并 [[csmar]] 演示数据 + `03_原始数据/管理者短视主义_2007-2024`，先构造 Green（词频）与 Pat（熵值法）两个核心变量并跑描述性统计，确认字段映射。
2. 字典复刻：复刻解学梅、朱琪玮（2021）113 词绿色化转型字典，这是被解释变量可比性的前提。
3. 可执行 skill：
   - `/stata-plan` 把本设计转成 do-file 骨架（合并 → 变量构造 → 描述统计 → 基准 → 机制 → 异质性 → 稳健性）；注意熵值法 Pat 需"含短视 / 剔除短视"两版本以适配机制检验。
   - `/novelty` 验证本设计相对 [[谢婷婷-2025-耐心资本-动态能力-绿色转型]] 的差异化贡献（机制从动态能力转为管理者短视 + 融资约束）。
   - `/check` 扫描本设计涉及的 wiki 页面是否齐全、cross-ref 是否完整。
4. 风险提示：
   - 主测度先固定 C 熵值法，B1 / A4 作稳健性，分阶段推进。
   - 机制变量 Myopia 与熵值法 Pat 同源（熵值法含短视指标），主测度须用剔除短视的 Pat 版本。
   - 词频法被解释变量须配漂绿对照，回应"绿色词频上升只是漂绿而非实质转型"的潜在批评。

---

## Related

- 直接相关论文：[[谢婷婷-2025-耐心资本-动态能力-绿色转型]]（同因变量）· [[邱蓉-2024-耐心资本-全要素生产率]]（C 熵值法主口径）· [[强国令-2025-耐心资本-漂绿]]（绿色场景 + A4 口径）· [[代飞-2025-耐心资本-双元创新-管理者短视]]（管理者短视机制）· [[储佩佩-2025-耐心资本-企业韧性]]（融资约束 + 治理机制）
- 理论源头：[[stein-1988-takeover-threats-managerial-myopia]] · [[edmans-2009-blockholder-trading-managerial-myopia]]
- 变量：[[patient-capital]] · [[green-transformation]] · [[managerial-myopia]] · [[greenwashing]]
- 变量字典：[[outputs/variable-map-patient-capital-2026-05-09]]
- 数据源：[[csmar]] · [[cnrds]] · [[hua-zheng-esg]] · [[wind]]
- 模型：[[two-way-fixed-effects-firm-year]] · [[two-way-fixed-effects-industry-year]]
- 机制：[[managerial-myopia-mediation]] · [[financing-constraint-mediation]] · [[agency-cost-mediation]] · [[information-asymmetry-mediation]]
- 假设：[[pc-attenuates-managerial-myopia]] · [[pc-promotes-high-quality-development]]
- 识别：[[iv-top10-shareholder-ratio]] · [[iv-industry-mean-trans-excluding-self]] · [[iv-firm-life-cycle-dickinson]] · [[gmm-dynamic-panel]] · [[firm-fixed-effects]] · [[heckman-psm-restatement]] · [[instrumental-variable-2sls]]
- 异质性：[[heterogeneity-key-pollution-monitoring]] · [[ownership-pollution-split]] · [[state-ownership-split]] · [[industry-competition-hhi-split]] · [[heterogeneity-market-competition-moderator-pc-nqpf]] · [[heterogeneity-firm-size-moderator-pc-nqpf]] · [[heterogeneity-green-transformation-degree]] · [[high-tech-industry-split]]
- 稳健性：[[placebo-random-pc-assignment]]
- 旧设计对照：[[outputs/empirical-design-pc-esg-2026-05-09]]
