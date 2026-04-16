#!/usr/bin/env bash
# ============================================================================
# ΩmegaWiki — One-Click Setup
# ============================================================================
# Usage:
#   chmod +x setup.sh && ./setup.sh            # English (default)
#   chmod +x setup.sh && ./setup.sh --lang zh  # Chinese / 中文
#
# What it does:
#   1. Checks prerequisites (Python, pip, Claude Code)
#   2. Creates virtual environment and installs dependencies
#   3. Copies configuration templates
#   4. Verifies the installation
#
# API key configuration (Semantic Scholar, DeepXiv, Review LLM) is handled
# interactively by Claude Code — run /setup after starting Claude Code.
# ============================================================================

set -e

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $1"; }

# Cross-platform sed -i (macOS BSD sed vs GNU sed)
_sed_i() {
  if [[ "$OSTYPE" == darwin* ]]; then
    sed -i '' "$@"
  else
    sed -i "$@"
  fi
}

# ── Language selection ──────────────────────────────────────────────
LANG_CODE="en"
_ARGS=("$@")
for i in "${!_ARGS[@]}"; do
  case "${_ARGS[$i]}" in
    --lang=*) LANG_CODE="${_ARGS[$i]#*=}" ;;
    --lang)   LANG_CODE="${_ARGS[$((i+1))]}" ;;
  esac
done
[[ "$LANG_CODE" == "en" || "$LANG_CODE" == "zh" ]] || { fail "Unknown lang: $LANG_CODE (use 'en' or 'zh')"; exit 1; }
I18N_DIR="$(cd "$(dirname "$0")" && pwd)/i18n/$LANG_CODE"
[ -d "$I18N_DIR" ] || { fail "i18n/$LANG_CODE not found — run from the project root"; exit 1; }

echo ""
echo "============================================"
echo "  ΩmegaWiki — Setup"
echo "============================================"
echo ""

# ── Step 1: Check prerequisites ─────────────────────────────────────────

info "Checking prerequisites..."

# Python
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 9 ]; then
        ok "Python $PY_VERSION"
    else
        fail "Python >= 3.9 required, found $PY_VERSION"
        exit 1
    fi
else
    fail "Python3 not found. Install Python 3.9+ first."
    exit 1
fi

# pip
if python3 -m pip --version &>/dev/null; then
    ok "pip available"
else
    fail "pip not found. Install with: python3 -m ensurepip"
    exit 1
fi

# Claude Code
if command -v claude &>/dev/null; then
    ok "Claude Code installed"
else
    warn "Claude Code not found."
    echo ""
    echo "  Claude Code is required to use ΩmegaWiki skills."
    echo "  Install with:"
    echo "    npm install -g @anthropic-ai/claude-code"
    echo ""
    read -p "  Continue setup without Claude Code? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  Install Claude Code first, then re-run setup.sh"
        exit 1
    fi
fi

# ── Step 2: Python environment + dependencies ───────────────────────────

echo ""
info "Setting up Python environment..."

# Detect if user is already in a virtual environment (venv or conda)
if [ -n "$VIRTUAL_ENV" ]; then
    ok "Using active venv: $VIRTUAL_ENV"
    USING_VENV="$VIRTUAL_ENV"
elif [ -n "$CONDA_DEFAULT_ENV" ] && [ "$CONDA_DEFAULT_ENV" != "base" ]; then
    ok "Using active conda env: $CONDA_DEFAULT_ENV"
    USING_VENV="conda:$CONDA_DEFAULT_ENV"
else
    # No active env — create .venv
    if [ -d ".venv" ]; then
        warn ".venv already exists, using it"
    else
        python3 -m venv .venv
        ok "Created .venv"
    fi
    source .venv/bin/activate
    ok "Activated .venv"
    USING_VENV=".venv"
fi

info "Installing dependencies..."
pip install -r requirements.txt -q
ok "Dependencies installed"

# ── Step 3: Configuration files ─────────────────────────────────────────

echo ""
info "Setting up configuration..."

# .env
if [ -f ".env" ]; then
    warn ".env already exists, not overwriting"
else
    cp .env.example .env
    ok "Created .env from template"
fi

# Claude Code settings
mkdir -p .claude
if [ -f ".claude/settings.local.json" ]; then
    warn ".claude/settings.local.json already exists, not overwriting"
else
    cp config/settings.local.json.example .claude/settings.local.json
    ok "Created .claude/settings.local.json"
fi

# ── Step 3b: Activate language files ───────────────────────────────
echo ""
info "Activating language: $LANG_CODE"
cp "$I18N_DIR/CLAUDE.md" CLAUDE.md
for src in "$I18N_DIR/skills"/*/SKILL.md; do
    skill_dir=$(dirname "$src")
    name=$(basename "$skill_dir")
    mkdir -p ".claude/skills/$name"
    cp "$src" ".claude/skills/$name/SKILL.md"
    # Copy any sibling resource files (e.g. prefill/foundations-catalog.yaml)
    for extra in "$skill_dir"/*; do
        [ -f "$extra" ] || continue
        case "$(basename "$extra")" in
            SKILL.md) ;;
            *) cp "$extra" ".claude/skills/$name/" ;;
        esac
    done
done
mkdir -p ".claude/skills/shared-references"
cp "$I18N_DIR/shared-references"/*.md ".claude/skills/shared-references/"
echo "$LANG_CODE" > .claude/.current-lang
ok "Language files activated ($LANG_CODE)"

# ── Step 4: Verify installation ─────────────────────────────────────────

echo ""
info "Verifying installation..."

ERRORS=0

# Check tools import (run from tools/ so _env.py resolves correctly)
for tool_check in \
    "fetch_arxiv:from fetch_arxiv import fetch_recent" \
    "fetch_s2:from fetch_s2 import search" \
    "fetch_deepxiv:from fetch_deepxiv import search" \
    "research_wiki:from research_wiki import slugify" \
    "lint:from lint import check_missing_fields"; do
    tool_name="${tool_check%%:*}"
    tool_import="${tool_check#*:}"
    if (cd tools && python3 -c "$tool_import") 2>/dev/null; then
        ok "tools/${tool_name}.py"
    else
        fail "tools/${tool_name}.py import error"
        ERRORS=$((ERRORS+1))
    fi
done

# ── Done ────────────────────────────────────────────────────────────────

echo ""
echo "============================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "  ${GREEN}Setup complete!${NC}"
else
    echo -e "  ${YELLOW}Setup complete with $ERRORS warning(s)${NC}"
fi
echo "============================================"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Authenticate Claude Code (if not already):"
echo "     claude login"
echo ""
echo "  2. Start Claude Code:"
echo "     claude"
echo ""
echo "  3. Complete API key configuration (guided):"
echo "     /setup"
echo "     Claude Code will walk you through Semantic Scholar,"
echo "     DeepXiv, and Review LLM — skip any you don't have yet."
echo ""
echo "  4. Then initialize your wiki:"
echo "     /init [your-research-topic]"
echo ""
echo "  For more, see README.md"
echo ""
