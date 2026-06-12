---
title: "动态能力 (Dynamic Capability, DC)"
slug: "dynamic-capability"
construct: "动态能力"
role: mediator
measurement: "三维度组合：吸收能力 AC = R&D / 营业收入；创新能力 IC = 标准化(研发投入强度) + 标准化(技术人员占比)；适应能力 AA = − 变异系数(R&D, 资本支出, 广告费)"
data_sources: [国泰安 CSMAR, 中国研究数据服务平台 CNRDS]
database_tables: [研发投入表, 利润表, 财务附注]
frequency: firm-year
source_papers: [谢婷婷-2025-耐心资本-动态能力-绿色转型]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

动态能力指企业为适应快速变化的市场环境，通过系统整合、构建和重新配置内外部资源以保持竞争优势的能力（Teece, Pisano & Shuen, 1997；Wang & Ahmed, 2007）。在 Wang & Ahmed (2007) 框架下，动态能力分为吸收能力、创新能力与适应能力三个维度。

谢婷婷 (2025) 在论文中将动态能力定位为耐心资本影响企业绿色转型的中介变量，但论文未在变量分类表中单独标注其角色（控制 / 中介 / 调节）。从理论模型与中介效应模型看，动态能力的实际角色是**中介变量**。

## Measurement

借鉴杨林等 (2020) 的测度方法，分三个维度独立测算：

- 吸收能力 AC = 年度研发支出 / 营业收入。
- 创新能力 IC：选取年度研发投入强度（R&D / 营收）与技术人员占比（技术人员数 / 员工总数）两个指标，分别按 z-score 标准化后加总得到综合值。
- 适应能力 AA：计算企业年度研发支出、资本支出、广告费三种支出的变异系数（CV），并取负号（保证 AA 越大代表资源分配越灵活，与适应能力正相关）。

原文未明确变异系数的计算窗口（企业内时间序列 vs 行业-年度截面）；复现时需作者补充。

## Data Source

[[csmar]] 财务报表中的研发支出、营业收入、资本支出、广告费明细。技术人员占比与员工构成可来自 CSMAR 公司治理表或上市公司年报"员工情况"附注。中介变量数据辅助来源 [[cnrds]]（中国研究数据服务平台）。

## Literature Variants

- 杨林等 (2020) 三维度（吸收 / 创新 / 适应）：本文采用。
- Teece (2007) 三维度：感知（sensing）、把握（seizing）、重构（reconfiguring），多用于案例与问卷研究，财务数据难以直接对应。
- 单维度替代：仅用 R&D 强度衡量创新能力，或用非财务指标（专利、新产品收入比）替代。
- 综合熵值法：将多个动态能力子指标用熵值法合成单一得分，未在本文使用。

## Construction Steps

吸收能力（AC）：
1. 取 R&D 支出与营业收入（CSMAR 财务报表）。
2. `gen ac = rd / revenue`。

创新能力（IC）：
1. 计算研发投入强度：`gen rd_intensity = rd / revenue`。
2. 计算技术人员占比：`gen tech_share = tech_emp / total_emp`。
3. 分别标准化：`egen rd_z = std(rd_intensity); egen tech_z = std(tech_share)`。
4. 加总：`gen ic = rd_z + tech_z`。

适应能力（AA）：
1. 取年度研发支出、资本支出、广告费三个变量。
2. 计算三个变量的变异系数（具体窗口未在论文中明确）。
3. `gen aa = - cv_value`。

## Stata Notes

```
* 吸收能力
gen ac = rd / revenue

* 创新能力
gen rd_intensity = rd / revenue
gen tech_share = tech_emp / total_emp
egen rd_z = std(rd_intensity)
egen tech_z = std(tech_share)
gen ic = rd_z + tech_z

* 适应能力（窗口需明确，下例为企业层面跨变量截面 CV）
egen mean_3 = rowmean(rd capex ad)
egen sd_3 = rowsd(rd capex ad)
gen aa = - sd_3 / mean_3

* 中介检验：表 6 列 (1)(2)
reghdfe ac PC controls, absorb(firmid year) cluster(firmid)
reghdfe green PC ac controls, absorb(firmid year) cluster(firmid)
```

## Caveats

- 三个维度子指标量纲不一致，IC 标准化前需处理极端值（缩尾），否则 z-score 易被异常值主导。
- 适应能力的变异系数窗口选择对结果影响极大（企业-年度截面 CV vs 企业内时间序列 CV vs 行业 CV），原文未明示，需自行选择并做稳健性。
- 三个维度间相关性可能较高，逐步法中介检验易出现共线性，可考虑用 Bootstrap 中介检验。
- 杨林等 (2020) 原文用于战略突变研究，迁移到绿色转型场景需检验外部效度。

## Related

- 起作用的核心解释变量：[[patient-capital]]（耐心资本）。
- 被中介解释的目标：[[green-transformation]]（绿色转型）。
- 关联机制页面：[[dynamic-capability-mediation]]。
- 来源论文：[[谢婷婷-2025-耐心资本-动态能力-绿色转型]]。
