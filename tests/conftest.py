"""Language-aware pytest fixtures for skill tests.

Reads .claude/.current-lang (written by setup.sh --lang <code>).
Defaults to 'en' when the file is absent (e.g. in CI, or before setup.sh is run).
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LANG_FILE = PROJECT_ROOT / ".claude" / ".current-lang"


def _current_lang() -> str:
    if LANG_FILE.exists():
        lang = LANG_FILE.read_text().strip()
        if lang in ("en", "zh"):
            return lang
    # Auto-detect from installed skill files (used when .current-lang is absent)
    import re as _re
    probe = PROJECT_ROOT / ".claude" / "skills" / "ingest" / "SKILL.md"
    if probe.exists() and _re.search(r"[\u4e00-\u9fff]", probe.read_text(encoding="utf-8")):
        return "zh"
    return "en"


@pytest.fixture(scope="session")
def current_lang():
    return _current_lang()


# ── /ideate 5-phase pipeline keywords ──────────────────────────────────────

IDEATE_PHASE_KEYWORDS = {
    "en": [
        ("Phase 1", "Landscape"),
        ("Phase 2", "Brainstorm"),
        ("Phase 3", "Filter"),
        ("Phase 4", "Validation"),
        ("Phase 5", "Write"),
    ],
    "zh": [
        ("Phase 1", "景观"),
        ("Phase 2", "脑暴"),
        ("Phase 3", "筛选"),
        ("Phase 4", "验证"),
        ("Phase 5", "写入"),
    ],
}


@pytest.fixture(scope="session")
def ideate_phase_keywords(current_lang):
    return IDEATE_PHASE_KEYWORDS[current_lang]


# ── /ingest workflow step keywords ─────────────────────────────────────────

INGEST_WORKFLOW_STEPS = {
    "en": [
        "Resolve the source",
        "enrichment",
        "paper page",
        "claims",
        "paper-to-paper",
        "Topics",
        "Log",
        "Report",
    ],
    "zh": [
        "解析来源",
        "enrichment",
        "paper 页面",
        "claims",
        "paper-to-paper",
        "topic",
        "日志",
        "汇报",
    ],
}


@pytest.fixture(scope="session")
def ingest_workflow_steps(current_lang):
    return INGEST_WORKFLOW_STEPS[current_lang]


# ── /review workflow step keywords ─────────────────────────────────────────

REVIEW_WORKFLOW_KEYWORDS = {
    "en": ["context", "Review LLM", "multi-round", "Structured Output"],
    "zh": ["上下文", "Review LLM", "多轮", "结构化输出"],
}


@pytest.fixture(scope="session")
def review_workflow_keywords(current_lang):
    return REVIEW_WORKFLOW_KEYWORDS[current_lang]


# ── CLAUDE.md section markers ───────────────────────────────────────────────

CLAUDE_MD_MARKERS = {
    "en": {
        "entity_section": "## 9 Page Types",
        "graph_section": "graph/ (auto-generated",
        "graph_auto_generated": "auto-generated",
        "graph_no_edit": "do not edit",
        "index_format_split": "## index.md format",
        "index_format_assert": "index.md format",
        "constraints": "## Constraints",
        "body_label": "Body sections:",
    },
    "zh": {
        "entity_section": "9 类页面",
        "graph_section": "graph/（自动生成",
        "graph_auto_generated": "自动生成",
        "graph_no_edit": "勿手动编辑",
        "index_format_split": "## index.md 格式",
        "index_format_assert": "index.md 格式",
        "constraints": "约束",
        "body_label": "正文：",
    },
}


@pytest.fixture(scope="session")
def claude_md_markers(current_lang):
    return CLAUDE_MD_MARKERS[current_lang]
