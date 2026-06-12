---
title: "ESG 表现 (ESG Performance)"
slug: "esg-performance"
construct: "企业 ESG 表现"
role: dependent
measurement: "主流做法是采用第三方 ESG 评级机构给出的综合得分或评级。在中国 A 股市场最常用的是华证 ESG 评级（取连续得分 0—100 或离散等级 AAA—CCC 赋值），也可拆为 E、S、G 三个分项分别测度。"
data_sources: [华证 ESG 评级, CSMAR ESG, Wind ESG, 商道融绿]
database_tables: [华证 ESG 季度评分, 华证 ESG 等级, ESG 三分项指标]
frequency: firm-year（按季度评分聚合至年度）
source_papers: [唐亮-2025-耐心资本-esg表现]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

理论构念：企业在环境（Environmental）、社会责任（Social）、公司治理（Governance）三个维度的综合可持续表现。它衡量企业除短期财务回报之外、对长期价值与利益相关者（员工、供应商、社区、监管者、投资者）的综合责任履行。

## Measurement

操作化分两类：

- 综合评分：第三方 ESG 评级机构基于上市公司公开披露、媒体监测、政策合规、舆情等数据，按 130+ 底层指标合成一个综合得分。常见连续口径 0—100，或离散等级 AAA / AA / A / BBB / BB / B / CCC（赋 9—1 分或类似数值）。
- 三分项：分别取 E-score、S-score、G-score 分项评分，做单独回归以辨认耐心资本 / 治理结构对哪一维度影响更显著。

## Data Source

- 华证 ESG 评级：覆盖全部 A 股，2009 年起按季度更新，3 个一级 + 14 个二级 + 26 个三级 + 130+ 底层指标。详见 [[hua-zheng-esg]]。
- 商道融绿（SynTao Green Finance）：早期国内重要 ESG 数据提供方。
- 万得 ESG（Wind）：综合多家评级数据并自建 ESG 评分。
- 国泰安 [[csmar]]：CSMAR ESG 子库。

## Literature Variants

不同论文对 ESG 表现的具体测度存在分歧，记录已 ingest 论文的 variants：

- 唐亮 (2025) 测度（A1 框架配套）：以华证 ESG 评级给出的 ESG 得分作为 ESG 主指标（在描述性统计中已做 0—1 标准化，均值 0.735、标准差 0.043）。稳健性中以 ESG 等级（AAA—CCC 赋值）替换连续得分。分项回归直接取 E-score、S-score、G-score。来源：[[唐亮-2025-耐心资本-esg表现]]。
- *预留位置：李思飞 (2025) ESG 测度待 Batch 4 ingest 后补充。*

## Construction Steps

唐亮 (2025) 的具体做法：

1. 从华证 ESG 评级数据库下载样本期内全部上市公司季度 ESG 得分。
2. 按公司-年度做平均或取年末值，得到 firm-year 面板。
3. 对得分做线性标准化（0—1）以便于与控制变量量纲匹配；如使用稳健性版本，则按 AAA—CCC 等级赋值离散变量。
4. 三分项 E-score、S-score、G-score 分别独立保存，用于分项回归。

## Stata Notes

```stata
* 主回归：连续 ESG 得分
reghdfe ESG PC $controls, absorb(industry year firmid) cluster(firmid)

* 稳健性：替换为评级等级（AAA=9, AA=8, ..., CCC=1）
reghdfe ESG_grade PC $controls, absorb(industry year firmid) cluster(firmid)

* 分项回归
foreach v in E_score S_score G_score {
    reghdfe `v' PC $controls, absorb(industry year firmid) cluster(firmid)
}
```

## Caveats

- 不同评级机构对同一公司的评分相关性并不高（Berg, Kölbel, Rigobon 2022 文献中称为 "ESG rating divergence"），主回归选定一家评级数据库后需在稳健性中替换另一家。
- 华证 ESG 评级体系自身在 2018 年前后存在方法迭代，时间序列连续性需检查。
- ESG 得分高度内生：经营好、合规度高、信息披露规范的企业天然得分高，与耐心资本可能存在反向因果，主分析需配合工具变量或滞后处理。
- 描述性统计若做了 0—1 标准化，需明确说明，否则系数解读可能误差一个数量级。

## Related

- 配套数据库：[[hua-zheng-esg]] · [[csmar]] · [[wind]] · [[cnrds]]。
- 与本变量并列的可持续相关变量：[[environmental-performance]] · [[green-transformation]] · [[greenwashing]]。
- 已 ingest 来源论文：[[唐亮-2025-耐心资本-esg表现]]。
