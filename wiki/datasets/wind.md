---
title: "Wind 数据库"
slug: "wind"
provider: "万得信息技术股份有限公司（Wind）"
coverage: "1990 至今；A 股、港股、债券、基金、宏观（EDB）、行业、ESG（含华证）等全模块"
unit: "firm-year / firm-quarter / firm-day / city-year（按子库）"
fields: [财务三表, 公司治理, 机构投资者持股, ESG 评分（含华证 ESG）, 行业指标, 宏观经济 EDB, PE/VC]
project_paths: []
source_papers: [强国令-2025-耐心资本-漂绿]
date_updated: 2026-06-12
---

## Scope

Wind 是国内机构端占有率最高的金融数据终端，覆盖上市公司财务、行情、机构持股、债券、基金、宏观、行业、ESG 等几乎全部经管实证常用数据。学术使用上它与 [[csmar]] 的分工大致是：CSMAR 是面板研究的"底座"（结构化、可批量、文档全），Wind 是"补给站"——终端里现取现用，强项在时效性、宏观 EDB 序列、债券与基金明细、第三方评级转售（如华证 ESG），以及 CSMAR 没有的 PE/VC 股权投资库。

注意 Wind 是按终端账号授权的商业产品，单次提数有流量限制；写论文时大批量面板仍建议以 CSMAR 为主、Wind 取增量字段。

## Fields

强国令-2025-耐心资本-漂绿 主要使用：

- ESG 评分：华证 ESG 评分（实绩端，漂绿测度的一端，参见 greenwashing；评级体系详见 [[hua-zheng-esg]]）。
- 机构持股：换手率、机构投资者持股比例（稳定型股权 Invest 构造）。
- 财务：长期负债、总负债（关系型债权 Debt 构造）及控制变量基础数据，与 [[csmar]] 互补取数。

## Merge Keys

`wind_code` 或 `stkcd` + `report_period` 或 `trade_dt`。Wind 代码带交易所后缀（.SH / .SZ），CSMAR 是纯数字，合并前先转格式、补前导零。

## Cleaning Rules

- 与 CSMAR 合并先统一股票代码格式。
- ESG 评分类字段年中可能多次更新（评级调整），明确取年末快照还是年度均值；华证 2022 年体系升级后历史评级被回溯调整，详见 [[hua-zheng-esg]] 的 Versioning。
- 长期负债 / 总负债比率接近 1 的极端值多为小样本企业，结合 1% / 99% 缩尾。

## Missingness

- 华证 ESG 评分 2010 年前覆盖偏少。
- 新上市公司当年常缺机构投资者换手率指标。

## Access

- 机构版终端按账号订阅，多数财经院校在图书馆或实验室提供公用机位。
- 提供 Excel 插件与 API（量化接口），批量提数受账号流量配额限制。

## Project Files

本项目演示数据未含 Wind 原始导出；复现 强国令-2025-耐心资本-漂绿 需在终端导出华证 ESG 评分与机构投资者换手率。

## Related Variables

- greenwashing 的实绩端评分（华证 ESG）经本库取得。
- patient-capital A4 框架下机构投资者换手率二分组与稳定型股权持股比例可经本库取数。

## Sources

- Wind 官网：<https://www.wind.com.cn/>
- 终端市场地位与功能对比（第三方评测口径）：<https://zhuanlan.zhihu.com/p/528788705>
