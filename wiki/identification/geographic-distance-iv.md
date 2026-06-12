---
title: "金融中心地理距离工具变量"
slug: "geographic-distance-iv"
strategy_type: iv
source_papers: [邱蓉-2024-耐心资本-全要素生产率]
assumptions:
  - "地理位置由自然条件外生决定，不直接决定企业全要素生产率（排他性）。"
  - "距金融中心越近，企业获取金融服务越便利，越容易吸引到长期资金、形成耐心资本（相关性）。"
  - "上市年限对距离工具变量的乘子作用反映了'获取金融服务的累积曝光时间'。"
threats:
  - "金融中心同时是产业、人才、信息聚集地，距离可能直接影响 TFP（排他性受质疑）。"
  - "上市年限本身可能与 TFP 相关（生存偏差、企业成熟度），导致 IV2 = (1/距离) × 滞后上市年限 仍残留内生性。"
  - "高铁、互联网时代下'地理距离'的经济含义已经被压缩，工具强度可能下降。"
implementation_notes: "IV2 = (各企业到上海、深圳金融中心的加权距离的倒数) × (滞后一期上市年限)；与 IV1 = Pat 滞后一期 共同构成 2SLS 双工具，可做过度识别检验。"
date_updated: 2026-05-07
---

## Identification Problem

耐心资本与企业全要素生产率之间存在双向因果：高生产率的企业更容易吸引长期投资者形成耐心资本，反过来耐心资本又提升生产率。直接 OLS 估计的 Pat 系数包含了反向因果偏差。固定效应只能控制时不变异质性，无法解决同期反向因果。

## Strategy

构造一个与耐心资本相关、但只通过耐心资本影响 TFP 的外生变量作为工具变量。邱蓉等 (2024) 借鉴熊灵等 (2023)、邱蓉等 (2024) 的做法构造空间维度的 IV2：

```
distance_weighted_i = (distance_to_shanghai_i + distance_to_shenzhen_i) / 2
IV2_it = (1 / distance_weighted_i) × Age_(it−1)
```

逻辑：

- 上海、深圳是中国两大金融中心，集聚了大量长期投资者（公募、社保、保险、QFII 等）。
- 距金融中心越近，企业获取这些长期资金的成本越低，越容易形成耐心资本。
- 地理距离由自然条件决定，外生于企业生产率。
- 乘以上市年限是为引入时间维度变异（纯空间距离不随时间变化，无法在固定效应模型中识别）。

与 IV2 并用：IV1 = Pat 滞后一期（时间维度）。两个工具共同识别 → 过度识别检验。

## Key Assumptions

1. **相关性**：距金融中心近 + 上市年限长 → 耐心资本水平高。表 6 第一阶段 IV2 系数 0.518***（t = 6.09），F = 37.13，强工具。
2. **排他性**：距金融中心的距离不直接影响 TFP，只通过耐心资本渠道影响 TFP。这是关键且较弱的假设。
3. **稳定性**：距离 × 上市年限的工具有效性在样本期内稳定。

## Implementation

```
* 步骤 1：准备城市经纬度数据
import delimited "city_coords.csv", clear  // 城市名 + 经度 + 纬度

* 步骤 2：计算企业所在城市到上海、深圳的球面距离（haversine）
gen dist_sh = haversine(lng_firm, lat_firm, 121.473, 31.230)
gen dist_sz = haversine(lng_firm, lat_firm, 114.057, 22.543)
gen dist_avg = (dist_sh + dist_sz) / 2
gen dist_inv = 1 / dist_avg

* 步骤 3：构造 IV2
xtset firmid year
gen iv2 = dist_inv * L.age_yrs

* 步骤 4：2SLS
ivreghdfe TFP (Pat = L.Pat iv2) L.Fin L.Age L.Roa L.Growth L.Top1, ///
    absorb(firmid year) cluster(firmid) first
```

## Diagnostics

- 弱工具变量：第一阶段 F 统计量。表 6 报告 IV2 第一阶段 F = 37.13，远高于经验阈值 10。
- 过度识别：Sargan / Hansen J 检验。原文报告"两个工具变量均通过了过度识别检验"，未列出 J 统计量。
- 排他性：邱蓉等 (2024) 用文字论证，未做正式排他性检验（本质上 IV 排他性不可直接检验）。

## Limitations

- 地理距离的工具有效性在数字金融时代可能下降：互联网券商、数字银行、远程路演等让地理距离的"信息成本"含义被削弱。
- IV2 包含上市年限，而上市年限本身与企业成熟度、生存偏差、规模相关，可能违反排他性。
- 第二阶段 Pat 系数 311.36（IV2）显著大于基准 1.827 与 IV1 的 15.879，可能反映的是对"被金融中心地理距离影响的子样本"的局部平均处理效应（LATE），而非总体 ATE，使用时需谨慎解释。
- 未做排他性正式检验（如 placebo IV、bound analysis），是本识别策略的主要弱项。
