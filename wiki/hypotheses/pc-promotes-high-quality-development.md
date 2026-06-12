---
title: "H1：耐心资本能够促进企业高质量发展"
slug: "pc-promotes-high-quality-development"
status: literature_supported
mechanism: "耐心资本通过缓解信息不对称（[[information-asymmetry-mediation]]）与降低第一类代理成本（[[agency-cost-mediation]]）两条平行通道，提升企业生产效率与创新能力，进而推动以 TFP 为代理的高质量发展"
expected_sign: "正"
source_papers: [李季鹏-2025-耐心资本-高质量发展]
date_updated: 2026-05-07
---

## Hypothesis

H1：耐心资本（含战略型股权 Equity 与关系型债权 Debt 两条子路径）能够促进企业高质量发展（以 LP 法 TFP 衡量）。

## Literature Basis

- 股东积极主义理论：耐心资本投资者具有长期稳定性，更看重企业的长期发展潜力而非短期收益，会更积极地参与公司治理（李向前 2002），减少管理者机会主义行为。
- 信息不对称理论：耐心资本与企业建立长期合作关系，企业发展直接决定投资者利益，因而采取措施缓解管理层与外部投资者之间的信息不对称，帮助企业做出更优质的决策（参 [[information-asymmetry-mediation]]）。
- 缺乏耐心资本对企业发展不利的早期论证（William 2011）。
- 高质量发展定义：以高效、高层次、持续创新为核心，长期稳定的经济和社会价值创造（黄速建等 2018）。

## Testable Model

- (1) TFP_LP_it = α₀ + α₁·Equity_it + α₂·Controls + λ + T + ε_it，预期 α₁ > 0。
- (2) TFP_LP_it = α₀ + α₁·Debt_it + α₂·Controls + λ + T + ε_it，预期 α₁ > 0。

模型 → [[two-way-fixed-effects-industry-year]]，行业 + 年份双向固定效应。

## Evidence

来自 [[李季鹏-2025-耐心资本-高质量发展]]（表 3，N=11039）：

- 加控制变量后：Equity 系数 1.775***（se=0.049），Debt 系数 0.408***（se=0.069），均 1% 显著为正，方向与预期一致。
- 不加控制变量：Equity 系数 1.845***（se=0.046），Debt 系数 0.199***（se=0.063），方向稳定。
- 战略型股权的估计系数远大于关系型债权，作者据此认定战略型股权在 PC 促进高质量发展中作用更大。
- 稳健性 1：替换被解释变量为 OP 法 TFP，结论不变。 → [[alternative-tfp-op-method]]
- 稳健性 2：剔除 2015 年战略型股权样本（A 股市场异常波动），结论不变。
- 内生性：以同行业其他企业 PC 均值为 IV ([[iv-industry-mean-pc-excluding-self]]) 做 [[instrumental-variable-2sls]]，第一阶段 F 值（Equity: 1207.4 / Debt: 1194.2）远超 16.38，第二阶段系数仍 1% 显著为正。

H1 在基准、稳健性、内生性三条路径上均得到支持。

## Risks

- 异质性切分缺失：未按产权性质、行业、规模、地区披露差异，无法判断结论在全样本均匀成立还是被某子样本驱动。
- 中介路径作者使用江艇（2022）两步法，未做 Sobel/Bootstrap 显著性检验。
- 测度依赖：高质量发展 = LP 法 TFP 的单一代理是否能完全捕捉"绿色 + 共享 + 协调"维度，存在测度争议。
- B2 中位数判定法对行业-年度内机构投资者数量稀少的行业（如部分小行业）易出现噪声分组。
