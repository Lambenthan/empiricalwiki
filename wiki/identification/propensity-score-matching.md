---
title: "倾向得分匹配 PSM（含 PSM-DID）"
slug: "propensity-score-matching"
strategy_type: psm
source_papers: []
assumptions: ["可忽略性 / 条件独立 CIA：给定协变量，处理分配与潜在结果独立", "共同支撑：处理组与控制组的倾向得分分布有重叠", "协变量为前定变量，不受处理影响"]
threats: ["CIA 对不可观测混杂无能为力——PSM 只解决可观测选择", "得分模型设定错误导致匹配失衡", "卡尺过宽引入坏对照，过窄丢样本损外部有效性"]
implementation_notes: "psmatch2 或 teffects psmatch；匹配后必报平衡性检验（标准化偏差 <10%）与共同支撑图。模板见 tools/stata-templates/psm.do"
date_updated: 2026-06-12
---

## Identification Problem

处理组与控制组在可观测特征上系统性不同（大公司更可能被试点、好公司更可能拿认证），直接比较把特征差异错算成处理效应。PSM 用"处理概率相同"的个体互为反事实。

## Strategy

1. Logit/Probit 估计处理概率（倾向得分）：`P(Treat=1|X)`，X 取处理前一期的公司特征。
2. 按得分匹配（最近邻 1:1 / 1:k、卡尺、核匹配），得到平衡样本。
3. 在匹配样本上估计 ATT；与 DID 结合（PSM-DID）时在匹配样本上跑双重差分。

## Key Assumptions

- **CIA 是全部重量所在**：你必须论证"影响处理分配的变量都已观测并放进 X"。这在经管语境通常很强，所以 PSM 多作为稳健性而非主识别。
- 共同支撑：修剪得分超出对方支撑域的观测。
- X 必须是前定的：用处理后变量匹配会"控制掉"处理效应本身。

## Implementation

- `psmatch2 treat x1 x2 ..., outcome(y) neighbor(1) caliper(0.05) ties common` 或 `teffects psmatch (y) (treat x1 x2 ...)`（后者标准误更正规）。
- 匹配比例与卡尺是研究者自由度，正文给基准（常用 1:1 卡尺 0.05），稳健性换 1:4、核匹配。
- 模板：`tools/stata-templates/psm.do`。

## Diagnostics

- 平衡性检验：匹配后各协变量标准化偏差 |bias| < 10%（至少 < 20%），t 检验不显著；报匹配前后对比表。
- 共同支撑图：处理组与控制组得分密度重叠区。
- Rosenbaum 边界 / Oster δ：评估"还需多强的不可观测混杂才能翻掉结论"。

## Limitations

- 对不可观测混杂毫无防御——这点必须在论文里诚实说出来，并以 IV（[[instrumental-variables]]）或 DID（[[difference-in-differences]]）补强。
- 得分估计误差未进入第二步标准误（psmatch2 的已知问题），重要结论用 teffects 或 bootstrap 核验。
- 匹配丢样本改变了估计对象（ATT on matched sample），外推要克制。
