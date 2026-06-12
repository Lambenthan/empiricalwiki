---
title: "财务重述 (Financial Restatement, Restate)"
slug: "financial-restatement"
construct: "财务重述"
role: dependent
measurement: "公司当年发生财务重述行为则 Restate=1，否则为 0；亦可用一年内重述公告次数作为频率指标作稳健性。"
data_sources: [迪博数据库]
database_tables: [财务重述公告记录]
frequency: firm-year
source_papers: [徐灿宇-2023-异质机构投资者-实地调研-财务重述]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

财务重述（Financial Restatement）是指上市公司对前期已披露的财务报告做出会计差错更正与追溯调整的行为。它通常意味着原报告的可靠性下降，反映出管理层为追求个人利益而操纵盈余的事后补救动作，是管理层机会主义行为的可观察体现。

## Measurement

主流口径有二：

- 哑变量口径（徐灿宇等 2023）：当年发生财务重述事件取 1，否则为 0；样本均值约 0.136，约 14% 的公司—年度发生重述。
- 频率口径：一年内发布的财务重述公告次数；适合用作稳健性，可缓解多次重述被等同于一次的问题。

按内容可进一步细分：

- 技术问题型（Restate_t）：录入、校对、排版、统计、计算等技术原因导致的更正。
- 非技术问题型（Restate_nt）：会计问题、敏感问题等非技术原因导致的更正。

按经济后果可细分：

- 欺诈型（Restate_f）：当年同时发生违规行为的财务重述。
- 非欺诈型（Restate_nf）：发生重述但未发生违规。

## Data Source

[[迪博内部控制与风险管理数据库]]（迪博 DIB）：直接给出财务重述明细记录，包括重述时间、重述内容、重述类别。徐灿宇等 (2023) 使用迪博库判定 Restate=1。

## Literature Variants

- 单年是否发生（哑变量）：徐灿宇等 (2023)；袁蓉丽等 (2018)。
- 一年内重述次数（频率）：稳健性常见做法。
- 按重述类型细分：李春涛等 (2014) 区分技术问题型 vs 非技术问题型。
- 按经济后果细分：以是否伴随违规事件区分欺诈型 vs 非欺诈型。

## Construction Steps

1. 从迪博数据库下载财务重述公告记录表，获取公告日期、公告内容字段。
2. 按公司—年度聚合：当年至少有一次重述则 Restate=1。
3. 频率版本：count 当年内重述公告次数。
4. 类型版本：按公告内容关键字（"录入错误""会计估计变更""差错更正"等）匹配技术 vs 非技术；将公司—年度与违规行为表（如证监会处罚、交易所违规处分）合并判定欺诈型 vs 非欺诈型。

## Stata Notes

```stata
* 哑变量
gen restate = 0
replace restate = 1 if restatement_flag == 1

* 频率
bys stkcd year: egen restate_freq = total(restatement_event)

* 类型分组
gen restate_t = inlist(restate_type, "技术错误", "录入错误", "排版错误")
gen restate_nt = (restate==1 & restate_t==0)
```

## Caveats

- 迪博库对"重述事件"的判定可能与上交所/深交所披露文档存在小幅不一致，推荐与原始公告抽样核对。
- 财务重述的"年份"应当指事件发生年还是被重述的会计年度？文献多采用事件发生年（即公告年）作为 Restate=1 的赋值年，避免追溯赋值造成识别混淆。
- 均值偏低（约 13.6%），可能存在稀有事件偏差；徐灿宇等 (2023) 用稀有事件 Logistic 与补对数—对数模型作稳健性。
- 类型划分的关键字方法存在主观性，跨论文口径不完全一致。

## Related

- [[徐灿宇-2023-异质机构投资者-实地调研-财务重述]] — 本变量首次进入本 wiki 的论文。
- [[information-environment-channel]] — 财务重述的常见前因路径之一。
- [[internal-control-channel]] — 内部控制水平直接影响重述发生概率。
- [[restatement-type-split]] — 技术 / 非技术 / 欺诈 / 非欺诈分组。
