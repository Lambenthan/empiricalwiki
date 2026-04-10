"""Tests for .claude/skills/init/SKILL.md

Validates:
  - SKILL.md structure follows extending.md requirements
  - All 8 entity types are covered
  - Tool references point to existing files
  - Workflow steps are complete
  - Constraints match CLAUDE.md
  - Dependencies are valid
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = PROJECT_ROOT / ".claude" / "skills" / "init" / "SKILL.md"
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"


@pytest.fixture(scope="module")
def skill_content():
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def claude_content():
    return CLAUDE_MD.read_text(encoding="utf-8")


# ── Structure ────────────────────────────────────────────────────────────────

class TestSkillStructure:
    """SKILL.md exists and has all required sections per extending.md."""

    def test_file_exists(self):
        assert SKILL_PATH.exists()

    def test_has_frontmatter(self, skill_content):
        assert skill_content.startswith("---")
        assert "description:" in skill_content

    def test_has_title(self, skill_content):
        assert "# /init" in skill_content

    def test_has_inputs_section(self, skill_content):
        assert "## Inputs" in skill_content

    def test_has_outputs_section(self, skill_content):
        assert "## Outputs" in skill_content

    def test_has_wiki_interaction_section(self, skill_content):
        assert "## Wiki Interaction" in skill_content

    def test_has_workflow_section(self, skill_content):
        assert "## Workflow" in skill_content

    def test_has_constraints_section(self, skill_content):
        assert "## Constraints" in skill_content

    def test_has_error_handling_section(self, skill_content):
        assert "## Error Handling" in skill_content

    def test_has_dependencies_section(self, skill_content):
        assert "## Dependencies" in skill_content

    def test_has_argument_hint(self, skill_content):
        assert "argument-hint:" in skill_content


# ── Wiki Interaction ─────────────────────────────────────────────────────────

class TestWikiInteraction:
    """Wiki Interaction section documents reads and writes."""

    def test_has_reads_subsection(self, skill_content):
        assert "### Reads" in skill_content

    def test_has_writes_subsection(self, skill_content):
        assert "### Writes" in skill_content

    def test_reads_raw_papers(self, skill_content):
        assert "raw/papers/" in skill_content

    def test_writes_index(self, skill_content):
        assert "index.md" in skill_content

    def test_writes_log(self, skill_content):
        assert "log.md" in skill_content

    def test_writes_summary(self, skill_content):
        assert "Summary/" in skill_content

    def test_writes_topics(self, skill_content):
        assert "topics/" in skill_content

    def test_writes_ideas(self, skill_content):
        assert "ideas/" in skill_content

    def test_mentions_graph_edges(self, skill_content):
        assert "Graph edges" in skill_content or "graph edge" in skill_content.lower()


# ── Entity Coverage ──────────────────────────────────────────────────────────

class TestEntityCoverage:
    """All 8 entity types are mentioned in outputs or workflow."""

    ENTITIES = ["papers", "concepts", "topics", "people",
                "ideas", "experiments", "claims", "Summary"]

    @pytest.mark.parametrize("entity", ENTITIES)
    def test_entity_mentioned_in_outputs(self, skill_content, entity):
        # Entity should appear in Outputs section or workflow
        assert entity in skill_content, f"Entity '{entity}' not mentioned in skill"

    def test_no_experiments_created_directly(self, skill_content):
        """init should NOT create experiments — that's /exp-design's job."""
        assert "不创建空 experiments" in skill_content or "exp-design" in skill_content


# ── Workflow Steps ───────────────────────────────────────────────────────────

class TestWorkflow:
    """Workflow has all expected steps."""

    def test_step1_init(self, skill_content):
        assert "### Step 1" in skill_content
        assert "research_wiki.py init" in skill_content

    def test_step2_collect_sources(self, skill_content):
        assert "### Step 2" in skill_content
        assert "raw/papers/" in skill_content

    def test_step3_domain_analysis(self, skill_content):
        assert "### Step 3" in skill_content

    def test_step4_skeleton_pages(self, skill_content):
        assert "### Step 4" in skill_content
        assert "Summary" in skill_content
        assert "topics" in skill_content.lower()

    def test_step5_batch_ingest(self, skill_content):
        assert "### Step 5" in skill_content
        assert "/ingest" in skill_content

    def test_step6_ideas_optional(self, skill_content):
        assert "### Step 6" in skill_content
        assert "idea" in skill_content.lower()

    def test_step7_graph_rebuild(self, skill_content):
        assert "### Step 7" in skill_content
        assert "rebuild-index" in skill_content
        assert "rebuild-context-brief" in skill_content
        assert "rebuild-open-questions" in skill_content

    def test_step8_report(self, skill_content):
        assert "### Step 8" in skill_content

    def test_ingest_is_delegated(self, skill_content):
        """Papers are ingested via /ingest skill, not inline."""
        assert "/ingest" in skill_content

    def test_importance_ordering(self, skill_content):
        """High importance papers should be ingested first."""
        assert "importance" in skill_content.lower()


# ── Tool References ──────────────────────────────────────────────────────────

class TestToolReferences:
    """Referenced tools exist on disk."""

    TOOLS = [
        ("tools/research_wiki.py", "research_wiki.py"),
        ("tools/fetch_s2.py", "fetch_s2.py"),
        ("tools/fetch_deepxiv.py", "fetch_deepxiv.py"),
        ("tools/lint.py", "lint.py"),
        # fetch_arxiv.py is NOT referenced by /init (it's an RSS fetcher for /daily-arxiv)
    ]

    @pytest.mark.parametrize("tool_path,name", TOOLS)
    def test_tool_exists(self, tool_path, name):
        full_path = PROJECT_ROOT / tool_path
        assert full_path.exists(), f"Tool {tool_path} not found"

    @pytest.mark.parametrize("tool_path,name", TOOLS)
    def test_tool_referenced_in_skill(self, skill_content, tool_path, name):
        assert name in skill_content, f"Tool {name} not referenced in SKILL.md"

    def test_research_wiki_subcommands(self, skill_content):
        """Key research_wiki.py subcommands are referenced."""
        for cmd in ["init", "slug", "add-edge", "rebuild-index",
                     "rebuild-context-brief", "rebuild-open-questions", "stats", "log"]:
            assert cmd in skill_content, f"Subcommand '{cmd}' not in SKILL.md"

    def test_references_fetch_deepxiv_search(self, skill_content):
        assert "fetch_deepxiv.py search" in skill_content, \
            "Must reference fetch_deepxiv.py search for semantic search"

    def test_references_s2_citations(self, skill_content):
        assert "fetch_s2.py references" in skill_content or "fetch_s2.py citations" in skill_content, \
            "Must reference fetch_s2.py references/citations for citation-chain expansion"


# ── Smart Expansion (Step 2) ────────────────────────────────────────────────

class TestSmartExpansion:
    """Step 2 search expansion is properly designed."""

    def test_citation_chain_expansion(self, skill_content):
        """Citation-chain expansion is the primary discovery method."""
        assert ("citation" in skill_content.lower() or "references" in skill_content.lower()), \
            "Must use citation-chain expansion as primary discovery"

    def test_expansion_budget(self, skill_content):
        """Expansion has a paper budget to prevent over-fetching."""
        assert ("5" in skill_content and "8" in skill_content) or "budget" in skill_content.lower(), \
            "Must define a paper budget for expansion"

    def test_download_mechanism(self, skill_content):
        """Actual download mechanism is specified (curl/wget)."""
        assert "curl" in skill_content.lower() or "download" in skill_content.lower(), \
            "Must specify how to download papers to raw/"

    def test_dedup_before_download(self, skill_content):
        """Deduplication is done before downloading."""
        assert ("dedup" in skill_content.lower() or "deduplicate" in skill_content.lower()
                or "去重" in skill_content), \
            "Must deduplicate against existing papers before downloading"

    def test_transparency(self, skill_content):
        """User can distinguish provided vs discovered papers."""
        assert ("transparency" in skill_content.lower() or "透明" in skill_content
                or "discovered" in skill_content.lower() or "发现" in skill_content), \
            "Must clearly separate user-provided from discovered papers"


# ── Subagent Ingest (Step 5) ────────────────────────────────────────────────

class TestSubagentIngest:
    """Step 5 uses parallel subagents with worktree isolation for each paper."""

    def test_subagent_mentioned(self, skill_content):
        """Subagent/Agent is the mechanism for ingest."""
        assert ("subagent" in skill_content.lower() or "agent(" in skill_content
                or "子代理" in skill_content), \
            "Must use Agent subagents for paper ingest"

    def test_parallel_execution(self, skill_content):
        """Papers are ingested in parallel via background agents."""
        assert ("run_in_background" in skill_content or "parallel" in skill_content.lower()
                or "后台" in skill_content or "并行" in skill_content), \
            "Must use run_in_background or parallel execution for agents"

    def test_worktree_isolation(self, skill_content):
        """Each agent runs in an isolated git worktree."""
        assert ("worktree" in skill_content.lower() or "isolation" in skill_content.lower()), \
            "Must use worktree isolation for parallel agents"

    def test_merge_phase_described(self, skill_content):
        """After parallel fan-out, a merge phase brings results together."""
        assert ("merge" in skill_content.lower() or "合并" in skill_content), \
            "Must describe the fan-in merge phase after parallel ingest"

    def test_dedup_edges_after_merge(self, skill_content):
        """dedup-edges must be run after merging parallel worktrees."""
        assert "dedup-edges" in skill_content, \
            "Must run dedup-edges after parallel merge to remove duplicate edges"

    def test_no_bypass(self, skill_content):
        """Must not bypass subagents to create pages directly."""
        assert ("bypass" in skill_content.lower() or "绕过" in skill_content
                or "never bypass" in skill_content.lower() or "禁止绕过" in skill_content), \
            "Must prohibit bypassing subagents"

    def test_init_mode_skips_s2_citations(self, skill_content):
        """Init-mode subagent must skip fetch_s2.py citations/references (done in Step 2)."""
        prompt_section = skill_content[skill_content.find("Agent({"):]
        assert ("citations" in prompt_section.lower() and
                ("skip" in prompt_section.lower() or "跳过" in prompt_section)), \
            "Subagent prompt must tell ingest to skip S2 citations (already done in Step 2)"

    def test_init_mode_skips_index_update(self, skill_content):
        """Init-mode subagent must skip index.md update (rebuilt by orchestrator in Step 7)."""
        prompt_section = skill_content[skill_content.find("Agent({"):]
        assert ("index.md" in prompt_section and
                ("skip" in prompt_section.lower() or "跳过" in prompt_section)), \
            "Subagent prompt must tell ingest to skip index.md update (rebuilt by orchestrator)"

    def test_init_mode_wiki_state_passed(self, skill_content):
        """Orchestrator must pass current wiki state to each subagent."""
        prompt_section = skill_content[skill_content.find("Agent({"):]
        assert ("topics" in prompt_section.lower() or "topics already created" in prompt_section.lower()), \
            "Subagent prompt must include current wiki state (existing topics/papers)"


# ── Constraints ──────────────────────────────────────────────────────────────

class TestConstraints:
    """Constraints match CLAUDE.md rules."""

    def test_raw_readonly(self, skill_content):
        assert "raw/ 只读" in skill_content or "raw/ is read-only" in skill_content.lower()

    def test_graph_via_tools(self, skill_content):
        assert "graph/" in skill_content and "tools" in skill_content.lower()

    def test_bidirectional_links(self, skill_content):
        assert (
            "双向链接" in skill_content or "反向链接" in skill_content
            or "bidirectional" in skill_content.lower() or "backlink" in skill_content.lower()
        )

    def test_tex_priority(self, skill_content):
        assert "tex" in skill_content.lower() and "pdf" in skill_content.lower()

    def test_slug_via_tool(self, skill_content):
        assert "research_wiki.py slug" in skill_content

    def test_claude_md_templates(self, skill_content):
        assert "CLAUDE.md" in skill_content

    def test_importance_scale(self, skill_content):
        # Check that importance scale is documented
        assert "1=" in skill_content or "1-5" in skill_content


# ── Error Handling ───────────────────────────────────────────────────────────

class TestErrorHandling:
    """Error scenarios are documented."""

    def test_empty_raw(self, skill_content):
        assert (
            "raw/ 为空" in skill_content or "为空" in skill_content
            or "raw/ is empty" in skill_content.lower() or "empty" in skill_content.lower()
        )

    def test_search_failure(self, skill_content):
        assert "搜索失败" in skill_content or "search" in skill_content.lower()

    def test_single_ingest_failure(self, skill_content):
        assert ("ingest 失败" in skill_content or "失败" in skill_content or
                "ingest fail" in skill_content.lower() or "partial ingest" in skill_content.lower())

    def test_idempotent(self, skill_content):
        assert (
            "幂等" in skill_content or "已存在" in skill_content
            or "idempotent" in skill_content.lower() or "already exist" in skill_content.lower()
        )

    def test_deepxiv_failure(self, skill_content):
        errors_section = skill_content[skill_content.find("## Error Handling"):]
        assert "deepxiv" in errors_section.lower() or "DeepXiv" in errors_section, \
            "Must handle DeepXiv API unavailability with graceful fallback"


# ── CLAUDE.md Consistency ────────────────────────────────────────────────────

class TestClaudeMdConsistency:
    """Skill is consistent with product CLAUDE.md."""

    def test_skill_listed_in_claude_md(self, claude_content):
        assert "/init" in claude_content

    def test_all_entity_dirs_from_claude_md(self, skill_content, claude_content):
        """All entity directories in CLAUDE.md are mentioned in skill."""
        for entity in ["papers", "concepts", "topics", "people",
                       "ideas", "experiments", "claims", "Summary"]:
            assert entity in skill_content

    def test_edge_types_valid(self, skill_content, claude_content):
        """Edge types mentioned in skill are valid per CLAUDE.md."""
        valid_types = {"extends", "contradicts", "supports", "inspired_by",
                       "tested_by", "invalidates", "supersedes", "addresses_gap",
                       "derived_from"}
        # Find edge type mentions in skill
        edge_mentions = re.findall(r"--type\s+(\w+)", skill_content)
        for edge_type in edge_mentions:
            assert edge_type in valid_types, f"Edge type '{edge_type}' not valid"

    def test_log_format_matches(self, skill_content):
        """Log entries follow CLAUDE.md format."""
        assert "init |" in skill_content
