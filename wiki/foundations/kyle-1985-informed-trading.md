---
title: "Kyle (1985) 知情交易与市场微观结构"
slug: "kyle-1985-informed-trading"
domain: "市场微观结构 / 资产定价"
status: mainstream
aliases: [Kyle model, 连续拍卖模型, informed trading model]
first_introduced: "Kyle (1985), Econometrica 53(6): 1315-1335"
date_updated: 2026-06-03
source_url: "https://doi.org/10.2307/1913210"
---

## Definition

Kyle (1985) 的市场微观结构模型刻画一个知情交易者、若干噪声（流动性）交易者与一个竞争性做市商之间的博弈。做市商只观察到净订单流（知情者 + 噪声交易者之和），无法区分二者，按净订单流的条件期望定价；知情者据私有信息策略性下单，并以噪声交易作掩护。

## Intuition

做市商看不到谁在交易、只看到总买卖差额。知情者若交易太猛会暴露信息、推动价格不利于己，故会"克制"地交易，把私有信息部分而非全部地注入价格。噪声交易者的存在是知情者能获利的前提——没有噪声，做市商就能从任何订单反推出信息，知情者无利可图。

## Formal notation

竞争性做市商定价 P = E[V | 总订单流 d]，d = 知情者订单 + 噪声交易需求。原始 Kyle (1985) 用正态分布的企业价值与正态噪声需求获得线性均衡：价格冲击系数 λ（Kyle's lambda）度量市场深度的倒数。零利润条件 + 知情者最优化联立求理性预期均衡。

## Key variants

- 二元企业价值 + 指数噪声需求（如 [[edmans-2009-blockholder-trading-managerial-myopia]]）：使知情者交易量可闭式内生求解，并借短卖约束把交易量与初始持股挂钩。
- 多期/连续时间 Kyle：信息逐步注入价格。
- 含实体决策的 Kyle（Edmans 2009、Holmstrom-Tirole 1993）：把价格效率反馈到经理投资/努力，连接金融市场与实体效率。

## Known limitations

- 竞争性零利润做市商、风险中性等设定是简化；引入做市商风险厌恶或市场势力会改变定价。
- 噪声交易需求外生给定，其来源（流动性冲击、行为偏差）未被建模。
- 线性均衡依赖正态性假设；非正态需特定函数形式（如指数）才可解。

## Open problems

- 内生化噪声交易、做市商竞争结构。
- 多知情者、信息互补/替代下的均衡刻画。

## Relevance to active research

Kyle 框架是把"信息如何进入价格"形式化的标准工具，也是公司金融中"价格效率 → 实体效率"反馈类模型（退出型治理、反馈效应文献）的微观基础。本 wiki 中 [[edmans-2009-blockholder-trading-managerial-myopia]] 即在此框架上叠加短卖约束与经理投资决策，论证退出型治理如何抑制管理者短视。
