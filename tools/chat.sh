#!/usr/bin/env bash
# Start the EmpiricalWiki chat bridge: a thin local server that lets the rendered
# site (tools/view.sh) talk to your LOCAL Claude Code. It spawns the real `claude`
# binary in headless mode with cwd = this project, using your existing login.
#
# Bound to 127.0.0.1 only. Run it alongside tools/view.sh, then click the
# "✦ Claude" button at the bottom-right of the site.
#
#   tools/chat.sh                 # start on :8788, full permissions (bypassPermissions)
#   EW_PERMISSION=acceptEdits tools/chat.sh   # safer: auto-apply edits, gate other commands
#   EW_CHAT_PORT=9000 tools/chat.sh           # different port

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

command -v node >/dev/null 2>&1 || { echo "✗ 需要 Node.js: https://nodejs.org"; exit 1; }

# Resolve the claude binary (must be the one you log in with).
if [ -z "${CLAUDE_BIN:-}" ]; then
  if command -v claude >/dev/null 2>&1; then
    CLAUDE_BIN="$(command -v claude)"
  else
    echo "✗ 找不到 claude 命令。请确认 Claude Code 已安装并在 PATH 中，或设 CLAUDE_BIN=/path/to/claude"
    exit 1
  fi
fi
export CLAUDE_BIN

echo "✓ claude: $CLAUDE_BIN"

# The bridge uses the official Agent SDK (same core as Claudian). Ensure deps.
BRIDGE="$ROOT/tools/chat-bridge"
if [ ! -d "$BRIDGE/node_modules/@anthropic-ai/claude-agent-sdk" ]; then
  echo "↻ 首次运行：安装 Agent SDK …"
  ( cd "$BRIDGE" && npm install --no-audit --no-fund )
fi
exec node "$BRIDGE/server.mjs"
