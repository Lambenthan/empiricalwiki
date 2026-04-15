"""Tests for /daily-arxiv SKILL.md structural completeness.

Validates that the daily-arxiv skill follows extending.md structure,
references existing tools, documents wiki interactions, and aligns
with product CLAUDE.md.
"""

import re
from pathlib import Path

import pytest

# ── Paths ───────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = PROJECT_ROOT / ".claude" / "skills" / "daily-arxiv" / "SKILL.md"
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
TOOLS_DIR = PROJECT_ROOT / "tools"


@pytest.fixture(scope="module")
def skill_text():
    assert SKILL_PATH.exists(), f"daily-arxiv SKILL.md not found at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def claude_md_text():
    assert CLAUDE_MD.exists(), f"Product CLAUDE.md not found at {CLAUDE_MD}"
    return CLAUDE_MD.read_text(encoding="utf-8")


# ── 1. Required sections (extending.md structure) ──────────────────────

REQUIRED_SECTIONS = [
    "Inputs",
    "Outputs",
    "Wiki Interaction",
    "Workflow",
    "Constraints",
    "Error Handling",
    "Dependencies",
]


class TestSkillStructure:
    """Validate SKILL.md has all required sections per extending.md."""

    def test_file_exists(self):
        assert SKILL_PATH.exists()

    def test_has_frontmatter(self, skill_text):
        assert skill_text.startswith("---"), "SKILL.md must start with YAML frontmatter"
        parts = skill_text.split("---", 2)
        assert len(parts) >= 3, "SKILL.md must have closing --- for frontmatter"

    def test_frontmatter_has_description(self, skill_text):
        fm = skill_text.split("---", 2)[1]
        assert "description:" in fm, "Frontmatter must include description"

    def test_has_skill_heading(self, skill_text):
        assert re.search(r"^# /daily-arxiv", skill_text, re.MULTILINE), \
            "SKILL.md must have '# /daily-arxiv' heading"

    def test_has_intro_paragraph(self, skill_text):
        assert re.search(r"^>", skill_text, re.MULTILINE), \
            "SKILL.md must have intro paragraph (blockquote)"

    @pytest.mark.parametrize("section", REQUIRED_SECTIONS)
    def test_has_required_section(self, skill_text, section):
        pattern = rf"^##\s+{re.escape(section)}"
        assert re.search(pattern, skill_text, re.MULTILINE), \
            f"Missing required section: ## {section}"


# ── 2. Wiki Interaction documentation ──────────────────────────────────

class TestWikiInteraction:
    """Validate that wiki reads/writes are fully documented."""

    def test_has_reads_subsection(self, skill_text):
        assert re.search(r"^###\s+Reads", skill_text, re.MULTILINE), \
            "Wiki Interaction must have ### Reads subsection"

    def test_has_writes_subsection(self, skill_text):
        assert re.search(r"^###\s+Writes", skill_text, re.MULTILINE), \
            "Wiki Interaction must have ### Writes subsection"

    def test_reads_topics(self, skill_text):
        reads = _extract_section(skill_text, "Reads", level=3)
        assert "topics/" in reads, "Must document reading topics/ for keyword extraction"

    def test_reads_concepts(self, skill_text):
        reads = _extract_section(skill_text, "Reads", level=3)
        assert "concepts/" in reads, "Must document reading concepts/ for relevance"

    def test_reads_index(self, skill_text):
        reads = _extract_section(skill_text, "Reads", level=3)
        assert "index.md" in reads, "Must document reading index.md for dedup"

    def test_reads_gap_map(self, skill_text):
        reads = _extract_section(skill_text, "Reads", level=3)
        assert "open_questions.md" in reads, "Must document reading open_questions.md"

    def test_writes_papers(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "papers/" in writes, "Must document writing papers/ via /ingest"

    def test_writes_log(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "log.md" in writes, "Must document writing log.md"

    def test_writes_topics_sota(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "topics/" in writes, "Must document writing topics/ for SOTA updates"

    def test_documents_graph_edges(self, skill_text):
        assert re.search(r"^###\s+Graph edges", skill_text, re.MULTILINE), \
            "Wiki Interaction must have ### Graph edges subsection"


# ── 3. Workflow steps ──────────────────────────────────────────────────

EXPECTED_WORKFLOW_KEYWORDS = [
    ("RSS", "RSS"),              # Step 1: fetch RSS
    ("相关性", "relevance"),     # Step 2/3: relevance context/scoring (en) / 相关性 (zh)
    ("Ingest", "ingest"),        # Step 4: auto-ingest
    ("SOTA", "SOTA"),            # Step 5: SOTA detection
    ("digest", "digest"),        # Step 6: generate digest
    ("报告", "report"),          # Step 7: report (en) / 报告 (zh)
]


class TestWorkflow:
    """Validate workflow covers all required steps."""

    @pytest.mark.parametrize("zh_kw,en_kw", EXPECTED_WORKFLOW_KEYWORDS)
    def test_workflow_contains_keyword(self, skill_text, zh_kw, en_kw):
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert zh_kw in workflow or en_kw in workflow.lower(), \
            f"Workflow missing content containing '{zh_kw}' or '{en_kw}'"

    def test_has_at_least_6_steps(self, skill_text):
        workflow = _extract_section(skill_text, "Workflow", level=2)
        steps = re.findall(r"^### Step \d+", workflow, re.MULTILINE)
        assert len(steps) >= 6, f"Expected >= 6 workflow steps, found {len(steps)}"

    def test_relevance_scoring_documented(self, skill_text):
        """Must document the 0-3 relevance scoring system."""
        workflow = _extract_section(skill_text, "Workflow", level=2)
        for score in ["0", "1", "2", "3"]:
            assert score in workflow, f"Relevance score {score} not documented"

    def test_ingest_delegation(self, skill_text):
        """Must delegate to /ingest for high-relevance papers."""
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "/ingest" in workflow, "Must call /ingest for high-relevance papers"

    def test_dedup_check(self, skill_text):
        """Must check for duplicate papers before processing."""
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "去重" in workflow or "dedup" in workflow.lower() or "重复" in workflow, \
            "Must document deduplication check"

    def test_batch_scoring(self, skill_text):
        """Should use batch LLM scoring, not per-paper calls."""
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "批量" in workflow or "batch" in workflow.lower(), \
            "Should document batch scoring approach"


# ── 4. Tool references ─────────────────────────────────────────────────

REQUIRED_TOOL_REFS = [
    ("fetch_arxiv.py", "Must reference fetch_arxiv.py for RSS fetching"),
    ("fetch_deepxiv.py trending", "Must reference fetch_deepxiv.py trending for hot papers"),
    ("fetch_deepxiv.py brief", "Must reference fetch_deepxiv.py brief for TLDR enrichment"),
    ("init_discovery.py download", "Must reference init_discovery.py download for raw/discovered/ handoff"),
    ("research_wiki.py rebuild-context-brief", "Must reference rebuild-context-brief"),
    ("research_wiki.py rebuild-open-questions", "Must reference rebuild-open-questions"),
    ("research_wiki.py log", "Must reference log for audit trail"),
]


class TestToolReferences:
    """Validate tool references and existence."""

    @pytest.mark.parametrize("tool_ref,msg", REQUIRED_TOOL_REFS)
    def test_references_tool(self, skill_text, tool_ref, msg):
        assert tool_ref in skill_text, msg

    def test_fetch_arxiv_exists(self):
        assert (TOOLS_DIR / "fetch_arxiv.py").exists(), \
            "tools/fetch_arxiv.py must exist"

    def test_fetch_deepxiv_exists(self):
        assert (TOOLS_DIR / "fetch_deepxiv.py").exists(), \
            "tools/fetch_deepxiv.py must exist"

    def test_research_wiki_exists(self):
        assert (TOOLS_DIR / "research_wiki.py").exists(), \
            "tools/research_wiki.py must exist"


# ── 5. Ingest delegation ──────────────────────────────────────────────

class TestIngestDelegation:
    """Validate that daily-arxiv delegates to /ingest properly."""

    def test_calls_ingest_skill(self, skill_text):
        deps = _extract_section(skill_text, "Dependencies", level=2)
        assert "/ingest" in deps, "Dependencies must list /ingest skill"

    def test_max_ingest_limit(self, skill_text):
        assert "max-ingest" in skill_text or "max_ingest" in skill_text, \
            "Must support max-ingest limit parameter"

    def test_dry_run_option(self, skill_text):
        assert "dry-run" in skill_text or "dry_run" in skill_text, \
            "Must support --dry-run option"

    def test_raw_is_read_only_with_init_generated_dir_note(self, skill_text):
        assert "raw/discovered/" in skill_text, \
            "/daily-arxiv should acknowledge init-managed introduced papers under raw/discovered/"
        assert "raw/tmp/" in skill_text, \
            "/daily-arxiv should acknowledge init-managed prepared local inputs under raw/tmp/"

    def test_ingests_from_discovered_path_not_bare_url(self, skill_text):
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "canonical_ingest_path" in workflow, \
            "/daily-arxiv should hand off a canonical raw/discovered/ path to /ingest"


# ── 6. SOTA Detection ─────────────────────────────────────────────────

class TestSOTADetection:
    """Validate SOTA detection and update feature."""

    def test_sota_in_workflow(self, skill_text):
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "SOTA" in workflow, "Workflow must include SOTA detection step"

    def test_topics_sota_tracker(self, skill_text):
        """Must reference topics/ SOTA tracker for comparison."""
        assert "SOTA tracker" in skill_text, \
            "Must reference topics/ SOTA tracker"

    def test_sota_update_writes_topics(self, skill_text):
        """SOTA updates must write back to topics/ pages."""
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "topic" in workflow.lower() and "SOTA" in workflow, \
            "SOTA updates must modify topics/ pages"


# ── 7. Constraints ─────────────────────────────────────────────────────

REQUIRED_CONSTRAINTS_KEYWORDS = [
    ("3", "3"),              # only ingest relevance >= 3
    ("max", "max"),          # max ingest limit
    ("raw/", "raw/"),        # raw is read-only
    ("graph/", "graph/"),    # graph only via tools
    ("去重", "edup"),        # dedup (Deduplication / 去重)
    ("log.md", "log.md"),    # log append-only
]


class TestConstraints:
    """Validate constraints align with product CLAUDE.md rules."""

    @pytest.mark.parametrize("zh_kw,en_kw", REQUIRED_CONSTRAINTS_KEYWORDS)
    def test_constraint_present(self, skill_text, zh_kw, en_kw):
        constraints = _extract_section(skill_text, "Constraints", level=2)
        assert zh_kw in constraints or en_kw in constraints.lower(), \
            f"Constraints must mention '{zh_kw}' or '{en_kw}'"


# ── 8. Error handling ──────────────────────────────────────────────────

class TestErrorHandling:
    """Validate error handling covers critical failure modes."""

    def test_rss_failure(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "RSS" in errors or "拉取" in errors or "network" in errors.lower(), \
            "Must handle RSS fetch failure"

    def test_ingest_failure(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "ingest" in errors.lower(), \
            "Must handle partial ingest failure"

    def test_empty_results(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "空" in errors or "empty" in errors.lower(), \
            "Must handle empty RSS results"

    def test_wiki_not_initialized(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "init" in errors or "不存在" in errors or "init" in errors.lower(), \
            "Must handle missing wiki directory"

    def test_deepxiv_unavailable(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "deepxiv" in errors.lower(), \
            "Must handle DeepXiv API unavailability with graceful fallback"


# ── 9. CLAUDE.md consistency ───────────────────────────────────────────

class TestClaudeMdConsistency:
    """Validate that skill aligns with product CLAUDE.md."""

    def test_skill_listed_in_claude_md(self, claude_md_text):
        assert "/daily-arxiv" in claude_md_text, \
            "daily-arxiv must be listed in product CLAUDE.md skills table"

    def test_log_format_matches(self, skill_text):
        """Log message should follow CLAUDE.md log.md format."""
        assert "daily-arxiv |" in skill_text, \
            "Log format must follow 'daily-arxiv | ...' pattern from CLAUDE.md"

    def test_digest_format_documented(self, skill_text):
        """Digest output format must be documented."""
        assert ("### 高优先级" in skill_text or "高优先级" in skill_text or
                "High Priority" in skill_text), \
            "Must document digest format with priority sections"

    def test_cron_scheduling_mentioned(self, skill_text):
        """Must document cron scheduling capability."""
        assert "cron" in skill_text.lower() or "Cron" in skill_text, \
            "Must document cron scheduling support"


# ── Helpers ─────────────────────────────────────────────────────────────

def _extract_section(text: str, heading: str, level: int = 2) -> str:
    """Extract content under a markdown heading until the next heading of same or higher level."""
    prefix = "#" * level
    pattern = rf"^{prefix}\s+{re.escape(heading)}.*?\n(.*?)(?=^{'#' * level}\s|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1)
    # Fallback: try partial match
    pattern = rf"^{prefix}\s+.*{re.escape(heading)}.*?\n(.*?)(?=^{'#' * level}\s|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""
