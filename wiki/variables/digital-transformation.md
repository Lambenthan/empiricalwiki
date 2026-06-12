---
title: "企业数字化转型 (Digital Transformation)"
slug: "digital-transformation"
construct: "企业数字化转型"
role: core_explanatory
measurement: "李心武 (2025) 基准用 ln(企业当年独立申请的数字经济专利数 + 1)；稳健性中替换为 (a) 独立 + 联合申请的数字经济专利总量 + 1 取对数；(b) 财务报表附注中数字经济相关无形资产占年末无形资产总额之比；(c) 上市公司年报文本中数字化转型相关词汇词频 + 1 取对数。"
data_sources: [CNRDS 数字化转型数据库, 上市公司年报文本, 上市公司财务报表附注]
database_tables: [数字经济专利, 上市公司年报全文, 无形资产明细]
frequency: firm-year
source_papers: [李心武-2025-耐心资本-数字化转型-价值发现]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

企业数字化转型指企业利用大数据、人工智能、云计算、区块链等数字技术重塑生产、运营、销售与治理流程的过程。理论上对应"竞争优势理论"中传统生产要素驱动能力受限时，企业借助数字技术从根本上提升竞争力的战略路径（赵宸宇等，2021）。

## Measurement

李心武 (2025) 在 D 框架（基金持仓视角）下采用专利驱动的客观度量，避免年报文本测度受到"多言寡行"策略性披露的污染：

- **基准 Digital_{j,t}** = ln(企业 j 在 t 年独立申请的数字经济专利数量 + 1)。参考黄勃等 (2023)。
- **稳健性度量 1（Digital1）** = ln(企业当年独立申请 + 联合申请的数字经济专利总量 + 1)。
- **稳健性度量 2（Digital2）** = 企业财务报表附注中与数字经济相关的无形资产 / 年末无形资产总额。
- **稳健性度量 3（Digital3）** = ln(上市公司年报文本中数字化转型相关词汇词频 + 1)。参考吴非等 (2021)。

为捕捉策略性披露行为，作者额外构造：

- **言（Talk Level）**：年报数字化转型相关词频，与同行业同年度中位数比较。
- **行（Action Level）**：独立申请的数字经济专利数，与同行业同年度中位数比较。
- **多言寡行 TMAL** = 1 当 Talk = 1 且 Action = 0；否则 = 0。

## Data Source

数字经济专利来自 [[cnrds]]（中国研究数据服务平台）数字经济专利子库。年报文本词频从巨潮资讯网公开年报抽取后用分词工具统计。无形资产明细来自财务报表附注。

## Literature Variants

- **吴非等 (2021)**：年报文本词频路径，是国内最早大范围使用的数字化转型代理；优点是覆盖面广，缺点是受年报"披露策略"影响。
- **黄勃等 (2023)**：数字经济专利路径，是李心武 (2025) 的基准；强调"行"端事实，受策略性披露影响小。
- **李哲等 (2024)、李鑫等 (2024)**：发现年报词频度量存在"多言寡行"策略性披露问题，提出 Talk × Action 二维分类。
- **谢婷婷-2025**、**储佩佩-2025** 等本项目耐心资本论文：多采用年报词频构造数字化转型综合指数。

李心武 (2025) 的特殊贡献：把"言"与"行"两类度量同时进入模型，用交乘项 TMAL × Digital 检验耐心资本能否识别策略性披露，是 D 框架下的方法论亮点。

## Construction Steps

基准度量（Digital）：

1. 从 [[cnrds]] 数字经济专利子库取 t 年企业独立申请的数字经济专利数 N_{j,t}。
2. 计算 Digital_{j,t} = ln(N_{j,t} + 1)。

多言寡行 TMAL：

1. 计算 t 年企业 j 的"言" Talk_{j,t}（年报数字化词频）与同行业同年度中位数比较，得到 Talk = 1 / 0。
2. 计算 t 年企业 j 的"行" Action_{j,t}（独立数字经济专利数）与同行业同年度中位数比较，得到 Action = 1 / 0。
3. TMAL = 1 if Talk = 1 and Action = 0; else TMAL = 0。

## Stata Notes

```stata
gen Digital  = ln(digi_patent_indep + 1)
gen Digital1 = ln(digi_patent_total + 1)
gen Digital2 = digi_intangible / total_intangible
gen Digital3 = ln(digi_word_freq + 1)

bysort indcd year: egen talk_med   = median(digi_word_freq)
bysort indcd year: egen action_med = median(digi_patent_indep)
gen Talk   = digi_word_freq    > talk_med
gen Action = digi_patent_indep > action_med
gen TMAL   = (Talk == 1 & Action == 0)
```

## Caveats

- "言"端度量必须与"行"端度量分开报告，否则在二级市场样本中可能放大策略性披露的偏误。
- 数字经济专利数量在科技密集型行业天然偏高，跨行业比较时需控制行业固定效应或做行业内中位数划分。
- 财务报表附注路径（Digital2）样本损失较大，仅适合作为稳健性。

## Related

- variables：[[patient-capital]]
- datasets：[[cnrds]] · [[csmar]]
- models：[[two-way-fixed-effects-firm-year]]
- papers：[[李心武-2025-耐心资本-数字化转型-价值发现]]
