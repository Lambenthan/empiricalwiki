---
title: "企业全要素生产率 (Total Factor Productivity, TFP)"
slug: "total-factor-productivity"
construct: "全要素生产率"
role: dependent
measurement: "基于 Cobb-Douglas 生产函数的两阶段估计：第一阶段利用中间投入数据估计生产率，第二阶段通过回归确定生产函数参数；常见方法 OLS / OP / LP，邱蓉等 (2024) 基准用 LP 法，稳健性用 OLS、OP。"
data_sources: [国泰安 CSMAR]
database_tables: [资产负债表, 利润表, 员工人数, 固定资产, 中间投入]
frequency: firm-year
source_papers: [邱蓉-2024-耐心资本-全要素生产率]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

理论构念：在劳动、资本等可观测要素投入之外，无法被这些要素直接解释的产出增量，反映企业的技术水平、管理效率与资源配置质量。Cobb-Douglas 设定下记为 Y = A · K^α · L^β（含或不含中间投入），TFP = ln A 即"剩余项"。

在邱蓉等 (2024) 的内生增长模型中，A = exp(γI − δU)，其中 I 为创新效率、U 为不确定性感知，强调 TFP 的微观可分解性。

## Measurement

学界主流估计法（鲁晓东、连玉君，2012）：

- **OLS 法**：直接对 ln Y = α₀ + α_K · ln K + α_L · ln L + ε 做 OLS，残差即 ln TFP。优点是简单；缺点是要素投入与生产率冲击同期相关，存在内生性。
- **OP 法 (Olley and Pakes, 1996)**：用企业投资作为生产率的代理变量，分两阶段估计；解决了同时性偏差，但只能保留正投资样本，损失数据。
- **LP 法 (Levinsohn and Petrin, 2003)**：用中间投入（原材料、能源等）替代投资作为代理变量，在解决内生性的同时保留更多样本，是中国上市公司 TFP 估计的事实标准。

邱蓉等 (2024) 采用：

- 基准回归：LP 法。
- 稳健性：OLS 法（变量名 TFP_OLS）和 OP 法（TFP_OP）。

## Data Source

[[csmar]] 是中国 A 股 TFP 估计的主流数据源，需要：

- 营业收入或工业增加值（产出 Y）。
- 员工人数（劳动 L）。
- 固定资产净额（资本 K）。
- 购买商品、接受劳务支付的现金或营业成本中的中间投入项（中间投入 M，仅 LP 法用）。
- 资本投资（仅 OP 法用）。

## Literature Variants

- **OLS / FE 残差**：早期文献做法。
- **OP**：保留正投资样本的 GMM 类似估计。
- **LP**：用中间投入替代投资，是国内主流。
- **ACF (Ackerberg, Caves, Frazer, 2015)**：在 LP 基础上修正了劳动系数识别问题，但中文实证使用较少。
- **GMM / 半参数法**：少数论文使用。

不同方法估计的 TFP 序列高度相关但绝对水平有差异，故论文常并列报告。

## Construction Steps

LP 法 Stata 实现（参考鲁晓东、连玉君 2012）：

1. 准备样本：剔除 ST、金融保险、关键字段缺失（产出 / 劳动 / 资本 / 中间投入）。
2. 变量构造：
   - Y = ln(营业收入)（或工业增加值，需用永续盘存法剥离中间投入）。
   - L = ln(员工人数)。
   - K = ln(固定资产净额)，可用永续盘存法做实物资本存量。
   - M = ln(中间投入)，可用"营业成本 + 销售费用 + 管理费用 − 当期折旧 − 当期工资"近似。
3. 用 `levpet Y, free(L) proxy(M) capital(K) reps(50)`（社区命令）或 `prodest Y, free(L) state(K) proxy(M) method(lp)` 估计。
4. 把估计出的 ln TFP（即残差）保存为变量 TFP，加入回归。
5. 稳健性可分别用 `regress Y L K, robust`（OLS）与 `opreg Y, free(L) state(K) proxy(I)`（OP）。

## Stata Notes

```
* LP 法（基准）
prodest Y, free(L) state(K) proxy(M) method(lp) va
predict tfp_lp, residuals

* OP 法（稳健性）
prodest Y, free(L) state(K) proxy(I) method(op) va
predict tfp_op, residuals

* OLS / FE 残差（稳健性）
reghdfe Y L K, absorb(industry year) residuals(tfp_ols)
```

注意 `prodest` 默认输出的是 ω̂_it（log productivity），即邱蓉等 (2024) 描述性统计中均值约 8.301、标准差 1.079 的口径。

## Caveats

- LP 法对"中间投入"的口径选择敏感；不同论文用"营业成本 − 折旧 − 工资"或"购买商品现金"，结果会有差异。
- 行业层面 TFP 估计需在子样本内分别估计生产函数参数（按 GICS / 证监会一级行业），否则参数同质性假设不成立。
- 上市公司样本存在生存偏差，OP 法部分缓解但不能完全消除。
- 中文实证常把 ln Y 直接作为产出，而不是工业增加值；此口径下估出的 TFP 含中间投入贡献，需谨慎与生产率核算文献比较。

## Related

- 配套核心解释变量：[[patient-capital]]。
- 主要文献：[[邱蓉-2024-耐心资本-全要素生产率]]（基准 LP，稳健性 OLS / OP）。
- 配套中介机制：[[innovation-efficiency-uncertainty-mediation]]。
