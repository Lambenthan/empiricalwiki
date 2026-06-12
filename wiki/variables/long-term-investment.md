---
title: "企业长期投资 (Long-term Investment)"
slug: "long-term-investment"
construct: "企业经营性、跨会计年度的内生增长投入"
role: dependent
measurement: "胡楠等 (2021)：分两路。Capex = 资本性支出 / 总资产；R&D = 研发支出 / 营业收入。稳健性下另有 Capex2/Capex3 与 R&D2 等替代口径"
data_sources: [CSMAR, 上市公司年报]
database_tables: [现金流量表, 利润表, 资产负债表]
frequency: firm-year
source_papers: [胡楠-2021-管理者短视主义-长期投资-文本分析]
available_in_project: true
project_paths: ["../../../基础数据"]
date_updated: 2026-05-07
---

## Definition

企业对内的、具有经营性质、创造经济收益的期间超过一个会计年度的投资（胡楠等 2021）。具体由两条主线构成：

1. 资本支出（Capex）：购建使用年限超过一个会计年度的资产（固定资产、无形资产、其他长期资产）而发生的净支出。
2. 研发支出（R&D）：当年研发投入。

二者共同特征：投入在前、收益在后；产出不确定；收益具有跨期性（Quirin and Wiginton 1981；Pindyck 1982；Zaheer et al. 1999）。这使得长期投资在短视管理者偏好中往往被系统性低估。

## Measurement

【主测度】（胡楠等 2021，借鉴吕长江、张海平 2011；张兆国等 2014；虞义华等 2018）：

资本支出（Capex / Assets）：

```
Capex_it = [购建固定资产、无形资产和其他长期资产支付的现金
            + 取得子公司及其他营业单位支付的现金净额
            - 处置固定资产、无形资产和其他长期资产收回的现金净额
            - 处置子公司及其他营业单位收到的现金净额
            - (固定资产折旧 + 无形资产摊销 + 长期待摊费用摊销)] / 年末总资产
```

研发支出（R&D / Revenue）：

```
R&D_it = 当年研发支出 / 营业收入
```

研发费用缺失用 0 代替（胡楠等 2021）。

【稳健性测度】：

- Capex2 = 固定资产净值的改变量 / 年初总资产（李焰等 2011）。
- Capex3 = (固定资产 + 长期投资 + 无形资产) 净值改变量 / 年初总资产（李万福等 2011）。
- R&D2 = 当年研发支出 / 总资产。
- R&D3 = R&D 但删除研发支出缺失样本（不用 0 填充）。

【投资效率】：Capex_Residual = Richardson (2006) + 吕长江、张海平 (2011) 预期投资模型的残差绝对值，越大代表投资效率越低：

```
Capex_it = α₀ + α₁·TBQ_{i,t-1} + α₂·Lev_{i,t-1} + α₃·Cash_{i,t-1} + α₄·AGE_{i,t-1}
         + α₅·SIZE_{i,t-1} + α₆·YRET_{i,t-1} + α₇·Capex_{i,t-1} + ΣYear + ΣIndustry + ε
```

## Data Source

- CSMAR：现金流量表（购建/处置长期资产现金流）、利润表（研发支出、营业收入）、资产负债表（总资产、固定资产、无形资产、长期投资）。
- 上市公司年报：研发支出在 2007 年新会计准则后必须披露，但仍存在缺失；早期年份缺失率高。

## Literature Variants

| 变体 | 出处 | 备注 |
|------|------|------|
| Capex / 总资产 | 胡楠等 (2021)；吕长江、张海平 (2011) | 主测度 |
| Capex2（固定资产净值变化 / 年初总资产） | 李焰等 (2011) | 稳健性 |
| Capex3（固定资产+长期投资+无形资产净值变化 / 年初总资产） | 李万福等 (2011) | 稳健性 |
| R&D / 营业收入 | 胡楠等 (2021)；张兆国等 (2014) | 主测度，缺失填 0 |
| R&D / 总资产 | 胡楠等 (2021) 稳健性 | 替代分母 |
| 投资效率（Capex_Residual） | Richardson (2006)；吕长江、张海平 (2011) | 用于中介机制 |

## Construction Steps

1. 从 CSMAR 现金流量表抽取购建固定资产、无形资产、其他长期资产的现金支付与收回；处置子公司净额；折旧摊销分项。
2. 按公式合并为当年净资本性支出，除以年末总资产得到 Capex。
3. 从 CSMAR 财务附注或主表抽取当年研发支出，除以营业收入得到 R&D；缺失填 0。
4. 稳健性时计算 Capex2、Capex3、R&D2 与 R&D（不填 0 版本）。
5. 投资效率：先估预期投资模型 → 取残差 → 取绝对值。
6. 全部连续变量上下 1% 缩尾。

## Stata Notes

```stata
* Capex
gen capex_raw = 购建长期资产现金 + 取得子公司净额 ///
              - 处置长期资产现金 - 处置子公司净额 ///
              - 折旧 - 无形摊销 - 长期待摊摊销
gen Capex = capex_raw / total_assets
winsor2 Capex, replace cuts(1 99)

* R&D
gen RD = rd_expense / revenue
replace RD = 0 if missing(rd_expense)
winsor2 RD, replace cuts(1 99)

* 投资效率
reghdfe Capex L.TBQ L.Lev L.Cash L.AGE L.SIZE L.YRET L.Capex, absorb(industry year) resid
predict res, residuals
gen Capex_Residual = abs(res)
```

## Caveats

- R&D 缺失填 0 与不填两种处理在研发不密集行业差异明显；应同时报告。
- Capex 公式包含子公司收购净额，会受 M&A 大额事件冲击；是否剔除并购年份是常见稳健性。
- 折旧/摊销使用账面值还是当期计提需注意：胡楠等 (2021) 使用当期计提项。
- 行业差异：制造业 Capex 高、服务业研发占营收比可能更高，行业 FE 必备。
- 长期投资本身可能存在过度投资，研究中介路径时应考虑投资效率而非仅看绝对水平（胡楠等 2021）。

## Related

- 主源头论文：[[胡楠-2021-管理者短视主义-长期投资-文本分析]]
- 自变量配套：[[managerial-myopia]]（短视抑制长期投资）· [[patient-capital]]（耐心资本促进长期投资）
- 数据源：[[csmar]]
- 应用论文：[[代飞-2025-耐心资本-双元创新-管理者短视]]（用专利创新度量长期投资的另一条路径）
