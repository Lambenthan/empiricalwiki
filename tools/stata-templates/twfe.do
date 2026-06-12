*=============================================================
* twfe.do — 双向固定效应基准面板（配套 wiki/identification/two-way-fixed-effects）
* 依赖: ssc install reghdfe winsor2 ftools estout
*=============================================================
clear all
set more off

*--- 0. 路径与数据 -------------------------------------------
global DATA "data"
global OUT  "output"
use "$DATA/panel.dta", clear   // 主面板: stkcd year + 变量

*--- 1. 标准清洗（全项目只做一次）---------------------------
* 剔除金融保险业（证监会行业代码 J）
drop if substr(ind_code, 1, 1) == "J"
* 剔除 ST/*ST
drop if st_flag == 1
* 连续变量 1%/99% 缩尾
local convars "y x size lev roe cash age top10"
winsor2 `convars', replace cuts(1 99)
* CHECK: 清洗后样本量与年份分布
count
tab year

*--- 2. 面板声明与组内变异检查 -------------------------------
xtset stkcd year
* CHECK: 核心解释变量组内变异是否足够（within SD 过小则系数会被 FE 吸收）
xtsum x

*--- 3. 逐层加入 FE 的系数轨迹 -------------------------------
eststo clear
eststo m1: reg y x size lev roe cash age top10, vce(cluster stkcd)
eststo m2: reghdfe y x size lev roe cash age top10, absorb(year) vce(cluster stkcd)
eststo m3: reghdfe y x size lev roe cash age top10, absorb(stkcd year) vce(cluster stkcd)
eststo m4: reghdfe y x size lev roe cash age top10, absorb(stkcd ind_code#year) vce(cluster stkcd)
* CHECK: m1→m4 系数漂移幅度；大幅漂移 = 遗漏变量敏感，需要识别设计接力
esttab m1 m2 m3 m4 using "$OUT/twfe_baseline.rtf", replace ///
    b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_within, fmt(%9.0f %9.3f)) title("TWFE 基准回归")
