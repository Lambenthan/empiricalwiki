---
title: "耐心资本 (Patient Capital, PC)"
slug: "patient-capital"
construct: "耐心资本"
role: core_explanatory
measurement: "理论上指持有期长、容忍不确定性、深度参与治理的资本形态。实证测度尚未统一，本项目文献至少存在 8 种操作化路径（A1–A4 + B1/B2 + C + D）。代飞 (2025) 采用 A2 框架：关系型债务占比 + 稳定型股权指标之和。"
data_sources: [国泰安 CSMAR, CCER, Wind]
database_tables: [机构投资者持股, 长期借款, 应付债券, 应付票据]
frequency: firm-year
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

理论构念：长期持有、风险包容、价值共创的异质性战略资本。林毅夫等首先系统引入，强调对短期逐利资本的批判性反思。

## Measurement

操作化必须区分两个维度——时间属性（持有期长度）和结构属性（股权 vs 债权 vs 政府引导基金）。常见做法：

- 股权侧：机构投资者稳定持股 / 持股期限 / 换手率反向指标。
- 债权侧：银行长期贷款占比 / 非流动负债结构 / 关系型债务。
- 综合指标：熵值法将多个子指标合成单一 PC 评分。

## Data Source

[[csmar]] 财务报表与机构投资者持股；少数论文需补 Wind/CCER 长期债权明细。专利数据通常配套使用 [[cpdp-patent-database]]。

## Literature Variants

- A1（经典版）：换手率 3 分组（顶 30% 为非耐心、底 30% 为耐心）+ 银行总长期借款。
- A2（标准差变体 + 银行长债）：稳定型股权 = 机构持股比例 / 过去 3 年持股标准差；关系型债务 = 银行长期贷款 / (银行贷款 + 应付债券 + 应付票据)。两者求和。代表：[[代飞-2025-耐心资本-双元创新-管理者短视]]。
- A3（标准差变体 + 非流动负债明细）：替换债权侧为更细的非流动负债分项。
- A4（换手率 2 分组 + 总长债）：换手率二分位划分。
- B1（持股时长法）：以机构持股最长持续期为耐心程度。
- B2（持股稳定性中位数法）：以持股稳定性变量是否高于行业中位数划分异质机构投资者。
- C（综合指标 / 熵值法）：将多个 PC 子指标用熵值法合成综合得分。
- D（基金持仓视角）：从基金重仓股稳定性切入。

具体每条变体的 source paper 见各 paper 卡片。

## Construction Steps

A2 操作化（代飞 2025）：

1. 从 CSMAR 长期借款明细取银行长期贷款（剔除非银行机构借款）；
2. 取应付债券 + 应付票据；
3. 关系型债务占比 = 银行长期贷款 ÷ (银行长期贷款 + 应付债券 + 应付票据)；
4. 取机构投资者整体持股比例（CSMAR 机构投资者持股表）；
5. 计算过去 3 年持股比例标准差；
6. 稳定型股权 = 当期持股比例 ÷ 过去 3 年标准差（如标准差为 0 需补救处理）；
7. PC = 关系型债务占比 + 稳定型股权指标。

## Stata Notes

```
* 关系型债务占比
gen relational_debt = bank_long_loan / (bank_long_loan + bond_payable + note_payable)

* 稳定型股权（窗口=3，需 panel sort）
xtset firmid year
bysort firmid: gen inst_ratio_sd = sd(inst_ratio[_n-2 .. _n])
gen stable_equity = inst_ratio / inst_ratio_sd

gen patient_capital = relational_debt + stable_equity
```

## Caveats

- 不同变体间相关性不一定高；选择何种 PC 测算直接影响系数大小与显著性。
- 稳定型股权对 inst_ratio_sd → 0 的小公司极敏感，需缩尾或加 ε。
- 关系型债务侧若忽略非银金融机构（信托、险资），会低估 PC。

## Related

- 项目主题文件：[[../README]] 与 `02_变量字典/测算方法说明.md`。
- 配套被解释变量：[[exploratory-innovation]] · [[exploitative-innovation]]。
- 配套中介：[[managerial-myopia]]。
