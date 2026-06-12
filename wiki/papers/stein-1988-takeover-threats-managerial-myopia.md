---
title: "Takeover Threats and Managerial Myopia"
slug: "stein-1988-takeover-threats-managerial-myopia"
arxiv: ""
venue: "Journal of Political Economy 96(1): 61-80"
year: 1988
tags: [theory, managerial-myopia, signaling, takeover, corporate-governance]
importance: 5
paper_kind: theory
date_added: 2026-05-29
source_type: pdf
s2_id: ""
keywords: [managerial myopia, takeover, signaling, asymmetric information, patient capital]
domain: "公司金融理论"
code_url: ""
cited_by: []
theory:
  model_class: "三期信号传递博弈（不对称信息，含收购者）"
  solution_concept: "贝叶斯精炼均衡 + 直觉标准（Kreps 1985）"
  key_propositions: [stein-prop1-dual-equilibria, stein-prop2-welfare-nonmonotonic, stein-prop3-informed-small-signaling, stein-prop4-informed-pooling-vanishes, stein-prop5-informed-no-welfare-loss, stein-cs-patient-stockholders-reduce-myopia]
  predictions: [pc-attenuates-managerial-myopia]
---

## 研究问题

收购压力是否会促使经理牺牲长期利益以抬高当期利润（管理者短视）？在股东和经理都理性的前提下，短视能否作为均衡出现？放任收购市场（最小化收购成本）是不是社会最优政策？

## 模型环境

三期（t=1, 2, 3）信号传递博弈。Acme 石油公司在 t=1 获知油藏状态：好状态（概率 p）有 x₁ 桶油，坏状态（概率 1−p）有 x₂ 桶，x₂ < x₁。股东不可观测状态，只能用先验 p、1−p 给公司估值：

```
V₀ = (1+r)[p·x₁ + (1−p)·x₂]          (eq 1)
```

油是"长期资产"：今天卖每桶得 \$1，等到 t=3 卖每桶得 \$(1+r)。实际利率取 0，故等到 t=3 才卖是长期利润最大化策略。经理唯一能传递"好状态"信号的方式是 t=1 提前卖油抬高当期盈利（其余信号方式如分红、回购被假设成本过高而排除）。收购者在 t=2 调查公司，得到协同改进 v ~ F(v)，可付成本 c 发起收购；c 是度量"收购压力"的参数。

## 核心假设

- [[stein-asymmetric-information]]：经理知状态、股东不知。
- [[stein-long-term-asset-timing]]：长期资产的时序结构（今天 \$1 vs 未来 \$(1+r)）。
- [[stein-signaling-only-via-current-earnings]]：唯一信号渠道是 t=1 卖油抬当期盈利。
- [[stein-raider-takeover-cost]]：收购者与收购成本 c。
- [[stein-managers-maximize-shareholder-return]]：基准设定经理与股东利益一致（§IV 放松为 U = Y + βC）。

## 解概念

聚焦满足直觉标准（Kreps 1985）的贝叶斯精炼均衡。底层结构是 Spence(1973)式信号传递博弈。见 [[signaling-game]]、[[intuitive-criterion]]。

## 命题与证明

- [[stein-prop1-dual-equilibria]]：收购者不知情时，混同与分离均衡可并存。
- [[stein-prop2-welfare-nonmonotonic]]：收购者不知情时，福利对 c 非单调，收购可致事前福利损失。
- [[stein-prop3-informed-small-signaling]]：收购者知情时，好公司可用任意小信号成本分离。
- [[stein-prop4-informed-pooling-vanishes]]：收购者知情时混同均衡基本消失。
- [[stein-prop5-informed-no-welfare-loss]]：收购者知情且 β=0 时收购永不致福利损失（§IV 中 β>0 反转）。
- [[stein-cs-patient-stockholders-reduce-myopia]]：耐心股东降低短视、提高中等成本区间福利（比较静态）。

## 比较静态

短视程度随**收购成本 c 下降**（收购压力↑）、**股东越不耐心**、**信息不对称越强**而加剧。低 c → 唯一短视分离均衡；高 c → 唯一不传信号；中等 c → 取决于股东信念（耐心→混同、不耐心→分离）。临界点满足 eq 2、eq 3：

```
分离可支撑：G(c)(1+r)(x₁−x₂) − rx₂ ≥ 0          (eq 2)
混同可支撑：G(c)(1+r)(1−p)(x₁−x₂) − rx₂ ≤ 0      (eq 3)
```

其中 G(c) = 1 − F(c) 是收购概率，c_p < c_s。

## 可检验推论

模型导出、可拿去实证的符号关系：

- **耐心资本/耐心股东降低管理者短视** → 落 [[pc-attenuates-managerial-myopia]]（理论侧来源）。
- 短视主要发生在**从未被收购**的公司，难以从被收购样本观测（样本选择问题）。
- 低 R&D 公司被收购更少 **不能**证伪短视：模型预测短视公司事前收购概率更低。
- 投资公告的正向股价反应（McConnell-Muscarella 1985）与短视假说**一致**（经理越不愿投，所投项目 NPV 越高）。
- 反收购章程修正案的正向股价反应（Linn-McConnell 1983）与模型一致。
- 更锐利的检验（脚注 19）：比较反收购条款采纳前后的资本/R&D 支出。

## 对实证的启发

本文是"管理者短视"和"耐心资本降低短视"的理论微观基础。它直接为本项目的 [[managerial-myopia-mediation]] 机制和 [[pc-attenuates-managerial-myopia]] 假设提供理论侧支撑——[[代飞-2025-耐心资本-双元创新-管理者短视]] 和 [[胡楠-2021-管理者短视主义-长期投资-文本分析]] 的实证检验对应的正是 Stein 的"耐心股东 → 少短视"机制。Stein 反复使用的 "patient stockholders" 是"耐心资本"概念的理论祖先。

## Related

- 机制：[[managerial-myopia-mediation]]、[[information-asymmetry-mediation]]
- 假设：[[pc-attenuates-managerial-myopia]]
- 实证检验方：[[代飞-2025-耐心资本-双元创新-管理者短视]]、[[胡楠-2021-管理者短视主义-长期投资-文本分析]]
- 同问题理论（互补机制·退出型治理）：[[edmans-2009-blockholder-trading-managerial-myopia]]
- 理论基础：[[signaling-game]]、[[intuitive-criterion]]
