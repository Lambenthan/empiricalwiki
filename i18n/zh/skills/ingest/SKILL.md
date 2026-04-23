---
description: 消化一篇论文，创建 wiki 页面（papers + concepts + people + claims）并建立所有交叉引用与图谱边
argument-hint: <local-path-or-arXiv-URL>
---

# /ingest

> 消化一篇论文，完整纳入 wiki：创建 paper 页面，提取/创建 concepts、people、claims，
> 建立所有双向交叉引用，维护 graph edges，更新 index.md 和 log.md。
> 这是 wiki 最核心的 skill——所有知识通过 ingest 流入。

## Inputs

- `source`：本地 `.tex` / `.pdf` 路径、`/init` 交接的规范来源路径（例如 `raw/tmp/...` 下的合成 `.tex`，或 `raw/discovered/...` 下抓取到的源码目录 / PDF），或 arXiv URL（如 `https://arxiv.org/abs/2106.09685`）

## Outputs

- `wiki/papers/{slug}.md` — 论文页面
- `wiki/concepts/{slug}.md` — 新发现概念的页面（若 wiki 中不存在）
- `wiki/people/{slug}.md` — 重要作者页面（importance >= 4 且 wiki 中不存在）
- `wiki/claims/{slug}.md` — 论文提出的核心 claims（若 wiki 中不存在）
- 更新的交叉引用页面（concepts、topics、people、claims 的反向链接）
- 更新的 `wiki/graph/edges.jsonl`
- 更新的 `wiki/graph/context_brief.md` 和 `wiki/graph/open_questions.md`
- 更新的 `wiki/index.md` 和 `wiki/log.md`

## Wiki Interaction

### Reads
- `wiki/index.md` — 获取所有已有页面的 slug 和 tags，用于匹配
- `wiki/papers/*.md` — 检查论文是否已收录
- `wiki/concepts/*.md` — 匹配已有概念，追加 key_papers
- `wiki/topics/*.md` — 匹配研究方向，追加论文
- `wiki/people/*.md` — 匹配已有作者
- `wiki/claims/*.md` — 匹配已有 claims，追加 evidence
- `wiki/graph/open_questions.md` — 检查论文是否填补已知知识缺口

### Writes
- `wiki/papers/{slug}.md` — CREATE
- `wiki/concepts/{slug}.md` — CREATE（新概念）或 EDIT（追加 key_papers）
- `wiki/topics/{slug}.md` — EDIT（追加 seminal_works / recent_work）
- `wiki/people/{slug}.md` — CREATE（新作者）或 EDIT（追加 Key papers）
- `wiki/claims/{slug}.md` — CREATE（新 claim）或 EDIT（追加 evidence）
- `wiki/graph/edges.jsonl` — APPEND（通过 tools/research_wiki.py add-edge）
- `wiki/graph/context_brief.md` — REBUILD
- `wiki/graph/open_questions.md` — REBUILD
- `wiki/index.md` — EDIT
- `wiki/log.md` — APPEND

### Graph edges created
- `paper → concept`: `supports` / `extends`
- `paper → paper`: `extends` / `contradicts` / `supersedes`
- `paper → claim`: `supports` / `contradicts`
- `concept → topic`: (if new concept discovered under existing topic)

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。
设 `WIKI_ROOT=wiki/`。

### Step 1: 解析来源

1. 检测 source 类型：
   - **arXiv URL**：尝试获取 tex source（ar5iv HTML 或直接下载 .tex）；若失败则下载 PDF
   - **本地 .tex**：直接读取
   - **本地 .pdf**：先读取 PDF，在有把握时恢复标题；如果 agent 已经拿到可信 arXiv ID，也一并保留；然后运行 `python3 tools/prepare_paper_source.py --raw-root raw --source <local-path> [--title "<recovered-title>"] [--arxiv-id "<recovered-arxiv-id>"]`；该 helper 会优先使用 handoff 进来的或 filename/path 中的 arXiv ID，再尝试 agent 标题经 Semantic Scholar 的恢复，否则就直接回退到 synthetic `.tex`。如果 agent 已经提供标题，就把它当作 authoritative title；抓取源码里的标题只能作为清洗后的 fallback metadata
   - **INIT MODE 规范交接路径**：若 `/init` 传入来自 `.checkpoints/init-sources.json` 的路径，则直接 ingest 该 `canonical_ingest_path`，不要重新扫描相邻 raw 目录
2. 提取元数据：标题、摘要、作者列表（含机构）、发表日期、venue
3. 提取参考文献列表（BibTeX entries 或 reference section）
4. raw 来源持久化规则：
   - 若交接的 source 已位于 `raw/discovered/` 或 `raw/tmp/`，则直接把该路径视为 canonical source，不要再复制到 `raw/papers/`
   - 若 source 是直接给定的 arXiv URL，则把抓取到的原始来源保存到 `raw/discovered/` 并从那里 ingest；不要把抓取来源写入 `raw/papers/`

### Step 2: 预处理与标注

1. **生成 slug**：
   ```bash
   python3 tools/research_wiki.py slug "<paper-title>"
   ```
2. **检查重复**：在 `wiki/papers/` 中查找是否已有相同 slug 或 arxiv ID。若已存在，提示用户并终止。
3. **提取关键词**：从标题和摘要中抽取 3-8 个核心关键词
4. **标注领域**：判断所属研究领域（NLP / CV / ML Systems / Robotics 等）
5. **查询 Semantic Scholar**（若有 arXiv ID）：
   ```bash
   python3 tools/fetch_s2.py paper <arxiv_id>
   ```
   获取引用量、s2_id，结合顶会身份和相关性评估 importance（1-5）
6. **DeepXiv 增强**（若有 arXiv ID，可选）：
   ```bash
   python3 tools/fetch_deepxiv.py brief <arxiv_id>
   ```
   使用 TLDR 辅助 Key idea 段落初稿，使用 keywords 补充 tags。
   ```bash
   python3 tools/fetch_deepxiv.py head <arxiv_id>
   ```
   使用论文结构信息（section names + TLDRs）验证/补充从 tex/pdf 解析的结构。
   ```bash
   python3 tools/fetch_deepxiv.py social <arxiv_id>
   ```
   社交影响力指标作为 importance 评估的辅助信号（高 tweet 数 → 社区关注度高）。
   **若 DeepXiv 不可用**：跳过所有 DeepXiv 步骤，仅依赖 S2 + 源文件解析（回退到原有行为）。
7. **提取图表描述**：figure/table captions；关键图表可送 vision API 解读
7. **Appendix 摘要**（非全文提取）

### Step 3: 创建 paper 页面

按 CLAUDE.md paper 模板填写所有字段，生成 `wiki/papers/{slug}.md`：

- frontmatter：title, slug, arxiv, venue, year, tags, importance, date_added, source_type, s2_id, keywords, domain, code_url, cited_by
- 正文各节：Problem, Key idea, Method, Results, Limitations, Open questions, My take, Related

### Step 4: 识别 Claims（先找已有，确认没有才新建）

> 🚨 **关键 — Step 4 开始前必读。**
> Claims 在多篇论文之间是**共享**的。多篇论文通常以不同证据支持**同一个命题**。你的任务是找到每篇论文所支持的已有 claim，而**不是**每篇论文都新建一个 claim。在生产（test6 OmegaWiki，15 篇论文）中，这一步此前被随意执行，产生了 45 个 claim — 其中 4 个 claim 都在表达"方法 X 产生的 prompt 超越人工/手写 prompt"。这浪费了大量时间，并破坏了 claim-graph 推理。**下面的去重工具就是为了防止这种情况。请使用它。**

**每篇论文的硬上限：**
- importance < 5：**最多 1 个新 claim**
- importance == 5（seminal）：**最多 2 个新 claim**
- 该论文支持的所有其他 claim 必须与已有 claim 匹配（见下面 Branch A 或 B）

#### Step 4.1: 识别候选 claims

阅读论文的贡献部分和摘要。列出论文明确断言的 1-3 个主要实证或概念性命题。每个候选包含：
- 一个简短标题（命题本身，例如 "LLM-optimized prompts outperform human-written prompts"）
- 若干 tag（例如 `prompt-optimization,llm`）

#### Step 4.2: 对每个候选，搜索已有等价项 — 强制调用工具

```bash
python3 tools/research_wiki.py find-similar-claim wiki/ "<候选 claim 标题>" --tags "<逗号分隔的 tags>"
```

这是一个确定性工具，使用规范化 token 匹配 + tag 加权 Jaccard。它返回一个按相似度降序排序的 JSON 列表，例如：

```json
[
  {
    "slug": "llm-prompts-beat-human",
    "title": "LLM-optimized prompts outperform human-written prompts",
    "tags": ["prompt-optimization", "llm"],
    "status": "weakly_supported",
    "confidence": 0.7,
    "source_papers": ["opro"],
    "score": 0.62,
    "match_reason": "canonicalized token Jaccard 0.56; tags shared: ['prompt-optimization']"
  }
]
```

空列表 `[]` 表示没有相似 claim，可以进入 Branch C。

#### Step 4.3: 基于 JSON 结果分支处理

**Branch A — top 结果 score >= 0.80**（或精确标题匹配 score == 1.0）：
这是**同一个 claim**。**不要**新建文件。请执行：
1. 读取已有 claim 文件：`wiki/claims/<top-slug>.md`
2. 在其 `evidence` 列表追加新 entry：
   ```yaml
   - source: <paper-slug>
     type: supports        # 或 contradicts
     strength: moderate    # weak | moderate | strong
     detail: "<来自本文的一句话证据摘要>"
   ```
3. 将 `<paper-slug>` 追加到 claim 的 `source_papers`（若不存在）
4. 重新评估 `confidence` 和 `status`：更多强证据 ⇒ 更高 confidence；证据混杂 ⇒ `weakly_supported`
5. 添加 graph edge：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to claims/<top-slug> --type supports --evidence "<detail>"
   ```
6. 在 paper 页面的 `## Related` 追加 `supports: [[<top-slug>]]`

**Branch B — top 结果 score 0.40-0.80**（相似但不完全一致）：
读取已有 claim 的标题和 `## Statement` 段落。做出判断：
- 如果两者表达**同一命题**但措辞不同 → 按 Branch A 处理
- 如果两者是**真正不同的命题**只是共享词汇 → 按 Branch C 处理

**不确定时默认走 Branch A。** 过度合并的代价远小于过度创建：错误合并的 claim 以后可以拆分，但大量近似重复的 claim 会毒化所有下游推理。若选择 Branch C，必须指出命题中具体哪个方面是真正新颖的。

**Branch C — top 结果 score < 0.40 或列表为空**：
没有已有 claim 覆盖该命题。
1. **先检查硬上限。** 清点你已为本文创建了多少个新 claim。若达到上限（importance < 5 时为 1，importance == 5 时为 2），**停止创建新 claim**。强制将剩余候选转入 Branch A — 从刚才的 `find-similar-claim` 结果中选最接近的已有 claim 合并，即使 score < 0.40。
2. 否则，按 CLAUDE.md 模板创建 `wiki/claims/{claim-slug}.md`：
   - 生成 slug：`python3 tools/research_wiki.py slug "<claim-title>"`
   - status：`proposed` 或 `weakly_supported`（取决于论文证据强度）
   - source_papers：`[<paper-slug>]`
   - 用本文的 entry 初始化 `evidence`
3. 添加 graph edge + 更新 paper 的 `## Related`（与 Branch A 的第 5-6 步相同）

#### Step 4.4: Step 4 末尾的强制自检

记录本次 ingest 匹配和新建了多少 claim：
```bash
python3 tools/research_wiki.py log wiki/ "ingest | claims for <paper-slug>: N matched existing, M new"
```

**如果 M 超过硬上限**，说明你违反了约束。停止、撤销多余的新 claim 文件，将它们转换为 Branch A 的追加操作。

#### 反模式（绝不要这样做）

- ❌ **跳过 `find-similar-claim`**，理由是"我已经知道这是新 claim" — 你不知道，test6 事故已经证明了
- ❌ **对每个主要贡献都创建一个新 claim**，不检查是否已被已有 claim 覆盖
- ❌ **仅用 slug 对比**（"slug 不同所以 claim 不同"）— slug 是由标题自动生成的，paraphrase 即使表达同一命题也会得到不同 slug
- ❌ **把 Branch B 当成"默认新建"** — 默认动作是合并，不是拆分

### Step 5: 处理交叉引用

**Part A — Concepts 匹配与创建（先找已有，确认没有才新建）**

> 🚨 **关键 — 新建任何 concept 页面前必读。**
> Concepts 在多篇论文之间是**共享**的。多篇论文通常是在深化已有概念，而不是引入新概念。你的任务是找到每篇论文所扩展的已有 concept，把该论文追加到其 `key_papers`，而**不是**每篇论文都新建一个 concept。在生产（test6 OmegaWiki，15 篇论文）中，这一步此前产生了 37 个 concept，其中包括 3 个表达"LLM 作为梯度"的 concept（`textual-gradient-descent`、`textual-gradient-optimization`、`verbal-gradient`）以及 2 个表达"LLM 作为进化算子"的 concept（`llm-driven-evolutionary-operators`、`llms-evolutionary-operators`）。**下面的去重工具就是为了防止这种情况。请使用它。**

**每篇论文的硬上限（只统计新建的 concept 页面）：**
- importance < 5：**最多 1 个新 concept**
- importance == 5（seminal）：**最多 3 个新 concept**
- 该论文涉及的所有其他 concept 必须匹配到已有 concept，或引用已有 foundation（见下面 Branch 0 / Branch A / Branch B）
- Foundation 引用（Branch 0）**不计入**硬上限 — 引用背景知识是零成本操作

#### Step 5.A.1: 识别候选 concepts

阅读论文的 method/approach 部分。列出论文引入或显著扩展的 1-3 个技术概念。每个候选包含：
- 一个标题（例如 "Textual Gradient Descent"）
- 若干论文中使用的别名（例如 `["natural language gradient", "text gradient", "APO gradient"]`）

#### Step 5.A.2: 对每个候选，搜索已有等价项 — 强制调用工具

```bash
python3 tools/research_wiki.py find-similar-concept wiki/ "<候选 concept 标题>" --aliases "<逗号分隔的别名>"
```

这是一个确定性工具，通过精确标题、别名重叠、短语包含、token Jaccard 进行匹配。它**同时扫描 `wiki/concepts/` 和 `wiki/foundations/`**，每个结果带有 `entity_type: "concept"` 或 `entity_type: "foundation"` 标签。结果会让 foundation 命中优先排在最前面，然后按 score 降序返回 concepts。例如：

```json
[
  {
    "entity_type": "foundation",
    "slug": "attention-mechanism",
    "title": "Attention Mechanism",
    "aliases": ["scaled dot-product attention", "self-attention"],
    "score": 0.85,
    "match_reason": "phrase containment: 'self-attention' ↔ 'attention mechanism'"
  },
  {
    "entity_type": "concept",
    "slug": "textual-gradient-descent",
    "title": "Textual Gradient Descent",
    "aliases": ["natural language gradient", "text gradient"],
    "key_papers": ["protegi"],
    "maturity": "emerging",
    "score": 1.0,
    "match_reason": "exact normalized match: 'Natural Language Gradient' == 'natural language gradient'"
  }
]
```

空列表 `[]` 表示没有相似 concept 或 foundation；可以进入 Branch C。

#### Step 5.A.3: 基于 JSON 结果分支处理

**Branch 0 — 任意结果 `entity_type: "foundation"` 且 score >= 0.80**（**在评估 Branch A 之前先判断此分支**）：
候选属于基础背景知识。**不要新建 concept 页面，也不要修改 foundation 页面（foundations 是终端节点 — 不写反向链接）。**
1. 在 paper 的 `## Related` 追加 `[[<foundation-slug>]]`（直接引用 foundation）
2. 添加 graph edge：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to foundations/<foundation-slug> --type derived_from --evidence "<一句话摘要>"
   ```
3. **绝不**把该论文写入 foundation 的 frontmatter — foundations 不写反向链接。
4. 该候选**不计入**每篇论文的硬上限。

如果 top 结果是 foundation 但 score 在 0.40-0.80 之间，读 foundation 的 `## Definition`。如果确实是同一个教科书概念，按 Branch 0 处理；如果论文是在该背景之上提出了具体的新技术机制，则继续评估 Branch A/B/C — 但在引用相应 concept 的同时，也向 foundation 写一条 `derived_from` 边。

**Branch A — top concept 结果（entity_type "concept"）score >= 0.85**（精确、别名或短语包含）：
这是**同一概念**。**不要**新建文件。请执行：
1. 读取已有 concept 文件：`wiki/concepts/<top-slug>.md`
2. 将 `<paper-slug>` 追加到其 `key_papers`（若已存在则跳过）
3. 若论文使用了一个不在该 concept `aliases` 中的新别名，追加进去
4. 若论文引入了值得记录的 variant，在该 concept 的 `## Variants` 追加一个条目
5. 添加 graph edge：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to concepts/<top-slug> --type supports --evidence "<一句话摘要>"
   ```
6. 在 paper 页面的 `## Related` 追加 `[[<top-slug>]]`

**Branch B — top concept 结果 score 0.40-0.85**（相似但不完全一致）：
读取已有 concept 的 `## Definition` 和 `## Intuition`。做判断：
- 若两者指**同一技术思想**（一个是更具体的名称、替换措辞或子类）→ 按 Branch A 处理。若候选是有意义的子类，也追加到 `## Variants`。
- 若两者是**真正不同的技术思想**只是共享词汇 → 按 Branch C 处理。

**不确定时默认走 Branch A。** 过度合并的代价远小于过度创建：错误合并的 concept 以后可以拆分（`## Variants` 历史会保留），但大量近似重复的 concept 会毒化 gap 检测、引用图和 survey 生成。若选择 Branch C，必须指出具体的技术区别（不同机制、不同数学形式化、不同应用类别）。

**Branch C — top 结果 score < 0.40 或列表为空**：
没有已有 concept 或 foundation 覆盖该想法。
1. **先检查硬上限。** 清点你已为本文新建的 concept 页面数量（Branch 0 的 foundation 引用不计入）。若达到上限（importance < 5 时为 1，importance == 5 时为 3），**停止创建新 concept**。强制将剩余候选转入 Branch A — 从 `find-similar-concept` 结果中选最接近的已有 concept 合并，即使 score < 0.40。
2. 否则，按 CLAUDE.md 模板创建 `wiki/concepts/{concept-slug}.md`：
   - 生成 slug：`python3 tools/research_wiki.py slug "<concept-title>"`
   - maturity：`emerging`
   - key_papers：`[<paper-slug>]`
   - aliases：列出论文中找到的所有别名（尽量齐全 — 这个列表决定了未来 ingest 能否匹配到）
3. 在 paper 页面的 `## Related` 追加 `[[<concept-slug>]]`
4. 添加 graph edge（与 Branch A 第 5 步相同）

#### Step 5.A.4: Part A 末尾的强制自检

记录本次 ingest 匹配、新建、foundation-引用 的 concept 数量：
```bash
python3 tools/research_wiki.py log wiki/ "ingest | concepts for <paper-slug>: N matched existing, M new, F foundation-refs"
```

**如果 M 超过硬上限**，说明你违反了约束。停止、撤销多余的新 concept 文件，将它们转换为 Branch A 的追加操作。

#### 反模式（绝不要这样做）

- ❌ **跳过 `find-similar-concept`**，理由是"我在 /ingest 开始时已经把所有 concept 页面都读过了" — 即使你读了，test6 事故已证明人眼去重会漏掉 paraphrase；而且你还需要 foundations 扫描
- ❌ **对论文中每个技术思想都新建一个 concept**，不检查是否已被已有 concept 或 foundation 覆盖
- ❌ **仅用 slug 对比** — slug 是由标题自动生成的，同一思想换个措辞就会得到不同 slug（test6：`llm-driven-evolutionary-operators` vs `llms-evolutionary-operators`）
- ❌ **把 Branch B 当成"默认新建"** — 默认动作是合并，不是拆分
- ❌ **把已有 concept 的"更一般"或"更具体"版本作为新页面创建** — 改为用 `## Variants` 扩展已有 concept
- ❌ **向 foundation 页面写反向引用** — foundations 是终端节点；它们根本没有 `key_papers` 这类字段，任何反向链接都违反不变量。只允许 paper → foundation 的 edge 以及 paper `## Related` 中的 `[[foundation-slug]]`。

**Part B — Topics 匹配：**

1. 将论文 domain/tags 与已有 topics 匹配
2. 对每个匹配的 topic：
   - importance >= 4：追加到 `## Seminal works`
   - importance < 4：追加到 `## SOTA tracker` 或 `## Recent work`（按年份）
3. 若论文与已有 topic 的 `## Open problems` 或 `## Research gaps` 直接相关：在 topic 页面标注

**Part C — Semantic Scholar 外部引用：**

1. 若有 arXiv ID，查询 citations 和 references：
   ```bash
   python3 tools/fetch_s2.py citations <arxiv_id>
   python3 tools/fetch_s2.py references <arxiv_id>
   ```
2. 对 citations 中已在 wiki 的论文：自动回填 `cited_by`
3. 对 references 中高引但 wiki 未收录的：在报告中列出建议后续 ingest

### Step 6: 处理作者

1. 提取第一作者和通讯作者
2. 对每位关键作者：
   - **若 `wiki/people/{author-slug}.md` 存在**：追加本文到 `## Key papers`；反向在 paper 中添加 `[[author-slug]]`
   - **若不存在且 importance >= 4**：按 CLAUDE.md people 模板创建页面
3. 对匹配的 topic，若作者是该领域关键人物：追加到 topic 的 `key_people`，反向在 people 的 `## Research areas` 追加

### Step 7: 更新导航与图谱

1. **index.md**：在对应分类下追加所有新建/修改的页面条目
   ```bash
   # 格式参照 CLAUDE.md 的 index.md 格式节
   ```
2. **log.md**：
   ```bash
   python3 tools/research_wiki.py log wiki/ "ingest | added papers/<slug> | updated: <list-of-updated-pages>"
   ```
3. **重建 graph 派生文件**：
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

### Step 8: 报告给用户

输出摘要，包含：
- 创建的页面列表（papers, concepts, people, claims）
- 更新的页面列表（追加了交叉引用的页面）
- 提取的 claims 及其状态
- 添加的 graph edges 数量
- 发现的矛盾点（若有）
- S2 发现的高引未收录论文建议列表（若有）

### Step 9: Wiki Growth 报告

```bash
python3 tools/research_wiki.py maturity wiki/ --json
```

在报告末尾追加一行 wiki 状态摘要：

```
Wiki: +1 paper, +{N} claims, +{M} concepts, +{K} edges | Maturity: {level} ({coverage}% coverage)
```

## Constraints

- **raw/ 除 canonical source prep 外只读**：把 `raw/papers/`、`raw/notes/`、`raw/web/` 当作用户自有输入。直接本地 `/ingest` 只能把生成的 prepared local sidecar 写到 `raw/tmp/`，直接 arXiv ingest 只能把抓取到的来源写到 `raw/discovered/`。INIT MODE `/ingest` 仍然只读，并且必须直接消费交接的 canonical path。
- **INIT MODE 的来源交接具有最高优先级**：当 `/init` 从 `.checkpoints/init-sources.json` 传入 `canonical_ingest_path` 时，直接 ingest 该路径，不要重新扫描 `raw/papers/`、`raw/tmp/` 或 `raw/discovered/`
- **graph/ 仅通过 tools 维护**：不得手动编辑 `graph/` 下的文件，仅通过 `python3 tools/research_wiki.py` 操作
- **双向链接**：写正向链接时同步写反向链接（参照 CLAUDE.md Cross Reference 规则表）
- **tex 优先**：.tex > .pdf > vision API fallback
- **slug 通过工具生成**：必须使用 `python3 tools/research_wiki.py slug` 生成 slug，不得手动拼写
- **index.md 立即更新**：每次 ingest 完成前必须更新 index.md
- **log.md append-only**：通过 `python3 tools/research_wiki.py log` 追加
- **importance 评分标准**：1=niche, 2=useful, 3=field-standard, 4=influential, 5=seminal
- **claim 提取保守**：仅提取论文明确主张的核心贡献，不过度推断
- **去重是强制的，不是可选的**：创建任何新 claim 或 concept 页面前，必须运行 `find-similar-claim` / `find-similar-concept` 并遵循 Step 4 / Step 5.A 的分支逻辑。`find-similar-concept` 同时扫描 `concepts/` 和 `foundations/`；foundation 命中走 Branch 0（仅引用，绝不新建）。跳过去重工具是 wiki 膨胀的头号原因。
- **每篇论文硬上限**：最多 1 个新 claim + 1 个新 concept（importance == 5 时为 2 个 claim + 3 个 concept）。其余候选必须通过 Branch A 匹配到已有 entity，或通过 Branch 0 引用 foundation。不确定时合并。
- **Foundations 是终端节点**：绝不从 paper 向 foundation 的 frontmatter 写反向链接。Foundation 引用只存在于 paper 的 `## Related` 和 `edges.jsonl` 中。

## Error Handling

- **来源解析失败**：tex 失败 → PDF 解析 → vision API → 报告用户手动处理。对于直接本地 PDF，如果没有恢复出可信标题，就在不带 `--title` 的情况下调用 `tools/prepare_paper_source.py`；这意味着只允许 filename/path arXiv-ID 恢复，然后立刻回退到 synthetic `.tex`。metadata 或 filename 标题只用于显示，不能驱动按标题检索。INIT MODE 下，`raw/tmp/` 中的合成 `.tex` 与 `raw/discovered/` 中的抓取源码目录 / PDF 都是合法输入，应按交接路径直接消费。
- **S2 API 不可用**：跳过 S2 相关步骤（citations 回填、importance 使用默认值 3），在报告中注明
- **DeepXiv API 不可用**：跳过 DeepXiv 增强步骤（TLDR、结构验证、社交指标），仅依赖 S2 + 源文件解析
- **slug 冲突**：若生成的 slug 已存在但内容不同，追加数字后缀（如 `attention-mechanism-2`）
- **wiki 目录不存在**：运行 `python3 tools/research_wiki.py init wiki/` 初始化后重试
- **部分步骤失败**：已完成的步骤保留，未完成的步骤在报告中列出，供用户手动补全

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — slug 生成
- `python3 tools/research_wiki.py find-similar-concept wiki/ "<title>" --aliases "<a,b,c>"` — **新建任何 concept 前强制调用**（Step 5 Part A）。同时扫描 `concepts/` 和 `foundations/`；foundation 命中优先排在最前。
- `python3 tools/research_wiki.py find-similar-claim wiki/ "<title>" --tags "<a,b,c>"` — **新建任何 claim 前强制调用**（Step 4）。规范化 token Jaccard + tag 加权阈值。
- `python3 tools/research_wiki.py add-edge wiki/ --from <id> --to <id> --type <type> --evidence "<text>"` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建压缩上下文
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建知识缺口地图
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/prepare_paper_source.py --raw-root raw --source <local-path> [--title "<recovered-title>"]` — 把本地来源规范化成 canonical ingest path
- `python3 tools/fetch_s2.py paper <arxiv_id>` — 查询 Semantic Scholar
- `python3 tools/fetch_s2.py citations <arxiv_id>` — 查询引用
- `python3 tools/fetch_s2.py references <arxiv_id>` — 查询参考文献
- `python3 tools/fetch_deepxiv.py brief <arxiv_id>` — 获取 TLDR + keywords
- `python3 tools/fetch_deepxiv.py head <arxiv_id>` — 获取论文结构
- `python3 tools/fetch_deepxiv.py social <arxiv_id>` — 获取社交影响力指标

### Shared References
- `.claude/skills/shared-references/citation-verification.md`（Phase 3 创建）

### External APIs
- Semantic Scholar API（via tools/fetch_s2.py）
- DeepXiv API（via tools/fetch_deepxiv.py，可选，不可用时 graceful fallback）
- arXiv（source download）
- ar5iv（HTML source）
