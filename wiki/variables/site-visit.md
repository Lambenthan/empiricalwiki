---
title: "机构投资者实地调研 (Site Visit, Vist)"
slug: "site-visit"
construct: "投资者实地调研"
role: moderator
measurement: "公司当年发生机构投资者实地调研活动取 1，否则为 0。来源于深交所自 2013 年起强制披露的《投资者关系活动记录表》。"
data_sources: [深圳证券交易所投资者关系活动记录表, 国泰安 CSMAR, 锐思 RESSET]
database_tables: [投资者关系活动记录表 / 调研事件表]
frequency: firm-year
source_papers: [徐灿宇-2023-异质机构投资者-实地调研-财务重述]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

机构投资者实地调研指证券分析师、机构投资者代表前往上市公司办公地或厂房等场所，与公司高管或员工进行面对面交流、参观与问答的活动。它是上市公司投资者关系管理的重要组成部分，也是机构投资者获取私有信息、了解公司真实经营状况的关键渠道。

## Measurement

- 哑变量口径（徐灿宇等 2023）：公司当年至少发生一次机构投资者实地调研事件，则 Vist=1，否则为 0；样本均值约 0.631，多数公司至少有一次。
- 频次口径（替代方案，常见于 Cheng et al.、Jiang & Yuan）：当年实地调研次数 / ln(1+次数)，用于刻画调研强度。
- 参与人数口径：当年参与调研的机构数量。

## Data Source

来自深圳证券交易所自 2013 年起要求上市公司编制并披露的 [[disclosure-investor-relations-form]]（《投资者关系活动记录表》）。CSMAR、锐思 RESSET 等数据库已对该表做结构化整理，可直接抽取实地调研事件、参与机构、调研时间。

注：上交所对投资者关系活动的强制披露要求晚于深交所，因此早期文献（包括徐灿宇等 2023）样本通常局限于深市 A 股。

## Literature Variants

- 哑变量（是否调研）：Cheng et al. (2016)、徐灿宇等 (2023)。
- 当年调研次数：Jiang & Yuan (2018)。
- 调研机构数量：刻画"被关注度"。
- 区分调研发起方：基金 / 券商 / 险资等。

## Construction Steps

1. 从深交所投资者关系活动记录表抓取每条调研事件的公司股票代码、活动日期、活动类型字段。
2. 仅保留 "实地调研" / "实地参观调研" 类型（剔除电话会议、业绩说明会等非实地形式）。
3. 按公司—年度聚合：count 实地调研事件次数；事件次数 ≥1 则 Vist=1。
4. 与稳定型机构投资者哑变量（Stable）交乘构造 Stable×Vist 调节项。

## Stata Notes

```stata
* 哑变量
bys stkcd year: egen visit_count = total(site_visit_flag)
gen vist = (visit_count >= 1)

* 频次（log 转换）
gen vist_freq = log(1 + visit_count)

* 交乘项
gen stable_x_vist = stable * vist
```

## Caveats

- 样本期 2013 年起方可使用（披露要求时间）；早于 2013 年的样本不可用。
- 上交所早期披露不完整，仅适合深市样本；扩展到全市场需谨慎核对披露完整性。
- 调研活动的内生性问题：业绩较差、信息不透明的公司可能更频繁被调研，反向因果需用 PSM、Heckman 或 IV 处理；徐灿宇等 (2023) 用 PSM 与 Heckman 缓解。
- 哑变量丧失了调研强度信息；高频调研与低频调研的治理效力可能不同。

## Related

- [[徐灿宇-2023-异质机构投资者-实地调研-财务重述]] — 实地调研作为调节变量首次进入本 wiki 的论文。
- [[disclosure-investor-relations-form]] — 数据底层来源。
- [[heterogeneous-institutional-investors-stable]] — 与本变量构造交乘的核心解释变量。
- [[information-environment-channel]] — 实地调研改善信息环境的理论路径。
