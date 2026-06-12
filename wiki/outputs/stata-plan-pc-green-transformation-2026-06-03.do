*=============================================================================*
* 耐心资本对企业绿色化转型的影响及作用机制 —— do 骨架（非最终可跑代码）
* 生成: /stata-plan --write-do  日期: 2026-06-03
* 权威 spec : wiki/outputs/empirical-design-pc-green-transformation-2026-06-03.md
* 配套计划  : wiki/outputs/stata-plan-pc-green-transformation-2026-06-03.md
* 数据底座  : blank/05_分析代码/耐心资本-全套代码.do（只读，本文件不改它）
*
* 约定:
*   - 被解释变量主口径 = LN(113 词绿色化转型词频 + 1)（解学梅、朱琪玮 2021），【需复刻字典】
*   - 核心解释变量主口径 = 熵值法 C 框架 Pat（含短视版，底座 耐心资本_YS）
*   - 机制 = 管理者短视 MD&A 版 Fullratio2 + 融资约束 KZ
*   - 凡 ★需确认★ 处为占位，落实前不要当成可跑代码
*   - 中文/空格路径一律加引号
*=============================================================================*

clear all
set more off
* set maxvar 32767

*--- 0. 安装外部命令（首次运行；已装可注释）-------------------------------*
* ssc install reghdfe, replace
* ssc install ftools, replace
* ssc install ivreghdfe, replace
* ssc install ranktest, replace
* ssc install winsor2, replace
* ssc install xtabond2, replace
* ssc install estout, replace
* ssc install rangestat, replace

*--- 路径（按本机改）--------------------------------------------------------*
global RAW  "/Users/han/Desktop/PatientCapital_Demo/blank/03_原始数据"
global MID  "/Users/han/Desktop/PatientCapital_Demo/blank/04_中间数据"
global OUT  "/Users/han/Desktop/PatientCapital_Demo/blank/06_结果输出"
* cap mkdir "$OUT/tables"
* cap mkdir "$OUT/figures"


*=============================================================================*
* 1-2. 输入数据准备与对齐主键（stkcd × year，均为数值）
*=============================================================================*

* --- 1.1 被解释变量：113 词词频主口径 -------------------------------------*
* ★需复刻★ 解学梅、朱琪玮(2021) 113 词字典 + 年报全文分词，Python 端落盘 green_freq.dta
*           底座目前只有成品"绿色化转型指数"xlsx（03_原始数据/E_ESG与绿色/...），无逐企业词频
* use green_freq.dta, clear          // 字段: stkcd year freq      ★需确认主口径★
* gen green = ln(freq + 1)
* save green_main.dta, replace
* 临时占位：未复刻前先用成品指数跑通流程，结论标"待主口径就位后复跑"
import excel using "$RAW/E_ESG与绿色/上市公司绿色化转型指数_2007-2024/绿色化转型指数_合并版.xlsx", firstrow clear
* ★需确认★ 列名（证券代码/年份/绿色化转型指数）→ 重命名为 stkcd year green_index
rename (证券代码 年份 绿色化转型指数) (stkcd year green_index)   // ★需确认实际列名★
destring stkcd year green_index, replace force
save green_index.dta, replace

* --- 1.2 财务控制变量 (FS_Combas 资产负债表) ------------------------------*
use "$RAW/A_财务报表/FS_Combas.dta", clear
keep if strmatch(Accper,"*-12-31")
keep if Typrep=="A"
gen stkcd = real(Stkcd)
gen year  = real(substr(Accper,1,4))
gen Size = ln(A001000000)                       // LN(总资产)
gen Lev  = A002000000 / A001000000              // 资产负债率
* ROE / Quick：FS_Combas 仅给资产总计/负债合计，缺净利润/所有者权益/流动项目 → ★需确认★
keep stkcd year Size Lev
save fin_bs.dta, replace

use "$RAW/A_财务报表/FS_Comins.dta", clear
keep if strmatch(Accper,"*-12-31")
keep if Typrep=="A"
gen stkcd = real(Stkcd)
gen year  = real(substr(Accper,1,4))
keep stkcd year B001101000                       // 营业收入
xtset stkcd year
gen Growth = B001101000/L.B001101000 - 1
keep stkcd year Growth
save fin_is.dta, replace

* --- 1.3 治理/股权（Top1, STATE, 独董/两职 ★需确认★）---------------------*
use "$RAW/B_公司治理与股权/HLD_CR.dta", clear
gen stkcd = real(Stkcd)
gen year  = real(substr(Reptdt,1,4))
keep stkcd year Shrcr1 Shrcr4                     // 第一大股东 / 前十大之和(主 IV)
rename Shrcr1 Top1
save gov_cr.dta, replace

use "$RAW/B_公司治理与股权/BDT_ManaGovAbil.dta", clear
gen stkcd = real(Symbol)
gen year  = real(substr(Enddate,1,4))
keep stkcd year PropertyRightsNature Boardsize Mngmhldn
rename PropertyRightsNature STATE                 // 1 国有 / 0 非国有
save gov_prop.dta, replace
* Indep(独立董事比例)、Dual(两职合一) 字段底座未见 → ★需确认★

* --- 1.4 上市公司年度信息（FirmAge, 行业, 省份）---------------------------*
use "$RAW/D_行业与市场/STK_LISTEDCOINFOANL.dta", clear
gen stkcd = real(Symbol)
gen year  = real(substr(EndDate,1,4))
* EstablishDate / LISTINGDATE 多为字符串日期，先转年
gen estyear = real(substr(EstablishDate,1,4))     // ★需确认★ 日期格式
gen lstyear = real(substr(LISTINGDATE,1,4))       // ★需确认★
gen FirmAge = ln(year - estyear + 1)
keep stkcd year FirmAge lstyear IndustryCodeD IndustryNameD PROVINCE
save listinfo.dta, replace

* --- 1.5 融资约束 KZ + 样本筛选标记 ---------------------------------------*
use "$RAW/C_创新与融资约束/BDT_FinConstKZ.dta", clear
gen stkcd = real(Symbol)
* ★需确认★ 该表的年度字段名（数据字典未列时间列）→ 假设有 year 或可由 Enddate 取
* gen year = real(substr(Enddate,1,4))
keep stkcd year KZ STPT IsNewOrSuspend ISBSE
rename KZ KZ_fc
save kz.dta, replace

* --- 1.6 行业竞争 HHI（行业层，m:1 合并）----------------------------------*
use "$RAW/D_行业与市场/INDFI_HHI.dta", clear
* ★需确认★ HHI 表的行业字段与时间字段，以及与企业行业(IndustryCodeD)的对接键
keep IndustryCode year HHI_A HHI_B HHI_C HHI_D    // ★需确认 year 列★
rename HHI_D HHI                                   // ★需确认主用哪列★
save hhi.dta, replace

* --- 1.7 两权分离率（异质性备查）-----------------------------------------*
use "$RAW/B_公司治理与股权/EN_EquityNatureAll.dta", clear
gen stkcd = real(Symbol)
* ★需确认★ 该表时间字段；Seperation = 两权分离率
* keep stkcd year EquityNature Seperation
* save sep.dta, replace

* --- 1.8 管理者短视 MD&A 版（机制主口径）---------------------------------*
use "$RAW/管理者短视主义_2007-2024/MD&A-管理者短视主义/管理者短视主义.dta", clear
gen stkcd = Scode
gen year  = Year
destring stkcd year, replace force
keep stkcd year Fullratio2
rename Fullratio2 Myopia                           // 底座已 ×100；★需确认是否再放大★
save myopia_mda.dta, replace

* --- 1.9 耐心资本（含短视版，底座成品）------------------------------------*
use "$MID/耐心资本_七合一_WZY.dta", clear
* 含短视版主口径
rename 耐心资本_YS Pat                              // 逐年熵值法（含 Fullratio2 短视指标）
* 替换口径
cap rename 稳定型股权3 PC_A4                         // A4 换手率 2 分组
cap rename 关系型债权1 Debt                          // 长期负债/总负债（债权侧）
* B1 持股时长法：周期后缀须与样本区间起点对齐 ★需确认★
cap rename 战略型投资者1_2012_2024 PC_B1
* Invest(股权侧分项)：强国令口径与底座字段对应关系 ★需确认★
cap gen Invest = PC_A4
keep stkcd year Pat PC_A4 PC_B1 Debt Invest
save pc_main.dta, replace


*=============================================================================*
* 4.2(关键) 剔除短视版熵值法 Pat —— 管理者短视中介专用
*   逻辑：复用底座 9.7 节逐年熵值法循环，唯一改动 = negative_var 删去 Fullratio2
*   含短视版做基线/异质/稳健；剔除短视版仅做以 Myopia 为中介的机制检验，
*   否则自变量内含中介(熵值含短视指标)，造成机械中介(设计 5.2/9 节)
*=============================================================================*
forvalues z=2007/2024 {
    use "$MID/熵值法汇总.dta", clear
    keep if year==`z'
    * 缺失清理【不含 Fullratio2】
    foreach i in 投资者长期持股比例 投资者短期持股比例 稳定型股权2 ///
                 长期资本负债率 企业短期财务杠杆 资本增长保持率 {
        drop if `i'==.
    }
    winsor2 投资者长期持股比例 投资者短期持股比例 稳定型股权2 ///
            长期资本负债率 企业短期财务杠杆 资本增长保持率, cut(1 99) replace
    * 正向指标不变；负向指标【删去 Fullratio2】★这是剔除短视版的唯一差异★
    global positive_var 投资者长期持股比例 稳定型股权2 长期资本负债率 资本增长保持率
    global negative_var 投资者短期持股比例 企业短期财务杠杆
    global all_var $positive_var $negative_var
    foreach i in $positive_var {
        qui sum `i'
        gen x_`i'=(`i'-r(min))/(r(max)-r(min))
    }
    foreach i in $negative_var {
        qui sum `i'
        gen x_`i'=(r(max)-`i')/(r(max)-r(min))
    }
    foreach i in $all_var {
        egen `i'_sum=sum(x_`i')
        gen y_`i'=x_`i'/`i'_sum
    }
    gen n=_N
    foreach i in $all_var {
        gen y_lny_`i'=y_`i'*ln(y_`i')
        replace y_lny_`i'=0 if x_`i'==0
    }
    foreach i in $all_var {
        egen y_lny_`i'_sum=sum(y_lny_`i')
    }
    foreach i in $all_var {
        gen E_`i'= -1/ln(n)*y_lny_`i'_sum
    }
    foreach i in $all_var {
        gen d_`i'= 1-E_`i'
    }
    egen d_sum = rowtotal(d_*)
    foreach i in $all_var {
        gen W_`i'= d_`i'/d_sum
    }
    foreach i in $all_var {
        gen Score_`i'= x_`i'*W_`i'
    }
    egen Score=rowtotal(Score_*)
    rename Score 耐心资本_YS_nomyopia
    keep stkcd year 耐心资本_YS_nomyopia
    save 逐年熵值法_nomyopia`z'.dta, replace
}
use 逐年熵值法_nomyopia2007.dta, clear
forvalues i=2008/2024 { append using 逐年熵值法_nomyopia`i'.dta }
save pat_no_myopia.dta, replace
* 复核点：剔除短视版与含短视版相关但不为 1
* （合并后再 corr Pat 耐心资本_YS_nomyopia）


*=============================================================================*
* 2. 合并为面板（主表 = 被解释变量面板）
*=============================================================================*
use green_index.dta, clear                          // ★主口径就位后换 green_main.dta★
merge 1:1 stkcd year using pc_main.dta,        keep(master match) gen(_m_pc)
merge 1:1 stkcd year using pat_no_myopia.dta,  keep(master match) gen(_m_patnm)
merge 1:1 stkcd year using myopia_mda.dta,     keep(master match) gen(_m_myo)
merge 1:1 stkcd year using kz.dta,             keep(master match) gen(_m_kz)
merge 1:1 stkcd year using fin_bs.dta,         keep(master match) gen(_m_bs)
merge 1:1 stkcd year using fin_is.dta,         keep(master match) gen(_m_is)
merge 1:1 stkcd year using gov_cr.dta,         keep(master match) gen(_m_cr)
merge 1:1 stkcd year using gov_prop.dta,       keep(master match) gen(_m_prop)
merge 1:1 stkcd year using listinfo.dta,       keep(master match) gen(_m_li)
* 行业层 HHI：m:1
merge m:1 IndustryCode year using hhi.dta,     keep(master match) gen(_m_hhi)   // ★需确认对接键★
* 复核点：逐个查 merge 结果
foreach v in _m_pc _m_patnm _m_myo _m_kz _m_bs _m_is _m_cr _m_prop _m_li _m_hhi {
    di "==== `v' ===="
    tab `v'
}


*=============================================================================*
* 3. 样本筛选
*=============================================================================*
* 剔金融保险（行业代码 J）★需确认行业代码字段与前缀★
* drop if substr(IndustryCodeD,1,1)=="J"
* 剔 ST/*ST（用 KZ 表自带标记）★需确认 STPT==1 含义★
* drop if STPT==1
* 剔上市不足 2 年
* drop if year - lstyear < 2
* 剔北交所（视情况）
* drop if ISBSE==1
* 样本区间（主口径与谢婷婷 2025 对齐）
keep if inrange(year,2012,2023)
* 复核点
count


*=============================================================================*
* 4. 变量构造（其余）
*=============================================================================*
* 4.1 被解释变量 green 已在 1.1 处理（主口径就位前用 green_index 占位）
* 4.3 机制变量
rename 耐心资本_YS_nomyopia Pat_nm                   // 剔除短视版（机制 Myopia 专用）
* KZ_fc 已在 kz.dta；Myopia 已在 myopia_mda.dta
* 4.4 控制变量补全 ★需确认★
gen ROE   = .       // 需确认：缺净利润/所有者权益字段
gen Quick = .       // 需确认：缺流动资产/存货/流动负债
gen Indep = .       // 需确认：缺独立董事人数
gen Dual  = .       // 需确认：缺董事长=总经理标记
* 4.5 异质性/调节
egen HHI_med = median(HHI), by(year)
gen  HighComp = HHI < HHI_med
* green 主口径就位后用 green；占位阶段先用 green_index
egen Green_med = median(green_index), by(year)
gen  HighGreen = green_index >= Green_med
gen  KeyPollution  = .   // 需确认：CSMAR 环境子库，底座无
gen  Pollution_ind = .   // 需确认：生态环境部重污染目录映射 IndustryCodeD

* 占位主口径别名（主口径就位后改为 green = ln(freq+1)）
gen green = green_index   // ★需确认主口径★


*=============================================================================*
* 5. 缩尾与缺失、面板设定
*=============================================================================*
xtset stkcd year                                     // 复核点：无 repeated time values
winsor2 green Pat Pat_nm PC_B1 PC_A4 Debt Invest Myopia KZ_fc ///
        Size Lev Growth FirmAge Top1, cut(1 99) replace
egen nmiss = rowmiss(green Pat Size Lev Growth FirmAge Top1)
drop if nmiss > 0
* 复核点
sum green Pat Pat_nm Myopia KZ_fc Size Lev Growth FirmAge Top1
corr Pat Pat_nm                                      // 应高但 < 1

* 控制变量集合（ROE Quick Indep Dual 补齐后纳入）
global controls Size Lev Growth FirmAge Top1
* global controls Size Lev Growth FirmAge Top1 ROE Quick Indep Dual   // 补齐后启用


*=============================================================================*
* 6. 描述性统计
*=============================================================================*
estpost summarize green Pat Myopia KZ_fc $controls STATE HHI, detail
esttab using "$OUT/tables/T1_descriptive.rtf", ///
    cells("count mean sd min max") replace


*=============================================================================*
* 7. 相关性分析
*=============================================================================*
pwcorr green Pat Myopia KZ_fc $controls, star(0.05)


*=============================================================================*
* 8. 基准回归（含短视版 Pat）
*=============================================================================*
eststo m1: reghdfe green Pat    $controls, absorb(stkcd year) cluster(stkcd)
eststo m2: reghdfe green PC_B1  $controls, absorb(stkcd year) cluster(stkcd)
eststo m3: reghdfe green Invest Debt $controls, absorb(stkcd year) cluster(stkcd)
* 加省份/城市 FE 稳健
eststo m4: reghdfe green Pat $controls, absorb(stkcd year PROVINCE) cluster(stkcd)
esttab m1 m2 m3 m4 using "$OUT/tables/T3_baseline.rtf", ///
    b(3) se(3) star(* 0.1 ** 0.05 *** 0.01) ///
    stats(N r2_a, labels("N" "Adj.R2")) replace


*=============================================================================*
* 9. 机制检验 —— Myopia 段必须用剔除短视版 Pat_nm
*=============================================================================*
* 机制 1：管理者短视（主）— 用 Pat_nm
eststo s1: reghdfe Myopia Pat_nm        $controls, absorb(stkcd year) cluster(stkcd)
eststo s2: reghdfe green  Pat_nm Myopia $controls, absorb(stkcd year) cluster(stkcd)
* 机制 2：融资约束 KZ — 与短视指标不同源，用含短视版 Pat
eststo s3: reghdfe KZ_fc  Pat           $controls, absorb(stkcd year) cluster(stkcd)
eststo s4: reghdfe green  Pat KZ_fc     $controls, absorb(stkcd year) cluster(stkcd)
* Sobel + Bootstrap（管理者短视用 Pat_nm）★sgmediation 需确认可用★
* bootstrap, reps(1000) seed(20260603): ///
*     sgmediation green, mv(Myopia) iv(Pat_nm) cv($controls)
esttab s1 s2 s3 s4 using "$OUT/tables/T5_mechanism.rtf", ///
    b(3) se(3) star(* 0.1 ** 0.05 *** 0.01) replace


*=============================================================================*
* 10. 异质性检验（含短视版 Pat）
*=============================================================================*
foreach g in STATE HighComp HighGreen KeyPollution Pollution_ind {
    di "==== heterogeneity by `g' ===="
    cap reghdfe green Pat $controls if `g'==1, absorb(stkcd year) cluster(stkcd)
    cap reghdfe green Pat $controls if `g'==0, absorb(stkcd year) cluster(stkcd)
}
* 连续调节
gen Pat_HHI  = Pat * HHI
gen Pat_Size = Pat * Size
reghdfe green Pat HHI  Pat_HHI  $controls, absorb(stkcd year) cluster(stkcd)
reghdfe green Pat Size Pat_Size $controls, absorb(stkcd year) cluster(stkcd)
* 组间差异：Bootstrap 1000 经验 p / 费舍尔组合检验（略）


*=============================================================================*
* 11. 稳健性检验
*=============================================================================*
* 11.1 被解释变量替换
reghdfe green_index Pat $controls, absorb(stkcd year) cluster(stkcd)   // 成品指数
* reghdfe lngtfp Pat ...   ★需确认 绿色 TFP★
* reghdfe GWS    Pat ...   ★需确认 漂绿/华证 ESG★
* 11.2 PC 测度替换：Pat / PC_B1 / PC_A4（见第 8 节 + 下）
reghdfe green PC_A4 $controls, absorb(stkcd year) cluster(stkcd)
* 11.3 样本剔除
reghdfe green Pat $controls if !inrange(year,2020,2022), absorb(stkcd year) cluster(stkcd)  // 剔疫情
* reghdfe green Pat $controls if year!=2015, ...   // 剔股灾
* 11.4 缩尾敏感性 2%/5%（另存数据集重跑）
* 11.5 改聚类
reghdfe green Pat $controls, absorb(stkcd year) cluster(IndustryCode)
reghdfe green Pat $controls, absorb(stkcd year) cluster(PROVINCE)
* 11.6 滞后被解释变量
reghdfe F.green Pat $controls, absorb(stkcd year) cluster(stkcd)
* 11.7 安慰剂：随机置换 Pat 1000 次
* permute Pat beta=_b[Pat], reps(1000) seed(20260603): ///
*     reghdfe green Pat $controls, absorb(stkcd year) cluster(stkcd)


*=============================================================================*
* 内生性（IV 矩阵 + 系统 GMM + Heckman/PSM）
*=============================================================================*
* IV1（主）：前十大股东持股之和 Shrcr4
ivreghdfe green (Pat = Shrcr4) $controls, absorb(stkcd year) cluster(stkcd) first
* IV2：同行业(剔自身)同年 Pat 均值
bys IndustryCode year: egen iv_indPat = mean(Pat)
bys IndustryCode year: egen n_ind = count(Pat)
gen IV_ind = (iv_indPat*n_ind - Pat)/(n_ind - 1)
ivreghdfe green (Pat = IV_ind) $controls, absorb(stkcd year) cluster(stkcd) first
* IV3：Dickinson(2011) 现金流分类生命周期 ★需用 FS_Comscfd 现金流符号构造，需确认★
* 复核点：第一阶段 F>10、KP rk LM p<0.01；多工具时报告 Hansen J

* 系统 GMM
xtabond2 green L.green Pat $controls i.year, ///
    gmm(L.green Pat, lag(2 4)) iv(i.year $controls) twostep robust
* 复核点：AR(1) 显著、AR(2) p>0.1、Hansen J p>0.1 且工具数<组数

* Heckman + PSM：以 Pat 中位数构造处理组，处理自选择 ★实现略，需确认选择方程协变量★


*=============================================================================*
* 12. 表格导出（已分散在各节 esttab）
* 13. 复核清单见配套 .md 第 13 节
*=============================================================================*
* 本文件为骨架：★需确认★ 处须落实后方可整段运行；未覆盖 blank 原始 do。
