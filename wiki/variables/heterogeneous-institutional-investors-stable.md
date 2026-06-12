---
title: "异质机构投资者—稳定型 / 交易型 (Stable, B2 持股稳定性中位数法)"
slug: "heterogeneous-institutional-investors-stable"
construct: "异质机构投资者 / 耐心资本（股权侧时间属性变体）"
role: core_explanatory
measurement: "SD = 机构投资者持股比例 / 过去三年机构投资者持股比例标准差。当公司当年 SD ≥ 行业年度中位数时，Stable=1（稳定型机构投资者），否则 Stable=0（交易型机构投资者）。"
data_sources: [锐思 RESSET, 国泰安 CSMAR]
database_tables: [机构投资者持股明细]
frequency: firm-year
source_papers: [徐灿宇-2023-异质机构投资者-实地调研-财务重述]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

按持股稳定性把机构投资者划分为稳定型与交易型两类。稳定型机构投资者持股期限较长、持股份额较大，更注重公司可持续经营，治理意愿与能力较强；交易型机构投资者持股期限短、投机动机强，可能与管理层合谋掩盖坏消息。该划分属于本项目耐心资本测度路径中的 B2 框架（持股稳定性中位数法），是耐心资本股权侧时间属性的二分类操作化变体。

## Measurement

杨棉之等 (2018)、徐灿宇等 (2023) 采用以下公式：

```
SD_{i,t} = 机构投资者持股比例_{i,t} / 过去三年机构投资者持股比例的标准差_{i,t}

Stable_{i,t} = 1   if SD_{i,t} ≥ MEDIAN(SD)_{行业-年度}
              = 0   otherwise
```

其中 SD 越大代表持股比例相对其波动性越高，即持股越稳定。中位数比较按行业—年度分组进行。

样本均值（徐灿宇等 2023 深市 A 股 2013—2020 年）：Stable 均值 0.504，表明上市公司机构投资者样本中稳定型与交易型大致各占一半。

## Data Source

[[锐思 RESSET 数据库]] 提供季度 / 半年度机构投资者持股比例明细，可计算过去三年标准差；[[csmar]] 同样提供机构投资者持股数据，可作交叉验证。

## Literature Variants

- B1（持股时长法）：以机构持股最长持续期为耐心程度。
- **B2（持股稳定性中位数法，本变量）**：SD 与行业—年度中位数比较生成 0/1。代表：[[徐灿宇-2023-异质机构投资者-实地调研-财务重述]]。
- A2（标准差变体连续值）：直接以 机构持股 / 持股期标准差 作为连续耐心资本指标，再叠加债权侧。代表：[[代飞-2025-耐心资本-双元创新-管理者短视]]。
- A1（换手率分组法）：按机构投资者换手率三分位划分。

变体之间的对比：B2 转为二分类，便于 Logit 与 PSM；A2 保留连续值，便于 IV 与非线性检验。

## Construction Steps

1. 从锐思 / CSMAR 抓取每公司—季度（或半年）机构投资者总持股比例。
2. 按公司—年度聚合得年度持股比例（年末值或年均值）。
3. 对每公司—年度计算过去 3 年（含本年）持股比例的样本标准差。
4. SD = 当年持股比例 / 过去 3 年标准差。
5. 按 CSRC 行业代码（除制造业取二级，其余取一级）+ 年度分组，计算 SD 中位数。
6. SD ≥ 中位数则 Stable=1；否则 Stable=0。

## Stata Notes

```stata
* 步骤 3-4：滚动标准差与 SD
bys stkcd (year): asrol inst_hold, stat(sd) window(year 3) gen(inst_hold_sd3)
gen sd = inst_hold / inst_hold_sd3

* 步骤 5：行业—年度中位数
bys industry year: egen sd_med = median(sd)

* 步骤 6
gen stable = (sd >= sd_med) if !missing(sd, sd_med)
```

## Caveats

- 公式分母是过去三年标准差；当公司上市不足 3 年时该指标缺失，需剔除前 2 年观测。
- "行业"分类口径影响中位数划分：CSRC 大类 vs CSRC 制造业二级 vs 申万行业 → 同一公司可能跨口径切换 Stable 值。
- 该指标对持股比例的短期跳变非常敏感；解禁、增发等事件年份可能造成 SD 异常。
- 与 A2 的连续指标互补：当主回归用 OLS / Tobit 时建议用 A2；当主回归用 Logit / 需做 PSM 时 B2 更便利。
- 概念上是耐心资本的子操作化：仅刻画股权侧时间属性，不含债权侧；不能与 A2 的"股权 + 关系型债务总和"等同。

## Related

- [[patient-capital]] — 上位构念：本变量是耐心资本股权侧时间属性的 B2 操作化变体。
- [[徐灿宇-2023-异质机构投资者-实地调研-财务重述]] — 在本 wiki 中首次使用 B2 操作化。
- [[financial-restatement]] — 本变量在徐灿宇等 (2023) 中用于解释的被解释变量。
- [[site-visit]] — 与本变量构造交乘项以检验调节效应。
