---
title: "我国 A 股重污染行业上市公司样本（2004-2010 年报附注手工收集环境资本支出）"
slug: "heavy-pollution-industry-sample"
provider: "上市公司年报手工收集 + CSMAR + CCER"
coverage: "2004-2010 年；A 股市场 8 个重污染行业；3,843 个企业-年观测"
unit: "firm-year"
fields: [stkcd, year, env_capex, INST, INST_LONG, INST_SHORT, BHAR, ΔLOAN, LCOST, ETR, STATE, 一般公司财务指标]
project_paths: []
source_papers: [黎文靖-2015-机构投资者-环境绩效-重污染]
date_updated: 2026-05-07
---

## Scope

- 期间：2004-2010 年。
- 样本：A 股市场 8 个重污染行业上市公司——采掘业、纺织服装皮毛业、金属非金属业、生物医药业、石化塑胶业、造纸印刷业、水电煤气业、食品饮料业。
- 总观测数：3,843 个企业-年（在变量缺失剔除后；BHAR 和 LCOST 等子模型样本量略小，分别为 3,562 和 3,159）。
- 黎文靖 (2015) 的「8 个重污染行业」是该论文使用的早期划分，与生态环境部 2010 年后公布的 16 类重污染行业目录有差异。

## Fields

核心字段（黎文靖 2015 实际使用）：

- **手工收集**：env_capex（环境资本支出，从年报「在建工程」附注识别环保相关借方增加额）
- **CSMAR**：所有财务变量（ROA、DR、SGROW、SIZE、MKTB、AGE、MORTGAGE、INVINT、BETA、VOL、TRSHARE 等）、机构投资者持股（INST 及流动率分类后的 INST_LONG / INST_SHORT）、董事会信息（IDRATIO、BSIZE、TOP1）、贷款信息（短期+长期银行借款、利息支出）、所得税费用与利润总额。
- **CCER**：实际控制人 / 所有权类型（用于构造 STATE）。

派生字段：

- LNENV = ln(1+env_capex)
- ENV_DUM = 1[env_capex > 0]
- ΔLOAN = (短期借款+长期借款−上期短期借款−上期长期借款)/期初总资产
- LCOST = 利息支出/银行借款平均余额
- ETR = 所得税费用/利润总额（按论文规则截尾到 [0,1]）

## Merge Keys

- stkcd（股票代码）+ year
- CSMAR 与 CCER 通过 stkcd 合并；手工 env_capex 通过 stkcd × year 回填。

## Cleaning Rules

- 剔除变量缺失观测。
- 所有连续变量上下 1% Winsorize。
- ETR：分子为负设 0；分母为负或 ETR>1 设 1（参照 Adhikari et al., 2006）。
- 行业筛选：保留属于 8 个重污染行业的样本，按公司主营业务分类。

## Missingness

- env_capex：年报附注未披露的视为缺失而非 0；论文未明确披露「未披露」如何处理。本项目复现需谨慎区分。
- INST_LONG/INST_SHORT：因流动率三分位法需要机构投资者持续 ≥2 年的数据，部分早期年份观测被分类为「其他机构」（即未分类）。

## Project Files

无；本数据集仅作为黎文靖 (2015) 的样本范围记录，未在本项目内复现。如需复现：

1. 重新从 CSMAR 提取 8 个重污染行业 2004-2010 年面板。
2. 从 CSMAR 财务报表附注或同花顺年报全文识别 env_capex。
3. 与 CCER 所有权数据合并。

## Related Variables

- [[environmental-performance]]（LNENV、ENV_DUM 的构造来源）
- [[institutional-ownership]]（INST、INST_LONG、INST_SHORT）
- [[csmar]]（财务、机构持股数据）
- [[ccer-ownership-database]]（所有权数据，本论文核心异质性切分依据）
