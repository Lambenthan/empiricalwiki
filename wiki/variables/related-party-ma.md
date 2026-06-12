---
title: "关联并购虚拟变量（RMA）"
slug: "related-party-ma"
construct: "关联交易性质的并购事件标识"
role: control
measurement: "RMA = 1 当并购事件涉及关联交易，否则 = 0。关联交易识别依据 CSMAR 上市公司并购重组研究数据库中的关联交易标识字段。"
data_sources: [csmar]
database_tables: [上市公司并购重组研究数据库]
frequency: deal-event
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

刻画一起并购事件是否属于关联交易的二值变量。关联并购通常体现政府或大股东主导意愿，呈现"报表性重组"或利益输送特征，与非关联市场化并购在治理逻辑上差异显著。

周绍妮 (2017) 530 起国企并购样本中 RMA 均值 0.55，即 55% 为关联并购。

## Measurement

```
RMA_{deal} = 1   if 该并购事件涉及关联方交易
            = 0   otherwise
```

判定依据：CSMAR 上市公司并购重组研究数据库的"是否关联交易"字段，对应中国上市公司公告披露中的关联交易认定（参考《上市公司信息披露管理办法》《上海/深圳证券交易所股票上市规则》关联交易章节）。

## Data Source

[[csmar]] 上市公司并购重组研究数据库内含每起并购事件的关联交易标识。可与 t 年公告中的"关联交易"字段交叉核对。

## Literature Variants

- 二值标识（本变量）：周绍妮 (2017)、宋祥丞和鲁虹 (2016)、潘红波等 (2008)。
- 关联类型细分：进一步按"实际控制人主导 / 同一控制人下子公司间 / 母公司注入资产"分类。
- 关联强度：以关联方持股比例或管理层兼职数量做连续度量。

## Construction Steps

1. 从 CSMAR 并购重组库取每起并购事件的"是否关联交易"字段。
2. 与并购事件主表合并（按公告事件 ID）。
3. 与已筛选的样本（首次公告日 2010-2014、收购方为国企、并购成功等）合并。

## Stata Notes

```stata
gen RMA = (related_party == 1)
* 异质性切分
preserve
keep if RMA == 1
* 跑关联并购组回归
restore
keep if RMA == 0
* 跑非关联并购组回归
```

## Caveats

- CSMAR 关联交易标识依赖公司自报，存在低报或错报。建议与公告原文人工抽查校对。
- 周绍妮 (2017) 表 4 列 1 RMA 系数 −0.006 (n.s.)，主回归中关联并购对 ΔADJ_ROE 没有直接显著影响；其作用主要通过遮蔽机构投资者治理效应间接体现（异质性切分中可见，参见 [[related-party-ma-split]]）。
- 在子样本异质性分析中，作者去掉 RMA 这一控制变量（因子样本内 RMA 恒等），符合标准做法。
- 关联并购定义随《上市公司信息披露管理办法》多次修订而变；2014 年前后关联交易认定口径有差异，跨期研究需注意。

## Related

- 主用论文：[[周绍妮-2017-机构投资者-国企-并购绩效]]
- 用作切分：[[related-party-ma-split]]
- 配套被解释变量：[[state-soe-ma-performance]]
- 数据：[[csmar]]
