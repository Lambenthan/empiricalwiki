---
title: "熵平衡匹配（Entropy Balancing）"
slug: "entropy-balancing"
check_type: psm
purpose: "在不损失样本的情况下，使处理组与对照组的控制变量在三阶矩条件（均值、方差、偏度）上完全平衡，从而缓解可观测协变量层面的系统性差异对主效应估计的污染"
source_papers: [李心武-2025-耐心资本-数字化转型-价值发现]
implementation_notes: "Stata 用 ebalance 命令；Python 可用 ebalance.py 实现。需指定平衡的矩条件（默认前三阶），并对每个观测赋予权重"
date_updated: 2026-05-07
---

## Purpose

熵平衡是 Hainmueller (2012) 提出的可观测协变量平衡方法。相对于倾向得分匹配（PSM），它的优势在于：

- 不需要丢弃不匹配样本，保留全部观测。
- 可以同时平衡多阶矩（均值、方差、偏度），平衡精度高于 PSM。
- 通过最小化熵损失重新分配样本权重，避免对样本的硬性删减。

## When To Use

- 处理组与对照组在控制变量分布上存在系统性差异时。
- 样本量较大、希望保留全部观测的情况。
- 需要同时平衡均值、方差、偏度等多阶特征以提高内部有效性时。

## Implementation

李心武 (2025) 应用：

- 依据 Digital 是否为 0，把样本划分为"数字化转型企业"（Digital > 0）与"非数字化转型企业"（Digital = 0）两组。
- 对所有控制变量执行熵平衡，使两组的均值、方差、偏度完全相同。
- 在加权样本上重新估计主回归 Proportion = β · Digital + γ · Controls + Fund × Firm + Year + ε。

Stata 实现示例：

```stata
ebalance dummy_digital ${controls}, targets(3)
reghdfe Proportion Digital ${controls} [pw=_webal], absorb(fund_firm year) cluster(fund_firm)
```

其中 `targets(3)` 表示同时平衡到第三阶矩。

## Expected Table Pattern

熵平衡稳健性表通常并列报告：

- 列 (1)：原始样本基准回归。
- 列 (2)：熵平衡加权后的主回归。
- 平衡前后控制变量的均值、方差对比表（一般在附录或正文上方）。

## Interpretation

李心武 (2025) 报告：在控制了数字化转型企业与非数字化转型企业在企业特征层面的系统性差异后，Digital 系数仍显著为正，主结论稳健。

## Caveats

- 熵平衡仅平衡可观测协变量，对遗漏的不可观测变量无能为力，需与 IV、Heckman 等方法配合使用。
- 平衡到的矩越高（如方差、偏度），权重分布越极端，可能放大少量观测的影响。
- 加权回归的标准误需选用稳健 / 聚类版本，避免低估。

## Related

- robustness：[[sasabuchi-shape-test]]
- identification：[[heckman-treatment-effects]] · [[iv-fiber-cable-government-report]]
- papers：[[李心武-2025-耐心资本-数字化转型-价值发现]]
