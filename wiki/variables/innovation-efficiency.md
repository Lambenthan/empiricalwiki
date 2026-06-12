---
title: "创新效率 (Innovation Efficiency, Ineff)"
slug: "innovation-efficiency"
construct: "创新效率"
role: mediator
measurement: "三种专利（发明、实用新型、外观设计）数量加 1 取自然对数得到专利申请数，再用单位研发投入转化的专利申请数刻画创新效率。"
data_sources: [国泰安 CSMAR, 上市公司专利数据]
database_tables: [研发投入, 专利申请明细]
frequency: firm-year
source_papers: [邱蓉-2024-耐心资本-全要素生产率]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

创新效率指研发投入与专利产出之间的转化率，反映企业把资金投入转化为可专利化创新成果的能力。在邱蓉等 (2024) 的理论模型中记为 I，作为耐心资本与 TFP 之间的中介变量。

## Measurement

邱蓉等 (2024) 参照虞义华等 (2018)、方先明和胡丁 (2023)：

1. patent_count = 发明专利申请数 + 实用新型专利申请数 + 外观设计专利申请数。
2. ln_patent = ln(patent_count + 1)。
3. Ineff = ln_patent / 研发投入（或单位研发投入转化的专利申请数）。

样本均值 Ineff = 0.164，标准差 0.084，最小 0、最大 0.729。

## Data Source

[[csmar]] 提供研发投入字段（财务报表附注 - 研发支出）。专利数据可来自 CSMAR 专利子库、CNRDS 专利数据库、CPDP 或国家知识产权局开放数据。

## Literature Variants

- 加权专利数（按引用次数或质量分加权）：更精细，但中文实证较少使用。
- 仅发明专利计数：刻画"高质量"创新，不含实用新型与外观设计。
- 研发支出 / 营业收入：研发强度，是上游变量，不是效率指标。
- 专利产出 / 员工数：人均创新效率。

## Construction Steps

```
* CSMAR 专利字段：CN_Patentinfo（专利申请明细）
* 步骤 1：按企业-年度聚合三种专利
collapse (count) patent_id if patent_type=="发明", by(stkcd year)
rename patent_id n_invention
* 同理得 n_utility, n_design

* 步骤 2：合并并取对数
egen total_patent = rowtotal(n_invention n_utility n_design)
gen ln_patent = ln(total_patent + 1)

* 步骤 3：与研发投入合并（CSMAR 财务报表附注）
gen innov_efficiency = ln_patent / rd_expense
```

## Stata Notes

需要注意的边界情况：

- 研发投入为 0 或缺失：该年 Ineff 不可定义，可设为缺失或用研发投入 + 1 取对数后做比值。
- 专利申请年份有滞后（申请日 vs 公开日）：邱蓉等 (2024) 用申请数，故应用申请日年份匹配。
- 原口径 ln_patent / rd_expense 量纲混合（对数 / 元），稳健性可改用 ln_patent / ln(rd_expense + 1)。

## Caveats

- 专利计数受行业差异影响极大：制造业 vs 服务业、高科技 vs 传统行业不可同口径比较。
- 实用新型与外观设计的"创新含金量"低于发明专利，不加权可能放大低质量创新企业的得分。
- 研发投入存在企业操纵动机（享受加计扣除税收优惠），需做异常值识别。

## Related

- 上游：[[patient-capital]]。
- 下游：[[total-factor-productivity]]。
- 同属机制：[[innovation-efficiency-uncertainty-mediation]]。
- 相关机制对照：[[managerial-myopia-mediation]]（同样以耐心资本为上游，但走管理者认知渠道）。
- 配套创新变量（其他论文）：[[exploratory-innovation]] · [[exploitative-innovation]]。
