---
title: "企业高质量发展 (High-Quality Development, HQD)"
slug: "high-quality-development"
construct: "企业高质量发展"
role: dependent
measurement: "高质量发展是以可持续发展、生产效率提升与创新能力为核心的发展范式（黄速建等 2018）。中文实证文献以全要素生产率作为单一代理：李季鹏（2025）基准回归用 LP（Levinsohn-Petrin）法估计 TFP_LP，稳健性用 OP（Olley-Pakes）法估计 TFP_OP；亦有文献采用熵值法对盈利、创新、绿色、共享等多维度指标合成综合得分。"
data_sources: [国泰安 CSMAR]
database_tables: [资产负债表, 利润表, 员工人数, 固定资产, 中间投入]
frequency: firm-year
source_papers: [李季鹏-2025-耐心资本-高质量发展]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

理论构念：以高效率、高层次、持续创新为核心，旨在实现长期稳定的经济和社会价值创造的发展范式（黄速建等 2018）。在李季鹏（2025）的论述中，高质量发展强调"可持续发展基础上通过提高生产效率和创新能力实现企业的长期稳定发展"。该构念关注的不是当期产出而是潜在的长期价值创造能力。

## Measurement

中文实证文献存在两条主要操作化路径：

- 单一代理路径：以全要素生产率（[[total-factor-productivity]]）替代企业高质量发展。逻辑是 TFP 既反映当前产出与效率，又涵盖企业的长期发展潜力。这是李季鹏（2025）以及多数中文公司金融文献的做法。
- 多维合成路径：以熵值法对盈利能力、创新能力、绿色发展、共享发展、协调发展等多维度指标合成综合得分。该路径在区域经济与产业层面较常见。

李季鹏（2025）采用单一代理路径：

- 基准回归：使用 LP（Levinsohn-Petrin）法估计的 TFP_LP，参考苏启林和伍静（2024）。
- 稳健性检验：用 OP（Olley-Pakes）法估计的 TFP_OP 替代 LP 法 TFP_LP 重做基准回归。

样本（N=11039）描述性统计：均值 8.612，标准差 1.078，最小值 6.268，中位数 8.520，最大值 11.343。

## Data Source

[[csmar]] 提供 TFP 估计所需的全部输入：营业收入（产出）、员工人数（劳动）、固定资产净额（资本）、中间投入（LP 法）、企业投资（OP 法）。具体口径见 [[total-factor-productivity]]。

## Literature Variants

- LP 单一代理：李季鹏（2025）基准。
- OP 单一代理：李季鹏（2025）稳健性。
- OLS 残差法：早期文献做法，存在同时性偏差。
- ACF 修正：在 LP 基础上修正劳动系数识别问题，中文实证使用较少。
- 熵值法多维合成：盈利能力 × 创新能力 × 绿色发展 × 协调发展 × 开放发展 × 共享发展 等子维度合成。

不同测度的 TFP 序列高度相关但绝对水平有差异，单一代理与多维合成两条路径在实证结论上是否一致仍是开放问题。

## Construction Steps

LP 单一代理（李季鹏 2025 基准）：

1. 准备样本：剔除金融业、ST/*ST、资不抵债、缺失值。
2. 变量构造：Y = ln(营业收入)；L = ln(员工人数)；K = ln(固定资产净额)；M = ln(中间投入)（"营业成本 + 销售费用 + 管理费用 − 当期折旧 − 当期工资"近似）。
3. Stata 命令：`prodest Y, free(L) state(K) proxy(M) method(lp) va`，`predict tfp_lp, residuals`。
4. tfp_lp 直接作为被解释变量进入回归。

稳健性 OP 法步骤同上，仅将 `method(lp)` 换成 `method(op)`，proxy 变量改用企业投资 I。

## Stata Notes

```
* 基准：LP 法
prodest Y, free(L) state(K) proxy(M) method(lp) va
predict tfp_lp, residuals
rename tfp_lp TFP_LP

* 稳健性：OP 法
prodest Y, free(L) state(K) proxy(I) method(op) va
predict tfp_op, residuals
rename tfp_op TFP_OP
```

## Caveats

- 单一代理路径假设 TFP 充分概括"高质量"。当研究问题涉及绿色 / 共享 / 协调维度时，TFP 可能漏掉关键变化，需要熵值法多维合成。
- LP 与 OP 估计对中间投入 / 投资口径敏感，结果绝对水平不可直接互比，但相关性应足够高。
- 上市公司样本存在生存偏差。
- 中文实证常将 ln(营业收入) 直接作为产出，与生产率核算文献的"工业增加值"口径不一致，需谨慎跨文献比较。

## Related

- 配套核心解释变量：[[patient-capital]]。
- 上位代理：[[total-factor-productivity]]（本变量在李季鹏 2025 中即等价于 LP 法 TFP）。
- 主要文献：[[李季鹏-2025-耐心资本-高质量发展]]（基准 LP，稳健性 OP）；[[邱蓉-2024-耐心资本-全要素生产率]]（PC → TFP，与本变量在测度路径上一致）。
- 配套中介机制：[[information-asymmetry-mediation]] · [[agency-cost-mediation]]。
