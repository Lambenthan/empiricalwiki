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

EDGE_CONFIDENCE_VALUES = {"high", "medium", "low"}

CITATION_EDGE_TYPES = {"cites"}
CITATION_SOURCES = {"semantic_scholar", "parsed_bib", "manual"}

ANY_ENDPOINT = "*"
DIRECTION_DIRECTED = "directed"
DIRECTION_SYMMETRIC = "symmetric"
CONFIDENCE_REQUIRED = "required"
CONFIDENCE_NONE = "none"

# Single registry for typed semantic graph edges (graph/edges.jsonl).
# Attributes here are the source of truth; compatibility constants below are
# derived views for older tool code and CLI help.
EDGE_TYPE_SPECS: dict[str, dict[str, str]] = {
    # /ingest paper-paper semantic judgments.
    "same_problem_as": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_SYMMETRIC,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "similar_method_to": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_SYMMETRIC,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "complementary_to": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_SYMMETRIC,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "builds_on": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "compares_against": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "improves_on": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "challenges": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "surveys": {
        "from_kind": "papers",
        "to_kind": "papers",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },

    # /ingest paper-concept semantic judgments.
    "introduces_concept": {
        "from_kind": "papers",
        "to_kind": "concepts",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "uses_concept": {
        "from_kind": "papers",
        "to_kind": "concepts",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "extends_concept": {
        "from_kind": "papers",
        "to_kind": "concepts",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },
    "critiques_concept": {
        "from_kind": "papers",
        "to_kind": "concepts",
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_REQUIRED,
        "workflow": "ingest",
    },

    # Other semantic/provenance workflows. Endpoint constraints stay broad here
    # because older skills use these across claims, ideas, experiments, papers,
    # concepts, outputs, and foundations.
    "supports": {
        "from_kind": ANY_ENDPOINT,
        "to_kind": ANY_ENDPOINT,
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_NONE,
        "workflow": "claim_evidence",
    },
    "contradicts": {
        "from_kind": ANY_ENDPOINT,
        "to_kind": ANY_ENDPOINT,
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_NONE,
        "workflow": "claim_evidence",
    },
    "tested_by": {
        "from_kind": ANY_ENDPOINT,
        "to_kind": ANY_ENDPOINT,
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_NONE,
        "workflow": "experiment",
    },
    "invalidates": {
        "from_kind": ANY_ENDPOINT,
        "to_kind": ANY_ENDPOINT,
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_NONE,
        "workflow": "experiment",
    },
    "addresses_gap": {
        "from_kind": ANY_ENDPOINT,
        "to_kind": ANY_ENDPOINT,
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_NONE,
        "workflow": "idea",
    },
    "derived_from": {
        "from_kind": ANY_ENDPOINT,
        "to_kind": ANY_ENDPOINT,
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_NONE,
        "workflow": "provenance",
    },
    "inspired_by": {
        "from_kind": ANY_ENDPOINT,
        "to_kind": ANY_ENDPOINT,
        "direction": DIRECTION_DIRECTED,
        "confidence": CONFIDENCE_NONE,
        "workflow": "idea",
    },
}

# Accepted only for backwards compatibility; lint reports endpoint-specific
# migration warnings when these appear on old /ingest-shaped endpoints.
LEGACY_EDGE_TYPES = {"extends", "supersedes"}
LEGACY_PAPER_PAPER_EDGE_TYPES = LEGACY_EDGE_TYPES | {"inspired_by", "contradicts"}
LEGACY_PAPER_CONCEPT_EDGE_TYPES = {"supports", "extends"}


def _spec_matches(spec: dict[str, str], key: str, value: str | None) -> bool:
    return value is None or spec.get(key) == value


def edge_types_matching(*, from_kind: str | None = None,
                        to_kind: str | None = None,
                        direction: str | None = None,
                        confidence: str | None = None,
                        workflow: str | None = None) -> set[str]:
    """Return edge types whose registry metadata matches all provided filters."""
    matches: set[str] = set()
    for edge_type, spec in EDGE_TYPE_SPECS.items():
        if not _spec_matches(spec, "from_kind", from_kind):
            continue
        if not _spec_matches(spec, "to_kind", to_kind):
            continue
        if not _spec_matches(spec, "direction", direction):
            continue
        if not _spec_matches(spec, "confidence", confidence):
            continue
        if not _spec_matches(spec, "workflow", workflow):
            continue
        matches.add(edge_type)
    return matches


def edge_type_spec(edge_type: str) -> dict[str, str] | None:
    """Return registry metadata for a semantic edge type, or None if unknown."""
    return EDGE_TYPE_SPECS.get(edge_type)


def edge_is_symmetric(edge_type: str) -> bool:
    spec = edge_type_spec(edge_type)
    return bool(spec and spec.get("direction") == DIRECTION_SYMMETRIC)


def edge_requires_confidence(edge_type: str) -> bool:
    spec = edge_type_spec(edge_type)
    return bool(spec and spec.get("confidence") == CONFIDENCE_REQUIRED)


def edge_expected_endpoint(edge_type: str, endpoint: str) -> str:
    spec = edge_type_spec(edge_type)
    if not spec:
        return ANY_ENDPOINT
    return spec.get(f"{endpoint}_kind", ANY_ENDPOINT)


def edge_endpoint_matches(edge_type: str, from_kind: str, to_kind: str) -> bool:
    spec = edge_type_spec(edge_type)
    if not spec:
        return True
    expected_from = spec.get("from_kind", ANY_ENDPOINT)
    expected_to = spec.get("to_kind", ANY_ENDPOINT)
    from_ok = expected_from == ANY_ENDPOINT or expected_from == from_kind
    to_ok = expected_to == ANY_ENDPOINT or expected_to == to_kind
    return from_ok and to_ok


def edge_is_legacy_for_endpoint(edge_type: str, from_kind: str,
                                to_kind: str) -> bool:
    """Return True for legacy edge types on endpoint pairs /ingest no longer writes."""
    if from_kind == "papers" and to_kind == "papers":
        return edge_type in LEGACY_PAPER_PAPER_EDGE_TYPES
    if from_kind == "papers" and to_kind == "concepts":
        return edge_type in LEGACY_PAPER_CONCEPT_EDGE_TYPES
    return False


def edge_legacy_replacement_message(edge_type: str, from_kind: str,
                                    to_kind: str) -> str:
    """Human-facing migration hint for legacy edge endpoint pairs."""
    if from_kind == "papers" and to_kind == "papers":
        return f"Legacy paper-paper edge {edge_type!r}; use the new paper relation types"
    if from_kind == "papers" and to_kind == "concepts":
        return (
            f"Legacy paper-concept edge {edge_type!r}; use introduces_concept, "
            "uses_concept, extends_concept, or critiques_concept"
        )
    return f"Legacy edge {edge_type!r}"


# Derived views for existing tool call sites. These are not independent
# categories; each is computed from EDGE_TYPE_SPECS above.
PAPER_PAPER_EDGE_TYPES = edge_types_matching(
    from_kind="papers", to_kind="papers", workflow="ingest"
)
PAPER_CONCEPT_EDGE_TYPES = edge_types_matching(
    from_kind="papers", to_kind="concepts", workflow="ingest"
)
SYMMETRIC_EDGE_TYPES = edge_types_matching(direction=DIRECTION_SYMMETRIC)
CONFIDENCE_REQUIRED_EDGE_TYPES = edge_types_matching(confidence=CONFIDENCE_REQUIRED)
VALID_EDGE_TYPES = set(EDGE_TYPE_SPECS) | LEGACY_EDGE_TYPES

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
