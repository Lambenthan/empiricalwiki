---
description: 基于用户素材与可选外部发现搭建 ΩmegaWiki，并用并行 `/ingest` 完成最终论文集的消化
argument-hint: "[topic] [--no-introduction]"
---

# /init

> 从 `raw/` 搭建 wiki：先跑确定性 discovery planner，再由 LLM 做最终裁剪；`raw/notes/` 与 `raw/web/` 可种下 provisional 的 topics / ideas / concepts / claims；论文消化仍走并行 `/ingest` fan-out / fan-in。

## Inputs

- `topic`（可选）：研究方向关键词；如果 `raw/papers/` 已经给出了 seed set，或 notes/web 已经表达了意图，就可以省略
- `--no-introduction`（可选）：禁用外部找论文；只使用用户自有的 `raw/papers/`、`raw/notes/`、`raw/web/`
- 参数护栏：把 `topic` 与 `--no-introduction` 视为用户输入，而不是 agent 自行决定的策略开关；不得仅根据仓库状态推断 `--no-introduction`。`raw/papers/` 非空、`raw/notes/` 或 `raw/web/` 为空、或用户省略 `topic`，都不能单独成为启用 local-only 模式的理由。只有当用户明确要求禁用外部发现时，才可使用 `--no-introduction`。
- `raw/papers/`：用户自有论文来源（`.tex`、`.pdf`、压缩包）
- `raw/notes/`：用户笔记
- `raw/web/`：用户提供的网页存档

## Outputs

- 通过 `tools/research_wiki.py init` 建立 `wiki/` scaffold
- `raw/tmp/` — `/init` 生成的本地 prepared 来源
- `raw/discovered/` — `/init` 选中的外部论文（在 `--no-introduction` 时关闭）
- `wiki/Summary/{area}.md`、`wiki/topics/{topic}.md`、provisional `wiki/ideas/{slug}.md`、`wiki/concepts/{slug}.md`、`wiki/claims/{slug}.md`
- 通过并行 `/ingest` 创建的 `wiki/papers/*.md` 与论文驱动的 concepts / claims / people
- 更新后的 `wiki/index.md`、`wiki/log.md`、`wiki/graph/edges.jsonl`、`wiki/graph/context_brief.md`、`wiki/graph/open_questions.md`
- `.checkpoints/init-prepare.json`、`.checkpoints/init-plan.json`、`.checkpoints/init-sources.json`

## Wiki Interaction

### Reads

- `raw/papers/`、`raw/notes/`、`raw/web/`
- `.checkpoints/init-prepare.json` 与 `.checkpoints/init-sources.json`，供 resume / fan-out 使用
- `wiki/index.md` 以及已有 `wiki/topics/`、`wiki/ideas/`、`wiki/concepts/`、`wiki/claims/`

### Writes

- `wiki/` scaffold 与 provisional 页面
- `raw/tmp/` 与 `raw/discovered/`
- `wiki/index.md`、`wiki/log.md`、`wiki/graph/*`
- `.checkpoints/init-prepare.json`、`.checkpoints/init-plan.json`、`.checkpoints/init-sources.json` 与 `init-session` checkpoint metadata

### Graph edges created

- `/init` 本身只在 provisional 页面需要时写入少量 scaffold 级别的 edges
- 论文驱动的 edges 全部委托给 `/ingest`

## Workflow

**前置条件**：当前目录为项目根，且包含 `wiki/`、`raw/`、`tools/`。设 `WIKI_ROOT=wiki/`。先解析一次 `PYTHON_BIN`，并在整个 `/init` 流程里复用它，确保运行时使用与 `setup.sh` 安装依赖时相同的解释器：

```bash
if [ -x .venv/bin/python ]; then
  PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PYTHON_BIN=.venv/Scripts/python.exe
else
  PYTHON_BIN=python3
fi
export PYTHON_BIN
```

### Step 1: 初始化 wiki 结构

```bash
"$PYTHON_BIN" tools/research_wiki.py init wiki/
```

创建标准目录、`graph/`、`outputs/`、`index.md` 与 `log.md`。这里不要重复写第二条 init 日志。

### Step 2: 先把本地输入 prepare 到 `raw/tmp/`

```bash
"$PYTHON_BIN" tools/init_discovery.py prepare --raw-root raw --output-manifest .checkpoints/init-prepare.json
```

- 本地 PDF 能 decode 时，先转成 `raw/tmp/` 下的 synthetic `.tex`
- 对于不含嵌入 arXiv ID 的 PDF，尝试通过 Semantic Scholar 按标题搜索恢复 arXiv ID；恢复成功后，优先使用从 arXiv 抓取的原始 TeX 源码（`raw/tmp/papers/...-arxiv-src/`），而非 synthetic `.tex`
- notes / web 保持原始来源路径，`/init` 在 planning 阶段直接读取
- 本地论文若存在 usable 的 prepared `.tex`，其 `canonical_ingest_path` 必须指向 `raw/tmp/`
- decode / arXiv 源码抓取失败时记录 warning，而不是中止 `/init`
- 输出 manifest 到 `.checkpoints/init-prepare.json`

### Step 3: 基于 prepared 输入生成 plan、裁剪 shortlist，并写出最终 source manifest

```bash
"$PYTHON_BIN" tools/init_discovery.py plan [--topic "<topic>"] --mode auto --raw-root raw --wiki-root wiki --prepared-manifest .checkpoints/init-prepare.json --allow-introduction <true|false> --output-plan .checkpoints/init-plan.json
```

- `mode=seeded` 取决于 `.checkpoints/init-prepare.json` 中是否存在可解析本地论文；否则为 `bootstrap`
- `plan` 必须读取 prepare manifest，而不是重新扫描 `raw/`
- notes/web 的用户信号直接从原始来源文件读取
- 如果同一篇本地论文出现多个副本，优先级必须明确：原始本地 `.tex` > archive 解出的源码 `.tex` 或抓取到的 arXiv 源码目录 > 由 PDF 生成的 synthetic `.tex` > 原始 `.pdf`
- 若检测到中文 notes 或 web 内容，要保留 planner warning：当前 note/web 提取与排序对中文输入的可靠性可能更低，provisional 输出也应视为较低置信度
- seeded 模式下如果省略 `topic`，要从本地论文标题/摘要以及 notes/web 信号里提取 discovery 与 ranking 线索，而不是直接拒绝初始化
- 如果 seeded discovery 最终没有新增任何外部论文，也要继续用用户自带论文集往下走，而不是把它当成 fatal planner error
- 如果 `topic` 与 notes/web 关键词都缺失，bootstrap discovery 就没有可搜索的 query；此时应把它记为 planner error，而不是发起空搜索
- tool 先 over-pick 一个 **10-12** 篇的 shortlist
- tool 使用 S2 的 citations / references / search，以及可选 DeepXiv search
- 若 DeepXiv 可用，要在 tool 打分里显式使用返回的 `relevance_score`，而不是只在文字说明里提一句
- 若 `SEMANTIC_SCHOLAR_API_KEY` 未配置，也继续执行；但要把“走公开限速、会更慢”记录为 planner warning
- planner 输出、warnings、errors 都必须保存到 `.checkpoints/init-plan.json`

planner 评分策略：

- relevance = 30
- freshness = 20
- anchor/connectivity bonus = 20
- survey/benchmark/overview bonus = 15
- citation/centrality = 15
- 有 survey 就优先保留
- 最多保留一个偏旧 canonical anchor，而且只应在 bootstrap 或 seeded 且最终新增容量非常宽裕时考虑
- 在 seeded 模式且可新增论文空间有限时，不要预留偏旧 anchor；此时应让 freshness 主导，并防止偏旧的外部非 survey 论文仅凭 citation 优势堆积进入 shortlist
- 其余近分时 freshness 优先
- seeded 模式先看用户论文连接，再看 notes/web 偏好
- bootstrap 模式先 search，再从最强初始候选做 citation/reference 扩展

LLM 裁剪策略：

- 在 `fetch` 前读取 `.checkpoints/init-plan.json`，并把 over-pick 的 `shortlist` 明确裁成最终 **8-10** 篇
- 即使 shortlist 看起来已经“差不多”，也不得跳过裁剪步骤
- 默认保留所有可解析的用户论文，再用剩余名额选择 introduced 论文
- 若用户已提供超过 10 篇可解析论文，则不再新增外部论文
- 优先保留 survey/overview、在确有帮助时至多一篇偏旧 canonical anchor，以及来自不同 cluster 的近期代表作
- 当用户已经提供较充足的 seed set 时，应优先 freshness，并进一步降低偏旧 canonical 论文的优先级
- “至多一篇” 是上限，不代表必须保留一篇偏旧 canonical anchor
- 在 `fetch` 前，必须在工作流/响应中给出一个明确的最终选择结果，至少包含：`shortlist_count`、`final_count`，以及按 shortlist 顺序排列的最终 `candidate_id` 列表
- 若 `final_count` 不在 **8-10** 范围内，则必须先停止并修正最终选择，再执行 `fetch`；`--no-introduction` 或“用户已提供超过 10 篇可解析论文”这两种已说明例外除外
- `fetch` 只能接收最终选中的那组 `candidate_id`；禁止把整个 shortlist 默认原样转发，或默认把所有 shortlist ID 都传进去

若传入 `--no-introduction`：

- 只有在用户明确要求只使用本地论文时，才走这一分支
- 最终论文集 = `.checkpoints/init-prepare.json` 中所有可解析本地论文
- 仍然要执行 `fetch`（不给外部 ID），以写出 `.checkpoints/init-sources.json`

否则运行：

```bash
"$PYTHON_BIN" tools/init_discovery.py fetch --raw-root raw --plan-json .checkpoints/init-plan.json --prepared-manifest .checkpoints/init-prepare.json --output-sources .checkpoints/init-sources.json --id <candidate-id> --id <candidate-id>
```

- `/init` 下载的论文只允许写入 `raw/discovered/`，绝不写入 `raw/papers/`
- 若某篇 shortlist 论文已经由 prepared local source 覆盖，则禁止重复抓取
- `.checkpoints/init-sources.json` 是 Step 5 ingest 顺序的唯一真相源
- 用户本地论文在 `init-sources.json` 中以 `origin=user_local` 记录
- introduced 论文在 `init-sources.json` 中以 `origin=introduced` 记录，canonical path 位于 `raw/discovered/`

### Step 4: 在论文 ingest 前建立 scaffold 页面

创建一篇 `wiki/Summary/{area}.md`、若干 `wiki/topics/{slug}.md`，以及来自 notes/web 的 provisional `ideas/`、`concepts/`、`claims/`。

规则：

- notes/web 对“用户意图”是权威，对“文献置信度”不是权威
- 每个 notes/web 派生页面都必须在 frontmatter 后立即写入这一行：

```markdown
Provisional note: seeded from raw/notes or raw/web during /init; pending validation from ingested papers.
```

- `topics/`：方向被明确提到或反复出现时创建
- `ideas/`：用户明确提出或强烈暗示研究方向 / 假设时创建
- `concepts/`：技术机制在 notes/web 中反复出现，或在 notes/web 与最终论文集中各出现至少一次时创建
- `claims/`：只允许从显式断言创建，禁止靠推断补全

notes/web 派生 claim 的默认值：

```yaml
status: proposed
confidence: 0.2
source_papers: []
evidence: []
```

禁止创建 `people/` 页面与 `foundations/` 页面。此阶段直接创建的 scaffold 页面要同步写入 `wiki/index.md`。

### Step 4.5: commit scaffold、stash 无关脏文件、验证 merge 安全

spawn subagent 前：

- 运行 `git status --short`
- 将 `wiki/`、`raw/papers/`、`raw/tmp/`、`raw/discovered/` 与 `.checkpoints/init-*.json` 视作 scaffold 文件
- 将这些路径之外的脏文件先 stash：

```bash
UNRELATED=$(git status --short | awk '{print $2}' | grep -Ev '^(wiki/|raw/papers/|raw/tmp/|raw/discovered/|\.checkpoints/init-)' || true)
if [ -n "$UNRELATED" ]; then
  git stash push -u -m "init-unrelated-dirty-$(date +%Y%m%d-%H%M%S)" -- $UNRELATED
fi
```

- 记录 stash ref：

```bash
STASH_REF=$(git stash list | head -1 | cut -d: -f1)
"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session stash_ref "$STASH_REF"
```

- 在 worktree fan-out 前先记录当前 branch；`/init` 的 worktree 模式必须运行在一个有名字的 branch 上，不能处于 detached HEAD：

```bash
BASE_BRANCH=$(git branch --show-current)
if [ -z "$BASE_BRANCH" ]; then
  echo "/init 的 worktree 模式要求当前位于一个命名分支；请先切换到或创建分支。" >&2
  exit 1
fi
"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session base_branch "$BASE_BRANCH"
```

- 同时把最终选中的 paper IDs（post-trim 后的结果，不是 over-pick 的 shortlist）与 planner mode 写入 checkpoint metadata
- 验证 `.gitattributes` 对 `wiki/log.md`、`wiki/graph/edges.jsonl`、`wiki/index.md` 使用了 `merge=union`
- commit scaffold：

```bash
git add wiki/ raw/papers/ raw/tmp/ raw/discovered/ .checkpoints/init-prepare.json .checkpoints/init-plan.json .checkpoints/init-sources.json
git commit -m "init: scaffold before parallel ingest" --no-gpg-sign
BASE_COMMIT=$(git rev-parse HEAD)
"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session base_commit "$BASE_COMMIT"
```

### Step 5: 通过 worktree 隔离并行 ingest 论文

本步骤的论文来源只能来自 `.checkpoints/init-sources.json`：

- `origin=user_local`：优先 ingest `raw/tmp/` 中的 canonical prepared `.tex`；若 prepare 失败则回退到原始 `raw/papers/...`
- `origin=introduced`：ingest `raw/discovered/` 中抓取到的目录或 PDF

顺序以 `init-sources.json` 中的 `shortlist_rank` 为准，而不是重新扫目录或按 citation count。

为每篇论文启动一个 Agent 子代理，要求：

- `run_in_background: true`
- 使用 worktree isolation
- 从 `BASE_COMMIT` 新建临时 branch，绝不要直接复用已经签出的 `BASE_BRANCH`
- prompt 只使用**相对路径**
- 明确给出 INIT MODE skip 列表

每篇论文的 worktree 都应从当前 branch 上的 scaffold commit 拉出：

```bash
WT_BRANCH="init-${BASE_BRANCH//\//-}-<rank>-<paper-slug>"
WT_PATH="../.worktrees/$WT_BRANCH"
git worktree add -b "$WT_BRANCH" "$WT_PATH" "$BASE_COMMIT"
```

不要对当前 branch 名直接执行 `git worktree add`；Git 会因为该 branch 已经在主工作区签出而拒绝。

子代理 prompt 必须要求：

- 只对一个相对路径执行 `/ingest`
- 不得绕过 `/ingest`
- 在 INIT MODE 下，必须原样消费 handoff 给它的 canonical path，不能自己重选来源
- 跳过 `fetch_s2.py citations`
- 跳过 `fetch_s2.py references`
- 跳过每个子代理自己的 `rebuild-index`
- 跳过每个子代理自己的 `rebuild-context-brief`
- 跳过每个子代理自己的 `rebuild-open-questions`
- 跳过易冲突 topic 写入
- 仍然必须运行 `find-similar-claim` 与 `find-similar-concept`
- 退出前必须在各自 worktree 内提交 ingest 结果

全部子代理完成后：

1. 如有需要先切回 `BASE_BRANCH`，再按 planner 顺序在该 branch 上逐个 merge worktree branch
2. concept / claim 冲突默认保守合并，不要扩散近重复页面
3. 运行：

```bash
git switch "$BASE_BRANCH"
git merge --no-ff "$WT_BRANCH" --no-edit
git worktree remove "$WT_PATH"
git branch -d "$WT_BRANCH"
"$PYTHON_BIN" tools/research_wiki.py dedup-edges wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/
"$PYTHON_BIN" tools/lint.py wiki/ --fix
```

### Step 6: 最终报告与清理

报告中必须分开列出：

- 通过 `raw/tmp/` prepared path ingest 的用户论文
- 因 prepare 失败而回退到原始 `raw/papers/` 的用户论文
- `raw/discovered/` 中的 introduced 论文
- 由 notes/web 种下的 provisional 页面
- `/ingest` 新建的页面
- `/ingest` 更新过的页面
- 被跳过或失败的论文

若 `stash_ref` 存在，在最后再 pop。若 stash pop 失败，保留 checkpoint 并在报告中说明。

同时显式说明：

- `/prefill` 没有参与本次 `/init`
- 没有自动创建 foundations
- `people/` 与 claim 数量控制仍是后续 `/ingest` 任务

## Constraints

- `raw/papers/`、`raw/notes/`、`raw/web/` 是用户自有输入
- `raw/tmp/` 与 `raw/discovered/` 是 `/init` 生成的 handoff 区
- `/init` 只能把外部论文写到 `raw/discovered/`，把生成的 prepared local source 写到 `raw/tmp/`
- `/prefill` 只是可选背景预填充，不属于 `/init`
- 只有 `/prefill` 可以自动创建 foundations
- `/init` 不得直接创建 `people/` 页面
- notes/web 派生页面必须包含上面的 exact provisional notice
- provisional 状态不引入新的 frontmatter 字段
- 对 claim 置信度与 concept 合并，论文证据永远高于 notes/web
- 所有论文 ingest 必须通过并行 `/ingest` 子代理执行
- Step 5 必须读取 `.checkpoints/init-sources.json`，不得临时扫描 `raw/papers/` / `raw/tmp/` / `raw/discovered/`
- 子代理 prompt 只能出现相对路径

## Error Handling

- **`raw/papers/` 无可解析论文**：自动切换到 bootstrap 模式
- **`raw/notes/` 与 `raw/web/` 为空**：跳过 provisional seeding，继续
- **prepare 阶段的 PDF decode 失败**：把 warning 记入 `.checkpoints/init-prepare.json`，必要时回退到原始路径
- **`raw/notes/` 或 `raw/web/` 中检测到中文内容**：继续执行，但要保留 planner warning，说明当前 note/web 提取与排序对中文输入的可靠性可能更低，并把 rankings 与 provisional 页面视为较低置信度
- **S2 或 DeepXiv 不可用**：planner 使用剩余来源并继续执行；把 warning 保留在 checkpoint plan 中，并在最终报告里注明 discovery 降级
- **本地 PDF 的 arXiv ID 恢复或 TeX 源码抓取失败**：把 warning 记入 `.checkpoints/init-prepare.json`，回退到 synthetic `.tex` 或原始 PDF 路径，然后继续
- **某篇外部论文下载失败**：保留其余最终论文集，报告失败项
- **单篇 ingest 失败**：写 checkpoint，跳过该篇，继续其他论文，并在最终报告中列出
- **当前 checkout 处于 detached HEAD**：在 worktree fan-out 前停止，并要求用户先切换到或创建一个命名分支
- **worktree branch 没有 commit**：停止并先修复该 worktree，再进入 merge
- **stash pop 失败**：保留 checkpoint metadata，并给出手动恢复提示

## Dependencies

### Tools (via Bash)

- `"$PYTHON_BIN" tools/research_wiki.py init wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session <key> <value>`
- `"$PYTHON_BIN" tools/research_wiki.py checkpoint-save/load/clear wiki/ init-session ...`
- `"$PYTHON_BIN" tools/research_wiki.py dedup-edges wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py log wiki/ "<message>"`
- `"$PYTHON_BIN" tools/init_discovery.py prepare --raw-root raw --output-manifest .checkpoints/init-prepare.json`
- `"$PYTHON_BIN" tools/init_discovery.py plan [--topic "<topic>"] --mode auto --raw-root raw --wiki-root wiki --prepared-manifest .checkpoints/init-prepare.json --allow-introduction <true|false> --output-plan .checkpoints/init-plan.json`
- `"$PYTHON_BIN" tools/init_discovery.py fetch --raw-root raw --plan-json .checkpoints/init-plan.json --prepared-manifest .checkpoints/init-prepare.json --output-sources .checkpoints/init-sources.json --id <candidate-id>`
- `"$PYTHON_BIN" tools/lint.py wiki/ --fix`

### Skills

- `/ingest` — 每个子代理只 ingest 一篇论文，且运行在 INIT MODE

### `init_discovery.py` 内部使用的外部 API

- Semantic Scholar
- DeepXiv（可选）
- arXiv 下载端点
