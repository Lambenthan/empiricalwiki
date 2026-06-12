---
title: "CCER（色诺芬）经济金融数据库——所有权 / 实际控制人"
slug: "ccer-ownership-database"
provider: "色诺芬（CCERDATA）；1999 年起依托北京大学中国经济研究中心建设，2010 年总部迁成都"
coverage: "2001 年正式推出（V1.0）；A 股上市公司实际控制人、最终控股链条、所有权类型"
unit: "firm-year"
fields: [实际控制人名称, 实际控制人类型（国有/民营/外资/集体/其他）, 控股层级, 控制权比例, 现金流权, 两权分离度]
project_paths: []
source_papers: [黎文靖-2015-机构投资者-环境绩效-重污染]
date_updated: 2026-06-12
---

## Scope

CCER 经济金融数据库由色诺芬公司联合北京大学中国经济研究中心建设：1999 年在林毅夫、陈平与耶鲁陈志武指导下立项，2001 年推出 CCERDATA V1.0，对标 CRSP / COMPUSTAT 标准。它是国内最早一批研究型金融数据库，**所有权 / 实际控制人追溯数据是其传统强项**，常用于"最终控制人""金字塔结构""政治关联"研究。

全库现含标准数据（A 股、港股、新三板、货币、行业、宏观、基金、债券等 15 个版块）与特供数据（中国工业企业、海关进出口、县级财政、专利、环境等）。本卡聚焦经管面板最常用的所有权模块。

黎文靖-2015-机构投资者-环境绩效-重污染 用其构造 STATE 变量（实际控制人为国有单位取 1）。

## Fields

- 实际控制人名称；实际控制人类型：国有（中央 / 地方 / 国资委）、民营、外资、集体、其他。
- 终极控制权比例 / 现金流权 / 两权分离度。
- 控股链条（每一级控股公司）。

## Merge Keys

`stkcd × year`（部分子库为 `stkcd × event_date`，需自行扩展为年频）。

## Cleaning Rules

- 国有 vs 非国有以"实际控制人是否为国有单位（国资委、地方政府、央企集团）"为准。
- 注意改制年份：样本期内民营化或重组的公司需逐年判定 STATE，不能一刀切。

## Missingness

- 早期年份（2004–2006）部分公司缺实际控制人字段，可用招股说明书或巨潮资讯网补全。

## Access

- 官网 `www.ccerdata.cn`；高校经图书馆订购，部分高校提供教师个人 VIP 账号（不受 IP 限制）。

## Project Files

无；本项目未直接使用 CCER。[[csmar]]"公司治理"子库提供类似实际控制人字段，常作替代来源。

## Related Variables

- state-ownership-split（所有制异质性分组）。
- [[csmar]]（替代来源）。

## Sources

- 色诺芬官网（公司沿革与库结构）：<https://www.ccerdata.cn/home/company>
- 人民大学图书馆资源页：<https://libproxy.ruc.edu.cn/ermsClient/eresourceInfo.do?rid=346>
