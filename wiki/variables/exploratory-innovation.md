---
title: "探索式创新 (Exploratory Innovation)"
slug: "exploratory-innovation"
construct: "双元创新-探索式"
role: dependent
measurement: "IPC 主分类号前 4 位 5 年内未在该企业出现过的专利申请数（张庆垒等 2018）"
data_sources: [CPDP 专利数据库]
database_tables: [专利申请, IPC 分类]
frequency: firm-year
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

聚焦颠覆性技术突破、突破现有知识路径的创新活动。在双元创新框架下与利用式创新相对，对应 March (1991) "exploration"。

## Measurement

主流做法 (张庆垒等 2018)：

- 取每家企业当年专利申请。
- 按 IPC 主分类号前 4 位识别技术领域。
- 设定 5 年时间窗口；若该 IPC4 在过去 5 年中从未在该企业出现，则计入"新进入领域"。
- 探索式创新 = 当年新进入 IPC4 下的专利申请数。

## Data Source

[[cpdp-patent-database]]（CPDP 专利数据库），含申请号、申请年、IPC 全分类号、申请人。

## Literature Variants

- 张庆垒等 (2018) 的 IPC 前 4 位 + 5 年窗口：本项目主流做法。
- 部分论文采用 IPC 前 3 位，扩大技术领域口径。
- 也有用突破性专利前向引用数（前 1% 或前 5%）作为替代度量。

## Construction Steps

1. 抽取专利明细：firm_id, app_year, patent_no, ipc_full。
2. 提取 IPC 前 4 位：`gen ipc4 = substr(ipc_full, 1, 4)`。
3. 对每个 (firm_id, ipc4) 取首次出现年份 first_year。
4. 标记每条专利：`new_field = 1 if app_year < first_year[firm_id, ipc4] + 0` 或 `app_year - first_year >= 5` (如果该 ipc4 在过去 5 年内未出现)。
5. 实际更稳的做法：对每条专利，回看过去 5 年同公司是否申请过该 ipc4，若否则 new_field=1。
6. `bysort firm_id app_year: egen explore = total(new_field)`。

## Stata Notes

```
gen ipc4 = substr(ipc_full, 1, 4)
xtset firm_id app_year
* 用 rangestat 或 rolling 检查 ipc4 是否在过去 5 年出现过
bysort firm_id ipc4: gen first_year_ipc4 = app_year[1]
gen new_field = (app_year - first_year_ipc4 >= 5) | (app_year == first_year_ipc4)
* 复杂滚动窗口建议用 Python 预处理后导回 Stata
bysort firm_id app_year: egen explore = total(new_field)
collapse (max) explore, by(firm_id app_year)
```

## Caveats

- 专利申请≠创新成功；需结合授权数或前向引用做稳健性。
- 跨年同 IPC4 重复申请会被低估为"新领域"，需明确"新"的判定逻辑。
- IPC 系统每隔几年修订，长面板可能存在分类号迁移。

## Related

- [[exploitative-innovation]]（对偶）。
- [[patient-capital]]（核心解释变量）。
- 核心来源论文：[[代飞-2025-耐心资本-双元创新-管理者短视]]。
