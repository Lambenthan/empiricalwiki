---
title: "融资融券试点 DID（卖空机制外生冲击）"
slug: "did-short-selling-pilot"
strategy_type: did
source_papers: [杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]
assumptions:
  - 融资融券标的扩容相对于个股崩盘风险为外生事件
  - 处理组与对照组的崩盘风险变化在试点前满足平行趋势
  - 标的扩容时点不存在与机构投资者类型相关的预期效应
threats:
  - 标的扩容选样偏差（市值高、流动性好的股票优先入选）
  - 同期可能存在其他监管政策共变
  - 三重交互的解释依赖 INVW 子样本切分本身的有效性
implementation_notes: "三重交互形式：Crash = γ1 INVH×SSC×After + γ2 INVH×SSC + γ3 SSC×After + γ4 INVH + γ5 SSC + γ6 INVW + 控制变量 + Year + Ind。在稳定型/交易型子样本分别估计，γ1 即三重交互系数，反映卖空机制对'机构投资者-崩盘风险'关系的调节方向。"
date_updated: 2026-05-07
---

## Identification Problem

机构投资者持股、机构投资者类型与股价崩盘风险之间存在多重内生关系：稳定型机构投资者可能选择本身崩盘风险低的公司持股；崩盘风险也可能反向影响机构投资者交易行为。需要外生变化识别"卖空机制松绑"对"机构投资者-崩盘风险"关系的因果调节作用，而非简单 OLS 截面相关。

## Strategy

利用 2010 年 3 月 31 日中国证监会启动融资融券试点这一准自然实验：

- 处理组：被纳入融资融券标的池的股票（SSC=1）。
- 对照组：未被纳入的股票（SSC=0）。
- 时间维度：股票纳入两融之后的年度（After=1）vs 之前（After=0）。
- 三重交互 INVH × SSC × After 识别卖空机制对机构投资者持股与崩盘风险关系的调节效应。
- 在 INVW=1（稳定型）和 INVW=0（交易型）子样本中分别估计，对比两类机构投资者下三重交互系数的方向与幅度。

## Key Assumptions

1. 标的扩容时点对个股崩盘风险外生：扩容选股标准是市值与流动性，不直接以未来崩盘风险为依据。
2. 平行趋势：处理组与对照组在试点前的崩盘风险变化趋势相近。
3. SUTVA：标的扩容对未纳入股票无溢出效应（实际上溢出可能存在，本文未单独检验）。

## Implementation

模型 (7)：

```
Crash_{i,t} = γ0 + γ1 INVH_{i,t-1}*SSC_{i,t-1}*After_{i,t-1}
            + γ2 INVH_{i,t-1}*SSC_{i,t-1}
            + γ3 SSC_{i,t-1}*After_{i,t-1}
            + γ4 INVH_{i,t-1}
            + γ5 SSC_{i,t-1}
            + γ6 INVW_{i,t-1}
            + γ7 Ret + γ8 Sigma + γ9 Roa + γ10 Lev + γ11 Tobin'q
            + γ12 Dturn + γ13 Size + γ14 Accm + γ15 Year + γ16 Ind
            + ε_{i,t-1}
```

在 INVW=1 与 INVW=0 子样本下分别 OLS 估计，被解释变量为 Ncskew 或 Duvol。稳健性以 IsCrash 替代被解释变量，做 Logistic 回归。

## Diagnostics

本文未明确报告平行趋势检验、安慰剂检验等 DID 标准诊断，是该论文的一个识别短板。复现时建议补：
- 试点前年度交叉项的不显著（pre-trend）。
- 安慰剂时点（虚构 2009 年作为试点）做反事实检验。
- 使用 PSM 配对处理组与对照组后再 DID。

## Limitations

- 标的扩容选样有市值/流动性偏向，处理组与对照组并非随机分配。
- 三重交互系数解释依赖 INVW 子样本切分的有效性；若 B2 框架对类型识别有误，DID 结论会被污染。
- 本文未单独估计两融对崩盘风险的主效应（仅作交互项的一部分），无法回答"卖空机制本身是否抑制崩盘"的独立问题。

## Related

- 文献：[[杨棉之-2020-机构投资者异质性-卖空机制-股价崩盘风险]]
- 配套变量：[[short-selling-eligibility]] · [[institutional-investor-holding]] · [[institutional-investor-heterogeneity-stability]]
