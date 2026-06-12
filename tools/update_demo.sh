#!/usr/bin/env bash
# Update the demo branch from the current working tree WITHOUT switching branches.
#
# Why this exists: wiki content is gitignored on main (private-by-default) but
# tracked on demo. If you `git switch demo` in your working repo, git will
# DELETE your working wiki when you switch back (tracked-on-demo, absent-on-main).
# This script builds the demo commit with plumbing commands instead — your
# checkout never changes. Never `git switch demo` in your working repo.
#
# Usage: tools/update_demo.sh ["commit message"]
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

MSG="${1:-demo: 同步工作区 wiki（$(date +%F)）}"

TMP_INDEX=$(mktemp)
trap 'rm -f "$TMP_INDEX"' EXIT
export GIT_INDEX_FILE="$TMP_INDEX"

# Start from main's tree (README, tools, presets …), overlay the full wiki.
# Editor/plugin state stays out: .obsidian holds plugin configs that can
# contain API keys (GitHub secret scanning once blocked exactly this).
git read-tree HEAD
git add -f -- wiki/ \
  ':!wiki/.obsidian*' ':!wiki/.trash' ':!wiki/.claude'
TREE=$(git write-tree)
unset GIT_INDEX_FILE

PARENT=$(git rev-parse --verify --quiet refs/heads/demo || true)
if [ -n "$PARENT" ]; then
  # Skip empty updates
  if [ "$(git rev-parse "$PARENT^{tree}")" = "$TREE" ]; then
    echo "demo is already up to date."
    exit 0
  fi
  COMMIT=$(git commit-tree "$TREE" -p "$PARENT" -m "$MSG")
else
  COMMIT=$(git commit-tree "$TREE" -m "$MSG")
fi

git update-ref refs/heads/demo "$COMMIT"
echo "demo -> $(git rev-parse --short "$COMMIT")  (working tree untouched)"
echo "push with: git push origin demo"
