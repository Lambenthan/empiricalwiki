---
title: "稳定型机构投资者监督渠道"
slug: "stable-investor-monitoring-channel"
mechanism_type: governance
source_papers: [杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]
variables: [institutional-investor-heterogeneity-stability, stock-price-crash-risk]
evidence:
  - 稳定型样本组 INVH 系数对 Ncskew 为 −0.4714（5%），对 Duvol 为 −0.3261（5%）
  - 交易型样本组 INVH 系数对 Ncskew 为 1.5185（1%），对 Duvol 为 0.2778（5%）
date_updated: 2026-05-07
---

## Mechanism Statement

稳定型机构投资者持股期长、持股比例相对高，监督上市公司经营管理的边际收益高于成本，能够约束管理层机会主义行为，压缩坏消息囤积空间，从而降低股价崩盘风险。交易型机构投资者持股期短，倾向于追求价差，监督激励弱甚至与管理层合谋掩盖信息，加剧崩盘风险。

## Theoretical Logic

- 隐藏坏消息假说（Jin and Myers, 2006; Hutton et al., 2009）：股价崩盘的根源是管理层囤积负面信息超过临界点的集中释放。
- 稳定型机构投资者：基于股东积极主义理论，持股期长 + 持股比例高 → 监督收益 > 监督成本 → 主动参与治理 → 信息透明度提升 → 坏消息无法长期累积 → 崩盘风险下降。
- 交易型机构投资者：短视、追求价差，可能与管理层合谋（一起拉抬股价）或羊群行为推升泡沫，叠加管理层囤积坏消息的动机，崩盘风险上升。

## Empirical Proxy

- 通过 [[institutional-investor-heterogeneity-stability]] 的 INVW 二值哑变量切分两类样本。
- 对每类样本分别回归 INVH 对 [[stock-price-crash-risk]]（Ncskew/Duvol）的影响，比较系数方向。
- 系数方向相反即支持监督 vs 合谋的双向机制。

## Evidence Across Papers

- 杨棉之 (2020)：稳定型 INVH 显著负向，交易型 INVH 显著正向；稳健性（IsCrash 与 Logistic）一致。
- 曹丰等 (2015) 全 A 股样本：两类机构投资者均显著正向，与本文剔除中小创后样本结论相反。本文将这一差异归因于创业板/中小板上机构投资者交易策略与主板存在结构差异。
- An and Zhang (2013, JCF) 美国样本：长期专注型机构投资者（DED）显著降低崩盘风险。

## Boundary Conditions

- 持股稳定性的二值化门槛对样本切分的方向敏感。
- 稳定型机构投资者类型构成（社保 / 企业年金 / QFII）不同时，监督力度也可能不同；本文未做类型分项。
- 在控股股东主导的公司治理结构下，机构投资者监督力度受限，本机制在大股东持股比例极高的子样本中可能减弱。

## Open Questions

- 监督机制的中介变量（信息透明度、应计盈余管理、分析师跟踪等）未在本文显式中介检验中识别。
- 不同稳定型机构投资者（社保 vs 企业年金 vs QFII）监督方式与效果是否同质？
- 卖空机制松绑后稳定型机构投资者的监督渠道与价格效率渠道如何分解？
