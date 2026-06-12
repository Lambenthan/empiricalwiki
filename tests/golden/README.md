# 核心走廊金标准测试集

防止 ingest skill 改动导致抽取质量退化。三篇基准论文覆盖三种 ingest 形态：

| 基准 | 形态 | 考点 |
|------|------|------|
| `daifei-2025.golden.json` | `/empirical-ingest` 标准实证 | 变量×4、双数据集、IV+FE 双识别、机制+三假设 |
| `hunan-2021.golden.json` | `/empirical-ingest` 文本法实证 | 文本平台数据集、三异质性、2SRI 识别 |
| `stein-1988.golden.json` | `/theory-ingest` 理论建模 | 假设×5、命题×6、formalizes_mechanism 接桥、foundations 引用 |

## 何时跑

改动 `/empirical-ingest`、`/theory-ingest`、`/ingest` 或页面模板之后；升级 Claude Code / 换模型之后想确认抽取质量没掉时。

## 怎么跑

```bash
# 1. 开一个一次性沙盒（不要碰自己的真 wiki）
git worktree add /tmp/golden-run main && cd /tmp/golden-run
python3 tools/research_wiki.py init wiki

# 2. 用待测版本的 skill 重新 ingest 基准论文（在 Claude Code 里）
#    /empirical-ingest raw/papers/<代飞 2025 的 PDF>

# 3. 机器断言
python3 tools/golden_check.py --wiki wiki --golden tests/golden/daifei-2025.golden.json

# 4. 人工抽查：与 demo 分支上已校验的页面并排对比
git show demo:wiki/variables/patient-capital.md | less
```

## 断言设计（为什么不比对 slug）

LLM 每次生成的 slug 与措辞都会有合法差异，逐字 diff 全是噪声。金标准只断言两层**不该退化的结构事实**：

1. **边类型最小数量**：该论文应产出的每类边不少于历史校验值（如代飞 2025 至少 4 条 `operationalizes`）。
2. **关键构念落位**：核心构念关键词（如"耐心资本"）必须出现在对应类型目录的某个页面里——名字可以变，东西必须在。

数量减少或构念丢失即 FAIL，说明改动让抽取变浅了。新增更多边不算失败。

## 维护

基准论文的"正确答案"以 demo 分支的已校验页面为准。若你刻意改变抽取口径（如合并两个变量页），同步更新对应 golden 文件并在 commit message 里说明理由。
