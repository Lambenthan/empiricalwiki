---
title: "创新决策权配置调节（集权 vs 分权）"
slug: "innovation-decision-centralization-split"
grouping_variable: "CenR (Innovation Decision Centralization Residual)"
grouping_rule: "参考谭洪涛等 (2019)：以母公司无形资产 / 合并报表无形资产 (PI) 对 母公司总资产 / 合并报表总资产 (PA) 进行 OLS 回归，将残差作为 CenR；残差越大说明母公司控制创新决策权越集中。先做交互项再按 CenR 中位数划分集权 / 分权两组子样本。"
rationale: "集权模式下母公司可压缩子公司机会主义、统筹资源；分权模式下子公司决策自主权高，但资源整合能力弱。两种模式下耐心资本与创新韧性的非线性关系可能不同。"
source_papers: [贾勇-2025-耐心资本-创新韧性-倒u型]
date_updated: 2026-05-07
---

## Grouping Logic

构造步骤：

1. 计算 PI = 母公司无形资产 / 合并报表无形资产；PA = 母公司总资产 / 合并报表总资产。
2. 对 PI 与 PA 各做 1% 双侧缩尾。
3. 估计 PI = α₀ + α₁ × PA + ε₁，取残差 ε₁ 作为创新决策权配置 CenR。CenR 越大表示母公司在创新无形资产相对于其规模占比越高 → 母公司创新决策权越集中。
4. 先以 PC、PC²、CenR、CenR×PC、CenR×PC² 进入主回归（表 7 列 2）。
5. 再按 CenR 中位数将样本分为高集权组与低集权组（表 7 列 3、列 4）。

## Theoretical Rationale

- 集权管理：母公司监督能力强、压缩子公司机会主义空间，可统筹创新资源、提高决策一致性，但缺乏专有知识增加信息成本。
- 分权管理：决策自主性高，有利于探索新业务模式，但工作语言不一致带来沟通障碍，资源协调难度大。

## Sample Split

- 列 (3) 高集权组（CenR 高于中位数）：N = 12 893。
- 列 (4) 低集权组（CenR 低于中位数）：N = 12 892。

## Model

主回归形式（与管理者耐心程度类似）：

$$Res_{i,t+1} = \alpha_0 + \alpha_1 PC + \alpha_2 PC^2 + \alpha_3 CenR + \alpha_4 CenR \times PC + \alpha_5 CenR \times PC^2 + \sum \alpha_j Controls + Industry + Year + \varepsilon$$

子样本分别按相同模型回归（不含 CenR 主项与交互项）。

## Interpretation

贾勇 (2025) 表 7：

- 列 (2)：CenR 系数 0.113 (10% 显著)；CenR×PC = 2.397 (1% 显著)，CenR×PC² = -1.457（不显著）。
- 列 (3) 高集权组：PC = 0.778 (5%)，PC² = -0.799（不显著）。倒 U 型不成立，PC 与 Res 呈线性正相关。
- 列 (4) 低集权组：PC = 0.715 (5%)，PC² = -1.288 (5% 显著)。倒 U 型成立。
- 解释：当母公司创新决策权集中时，PC 增加可被母公司更高效地配置到关键创新活动，避免子公司机会主义，使 PC 一直处于"促进段"；当决策权分散，资源利用效率降低，过度耐心资本会陷入资源陷阱与协调失败。

## Related

- 主论文：[[贾勇-2025-耐心资本-创新韧性-倒u型]]
- 核心解释变量：[[patient-capital]]
- 被解释变量：[[innovation-resilience]]
