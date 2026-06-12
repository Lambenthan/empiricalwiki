---
title: "企业创新韧性 (Innovation Resilience, Res)"
slug: "innovation-resilience"
construct: "企业创新韧性"
role: dependent
measurement: "敏感性指标法（向宇等 2023 思路）：Res = 实际创新产出 / 预期创新产出。预期值 EIO = 行业 t-1 年创新效率均值 × 企业 t 年研发投入；行业当年创新效率 IE = 专利申请数 / ln(研发投入+1)。Res 越大表明创新产出越超预期、韧性越强。"
data_sources: [国泰安 CSMAR, 国家知识产权局]
database_tables: [上市公司专利申请, 上市公司研发投入, 行业分类]
frequency: firm-year
source_papers: [贾勇-2025-耐心资本-创新韧性-倒u型]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

企业创新韧性指企业在外部冲击与创新中断风险下，通过自我适应保持和恢复创新稳定的能力。它强调"创新产出"对外部扰动的吸收与恢复，而非企业整体经营韧性。与 [[enterprise-resilience]]（企业韧性，捕捉销售增长与股票收益波动）不同：本变量聚焦创新维度的逆境表现，覆盖范围更窄但与 R&D 决策的因果链更直接。

## Measurement

贾勇 (2025) 采用敏感性指标法 + 向宇等 (2023) 的"实际 / 预期产出"比值思路：

- 第 1 步：企业当年创新效率 IE_{i,t} = IO_{i,t} / Exp_{i,t}，其中 IO 是当年专利申请数，Exp = ln(研发投入 + 1)；
- 第 2 步：以企业 i 所属行业 j 在 t-1 年的创新效率均值 IE_{j,t-1} 作为基准；
- 第 3 步：预期创新产出 EIO_{i,t} = IE_{j,t-1} × Exp_{i,t}（用行业基准效率乘以企业当年研发投入推算"应该产出多少"）；
- 第 4 步：Res_{i,t} = IO_{i,t} / EIO_{i,t}。

Res ≥ 0；Res > 1 表示企业实际创新产出超过行业基准的"应有水平"，韧性较强；Res < 1 表示低于行业基准。基于贾勇 (2025) 描述性统计，N = 27 611，均值 1.052，中位数 0.252，标准差 2.205，最大值 14.219，呈左偏分布——多数企业创新韧性处于中下水平，少数样本拥有极高韧性值。

## Data Source

[[csmar]]：

- 上市公司专利申请数据库：用于 IO_{i,t}（专利申请数）。
- 财务报表：用于研发投入 R&D 总额、行业代码（计算行业基准）。

替代被解释变量稳健性中需用：

- 城市级创新效率（基于地级市 - 行业 - 年份的 IE 均值），重算 Res1。
- 专利授权数（替代申请数），重算 Res2。
- DEA 数据包络分析方法计算创新效率，重算 Res3。

## Literature Variants

文献对创新韧性 / 企业韧性 / 组织韧性的测度可分为四类：

- V1（敏感性指标法 / 比值法）：贾勇 (2025) 采用，以专利申请数 / 行业基准预期产出之比衡量。优势是计算简单、可与企业研发面板数据直接对接。
- V2（综合指标法）：赵华平等 (2024)、梁婧姝等 (2024) 等通过多个分项指标加权（如熵权法）合成创新韧性得分。
- V3（问卷调查法）：基于企业管理者主观感知，多见于战略管理领域；样本量受限。
- V4（事件研究 / 危机响应法）：基于特定外生冲击前后的创新表现差异。
- V5（敏感性 + 替代指标）：使用专利授权数代替申请数（Res2）或 DEA 法计算 IE（Res3），可见于贾勇 (2025) 的稳健性。

注意：本文 Res 与企业韧性 [[enterprise-resilience]]（储佩佩 2025 的"销售增长 + 收益波动率"熵权合成）属于不同构念，操作化口径与含义均不同，二者互为对照而非替代。

## Construction Steps

V1（贾勇 2025）：

1. 从 CSMAR 上市公司专利数据库取每企业每年专利申请数 IO_{i,t}。
2. 从年度财务报表取研发投入 R&D_{i,t}，构造 Exp_{i,t} = ln(R&D_{i,t} + 1)。
3. 按 (industry_code, t) 分组计算行业当年创新效率均值 IE_{j,t} = mean(IO_{i,t} / Exp_{i,t})。
4. 取滞后一期 IE_{j,t-1}，与企业 t 年 Exp 相乘得 EIO_{i,t}。
5. Res_{i,t} = IO_{i,t} / EIO_{i,t}。
6. 对 Res 上下 1% 缩尾。
7. 在主回归中将 Res 滞后一期处理（用 Res_{i,t+1} 作为被解释变量），以应对耐心资本的滞后效应。

## Stata Notes

```
* 假设已合并专利与研发数据，stkcd-year 面板
gen Exp = log(rd + 1)
gen IE = patent_apply / Exp

* 行业基准：按行业-年份取 IE 均值
egen IE_ind_mean = mean(IE), by(indcd year)
xtset stkcd year
gen IE_ind_lag = L.IE_ind_mean

* 预期创新产出与韧性
gen EIO = IE_ind_lag * Exp
gen Res = patent_apply / EIO

* 缩尾
winsor2 Res, cuts(1 99) replace

* 用作被解释变量时滞后一期
gen Res_lead = F.Res
```

## Caveats

- 当 Exp = 0 或行业 IE_{j,t-1} = 0 时 EIO 退化，需特别处理（drop 或赋极小值）。
- 专利申请数本身受行业惯例影响（化工、电子专利密集，咨询、零售专利稀疏），行业 FE 可吸收部分但不能完全；建议同时控制 Industry × Year 高阶 FE。
- 用专利申请数衡量"创新产出"会忽视专利质量；稳健性中改用专利授权数 Res2 部分缓解。
- DEA 法计算 IE 对样本结构敏感，重新分组样本时需重算前沿。
- 行业代码切换（证监会 2012 vs 2001）会导致基准 IE 跳变，需保持口径一致。
- 与 [[enterprise-resilience]] 不可混用：本变量仅刻画"创新维度"的恢复力，不涵盖财务绩效与股价波动。

## Related

- 核心解释变量：[[patient-capital]]
- 主要论文：[[贾勇-2025-耐心资本-创新韧性-倒u型]]
- 配套模型：[[two-way-fixed-effects-industry-year]]
- 配套机制：[[innovation-cooperation-mediation]] · [[innovation-ambidexterity-mediation]] · [[innovation-persistence-mediation]]
- 关联但不同的构念：[[enterprise-resilience]]（储佩佩 2025，企业整体韧性，对照而非替代）
- 配套稳健性：[[sasabuchi-shape-test]]
