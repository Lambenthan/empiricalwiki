---
title: "同花顺 iFinD 数据库"
slug: "tonghuashun"
provider: "同花顺（Hithink RoyalFlush）iFinD 金融数据终端"
coverage: "1990 至今；A 股、港股、债券、基金、机构投资者、宏观、行业等"
unit: "firm-year / firm-quarter / firm-day / institution-period（按子库）"
fields: [机构投资者持股, 机构投资者交易明细, 财务三表, 行情数据, 基金持仓, 公告事件]
project_paths: []
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
date_updated: 2026-06-12
---

## Scope

同花顺 iFinD 是与 [[wind]] 同类的本土金融数据终端，多数模块覆盖重叠。第三方评测的普遍口径是：功能覆盖约为 Wind 的九成、价格约为一半，API 支持 Python/C++/MATLAB 多语言；另类数据（如 ESG 评级转售）不如 Wind 全。对预算有限的课题组，iFinD 常作为 Wind 的平替或交叉验证源——尤其在机构投资者持股变动明细、基金重仓股变化、公告事件级数据上，两库互为校验。

周绍妮-2017-机构投资者-国企-并购绩效 同时使用 Wind 与同花顺抓取 2010–2014 年机构投资者半年度持股明细，构造换手率三分组（A1 框架）。

## Fields

周绍妮 (2017) 主要使用：

- 机构投资者持股：每期机构投资者编码 × 公司 × 持股股数，计算 CR_buy / CR_Sell 与换手率 CR_{k,t}（详见 stable-institutional-investors-turnover、transactional-institutional-investors-turnover）。
- 基金类型分类：混合 / 债券 / 指数 / 其他，验证 A1 三分组与基金类型的对应。
- 行情数据：股价 P_{i,t}（换手率分母市值标准化），与 [[csmar]] 行情库交叉验证。

## Merge Keys

机构投资者编码 × 股票代码 × 报告期。**同花顺机构编码与 Wind 不一致**，跨库合并先建编码映射表（基金代码可直接对齐，券商 / QFII 按名称匹配）。

## Cleaning Rules

- 机构编码统一：基金代码可对齐；券商自营、信托、保险产品按机构名称模糊匹配。
- 持股股数与持股比例交叉核对（股数 / 总股本 ≈ 披露比例，差额超 0.5% 人工核查）。
- 报告期边界：年报、半年报、季报披露时点不一致，按"半年度末快照"对齐时取最近一次披露。
- 上市不足 1 年的公司机构持股数据通常缺失，按剔除处理。

## Missingness

- 机构投资者交易明细 2009 年以前覆盖不全（周绍妮 2017 样本起 2010 规避此问题）。
- 私募基金在同花顺与 Wind 中覆盖都有限，A1 框架默认仅含公开披露机构。
- 信托、财务公司、企业年金等类别在不同库分类标准不一，需人工类型映射。

## Access

- iFinD 终端按账号订阅，价格低于 Wind，部分高校实验室配有公用账号。
- 提供 Excel 插件与多语言 API。

## Project Files

本项目演示数据未含同花顺原始导出；复现周绍妮 (2017) 需从 iFinD 导出 2010–2014 机构投资者半年度持股明细 + 基金类型分类。

## Related Variables

- stable-institutional-investors-turnover · transactional-institutional-investors-turnover：A1 换手率三分组的交易明细来源。
- institutional-investor-holding：与 [[wind]]、[[csmar]] 交叉验证全口径机构持股。

## Sources

- 同花顺 iFinD 产品页：<https://www.51ifind.com/>
- 终端功能与价格对比（第三方评测口径）：<https://www.zhihu.com/question/33665825>
