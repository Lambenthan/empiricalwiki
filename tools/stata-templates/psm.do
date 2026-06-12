*=============================================================
* psm.do — 倾向得分匹配与 PSM-DID（配套 wiki/identification/propensity-score-matching）
* 依赖: ssc install psmatch2 pstest reghdfe estout
*=============================================================
clear all
set more off
use "data/panel.dta", clear

*--- 1. 得分估计：协变量必须是处理前(前定)变量 ---------------
* 横截面匹配示例；面板逐年匹配时套 forvalues year 循环
logit treat l_size l_lev l_roe l_cash l_age l_top10   // l_ 前缀 = 滞后一期
predict pscore, pr
* CHECK: 共同支撑（两组得分分布重叠区）
twoway (kdensity pscore if treat==1) (kdensity pscore if treat==0), ///
    legend(label(1 "处理组") label(2 "控制组")) name(support, replace)

*--- 2. 匹配：基准 1:1 卡尺 0.05 -----------------------------
set seed 20260612
psmatch2 treat, pscore(pscore) neighbor(1) caliper(0.05) ties common
* CHECK: 落入共同支撑的样本数、未匹配上的处理组个数
tab _support treat

*--- 3. 平衡性检验（必报）------------------------------------
pstest l_size l_lev l_roe l_cash l_age l_top10, both graph
* CHECK: 匹配后 |bias| < 10%，t 检验不显著；不达标回去改得分模型

*--- 4. 匹配样本上的 ATT / PSM-DID ---------------------------
* 直接 ATT（psmatch2 自带，标准误偏乐观，仅作参考）
psmatch2 treat, pscore(pscore) neighbor(1) caliper(0.05) outcome(y)
* 正规做法：匹配样本 + 频数权重跑回归 / DID
gen matched = (_weight != .)
reghdfe y did size lev roe cash if matched [fweight=_weight], ///
    absorb(stkcd year) vce(cluster stkcd)

*--- 5. 稳健性：换匹配方式 -----------------------------------
psmatch2 treat, pscore(pscore) neighbor(4) caliper(0.05) ties common  // 1:4
psmatch2 treat, pscore(pscore) kernel                                  // 核匹配
* teffects 版本（标准误更正规，重要结论用它核验）
teffects psmatch (y) (treat l_size l_lev l_roe l_cash l_age l_top10), atet
