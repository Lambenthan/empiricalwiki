"""Tests for the /setup skill.

Validates:
- SKILL.md exists in both i18n/en and i18n/zh
- Required SKILL.md sections are present (language-agnostic)
- Referenced files exist (config/setup-guide.md, .env.example)
- setup-guide.md covers all four configurable keys
- setup scripts keep dependency installation deterministic
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EN_SKILL = PROJECT_ROOT / "i18n" / "en" / "skills" / "setup" / "SKILL.md"
ZH_SKILL = PROJECT_ROOT / "i18n" / "zh" / "skills" / "setup" / "SKILL.md"
ACTIVE_SKILL = PROJECT_ROOT / ".claude" / "skills" / "setup" / "SKILL.md"
SETUP_GUIDE = PROJECT_ROOT / "config" / "setup-guide.md"
ENV_EXAMPLE = PROJECT_ROOT / "config" / ".env.example"
SETUP_SH = PROJECT_ROOT / "setup.sh"
SETUP_PS1 = PROJECT_ROOT / "setup.ps1"
README_MD = PROJECT_ROOT / "README.md"


# ── File existence ─────────────────────────────────────────────────────────

def test_en_skill_exists():
    assert EN_SKILL.exists(), f"/setup SKILL.md (en) not found at {EN_SKILL}"


def test_zh_skill_exists():
    assert ZH_SKILL.exists(), f"/setup SKILL.md (zh) not found at {ZH_SKILL}"


def test_setup_guide_exists():
    assert SETUP_GUIDE.exists(), f"config/setup-guide.md not found at {SETUP_GUIDE}"


def test_env_example_exists():
    assert ENV_EXAMPLE.exists(), f"config/.env.example not found at {ENV_EXAMPLE}"


def test_setup_ps1_exists():
    assert SETUP_PS1.exists(), f"setup.ps1 not found at {SETUP_PS1}"


# ── SKILL.md required sections ─────────────────────────────────────────────

REQUIRED_SECTIONS_EN = [
    "## Inputs",
    "## Outputs",
    "## Wiki Interaction",
    "## Workflow",
    "## Constraints",
    "## Error Handling",
    "## Dependencies",
]

REQUIRED_SECTIONS_ZH = [
    "## Inputs",
    "## Outputs",
    "## Wiki Interaction",
    "## Workflow",
    "## Constraints",
    "## Error Handling",
    "## Dependencies",
]


@pytest.mark.parametrize("section", REQUIRED_SECTIONS_EN)
def test_en_skill_has_required_section(section):
    content = EN_SKILL.read_text(encoding="utf-8")
    assert section in content, f"EN SKILL.md missing section: {section}"


@pytest.mark.parametrize("section", REQUIRED_SECTIONS_ZH)
def test_zh_skill_has_required_section(section):
    content = ZH_SKILL.read_text(encoding="utf-8")
    assert section in content, f"ZH SKILL.md missing section: {section}"


# ── SKILL.md frontmatter ───────────────────────────────────────────────────

def test_en_skill_has_description_frontmatter():
    content = EN_SKILL.read_text(encoding="utf-8")
    assert content.startswith("---"), "EN SKILL.md must start with YAML frontmatter"
    assert "description:" in content, "EN SKILL.md frontmatter must have description field"


def test_zh_skill_has_description_frontmatter():
    content = ZH_SKILL.read_text(encoding="utf-8")
    assert content.startswith("---"), "ZH SKILL.md must start with YAML frontmatter"
    assert "description:" in content, "ZH SKILL.md frontmatter must have description field"


# ── Workflow coverage — four keys must be mentioned ───────────────────────

EXPECTED_KEYS_EN = [
    "SEMANTIC_SCHOLAR_API_KEY",
    "DEEPXIV_TOKEN",
    "LLM_API_KEY",
    "LLM_BASE_URL",
    "LLM_MODEL",
]

EXPECTED_KEYS_ZH = [
    "SEMANTIC_SCHOLAR_API_KEY",
    "DEEPXIV_TOKEN",
    "LLM_API_KEY",
]


@pytest.mark.parametrize("key", EXPECTED_KEYS_EN)
def test_en_skill_covers_env_key(key):
    content = EN_SKILL.read_text(encoding="utf-8")
    assert key in content, f"EN SKILL.md does not mention env key: {key}"


@pytest.mark.parametrize("key", EXPECTED_KEYS_ZH)
def test_zh_skill_covers_env_key(key):
    content = ZH_SKILL.read_text(encoding="utf-8")
    assert key in content, f"ZH SKILL.md does not mention env key: {key}"


# ── DeepXiv auto-registration in skills ───────────────────────────────────

def test_en_skill_has_deepxiv_autoregister():
    content = EN_SKILL.read_text(encoding="utf-8")
    assert "data.rag.ac.cn" in content or "auto-register" in content.lower(), \
        "EN SKILL.md should describe DeepXiv auto-registration"


def test_zh_skill_has_deepxiv_autoregister():
    content = ZH_SKILL.read_text(encoding="utf-8")
    assert "data.rag.ac.cn" in content or "自动注册" in content, \
        "ZH SKILL.md should describe DeepXiv auto-registration"


# ── Skills must not require wiki ──────────────────────────────────────────

def test_en_skill_wiki_interaction_is_none():
    content = EN_SKILL.read_text(encoding="utf-8")
    # Wiki Interaction section should say "None" for both reads and writes
    assert "None" in content or "none" in content.lower(), \
        "EN /setup skill should not require wiki access"


def test_zh_skill_wiki_interaction_is_none():
    content = ZH_SKILL.read_text(encoding="utf-8")
    assert "无" in content or "None" in content, \
        "ZH /setup skill should not require wiki access"


# ── setup-guide.md covers all keys ────────────────────────────────────────

GUIDE_EXPECTED_KEYS = [
    "SEMANTIC_SCHOLAR_API_KEY",
    "DEEPXIV_TOKEN",
    "LLM_API_KEY",
    "LLM_BASE_URL",
    "LLM_MODEL",
    "ARXIV_CATEGORIES",
]


@pytest.mark.parametrize("key", GUIDE_EXPECTED_KEYS)
def test_setup_guide_covers_key(key):
    content = SETUP_GUIDE.read_text(encoding="utf-8")
    assert key in content, f"config/setup-guide.md does not mention: {key}"


def test_setup_guide_has_verification_section(key="Configuration Verification"):
    content = SETUP_GUIDE.read_text(encoding="utf-8")
    assert "Verification" in content or "verification" in content, \
        "config/setup-guide.md should have a verification section"


# ── setup.sh no longer has interactive API key prompts ────────────────────

def test_setup_sh_no_s2_interactive_prompt():
    content = SETUP_SH.read_text(encoding="utf-8")
    # The old prompt was: read -p "  Enter S2 API key
    assert 'read -p "  Enter S2 API key' not in content, \
        "setup.sh should not have interactive S2 key prompt (moved to /setup skill)"


def test_setup_sh_no_review_llm_interactive_prompt():
    content = SETUP_SH.read_text(encoding="utf-8")
    assert 'read -p "  Enter API base URL' not in content, \
        "setup.sh should not have interactive Review LLM prompt (moved to /setup skill)"


def test_setup_sh_references_setup_skill():
    content = SETUP_SH.read_text(encoding="utf-8")
    assert "/setup" in content, \
        "setup.sh 'Next steps' should reference the /setup skill"


def test_setup_sh_uses_project_venv_for_installs():
    content = SETUP_SH.read_text(encoding="utf-8")
    assert ".venv/bin/python" in content, "setup.sh should resolve the project .venv python"
    assert "-m pip install -r requirements.txt" in content, "setup.sh should install with the resolved python"


def test_setup_ps1_uses_project_venv_for_installs():
    content = SETUP_PS1.read_text(encoding="utf-8")
    assert ".venv\\Scripts\\python.exe" in content, "setup.ps1 should resolve the project .venv python"
    assert "-m pip install -r requirements.txt" in content, "setup.ps1 should install with the resolved python"


def test_setup_sh_verifies_runtime_dependencies():
    content = SETUP_SH.read_text(encoding="utf-8")
    assert "import fitz" in content, "setup.sh should verify PyMuPDF availability"
    assert "import requests" in content, "setup.sh should verify requests availability"
    assert "import feedparser" in content, "setup.sh should verify feedparser availability"
    assert "deepxiv-sdk" in content, "setup.sh should surface DeepXiv diagnostics"


def test_setup_ps1_verifies_runtime_dependencies():
    content = SETUP_PS1.read_text(encoding="utf-8")
    assert "import fitz" in content, "setup.ps1 should verify PyMuPDF availability"
    assert "import requests" in content, "setup.ps1 should verify requests availability"
    assert "import feedparser" in content, "setup.ps1 should verify feedparser availability"
    assert "deepxiv-sdk" in content, "setup.ps1 should surface DeepXiv diagnostics"


def test_setup_scripts_note_non_persistent_activation():
    sh_content = SETUP_SH.read_text(encoding="utf-8")
    ps1_content = SETUP_PS1.read_text(encoding="utf-8")
    assert "does not activate your current shell permanently" in sh_content
    assert "/init will use .venv/bin/python automatically" in sh_content
    assert "does not activate your current shell permanently" in ps1_content
    assert "/init will use .venv automatically" in ps1_content


def test_readme_mentions_setup_venv_behavior():
    content = README_MD.read_text(encoding="utf-8")
    assert "setup creates .venv for OmegaWiki" in content
    assert "/init will use .venv automatically" in content
    assert "setup 会为 OmegaWiki 创建 .venv" in content
    assert "/init 会自动使用 .venv" in content


def test_setup_sh_recursively_syncs_skill_subtrees():
    content = SETUP_SH.read_text(encoding="utf-8")
    assert 'cp -R "$skill_dir"/. ".claude/skills/$name/"' in content, (
        "setup.sh should recursively copy skill subtrees so local references sync with SKILL.md"
    )


# ── Active skill file (after setup.sh --lang sync) ────────────────────────

def test_active_skill_exists_if_setup_was_run():
    """Only fails if setup.sh has been run but /setup skill wasn't synced."""
    lang_file = PROJECT_ROOT / ".claude" / ".current-lang"
    if not lang_file.exists():
        pytest.skip("setup.sh has not been run yet — skipping active skill check")
    assert ACTIVE_SKILL.exists(), (
        f"Active /setup skill not found at {ACTIVE_SKILL}. "
        "Run: ./setup.sh --lang $(cat .claude/.current-lang)"
    )


# ── CLAUDE.md registers /setup ────────────────────────────────────────────

def test_en_claude_md_lists_setup_skill():
    claude_md = PROJECT_ROOT / "i18n" / "en" / "CLAUDE.md"
    assert claude_md.exists(), "i18n/en/CLAUDE.md not found"
    content = claude_md.read_text(encoding="utf-8")
    assert "`/setup`" in content, "i18n/en/CLAUDE.md skills table should list /setup"


def test_zh_claude_md_lists_setup_skill():
    claude_md = PROJECT_ROOT / "i18n" / "zh" / "CLAUDE.md"
    assert claude_md.exists(), "i18n/zh/CLAUDE.md not found"
    content = claude_md.read_text(encoding="utf-8")
    assert "`/setup`" in content, "i18n/zh/CLAUDE.md skills table should list /setup"


def test_en_setup_mentions_init_managed_raw_dirs():
    content = EN_SKILL.read_text(encoding="utf-8")
    assert "raw/discovered/" in content, "EN /setup should mention init-managed raw/discovered/"
    assert "raw/tmp/" in content, "EN /setup should mention init-managed raw/tmp/"


def test_zh_setup_mentions_init_managed_raw_dirs():
    content = ZH_SKILL.read_text(encoding="utf-8")
    assert "raw/discovered/" in content, "ZH /setup should mention init-managed raw/discovered/"
    assert "raw/tmp/" in content, "ZH /setup should mention init-managed raw/tmp/"
