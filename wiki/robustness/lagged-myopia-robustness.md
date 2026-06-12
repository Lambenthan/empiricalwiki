---
title: "滞后一期短视主义指标稳健性"
slug: "lagged-myopia-robustness"
check_type: lagged_variable
purpose: "缓解管理者短视与企业长期投资同期相关 / 反向因果导致的内生性"
source_papers: [胡楠-2021-管理者短视主义-长期投资-文本分析]
implementation_notes: "用 Myopia_Index(t-1) 替换主回归中的 Myopia_Index(t)，其余设定不变"
date_updated: 2026-05-07
---

## Purpose

主回归用同期的 Myopia_Index 与 Capex/R&D 配对，存在两类风险：

1. 反向因果：当年的长期投资行为可能反过来影响管理者在 MD&A 中的短期视域措辞（例如压力增大时使用更多"尽快"、"压力"等词）。
2. 同期共变：当期不可观测冲击同时驱动 MD&A 措辞与投资决策。

## When To Use

- 当核心解释变量来自文本，而被解释变量来自财务报表，且二者出自同一报告期时。
- 当作者无可用工具变量但希望弱化反向因果指控时。
- 与 [[two-stage-residual-inclusion]] 并行使用更稳健。

## Implementation

胡楠等 (2021) 表 6 第 (2)、(4) 列：

```stata
xtset stkcd year
reghdfe Capex L.Myopia_Index controls, absorb(industry year) cluster(stkcd)
reghdfe RD L.Myopia_Index controls, absorb(industry year) cluster(stkcd)
```

## Expected Table Pattern

- L.Myopia_Index → Capex 系数 -0.017，t = -2.46（5%）。
- L.Myopia_Index → R&D 系数 -0.012，t = -2.77（1%）。
- 与同期回归（系数 -0.018 与 -0.014）符号、量级、显著性保持高度一致 → 结果对反向因果稳健。

## Interpretation

若滞后系数与同期系数差异巨大或符号反转，则警示当期回归被反向因果污染；本论文中两者高度吻合，表明 Myopia_Index 对长期投资的预测力跨期成立。

## Caveats

- 滞后只能弱化反向因果，不能根除（若反向因果具有跨期持续性仍存在偏误）。
- 滞后版本会损失第一年观测；样本量需注意保持。
- 与 [[two-stage-residual-inclusion]]、[[firm-fixed-effects]] 并行使用更稳健。

## Related

- 主用例：[[胡楠-2021-管理者短视主义-长期投资-文本分析]]
- 配套：[[two-stage-residual-inclusion]]
