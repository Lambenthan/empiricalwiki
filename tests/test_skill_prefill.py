"""Tests for the /prefill skill — bilingual SKILL.md and seed catalog."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EN_SKILL = PROJECT_ROOT / "i18n" / "en" / "skills" / "prefill" / "SKILL.md"
ZH_SKILL = PROJECT_ROOT / "i18n" / "zh" / "skills" / "prefill" / "SKILL.md"
EN_CATALOG = PROJECT_ROOT / "i18n" / "en" / "skills" / "prefill" / "foundations-catalog.yaml"
ZH_CATALOG = PROJECT_ROOT / "i18n" / "zh" / "skills" / "prefill" / "foundations-catalog.yaml"
ACTIVE_SKILL = PROJECT_ROOT / ".claude" / "skills" / "prefill" / "SKILL.md"
ACTIVE_CATALOG = PROJECT_ROOT / ".claude" / "skills" / "prefill" / "foundations-catalog.yaml"


def test_en_skill_exists():
    assert EN_SKILL.exists()


def test_zh_skill_exists():
    assert ZH_SKILL.exists()


def test_en_catalog_exists():
    assert EN_CATALOG.exists()


def test_zh_catalog_exists():
    assert ZH_CATALOG.exists()


REQUIRED_SECTIONS = [
    "## Inputs",
    "## Outputs",
    "## Wiki Interaction",
    "## Workflow",
    "## Constraints",
    "## Error Handling",
    "## Dependencies",
]


@pytest.mark.parametrize("section", REQUIRED_SECTIONS)
def test_en_has_required_sections(section):
    assert section in EN_SKILL.read_text(encoding="utf-8")


@pytest.mark.parametrize("section", REQUIRED_SECTIONS)
def test_zh_has_required_sections(section):
    assert section in ZH_SKILL.read_text(encoding="utf-8")


def test_en_describes_foundations_terminal():
    txt = EN_SKILL.read_text(encoding="utf-8")
    # The single-direction invariant must be stated explicitly
    assert "terminal" in txt.lower() or "single-direction" in txt.lower()
    # Must mention that foundations write no reverse link
    assert "no reverse link" in txt.lower() or "no outbound" in txt.lower() or "no outward" in txt.lower()


def test_zh_describes_foundations_terminal():
    txt = ZH_SKILL.read_text(encoding="utf-8")
    assert "终端" in txt or "单向" in txt
    assert "不写反向" in txt or "无外向" in txt or "禁止" in txt


def test_en_calls_fetch_wikipedia():
    txt = EN_SKILL.read_text(encoding="utf-8")
    assert "fetch_wikipedia.py" in txt


def test_zh_calls_fetch_wikipedia():
    txt = ZH_SKILL.read_text(encoding="utf-8")
    assert "fetch_wikipedia.py" in txt


def test_en_calls_research_wiki_for_index_and_log():
    txt = EN_SKILL.read_text(encoding="utf-8")
    assert "rebuild-index" in txt
    assert "research_wiki.py log" in txt


def test_skill_idempotent_constraint_documented():
    en = EN_SKILL.read_text(encoding="utf-8")
    zh = ZH_SKILL.read_text(encoding="utf-8")
    assert "idempotent" in en.lower() or "never overwrite" in en.lower()
    assert "幂等" in zh or "从不覆盖" in zh


def test_active_skill_present_after_setup():
    lang_file = PROJECT_ROOT / ".claude" / ".current-lang"
    if not lang_file.exists():
        pytest.skip("setup.sh not run yet")
    assert ACTIVE_SKILL.exists()
    assert ACTIVE_CATALOG.exists(), (
        "foundations-catalog.yaml must be copied alongside SKILL.md by setup.sh"
    )


def test_en_claude_md_lists_prefill():
    claude_md = PROJECT_ROOT / "i18n" / "en" / "CLAUDE.md"
    assert "`/prefill`" in claude_md.read_text(encoding="utf-8")


def test_zh_claude_md_lists_prefill():
    claude_md = PROJECT_ROOT / "i18n" / "zh" / "CLAUDE.md"
    assert "`/prefill`" in claude_md.read_text(encoding="utf-8")
