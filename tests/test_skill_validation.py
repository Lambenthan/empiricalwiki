"""Tests for wiki entity templates defined in CLAUDE.md.

Validates that all 8 entity types have correct YAML frontmatter templates
and required body sections as specified in the product CLAUDE.md.
"""

import re
from pathlib import Path
from typing import List, Optional

import pytest

# ── Locate product CLAUDE.md ─────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"


@pytest.fixture(scope="module")
def claude_md_text():
    assert CLAUDE_MD.exists(), f"Product CLAUDE.md not found at {CLAUDE_MD}"
    return CLAUDE_MD.read_text(encoding="utf-8")


# ── Schema definitions ───────────────────────────────────────────────────
# Each entity: (template heading pattern, required frontmatter fields, required body sections)

ENTITY_SCHEMAS = {
    "papers": {
        "heading": r"###\s+papers/\{slug\}\.md",
        "required_fields": [
            "title", "slug", "arxiv", "venue", "year", "tags",
            "importance", "date_added", "source_type", "s2_id",
            "keywords", "domain", "code_url", "cited_by",
        ],
        "required_sections": [
            "Problem", "Key idea", "Method", "Results",
            "Limitations", "Open questions", "My take", "Related",
        ],
    },
    "concepts": {
        "heading": r"###\s+concepts/\{concept-name\}\.md",
        "required_fields": [
            "title", "aliases", "tags", "maturity", "key_papers",
            "first_introduced", "date_updated", "related_concepts",
        ],
        "required_sections": [
            "Definition", "Intuition", "Formal notation", "Variants",
            "Comparison", "When to use", "Known limitations",
            "Open problems", "Key papers", "My understanding",
        ],
    },
    "topics": {
        "heading": r"###\s+topics/\{topic-name\}\.md",
        "required_fields": [
            "title", "tags", "my_involvement", "sota_updated",
            "key_venues", "related_topics", "key_people",
        ],
        "required_sections": [
            "Overview", "Timeline", "Seminal works", "SOTA tracker",
            "Open problems", "My position", "Research gaps", "Key people",
        ],
    },
    "people": {
        "heading": r"###\s+people/\{firstname-lastname\}\.md",
        "required_fields": [
            "name", "affiliation", "tags", "homepage",
            "scholar", "date_updated",
        ],
        "required_sections": [
            "Research areas", "Key papers", "Recent work",
            "Collaborators", "My notes",
        ],
    },
    "ideas": {
        "heading": r"###\s+ideas/\{idea-slug\}\.md",
        "required_fields": [
            "title", "slug", "status", "origin", "origin_gaps",
            "tags", "domain", "priority", "pilot_result",
            "failure_reason", "linked_experiments",
            "date_proposed", "date_resolved",
        ],
        "required_sections": [
            "Motivation", "Hypothesis", "Approach sketch",
            "Expected outcome", "Risks", "Pilot results", "Lessons learned",
        ],
    },
    "experiments": {
        "heading": r"###\s+experiments/\{experiment-slug\}\.md",
        "required_fields": [
            "title", "slug", "status", "target_claim", "hypothesis",
            "tags", "domain", "setup", "metrics", "baseline",
            "outcome", "key_result", "linked_idea",
            "date_planned", "date_completed", "run_log",
            "started", "estimated_hours", "remote",
        ],
        "required_sections": [
            "Objective", "Setup", "Procedure", "Results",
            "Analysis", "Claim updates", "Follow-up",
        ],
    },
    "claims": {
        "heading": r"###\s+claims/\{claim-slug\}\.md",
        "required_fields": [
            "title", "slug", "status", "confidence", "tags",
            "domain", "source_papers", "evidence", "conditions",
            "date_proposed", "date_updated",
        ],
        "required_sections": [
            "Statement", "Evidence summary", "Conditions and scope",
            "Counter-evidence", "Linked ideas", "Open questions",
        ],
    },
    "Summary": {
        "heading": r"###\s+Summary/\{area-name\}\.md",
        "required_fields": [
            "title", "scope", "key_topics", "paper_count", "date_updated",
        ],
        "required_sections": [
            "Overview", "Core areas", "Evolution",
            "Current frontiers", "Key references", "Related",
        ],
    },
    "foundations": {
        "heading": r"###\s+foundations/\{slug\}\.md",
        "required_fields": [
            "title", "slug", "domain", "status", "aliases",
            "first_introduced", "date_updated", "source_url",
        ],
        "required_sections": [
            "Definition", "Intuition", "Formal notation", "Key variants",
            "Known limitations", "Open problems", "Relevance to active research",
        ],
    },
}

# ── Helpers ───────────────────────────────────────────────────────────────


def _extract_template_block(text: str, heading_pattern: str) -> Optional[str]:
    """Extract the text block from a heading to the next same-or-higher level heading or top-level separator."""
    match = re.search(heading_pattern, text)
    if not match:
        return None
    start = match.start()
    rest = text[match.end():]
    # Find next ### heading (same level) or ## heading (higher level) — but not inside code blocks
    # Simple approach: find next "\n### " or "\n## " that is NOT inside a ``` block
    in_code = False
    lines = rest.split("\n")
    end_offset = len(rest)
    offset = 0
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code and (re.match(r"###\s", line) or re.match(r"##\s[^#]", line)):
            end_offset = offset
            break
        offset += len(line) + 1  # +1 for the \n
    return text[start:match.end() + end_offset]


def _extract_yaml_fields(block: str) -> List[str]:
    """Extract top-level field names from a YAML frontmatter code block."""
    yaml_match = re.search(r"```yaml\s*\n---\n(.*?)\n---\s*\n```", block, re.DOTALL)
    if not yaml_match:
        return []
    yaml_text = yaml_match.group(1)
    fields = []
    for line in yaml_text.split("\n"):
        # Top-level field: starts at column 0 with "key:" or "key: value"
        m = re.match(r"^([a-z_][a-z0-9_]*):", line)
        if m:
            fields.append(m.group(1))
    return fields


def _extract_body_sections(block: str) -> List[str]:
    """Extract section names from the body sections line (supports both 正文： and Body sections:)."""
    body_match = re.search(r"(?:正文|Body sections)：?(.*)", block)
    if not body_match:
        return []
    body_line = body_match.group(1)
    return re.findall(r"##\s+([^`/]+?)(?:\s*`|$)", body_line)


# ── Tests: CLAUDE.md exists and has expected structure ────────────────────


class TestClaudeMdStructure:
    def test_claude_md_exists(self):
        assert CLAUDE_MD.exists()

    def test_has_entity_table(self, claude_md_text, claude_md_markers):
        assert claude_md_markers["entity_section"] in claude_md_text

    def test_has_all_entity_headings(self, claude_md_text):
        for entity, schema in ENTITY_SCHEMAS.items():
            assert re.search(schema["heading"], claude_md_text), (
                f"Missing template heading for entity: {entity}"
            )

    def test_has_cross_reference_rules(self, claude_md_text):
        assert "Cross Reference" in claude_md_text or "Cross-Reference" in claude_md_text

    def test_has_graph_section(self, claude_md_text, claude_md_markers):
        assert claude_md_markers["graph_section"] in claude_md_text

    def test_has_index_format(self, claude_md_text, claude_md_markers):
        assert claude_md_markers["index_format_assert"] in claude_md_text

    def test_has_constraints(self, claude_md_text, claude_md_markers):
        assert claude_md_markers["constraints"] in claude_md_text


# ── Tests: YAML frontmatter fields ───────────────────────────────────────


class TestFrontmatterFields:
    """Validate that each entity template has all required YAML frontmatter fields."""

    @pytest.fixture(scope="class")
    def template_blocks(self, claude_md_text):
        blocks = {}
        for entity, schema in ENTITY_SCHEMAS.items():
            block = _extract_template_block(claude_md_text, schema["heading"])
            assert block is not None, f"Could not extract template block for {entity}"
            blocks[entity] = block
        return blocks

    @pytest.mark.parametrize("entity", list(ENTITY_SCHEMAS.keys()))
    def test_has_yaml_block(self, template_blocks, entity):
        block = template_blocks[entity]
        assert re.search(r"```yaml\s*\n---", block), (
            f"Entity {entity} template missing YAML frontmatter code block"
        )

    @pytest.mark.parametrize("entity", list(ENTITY_SCHEMAS.keys()))
    def test_required_fields_present(self, template_blocks, entity):
        block = template_blocks[entity]
        found_fields = _extract_yaml_fields(block)
        for field in ENTITY_SCHEMAS[entity]["required_fields"]:
            assert field in found_fields, (
                f"Entity {entity}: missing required field '{field}'. "
                f"Found: {found_fields}"
            )

    @pytest.mark.parametrize("entity", list(ENTITY_SCHEMAS.keys()))
    def test_no_unknown_top_level_fields(self, template_blocks, entity):
        """Warn if there are fields in template not in our schema (not a failure, just info)."""
        block = template_blocks[entity]
        found_fields = _extract_yaml_fields(block)
        expected = set(ENTITY_SCHEMAS[entity]["required_fields"])
        extra = set(found_fields) - expected
        # This is not an error — just a check that schema stays in sync
        # If you add a field to the template, add it to ENTITY_SCHEMAS too
        assert not extra, (
            f"Entity {entity}: fields in template but not in test schema: {extra}. "
            f"Update ENTITY_SCHEMAS in test_skill_validation.py."
        )


# ── Tests: body sections ─────────────────────────────────────────────────


class TestBodySections:
    """Validate that each entity template specifies all required body sections."""

    @pytest.fixture(scope="class")
    def template_blocks(self, claude_md_text):
        blocks = {}
        for entity, schema in ENTITY_SCHEMAS.items():
            block = _extract_template_block(claude_md_text, schema["heading"])
            assert block is not None, f"Could not extract template block for {entity}"
            blocks[entity] = block
        return blocks

    @pytest.mark.parametrize("entity", list(ENTITY_SCHEMAS.keys()))
    def test_has_body_line(self, template_blocks, entity, claude_md_markers):
        block = template_blocks[entity]
        label = claude_md_markers["body_label"]
        assert label in block, (
            f"Entity {entity} template missing body sections line (expected '{label}')"
        )

    @pytest.mark.parametrize("entity", list(ENTITY_SCHEMAS.keys()))
    def test_required_sections_present(self, template_blocks, entity):
        block = template_blocks[entity]
        found_sections = _extract_body_sections(block)
        for section in ENTITY_SCHEMAS[entity]["required_sections"]:
            assert section in found_sections, (
                f"Entity {entity}: missing required body section '## {section}'. "
                f"Found: {found_sections}"
            )


# ── Tests: field value constraints ────────────────────────────────────────


class TestFieldConstraints:
    """Validate enum/range constraints documented in templates."""

    def test_paper_importance_range(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["papers"]["heading"])
        assert block and "# 1-5" in block

    def test_concept_maturity_values(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["concepts"]["heading"])
        assert block and "stable" in block and "active" in block and "emerging" in block and "deprecated" in block

    def test_idea_status_values(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["ideas"]["heading"])
        assert block
        for status in ["proposed", "in_progress", "tested", "validated", "failed"]:
            assert status in block, f"ideas template missing status value: {status}"

    def test_experiment_status_values(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["experiments"]["heading"])
        assert block
        for status in ["planned", "running", "completed", "abandoned"]:
            assert status in block, f"experiments template missing status value: {status}"

    def test_experiment_outcome_values(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["experiments"]["heading"])
        assert block
        for outcome in ["succeeded", "failed", "inconclusive"]:
            assert outcome in block, f"experiments template missing outcome value: {outcome}"

    def test_claim_status_values(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["claims"]["heading"])
        assert block
        for status in ["proposed", "weakly_supported", "supported", "challenged", "deprecated"]:
            assert status in block, f"claims template missing status value: {status}"

    def test_claim_confidence_range(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["claims"]["heading"])
        assert block and "0.0-1.0" in block

    def test_claim_evidence_types(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["claims"]["heading"])
        assert block
        for etype in ["supports", "contradicts", "tested_by", "invalidates"]:
            assert etype in block, f"claims template missing evidence type: {etype}"

    def test_claim_evidence_strength(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["claims"]["heading"])
        assert block
        for strength in ["weak", "moderate", "strong"]:
            assert strength in block, f"claims template missing evidence strength: {strength}"

    def test_idea_priority_range(self, claude_md_text):
        block = _extract_template_block(claude_md_text, ENTITY_SCHEMAS["ideas"]["heading"])
        assert block and "# 1-5" in block


# ── Tests: cross-reference rules ──────────────────────────────────────────


class TestCrossReferenceRules:
    """Validate that new entity types have cross-reference rules."""

    def test_ideas_cross_ref(self, claude_md_text):
        assert "ideas/I" in claude_md_text and "origin_gaps" in claude_md_text

    def test_experiments_cross_ref(self, claude_md_text):
        assert "experiments/E" in claude_md_text and "target_claim" in claude_md_text

    def test_claims_cross_ref(self, claude_md_text):
        assert "claims/C" in claude_md_text and "source_papers" in claude_md_text


# ── Tests: index.md format ────────────────────────────────────────────────


class TestIndexFormat:
    """Validate that index.md format covers all 8 entity types."""

    @pytest.mark.parametrize("category", [
        "papers", "concepts", "topics", "people",
        "ideas", "experiments", "claims",
    ])
    def test_index_has_category(self, claude_md_text, category, claude_md_markers):
        split_key = claude_md_markers["index_format_split"]
        assert split_key in claude_md_text, f"index.md format section not found (expected '{split_key}')"
        idx_section = claude_md_text.split(split_key)[1].split("\n---")[0]
        assert f"{category}:" in idx_section, (
            f"index.md format missing category: {category}"
        )


# ── Tests: graph section ─────────────────────────────────────────────────


class TestGraphSection:
    """Validate graph/ documentation is present and complete."""

    def test_edges_jsonl_documented(self, claude_md_text):
        assert "edges.jsonl" in claude_md_text

    def test_query_pack_documented(self, claude_md_text):
        assert "context_brief.md" in claude_md_text

    def test_gap_map_documented(self, claude_md_text):
        assert "open_questions.md" in claude_md_text

    def test_edge_types_documented(self, claude_md_text):
        for etype in ["extends", "contradicts", "supports", "inspired_by",
                       "tested_by", "invalidates", "supersedes", "addresses_gap",
                       "derived_from"]:
            assert etype in claude_md_text, f"Edge type {etype} not documented"

    def test_graph_auto_generated_warning(self, claude_md_text, claude_md_markers):
        assert claude_md_markers["graph_auto_generated"] in claude_md_text
        assert claude_md_markers["graph_no_edit"] in claude_md_text
