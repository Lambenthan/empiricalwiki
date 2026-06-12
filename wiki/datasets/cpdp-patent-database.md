---
title: "中国专利数据（CPDP 及上市公司替代来源）"
slug: "cpdp-patent-database"
provider: "CPDP（He et al. 2018，工企-国知局匹配）；上市公司研究常用 CNRDS-CIRD / WinGo 专利库 / CnOpenData / 国家知识产权局"
coverage: "CPDP 本体：1998–2010 中国工业企业-专利匹配；上市公司替代来源多覆盖 1990 年代至今"
unit: "patent-record（可聚合至 firm-year）"
fields: [申请号, 申请年, 授权年, 申请人, 发明人, IPC 分类号, 专利类型（发明/实用新型/外观）, 引用]
project_paths: []
source_papers: [代飞-2025-耐心资本-双元创新-管理者短视]
date_updated: 2026-06-12
---

## Scope

先把名字捋清楚，这是专利数据最容易踩的坑：**CPDP（Chinese Patent Data Project）的标准含义是 He, Tong, Zhang & He (2018) 发布的"中国工业企业-国家知识产权局专利匹配数据"**，覆盖 1998–2010 年，含发明约 33 万条、实用新型约 42 万条、外观约 40 万条，配套论文发表于 *Nature Scientific Data*（DOI: 10.1038/sdata.2018.42）。它匹配的是**工企库**，不是上市公司，且止于 2010 年。

做**上市公司**专利研究（双元创新、绿色创新、专利质量），实际常用的来源是：

- **CNRDS 创新专利系列**（[[cnrds]]）：CIRD（上市公司专利）、CITE（引用）、GPRD/CGPRD（绿色专利）等，已按 stkcd 匹配好。
- **CSMAR 专利研究子库**（[[csmar]]）：上市公司与子公司专利，6 张表覆盖申请 / 授权 / 终止 / 撤回。
- **WinGo 中国专利库**、**CnOpenData**：补充专利质量指标与引用。
- **国家知识产权局检索系统**：原始权威源，需自行做申请人-公司匹配。

文献引用"CPDP"而研究对象是上市公司时，多半实际用的是上述替代源——读论文和写论文时都要把数据出处写到子库级。

## Fields

[[代飞-2025-耐心资本-双元创新-管理者短视]] 关键字段：申请人、申请年、IPC 主分类号，用于构造双元创新指标（按 IPC 与公司既有技术存量的重叠度区分探索式 / 利用式）。

## Merge Keys

申请人名匹配 → 上市公司及子公司清单 → `stkcd`。子公司清单需自建或外购（CSMAR 子公司表 + 工商信息匹配）。

## Cleaning Rules

- 申请人名标准化：去除"有限公司 / 股份有限公司"后缀，统一简繁与空格。
- 一专利多申请人按主申请人归属（或按比例分摊，需写明口径）。
- 撤回 / 视为撤回 / 驳回的申请是否计入，口径必须明示——"申请数"与"授权数"结论可能不同。
- 申请年 vs 授权年：创新产出研究通行用**申请年**（更接近研发完成时点），用授权年要单独说明理由。

## Missingness

- 子公司专利归属是最大不确定性来源，不同论文口径差异大。
- 早期 IPC 分类未细化到 4 位的专利需补码。
- CPDP 本体止于 2010 年；样本期更长的研究必须换用上面列出的替代来源。

## Project Files

无本地副本；按研究对象从 CNRDS / CSMAR / 国家知识产权局 / CnOpenData 接入。

## Related Variables

- [[exploratory-innovation]]、[[exploitative-innovation]] 直接构造自专利 IPC 分类。

## Sources

- He, Tong, Zhang & He (2018), "A database linking Chinese patents to China's census firms", *Nature Scientific Data*：<https://doi.org/10.1038/sdata.2018.42>
- CPDP 匹配数据规模与覆盖说明：<https://www.macrodatas.cn/article/972413285>
- CnOpenData 专利数据：<https://www.cnopendata.com/>
