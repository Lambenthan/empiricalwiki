---
title: "重点污染监控单位/非重点污染监控单位分组"
slug: "heterogeneity-key-pollution-monitoring"
grouping_variable: "KeyPollution（CSMAR 环境经济研究子库识别企业是否被列入重点污染监控单位）"
grouping_rule: "按企业是否属于重点污染监控单位虚拟变量分两组"
rationale: "重点污染监控单位面临更高环保压力与社会责任要求，且 ESG 改进空间大；耐心资本的长期投资属性恰好满足这类企业的长期 ESG 投入需求"
source_papers: [李思飞-2025-耐心资本-esg表现]
date_updated: 2026-05-07
---

## Grouping Logic

KeyPollution 来自 [[csmar]] "环境经济研究"子库，企业被生态环境部门列为国家或省级重点污染源监控单位时取 1，否则为 0。直接按虚拟变量分组，不需中位数划分。

注意：本分组与基于行业的"重污染行业目录"分类不同。
- 行业目录法（如生态环境部 16 类重污染行业）按行业代码批量识别，所有同行业企业归为同组（参见 [[ownership-pollution-split]] 与 [[heavy-pollution-industry-sample]]）；
- 重点污染监控单位是逐企业认定，由地方监管部门根据排污强度、污染物种类、所在区域生态敏感性等综合评估纳入名单。同一行业内企业可能既有又没有被列入。

## Theoretical Rationale

李思飞 (2025) 给出两条机制：

- 改进动力侧：重点污染监控单位面临高强度环保监管和社会责任要求，有强烈动机通过提升 ESG 表现来回应外部压力；而耐心资本的长期主义投资理念与可持续发展逻辑高度契合，更可能配置到这类企业。
- 改进空间侧：重点污染监控单位 ESG 起点较低，存在较大改进空间；耐心资本提供的长期资金与专业指导可推动企业实施环保改造、提升社会责任履行能力、优化治理结构；政策层面的环保支持进一步放大耐心资本的边际效应。

## Sample Split

李思飞 (2025) 表 7 列 (5)-(6)：

- 重点污染监控单位组：n = 7,320，PC 系数 1.7557** (t = 2.15)，Adj R² = 0.5549。
- 非重点污染监控单位组：n = 28,972，PC 系数 0.4536 (t = 1.41, n.s.)，Adj R² = 0.4908。
- 组间系数差异 -1.302*，对应 P 值 0.058。

## Model

主回归模型不变 ([[two-way-fixed-effects-firm-year]] 同结构)：

```
ESG_it = α₀ + α₁ PC_it + Controls + ΣFirm + ΣYear + ε
```

按 KeyPollution 取值 1/0 分组分别估计。

## Interpretation

- 重点污染监控单位子样本 PC 显著为正 (1.7557**) 且量级近基准回归两倍，非重点污染子样本不显著；组间差异在 10% 水平显著 (P = 0.058)。
- 该结果初看与"PC 对 E 分项无显著影响"的分项检验结论存在张力——若 PC 在重点污染单位中改善 ESG 显著，是改善 E 还是 S/G？作者未明确报告该子样本的 E/S/G 分项分解，是值得进一步追问的开放点。
- 政策启示：对环保高压企业引入长期资本（社保基金、政府引导基金、长期保险资金）能显著放大 ESG 治理边际，应作为绿色金融政策的重点工具。

## Related

- 主用例：[[李思飞-2025-耐心资本-esg表现]]
- 同一论文的另两类外部监督异质性：[[heterogeneity-analyst-coverage-monitoring]] · [[heterogeneity-media-coverage-monitoring]]
- 行业级污染分类的对照：[[ownership-pollution-split]] · [[heavy-pollution-industry-sample]]
- 数据：[[csmar]] (环境经济研究子库)
