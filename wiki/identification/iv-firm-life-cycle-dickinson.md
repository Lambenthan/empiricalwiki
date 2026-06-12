---
title: "工具变量 2SLS：企业生命周期（Dickinson 现金流分类）"
slug: "iv-firm-life-cycle-dickinson"
strategy_type: iv
source_papers: [唐亮-2025-耐心资本-esg表现]
assumptions: ["相关性：企业所处生命周期阶段（导入 / 成长 / 成熟 / 淘汰 / 衰退）显著影响其对耐心资本的吸引力与现金流稳定性，从而决定 PC 比重", "外生性：企业生命周期阶段不直接决定 ESG 表现，任何阶段企业都可能呈现好或差的 ESG 表现，因此满足排他性约束"]
threats: ["生命周期与 ESG 之间存在间接路径：成熟期企业资源更充足、信息披露更规范，可能直接拉高 ESG 分项", "Dickinson 现金流分类假设公司财务报表真实可靠，盈余管理会扰动分类结果"]
implementation_notes: "唐亮 (2025) 表 8：识别不足检验 LM 统计量（PC 75.845、Stequity 6.417、Rdebt 104.255）；弱工具 F 值（32.916、37.728、45.294）均通过 Stock-Yogo 10% maximal IV size 临界值；Sargan 统计量（6.732、25.047、6.601）显示模型恰好识别"
date_updated: 2026-05-07
---

## Identification Problem

耐心资本与企业 ESG 表现之间存在双向因果：耐心资本可以提升 ESG，但反过来 ESG 表现越好的企业越能吸引长期投资者，使 OLS 估计被反向因果与遗漏变量污染。

## Strategy

借助 Dickinson (2011) 的现金流分类法，结合 Gort 与 Klepper (1982) 提出的产品生命周期五阶段（导入期 / 成长期 / 成熟期 / 淘汰期 / 衰退期），通过经营、投资、筹资三大现金流的正负组合判定企业当年所处生命周期阶段，作为 PC 的工具变量。

工具变量逻辑：

- 第一阶段：PC ~ Lifecycle + Controls + 行业 FE + 年份 FE。
- 第二阶段：ESG ~ 拟合 PC + Controls + 行业 FE + 年份 FE。

因核心解释变量包括 PC、Stequity、Rdebt 三个版本，需分别做 IV 估计。

## Key Assumptions

- 相关性：第一阶段企业生命周期对 PC 系数显著，弱工具 F 统计量 > 10。本文 F = 32.916 / 37.728 / 45.294 全部满足。
- 外生性 / 排他性：企业生命周期影响 PC 但不直接影响 ESG。作者论证：任何阶段（导入、成长、成熟、淘汰、衰退）企业都可能呈现好或差的 ESG 表现。
- 过度识别：当 IV 数量等于内生变量数量（恰好识别）时不需要 Sargan 检验通过；唐亮 (2025) 给出 Sargan 统计量但表注明"恰好识别"，更多用于诊断而非检验。

## Implementation

```stata
* 基于 Dickinson (2011) 构造生命周期分类
* 经营现金流 OCF、投资现金流 ICF、筹资现金流 FCF 的正负组合 → 5 阶段
gen lifecycle = .
replace lifecycle = 1 if OCF < 0 & ICF < 0 & FCF >= 0   /* 导入期 */
replace lifecycle = 2 if OCF >= 0 & ICF < 0 & FCF >= 0  /* 成长期 */
replace lifecycle = 3 if OCF >= 0 & ICF < 0 & FCF < 0   /* 成熟期 */
replace lifecycle = 4 if (OCF >= 0 & ICF >= 0 & FCF < 0) | (OCF < 0 & ICF >= 0 & FCF < 0)  /* 淘汰期 */
replace lifecycle = 5 if OCF < 0 & ICF >= 0 & FCF >= 0  /* 衰退期 */

* 第一阶段 + 第二阶段
ivreghdfe ESG (PC = i.lifecycle) $controls, absorb(industry year) cluster(firmid) first
estat firststage
estat overid
```

## Diagnostics

- 识别不足检验（Anderson canon. corr.）：LM 统计量。本文 PC = 75.845、Stequity = 6.417、Rdebt = 104.255，三个指标对应不同 IV 配置，Stequity IV 较弱需谨慎。
- 弱工具检验（Cragg-Donald F、Kleibergen-Paap rk F）：F > Stock-Yogo 10% maximal IV size 临界值（约 16.38）。本文均通过。
- 过度识别：Sargan 统计量；本文报告"恰好识别"。

## Limitations

- Dickinson 五阶段分类对会计盈余管理高度敏感，激进的盈余管理可能错位生命周期判定。
- 排他性约束的"任何阶段都可能好或差 ESG"是定性论证，未做正式测试；如果成熟期企业因披露规范度更高而直接拉高 ESG，IV 排他性会受质疑。
- 若研究需要单独识别 Stequity（稳定型股权），需关注其 LM = 6.417 较弱，可能需要补充 IV 或合并工具策略。
- 与代飞 (2025) 的"行业 PC 均值 + PC 滞后"双工具法（[[instrumental-variable-2sls]]）相比，本生命周期 IV 优势是不依赖同行业其它公司的 PC（避免行业内技术外溢污染），缺点是单一 IV 难以验证 PC²、PC × X 的非线性 / 调节项。
