---
title: "命题1：不知情收购者下混同与分离均衡并存"
slug: "stein-prop1-dual-equilibria"
proposition_type: existence
formal_statement: "PROPOSITION 1. Depending on parameter values, with uninformed raiders there can be both pooling and separating equilibria that are Bayesian perfect and robust to the intuitive criterion."
conditions: "收购者不知情。分离可支撑当 G(c)(1+r)(x₁−x₂) − rx₂ ≥ 0（eq 2，c ≤ c_s）；混同可支撑当 G(c)(1+r)(1−p)(x₁−x₂) − rx₂ ≤ 0（eq 3，c ≥ c_p）。c_p < c_s。"
proof_technique: "贝叶斯精炼均衡构造 + 直觉标准（Kreps 1985）精炼；分离/混同信念下分别验证经理最优反应。"
source_papers: [stein-1988-takeover-threats-managerial-myopia]
predicts: []
date_updated: 2026-05-29
---

## Statement

> PROPOSITION 1. Depending on parameter values, with uninformed raiders there can be both pooling and separating equilibria that are Bayesian perfect and robust to the intuitive criterion.

## Conditions

- 分离均衡（经理短视卖油）：`G(c)(1+r)(x₁−x₂) − rx₂ ≥ 0`（eq 2），即 c ≤ c_s。
- 混同均衡（经理坚持长期持有）：`G(c)(1+r)(1−p)(x₁−x₂) − rx₂ ≤ 0`（eq 3），即 c ≥ c_p。
- c_p < c_s，故有三段：低 c（c < c_p）→ 唯一短视分离均衡；高 c（c > c_s）→ 唯一不传信号；中等 c（c_p ≤ c ≤ c_s）→ 分离与混同两种纯策略均衡并存（中间区间还存在混合策略均衡，eq 4）。

## Proof Sketch

构造贝叶斯精炼均衡，并用直觉标准排除不合理的离均衡路径信念。分离均衡里"lumpy signaling"使好公司至少要卖 x₂ 桶才能可信分离，信号成本不低于 rx₂。

## Comparative Statics

收购成本 c 越低（收购压力越大），越落入短视分离区间。详见 [[stein-cs-patient-stockholders-reduce-myopia]]。

## Testable Implications

见论文 §V 经验含义。

## Related

- [[stein-1988-takeover-threats-managerial-myopia]]
- [[signaling-game]]、[[intuitive-criterion]]
