"""Single source of truth for ΩmegaWiki entity schemas.

Centralizes the constants that lint.py and research_wiki.py both need:
entity directories, valid edge types, required frontmatter fields per
entity, valid enum values, and safe defaults for `lint --fix`.

If you change anything here, also update the matching template comments
in `i18n/en/CLAUDE.md` and `i18n/zh/CLAUDE.md` (and re-run setup.sh).
The Cross-Reference table in those files is the human-facing spec; this
file is the machine-facing copy that the tools actually consume.
"""

from __future__ import annotations

# All 9 entity directories (Summary lives at the wiki root, not under entities,
# but lint treats it as an entity directory because it has frontmatter pages).
ENTITY_DIRS = [
    "papers", "concepts", "topics", "people",
    "ideas", "experiments", "claims", "Summary",
    "foundations",
]

# Typed graph edges (graph/edges.jsonl). New types must be added here AND
# documented in CLAUDE.md's graph/ section.
VALID_EDGE_TYPES = {
    "extends", "contradicts", "supports", "inspired_by",
    "tested_by", "invalidates", "supersedes", "addresses_gap",
    "derived_from",
}

# Required frontmatter fields per entity type (lint.py reports a 🔴 if missing).
REQUIRED_FIELDS = {
    "papers": ["title", "slug", "tags", "importance"],
    "concepts": ["title", "tags", "maturity", "key_papers"],
    "topics": ["title", "tags"],
    "people": ["name", "tags"],
    "Summary": ["title", "scope", "key_topics"],
    "ideas": ["title", "slug", "status", "origin", "tags", "priority"],
    "experiments": ["title", "slug", "status", "target_claim", "hypothesis", "tags"],
    "claims": ["title", "slug", "status", "confidence", "tags", "source_papers", "evidence"],
    "foundations": ["title", "slug", "domain", "status"],
}

# Valid enum values per entity-qualified field. Format: "{entity}.{field}".
VALID_VALUES = {
    "papers.importance": {"1", "2", "3", "4", "5"},
    "concepts.maturity": {"stable", "active", "emerging", "deprecated"},
    "ideas.status": {"proposed", "in_progress", "tested", "validated", "failed"},
    "ideas.priority": {"1", "2", "3", "4", "5"},
    "experiments.status": {"planned", "running", "completed", "abandoned"},
    "experiments.outcome": {"succeeded", "failed", "inconclusive", ""},
    "claims.status": {"proposed", "weakly_supported", "supported", "challenged", "deprecated"},
    "foundations.status": {"mainstream", "historical"},
}

# Safe defaults for `lint --fix`. Only fields where a neutral default is
# reasonable. Note: `importance: "3"` and `confidence: "0.5"` are biased
# defaults for bulk-ingested wikis (3=field-standard, 0.5=coin-flip), but
# fixing that is a separate concern from centralizing the schema — see
# devlog for the discussion. Preserved as-is here.
FIELD_DEFAULTS = {
    "papers": {"tags": "[]", "importance": "3"},
    "concepts": {"tags": "[]", "maturity": "active", "key_papers": "[]"},
    "topics": {"tags": "[]"},
    "people": {"tags": "[]"},
    "Summary": {"key_topics": "[]"},
    "ideas": {"tags": "[]", "priority": "3"},
    "experiments": {"tags": "[]"},
    "claims": {"tags": "[]", "confidence": "0.5"},
    "foundations": {"status": "mainstream"},
}
