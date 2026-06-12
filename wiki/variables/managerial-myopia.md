---
title: "管理者短视主义 (Managerial Myopia)"
slug: "managerial-myopia"
construct: "管理者认知-时间偏好"
role: mediator
measurement: "胡楠等 (2021)：MD&A 文本中 43 个短期视域词词频占比 × 100；代飞 (2025) 在此基础上再 ×100"
data_sources: [上市公司年报 MD&A, CSMAR 公告]
database_tables: [年报全文, MD&A 抽取]
frequency: firm-year
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
available_in_project: true
project_paths: ["../../../03_原始数据/管理者短视主义_2007-2024"]
date_updated: 2026-05-07
---

## Definition

管理者在战略决策中表现出的对短期绩效指标的过度偏好与对长期投资的系统性低估。理论根源：委托代理 + 注意力基础观 + 高阶梯队理论。

## Measurement

主流做法 = 胡楠等 (2021) 文本量化：

1. 通过文本分析与机器学习方法构建中文短期视域词典（最终 43 个词）；
2. 对上市公司年报 "管理层讨论与分析 (MD&A)" 段做分词；
3. 词典法计算短期视域词词频 ÷ MD&A 总词频；
4. × 100（部分研究为线性变换便于读取再 × 100）。

## Data Source

CSMAR 上市公司公告库或巨潮咨讯网下载年报 PDF；需对 MD&A 章节做正则定位与分句切分；中文分词建议 jieba/THULAC + 财经语料。

## Literature Variants

- 胡楠等 (2021)：短期视域词典 + 词频比；本项目主流。
- Brochet, Loumioti & Serafeim (2015)：英文电话会议短期视域词，可作国际对照。
- 部分研究使用研发投入波动 / 投资期限结构作为间接代理。

## Construction Steps

1. 拿到胡楠等 (2021) 已发布的指标（建议直接用，避免重复造轮）；
2. 若自建：抓取年报 → 抽取 MD&A → 分词 → 词频统计 → 词典匹配 → 占比计算。

## Stata Notes

```
use myopia_index.dta, clear
* 视需要做线性放大
gen myopia_x100 = myopia * 100
* 缩尾
winsor2 myopia_x100, replace cuts(1 99)
```

## Caveats

- MD&A 文本质量参差：部分公司模板化套话比重大，会稀释信号。
- 词典法对新词不敏感；建议用胡楠等公开版本而非自建。
- 与 ROE、研发强度等控制变量存在反向因果，做中介需额外考虑。

## Related

- 方法学源头论文：管理者短视主义影响企业长期投资吗（胡楠 2021）— 待 ingest。
- 在项目中直接可用：路径 `03_原始数据/管理者短视主义_2007-2024`。
- 配套使用：[[patient-capital]]（自变量）→ [[managerial-myopia]]（中介）→ [[exploratory-innovation]] / [[exploitative-innovation]]。
