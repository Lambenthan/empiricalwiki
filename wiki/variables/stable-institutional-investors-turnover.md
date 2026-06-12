---
title: "稳定型机构投资者持股比例（A1 换手率三分组法，STABLEINS）"
slug: "stable-institutional-investors-turnover"
construct: "机构投资者异质性 / 耐心资本（股权侧时间属性，A1 换手率三分组变体）"
role: core_explanatory
measurement: "Step 1：按半年度计算每个机构投资者的双向最小买卖额比换手率 CR_{k,t}；Step 2：研究期内每半年度换手率求算术均值得 AVR_CR_k；Step 3：剔除持股期不足 2 期的机构投资者后，按 AVR_CR_k 等距三分组；Step 4：换手率最低组定义为稳定型机构投资者；Step 5：STABLEINS_{i, t} = 稳定型机构投资者在公司 i 的合计持股比例（取并购首次公告日前最近半年度或年度末数据）。"
data_sources: [wind, tonghuashun, csmar]
database_tables: [机构投资者持股, 机构投资者交易明细]
frequency: deal-event (snapshot at last semi-annual or annual report before announcement)
source_papers: [周绍妮-2017-机构投资者-国企-并购绩效]
available_in_project: false
project_paths: []
date_updated: 2026-05-07
---

## Definition

按机构投资者持股换手率三分组划分得到的"稳定型"机构投资者在某上市公司的合计持股比例。"稳定型"代表换手率最低的一组机构投资者，理论上对应长期持股、交易不频繁、有意愿主动监督公司治理的角色。

周绍妮 (2017) 530 起国企并购样本均值 1.10%、中位数 0.41%、std 1.56、最大 7.59%，整体水平远低于交易型机构投资者（参见 [[transactional-institutional-investors-turnover]]）。

## Measurement

借鉴 Gaspar (2005) 与 Yan and Zhang (2009)，并针对中国机构投资者发展周期较短做改进：

```
Step 1（双向最小买卖额比换手率，半年度）

CR_buy_{k,t}  = Σ_i ( S_{k,i,t}·P_{i,t} − S_{k,i,t-1}·P_{i,t-1} − S_{k,i,t-1}·ΔP_{i,t} ),  当 S_{k,i,t} ≥ S_{k,i,t-1}
CR_Sell_{k,t} = Σ_i 同上公式但条件相反

CR_{k,t} = 2·min(CR_buy_{k,t}, CR_Sell_{k,t}) / Σ_i ( S_{k,i,t}·P_{i,t} + S_{k,i,t}·P_{i,t-1} )

Step 2（研究期均值换手率）

AVR_CR_k = (1/N) · Σ_{j=1..N} CR_{k,j}    ， N 为研究期内的半年度数

Step 3（剔除新设机构）：剔除研究期内持股期不足 2 期的机构投资者。

Step 4（三分组）：按 AVR_CR_k 升序排序，等距分为三组，最低组为稳定型，最高组为交易型，中间组弃用。

Step 5（公司层持股比例）

STABLEINS_{i, t*} = Σ_{k ∈ Stable} 机构投资者 k 在公司 i 第 t* 期持股比例
```

时点 t* 取并购首次公告日前最近半年度末或年度末。

注：周绍妮 (2017) 与 Gaspar (2005)、Yan and Zhang (2009) 的差异在于：(1) 取双向交易额的 **最小值** 而非买入额，避免新设机构因建仓推高换手率；(2) 时间步用半年度而非季度，与中国半年报披露节奏一致；(3) 研究期 5 年内不再按机构-年滚动计算 AVR_CR，而是以整段研究期均值作为机构特征。

## Data Source

- [[wind]]、[[tonghuashun]]：机构投资者每期持股数与持股比例明细，用于计算 S_{k,i,t}。
- [[csmar]] 行情库：股价 P_{i,t} 与流通股数（用于规模标准化）。
- 三库交叉核对机构投资者编码与基金类型（混合 / 指数 / 债券 / 其他）。

## Literature Variants

- A1 换手率三分组法（本变量）：周绍妮 (2017)；最早源 Gaspar (2005)、Yan and Zhang (2009)。
- A2 持股标准差变体：稳定型股权 = 机构持股比例 / 过去 3 年标准差（连续值）。代表：[[代飞-2025-耐心资本-双元创新-管理者短视]]。
- B2 持股稳定性中位数法：[[institutional-investor-heterogeneity-stability]] / [[heterogeneous-institutional-investors-stable]]。
- 类型直接划分法：按机构名称分类（基金 / 保险 / QFII / 社保 / 信托 / 财务公司）；或按 Brickley (1988) 商业关系划分压力敏感 / 抵制型。

A1 与 B2 均使用换手率 / 稳定性指标，但 A1 在机构层面分组（一刀切定义机构身份），B2 在公司-年度层面定义（同一机构在不同公司可能稳定 / 交易标签不同）。A1 的优点是机构身份稳定、解释力强；缺点是丢失中间组样本，且对研究期较长时机构投资风格变化不敏感。

## Construction Steps

1. 从 [[wind]] / [[tonghuashun]] 抓取每个机构投资者每半年的持股明细 (机构编码 × 股票编码 × 期末持股股数 × 期末股价)。
2. 按机构 × 半年汇总 CR_buy 与 CR_Sell（按 S_{k,i,t} 与 S_{k,i,t-1} 大小判定方向）。
3. 计算单期换手率 CR_{k,t}。
4. 按机构汇总研究期 5 年共 10 个半年度，剔除持股期不足 2 期的机构。
5. AVR_CR_k = 算术均值。
6. 按 AVR_CR_k 升序排列后等距三分组，最低组打 Stable=1。
7. 按公司 × 时点（半年度末 / 年度末）合计稳定型机构投资者持股比例 → STABLEINS。
8. 与并购事件按"首次公告日前最近的时点"合并。

## Stata Notes

```stata
* 假设已有面板：机构 k × 公司 i × 半年 t，含 share_kit 与 price_it
gen mv_kit  = share_kit * price_it
gen mv_kit_l = mv_kit[_n-1]   // 同 (k,i) 上一期市值
gen ds = share_kit - share_kit[_n-1]

* 单期 CR_buy / CR_Sell 累计
gen buy_term  = (mv_kit - mv_kit_l - share_kit[_n-1] * (price_it - price_it[_n-1])) if ds >= 0
gen sell_term = (mv_kit - mv_kit_l - share_kit[_n-1] * (price_it - price_it[_n-1])) if ds < 0

bysort k t: egen CR_buy  = total(buy_term)
bysort k t: egen CR_Sell = total(sell_term)
bysort k t: egen denom   = total( share_kit * price_it + share_kit * price_it[_n-1] )

gen CR_kt = 2 * min(CR_buy, abs(CR_Sell)) / denom

* 机构均值
bysort k: egen AVR_CR = mean(CR_kt)
bysort k: egen periods = count(CR_kt)
keep if periods >= 2

* 三分组（按等距 tertile）
xtile CR_tier = AVR_CR, nq(3)
gen Stable = (CR_tier == 1)
gen Trans  = (CR_tier == 3)

* 公司层合计持股
bysort i t: egen STABLEINS = total( share_kit / total_share_it ) if Stable == 1
bysort i t: egen TRANSINS  = total( share_kit / total_share_it ) if Trans  == 1
```

## Caveats

- A1 三分组对中间组的处置丢失约 1/3 机构样本；公司层 STABLEINS + TRANSINS 之和不等于全口径机构持股。
- 研究期长度敏感：5 年期均值会平滑掉机构投资风格的渐变；周绍妮 (2017) 假设研究期内机构特征不变，长期面板（10+ 年）使用时需改回 Gaspar / Yan 的滚动均值。
- 方法对配对买卖完整性敏感：当 [[wind]] / [[tonghuashun]] 在某半年度只覆盖买入或只覆盖卖出（如新设机构、清算机构）时，CR 不稳定；论文通过"剔除持股期不足 2 期"做了部分处理。
- 中国情境特殊性：周绍妮 (2017) 表 2 显示稳定型机构投资者中指数型基金占 77.49%，**稳定型 ≈ 被动投资**；这一现象与西方文献"稳定型 = 主动监督者"的预设相反。引用本变量时务必同时引用文中 Caveats，避免直接套用西方文献的"稳定型 = 治理积极者"判断。
- 与 [[patient-capital]] 的关系：A1 仅捕捉"股权侧时间属性"，不含债权侧；不能与 [[代飞-2025-耐心资本-双元创新-管理者短视]] 的 A2 综合得分直接互换。

## Related

- 上位构念：[[patient-capital]] — A1 是耐心资本股权侧时间属性的三分组操作化变体。
- 同 paper 配对变量：[[transactional-institutional-investors-turnover]]
- 替代框架：[[institutional-investor-heterogeneity-stability]]（B2）、[[heterogeneous-institutional-investors-stable]]（B2）
- 数据：[[wind]] · [[tonghuashun]] · [[csmar]]
- 主用论文：[[周绍妮-2017-机构投资者-国企-并购绩效]]
