---
title: "企业韧性 (Enterprise Resilience)"
slug: "enterprise-resilience"
construct: "企业韧性"
role: dependent
measurement: "熵权法合成两个分项指标——三年内累计销售收入增长额（财务绩效增长性）+ 当年月度股票收益率的标准差（股票收益波动性，反向）。储佩佩 (2025) 的具体口径。"
data_sources: [国泰安 CSMAR]
database_tables: [月度股票收益率, 利润表, 资产负债表]
frequency: firm-year
source_papers: [储佩佩-2025-耐心资本-企业韧性]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

企业韧性指企业在受到外部冲击时具备的缓冲能力以及恢复至均衡状态的能力，是一种长期性、持续性概念，不仅表现在危机短线时间轴上，更蕴含于常态化发展的长远轨迹中。理论上是一个具有多重维度和路径依赖特征的情境变量。

## Measurement

储佩佩 (2025) 沿用陈琪和李梦函 (2024) 的财务绩效增长性 + 股票收益波动性思路：

- 分项 1（绩效增长性）：企业三年内累计销售收入增长额。数值越大代表逆势成长能力越强、韧性越强。
- 分项 2（收益波动性）：企业当年月度股票收益率的标准差。数值越小代表越稳定、韧性越强。
- 合成方式：熵权法对两个分项赋权，计算综合韧性得分 (Resilience)。

替代衡量（用作稳健性）：

- 企业股票日收益波动率（Levine et al., 2018）。

文献中其他口径（本文未采用，但作为变体提供）：

- 危机事件法（事件前一年 vs 事件后两年）：股价下跌幅度 + 时长 / ROE 变化（陈红等, 2024）。
- ESG 表现作为韧性代理（陈琪和李梦函, 2024）。
- 内部控制水平 / 管理层特质 / 政府治理 / 投资者保护制度（焦豪等 2024、侯林岐等 2024、胡海峰等 2020）。

## Data Source

[[csmar]]：

- 月度股票收益率 → 计算年内月度收益标准差。
- 利润表营业收入 → 计算三年累计销售收入增长。
- 资产负债表与利润表 → 衍生变量。

## Literature Variants

- V1（储佩佩 2025）：熵权法合成"三年累计销售收入增长 + 月度收益标准差"。
- V2（Levine et al., 2018）：股票日收益波动率。本文用作稳健性。
- V3（事件研究法）：危机前后对比，需要外生危机事件（08 金融危机、贸易战、新冠等）。
- V4（ESG 代理）：直接用第三方 ESG 评级作为韧性间接代理。

## Construction Steps

V1（储佩佩 2025）：

1. 取 CSMAR 月度股票收益率，按 (firmid, year) 分组计算月度收益标准差 sd_ret。
2. 取年度营业收入 sales，构造三年累积增长 sales_growth_3y = sales_t + sales_{t-1} + sales_{t-2} - 3×sales_{t-3}（或更标准的 sales_t - sales_{t-3}，原文为"三年内累计销售收入增长额"）。
3. 对两分项做缩尾或归一化处理。
4. 用熵权法计算两分项的客观权重，再加权合成 Resilience。注意收益波动性需取负向（韧性得分应单调递增）。

## Stata Notes

```
* 月度收益标准差
egen sd_ret = sd(monthret), by(stkcd year)

* 三年累计销售收入增长（按论文文字理解：当期与三年前的差）
xtset stkcd year
gen sales_growth_3y = sales - L3.sales

* 缩尾
winsor2 sd_ret sales_growth_3y, cuts(1 99) replace

* 熵权法合成（社区命令）
entropy_weight sales_growth_3y sd_ret_neg, gen(resilience)
```

## Caveats

- 熵权法权重对样本范围敏感，重做样本时需重算权重，结果可能微变。
- 月度收益标准差中包含的"系统性风险"成分难以分离，可能将宏观波动误归为个体韧性下降。
- 三年累积增长依赖样本期足够长，IPO 早期年份会损失观测。
- 与事件研究法相比，本指标无法精确刻画"危机响应速度"维度，仅能反映"长期均衡的稳定性"。

## Related

- 核心解释变量：[[patient-capital]]。
- 主要论文：[[储佩佩-2025-耐心资本-企业韧性]]。
- 配套机制：[[financing-constraint-mediation]] · [[innovation-persistence-mediation]] · [[governance-mediation]]。
