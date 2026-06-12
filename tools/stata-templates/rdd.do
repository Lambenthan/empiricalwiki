*=============================================================
* rdd.do — 断点回归（配套 wiki/identification/regression-discontinuity）
* 依赖: net install rdrobust + rddensity (from https://rdpackages.github.io/)
*=============================================================
clear all
set more off
use "data/sample.dta", clear
* 变量约定: run = 驱动变量, CUT = 阈值, y = 结果, d = 实际处理状态(fuzzy 用)
global CUT 0
gen run_c = run - $CUT    // 中心化

*--- 1. 操纵检验（第一道闸门，不过不必往下做）----------------
rddensity run, c($CUT) plot
* CHECK: 密度在阈值处无显著跳跃(p > 0.10)；财务门槛类驱动变量重点排查凑数行为

*--- 2. RD 图（必出）-----------------------------------------
rdplot y run, c($CUT) p(2) binselect(esmv) ///
    graph_options(name(rdplot, replace) xtitle("驱动变量") ytitle("结果"))

*--- 3. Sharp RD 主估计 ---------------------------------------
rdrobust y run, c($CUT) p(1) kernel(triangular) bwselect(mserd)
* 报 Conventional 系数 + Robust 推断(偏差修正)那一行
* CHECK: 记录最优带宽 h 与带宽内有效样本量

*--- 4. Fuzzy RD（越线只改变处理概率时）----------------------
rdrobust y run, c($CUT) fuzzy(d) p(1) kernel(triangular) bwselect(mserd)
* CHECK: 第一阶段(越线对 d)的跳跃幅度；太小则继承弱 IV 全部问题

*--- 5. 稳健性组合拳 ------------------------------------------
* (a) 带宽敏感性: 0.5 倍与 2 倍最优带宽
rdrobust y run, c($CUT) h(放入0.5h)
rdrobust y run, c($CUT) h(放入2h)
* (b) 协变量平滑性: 前定变量在阈值处不应跳
foreach v in size lev roe age {
    rdrobust `v' run, c($CUT) p(1) bwselect(mserd)
}
* (c) 安慰剂阈值: 在远离真阈值处应得零
rdrobust y run, c(放入伪阈值)
* (d) 甜甜圈 RD: 剔除紧贴阈值的观测(堆积嫌疑)
rdrobust y run if abs(run_c) > 放入剔除半径, c($CUT)
