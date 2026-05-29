#!/usr/bin/env bash
# View the wiki as a polished local website (graph + backlinks + search) via Quartz.
#
# First run clones Quartz into site/.quartz/ (gitignored) and installs its deps.
# Every run re-syncs wiki/*.md into Quartz's content/ and rebuilds, so the site
# always reflects the current wiki. The wiki is read-only here — nothing under
# wiki/ is modified.
#
# Usage:
#   tools/view.sh            # build + serve at http://localhost:8080
#   tools/view.sh --build    # build only (output in site/.quartz/public)
#   tools/view.sh --update    # force re-pull Quartz, then build + serve
#
# Requires: Node.js (https://nodejs.org) and git.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QZ="$ROOT/site/.quartz"
CONTENT="$QZ/content"
QUARTZ_REPO="https://github.com/jackyzha0/quartz.git"
# Pin to the last v4 release: the stable, documented clone→npm i→build flow.
# (v5 changed the architecture and needs a different scaffold step.)
QUARTZ_REF="v4.5.2"
SITE_TITLE="EmpiricalWiki — 实证 × 理论研究 wiki"

mode="serve"
case "${1:-}" in
  --build) mode="build" ;;
  --update) mode="update" ;;
esac

command -v node >/dev/null 2>&1 || { echo "✗ 需要先安装 Node.js: https://nodejs.org"; exit 1; }
command -v git  >/dev/null 2>&1 || { echo "✗ 需要 git"; exit 1; }

if [ "$mode" = "update" ] && [ -d "$QZ" ]; then
  echo "↻ 更新 Quartz ..."
  git -C "$QZ" pull --ff-only || true
  ( cd "$QZ" && npm i )
fi

if [ ! -d "$QZ" ]; then
  echo "⤓ 首次运行:克隆 Quartz 到 site/.quartz/ (仅本地,不进 git) ..."
  mkdir -p "$ROOT/site"
  git clone --depth 1 --branch "$QUARTZ_REF" "$QUARTZ_REPO" "$QZ"
  echo "⤓ 安装依赖 (npm i,首次较慢) ..."
  ( cd "$QZ" && npm i )
fi

# Targeted, idempotent patches to Quartz's own default config (schema-safe:
# each regex only matches the pristine default, so re-runs are no-ops).
if [ -f "$QZ/quartz.config.ts" ]; then
  # Site title.
  perl -0pi -e "s/pageTitle:\s*\"[^\"]*\"/pageTitle: \"$SITE_TITLE\"/" "$QZ/quartz.config.ts" || true
  # Drop git from the date priority: wiki content is gitignored, so the git step
  # only emits "untracked, dates inaccurate" warnings. Fall back to filesystem.
  perl -0pi -e 's/priority:\s*\["frontmatter",\s*"git",\s*"filesystem"\]/priority: ["frontmatter", "filesystem"]/' "$QZ/quartz.config.ts" || true
fi
if [ -f "$QZ/quartz.layout.ts" ]; then
  # Local graph depth 2 so a page shows its 2-hop neighbourhood — e.g. a theory
  # paper → propositions → hypotheses → empirical papers (the theory↔empirics bridge).
  perl -0pi -e 's/Component\.Graph\(\)/Component.Graph({ localGraph: { depth: 2 } })/' "$QZ/quartz.layout.ts" || true
fi

# Re-sync content: copy wiki/*.md preserving structure, excluding derived/config dirs.
echo "↻ 同步 wiki/ → Quartz content/ ..."
rm -rf "$CONTENT"
mkdir -p "$CONTENT"
( cd "$ROOT/wiki" && find . -name '*.md' \
    -not -path './graph/*' \
    -not -path './outputs/*' \
    -not -path './.obsidian/*' \
    -not -path './.trash/*' \
    -print0 \
  | while IFS= read -r -d '' f; do
      mkdir -p "$CONTENT/$(dirname "$f")"
      cp "$f" "$CONTENT/$f"
    done )

n=$(find "$CONTENT" -name '*.md' | wc -l | tr -d ' ')
echo "✓ 已同步 $n 个页面"

# Friendlier homepage: prepend a short intro above the auto-generated catalog.
# Operates on the copied content only (source wiki/index.md untouched). Also
# gives the home page a real title instead of falling back to "index".
if [ -f "$CONTENT/index.md" ]; then
  tmp="$CONTENT/.index.intro.tmp"
  cat > "$tmp" <<'INTRO'
---
title: EmpiricalWiki
---

# EmpiricalWiki — 实证 × 理论研究知识库

左侧按类型浏览，顶部全文搜索，右下角图谱查看「理论 ↔ 实证」的连接。

- 论文 `papers/` · 理论假设 `assumptions/` · 命题/定理 `propositions/`
- 变量 `variables/` · 数据 `datasets/` · 模型 `models/` · 机制 `mechanisms/` · 识别 `identification/` · 稳健性 `robustness/` · 异质性 `heterogeneity/`
- 提示：打开一篇论文，顺着 `[[链接]]` 与右侧反向链接，即可在理论与实证之间穿梭。

---

INTRO
  cat "$CONTENT/index.md" >> "$tmp"
  mv "$tmp" "$CONTENT/index.md"
fi

cd "$QZ"
if [ "$mode" = "build" ]; then
  npx quartz build
  echo "✓ 站点已构建到 site/.quartz/public/"
else
  echo "▶ 启动本地预览 → http://localhost:8080  (Ctrl-C 退出)"
  npx quartz build --serve
fi
