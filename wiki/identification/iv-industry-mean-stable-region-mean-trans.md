---
title: "工具变量：同行业其他国企稳定型持股均值（IVINSIND）+ 同省其他国企交易型持股均值（IVINSREG）双 IV"
slug: "iv-industry-mean-stable-region-mean-trans"
strategy_type: iv
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
assumptions:
  - "稳定型机构投资者存在行业投资偏好，本企业 STABLEINS 与同行业其他国企 STABLEINS 均值相关"
  - "交易型机构投资者通过实地调研形成地区投资偏好，本企业 TRANSINS 与同省其他国企 TRANSINS 均值相关"
  - "外生性：同行业 / 同省其他国企的机构投资者持股均值不通过本企业机构持股以外的渠道直接影响本企业并购绩效"
threats:
  - "行业内技术、政策、政府指令同时驱动行业内多个国企的并购决策与机构持股，外生性受挑战"
  - "同省国企可能受同一地方政府干预（如混合所有制改革进度），地区均值与并购绩效存在直接相关"
  - "稳定型机构投资者的地区偏好（蔡宏标和饶品贵 2015）若实际超过行业偏好，则 IVINSIND 与 IVINSREG 不能很好分离两个内生变量"
implementation_notes: "周绍妮 2017 仅在正文中文叙述工具变量结果，未列单独表格；二阶段中 TRANSINS 仍显著为正，结论稳健"
date_updated: 2026-05-07
---

## Identification Problem

STABLEINS 与 TRANSINS 同时进入主回归，存在两类内生性威胁：

1. 反向因果：并购绩效高的国企更易吸引机构投资者持股，导致 STABLEINS / TRANSINS 与 ε 相关；
2. 遗漏变量：未观测的公司治理质量同时影响机构投资者的进出与并购绩效。

主回归虽通过被解释变量差分 + 控制变量滞后部分缓解，但残留偏误难以排除。

## Strategy

借鉴王化成等 (2015)、Kim and Lu (2011)、陆瑶等 (2012) 的"行业 / 地区均值 IV"做法，分别为两个内生变量设计独立工具，避免单一工具同时作为两变量的工具导致欠识别：

- IVINSIND = (Σ_{j ∈ same industry, j ≠ i} STABLEINS_j) / (n_{ind, t} − 1)
  - 用于工具化 STABLEINS。
  - 相关性来源：稳定型机构投资者倾向选择特定行业（如公用事业、金融基础设施等防御性行业），形成行业聚集；同行业其他国企的稳定型机构持股均值与本企业稳定型机构持股相关。

- IVINSREG = (Σ_{j ∈ same province, j ≠ i} TRANSINS_j) / (n_{reg, t} − 1)
  - 用于工具化 TRANSINS。
  - 相关性来源：交易型机构投资者通过密集实地调研获取私有信息（蔡宏标和饶品贵 2015；谭劲松和林雨晨 2016），调研半径受地理距离制约，形成地区聚集；同省其他国企的交易型机构持股均值与本企业交易型机构持股相关。

二阶段最小二乘 (2SLS)：

- 第一阶段：
  - STABLEINS = π_{1,0} + π_{1,1}·IVINSIND + π_{1,2}·IVINSREG + Controls + Year + u_1
  - TRANSINS  = π_{2,0} + π_{2,1}·IVINSIND + π_{2,2}·IVINSREG + Controls + Year + u_2
- 第二阶段：
  - ΔADJ_ROE = β₀ + β₁·STABLE\_hat + β₂·TRANS\_hat + Controls + Year + ε

## Key Assumptions

- 相关性：IVINSIND 显著影响本企业 STABLEINS、IVINSREG 显著影响本企业 TRANSINS；联合 F 通过弱工具阈值。
- 外生性：
  - 同行业其他国企的稳定型机构持股均值不通过本企业 STABLEINS / TRANSINS 之外的渠道（如行业政策、技术外溢）影响本企业并购绩效；
  - 同省其他国企的交易型机构持股均值不通过本企业 STABLEINS / TRANSINS 之外的渠道（如地方政府混合所有制改革进度）影响本企业并购绩效。
- 排他性：模型已包含 SIZE / LEV / ROA / SH1 等控制变量，部分阻断行业 / 地区层面的可观测共同冲击；不可观测共同冲击仍是潜在威胁。

## Implementation

```stata
* 行业代码用 CSRC 一级或二级；地区代码用注册地省份（不含直辖市层级混淆）
bysort industry year: egen sum_stable = total(STABLEINS)
bysort industry year: egen n_ind      = count(STABLEINS)
gen IVINSIND = (sum_stable - STABLEINS) / (n_ind - 1)

bysort province year: egen sum_trans = total(TRANSINS)
bysort province year: egen n_reg     = count(TRANSINS)
gen IVINSREG = (sum_trans - TRANSINS) / (n_reg - 1)

* 双内生变量 2SLS（每个内生变量都允许两个工具一起做线性投影）
ivreg2 adj_dROE (STABLEINS TRANSINS = IVINSIND IVINSREG) ///
       SH1 ID LEV CASH RMA PT SIZE ROA i.year, robust first
estat firststage
```

## Diagnostics

- 周绍妮 (2017) 正文仅简述"二阶段交易型机构投资者持股与并购绩效仍显著正相关，结论稳健"，未给出第一阶段 F、Cragg-Donald F、Sargan / Hansen 等具体统计量；
- 复现时建议补报 Kleibergen-Paap rk F（双内生变量推荐 ≥ 10）以及 Hansen J（仅当工具数 > 内生变量数时可做过度识别）。

## Limitations

- 工具数 (2) = 内生变量数 (2) → 模型恰好识别，无法做 Hansen J 过度识别检验；
- "行业稳定型 + 地区交易型"的工具分配假设两类机构投资者偏好不交叉；若稳定型也有地区偏好或交易型也有行业偏好（实际中均存在），工具分配不严格分离两个内生变量；
- 论文未列工具变量结果详细表，复现透明度不足；建议在本项目复现时单独列表报告 first stage、second stage、F 检验结果。
- 国企子样本中行业 / 省份内观测较少时，均值波动大，IV 弱化。

## Related

- 主用论文：[[周绍妮-2017-机构投资者-国企-并购绩效]]
- 主回归：[[ols-cross-section-ma-event]]
- 同类思路：[[iv-industry-mean-pc-excluding-self]]（耐心资本研究中的单内生变量行业均值 IV）
