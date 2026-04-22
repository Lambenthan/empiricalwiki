"""Tests for the rewritten /init skill."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = PROJECT_ROOT / ".claude" / "skills" / "init" / "SKILL.md"
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
I18N_EN_CLAUDE_MD = PROJECT_ROOT / "i18n" / "en" / "CLAUDE.md"
I18N_ZH_CLAUDE_MD = PROJECT_ROOT / "i18n" / "zh" / "CLAUDE.md"


@pytest.fixture(scope="module")
def skill_content():
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def claude_content():
    return CLAUDE_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def i18n_en_claude_content():
    return I18N_EN_CLAUDE_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def i18n_zh_claude_content():
    return I18N_ZH_CLAUDE_MD.read_text(encoding="utf-8")


class TestSkillStructure:
    def test_exists(self):
        assert SKILL_PATH.exists()

    def test_frontmatter(self, skill_content):
        assert skill_content.startswith("---")
        assert "description:" in skill_content
        assert "argument-hint:" in skill_content

    @pytest.mark.parametrize("section", [
        "## Inputs",
        "## Outputs",
        "## Wiki Interaction",
        "## Workflow",
        "## Constraints",
        "## Error Handling",
        "## Dependencies",
    ])
    def test_required_sections(self, skill_content, section):
        assert section in skill_content


class TestPublicContract:
    def test_supports_no_introduction(self, skill_content):
        assert "--no-introduction" in skill_content

    def test_no_introduction_is_user_controlled(self, skill_content):
        lowered = skill_content.lower()
        assert "do not infer `--no-introduction` from repository state alone" in lowered
        assert "user explicitly asked to disable external discovery" in lowered

    def test_mentions_raw_discovered(self, skill_content):
        assert "raw/discovered/" in skill_content

    def test_mentions_raw_tmp(self, skill_content):
        assert "raw/tmp/" in skill_content

    def test_reads_notes_and_web(self, skill_content):
        assert "raw/notes/" in skill_content
        assert "raw/web/" in skill_content

    def test_provisional_notice_is_exact(self, skill_content):
        assert "Provisional note: seeded from raw/notes or raw/web during /init; pending validation from ingested papers." in skill_content

    def test_notes_web_claim_defaults(self, skill_content):
        assert "status: proposed" in skill_content
        assert "confidence: 0.2" in skill_content
        assert "source_papers: []" in skill_content
        assert "evidence: []" in skill_content

    def test_init_does_not_create_people_or_foundations(self, skill_content):
        lowered = skill_content.lower()
        assert "must not create `people/` pages directly" in lowered or "不得直接创建 `people/`" in skill_content
        assert "auto-create foundations" in lowered or "自动创建 foundations" in skill_content

    def test_prefill_is_optional(self, skill_content):
        assert "/prefill" in skill_content
        assert "optional" in skill_content.lower() or "可选" in skill_content

    def test_mentions_degraded_chinese_notes_warning(self, skill_content):
        lowered = skill_content.lower()
        assert "lower-confidence" in lowered or "较低置信度" in skill_content
        assert "raw/notes/" in skill_content


class TestWorkflow:
    def test_prefers_repo_python_bin(self, skill_content):
        assert "PYTHON_BIN" in skill_content
        assert ".venv/bin/python" in skill_content
        assert ".venv/Scripts/python.exe" in skill_content

    def test_step1_init(self, skill_content):
        assert "### Step 1" in skill_content
        assert "research_wiki.py init" in skill_content
        assert '"$PYTHON_BIN" tools/research_wiki.py init wiki/' in skill_content

    def test_step2_prepare(self, skill_content):
        assert "### Step 2" in skill_content
        assert "init_discovery.py prepare" in skill_content
        assert ".checkpoints/init-prepare.json" in skill_content
        assert '"$PYTHON_BIN" tools/init_discovery.py prepare' in skill_content

    def test_step3_discovery_plan_and_fetch(self, skill_content):
        assert "### Step 3" in skill_content
        assert "init_discovery.py plan" in skill_content
        assert "--output-plan .checkpoints/init-plan.json" in skill_content
        assert "init_discovery.py fetch" in skill_content
        assert ".checkpoints/init-sources.json" in skill_content
        assert "8-10" in skill_content
        assert '"$PYTHON_BIN" tools/init_discovery.py plan' in skill_content
        assert '"$PYTHON_BIN" tools/init_discovery.py fetch' in skill_content

    def test_step3_requires_explicit_final_selection_before_fetch(self, skill_content):
        assert "read `.checkpoints/init-plan.json`" in skill_content
        assert "before `fetch`" in skill_content
        assert "final selection artifact" in skill_content
        assert "`candidate_id`" in skill_content

    def test_step3_requires_revise_before_fetch_when_count_is_wrong(self, skill_content):
        lowered = skill_content.lower()
        assert "stop and revise the final selection before `fetch`" in lowered
        assert "`--no-introduction`" in skill_content
        assert "more than 10 parseable papers" in skill_content

    def test_step3_distinguishes_shortlist_from_final_set(self, skill_content):
        assert "over-picked `shortlist`" in skill_content
        assert "final **8-10** papers total" in skill_content
        assert "never forward the whole shortlist implicitly" in skill_content

    def test_step4_scaffold_pages(self, skill_content):
        assert "### Step 4" in skill_content
        assert "Summary" in skill_content
        assert "topics/" in skill_content
        assert "ideas/" in skill_content
        assert "concepts/" in skill_content
        assert "claims/" in skill_content

    def test_step4_5_scaffold_commit(self, skill_content):
        assert "### Step 4.5" in skill_content
        assert "git stash" in skill_content
        assert "raw/tmp/" in skill_content
        assert "raw/discovered/" in skill_content
        assert 'commit -m "init: scaffold before parallel ingest"' in skill_content

    def test_step4_5_records_base_branch_and_commit(self, skill_content):
        assert "git branch --show-current" in skill_content
        assert "base_branch" in skill_content
        assert "git rev-parse HEAD" in skill_content
        assert "base_commit" in skill_content

    def test_step4_5_checkpoint_ids_are_post_trim(self, skill_content):
        assert "post-trim" in skill_content
        assert "not the over-picked shortlist" in skill_content

    def test_step5_parallel_ingest(self, skill_content):
        assert "### Step 5" in skill_content
        assert "/ingest" in skill_content
        assert "run_in_background" in skill_content
        assert "worktree" in skill_content.lower()
        assert "dedup-edges" in skill_content
        assert ".checkpoints/init-sources.json" in skill_content

    def test_step6_report(self, skill_content):
        assert "### Step 6" in skill_content
        assert "raw/tmp/" in skill_content
        assert "raw/discovered/" in skill_content

    def test_resume_manifest_checkpoint(self, skill_content):
        assert ".checkpoints/init-prepare.json" in skill_content
        assert ".checkpoints/init-plan.json" in skill_content
        assert ".checkpoints/init-sources.json" in skill_content
        assert "checkpoint-set-meta" in skill_content

    def test_step3_mentions_explicit_deepxiv_relevance_score(self, skill_content):
        lowered = skill_content.lower()
        assert "`relevance_score`" in skill_content or "relevance_score" in skill_content
        assert "explicitly" in lowered or "显式" in skill_content


class TestParallelGuardrails:
    def test_gitattributes_union_merge(self, skill_content):
        assert ".gitattributes" in skill_content
        assert "merge=union" in skill_content

    def test_relative_paths_only(self, skill_content):
        assert "relative paths only" in skill_content.lower() or "相对路径" in skill_content

    def test_worktrees_branch_from_scaffold_commit(self, skill_content):
        assert "git worktree add -b" in skill_content
        assert "BASE_COMMIT" in skill_content
        assert "BASE_BRANCH" in skill_content

    def test_init_mode_skips(self, skill_content):
        lowered = skill_content.lower()
        assert "skip `fetch_s2.py citations`" in lowered
        assert "skip `fetch_s2.py references`" in lowered
        assert "skip per-subagent `rebuild-index`" in lowered
        assert "skip per-subagent `rebuild-context-brief`" in lowered
        assert "skip per-subagent `rebuild-open-questions`" in lowered

    def test_dedup_tools_still_required(self, skill_content):
        assert "find-similar-claim" in skill_content
        assert "find-similar-concept" in skill_content


class TestErrorHandling:
    def test_detached_head_is_called_out(self, skill_content):
        lowered = skill_content.lower()
        assert "detached head" in lowered
        assert "named branch" in lowered or "命名分支" in skill_content


class TestDependencies:
    def test_new_tool_exists(self):
        assert (PROJECT_ROOT / "tools" / "init_discovery.py").exists()

    @pytest.mark.parametrize("name", [
        "init_discovery.py",
        "research_wiki.py",
        "lint.py",
    ])
    def test_tool_referenced(self, skill_content, name):
        assert name in skill_content


class TestClaudemdConsistency:
    def test_skill_listed(self, claude_content):
        assert "/init" in claude_content

    def test_claude_mentions_raw_discovered(self, claude_content):
        assert "raw/discovered/" in claude_content

    def test_claude_mentions_raw_tmp(self, claude_content):
        assert "raw/tmp/" in claude_content

    def test_claude_declares_user_owned_skill_parameters(self, claude_content):
        lowered = claude_content.lower()
        assert "user-facing skill parameters are user-owned" in lowered
        assert "argument-hint" in claude_content

    def test_i18n_en_claude_declares_user_owned_skill_parameters(self, i18n_en_claude_content):
        lowered = i18n_en_claude_content.lower()
        assert "user-facing skill parameters are user-owned" in lowered
        assert "argument-hint" in i18n_en_claude_content

    def test_i18n_zh_claude_declares_user_owned_skill_parameters(self, i18n_zh_claude_content):
        assert "用户可见参数归用户所有" in i18n_zh_claude_content
        assert "argument-hint" in i18n_zh_claude_content
