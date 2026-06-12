---
title: "替换被解释变量：ESG 评级等级（AAA—CCC）"
slug: "robustness-replace-esg-rating"
check_type: alternative_variable
purpose: "用华证 ESG 评级的离散等级（AAA—CCC）替换连续 ESG 得分作为被解释变量，验证主结论不依赖具体的连续度量方式与可能的赋值偏差"
source_papers: [唐亮-2025-耐心资本-esg表现]
implementation_notes: "唐亮 (2025) 表 9 列 1：替换被解释变量为 AAA—CCC 赋值后的 ESG 等级，PC 系数 0.794***（t = 8.348），方向与基准回归一致，1% 水平显著"
date_updated: 2026-05-07
---

## Purpose

主回归使用华证 ESG 连续得分（已做 0—1 标准化），但连续得分对评级公司的内部赋分细节高度敏感（如 130+ 底层指标的加权方式、各级阈值划分）。把被解释变量改为离散评级等级（AAA / AA / A / BBB / BB / B / CCC，对应数值 1—9 或类似阶梯赋值），验证：

- 结果是否依赖连续得分的具体口径；
- 评级等级层面（粗粒度）下耐心资本的边际效应是否依然显著。

## When To Use

- 当连续 ESG 得分由不透明合成方法生成、对底层指标加权敏感时；
- 当稳健性章节需要展示对被解释变量度量噪声的不敏感性时；
- 当评级数据库同时提供连续得分与离散等级，二者不存在严格单调对应时。

## Implementation

```stata
* 1. 把华证 ESG 等级映射为数值（线性赋值）
gen ESG_grade = .
replace ESG_grade = 9 if rating == "AAA"
replace ESG_grade = 8 if rating == "AA"
replace ESG_grade = 7 if rating == "A"
replace ESG_grade = 6 if rating == "BBB"
replace ESG_grade = 5 if rating == "BB"
replace ESG_grade = 4 if rating == "B"
replace ESG_grade = 3 if rating == "CCC"
* （部分 ESG 评级体系还包括 CC 及以下，按需扩展）

* 2. 重新估计基准模型
reghdfe ESG_grade PC $controls, absorb(industry year firmid) cluster(firmid)
```

## Expected Table Pattern

| 列 | 因变量 | PC 系数 | 显著性 |
| --- | --- | --- | --- |
| (1) | ESG 等级（AAA—CCC 赋值） | 0.794 | 1% |
| (2) | 主回归 ESG 连续得分 | 0.030 | 1% |
| (3) | 控制城市 FE 的 ESG 连续得分 | 0.030 | 1% |

只要列 (1) 系数符号与基准一致且仍显著，即可判定结论对评级度量方式稳健。

## Interpretation

- 系数大小不可直接比较：连续得分量纲 0—1，等级量纲 1—9，倍数差异约 30 倍即正常。重点是符号与显著性。
- 控制变量系数方向应与主回归一致，否则提示替换变量与主变量在测度上有结构性偏差。
- 若等级回归中 PC 系数突然不显著或符号反向，应回到原始评级数据检查等级阈值的稳定性（如华证 2018 年方法迭代的影响）。

## Caveats

- 把序数评级当作基数变量（线性赋值 1—9）隐含等级间距相等的假设，但实际上 AAA—AA 与 BB—B 的差距可能不对称。更严格的做法是用有序 Probit / Logit 模型，但牺牲 FE 估计便利。
- 若仅有少数公司处于极端等级（AAA 或 CCC），结果可能被极值点驱动，需配合极值剔除或分位数稳健性。
- 等级映射的方向（高分对应高 ESG 还是低分对应高 ESG）不能在不同评级机构间机械迁移；商道融绿、Wind 等口径各异。
