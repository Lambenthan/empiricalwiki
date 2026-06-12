---
title: "Stata 执行计划：耐心资本对企业绿色化转型的影响"
slug: "stata-plan-pc-green-transformation-2026-06-03"
topic: "patient-capital → green transformation"
date: 2026-06-03
generated_by: "/stata-plan --write-do"
source_design: "outputs/empirical-design-pc-green-transformation-2026-06-03.md"
do_skeleton: "outputs/stata-plan-pc-green-transformation-2026-06-03.do"
---

# Stata 执行计划：耐心资本对企业绿色化转型的影响

> 本计划忠实于 `outputs/empirical-design-pc-green-transformation-2026-06-03.md`（唯一权威 spec）。
> 变量名优先采用 blank 项目真实数据底座（`05_分析代码/耐心资本-全套代码.do` + `03_原始数据/_数据字典.md`）中已存在的字段。底座中没有、设计中也未给出确定来源的变量，一律用占位符并标「需确认」，不假造。
> 配套 do 骨架见 `outputs/stata-plan-pc-green-transformation-2026-06-03.do`，本计划与 do 文件逐节对应。

## 安装的外部命令

```stata
ssc install reghdfe, replace      // 高维固定效应
ssc install ftools, replace        // reghdfe 依赖
ssc install ivreghdfe, replace     // 含高维 FE 的 IV/2SLS
ssc install ranktest, replace      // ivreghdfe 弱识别检验依赖
ssc install winsor2, replace       // 缩尾
ssc install xtabond2, replace      // 系统 GMM
ssc install estout, replace        // esttab 表格导出
ssc install rangestat, replace     // 三年滚动标准差（熵值法已用）
ssc install distinct, replace      // 唯一性核查（可选）
```

> reghdfe 报「command unrecognized」时，按底座 do 注释先 `ssc install`；`ivreghdfe` 依赖 `ranktest` 与 `ivreg2`，缺哪个补哪个。

---

## 1. 输入数据

| 文件 | 来源 | 关键字段（真实名） | 角色 |
|---|---|---|---|
| `04_中间数据/耐心资本_七合一_WZY.dta` | blank 熵值法成品 | `stkcd year 耐心资本_YS 耐心资本_Score_*`（含短视版）、`战略型投资者1_2012_2024`(B1)、`稳定型股权3`(A4)、`关系型债权1` | 核心解释变量 Pat / PC_B1 / Debt |
| `04_中间数据/熵值法汇总.dta` | blank 熵值法 7 指标半成品 | `投资者长期持股比例 投资者短期持股比例 稳定型股权2 长期资本负债率 企业短期财务杠杆 资本增长保持率 Fullratio2` | **重算「剔除短视版」熵值 Pat 的输入**（见第 4 节） |
| `03_原始数据/A_财务报表/FS_Combas.dta` | CSMAR | `Stkcd Accper Typrep A001000000`(资产总计) `A002000000`(负债合计) | 控制变量 Size / Lev |
| `03_原始数据/A_财务报表/FS_Comins.dta` | CSMAR | `Stkcd Accper Typrep B001101000`(营业收入) | Growth |
| `03_原始数据/B_公司治理与股权/BDT_ManaGovAbil.dta` | CSMAR | `Symbol Enddate PropertyRightsNature Boardsize`（`Mngmhldn`） | 产权异质性 STATE / 治理 |
| `03_原始数据/B_公司治理与股权/EN_EquityNatureAll.dta` | CSMAR | `Symbol EquityNature Seperation`(两权分离率) | 产权异质性（备） |
| `03_原始数据/B_公司治理与股权/HLD_CR.dta` | CSMAR | `Stkcd Reptdt Shrcr1`(第一大股东) `Shrcr4`(前十大之和) | 控制变量 Top1 + **主 IV** |
| `03_原始数据/C_创新与融资约束/BDT_FinConstKZ.dta` | CSMAR | `Symbol STPT IsNewOrSuspend ISBSE KZ` | 机制变量 KZ（替代 WW）+ 样本筛选标记 |
| `03_原始数据/C_创新与融资约束/PT_LCRDSPENDING.dta` | CSMAR | `Symbol Source StateTypeCode RDSpendSum RDSpendSumRatio` | 控制（可选 RD） |
| `03_原始数据/D_行业与市场/INDFI_HHI.dta` | CSMAR | `IndustryCode Markettype HHI_A HHI_B HHI_C HHI_D` | 行业竞争异质性 |
| `03_原始数据/D_行业与市场/STK_LISTEDCOINFOANL.dta` | CSMAR | `Symbol EndDate IndustryCodeD IndustryNameD EstablishDate LISTINGDATE PROVINCE` | FirmAge / 行业 / 省份回填 |
| `03_原始数据/管理者短视主义_2007-2024/MD&A-管理者短视主义/管理者短视主义.dta` | 胡楠 2021 | `Scode Year Fullratio2`(MD&A 版) | **机制主口径 Myopia** |
| `03_原始数据/E_ESG与绿色/上市公司绿色化转型指数_2007-2024/绿色化转型指数_合并版.xlsx` | 项目成品 | 证券代码 / 年份 / 绿色化转型指数 | **稳健性对照**（成品指数，非词频主口径） |
| 词频成品 `green_freq.dta`（**需生成**） | CSMAR 年报全文 + 113 词字典 | `stkcd year freq` | **被解释变量主口径 Green = LN(freq+1)** |

> **关键缺口（需确认 / 需复刻）**：被解释变量主口径是「113 词词频 LN(freq+1)」（解学梅、朱琪玮 2021）。blank 底座目前只有**成品绿色化转型指数 xlsx** 和 `上市公司绿色转型关键词.txt`，**没有逐企业词频 dta**。113 词字典与年报全文分词须先在 Python 端复刻落盘为 `green_freq.dta`（设计第 6.3 节步骤 1、第 14 节第 2 条）。在该文件就位前，主回归先用成品指数占位跑通流程，标「需确认主口径」。

---

## 2. 主键与合并顺序

主键统一为 `stkcd`(数值) × `year`(数值)。各源主键差异需先对齐：

- CSMAR 财务/治理表用 `Stkcd`/`Symbol` + `Accper`/`Enddate`/`EndDate`/`Reptdt`，须 `keep if strmatch(Accper,"*-12-31")`（合并报表再 `keep if Typrep=="A"`），再 `gen year=real(substr(...,1,4))`、`gen stkcd=real(Symbol/Stkcd)`。
- 管理者短视表主键是 `Scode Year`，重命名为 `stkcd year`。
- HHI 表主键是行业×市场×年（**需确认**其精确时间字段名），按 `IndustryCodeD`(回填到企业) × year 合并，非 1:1。

合并骨架（全部 `merge 1:1 stkcd year`，主表为词频/指数面板）：

```stata
use green_freq.dta, clear        // 或成品指数（需确认主口径）
merge 1:1 stkcd year using "04_中间数据/耐心资本_七合一_WZY.dta", keep(master match) gen(_m_pc)
merge 1:1 stkcd year using pat_no_myopia.dta,   keep(master match) gen(_m_patnm)   // 剔除短视版
merge 1:1 stkcd year using myopia_mda.dta,      keep(master match) gen(_m_myo)
merge 1:1 stkcd year using kz.dta,              keep(master match) gen(_m_kz)
merge 1:1 stkcd year using fin.dta,             keep(master match) gen(_m_fin)     // Size/Lev/Growth/ROE
merge 1:1 stkcd year using gov.dta,             keep(master match) gen(_m_gov)     // Top1/STATE/Indep/Dual
merge m:1 IndustryCodeD year using hhi.dta,     keep(master match) gen(_m_hhi)     // 行业层非 1:1
```

**复核点**：每步 merge 后 `tab _m_*`，确认 `match` 占比与 `master only` 行数；记录哪些源覆盖不全（机构持股 2007 前覆盖差）。

---

## 3. 样本筛选

```stata
* 剔除金融保险（行业代码 J 开头）；行业字段需确认（IndustryCodeD 或 SIC）
drop if substr(IndustryCodeD,1,1)=="J"          // 需确认行业代码字段与前缀规则
* 剔除 ST/*ST：BDT_FinConstKZ 自带 STPT 标记，直接用
drop if STPT==1                                  // 需确认 STPT==1 是否表示"剔除"
* 剔除上市不足 2 年；熵值法含 3 年滚动标准差，前期观测自然受限
drop if year - year(LISTINGDATE) < 2            // LISTINGDATE 为日期型需先取年
* 剔除北交所（若不纳入）
drop if ISBSE==1                                 // 需确认
* 样本区间：主口径 2012—2023（与谢婷婷 2025 对齐）
keep if inrange(year,2012,2023)
* 关键变量缺失剔除
drop if missing(green) | missing(Pat)
```

**复核点**：每条 `drop` 后 `count`；最终 `count` 与设计预期 25000—30000 区间比对。

---

## 4. 变量构造

### 4.1 被解释变量

```stata
gen green = ln(freq + 1)          // 主口径，freq 来自 green_freq.dta（需确认）
* 稳健 1：绿色 TFP（lngtfp）——需 SBM-ML 外部测算，本项目暂缺，标"需确认"
* 稳健 2/对照：漂绿 GWS——需华证 ESG，本项目部分可得，仅稳健性
```

### 4.2 核心解释变量（熵值法 C 框架 · 两版）

**含短视版（基线主回归用）**——直接取底座成品：

```stata
gen Pat = 耐心资本_YS              // 逐年熵值法主口径（底座已含 Fullratio2 短视指标）
* 备选：耐心资本_Score_2012 等混合熵值法版本（需确认与样本区间匹配）
```

**剔除短视版（管理者短视中介检验专用）**——重算熵值，**从 7 指标中剔除 `Fullratio2`**。这是计划中最关键的一步：底座 `耐心资本_YS` 的负向指标集含 `Fullratio2`，若做 PC→Myopia→Green 时仍用含短视版 Pat，自变量内含中介变量，会造成机械中介（设计第 5.2 节注、第 9 节技术注意）。

落实方式 = 复用底座 9.7 节逐年熵值法循环，**唯一改动是把 `Fullratio2` 从 `negative_var` 中删除**，其余标准化/熵权/合成逻辑原样保留，输出变量另命名 `耐心资本_YS_nomyopia` 存为 `pat_no_myopia.dta`：

```stata
* —— 剔除短视版熵值法（基于 04_中间数据/熵值法汇总.dta 重算）——
forvalues z=2007/2024 {
    use "04_中间数据/熵值法汇总.dta", clear
    keep if year==`z'
    * 注意：剔除短视版的缺失值清理与缩尾【不再包含 Fullratio2】
    foreach i in 投资者长期持股比例 投资者短期持股比例 稳定型股权2 ///
                 长期资本负债率 企业短期财务杠杆 资本增长保持率 {
        drop if `i'==.
    }
    winsor2 投资者长期持股比例 投资者短期持股比例 稳定型股权2 ///
            长期资本负债率 企业短期财务杠杆 资本增长保持率, cut(1 99) replace
    * 正向指标不变；负向指标【删去 Fullratio2】
    global positive_var 投资者长期持股比例 稳定型股权2 长期资本负债率 资本增长保持率
    global negative_var 投资者短期持股比例 企业短期财务杠杆            // ← 不含 Fullratio2
    global all_var $positive_var $negative_var
    * …（标准化 → 比重 → 信息熵 → 权重 → 综合得分，逻辑与底座 9.7 节完全一致）…
    rename Score 耐心资本_YS_nomyopia
    keep stkcd year 耐心资本_YS_nomyopia
    save 逐年熵值法_nomyopia`z'.dta, replace
}
use 逐年熵值法_nomyopia2007.dta, clear
forvalues i=2008/2024 { append using 逐年熵值法_nomyopia`i'.dta }
save pat_no_myopia.dta, replace
```

**复核点**：`corr 耐心资本_YS 耐心资本_YS_nomyopia` 应高但 < 1；两版权重表对比，确认剔除 `Fullratio2` 后其余 6 指标权重重新归一。机制回归一律用 `Pat_nm = 耐心资本_YS_nomyopia`，基线/异质性/稳健用含短视版 `Pat`。

**替换口径（稳健性）**：

```stata
gen PC_B1   = 战略型投资者1_2012_2024      // B1 持股时长法，与样本区间对齐（需确认周期后缀）
gen PC_A4   = 稳定型股权3                    // A4 换手率 2 分组
gen Debt    = 关系型债权1                    // 长期负债/总负债（债权侧分项）
gen Invest  = 稳定型股权3                    // 股权侧分项（需确认 Invest 与强国令口径对应字段）
```

### 4.3 机制变量

```stata
gen Myopia = Fullratio2                      // 管理者短视 MD&A 版（底座已 ×100，需确认是否再放大）
winsor2 Myopia, cut(1 99) replace
gen KZ_fc  = KZ                              // 融资约束：底座有现成 KZ 指数
* 设计写 WW 指数；底座只有 KZ。本计划用 KZ 作融资约束机制可得口径，WW 标"需确认/需另算"
```

### 4.4 控制变量

```stata
gen Size    = ln(A001000000)                 // LN(总资产)
gen Lev     = A002000000 / A001000000         // 资产负债率
gen Growth  = B001101000 / L.B001101000 - 1   // 营收增长率（需先 xtset）
gen FirmAge = ln(year - year(EstablishDate) + 1)
gen Top1    = Shrcr1                          // 第一大股东持股比例
* ROE / Quick / Indep / Dual：底座数据字典未直接给净利润/速动/独董/两职字段
gen ROE     = .    // 需确认（净利润、所有者权益字段缺，FS_Combas 仅给资产/负债总计）
gen Quick   = .    // 需确认（缺流动资产/存货/流动负债字段）
gen Indep   = .    // 需确认（BDT_ManaGovAbil 给 Boardsize，未见独立董事人数）
gen Dual    = .    // 需确认（未见董事长=总经理字段）
```

### 4.5 异质性 / 调节变量

```stata
gen STATE   = PropertyRightsNature           // 1 国有 / 0 非国有（来自 BDT_ManaGovAbil）
gen HHI     = HHI_D                           // 行业竞争度（营业收入口径，需确认主用哪一列）
egen HHI_med = median(HHI), by(year)
gen HighComp = HHI < HHI_med                  // 高竞争 = 低 HHI
gen KeyPollution = .                          // 重点污染监控：底座无此字段，需确认 CSMAR 环境子库
gen Pollution_ind = .                         // 重污染行业目录：需确认（生态环境部目录映射 IndustryCodeD）
egen Green_med = median(green), by(year)
gen HighGreen = green >= Green_med
gen Sep     = Seperation                      // 两权分离率（异质性备查，设计第13节列为需补节点）
```

---

## 5. 缩尾与缺失值处理

```stata
xtset stkcd year                              // 复核点：唯一性
* 连续变量上下 1% 缩尾
winsor2 green Pat PC_B1 PC_A4 Debt Invest Myopia KZ_fc ///
        Size Lev Growth FirmAge Top1, cut(1 99) replace
* 缩尾敏感性（稳健性）：另存 2%、5% 版本
* 缺失：主回归样本 = 所有基线变量非缺
egen nmiss = rowmiss(green Pat Size Lev Growth FirmAge Top1)
drop if nmiss > 0
```

**复核点**：`xtset` 报 repeated time values 即主键不唯一，须回查 merge；`sum green Pat ...` 看分布是否有异常（Pat 对小公司滚动标准差 → 0 极敏感，见 patient-capital caveats）。

---

## 6. 描述性统计

```stata
estpost summarize green Pat PC_B1 PC_A4 Debt Invest Myopia KZ_fc ///
        Size Lev Growth FirmAge Top1 STATE HHI, detail
esttab using "06_结果输出/tables/T1_descriptive.rtf", ///
    cells("count mean sd min max") replace
```

---

## 7. 相关性分析

```stata
pwcorr green Pat Myopia KZ_fc Size Lev Growth FirmAge Top1, star(0.05)
* 导出相关矩阵 + VIF（基线 OLS 后 estat vif）检查多重共线
```

---

## 8. 基准回归

主模型 = 企业 + 年份双向 FE + 企业层聚类（[[two-way-fixed-effects-firm-year]]），核心解释变量用**含短视版** `Pat`：

```stata
* 式(1) 列(a)：C 熵值法主口径
reghdfe green Pat Size Lev Growth FirmAge Top1 [ROE Quick Indep Dual], ///
    absorb(stkcd year) cluster(stkcd)            // 方括号内变量待补齐（见 4.4 需确认）
* 列(b)：B1 持股时长法
reghdfe green PC_B1 $controls, absorb(stkcd year) cluster(stkcd)
* 列(c)：股权 vs 债权分项（式 2）
reghdfe green Invest Debt $controls, absorb(stkcd year) cluster(stkcd)
* 稳健：加城市/省份 FE
reghdfe green Pat $controls, absorb(stkcd year PROVINCE) cluster(stkcd)
```

预期 β₁(Pat) > 0 且显著（设计锚定谢婷婷 2025 基准 0.212***）。

---

## 9. 机制检验

江艇（2022）两步法 + Sobel + Bootstrap（参考邱蓉 2024 的 Bootstrap 1000）。**核心解释变量在此节一律改用剔除短视版 `Pat_nm`**：

```stata
gen Pat_nm = 耐心资本_YS_nomyopia                 // ← 机制检验专用，避免自变量内含中介

* 机制 1：管理者短视（主，预期 α1<0；myopia→green 为本项目新检验，预期 β2<0）
reghdfe Myopia Pat_nm $controls, absorb(stkcd year) cluster(stkcd)            // 式(3)
reghdfe green  Pat_nm Myopia $controls, absorb(stkcd year) cluster(stkcd)     // 式(4)

* 机制 2：融资约束 KZ（预期 α1<0；这里可用含短视版 Pat，KZ 与短视指标不同源）
reghdfe KZ_fc  Pat $controls, absorb(stkcd year) cluster(stkcd)
reghdfe green  Pat KZ_fc $controls, absorb(stkcd year) cluster(stkcd)

* Sobel + Bootstrap（管理者短视用 Pat_nm）
bootstrap r(ind_eff), reps(1000) seed(20260603): ///
    sgmediation green, mv(Myopia) iv(Pat_nm) cv($controls)   // sgmediation 需确认安装/可用性
```

> **落实要点（任务①要求贴的关键行）**：第 4.2 节用「`negative_var` 删去 `Fullratio2` 重算熵值 → `耐心资本_YS_nomyopia` → `pat_no_myopia.dta`」生成剔除短视版；本节 `gen Pat_nm = 耐心资本_YS_nomyopia`，所有以 `Myopia` 为中介的式(3)/式(4)/Bootstrap 都用 `Pat_nm` 而非 `Pat`。KZ 中介因与短视指标不同源，沿用含短视版 `Pat`。

---

## 10. 异质性检验

```stata
foreach g in STATE HighComp HighGreen KeyPollution Pollution_ind {
    reghdfe green Pat $controls if `g'==1, absorb(stkcd year) cluster(stkcd)
    reghdfe green Pat $controls if `g'==0, absorb(stkcd year) cluster(stkcd)
}
* 组间差异：Bootstrap 1000 次经验 p 值 / Chow（费舍尔组合检验）
* 连续调节：规模、行业竞争
gen Pat_HHI  = Pat * HHI
gen Pat_Size = Pat * Size
reghdfe green Pat HHI Pat_HHI   $controls, absorb(stkcd year) cluster(stkcd)
reghdfe green Pat Size Pat_Size $controls, absorb(stkcd year) cluster(stkcd)
```

> 设计第 10 节标注产权方向（谢婷婷国企更强 vs 强国令非国企更强）与 HHI 取向均存文献冲突，结果须明确 HHI 取向并讨论分歧，不照搬单篇预期。

---

## 11. 稳健性检验

```stata
* 11.1 被解释变量替换：成品绿色化转型指数 / 绿色 TFP / 漂绿对照
reghdfe green_index Pat $controls, absorb(stkcd year) cluster(stkcd)  // 成品指数
* reghdfe lngtfp ...   (需 SBM-ML，标需确认)
* reghdfe GWS Pat ...  (预期负；需华证 ESG，仅可选)
* 11.2 PC 测度替换：Pat / PC_B1 / PC_A4 三框架矩阵（已在第 8 节）
* 11.3 样本剔除
reghdfe green Pat $controls if !inrange(year,2020,2022), absorb(stkcd year) cluster(stkcd)  // 剔疫情
* 剔 2015 股灾年；剔绿色金融改革试验区（需确认试验区企业名单）
* 11.4 缩尾敏感性：2% / 5%（见第 5 节另存版本）
* 11.5 改聚类层级
reghdfe green Pat $controls, absorb(stkcd year) cluster(IndustryCodeD)
reghdfe green Pat $controls, absorb(stkcd year) cluster(PROVINCE)
* 11.6 滞后被解释变量 / 更换标准误
reghdfe F.green Pat $controls, absorb(stkcd year) cluster(stkcd)
* 11.7 安慰剂：1000 次随机置换 Pat（permute）
```

### 内生性（设计第 8 节，IV 矩阵）

```stata
* IV1（主）：前十大股东持股之和 Shrcr4
ivreghdfe green (Pat = Shrcr4) $controls, absorb(stkcd year) cluster(stkcd) first
* IV2：同行业（剔自身）同年份 Pat / green 均值
bys IndustryCodeD year: egen iv_indPat = mean(Pat)
bys IndustryCodeD year: egen n_ind = count(Pat)
gen IV_ind = (iv_indPat * n_ind - Pat) / (n_ind - 1)      // 剔除自身的行业均值
ivreghdfe green (Pat = IV_ind) $controls, absorb(stkcd year) cluster(stkcd) first
* IV3：Dickinson(2011) 现金流分类生命周期（需用 FS_Comscfd 现金流符号构造，需确认）
* 多工具并入时报告 Hansen J；单工具报告 KP-F、KP rk LM（>10 / p<0.01）
* 系统 GMM
xtabond2 green L.green Pat $controls i.year, ///
    gmm(L.green Pat, lag(2 4)) iv(i.year $controls) twostep robust
*  报告 AR(1)/AR(2)、Hansen J
* Heckman + PSM：以 Pat 中位数构造处理组，处理自选择
```

**复核点**：第一阶段 F > 10、KP rk LM p < 0.01；GMM 的 AR(2) p > 0.1、Hansen J p > 0.1 且工具数 < 组数。

---

## 12. 表格导出

```stata
* 统一用 esttab 输出到 06_结果输出/tables/
esttab m1 m2 m3 using "06_结果输出/tables/T3_baseline.rtf", ///
    b(3) se(3) star(* 0.1 ** 0.05 *** 0.01) ///
    keep(Pat PC_B1 Invest Debt) ///
    stats(N r2_a, labels("N" "Adj.R2")) replace
```

| 表号 | 内容 | 核心解释变量版本 |
|---|---|---|
| 表 1 | 描述性统计 | — |
| 表 2 | 相关性矩阵 | — |
| 表 3 | 基准：Pat(C) / PC_B1 / Invest+Debt | 含短视版 Pat |
| 表 4 | 内生性：IV1/IV2/IV3 + 系统 GMM | 含短视版 Pat |
| 表 5 | 机制：Myopia（用 Pat_nm）+ KZ（用 Pat）+ Sobel + Bootstrap | **Myopia 段用剔除短视版** |
| 表 6 | 异质性：污染/产权/竞争/规模/绿色程度 | 含短视版 Pat |
| 表 7 | 稳健性矩阵：BeV 替换 × PC 测度替换 | 多版本 |

---

## 13. 复核清单

- [ ] 安装命令全部成功（reghdfe / ivreghdfe / ranktest / winsor2 / xtabond2 / estout / rangestat）。
- [ ] `green_freq.dta`（113 词词频主口径）是否已生成；未生成则当前主回归用成品指数占位，结论标「待主口径就位后复跑」。
- [ ] 每个 merge 后 `tab _m_*`，记录 match 率与覆盖缺口。
- [ ] `xtset stkcd year` 无 repeated time values（主键唯一）。
- [ ] `sum` 检查 Pat（小公司滚动 SD→0 极值）、green（零词频比例）、Myopia 分布。
- [ ] `corr Pat 耐心资本_YS_nomyopia` 高但 < 1，确认剔除短视版构造正确。
- [ ] 机制检验中以 Myopia 为中介的回归全部用 `Pat_nm`，未误用含短视版。
- [ ] 第一阶段 F > 10、KP rk LM p < 0.01；GMM AR(2) p>0.1、Hansen J p>0.1。
- [ ] 「需确认」变量清单（ROE / Quick / Indep / Dual / KeyPollution / Pollution_ind / WW / lngtfp / GWS / Invest 字段映射 / 行业代码前缀 / STPT 含义 / B1 周期后缀 / HHI 选列）逐项落实或在论文中说明替代口径。
- [ ] 未覆盖 blank 项目 `05_分析代码/耐心资本-全套代码.do`（本计划只读、不改）。

---

## 需确认变量清单（汇总）

| 变量 | 状态 | 说明 |
|---|---|---|
| `freq` / `green`(主口径) | 需复刻 | 113 词字典 + 年报全文分词，底座只有成品指数 xlsx，无逐企业词频 dta |
| `ROE` | 需确认 | FS_Combas 仅给资产/负债总计，缺净利润、所有者权益 |
| `Quick` | 需确认 | 缺流动资产/存货/流动负债字段 |
| `Indep` | 需确认 | BDT_ManaGovAbil 给 Boardsize，未见独立董事人数 |
| `Dual` | 需确认 | 未见董事长=总经理字段 |
| `WW`(融资约束) | 需确认 | 设计写 WW，底座只有 KZ；本计划用 KZ 作可得口径 |
| `lngtfp`(绿色 TFP) | 需确认 | 需 SBM-ML 外部测算，项目暂缺 |
| `GWS`(漂绿) | 需确认 | 需华证 ESG（部分可得），仅稳健性 |
| `Invest`(股权侧分项) | 需确认 | 强国令 Invest 口径与底座 `稳定型股权3` 是否一致 |
| `PC_B1` 周期后缀 | 需确认 | `战略型投资者1_YYYY_2024` 须与样本区间起点对齐 |
| 行业代码前缀(金融剔除) | 需确认 | IndustryCodeD 是否 "J" 前缀，还是另有 SIC |
| `STPT` 取值含义 | 需确认 | ==1 表示"应剔除"还是"是 ST" |
| `KeyPollution` | 需确认 | 重点污染监控单位，底座无此字段（CSMAR 环境子库） |
| `Pollution_ind` | 需确认 | 重污染行业目录到 IndustryCodeD 的映射 |
| HHI 选列 | 需确认 | HHI_A/B/C/D 主用哪一列 |
| 绿色金融改革试验区名单 | 需确认 | 稳健性样本剔除用 |
