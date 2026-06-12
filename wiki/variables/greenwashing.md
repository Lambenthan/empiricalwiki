---
title: "企业漂绿 (Greenwashing, GWS)"
slug: "greenwashing"
construct: "漂绿"
role: dependent
measurement: "彭博 ESG 评分（披露端，'言'）与华证 ESG 评分（实绩端，'行'）的行业内标准化差分；正值表示披露强于实绩，即漂绿程度更高"
data_sources: [彭博 ESG 评分, 华证 ESG 评分]
database_tables: [Bloomberg ESG Disclosure Score, 华证 ESG 评分]
frequency: firm-year
source_papers: [强国令-2025-耐心资本-漂绿]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

漂绿（greenwashing）指企业对外披露的环境形象与实际环境绩效之间的偏离——"言行不一"。本变量从外界监督视角出发，量化披露端与实绩端的差距，差距越大说明企业越倾向于用披露内容掩饰实质环境表现。

## Measurement

强国令 (2025) 借鉴 Yu 等 (2020) 与 Zhang (2022) 的方法（公式 1）：

GWS_{i,t} = (ESG_{dis,i,t} − \overline{ESG}_{dis}) / σ_{dis} − (ESG_{pre,i,t} − \overline{ESG}_{pre}) / σ_{pre}

其中：

- ESG_{dis,i,t}：企业 i 第 t 年的彭博 ESG 评分（披露端，反映"言"，聚焦对外披露的广度、深度、质量）。
- ESG_{pre,i,t}：企业 i 第 t 年的华证 ESG 评分（实绩端，反映"行"，聚焦实际运营中的环境管理水平与效果）。
- \overline{ESG}_{dis} 与 \overline{ESG}_{pre}：分别为彭博 ESG 与华证 ESG 评分的行业平均值。
- σ_{dis} 与 σ_{pre}：分别为两套评分在行业层面的标准差。

行业内标准化的目的是剔除不同行业 ESG 基准差异。GWS 取正值表示披露端相对行业平均的偏离高于实绩端的偏离，对应漂绿；取负值则表示"少言多行"。

## Data Source

- 披露端：Bloomberg ESG Disclosure Score（彭博 ESG 评分），需 Bloomberg 终端订阅。
- 实绩端：华证 ESG 评分（中国本土 ESG 评分体系），可通过 [[wind]] 或 CNRDS 获得。
- 行业分类：通常采用证监会 2012 版一级行业（制造业再细分为二级），以保证行业内可比。

## Literature Variants

- Yu et al. (2020) 与 Zhang (2022) 的"言行差距"标准化范式，本变量的母体方法。
- 替代度量（强国令 2025 在稳健性检验中使用）：
  - 选择性披露与象征性披露占比的几何平均（基于 ESG 报告文本）。
  - 漂绿同构指数（同业漂绿模仿程度）。
  - 企业社会责任报告的文本相似性（披露内容相似度过高视为模板化漂绿）。
- 国际文献中亦有用 ESG 争议事件数 / 监管处罚记录 / 第三方研究报告作为漂绿度量。

## Construction Steps

1. 按 stkcd × year 合并 Bloomberg ESG 评分（披露端）与华证 ESG 评分（实绩端）。
2. 按行业（industry × year）分别计算 ESG_dis 与 ESG_pre 的均值与标准差。
3. 各自做行业内标准化：z_dis = (ESG_dis − mean_dis) / sd_dis；z_pre = (ESG_pre − mean_pre) / sd_pre。
4. GWS = z_dis − z_pre。
5. 按需做 1%/99% 缩尾防极端值。

## Stata Notes

```
* 假定 ESG_dis 与 ESG_pre 已合并到主面板
egen dis_mean = mean(ESG_dis), by(industry year)
egen dis_sd   = sd(ESG_dis),   by(industry year)
egen pre_mean = mean(ESG_pre), by(industry year)
egen pre_sd   = sd(ESG_pre),   by(industry year)

gen z_dis = (ESG_dis - dis_mean) / dis_sd
gen z_pre = (ESG_pre - pre_mean) / pre_sd
gen GWS   = z_dis - z_pre
winsor2 GWS, cuts(1 99) replace
```

## Caveats

- 彭博 ESG 评分覆盖样本以国际化披露较好的大型 A 股为主，2009 年早期年份覆盖偏少；可能造成样本向头部企业偏移。
- 华证 ESG 评分的行业打分口径每年调整，跨年序列需注意版本一致性。
- 行业内标准化对小行业（< 30 家）敏感；可考虑使用证监会一级行业作为最小颗粒度。
- 标准化差分隐含"披露与实绩可比"的假设，但两套评分的子指标权重不同；解读时应说明是相对位置差异而非绝对差距。
- 该变量适合作为外部观测视角的漂绿代理；若研究焦点在内部决策，应辅以 ESG 报告文本分析变量。

## Related

- 核心来源论文：[[强国令-2025-耐心资本-漂绿]]。
- 配套核心解释变量：[[patient-capital]]（A4 框架）。
- 数据底座：[[wind]] · [[csmar]]。
- 同主题对照变量：[[exploratory-innovation]] / [[exploitative-innovation]]（同样以耐心资本为解释变量但被解释变量为创新）。
