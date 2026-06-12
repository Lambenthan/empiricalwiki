---
title: "企业不确定性感知 (Uncertainty Perception, Uncer)"
slug: "uncertainty-perception"
construct: "企业不确定性感知"
role: mediator
measurement: "上市公司年报 MD&A 部分不确定性相关词汇出现频次 / 该部分总词频。"
data_sources: [上市公司年报 MD&A 文本]
database_tables: [年报 PDF, 不确定性词典]
frequency: firm-year
source_papers: [邱蓉-2024-耐心资本-全要素生产率]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

理论构念：企业管理层在年报中表达出的对外部经济、市场、技术、政策、地缘政治等不确定性因素的认知强度。Uncer 越高，管理层越倾向于推迟长周期投资、减少研发投入。

在邱蓉等 (2024) 的内生增长模型中记为 U，作为耐心资本与 TFP 之间的中介变量；同时是验证"耐心资本通过缓冲不确定性提升 TFP"渠道的关键代理。

## Measurement

借鉴聂辉华等 (2020)、Yu et al. (2021)：

1. 收集上市公司年报 PDF。
2. 抽取"管理层讨论与分析"（MD&A）章节文本。
3. 准备不确定性相关词典（如"波动""不确定""动荡""风险""变化"等）。
4. 统计 MD&A 中不确定性词汇出现的频次。
5. Uncer = 不确定性词频 / MD&A 部分总词频。

样本均值 Uncer = 0.086，标准差 0.103，最小 0、最大 1.244。

## Data Source

数据来源不在 [[csmar]]：需要从巨潮资讯网或交易所网站下载年报 PDF，然后用文本工具抽 MD&A 段。CNRDS 与万得也提供文本数据库。

## Literature Variants

- Baker, Bloom, Davis (2016) 经济政策不确定性指数（EPU）：宏观层面的报刊文本指数，与本指标互补。
- Loughran-McDonald 财务文本词典中的 Uncertainty 列表：英文公司 10-K 标准做法。
- 中文不确定性词典（聂辉华等 2020、Yu et al. 2021）：本文采用，更适配中文年报。

## Construction Steps

```
* 步骤 1：下载并解析年报 PDF
* 用 Python 脚本从巨潮资讯网抓取 → pdfplumber 抽取文本
* 定位 "管理层讨论与分析" 段（关键词或 TOC）

* 步骤 2：分词（jieba / THULAC / pkuseg）
import jieba
words = jieba.lcut(mda_text)

* 步骤 3：词典匹配
uncer_dict = ["不确定", "波动", "动荡", "风险", "变化", ...]
n_uncer = sum(1 for w in words if w in uncer_dict)
n_total = len(words)
uncer = n_uncer / n_total
```

最终输出 firmid - year - uncer 长面板，与 CSMAR 财务面板按 stkcd × year 合并。

## Caveats

- 词典选择决定结果：不同论文使用的不确定性词典覆盖度差异大，需明确披露词典内容并稳健性测试。
- MD&A 文本质量参差：早期年份（2008 前）部分公司 MD&A 段较短甚至缺失；样本期建议 ≥ 2010。
- 文本测度只能捕捉"被言说"的不确定性，无法捕捉管理层有意隐瞒或淡化的部分；存在系统性测量误差。
- 与 EPU 等宏观指数相关性高，但企业层面变异更大，多为独立信息。

## Related

- 上游：[[patient-capital]]。
- 下游：[[total-factor-productivity]]。
- 同属机制：[[innovation-efficiency-uncertainty-mediation]]。
- 文献起源：聂辉华等 (2020)、Yu et al. (2021) 是中文不确定性感知文本指标的奠基性工作。
