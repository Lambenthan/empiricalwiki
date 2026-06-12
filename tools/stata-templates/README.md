# Stata 模板库

`/stata-plan --write-do` 生成 do 骨架时的参考模板，也可以直接复制改造。每个模板与 `wiki/identification/` 的同名预置策略卡配套：

| 模板 | 策略卡 | 适用 |
|------|--------|------|
| `twfe.do` | [[two-way-fixed-effects]] | 基准双向固定效应面板 |
| `did_staggered.do` | [[difference-in-differences]] | 经典 2×2 与多期交错 DID |
| `psm.do` | [[propensity-score-matching]] | PSM 与 PSM-DID |
| `iv_2sls.do` | [[instrumental-variables]] | 工具变量 2SLS |
| `rdd.do` | [[regression-discontinuity]] | 精确 / 模糊断点回归 |

约定：

- 所有模板假设主面板为 `stkcd × year`，已完成清洗（剔金融、剔 ST、缩尾）；清洗段在 `twfe.do` 开头给出一次，其余模板不重复。
- `// CHECK:` 注释是强制复核点（样本量、merge 结果、平衡性），跑完每段先看这些再往下走。
- 依赖的社区命令在各模板头部用 `ssc install` 列出，首次运行先装。
- 模板只是骨架：变量名、阈值、带宽、卡尺都要按你的研究改，不要原样照跑。
