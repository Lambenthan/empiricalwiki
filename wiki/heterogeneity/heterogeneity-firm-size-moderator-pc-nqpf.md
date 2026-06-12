---
title: "企业规模调节：耐心资本对新质生产力影响的规模放大效应"
slug: "heterogeneity-firm-size-moderator-pc-nqpf"
grouping_variable: "企业规模 Size = ln(总资产)"
grouping_rule: "在基准模型中加入 Size 主效应 + 稳定型股权 × Size + 关系型债权 × Size 两组交互项（连续调节，未做样本分组）"
rationale: "规模较大的企业在发展新质生产力的条件和基础上更优——内部控制体系更成熟、信息披露更规范、资源能力更厚实——耐心资本带来的内外部环境改善（内控质量提升、信息优势增强）能更快速、更有效地作用于新质生产力的提升，从而产生更强的促进作用"
source_papers: [杨芳-2024-耐心资本-新质生产力-内部控制-信息不对称]
date_updated: 2026-05-07
---

## Grouping Logic

本异质性分析采用"调节变量 × 核心解释变量"的连续交互项形式，而非样本分组。在基准模型中加入：

- 企业规模主效应：`β_Size · Size`
- 稳定型股权 × 企业规模：`β_Wd_Size · Wd × Size`
- 关系型债权 × 企业规模：`β_Pc_Size · Pc × Size`

其中企业规模 Size = ln(总资产)。所有变量沿用基准模型 1% 缩尾与滞后一期处理。样本量与主回归一致 n = 17182。

## Theoretical Rationale

杨芳等（2024）从企业内部环境与外部环境联动角度论证规模的放大作用：

- **内控基础更厚**：规模较大的企业内部控制体系建设较为成熟、组织流程规范，耐心资本治理监督渗透时摩擦较小，内部控制质量改善的边际效率更高。
- **信息披露更规范**：大规模企业披露规则严格，耐心资本信号传递（信誉机制、声誉机制）作用空间更大，信息不对称缓解的边际效应更显著。
- **资源能力更强**：发展新质生产力（如数字技术、绿色技术、人工智能采纳）需要大额持续投入，规模较大的企业有更强的承担能力，耐心资本到位后能更快转化为生产力提升。
- **战略响应能力更强**：政策导向（"双碳"、新质生产力培育）的重点对象是大规模企业，耐心资本流入后的政策红利转化效率更高。

## Sample Split

杨芳等（2024）表 6 Panel A（n = 17182，调整 R² = 0.445/0.451）：

- 主效应：企业规模 Size 系数 2.0395∗∗∗（t = 34.39）/ 2.2553∗∗∗（t = 35.13），表明企业规模与新质生产力发展水平显著正相关。
- 主项 PC：稳定型股权 10.6584∗∗∗（t = 2.62）；关系型债权 2.7539∗∗∗（t = 4.18）（注意系数大小与基准回归不同，因加入交互项后基础组别发生变化）。
- 交互项：
  - 稳定型股权 × 企业规模：0.9960∗∗∗（t = 12.63）。
  - 关系型债权 × 企业规模：0.0567∗∗∗（t = 4.41）。

两组交互项均在 1% 水平显著为正，表明耐心资本对新质生产力的促进作用在规模较大的企业中显著更强。

## Model

```stata
* 准备 Size 中心化（避免共线性）
gen size_c = size - r(mean) // 或采用 demean

* 调节模型（两个 PC 维度分别跑）
reghdfe Npro L.Wd L.size L.Wd##c.L.size $controls, ///
    absorb(industry year) cluster(firmid)
reghdfe Npro L.Pc L.size L.Pc##c.L.size $controls, ///
    absorb(industry year) cluster(firmid)
```

注意：因 Size 与控制变量中 Roa、boardsize 等已有相关性，建议 Size 中心化或对 PC 与 Size 同步去均值，以减轻交互项与主效应间的共线性。

## Interpretation

- 交互项系数为正且显著，表明 PC → NQPF 的边际效应随企业规模增大而增强。
- 经济意义：稳定型股权 × Size 系数 0.9960（Wd 平均 0.012、Size 平均接近 22），意味着规模每增加 1 个单位（lnA 加 1，即资产翻 2.7 倍），稳定型股权对 NQPF 的边际效应额外增加 0.996 个单位；与基准 22.40 相比，规模较大的企业耐心资本作用约放大 4%-5%。
- 关系型债权 × Size 系数 0.0567，相对较小，反映债权侧对规模的调节敏感度低于股权侧；可能因为长期债权对规模本身较为依赖，规模放大空间有限。
- 实务含义：耐心资本政策对中小规模企业的边际效应较弱，应配套中小企业新质生产力专项扶持机制（如政策性长期贷款、科创板专项融资），才能让中小企业也享受耐心资本带来的红利。

## Related

- 来源论文：[[杨芳-2024-耐心资本-新质生产力-内部控制-信息不对称]]（表 6 Panel A）。
- 同 paper 异质性：[[heterogeneity-equity-concentration-moderator-pc-nqpf]]（股权集中度调节）、[[heterogeneity-market-competition-moderator-pc-nqpf]]（市场竞争程度调节）。
- 类似规模异质性（不同因变量）：[[heterogeneity-firm-size-split-pc-esg]]（PC → ESG 表现，唐亮 2025，样本分组形式）。
- 配套被解释变量：[[new-quality-productive-forces]]。
- 配套核心解释变量：[[stable-institutional-investors-turnover]] · [[relational-debt-total-long-debt-ratio]]。
