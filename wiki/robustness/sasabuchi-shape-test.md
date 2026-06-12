---
title: "Sasabuchi U 型 / 倒 U 型显著性检验"
slug: "sasabuchi-shape-test"
check_type: alternative_model
purpose: "二次项系数显著不能直接断定 U / 倒 U 型；Sasabuchi 检验同时验证两侧斜率方向相反且显著，并给出拐点的 Fieller 置信区间"
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
implementation_notes: "Stata: utest 命令；输出包含 t 值、p 值、拐点、Fieller CI、两侧斜率"
date_updated: 2026-05-07
---

## Purpose

避免对二次项符号显著就武断断定非线性关系。Sasabuchi (1980) 的检验需同时满足：

- 极值点位于样本范围内；
- 左侧斜率与右侧斜率方向相反且各自显著。

## When To Use

- 因变量与某连续变量的关系疑似 U 型 / 倒 U 型。
- 已经做过含平方项的回归并得到 ξ₂ > 0 (U) 或 < 0 (倒 U)。
- 期望强化对功能形式的判断而非仅依赖二次项符号。

## Implementation

```stata
* 先运行二次项回归
reghdfe Y X X2 controls, absorb(industry year) cluster(stkcd)

* Sasabuchi 检验
utest X X2
* 输出: t-value, p-value, extreme point, Fieller 95% CI, left slope, right slope
```

## Expected Table Pattern

代飞 (2025) 表 4 / 表 8 的格式：

| 检验指标 | 结果 |
| --- | --- |
| Sasabuchi t / p | t = 2.75, p = 0.006 |
| 极值点 | PC = 167.77 |
| Fieller 95% CI | [132.53, 189.36] |
| 左侧斜率 / t | -0.21, t = -3.42 |
| 右侧斜率 / t | 0.33, t = 2.52 |

## Interpretation

- p < 0.05 + 拐点位于样本数据 [min, max] 区间 + 两侧斜率方向相反且显著 → U 型成立。
- 拐点位于样本之外 → 实际只观察到单调段，"U 型"是外推，不可断言。
- 代飞 (2025)：拐点 167.77 在样本范围内但远高于均值 21.98，意味着大多数企业处于左侧（PC 上升仍在抑制 exploit），需扩大 PC 注入才能进入右侧促进区间。

## Caveats

- Fieller CI 在小样本下可能很宽。
- 拐点的政策含义需结合样本分位数解读，不能机械引用。
- utest 默认不处理 cluster SE 的修正，需额外注意。
