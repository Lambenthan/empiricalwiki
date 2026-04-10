---
description: 消化一篇论文，创建 wiki 页面（papers + concepts + people + claims）并建立所有交叉引用与图谱边
argument-hint: <local-path-or-arXiv-URL>
---

# /ingest

> 消化一篇论文，完整纳入 wiki：创建 paper 页面，提取/创建 concepts、people、claims，
> 建立所有双向交叉引用，维护 graph edges，更新 index.md 和 log.md。
> 这是 wiki 最核心的 skill——所有知识通过 ingest 流入。

## Inputs

- `source`：本地 .tex / .pdf 路径，或 arXiv URL（如 `https://arxiv.org/abs/2106.09685`）

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
   - **本地 .pdf**：提取文本（PyMuPDF 或 vision API fallback）
2. 提取元数据：标题、摘要、作者列表（含机构）、发表日期、venue
3. 提取参考文献列表（BibTeX entries 或 reference section）
4. 如有 arXiv ID，保存原始文件到 `raw/papers/`

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

### Step 4: 提取 claims

从论文内容中提取 1-3 个核心 claims（论文的主要贡献断言）。

对每个 claim：
1. 生成 claim slug：`python3 tools/research_wiki.py slug "<claim-title>"`
2. 检查 `wiki/claims/` 是否已有匹配的 claim（语义匹配，非仅 slug 匹配）
3. **若 claim 已存在**：
   - 在 claim 页面的 `evidence` 列表追加新 evidence entry：
     ```yaml
     - source: <paper-slug>
       type: supports    # supports | contradicts
       strength: moderate  # weak | moderate | strong（根据论文证据强度）
       detail: "..."
     ```
   - 根据新 evidence 重新评估 `confidence` 和 `status`
   - 添加 graph edge：
     ```bash
     python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to claims/<claim-slug> --type supports --evidence "<detail>"
     ```
4. **若 claim 不存在**：
   - 按 CLAUDE.md claim 模板创建 `wiki/claims/{claim-slug}.md`
   - status: proposed 或 weakly_supported（取决于论文 evidence 强度）
   - source_papers: [<paper-slug>]
   - evidence 初始化为该论文的 evidence entry
   - 添加 graph edge：同上
5. 在 paper 页面的 `## Related` 中追加 claim 链接：`supports: [[claim-slug]]`

### Step 5: 处理交叉引用

**Part A — Concepts 匹配与创建（含语义去重）：**

1. 读取 `wiki/index.md`，提取所有已有 concepts 的 slug 和 tags
2. 读取每个已有 concept 的 frontmatter，获取 `title` 和 `aliases` 列表
3. **同时扫描 `wiki/foundations/*.md`** 的 `title`、`slug` 和 `aliases`。Foundations 是 `/prefill` 沉淀的背景知识页面 — 对于教科书材料，foundations 优先于新建 concept。
4. 对论文中提到的每个候选概念，**先检查是否与已有概念重复**：
   - **Foundation 命中**（slug、title 或 alias）：候选属于基础背景知识。**不要新建 concept 页面**。直接在 paper 的 `## Related` 追加 `[[foundation-slug]]`。Foundations 是终端节点 — 不要修改 foundation 页面（不写反向链接）。
   - 与已有概念的 slug 精确匹配 → 是同一概念
   - 与已有概念的 title 或 aliases 中任一项语义相同（别名、子类、具体实现）→ 是同一概念
   - 若是已有概念的**变体或子类**（如 "scaled dot-product attention" vs "attention-mechanism"）→ 不创建新页面，追加到已有概念的 `## Variants` 并将候选名加入 `aliases`
   - 只有**确实是全新概念**且未被任何 foundation 覆盖时才创建新页面
4. 对每个匹配的 concept：
   - 若本文是该概念的核心论文：追加 slug 到 concept 的 `key_papers`
   - 若引入新变体：在 concept 的 `## Variants` 追加，将变体名加入 `aliases`
   - 若有矛盾：在 concept 页面记录 contradiction note
   - 反向：在 paper 的 `## Related` 追加 `[[concept-slug]]`
   - 添加 graph edge：
     ```bash
     python3 tools/research_wiki.py add-edge wiki/ --from papers/<paper-slug> --to concepts/<concept-slug> --type supports --evidence "..."
     ```
5. 若论文引入了全新概念（经过上述去重检查确认 wiki 中无匹配）：
   - 按 CLAUDE.md concept 模板创建 `wiki/concepts/{concept-slug}.md`
   - maturity: emerging
   - key_papers: [<paper-slug>]
   - aliases: [常见别名]（在创建时就收集该概念的已知别名）
   - 在 paper 的 `## Related` 追加 `[[concept-slug]]`

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

- **raw/ 只读**：不得修改 `raw/` 下的文件
- **graph/ 仅通过 tools 维护**：不得手动编辑 `graph/` 下的文件，仅通过 `python3 tools/research_wiki.py` 操作
- **双向链接**：写正向链接时同步写反向链接（参照 CLAUDE.md Cross Reference 规则表）
- **tex 优先**：.tex > .pdf > vision API fallback
- **slug 通过工具生成**：必须使用 `python3 tools/research_wiki.py slug` 生成 slug，不得手动拼写
- **index.md 立即更新**：每次 ingest 完成前必须更新 index.md
- **log.md append-only**：通过 `python3 tools/research_wiki.py log` 追加
- **importance 评分标准**：1=niche, 2=useful, 3=field-standard, 4=influential, 5=seminal
- **claim 提取保守**：仅提取论文明确主张的核心贡献，不过度推断
- **重复检查**：创建任何页面前先检查是否已存在

## Error Handling

- **来源解析失败**：tex 失败 → PDF 解析 → vision API → 报告用户手动处理
- **S2 API 不可用**：跳过 S2 相关步骤（citations 回填、importance 使用默认值 3），在报告中注明
- **DeepXiv API 不可用**：跳过 DeepXiv 增强步骤（TLDR、结构验证、社交指标），仅依赖 S2 + 源文件解析
- **slug 冲突**：若生成的 slug 已存在但内容不同，追加数字后缀（如 `attention-mechanism-2`）
- **wiki 目录不存在**：运行 `python3 tools/research_wiki.py init wiki/` 初始化后重试
- **部分步骤失败**：已完成的步骤保留，未完成的步骤在报告中列出，供用户手动补全

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — slug 生成
- `python3 tools/research_wiki.py add-edge wiki/ --from <id> --to <id> --type <type> --evidence "<text>"` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建压缩上下文
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建知识缺口地图
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
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
