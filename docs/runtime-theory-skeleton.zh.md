# 理论建模通用骨架

> TheoryWiki 的设计基准。任何形式化经济学模型——博弈论、一般均衡、契约理论、机制设计、宏观 DSGE、资产定价、产业组织——都共享同一副逻辑骨架。理论 ingest 时对着这 6 个固定槽位抽取。
>
> 实证论文的"固定模板"(变量/数据/模型/识别)是**范式绑定**的；理论的这 6 部分是**逻辑语法**,跨子领域更普适。难点不在结构,在于**忠实填充**:形式化陈述必须逐字引用、禁止释义。

---

## 6 个固定槽位 → 页面类型映射

| # | 槽位 | 装什么 | 落到哪 |
|---|------|--------|--------|
| ① | **环境 / 原语** | 谁(参与人)、能做什么(行动/策略)、想要什么(偏好/支付)、知道什么(信息)、何时(时序)、约束(技术/可行集) | `assumptions/` + 论文页 `## 模型环境` |
| ② | **解概念** | Nash / 子博弈精炼 / 贝叶斯精炼 / 竞争均衡 / 理性预期均衡 … | `foundations/`(可复用、终端节点) |
| ③ | **结果** | 命题/定理/引理:存在性、刻画、唯一性、福利、比较静态 | `propositions/` |
| ④ | **论证** | 证明技术:不动点、逆向归纳、包络定理、显示偏好、反例 … | `propositions/` 的 `proof_technique` 字段 |
| ⑤ | **比较静态** | 内生量随参数怎么动(模型的"预测引擎") | `propositions/`(proposition_type: comparative_statics)或正文 `## Comparative Statics` |
| ⑥ | **可检验推论** | 模型吐出的、能拿去实证的符号关系 | `hypotheses/` ← **理论↔实证的桥** |

①里"模型原语"按页拆进 `assumptions/`;整体环境叙述放论文页 `## 模型环境`。②③④⑤⑥ 各有对应。

---

## 抽取顺序(理论 ingest 的固定流程)

1. **环境/原语** → 通读模型设定段,逐条拆 `assumptions/`,论文页写 `## 模型环境`
2. **解概念** → 识别均衡概念,链到或新建 `foundations/`
3. **结果** → 每个命题/定理/引理一页 `propositions/`,`formal_statement` **逐字引用**,`conditions` 写清成立条件
4. **论证** → 填 `proof_technique`(查不到写"未报告",不猜)
5. **比较静态** → 进 `propositions/` 字段或正文
6. **可检验推论** → 落 `hypotheses/`,写正向边 `predicts`(命题→假设)

---

## 桥边:理论与实证在同一张 graph 上接上

```
theory-paper --assumes-->              assumptions/X
theory-paper --proves-->               propositions/P
theory-paper --formalizes_mechanism--> mechanisms/M   (与实证共享)
propositions/P --predicts-->           hypotheses/H   (理论侧)
empirical-paper --tests_hypothesis-->  hypotheses/H   (实证侧,既有边)
empirical-paper --tests_mechanism-->   mechanisms/M   (实证侧,既有边)
theory-paper --derived_from-->         foundations/F
```

接上之后,一个 `mechanisms/` 或 `hypotheses/` 页面同时挂着**理论侧(谁建了模型)**与**实证侧(谁验了证)**。可对 graph 提问:"这个机制谁从理论上证明了、谁实证检验了、结论一致吗?"——这是纯实证 wiki 给不了的视角。

边的语义与置信度规则见 `tools/_schemas.py` 的 `EDGE_TYPE_SPECS`(`theory_ingest` workflow):`assumes`/`proves` 是确定的结构事实,不带 confidence;`formalizes_mechanism`/`predicts` 是判断,需带 `confidence: high|medium|low`。

---

## 边界

- 这套骨架覆盖**解析式/形式化理论**。纯计算的 agent-based / 仿真模型偏实验性质,落 `experiments/` 更合适,不进 `propositions/`。
- 纯公理化决策论(表示定理)也适用:①的原语=偏好公理,③=表示定理,②时序等槽位留空即可。
- `propositions/` 不可与 `claims/` 混用:命题是被证明的形式化结果,claim 是带置信度的实证断言。
