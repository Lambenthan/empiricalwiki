---
title: "交易型机构投资者持股比例（A1 换手率三分组法，TRANSINS）"
slug: "transactional-institutional-investors-turnover"
construct: "机构投资者异质性 / 短期机构投资者（A1 换手率三分组变体的高换手组）"
role: core_explanatory
measurement: "Step 1：按半年度计算每个机构投资者的双向最小买卖额比换手率 CR_{k,t}；Step 2：研究期内每半年度换手率求算术均值得 AVR_CR_k；Step 3：剔除持股期不足 2 期的机构投资者后，按 AVR_CR_k 等距三分组；Step 4：换手率最高组定义为交易型机构投资者；Step 5：TRANSINS_{i, t} = 交易型机构投资者在公司 i 的合计持股比例（取并购首次公告日前最近半年度或年度末数据）。"
data_sources: [wind, tonghuashun, csmar]
database_tables: [机构投资者持股, 机构投资者交易明细]
frequency: deal-event (snapshot at last semi-annual or annual report before announcement)
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

按机构投资者持股换手率三分组划分得到的"交易型"机构投资者在某上市公司的合计持股比例。"交易型"代表换手率最高的一组机构投资者，西方主流文献预设其为短期投机者；但周绍妮 (2017) 在中国情境下提出反直觉判断：**交易型 ≈ 主动投资型**，因激励机制与短期业绩高度相关，反而更有动力主动监督公司治理与并购决策。

周绍妮 (2017) 530 起国企并购样本均值 4.23%、中位数 1.19%、std 6.53、最大 31.12%，整体水平显著高于稳定型（[[stable-institutional-investors-turnover]] 均值 1.10%）。

## Measurement

公式与 [[stable-institutional-investors-turnover]] 一致，仅在 Step 4 取换手率最高组：

```
Step 1-3：见 stable-institutional-investors-turnover

Step 4（三分组）：按 AVR_CR_k 升序排列后等距三分组，最高组定义为交易型 (Trans=1)。

Step 5（公司层合计持股比例）

TRANSINS_{i, t*} = Σ_{k ∈ Trans} 机构投资者 k 在公司 i 第 t* 期持股比例
```

时点 t* 取并购首次公告日前最近半年度末或年度末。

## Data Source

[[wind]]、[[tonghuashun]] 提供机构投资者半年度持股变动；[[csmar]] 行情库提供股价。

## Literature Variants

- A1 换手率三分组法（本变量）：周绍妮 (2017)；最早源 Gaspar (2005)、Yan and Zhang (2009)。
- A1 二分组变体（中位数法）：换手率高于行业-年度中位数的为交易型，低于的为稳定型。
- B2 中位数稳定性法：[[institutional-investor-heterogeneity-stability]]（INVW=0 即交易型）。
- 类型直接划分法：将证券投资基金中的混合型基金视为交易型。

## Construction Steps

参见 [[stable-institutional-investors-turnover]] Construction Steps，Step 6 改为打 `Trans = (CR_tier == 3)`。

## Stata Notes

参见 [[stable-institutional-investors-turnover]] Stata Notes，使用 `Trans` 标签代替 `Stable`：

```stata
gen Trans = (CR_tier == 3)
bysort i t: egen TRANSINS = total( share_kit / total_share_it ) if Trans == 1
```

## Caveats

- 中国情境特殊性：周绍妮 (2017) 论证我国交易型机构投资者中混合型基金占 70.16%，激励机制与短期业绩挂钩反而提升监督动机；表 4 列 1 显示 TRANSINS 系数 0.004*** 显著为正，验证此判断。这一发现与西方文献（Yan, 2009; Bushee, 1998）相反。
- 仅在政府干预较弱的非关联并购中显著：周绍妮 (2017) 表 4 列 3 非关联并购组 TRANSINS 0.004***、列 2 关联并购组 TRANSINS 0.002 (n.s.)；交易型机构投资者治理作用受政府干预阻断（参见 [[related-party-ma-split]]）。
- 高换手率组的内部异质性：混合型基金、其他基金、券商自营、QFII 等高换手率机构投资者投资动机差异大；本变量将其混合可能掩盖更细的类型异质性。
- 用于耐心资本研究的注意事项：交易型机构投资者**不是**耐心资本；本变量更应作为对照组使用，与 [[stable-institutional-investors-turnover]] 配对呈现，而不是单独作为耐心资本测度。

## Related

- 配对变量：[[stable-institutional-investors-turnover]]
- 上位构念：[[institutional-investor-holding]] · [[patient-capital]]（patient-capital 仅与稳定型相关，与交易型相反）
- 替代框架：[[institutional-investor-heterogeneity-stability]]（B2）
- 数据：[[wind]] · [[tonghuashun]] · [[csmar]]
- 主用论文：[[周绍妮-2017-机构投资者-国企-并购绩效]]
