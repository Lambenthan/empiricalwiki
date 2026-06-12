---
title: "断点回归 RDD（精确与模糊）"
slug: "regression-discontinuity"
strategy_type: rd
source_papers: []
assumptions: ["连续性：潜在结果在阈值处关于驱动变量连续", "不可精确操纵：个体无法精确控制自己落在阈值哪一侧", "局部随机化：阈值邻域内处理近似随机"]
threats: ["驱动变量被操纵（McCrary 检验密度跳跃）", "阈值处其他政策共变（复合处理）", "带宽选择敏感、远离阈值外推无效"]
implementation_notes: "rdrobust + rdplot + rddensity 三件套；报告 MSE 最优带宽及 0.5/2 倍带宽稳健性。模板见 tools/stata-templates/rdd.do"
date_updated: 2026-06-12
---

## Identification Problem

处理由某个连续变量（驱动变量）是否越过阈值决定：评分线、规模门槛、持股比例红线。阈值两侧紧邻的个体在其他方面近似相同，处理状态却跳变——这是最接近自然实验的观察性设计。

## Strategy

- **Sharp RD**：越线即处理。`τ = lim(x↓c) E[Y|X=x] − lim(x↑c) E[Y|X=x]`，局部多项式在阈值两侧分别拟合。
- **Fuzzy RD**：越线只改变处理概率，用"越线"作处理的 IV，估计阈值处 complier 的 LATE。

经管常见场景：监管规模门槛（如披露义务）、指数纳入市值线、持股 5% 举牌线、评级阈值。

## Key Assumptions

- 连续性假设：除处理外，一切影响 Y 的因素在阈值处连续。
- 不可精确操纵：若个体能把自己"挪"过线（盈余管理凑门槛是经管高发区），阈值附近就是选择出来的样本，设计崩溃——这是 RDD 用于财务数据时第一个要排查的事。

## Implementation

- 估计：`rdrobust y x, c(阈值) p(1) kernel(triangular) bwselect(mserd)`，默认局部线性 + MSE 最优带宽 + 偏差修正稳健推断。
- 可视化：`rdplot`（分箱散点 + 拟合线），RDD 论文没有这张图等于没做。
- 模板：`tools/stata-templates/rdd.do`。

## Diagnostics

- **McCrary / rddensity**：驱动变量密度在阈值处是否跳跃（操纵检验），`rddensity x, c(阈值)`。
- 协变量平滑性：前定特征在阈值处不应跳跃（逐个跑一遍 rdrobust）。
- 安慰剂阈值：在假阈值处估计应得零。
- 带宽稳健性：0.5 倍、2 倍最优带宽下系数稳定。
- 甜甜圈 RD：剔除紧贴阈值的观测（堆积嫌疑）重估。

## Limitations

- 估计的是**阈值处的局部效应**，对远离阈值的个体外推无效；政策建议要写得克制。
- 高阶多项式全局拟合已被弃用（Gelman-Imbens 批评），坚持局部线性 / 二次。
- Fuzzy RD 第一阶段弱（越线只略微提高处理概率）时继承弱 IV 全部问题。
