---
title: "直觉标准（Intuitive Criterion）"
slug: "intuitive-criterion"
domain: "博弈论（均衡精炼）"
status: mainstream
aliases: [Cho-Kreps intuitive criterion, 直觉准则]
first_introduced: "Cho and Kreps 1987；Stein 1988 引用 Kreps 1985"
date_updated: 2026-05-29
source_url: ""
---

## Definition

信号博弈的一种均衡精炼准则：删除那些依赖"不合理离均衡路径信念"的贝叶斯精炼均衡。若某类型在任何合理信念下都不可能从某个离均衡信号中获益，接收者就不应把该信号归因于该类型。

## Intuition

用"谁有动机偏离"来约束离均衡信念：只有真正可能因偏离而获益的类型，才被允许出现在离均衡信号的后验里。这样能筛掉大量靠"威胁性悲观信念"支撑的均衡。

## Formal notation

对离均衡信号 s'，先求出"在任何后验下都不会因发 s' 而比均衡更好"的类型集合 D；要求接收者对 s' 的后验只放在 D 的补集上。若由此能推翻原均衡，则该均衡不满足直觉标准。

## Key variants

D1、D2、神圣直觉准则（divinity）等更强精炼；直觉标准是其中较弱、应用最广的一档。

## Known limitations

在某些博弈里仍留下多重均衡；过强的精炼又可能排除掉合理均衡。

## Open problems

不同精炼准则的选择缺乏统一的行为基础。

## Relevance to active research

是判定"哪个信号均衡可解释"的标准工具。[[stein-1988-takeover-threats-managerial-myopia]] 的命题1、命题4 都以"通过直觉标准"为均衡选择条件。
