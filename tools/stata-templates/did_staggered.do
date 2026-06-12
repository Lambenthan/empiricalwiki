*=============================================================
* did_staggered.do — 经典与交错 DID（配套 wiki/identification/difference-in-differences）
* 依赖: ssc install reghdfe csdid drdid bacondecomp eventstudyinteract estout
*=============================================================
clear all
set more off
use "data/panel.dta", clear
* 变量约定: first_treat_year = 个体首次受处理年份(从未处理 = 0 或缺失)

*--- 1. 处理变量构造 -----------------------------------------
gen treat = (first_treat_year > 0 & !missing(first_treat_year))
gen post  = (year >= first_treat_year) if treat == 1
replace post = 0 if treat == 0
gen did   = treat * post
* 事件时间（事件研究图用）
gen event_time = year - first_treat_year if treat == 1
* CHECK: 处理组规模、各批次处理年份分布
tab first_treat_year

*--- 2. TWFE 基准（交错情形下仅作基准，不作主结论）----------
reghdfe y did size lev roe cash, absorb(stkcd year) vce(cluster stkcd)
est store twfe

*--- 3. Goodman-Bacon 分解：诊断负权重 -----------------------
* 仅平衡面板可用；看"已处理 vs 后处理"比较的权重占比
bacondecomp y did, ddetail
* CHECK: 负权重或坏比较占比高 → TWFE 系数不可信，主结论用下面的稳健估计量

*--- 4. Callaway & Sant'Anna (csdid) 主估计 ------------------
gen gvar = first_treat_year
replace gvar = 0 if missing(gvar)
csdid y size lev roe cash, ivar(stkcd) time(year) gvar(gvar) method(dripw)
estat simple        // 总 ATT
estat event         // 事件研究系数
csdid_plot          // 事件研究图
* CHECK: 处理前各期系数应不显著且无趋势（平行趋势旁证）

*--- 5. Sun & Abraham 交互加权（交叉验证）--------------------
* 需要 never-treated 或 last-treated 作对照
gen never_treat = (gvar == 0)
eventstudyinteract y L*event F*event, vce(cluster stkcd) ///
    absorb(stkcd year) cohort(gvar) control_cohort(never_treat)

*--- 6. 安慰剂：随机化处理时点 -------------------------------
* 抽 500 次伪处理年份，真实系数应落在伪系数分布 5% 尾部之外
* （循环略：permute 或自写 forvalues + 存系数）
