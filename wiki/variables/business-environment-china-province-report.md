---
title: "营商环境（《中国省份营商环境研究报告》指数, BE）"
slug: "business-environment-china-province-report"
construct: "营商环境"
role: moderator
measurement: "省份-年度营商环境综合指数。原始数据取自《中国省份营商环境研究报告》（白钰、冯均科 2024 路径），按企业注册地省份-年份匹配；缺失年份采用线性插值法补充。"
data_sources: [中国省份营商环境研究报告]
database_tables: []
frequency: province-year
source_papers: [杨芳-2025-耐心资本-制造业-新质生产力-营商环境]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

营商环境作为企业在准入、生产经营、退出过程中涉及的政务环境、市场环境、法治环境、人文环境等相关外部因素和条件的总和（杨芳等，2025）。本变量作为耐心资本对制造业企业新质生产力提升作用的调节变量。

杨芳 (2025) 强调营商环境优化主要包括三个维度：市场环境、法治环境、国际环境。

## Measurement

借鉴白钰、冯均科 (2024) 的研究：

1. 以各年份的《中国省份营商环境研究报告》作为原始数据，取省份-年度营商环境综合指数。
2. 对缺失年份的数据采用线性插值法补充。
3. 按企业注册地省份-年份与企业-年度面板合并。

杨芳 (2025) 文中未列出 BE 描述性统计的具体均值与标准差，仅在表 5 列 (5)-(6) 报告调节效应：c.Wd × c.BE 系数 2.2057***（t = 9.3451），c.Pc × c.BE 系数 0.3597***（t = 9.2721），均在 1% 水平显著为正。

## Data Source

《中国省份营商环境研究报告》：由相关研究机构发布的年度报告，按省份提供营商环境综合得分。具体发布机构与覆盖年份原文未明，需结合白钰、冯均科 (2024) 原文与最新年度版本核对。

## Literature Variants

- 《中国省份营商环境研究报告》指数（本变量）：白钰、冯均科 (2024) 路径，使用《研究报告》综合得分，缺失年份线性插值。
- 王小鲁等《中国分省份市场化指数报告》（[[business-environment-marketization]]）：谢婷婷 (2025) 采用，覆盖 5 个一级指标（政府与市场关系、非国有经济发展、产品市场发育、要素市场发育、市场中介组织发育）；谢婷婷 (2025) 样本均值 0.33、SD 0.15。
- 世界银行营商环境指数：仅有省会城市数据，时间序列短。
- 各府级营商环境指数（粤港澳大湾区、长三角等）：覆盖范围窄。

> 杨芳 (2025) 与谢婷婷 (2025) 均使用"营商环境"概念但口径完全不同：杨芳采用《中国省份营商环境研究报告》综合指数 + 线性插值，谢婷婷使用王小鲁市场化指数。两者构造维度、数值范围与外推策略均存在差异，跨论文比较时不可互换。

## Construction Steps

1. 从《中国省份营商环境研究报告》的年度版本中抽取省份-年度营商环境综合得分。
2. 对原始报告未覆盖的年份，使用相邻年份做线性插值：BE(t) = BE(t-1) + (BE(t+1) - BE(t-1)) × ((t - (t-1)) / ((t+1) - (t-1)))。
3. 按企业注册地省份与企业-年度面板按 (province, year) 合并。
4. 调节效应模型中构造交互项：`gen Wd_BE = Wd × BE`、`gen Pc_BE = Pc × BE`。
5. 滞后一期处理与主解释变量保持一致：杨芳 (2025) 模型 (3) 中 Pa 与 BE 均取滞后一期。

## Stata Notes

```stata
* 合并营商环境指数
merge m:1 province year using business_env_report.dta, keep(3) nogen

* 构造交互项
gen Wd_BE = Wd * BE
gen Pc_BE = Pc * BE

* 调节效应（杨芳 2025 模型 3 / 表 5 列 5-6）
xtset stkcd year
reghdfe Npro L.Wd L.BE L.Wd_BE controls, absorb(industry year)
reghdfe Npro L.Pc L.BE L.Pc_BE controls, absorb(industry year)
```

## Caveats

- 报告原始数据并非每年完整覆盖所有省份，线性插值会平滑短期政策冲击；建议在稳健性检验中报告"剔除插值年份"子样本结果。
- 省级层面口径较粗，无法捕捉同省内部地市差异（北京 vs 河北、上海 vs 安徽差异巨大）。
- 与企业注册地的匹配可能与企业实际经营地不一致（尤其总部 vs 主要生产地分离的制造业企业）。
- 与控制变量（GDP、ROA 区域均值、市场化程度）共线性较强，使用时需做共线性诊断。
- 调节效应的解释边界条件：BE 与 Pa 都可能存在内生性（高营商环境省份本就吸引耐心资本），c.Pa × c.BE 的因果解释需谨慎。
- 数据可获得性：《中国省份营商环境研究报告》非公开数据库，需通过白钰、冯均科 (2024) 引用线索或直接联系发布机构获取。

## Related

- 互补口径：[[business-environment-marketization]] —— 王小鲁市场化指数路径，谢婷婷 (2025) 采用。
- 调节对象：[[patient-capital]] / [[stable-institutional-investors-turnover]] / [[relational-debt-total-long-debt-ratio]]。
- 被调节的 outcome：[[new-quality-productive-forces]]。
- 主用论文：[[杨芳-2025-耐心资本-制造业-新质生产力-营商环境]]。
