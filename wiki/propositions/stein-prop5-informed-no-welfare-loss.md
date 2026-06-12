---
title: "命题5：知情收购者下收购永不致事前福利损失（β=0）"
slug: "stein-prop5-informed-no-welfare-loss"
proposition_type: welfare
formal_statement: "PROPOSITION 5. When raiders are informed, the takeover mechanism can never lead to ex ante welfare losses. Even though welfare may not be monotonic in c, it is guaranteed that any finite c is preferable to an infinite c."
conditions: "收购者知情，且经理与股东利益一致（β=0）。§IV 引入控制权偏好 β>0 时此结论反转。"
proof_technique: "条件期望性质（附录 A2–A4）：用均衡信号成本 rx* = min{rx₂, (1+r)G(z)(x₁−x₂)}（eq 6），证明事前收购收益 G(c)E(v−c | v≥c) − prx* ≥ 0。"
source_papers: [stein-1988-takeover-threats-managerial-myopia]
predicts: []
date_updated: 2026-05-29
---

## Statement

> PROPOSITION 5. When raiders are informed, the takeover mechanism can never lead to ex ante welfare losses. Even though welfare may not be monotonic in c, it is guaranteed that any finite c is preferable to an infinite c.

## Conditions

收购者知情 **且 β=0**（经理无控制权私利）。直觉：v 平均而言较小时信号成本也小（知情下坏公司没动机抬价），故收购收益足以覆盖信号浪费。

## Proof Sketch

附录 A2–A4：均衡信号成本 `rx* = min{rx₂, (1+r)G(z)(x₁−x₂)}`（eq 6），其中 z = c + (1+r)(x₁−x₂)。由 `E(v−c | v≥c) ≥ z−c = (1+r)(x₁−x₂)` 推出事前收购收益 `G(c)E(v−c | v≥c) − prx* ≥ G(z)(1+r)(x₁−x₂) − prx* ≥ 0`。

## Comparative Statics

**关键反转（§IV）**：一旦经理有控制权偏好（β>0），结论倒过来——知情收购者反而比不知情更糟，可能加剧道德风险（经理为留任浪费资源）。

## Testable Implications

收购的福利效应高度依赖"经理是否为控制权而非股东价值行事"——纯信息渠道与代理渠道需分开识别。

## Related

- [[stein-1988-takeover-threats-managerial-myopia]]
- [[stein-prop2-welfare-nonmonotonic]]（不知情对照）
- [[stein-managers-maximize-shareholder-return]]（β=0 假设，§IV 放松）
