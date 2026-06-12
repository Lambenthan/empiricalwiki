---
title: "引理3：经理最优长期投资水平 θ"
slug: "edmans-lemma3-investment-level"
proposition_type: characterization
formal_statement: "LEMMA 3. M chooses investment level θ given by θ = min((1−ω)g / (2ωX(1−π_X)), 1). If θ < 1, it is increasing in g and π_X, and decreasing in X and ω."
conditions: "高质量企业的经理在 t=0 选 θ ∈ [0,1]；投资把 t=3 价值抬到 V = X + gθ，但以概率 θ² 触发坏信号 s_b。经理目标函数（eq 10）：(1−ω)(X+gθ) + ωθ²π_X·X + ω(1−θ²)X。"
proof_technique: "对经理目标函数（eq 10）关于 θ 求一阶条件并取与 1 的较小者。"
source_papers: [edmans-2009-blockholder-trading-managerial-myopia]
predicts: [pc-attenuates-managerial-myopia]
date_updated: 2026-06-03
---

## Statement

> LEMMA 3. M chooses investment level θ given by θ = min((1−ω)g / (2ωX(1−π_X)), 1). If θ < 1, it is increasing in g and π_X, and decreasing in X and ω.

## Conditions

- 高质量企业经理 t=0 选投资 θ∈[0,1]，把 t=3 价值抬到 V=X+gθ，但以概率 θ² 触发 s_b。
- g 为投资生产率；投资无个人努力成本（不存在标准的 effort conflict）；投资机会不为市场与 B 所知。
- 目标函数（eq 10）：(1−ω)(X+gθ)+ωθ²π_X·X+ω(1−θ²)X。

## Proof Sketch

对 eq 10 关于 θ 求一阶条件，得内点解 (1−ω)g/(2ωX(1−π_X))，与上限 1 取小。投资随生产率 g 升、随"发出 s_b 的成本"降——后者正比于高低质量企业价值差 X 与经理短视权重 ω。

## Comparative Statics

- θ 随**市场效率 π_X 上升**而上升：π_X 越高，s_b 时股价跌得越少（更接近基本面），经理越敢做压低当期盈利的长期投资。
- θ 随 ω 上升而下降（经理越短视越欠投资）、随 X 上升而下降（质量差越大、s_b 误判成本越高）。
- 由于 π_X 又取决于持股 α（[[edmans-prop1-market-efficiency]]），投资 θ 经由 π_X 取决于 block size——这是通往主结果 [[edmans-prop2-investment]] 的桥。
- **短视是理性的**：s_b 后股价下跌（因可能来自低质量企业），经理为规避该下跌而把 θ 压到一阶最优 1 以下。

## Testable Implications

经由 π_X 把"价格效率 → 实体投资"接上，构成 [[pc-attenuates-managerial-myopia]] 的形式化内核。

## Related

- [[edmans-2009-blockholder-trading-managerial-myopia]]
- [[edmans-manager-myopia-weight]]
- [[edmans-prop2-investment]]
