---
title: "信号传递博弈（Signaling Game）"
slug: "signaling-game"
domain: "博弈论 / 信息经济学"
status: mainstream
aliases: [signaling, Spence signaling, 代价高昂信号]
first_introduced: "Spence 1973"
date_updated: 2026-05-29
source_url: ""
---

## Definition

一类不完全信息动态博弈：拥有私有信息的一方（发送者）先采取一个可观测、且对不同类型成本不同的行动（信号），不知情的一方（接收者）据此更新信念并行动。Spence(1973) 的劳动力市场教育信号是原型。

## Intuition

只有当"发好信号"对不同类型的成本足够不同时，信号才可信——高类型发信号便宜、低类型发信号贵，于是分离均衡里信号成为类型的可信标志。代价为零的信号无法分离。

## Formal notation

类型 θ ~ 先验；发送者选信号 s，成本 c(s, θ)；接收者观测 s、更新后验 μ(θ|s)、选行动 a。均衡要求发送者最优、接收者贝叶斯更新且最优。

## Key variants

- 分离均衡 / 混同均衡 / 半分离均衡
- Stein(1988) 把它用于"经理用提前卖油（牺牲长期价值）向市场传递好状态"，信号成本即长期价值损失 rx₂。

## Known limitations

多重均衡问题严重——需要均衡精炼（如直觉标准）才能做出可解释的预测。

## Open problems

离均衡路径信念的合理性约束在不同精炼准则下结论不同。

## Relevance to active research

公司金融中大量"信息不对称 → 信号"模型的统一框架；本 wiki 中 [[stein-1988-takeover-threats-managerial-myopia]] 的底层结构。
