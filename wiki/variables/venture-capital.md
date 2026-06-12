---
title: "风险投资 (Venture Capital, VC)"
slug: "venture-capital"
construct: "风险投资"
role: mediator
measurement: "风险投资机构在被投企业中的持股比例。简冠群 (2025) 借鉴周冲、袁经发 (2023) 使用风险投资持股比例 (VC) 衡量。"
data_sources: [国泰安 CSMAR, Wind, 私募通]
database_tables: [风险投资数据库, 上市公司股东信息表, IPO 招股说明书]
frequency: firm-year
source_papers: [简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

风险投资（Venture Capital, VC）指专门投资于早期、高成长性、高不确定性的科技创新型企业的权益资本。风险投资的核心特征：(a) 高风险、高潜在回报；(b) 持有期相对较短，通过股权退出（IPO 或并购）获取资本增值；(c) 通常伴随主动参与企业治理的"增值服务"。

按组织结构形式可分为：

- 独立风险投资（IVC, Independent Venture Capital）— 以专业 VC 机构为主体，更关注财务回报，对增长潜力大、创新能力强的企业具有更高投资意愿。
- 企业风险投资（CVC, Corporate Venture Capital）— 以企业战略投资部门为主体，更关注被投企业对母公司战略的服务程度。

## Measurement

简冠群 (2025) 测度（本论文）：

- VC = 风险投资机构持股比例 = ∑(风险投资机构 j 在企业 i 当期持股数) / 企业 i 总股本。

借鉴周冲、袁经发 (2023) 的做法，识别股东列表中类型为"风险投资"或"创业投资"的机构投资者，加总其持股比例。

替代度量（其他文献中常见，本论文未使用）：

- VC 哑变量：是否有 VC 持股（有 = 1）。
- 高 VC 持股哑变量：VC 持股比例是否高于行业中位数。
- VC 投资金额：以股权融资轮次中 VC 出资金额衡量。
- IVC / CVC 区分：薛超凯等 (2019) 区分独立与企业 VC 的差异化效应。

## Data Source

- [[csmar]] 风险投资数据库（识别股东中 VC 类机构）。
- [[wind]] 私募股权与创投数据库（补充未上市阶段 VC 投资记录）。
- 私募通（清科）历年 IPO / 融资轮次数据（用于补充 IVC vs CVC 区分）。

## Literature Variants

- 简冠群 (2025) — VC 持股比例（借鉴周冲、袁经发 2023）。
- 周冲、袁经发 (2023) — 中小企业融资成本研究中以 VC 持股比例为关键变量。
- 薛超凯、任宗强、党兴华 (2019) — IVC vs CVC 区分对初创企业创新的差异化影响。
- Hellmann & Puri (2000) — 美国 VC 文献中以 VC 是否进入企业治理结构（董事会席位）作为度量。

## Construction Steps

简冠群 (2025) 测度复现：

1. 从 CSMAR 上市公司股东表抽取每年所有股东信息（股东名称、持股数、持股比例）。
2. 从 CSMAR 风险投资数据库（或私募通、清科）取风险投资机构名单。
3. 按机构名称匹配，识别股东中属于风险投资 / 创业投资类型的机构。
4. 加总该企业当期所有 VC 类机构持股比例 → VC(i, t)。

## Stata Notes

```stata
* 假设已建立股东 - 机构类型对应表 shareholder_type
gen is_vc = (institution_type == "venture_capital")

bysort stkcd year: egen VC = total(holding_ratio) if is_vc == 1
replace VC = 0 if missing(VC)

* 主回归（机制第一阶段）
reghdfe VC Treat $controls Market, absorb(industry year) cluster(industry)
reghdfe VC Degree $controls Market, absorb(industry year) cluster(industry)
```

## Caveats

- VC 与 PE（Private Equity）、产业投资基金、政府引导基金边界模糊；不同数据库的"VC 类机构"定义差异较大。
- 风险投资机构在 IPO 后是否持续标记为 VC 需明确（部分研究只取 IPO 前 VC 持股快照）。
- 多家 VC 联合投资时是否区分领投 / 跟投，会影响 VC 治理参与度的解读。
- VC 与耐心资本边界：风险投资偏短期、高风险；耐心资本偏长期、低风险，简冠群 (2025) 将二者作为两条平行机制处理。
- VC 持股与企业当期业绩可能存在反向因果（业绩好的企业更易获得 VC 持股），需以滞后或 IV 处理。

## Related

- 互补变量：[[patient-capital]]（耐心资本，长期资金互补）。
- 配套机制：[[venture-capital-attraction-channel]]（专精特新转型 → VC → 新质生产力）。
- 配套被解释变量：[[new-quality-productive-forces]]。
- 配套数据集：[[csmar]] · [[wind]]。
- 配套论文：[[简冠群-2025-专精特新-新质生产力-风险投资-耐心资本]]。
