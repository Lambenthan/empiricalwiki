*=============================================================
* iv_2sls.do — 工具变量 2SLS（配套 wiki/identification/instrumental-variables）
* 依赖: ssc install ivreghdfe ivreg2 ranktest ftools estout
*=============================================================
clear all
set more off
use "data/panel.dta", clear

*--- 1. 工具变量构造示例：行业 leave-one-out 均值 -------------
bysort ind_code year: egen x_ind_sum = total(x)
bysort ind_code year: gen  x_ind_n   = _N
gen z_loo = (x_ind_sum - x) / (x_ind_n - 1)
* CHECK: 行业-年份单元里企业数过少(<5)的 z_loo 噪声大，考虑剔除
bysort ind_code year: drop if _N < 5

*--- 2. OLS 基准（与 2SLS 并排呈现）--------------------------
eststo clear
eststo ols: reghdfe y x size lev roe cash, absorb(stkcd year) vce(cluster stkcd)

*--- 3. 2SLS ---------------------------------------------------
eststo iv: ivreghdfe y size lev roe cash (x = z_loo), ///
    absorb(stkcd year) cluster(stkcd) first
* CHECK 三件套:
*   (1) 第一阶段: z_loo 系数显著、符号合预期
*   (2) 弱工具: Kleibergen-Paap rk Wald F（对照 Stock-Yogo 临界值；
*       F 偏弱时改报 Anderson-Rubin 置信区间: weakiv 命令）
*   (3) 多 IV 时: Hansen J 不拒绝（单 IV 恰好识别，无此检验）

*--- 4. 内生性检验 --------------------------------------------
* Durbin-Wu-Hausman: OLS 与 IV 是否系统性偏离
ivreg2 y size lev roe cash i.year (x = z_loo), cluster(stkcd) endog(x)

*--- 5. 排他性旁证（按研究情境取舍）--------------------------
* (a) Reduced form: z 直接对 y 回归，系数应与主结果方向一致
reghdfe y z_loo size lev roe cash, absorb(stkcd year) vce(cluster stkcd)
* (b) 安慰剂结果变量: z 对"不该被影响的 y_placebo"回归，应得零

*--- 6. 输出 ---------------------------------------------------
esttab ols iv using "output/iv_2sls.rtf", replace ///
    b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_within widstat, fmt(%9.0f %9.3f %9.1f) ///
    labels("N" "Within R2" "KP rk Wald F")) title("OLS vs 2SLS")
