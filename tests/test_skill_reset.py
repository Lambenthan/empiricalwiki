"""Tests for the /reset skill — bilingual SKILL.md."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EN_SKILL = PROJECT_ROOT / "i18n" / "en" / "skills" / "reset" / "SKILL.md"
ZH_SKILL = PROJECT_ROOT / "i18n" / "zh" / "skills" / "reset" / "SKILL.md"
ACTIVE_SKILL = PROJECT_ROOT / ".claude" / "skills" / "reset" / "SKILL.md"


def test_en_skill_exists():
    assert EN_SKILL.exists()


def test_zh_skill_exists():
    assert ZH_SKILL.exists()


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
def test_en_required_sections(section):
    assert section in EN_SKILL.read_text(encoding="utf-8")


@pytest.mark.parametrize("section", REQUIRED_SECTIONS)
def test_zh_required_sections(section):
    assert section in ZH_SKILL.read_text(encoding="utf-8")


SCOPES = ["wiki", "raw", "log", "checkpoints", "all"]


@pytest.mark.parametrize("scope", SCOPES)
def test_en_documents_scope(scope):
    assert scope in EN_SKILL.read_text(encoding="utf-8")


@pytest.mark.parametrize("scope", SCOPES)
def test_zh_documents_scope(scope):
    assert scope in ZH_SKILL.read_text(encoding="utf-8")


def test_en_requires_confirmation():
    txt = EN_SKILL.read_text(encoding="utf-8")
    assert "confirm" in txt.lower() or "[y/N]" in txt


def test_zh_requires_confirmation():
    txt = ZH_SKILL.read_text(encoding="utf-8")
    assert "确认" in txt or "[y/N]" in txt


def test_en_calls_reset_wiki_tool():
    txt = EN_SKILL.read_text(encoding="utf-8")
    assert "reset_wiki.py" in txt


def test_en_mentions_raw_discovered():
    txt = EN_SKILL.read_text(encoding="utf-8")
    assert "raw/discovered/" in txt


def test_en_mentions_raw_tmp():
    txt = EN_SKILL.read_text(encoding="utf-8")
    assert "raw/tmp/" in txt


def test_zh_calls_reset_wiki_tool():
    txt = ZH_SKILL.read_text(encoding="utf-8")
    assert "reset_wiki.py" in txt


def test_zh_mentions_raw_discovered():
    txt = ZH_SKILL.read_text(encoding="utf-8")
    assert "raw/discovered/" in txt


def test_zh_mentions_raw_tmp():
    txt = ZH_SKILL.read_text(encoding="utf-8")
    assert "raw/tmp/" in txt


def test_en_protects_claude_md_and_skills():
    txt = EN_SKILL.read_text(encoding="utf-8").lower()
    assert "claude.md" in txt
    assert ".claude" in txt or "skills" in txt


def test_zh_protects_claude_md_and_skills():
    txt = ZH_SKILL.read_text(encoding="utf-8")
    assert "CLAUDE.md" in txt
    assert ".claude" in txt or "skill" in txt.lower()


def test_active_skill_present_after_setup():
    lang_file = PROJECT_ROOT / ".claude" / ".current-lang"
    if not lang_file.exists():
        pytest.skip("setup.sh not run yet")
    assert ACTIVE_SKILL.exists()


def test_en_claude_md_lists_reset():
    claude_md = PROJECT_ROOT / "i18n" / "en" / "CLAUDE.md"
    assert "`/reset`" in claude_md.read_text(encoding="utf-8")


def test_zh_claude_md_lists_reset():
    claude_md = PROJECT_ROOT / "i18n" / "zh" / "CLAUDE.md"
    assert "`/reset`" in claude_md.read_text(encoding="utf-8")
