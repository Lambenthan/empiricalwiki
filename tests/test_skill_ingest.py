"""Tests for /ingest SKILL.md structural completeness.

Validates that the ingest skill follows the extending.md structure,
references existing tools, and documents all required wiki interactions.
"""

import re
from pathlib import Path

import pytest

# ── Paths ───────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = PROJECT_ROOT / ".claude" / "skills" / "ingest" / "SKILL.md"
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
TOOLS_DIR = PROJECT_ROOT / "tools"


@pytest.fixture(scope="module")
def skill_text():
    assert SKILL_PATH.exists(), f"Ingest SKILL.md not found at {SKILL_PATH}"
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
        assert re.search(r"^# /ingest", skill_text, re.MULTILINE), \
            "SKILL.md must have '# /ingest' heading"

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

    def test_reads_index(self, skill_text):
        reads = _extract_section(skill_text, "Reads", level=3)
        assert "index.md" in reads, "Must document reading index.md"

    def test_reads_papers(self, skill_text):
        reads = _extract_section(skill_text, "Reads", level=3)
        assert "papers/" in reads, "Must document reading papers/"

    def test_writes_papers(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "papers/" in writes, "Must document writing papers/"

    def test_writes_claims(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "claims/" in writes, "Must document writing claims/"

    def test_writes_graph_edges(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "edges.jsonl" in writes, "Must document writing graph/edges.jsonl"

    def test_writes_query_pack(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "context_brief.md" in writes, "Must document writing context_brief.md"

    def test_writes_gap_map(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "open_questions.md" in writes, "Must document writing open_questions.md"

    def test_writes_index(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "index.md" in writes, "Must document writing index.md"

    def test_writes_log(self, skill_text):
        writes = _extract_section(skill_text, "Writes", level=3)
        assert "log.md" in writes, "Must document writing log.md"

    def test_documents_graph_edges_created(self, skill_text):
        assert re.search(r"^###\s+Graph edges", skill_text, re.MULTILINE), \
            "Wiki Interaction must have ### Graph edges subsection"


# ── 3. Workflow steps ──────────────────────────────────────────────────


class TestWorkflow:
    """Validate workflow covers all required steps."""

    def test_workflow_contains_all_steps(self, skill_text, ingest_workflow_steps):
        workflow = _extract_section(skill_text, "Workflow", level=2)
        for step_keyword in ingest_workflow_steps:
            assert step_keyword in workflow, \
                f"Workflow missing step containing '{step_keyword}'"

    def test_has_at_least_8_steps(self, skill_text):
        workflow = _extract_section(skill_text, "Workflow", level=2)
        steps = re.findall(r"^### Step \d+", workflow, re.MULTILINE)
        assert len(steps) >= 8, f"Expected >= 8 workflow steps, found {len(steps)}"

    def test_local_pdf_flow_is_agent_first(self, skill_text):
        lowered = skill_text.lower()
        assert "filename/path arxiv" in lowered
        assert "--arxiv-id" in skill_text
        assert "authoritative" in lowered
        assert "synthetic `.tex`" in skill_text


# ── 4. Tool references ─────────────────────────────────────────────────

REQUIRED_TOOL_CALLS = [
    ("research_wiki.py slug", "Must use research_wiki.py slug for slug generation"),
    ("research_wiki.py add-edge", "Must use research_wiki.py add-edge for graph edges"),
    ("research_wiki.py rebuild-context-brief", "Must use research_wiki.py rebuild-context-brief"),
    ("research_wiki.py rebuild-open-questions", "Must use research_wiki.py rebuild-open-questions"),
    ("research_wiki.py log", "Must use research_wiki.py log for audit logging"),
    ("prepare_paper_source.py", "Must reference prepare_paper_source.py for direct local PDF normalization"),
]


class TestToolReferences:
    """Validate that SKILL.md references the correct tools and that those tools exist."""

    @pytest.mark.parametrize("tool_ref,msg", REQUIRED_TOOL_CALLS)
    def test_references_tool(self, skill_text, tool_ref, msg):
        assert tool_ref in skill_text, msg

    def test_research_wiki_tool_exists(self):
        assert (TOOLS_DIR / "research_wiki.py").exists(), \
            "tools/research_wiki.py must exist"

    def test_fetch_s2_tool_exists(self):
        assert (TOOLS_DIR / "fetch_s2.py").exists(), \
            "tools/fetch_s2.py must exist"

    def test_prepare_paper_source_tool_exists(self):
        assert (TOOLS_DIR / "prepare_paper_source.py").exists(), \
            "tools/prepare_paper_source.py must exist"

    def test_references_fetch_s2(self, skill_text):
        assert "fetch_s2.py" in skill_text, \
            "Must reference fetch_s2.py for Semantic Scholar queries"

    def test_references_fetch_deepxiv_brief(self, skill_text):
        assert "fetch_deepxiv.py brief" in skill_text, \
            "Must reference fetch_deepxiv.py brief for TLDR enrichment"

    def test_fetch_deepxiv_tool_exists(self):
        assert (TOOLS_DIR / "fetch_deepxiv.py").exists(), \
            "tools/fetch_deepxiv.py must exist"


# ── 5. Entity coverage ─────────────────────────────────────────────────

# Ingest must handle or mention these entity types
ENTITY_TYPES_IN_OUTPUT = ["papers", "concepts", "people", "claims"]
ENTITY_TYPES_IN_CROSSREF = ["concepts", "topics", "people", "claims"]


class TestEntityCoverage:
    """Validate that ingest covers all relevant entity types."""

    @pytest.mark.parametrize("entity", ENTITY_TYPES_IN_OUTPUT)
    def test_output_mentions_entity(self, skill_text, entity):
        outputs = _extract_section(skill_text, "Outputs", level=2)
        assert entity in outputs, \
            f"Outputs must mention creating/updating {entity}/ pages"

    @pytest.mark.parametrize("entity", ENTITY_TYPES_IN_CROSSREF)
    def test_crossref_handles_entity(self, skill_text, entity):
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert entity in workflow, \
            f"Workflow must handle cross-references for {entity}/"

    def test_concept_dedup_check(self, skill_text):
        """Ingest must check aliases before creating new concept pages."""
        assert "aliases" in skill_text, \
            "Must check concept aliases for semantic dedup before creating new concepts"

    def test_concept_dedup_workflow(self, skill_text):
        """Ingest Part A must include dedup step."""
        part_a = skill_text[skill_text.find("Part A"):]
        assert "去重" in part_a or "dedup" in part_a.lower() or "重复" in part_a, \
            "Part A must describe concept dedup workflow"


# ── 6. Constraints alignment with CLAUDE.md ────────────────────────────

REQUIRED_CONSTRAINTS = [
    ("raw/", "raw/"),               # raw is read-only
    ("graph/", "graph/"),           # graph only via tools
    ("双向链接", "idirectional"),   # bidirectional links (en: Bidirectional / zh: 双向链接)
    ("tex", "tex"),                 # tex priority
    ("slug", "slug"),               # slug via tool
    ("index.md", "index.md"),       # index updated immediately
    ("log.md", "log.md"),           # log append-only
    ("importance", "importance"),   # importance scoring
]


class TestConstraints:
    """Validate constraints align with product CLAUDE.md rules."""

    @pytest.mark.parametrize("zh_kw,en_kw", REQUIRED_CONSTRAINTS)
    def test_constraint_present(self, skill_text, zh_kw, en_kw):
        constraints = _extract_section(skill_text, "Constraints", level=2)
        assert zh_kw in constraints or en_kw in constraints.lower(), \
            f"Constraints must mention '{zh_kw}' or '{en_kw}'"

    def test_raw_readonly(self, skill_text):
        constraints = _extract_section(skill_text, "Constraints", level=2)
        assert "只读" in constraints or "read-only" in constraints.lower(), \
            "Must explicitly state raw/ is read-only"

    def test_init_mode_source_handoff(self, skill_text):
        lowered = skill_text.lower()
        assert "init-sources.json" in skill_text, \
            "INIT MODE must document manifest-driven source handoff"
        assert "raw/tmp/" in skill_text, \
            "INIT MODE must accept prepared local sources from raw/tmp/"
        assert "raw/discovered/" in skill_text, \
            "INIT MODE must accept introduced sources from raw/discovered/"
        assert "canonical_ingest_path" in lowered, \
            "INIT MODE must respect the handed-off canonical ingest path"

    def test_discovered_and_tmp_sources_are_not_duplicated_into_raw_papers(self, skill_text):
        assert (
            "do not duplicate it into `raw/papers/`" in skill_text
            or "不要再复制到 `raw/papers/`" in skill_text
        ), "Ingest should treat raw/discovered/ and raw/tmp/ as canonical instead of copying them into raw/papers/"

    def test_direct_arxiv_fetches_go_to_raw_discovered(self, skill_text):
        assert (
            "save the fetched source artifact under `raw/discovered/`" in skill_text
            or "保存到 `raw/discovered/` 并从那里 ingest" in skill_text
        ), "Direct arXiv ingests should store fetched sources under raw/discovered/"


# ── 7. Error handling ──────────────────────────────────────────────────

class TestErrorHandling:
    """Validate error handling covers critical failure modes."""

    def test_source_parse_failure(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "解析失败" in errors or "parse" in errors.lower() or "失败" in errors, \
            "Must handle source parsing failure"

    def test_s2_api_failure(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "S2" in errors or "Semantic Scholar" in errors, \
            "Must handle Semantic Scholar API failure"

    def test_slug_conflict(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "slug" in errors.lower() or "冲突" in errors, \
            "Must handle slug conflicts"

    def test_deepxiv_failure(self, skill_text):
        errors = _extract_section(skill_text, "Error Handling", level=2)
        assert "deepxiv" in errors.lower() or "DeepXiv" in errors, \
            "Must handle DeepXiv API unavailability with graceful fallback"


# ── 8. Cross-reference rules completeness ──────────────────────────────

class TestCrossRefRules:
    """Validate that ingest implements the cross-reference rules from CLAUDE.md."""

    def test_paper_to_concept_backlink(self, skill_text):
        """papers/A → concepts/B: concept's key_papers must be updated."""
        assert "key_papers" in skill_text, \
            "Must update concept's key_papers when paper references concept"

    def test_paper_to_people_backlink(self, skill_text):
        """papers/A → people/C: person's Key papers must be updated."""
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "Key papers" in workflow, \
            "Must update person's Key papers when paper references author"

    def test_paper_to_claim_backlink(self, skill_text):
        """papers/A → claims/D: claim's evidence must be updated."""
        workflow = _extract_section(skill_text, "Workflow", level=2)
        assert "evidence" in workflow, \
            "Must update claim's evidence when paper supports/contradicts claim"

    def test_cited_by_backfill(self, skill_text):
        """S2 citations: existing papers' cited_by must be updated."""
        assert "cited_by" in skill_text, \
            "Must backfill cited_by for existing wiki papers"


# ── 9. Consistency with product CLAUDE.md ──────────────────────────────

class TestClaudeMdConsistency:
    """Validate that skill references match the product CLAUDE.md definitions."""

    def test_skill_listed_in_claude_md(self, claude_md_text):
        assert "/ingest" in claude_md_text, \
            "Ingest skill must be listed in product CLAUDE.md skills table"

    def test_edge_types_valid(self, skill_text, claude_md_text):
        """All edge types mentioned in skill must be valid per CLAUDE.md."""
        valid_types = {
            "extends", "contradicts", "supports", "inspired_by",
            "tested_by", "invalidates", "supersedes", "addresses_gap",
            "derived_from",
        }
        # Find edge type references in add-edge calls
        edge_calls = re.findall(r"--type\s+(\w+)", skill_text)
        for etype in edge_calls:
            assert etype in valid_types, \
                f"Edge type '{etype}' not in valid set: {valid_types}"

    def test_importance_scale_documented(self, skill_text):
        """Must document the 1-5 importance scale."""
        assert "1=" in skill_text or "1-5" in skill_text, \
            "Must document importance scale"

    def test_log_format_matches(self, skill_text):
        """Log message format should match CLAUDE.md log.md format."""
        assert "ingest |" in skill_text, \
            "Log format must follow 'ingest | ...' pattern from CLAUDE.md"


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
