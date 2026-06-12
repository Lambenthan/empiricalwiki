#!/usr/bin/env bash
# View the wiki as a polished local website (graph + backlinks + search) via Quartz.
#
# First run clones Quartz into site/.quartz/ (gitignored) and installs its deps.
# Every run re-syncs wiki/*.md into Quartz's content/ and rebuilds, so the site
# always reflects the current wiki. The wiki is read-only here — nothing under
# wiki/ is modified.
#
# Usage:
#   tools/view.sh            # build + serve at http://localhost:8080 (+ Claude 对话挂件)
#   tools/view.sh --build    # build only (output in site/.quartz/public)
#   tools/view.sh --update   # force re-pull Quartz, then build + serve
#   tools/view.sh --no-chat  # serve without starting the Claude chat bridge
#
# Requires: Node.js (https://nodejs.org) and git. The chat bridge additionally
# requires a logged-in local Claude Code (`claude` on PATH) — without it the
# site still serves, just read-only.

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
nochat=0
for arg in "$@"; do
  case "$arg" in
    --build) mode="build" ;;
    --update) mode="update" ;;
    --no-chat) nochat=1 ;;
  esac
done

command -v node >/dev/null 2>&1 || { echo "✗ 需要先安装 Node.js: https://nodejs.org"; exit 1; }
command -v git  >/dev/null 2>&1 || { echo "✗ 需要 git"; exit 1; }
# Quartz v4.5.2 requires node >= 22 (its package.json engines field).
NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]')
if [ "$NODE_MAJOR" -lt 22 ]; then
  echo "✗ Quartz $QUARTZ_REF 需要 Node.js >= 22,当前为 $(node --version)"
  exit 1
fi

if [ "$mode" = "update" ] && [ -d "$QZ" ]; then
  # The clone is a shallow checkout of a tag (detached HEAD) — `git pull`
  # can never advance it. Updating means re-cloning the pinned ref.
  echo "↻ 更新 Quartz(重新克隆 $QUARTZ_REF)..."
  rm -rf "$QZ"
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
  # Graph: local graph 2-hop (shows a theory paper → propositions → hypotheses →
  # empirical papers, i.e. the bridge); global graph de-hairballed by dropping
  # tag hub-nodes and spreading nodes apart (higher repel, longer links).
  perl -0pi -e 's/Component\.Graph\(\)/Component.Graph({ localGraph: { depth: 2, showTags: false }, globalGraph: { showTags: false, repelForce: 0.8, linkDistance: 35, scale: 1.05 } })/' "$QZ/quartz.layout.ts" || true
fi
# --- Claude 对话挂件 -----------------------------------------------------------
# Right-sidebar panel that talks to your LOCAL Claude Code through
# tools/chat-bridge (Agent SDK, same core design as the Claudian Obsidian
# plugin). Source of truth is tools/quartz-ext/ (tracked); installed into the
# gitignored Quartz clone on every run so it survives re-clone / rebuild.
EXT="$ROOT/tools/quartz-ext"
if [ -d "$EXT" ] && [ -d "$QZ/quartz/components" ]; then
  cp "$EXT/EwChat.tsx"        "$QZ/quartz/components/EwChat.tsx"
  cp "$EXT/ewchat.inline.ts"  "$QZ/quartz/components/scripts/ewchat.inline.ts"
  cp "$EXT/ewchat.scss"       "$QZ/quartz/components/styles/ewchat.scss"
  # Register the component in components/index.ts (idempotent).
  IDX="$QZ/quartz/components/index.ts"
  if [ -f "$IDX" ] && ! grep -q "EwChat" "$IDX"; then
    perl -0pi -e 's{import Comments from "\./Comments"}{import Comments from "./Comments"\nimport EwChat from "./EwChat"}' "$IDX"
    perl -0pi -e 's{\n  Comments,\n}{\n  Comments,\n  EwChat,\n}' "$IDX"
  fi
  # Mount as the FIRST right-sidebar item: it switches the rail between the
  # page views (Graph / ToC / Backlinks) and the Claude chat.
  if ! grep -q "Component.EwChat()" "$QZ/quartz.layout.ts"; then
    perl -0pi -e 's/(right: \[\s*)(Component\.Graph)/${1}Component.EwChat(),\n    $2/' "$QZ/quartz.layout.ts" || true
    perl -0pi -e 's/right: \[\]/right: [Component.EwChat()]/g' "$QZ/quartz.layout.ts" || true
  fi
  echo "✓ Claude 对话挂件已安装"
fi

# Quartz traps the mouse wheel over the left sidebar (explorer sets
# overscroll-behavior: contain). Override it so the page scrolls when the
# explorer is at its boundary. Appended once (marker-guarded), compiled by build.
CSS_FILE="$QZ/quartz/styles/custom.scss"
if [ -f "$CSS_FILE" ] && ! grep -q 'EW-sidebar-scroll' "$CSS_FILE"; then
  printf '\n/* EW-sidebar-scroll: stop the explorer from trapping the page scroll */\n.explorer-content, .explorer-content ul { overscroll-behavior: auto; }\n' >> "$CSS_FILE"
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
  # --- Claude chat bridge (auto-start) ------------------------------------
  # Starts alongside the site so the chat panel works out of the box. Needs a
  # logged-in local `claude`; otherwise the site runs read-only.
  BRIDGE_PID=""
  if [ "$nochat" -eq 0 ] && command -v claude >/dev/null 2>&1; then
    BRIDGE="$ROOT/tools/chat-bridge"
    if [ ! -d "$BRIDGE/node_modules/@anthropic-ai/claude-agent-sdk" ]; then
      echo "↻ 首次运行:安装对话桥接依赖(Agent SDK)..."
      ( cd "$BRIDGE" && npm install --no-audit --no-fund )
    fi
    CLAUDE_BIN="$(command -v claude)" node "$BRIDGE/server.mjs" &
    BRIDGE_PID=$!
    trap '[ -n "$BRIDGE_PID" ] && kill "$BRIDGE_PID" 2>/dev/null || true' EXIT INT TERM
    echo "✓ Claude 对话桥接已启动 (127.0.0.1:8788),站点右栏「Claude」页签即可对话"
  elif [ "$nochat" -eq 0 ]; then
    echo "⚠ 未找到 claude 命令,跳过对话挂件后端(站点只读)。安装 Claude Code 后重跑即可启用。"
  fi
  echo "▶ 启动本地预览 → http://localhost:8080  (Ctrl-C 退出)"
  npx quartz build --serve
fi
