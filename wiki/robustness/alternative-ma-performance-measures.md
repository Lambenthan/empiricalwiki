---
title: "并购绩效替代度量稳健性（ΔADJ_ROA / ΔADJ_EBIT / 长窗口 ADJ_ROE）"
slug: "alternative-ma-performance-measures"
check_type: alternative_variable
purpose: "检验主回归对被解释变量定义的敏感性。原 ΔADJ_ROE 以 ROE 差分衡量并购绩效，替代指标包括 ΔADJ_ROA（陈仕华等 2014）、ΔADJ_EBIT（潘红波和余明桂 2014）、并购前后两年 ADJ_ROE 长窗口均值差。"
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
implementation_notes: "周绍妮 (2017) 正文叙述结果未发生实质性改变，未列单独表格；具体系数与显著性仅文字披露"
date_updated: 2026-05-07
---

## Purpose

ΔADJ_ROE 在分子分母上对净资产摊薄敏感（并购完成后净资产被稀释会拉低 ROE），可能将"会计性"分母效应误判为绩效下滑。引入三类替代度量：

1. ΔADJ_ROA = 剔除行业 ROA 的并购前后一年差额（陈仕华等 2014）；
2. ΔADJ_EBIT = 剔除行业 EBIT / 总资产的并购前后一年差额（潘红波和余明桂 2014）；
3. 长窗口 ADJ_ROE：并购后两年 ADJ_ROE 均值 − 并购前两年 ADJ_ROE 均值（陈仕华 2014）。

三种指标分别从分母（总资产 vs 净资产）、利润口径（净利润 vs 息税前利润）、时间窗口（1 年 vs 2 年）三个方向校验主结论稳健性。

## When To Use

- 主结论涉及绩效相关被解释变量；
- 担心被解释变量构造方式（差分基础、行业调整方法、时间窗口）影响结论；
- 同时希望验证短期市场反应外的"会计绩效"层面是否一致。

## Implementation

```stata
* ΔADJ_ROA
bysort industry year: egen roa_ind = mean(roa)
gen adj_roa = roa - roa_ind
gen adj_roa_pre  = adj_roa if year == event_year - 1
gen adj_roa_post = adj_roa if year == event_year + 1
bysort stkcd event_id: egen pre_a  = max(adj_roa_pre)
bysort stkcd event_id: egen post_a = max(adj_roa_post)
gen d_adj_roa = post_a - pre_a

* ΔADJ_EBIT
gen ebit_rate = ebit / total_assets
bysort industry year: egen ebit_ind = mean(ebit_rate)
gen adj_ebit = ebit_rate - ebit_ind
* 同样按事件前后一年差分

* 长窗口 ADJ_ROE：限于 2010-2013 年并购事件（保证 t+2 数据可得）
gen adj_roe_avg_pre  = (L1.adj_roe + L2.adj_roe) / 2
gen adj_roe_avg_post = (F1.adj_roe + F2.adj_roe) / 2
gen d_adj_roe_long = adj_roe_avg_post - adj_roe_avg_pre

* 三轮替换主回归被解释变量
foreach y of varlist d_adj_roa d_adj_ebit d_adj_roe_long {
    reg `y' STABLEINS TRANSINS SH1 ID LEV CASH RMA PT SIZE ROA i.year, robust
}
```

## Expected Table Pattern

每行替换一种被解释变量、报告 STABLEINS、TRANSINS 系数 + 显著性 + R²；与主表 [表 4 列 1] 对照。

## Interpretation

- 周绍妮 (2017) 报告"前文结论并未发生实质性改变"，即三种替代被解释变量下 TRANSINS 仍显著为正、STABLEINS 仍不显著；
- 论文未公布具体系数，复现透明度受限；本项目复现时建议补全表格。

## Caveats

- 长窗口 ADJ_ROE 限于 2010-2013 年发生的并购事件（保证 t+2 数据可得），样本量减少 117 起（2014 年并购全部剔除）；
- ΔADJ_ROA 与 ΔADJ_ROE 高度相关（两者分子均为净利润），交叉验证力度有限；
- ΔADJ_EBIT 排除了利息与税收的影响，更接近主营经营效率，但忽视并购后的资本结构变化（高杠杆并购后利息支出增加是真实经营负担）；
- 论文未单独列表，仅文字披露"结果稳健"，未提供具体系数 / 显著性 / 样本量；可作为本项目复现时增强透明度的补充。

## Related

- 主用论文：[[周绍妮-2017-机构投资者-国企-并购绩效]]
- 主回归被解释变量：[[state-soe-ma-performance]]
- 主回归模型：[[ols-cross-section-ma-event]]
