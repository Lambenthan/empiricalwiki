---
title: "国有企业并购绩效（剔除行业 ROE 变化量，ΔADJ_ROE）"
slug: "state-soe-ma-performance"
construct: "国有企业并购绩效"
role: dependent
measurement: "ΔADJ_ROE = (并购首次公告日后一年 ROE) − (并购首次公告日前一年 ROE)，再剔除同期行业 ROE 均值。"
data_sources: [csmar]
database_tables: [上市公司并购重组研究数据库, 利润表, 资产负债表]
frequency: deal-event
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

事件层（deal-event）变量，刻画一起并购事件对主并方上市公司净资产收益率（ROE）的相对改善幅度。被解释变量取并购首次公告日前后一年 ROE 差值，再减同期行业 ROE 均值，从而：(1) 控制并购前公司基本面对绩效的影响（差分形式），(2) 控制行业整体景气波动（剔除行业均值）。

周绍妮 (2017) 530 起国企并购样本中，ΔADJ_ROE 均值 −0.01、中位数 0、std 0.13、最小值 −0.41、最大值 0.36，呈现"并购绩效悖论"——国企并购整体绩效不升反降。

## Measurement

```
ROE_{i,t} = 净利润_{i,t} / 净资产_{i,t}
ROE_{ind, t} = 同年同行业（CSRC 一级或二级）所有上市公司 ROE 均值

ADJ_ROE_{i,t} = ROE_{i,t} − ROE_{ind, t}

ΔADJ_ROE_{i, deal} = ADJ_ROE_{i, post} − ADJ_ROE_{i, pre}
```

其中 pre 为并购首次公告日所在会计年度的前一年（t-1），post 为后一年（t+1）。事件单位为"deal"，同一公司可对应多起并购，每起并购作为独立观测。

## Data Source

[[csmar]] 提供：
- 并购事件（首次公告日、是否成功、并购标的类型、关联交易标识、交易金额、转让股权比例）；
- 主并方公司年度财务（净利润、净资产）；
- 行业代码（CSRC 行业分类）。

## Literature Variants

- ΔADJ_ROE（本变量）：[[周绍妮-2017-机构投资者-国企-并购绩效]] 主指标，参考李维安和李滨 (2008)、辛清泉等 (2014)。
- ΔADJ_ROA：陈仕华等 (2014) 建议；以剔除行业 ROA 的变化量替代。
- ΔADJ_EBIT：潘红波和余明桂 (2014) 建议；以剔除行业 EBIT 率的变化量替代。
- 长窗口 ΔADJ_ROE（陈仕华等 2014）：并购后两年 ADJ_ROE 均值减并购前两年 ADJ_ROE 均值，刻画长期效应。
- 市场反应类（CAR / BHAR）：本文未使用，但属国际并购文献主流。中国国企并购研究因股价噪音较大、政策事件频繁，常优先采用财务指标变化量。

## Construction Steps

1. 从 CSMAR 并购重组研究数据库筛选样本：上市公司为收购方、并购标的为股权、并购成功、非金融、非小并购等（详见 [[周绍妮-2017-机构投资者-国企-并购绩效]] 样本筛选）。
2. 取每起并购首次公告日所在年度，提取 t-1 与 t+1 年度的净利润 / 净资产计算 ROE_{pre} 与 ROE_{post}。
3. 按 CSRC 行业 × 年度计算 ROE 均值 ROE_{ind, t-1} 与 ROE_{ind, t+1}。
4. ADJ_ROE_{pre} = ROE_{pre} − ROE_{ind, t-1}；ADJ_ROE_{post} = ROE_{post} − ROE_{ind, t+1}。
5. ΔADJ_ROE = ADJ_ROE_{post} − ADJ_ROE_{pre}。
6. 上下 1% 缩尾。

## Stata Notes

```stata
* 计算行业-年度 ROE 均值
bysort industry year: egen roe_ind = mean(roe)
gen adj_roe = roe - roe_ind

* 取并购公告年的 t-1 与 t+1 ADJ_ROE
gen adj_roe_pre  = adj_roe if year == event_year - 1
gen adj_roe_post = adj_roe if year == event_year + 1

* 按 deal 事件聚合（先按 stkcd × event 折叠）
bysort stkcd event_id: egen pre  = max(adj_roe_pre)
bysort stkcd event_id: egen post = max(adj_roe_post)
gen d_adj_roe = post - pre

winsor2 d_adj_roe, replace cuts(1 99)
```

## Caveats

- 事件单位：同一公司一年可能多起并购，前后一年 ROE 一致，会产生相关观测；论文未明示如何处理 deal 内嵌套的统计相关性。
- 行业均值剔除假设行业景气在 t-1 与 t+1 之间外生于本企业并购决策；当并购集中发生于行业景气拐点附近时该假设受挑战。
- ROE 对净资产规模敏感；并购完成后净资产摊薄会拉低 ROE，可能将"会计性"分母效应误判为绩效下滑。
- "并购绩效悖论"是中国市场的稳定特征，不一定代表 ΔADJ_ROE 测算偏差；但建议同时报告 ΔADJ_ROA、ΔADJ_EBIT 作为稳健性检查（参见 [[alternative-ma-performance-measures]]）。
- 国有企业与非国有企业的 ROE 趋势不同，本变量在国企子样本中均值为负、在非国企样本可能为正；跨产权对比时需谨慎。

## Related

- 主用论文：[[周绍妮-2017-机构投资者-国企-并购绩效]]
- 替代指标：[[alternative-ma-performance-measures]]
- 关联事件特征变量：[[related-party-ma]]
- 数据来源：[[csmar]]
