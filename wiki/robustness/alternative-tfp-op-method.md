---
title: "替换被解释变量：OP 法估计的全要素生产率"
slug: "alternative-tfp-op-method"
check_type: alternative_variable
purpose: "检验以 LP 法 TFP_LP 衡量的高质量发展结果是否稳健于不同 TFP 估计方法。OP（Olley-Pakes 1996）法以企业投资作为生产率代理变量，与 LP（Levinsohn-Petrin 2003）法以中间投入作为代理变量在同时性偏差处理上互为对比。"
source_papers: [李季鹏-2025-耐心资本-高质量发展]
implementation_notes: "李季鹏（2025）稳健性检验环节使用 OP 法 TFP_OP 替换基准 TFP_LP 重做表 3 基准回归。Equity 与 Debt 的估计系数仍在 1% 水平上显著为正，与基准结论一致。原文标注稳健性回归表'限于篇幅未予列示，留存备索'，未提供具体系数。"
date_updated: 2026-05-07
---

## Purpose

LP 法依赖中间投入作为生产率代理变量、保留更多样本，是中国上市公司 TFP 估计的事实标准；OP 法依赖企业投资、需剔除非正投资样本但能避开中间投入测度噪声。两者估计的 TFP 序列高度相关但绝对水平不同，互换被解释变量是检验 PC → HQD 结果是否对 TFP 估计方法敏感的标准做法。

## When To Use

- 主回归被解释变量为 LP 法 TFP，需要论证结果不被中间投入测度方式驱动时使用。
- 数据覆盖期内企业投资数据完整、非正投资样本占比可控时使用。
- 适用于以"高质量发展 / 全要素生产率 / 生产效率"为被解释变量的中文公司金融实证。

## Implementation

```stata
* OP 法 TFP 估计
prodest Y, free(L) state(K) proxy(I) method(op) va
predict tfp_op, residuals

* 重做基准回归
reghdfe tfp_op Equity controls, absorb(industry year) cluster(firmid)
reghdfe tfp_op Debt   controls, absorb(industry year) cluster(firmid)
```

数据需求：CSMAR 营业收入、员工数、固定资产净额、企业投资（构建当期资本投资 I 序列）。OP 法只能保留 I > 0 的样本，相对 LP 法会有样本损失。

## Expected Table Pattern

预期模板：基准回归两列（Equity / Debt）核心系数与符号、显著性水平与 LP 法表 3 一致。系数绝对量级可与 LP 法略有差异（OP 与 LP 估计的 TFP 标尺不同），但符号与 1% 显著性应稳健。

## Interpretation

- 若 Equity 与 Debt 系数仍 1% 显著为正：H1 不受 TFP 估计方法选择影响，结论稳健。
- 若量级或显著性发生明显变化：需进一步排查中间投入与企业投资的测度差异，或考虑生存偏差（OP 法剔除非正投资样本会强化生存偏差）。

李季鹏（2025）报告的结果为前者：OP 法替换后 Equity 与 Debt 仍 1% 显著为正。

## Caveats

- OP 法剔除非正投资样本，可能加剧生存偏差。
- 原文未列示 OP 法稳健性回归表，仅文字描述，复现验证存在障碍。
- OP 与 LP 估计的 TFP 量纲不同，绝对系数大小不可直接互比，应只关注符号与显著性。
- ACF（Ackerberg, Caves, Frazer 2015）作为 LP 法的修正版未在该文稳健性中使用，是后续可补充的稳健性方向。
