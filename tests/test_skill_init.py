"""Tests for the refactored /init skill."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EN_SKILL = PROJECT_ROOT / "i18n" / "en" / "skills" / "init" / "SKILL.md"
ZH_SKILL = PROJECT_ROOT / "i18n" / "zh" / "skills" / "init" / "SKILL.md"
ACTIVE_SKILL = PROJECT_ROOT / ".claude" / "skills" / "init" / "SKILL.md"
EN_REFS = PROJECT_ROOT / "i18n" / "en" / "skills" / "init" / "references"
ZH_REFS = PROJECT_ROOT / "i18n" / "zh" / "skills" / "init" / "references"
ACTIVE_REFS = PROJECT_ROOT / ".claude" / "skills" / "init" / "references"
EN_CLAUDE_MD = PROJECT_ROOT / "i18n" / "en" / "CLAUDE.md"
ZH_CLAUDE_MD = PROJECT_ROOT / "i18n" / "zh" / "CLAUDE.md"
ROOT_CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"


@pytest.fixture(scope="module")
def en_skill_text():
    return EN_SKILL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def zh_skill_text():
    return ZH_SKILL.read_text(encoding="utf-8")


REQUIRED_SECTIONS = [
    "## Inputs",
    "## Outputs",
    "## Wiki Interaction",
    "## Workflow",
    "## Constraints",
    "## Error Handling",
    "## Dependencies",
]


class TestSkillFiles:
    def test_en_skill_exists(self):
        assert EN_SKILL.exists()

    def test_zh_skill_exists(self):
        assert ZH_SKILL.exists()

    def test_reference_dirs_exist(self):
        assert EN_REFS.exists()
        assert ZH_REFS.exists()

    def test_reference_files_exist(self):
        for root in (EN_REFS, ZH_REFS):
            assert (root / "prepare-and-discovery.md").exists()
            assert (root / "planner-policy.md").exists()
            assert (root / "parallel-ingest.md").exists()

    def test_active_skill_exists_if_setup_was_run(self):
        lang_file = PROJECT_ROOT / ".claude" / ".current-lang"
        if not lang_file.exists():
            pytest.skip("setup.sh has not been run yet — skipping active runtime check")
        assert ACTIVE_SKILL.exists()
        assert (ACTIVE_REFS / "prepare-and-discovery.md").exists()
        assert (ACTIVE_REFS / "planner-policy.md").exists()
        assert (ACTIVE_REFS / "parallel-ingest.md").exists()


class TestSkillStructure:
    def test_frontmatter(self, en_skill_text):
        assert en_skill_text.startswith("---")
        assert "description:" in en_skill_text
        assert "argument-hint:" in en_skill_text

    @pytest.mark.parametrize("section", REQUIRED_SECTIONS)
    def test_required_sections_present(self, en_skill_text, zh_skill_text, section):
        assert section in en_skill_text
        assert section in zh_skill_text

    def test_skill_links_local_references(self, en_skill_text, zh_skill_text):
        for name in (
            "references/prepare-and-discovery.md",
            "references/planner-policy.md",
            "references/parallel-ingest.md",
        ):
            assert name in en_skill_text
            assert name in zh_skill_text


class TestPublicContract:
    def test_supports_no_introduction(self, en_skill_text):
        assert "--no-introduction" in en_skill_text

    def test_no_introduction_is_user_controlled(self, en_skill_text):
        lowered = en_skill_text.lower()
        assert "do not infer `--no-introduction` from repository state alone" in lowered
        assert "user explicitly asked to disable external discovery" in lowered

    def test_mentions_raw_tmp_and_discovered(self, en_skill_text):
        assert "raw/tmp/" in en_skill_text
        assert "raw/discovered/" in en_skill_text

    def test_reads_notes_and_web(self, en_skill_text):
        assert "raw/notes/" in en_skill_text
        assert "raw/web/" in en_skill_text

    def test_provisional_notice_is_exact(self, en_skill_text):
        assert "Provisional note: seeded from raw/notes or raw/web during /init; pending validation from ingested papers." in en_skill_text

    def test_notes_web_claim_defaults_documented(self, en_skill_text):
        assert "status: proposed" in en_skill_text
        assert "confidence: 0.2" in en_skill_text
        assert "source_papers: []" in en_skill_text
        assert "evidence: []" in en_skill_text

    def test_prefill_is_optional(self, en_skill_text, zh_skill_text):
        assert "/prefill" in en_skill_text
        assert "optional" in en_skill_text.lower()
        assert "/prefill" in zh_skill_text
        assert "可选" in zh_skill_text

    def test_init_does_not_create_people_or_foundations(self, en_skill_text, zh_skill_text):
        lowered = en_skill_text.lower()
        assert "must not create `people/` pages directly" in lowered
        assert "must not auto-create foundations" in lowered
        assert "不得直接创建 `people/` 页面" in zh_skill_text
        assert "不得自动创建 foundations" in zh_skill_text


class TestWorkflow:
    def test_prefers_repo_python_bin(self, en_skill_text):
        assert "PYTHON_BIN" in en_skill_text
        assert ".venv/bin/python" in en_skill_text
        assert ".venv/Scripts/python.exe" in en_skill_text

    def test_core_steps_present(self, en_skill_text):
        for step in ("### Step 1", "### Step 2", "### Step 3", "### Step 4", "### Step 5", "### Step 6"):
            assert step in en_skill_text

    def test_prepare_and_plan_commands_present(self, en_skill_text):
        assert '"$PYTHON_BIN" tools/init_discovery.py prepare' in en_skill_text
        assert "--pdf-titles-json .checkpoints/init-pdf-titles.json" in en_skill_text
        assert '"$PYTHON_BIN" tools/init_discovery.py plan' in en_skill_text
        assert '"$PYTHON_BIN" tools/init_discovery.py fetch' in en_skill_text

    def test_prepare_helper_present(self, en_skill_text):
        assert "prepare_paper_source.py" in en_skill_text

    def test_prepare_contract_is_agent_first(self, en_skill_text):
        lowered = en_skill_text.lower()
        assert ".checkpoints/init-pdf-titles.json" in en_skill_text
        assert "arxiv_id" in en_skill_text
        assert "filename/path arxiv id" in lowered
        assert "authoritative" in lowered
        assert "do not use pdf metadata or body text as arxiv-id hints" in lowered

    def test_final_selection_contract_present(self, en_skill_text):
        assert "shortlist" in en_skill_text
        assert "final **8-10** papers total" in en_skill_text
        assert "final selection artifact" in en_skill_text
        assert "`candidate_id`" in en_skill_text
        assert "stop and revise the final selection before `fetch`" in en_skill_text

    def test_planner_policy_is_qualitative_in_skill_doc(self, en_skill_text):
        lowered = en_skill_text.lower()
        assert "favor relevance, freshness, connectivity, and survey coverage" in lowered
        assert "exact ranking weights" in lowered
        assert "tools/init_discovery.py" in en_skill_text
        assert "relevance = 30" not in en_skill_text
        assert "freshness = 20" not in en_skill_text
        assert "anchor/connectivity bonus = 20" not in en_skill_text

    def test_parallel_ingest_contract_present(self, en_skill_text):
        lowered = en_skill_text.lower()
        assert ".checkpoints/init-sources.json" in en_skill_text
        assert "relative paths only" in lowered
        assert "detached head" in lowered
        assert "commit the freshly created scaffold" in lowered
        assert ".gitattributes" in en_skill_text
        assert "merge=union" in en_skill_text
        assert "skip `fetch_s2.py citations`" in lowered
        assert "skip `fetch_s2.py references`" in lowered
        assert "skip per-subagent `rebuild-index`" in lowered
        assert "commit the ingest result inside the worktree before exiting" in lowered

    def test_rebuild_steps_present(self, en_skill_text):
        assert "dedup-edges" in en_skill_text
        assert "rebuild-index" in en_skill_text
        assert "rebuild-context-brief" in en_skill_text
        assert "rebuild-open-questions" in en_skill_text
        assert 'tools/lint.py --wiki-dir wiki/ --fix' in en_skill_text


class TestReferenceDocs:
    def test_prepare_reference_covers_manifest_and_fetch(self):
        text = (EN_REFS / "prepare-and-discovery.md").read_text(encoding="utf-8")
        lowered = text.lower()
        assert "canonical_ingest_path" in text
        assert ".checkpoints/init-sources.json" in text
        assert ".checkpoints/init-pdf-titles.json" in text
        assert "arxiv_id" in text
        assert "authoritative" in lowered
        assert "raw/discovered/" in text
        assert "raw/tmp/" in text
        assert "prepare_paper_source.py" in text

    def test_planner_reference_is_behavioral_not_numeric(self):
        text = (EN_REFS / "planner-policy.md").read_text(encoding="utf-8")
        lowered = text.lower()
        assert "behavioral policy" in lowered
        assert "tools/init_discovery.py" in text
        assert "exact weights" in lowered
        assert "30" not in text
        assert "20" not in text
        assert "15" not in text

    def test_parallel_reference_covers_worktrees(self):
        text = (EN_REFS / "parallel-ingest.md").read_text(encoding="utf-8")
        assert "git worktree add -b" in text
        assert "relative source path" in text
        assert "dedup-edges" in text
        assert 'git commit -m "init: scaffold before parallel ingest" --no-gpg-sign' in text
        assert ".gitattributes" in text
        assert "merge=union" in text
        assert "Commit the result inside the worktree before exiting" in text
        assert "A branch with no ingest commit is an error" in text


class TestClaudemdConsistency:
    def test_claude_mentions_local_skill_references(self):
        for path in (EN_CLAUDE_MD, ZH_CLAUDE_MD, ROOT_CLAUDE_MD):
            text = path.read_text(encoding="utf-8")
            assert "SKILL.md" in text
            assert "reference" in text.lower() or "参考文件" in text
            assert "/init" in text


class TestDependencies:
    def test_required_tools_exist(self):
        assert (PROJECT_ROOT / "tools" / "init_discovery.py").exists()
        assert (PROJECT_ROOT / "tools" / "prepare_paper_source.py").exists()
        assert (PROJECT_ROOT / "tools" / "research_wiki.py").exists()
        assert (PROJECT_ROOT / "tools" / "lint.py").exists()
