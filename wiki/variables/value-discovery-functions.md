---
title: "耐心资本的价值发现功能 (Value Discovery Functions)"
slug: "value-discovery-functions"
construct: "二级市场价值发现"
role: dependent
measurement: "李心武 (2025) 用三个独立的代理变量衡量价值发现功能：(1) AnaVis_{j,t+1} = ln(分析师当年实地调研次数 + 1)，滞前一期；(2) TOver_{j,t+1} = 公司股票年交易量 / 流通股数 ÷ 交易日天数得到的日均换手率，滞前一期；(3) RE_PEG_{j,t+1} = PEG 模型测度的股权融资成本 = sqrt(EPS_{t+2} − EPS_{t+1}) / 股价 P_t，滞前一期。"
data_sources: [国泰安 CSMAR, 上市公司年报与公告]
database_tables: [分析师调研, 股票交易, 一致预期 EPS, 股价]
frequency: firm-year
source_papers: [李心武-2025-耐心资本-数字化转型-价值发现]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

耐心资本的价值发现功能 = 耐心资本通过持仓行为，向二级市场传递企业内在价值信号，引导其他市场参与者（分析师、投资者）更多关注、交易并以更合理价格定价的能力。李心武 (2025) 把这一构念拆为三个可观测的代理变量：分析师关注、投资者交易活跃度、企业股权融资成本。

## Measurement

李心武 (2025) 的三个代理变量：

- **AnaVis_{j,t+1}（分析师实地调研）**：企业当年被分析师实地调研的次数 + 1 取自然对数，并滞前一期。代表分析师对企业的关注与信息挖掘强度（曹新伟等，2015）。
- **TOver_{j,t+1}（股票换手率）**：公司股票年交易量 / 流通股总数 ÷ 当年交易日天数 = 日均换手率，再滞前一期。代表投资者交易活跃度与股价信息含量（陈梦根、毛小元，2007）。
- **RE_PEG_{j,t+1}（股权融资成本）**：PEG 模型测度，公式：

  `RE_PEG_t = sqrt(EPS_{t+2} − EPS_{t+1}) / P_t`

  其中 EPS_{t+1}、EPS_{t+2} 为分析师一致预期每股收益，P_t 为期末股价。RE_PEG 越低代表股权融资成本越低、二级市场信息传递效率越高（曾颖、陆正飞，2006）。

## Data Source

- AnaVis：[[csmar]] 分析师调研子库 / Wind 调研记录。
- TOver：[[csmar]] 股票交易子库（年交易量、流通股数、交易日天数）。
- RE_PEG：[[csmar]] 一致预期 EPS 子库 + 股价子库。

## Literature Variants

- 价值发现作为构念在国内外公司金融文献中常用以下代理：分析师覆盖度、分析师预测准确度、股价同步性 R²、换手率、买卖价差、股权融资成本、机构投资者扎堆度。
- 李心武 (2025) 选取的 (AnaVis, TOver, RE_PEG) 组合属于 D 框架（基金持仓视角）下相对全面的三角组合，分别对应：信息挖掘端、交易端、定价端。
- 与 A/B/C 框架下的耐心资本论文不同，D 框架不把 PC 直接作为效应变量，而是通过 PC 持仓比例与数字化转型程度的交乘项检验"持仓 → 价值发现"的传导。

## Construction Steps

```text
AnaVis_{j,t+1}   = ln(visit_count_{j,t} + 1) 然后整列下移一期
TOver_{j,t+1}    = (年交易量 / 流通股数) / 交易日天数 然后整列下移一期
RE_PEG_{j,t+1}   = sqrt(F_EPS_{t+2} − F_EPS_{t+1}) / P_t 然后整列下移一期
```

## Stata Notes

```stata
gen anavis  = ln(visit_count + 1)
xtset firm year
gen AnaVis_F1 = F.anavis

gen turnover = (vol_year / float_share) / trading_days
gen TOver_F1 = F.turnover

gen RE_PEG = sqrt(eps_t2 - eps_t1) / price_year_end
gen RE_PEG_F1 = F.RE_PEG
```

## Caveats

- 三个代理变量分别捕捉不同维度，回归时应分别报告，不应合成综合得分。
- RE_PEG 在 EPS_{t+2} − EPS_{t+1} ≤ 0 时无定义，作者保留缺失观测，导致样本量降至 742,527（基线为 884,961）。
- AnaVis 仅覆盖披露调研记录的公司，存在选择性偏误；TOver 在停牌或重大资产重组样本中存在异常值，需做缩尾处理。

## Related

- variables：[[patient-capital]] · [[digital-transformation]]
- datasets：[[csmar]]
- models：[[two-way-fixed-effects-firm-year]]
- papers：[[李心武-2025-耐心资本-数字化转型-价值发现]]
