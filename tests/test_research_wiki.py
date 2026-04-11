"""Tests for tools/research_wiki.py — Wiki Knowledge Engine."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Adjust path so we can import the module directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import research_wiki as rw


# ── Helper fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def wiki(tmp_path):
    """Create and return an initialized wiki directory."""
    w = tmp_path / "wiki"
    rw.init_wiki(str(w))
    return w


def _write_page(wiki, entity_type, slug, frontmatter_str, body=""):
    """Helper to write a wiki page with frontmatter and optional body."""
    p = wiki / entity_type / f"{slug}.md"
    p.write_text(f"---\n{frontmatter_str}\n---\n{body}\n", encoding="utf-8")
    return p


# ── slugify ───────────────────────────────────────────────────────────────

class TestSlugify:
    def test_basic_title(self):
        assert rw.slugify("Flash Attention") == "flash-attention"

    def test_strips_stop_words(self):
        slug = rw.slugify("Attention Is All You Need")
        assert "is" not in slug.split("-")
        assert "all" in slug.split("-")

    def test_lora_title(self):
        slug = rw.slugify("LoRA: Low-Rank Adaptation of Large Language Models")
        assert slug.startswith("lora")
        assert "low" in slug.split("-")
        assert "rank" in slug.split("-")

    def test_empty_title_fallback(self):
        assert rw.slugify("") == "untitled"

    def test_only_stop_words(self):
        slug = rw.slugify("a the of")
        assert slug  # should not be empty

    def test_special_characters_stripped(self):
        slug = rw.slugify("GPT-4: A New Era?")
        assert "?" not in slug
        assert ":" not in slug

    def test_max_six_keywords(self):
        slug = rw.slugify("one two three four five six seven eight nine ten")
        assert len(slug.split("-")) <= 6

    def test_kebab_case_format(self):
        slug = rw.slugify("Some Random Title Here")
        assert "_" not in slug
        assert " " not in slug
        assert slug == slug.lower()


# ── init_wiki ─────────────────────────────────────────────────────────────

class TestInitWiki:
    def test_creates_all_dirs(self, tmp_path):
        wiki = tmp_path / "wiki"
        rw.init_wiki(str(wiki))
        for d in rw.ENTITY_DIRS:
            assert (wiki / d).is_dir(), f"Missing dir: {d}"
        assert (wiki / "graph").is_dir()
        assert (wiki / "outputs").is_dir()

    def test_creates_seed_files(self, tmp_path):
        wiki = tmp_path / "wiki"
        rw.init_wiki(str(wiki))
        assert (wiki / "index.md").exists()
        assert (wiki / "log.md").exists()
        assert (wiki / "graph" / "edges.jsonl").exists()
        assert (wiki / "graph" / "context_brief.md").exists()
        assert (wiki / "graph" / "open_questions.md").exists()

    def test_index_has_all_entity_sections(self, tmp_path):
        wiki = tmp_path / "wiki"
        rw.init_wiki(str(wiki))
        content = (wiki / "index.md").read_text()
        for entity in rw.ENTITY_DIRS:
            assert f"{entity}:" in content

    def test_idempotent(self, tmp_path):
        wiki = tmp_path / "wiki"
        rw.init_wiki(str(wiki))
        (wiki / "index.md").write_text("custom content")
        rw.init_wiki(str(wiki))
        assert (wiki / "index.md").read_text() == "custom content"

    def test_log_entry_written(self, tmp_path):
        """init_wiki must append exactly one `init | wiki initialized` line to log.md.

        /init SKILL.md Step 1 deliberately does NOT call `log` manually and relies
        on this internal append — if this test breaks, revisit init/SKILL.md Step 1.
        """
        wiki = tmp_path / "wiki"
        rw.init_wiki(str(wiki))
        log = (wiki / "log.md").read_text()
        assert "init | wiki initialized" in log
        # Exactly one init line — guards against accidental double-logging.
        assert log.count("init | wiki initialized") == 1


# ── add_edge ──────────────────────────────────────────────────────────────

class TestAddEdge:
    def test_adds_edge(self, wiki):
        rw.add_edge(str(wiki), "paper-a", "concept-b", "supports", "Fig 3")
        edges = rw.load_edges(str(wiki))
        assert len(edges) == 1
        e = edges[0]
        assert e["from"] == "paper-a"
        assert e["to"] == "concept-b"
        assert e["type"] == "supports"
        assert e["evidence"] == "Fig 3"
        assert "date" in e

    def test_dedup(self, wiki):
        rw.add_edge(str(wiki), "a", "b", "extends")
        rw.add_edge(str(wiki), "a", "b", "extends")
        assert len(rw.load_edges(str(wiki))) == 1

    def test_different_type_not_deduped(self, wiki):
        rw.add_edge(str(wiki), "a", "b", "extends")
        rw.add_edge(str(wiki), "a", "b", "contradicts")
        assert len(rw.load_edges(str(wiki))) == 2

    def test_invalid_type_exits(self, wiki):
        with pytest.raises(SystemExit):
            rw.add_edge(str(wiki), "a", "b", "nonsense")

    def test_all_valid_types_accepted(self, wiki):
        for i, t in enumerate(sorted(rw.VALID_EDGE_TYPES)):
            rw.add_edge(str(wiki), f"a{i}", f"b{i}", t)
        assert len(rw.load_edges(str(wiki))) == len(rw.VALID_EDGE_TYPES)

    def test_entity_validation_warns(self, wiki, capsys):
        """add-edge with nonexistent entities should still succeed but warn."""
        rw.add_edge(str(wiki), "papers/nonexistent", "claims/missing", "supports")
        edges = rw.load_edges(str(wiki))
        assert len(edges) == 1
        out = json.loads(capsys.readouterr().out.strip().split("\n")[-1])
        assert out["status"] == "ok"
        assert "warnings" in out
        assert len(out["warnings"]) == 2

    def test_entity_validation_no_warn_for_existing(self, wiki, capsys):
        _write_page(wiki, "papers", "lora", 'title: "LoRA"')
        _write_page(wiki, "claims", "rank", 'title: "Rank"')
        rw.add_edge(str(wiki), "papers/lora", "claims/rank", "supports")
        out = json.loads(capsys.readouterr().out.strip().split("\n")[-1])
        assert out["status"] == "ok"
        assert "warnings" not in out or out["warnings"] == []


# ── load_edges ────────────────────────────────────────────────────────────

class TestLoadEdges:
    def test_empty_file(self, wiki):
        assert rw.load_edges(str(wiki)) == []

    def test_handles_malformed_lines(self, wiki):
        edges_path = wiki / "graph" / "edges.jsonl"
        edges_path.write_text('{"from":"a","to":"b","type":"extends"}\nBADLINE\n')
        edges = rw.load_edges(str(wiki))
        assert len(edges) == 1

    def test_nonexistent_file(self, tmp_path):
        assert rw.load_edges(str(tmp_path / "nope")) == []


# ── rebuild_open_questions ───────────────────────────────────────────────────────

class TestRebuildGapMap:
    def test_empty_wiki(self, wiki):
        rw.rebuild_open_questions(str(wiki))
        content = (wiki / "graph" / "open_questions.md").read_text()
        assert "No gaps" in content

    def test_collects_from_papers(self, wiki):
        _write_page(wiki, "papers", "test-paper", 'title: Test',
                     "\n## Open questions\n\n- Why does X happen?\n- Is Y possible?\n\n## Results\n\nStuff.")
        rw.rebuild_open_questions(str(wiki))
        content = (wiki / "graph" / "open_questions.md").read_text()
        assert "Why does X happen?" in content
        assert "paper/test-paper" in content

    def test_collects_from_claims(self, wiki):
        _write_page(wiki, "claims", "claim-x",
                     'title: X is better than Y\nstatus: proposed')
        rw.rebuild_open_questions(str(wiki))
        content = (wiki / "graph" / "open_questions.md").read_text()
        assert "X is better than Y" in content

    def test_skips_supported_claims(self, wiki):
        _write_page(wiki, "claims", "solid", 'title: Solid claim\nstatus: supported')
        rw.rebuild_open_questions(str(wiki))
        content = (wiki / "graph" / "open_questions.md").read_text()
        assert "Solid claim" not in content


# ── rebuild_context_brief (alias for compile-context --for general) ──────────

class TestRebuildQueryPack:
    def test_empty_wiki(self, wiki):
        rw.rebuild_context_brief(str(wiki))
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert "Query Pack" in content

    def test_includes_papers(self, wiki):
        _write_page(wiki, "papers", "lora", 'title: LoRA\nimportance: 5\ndomain: NLP')
        rw.rebuild_context_brief(str(wiki))
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert "LoRA" in content
        assert "Papers" in content

    def test_respects_max_chars(self, wiki):
        for i in range(50):
            _write_page(wiki, "papers", f"paper-{i}",
                         f'title: Paper number {i} with a long title for padding\nimportance: 3')
        rw.rebuild_context_brief(str(wiki), max_chars=500)
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert len(content) <= 550

    def test_includes_edges(self, wiki):
        rw.add_edge(str(wiki), "paper-a", "concept-b", "supports")
        rw.rebuild_context_brief(str(wiki))
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert "paper-a" in content


# ── get_stats ─────────────────────────────────────────────────────────────

class TestGetStats:
    def test_empty_wiki(self, wiki):
        stats = rw.get_stats(str(wiki))
        assert stats["papers"] == 0
        assert stats["edges"] == 0

    def test_counts_files(self, wiki):
        _write_page(wiki, "papers", "a", 'title: A')
        _write_page(wiki, "papers", "b", 'title: B')
        _write_page(wiki, "concepts", "c", 'title: C')
        stats = rw.get_stats(str(wiki))
        assert stats["papers"] == 2
        assert stats["concepts"] == 1

    def test_counts_claim_statuses(self, wiki):
        _write_page(wiki, "claims", "x", 'title: X\nstatus: supported')
        _write_page(wiki, "claims", "y", 'title: Y\nstatus: challenged')
        _write_page(wiki, "claims", "z", 'title: Z\nstatus: proposed')
        stats = rw.get_stats(str(wiki))
        assert stats["claims"] == 3
        assert stats["claims_supported"] == 1
        assert stats["claims_challenged"] == 1

    def test_json_output(self, wiki, capsys):
        capsys.readouterr()
        rw.get_stats(str(wiki), as_json=True)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "papers" in data


# ── get_maturity ─────────────────────────────────────────────────────────

class TestGetMaturity:
    def test_empty_wiki_is_cold(self, wiki):
        result = rw.get_maturity(str(wiki))
        assert result["level"] == "cold"
        assert result["coverage_score"] == 0.0
        assert result["papers"] == 0

    def test_few_papers_still_cold(self, wiki):
        for i in range(3):
            _write_page(wiki, "papers", f"p{i}", f"title: P{i}")
        for i in range(5):
            _write_page(wiki, "claims", f"c{i}", f"title: C{i}\nstatus: proposed")
        result = rw.get_maturity(str(wiki))
        assert result["level"] == "cold"

    def test_warm_threshold(self, wiki):
        for i in range(5):
            _write_page(wiki, "papers", f"p{i}", f"title: P{i}")
        for i in range(10):
            _write_page(wiki, "claims", f"c{i}", f"title: C{i}\nstatus: proposed")
        result = rw.get_maturity(str(wiki))
        assert result["level"] == "warm"

    def test_warm_exact_boundary(self, wiki):
        for i in range(19):
            _write_page(wiki, "papers", f"p{i}", f"title: P{i}")
        for i in range(39):
            _write_page(wiki, "claims", f"c{i}", f"title: C{i}\nstatus: proposed")
        result = rw.get_maturity(str(wiki))
        assert result["level"] == "warm"

    def test_hot_requires_experiment_evidence(self, wiki):
        for i in range(20):
            _write_page(wiki, "papers", f"p{i}", f"title: P{i}")
        for i in range(40):
            _write_page(wiki, "claims", f"c{i}", f"title: C{i}\nstatus: proposed")
        result = rw.get_maturity(str(wiki))
        # 20 papers + 40 claims but no experiment evidence → still warm
        assert result["level"] == "warm"
        assert result["has_experiment_evidence"] is False

    def test_hot_with_experiment_evidence(self, wiki):
        for i in range(20):
            _write_page(wiki, "papers", f"p{i}", f"title: P{i}")
        for i in range(40):
            _write_page(wiki, "claims", f"c{i}", f"title: C{i}\nstatus: proposed")
        _write_page(wiki, "experiments", "exp1",
                    "title: E1\nstatus: completed\noutcome: succeeded")
        rw.add_edge(str(wiki), "experiments/exp1", "claims/c0",
                    "supports", "test evidence")
        result = rw.get_maturity(str(wiki))
        assert result["level"] == "hot"
        assert result["has_experiment_evidence"] is True
        assert result["experiments_completed"] >= 1

    def test_graph_density_positive(self, wiki):
        _write_page(wiki, "papers", "a", "title: A")
        _write_page(wiki, "papers", "b", "title: B")
        rw.add_edge(str(wiki), "papers/a", "papers/b", "extends", "test")
        result = rw.get_maturity(str(wiki))
        assert result["graph_density"] > 0

    def test_graph_density_empty(self, wiki):
        result = rw.get_maturity(str(wiki))
        assert result["graph_density"] == 0.0

    def test_coverage_score_range(self, wiki):
        # Empty → 0
        result = rw.get_maturity(str(wiki))
        assert 0.0 <= result["coverage_score"] <= 1.0
        # Add a bunch of stuff → should be > 0 but <= 1.0
        for i in range(30):
            _write_page(wiki, "papers", f"p{i}", f"title: P{i}")
        for i in range(50):
            _write_page(wiki, "claims", f"c{i}", f"title: C{i}\nstatus: proposed")
        result = rw.get_maturity(str(wiki))
        assert 0.0 < result["coverage_score"] <= 1.0

    def test_json_output_keys(self, wiki, capsys):
        capsys.readouterr()
        rw.get_maturity(str(wiki), as_json=True)
        out = capsys.readouterr().out
        data = json.loads(out)
        expected_keys = {
            "level", "papers", "claims", "experiments_completed",
            "ideas_total", "ideas_failed", "edges", "graph_density",
            "coverage_score", "has_experiment_evidence",
        }
        assert expected_keys == set(data.keys())

    def test_cli_integration(self, wiki):
        tool_path = Path(__file__).resolve().parent.parent / "tools" / "research_wiki.py"
        result = subprocess.run(
            [sys.executable, str(tool_path), "maturity", str(wiki), "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["level"] == "cold"


# ── append_log ────────────────────────────────────────────────────────────

class TestAppendLog:
    def test_appends_entry(self, wiki):
        rw.append_log(str(wiki), "ingest | added papers/lora")
        log = (wiki / "log.md").read_text()
        assert "ingest | added papers/lora" in log

    def test_creates_log_if_missing(self, tmp_path):
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        rw.append_log(str(wiki), "first entry")
        assert (wiki / "log.md").exists()
        assert "first entry" in (wiki / "log.md").read_text()

    def test_format_matches_spec(self, tmp_path):
        import re
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        rw.append_log(str(wiki), "lint | report: 0 red")
        log = (wiki / "log.md").read_text()
        assert re.search(r"## \[\d{4}-\d{2}-\d{2}\] lint \| report: 0 red", log)


# ── _parse_frontmatter (enhanced) ────────────────────────────────────────

class TestParseFrontmatter:
    def test_basic(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text('---\ntitle: "Hello World"\nstatus: active\n---\nBody\n')
        fm = rw._parse_frontmatter(p)
        assert fm["title"] == "Hello World"
        assert fm["status"] == "active"

    def test_inline_list(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\ntags: [ml, nlp, transformers]\n---\n")
        fm = rw._parse_frontmatter(p)
        assert fm["tags"] == ["ml", "nlp", "transformers"]

    def test_integer(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\nimportance: 5\nyear: 2025\n---\n")
        fm = rw._parse_frontmatter(p)
        assert fm["importance"] == 5
        assert fm["year"] == 2025

    def test_no_frontmatter(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("No frontmatter here.\n")
        assert rw._parse_frontmatter(p) == {}

    def test_missing_file(self, tmp_path):
        assert rw._parse_frontmatter(tmp_path / "nope.md") == {}

    def test_float(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\nconfidence: 0.85\n---\n")
        fm = rw._parse_frontmatter(p)
        assert fm["confidence"] == 0.85

    def test_nested_dict(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\ntitle: Exp\nsetup:\n  model: gpt-4\n  dataset: mmlu\n---\n")
        fm = rw._parse_frontmatter(p)
        assert isinstance(fm["setup"], dict)
        assert fm["setup"]["model"] == "gpt-4"
        assert fm["setup"]["dataset"] == "mmlu"

    def test_block_list(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\ntags:\n  - ml\n  - nlp\n  - cv\n---\n")
        fm = rw._parse_frontmatter(p)
        assert fm["tags"] == ["ml", "nlp", "cv"]

    def test_list_of_dicts(self, tmp_path):
        """Claims evidence format: list of dicts."""
        p = tmp_path / "test.md"
        p.write_text(
            "---\n"
            "title: Test Claim\n"
            "evidence:\n"
            "  - source: paper-a\n"
            "    type: supports\n"
            "    strength: strong\n"
            "    detail: Table 2 shows improvement\n"
            "  - source: exp-b\n"
            "    type: tested_by\n"
            "    strength: moderate\n"
            "    detail: Preliminary results\n"
            "---\n"
        )
        fm = rw._parse_frontmatter(p)
        assert isinstance(fm["evidence"], list)
        assert len(fm["evidence"]) == 2
        assert fm["evidence"][0]["source"] == "paper-a"
        assert fm["evidence"][0]["strength"] == "strong"
        assert fm["evidence"][1]["source"] == "exp-b"

    def test_empty_inline_list(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\ntags: []\n---\n")
        fm = rw._parse_frontmatter(p)
        assert fm["tags"] == []

    def test_boolean(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\nanonymous: true\ndraft: false\n---\n")
        fm = rw._parse_frontmatter(p)
        assert fm["anonymous"] is True
        assert fm["draft"] is False


# ── _serialize_frontmatter ────────────────────────────────────────────────

class TestSerializeFrontmatter:
    def test_roundtrip_scalar(self, tmp_path):
        fm = {"title": "Test", "status": "active", "importance": 5}
        text = rw._serialize_frontmatter(fm)
        assert "title: Test" in text
        assert "importance: 5" in text

    def test_roundtrip_list(self, tmp_path):
        fm = {"tags": ["ml", "nlp"]}
        text = rw._serialize_frontmatter(fm)
        assert "[ml, nlp]" in text

    def test_roundtrip_empty_list(self, tmp_path):
        fm = {"tags": []}
        text = rw._serialize_frontmatter(fm)
        assert "tags: []" in text

    def test_roundtrip_nested_dict(self, tmp_path):
        fm = {"setup": {"model": "gpt-4", "dataset": "mmlu"}}
        text = rw._serialize_frontmatter(fm)
        assert "setup:" in text
        assert "  model: gpt-4" in text

    def test_roundtrip_list_of_dicts(self, tmp_path):
        fm = {"evidence": [
            {"source": "paper-a", "type": "supports", "strength": "strong"},
        ]}
        text = rw._serialize_frontmatter(fm)
        assert "evidence:" in text
        assert "  - source: paper-a" in text
        assert "    type: supports" in text

    def test_roundtrip_float(self):
        fm = {"confidence": 0.85}
        text = rw._serialize_frontmatter(fm)
        assert "confidence: 0.85" in text


# ── read_meta / set_meta ─────────────────────────────────────────────────

class TestReadMeta:
    def test_read_all(self, wiki, capsys):
        _write_page(wiki, "claims", "test", 'title: Test Claim\nstatus: proposed\nconfidence: 0.5')
        capsys.readouterr()
        rw.read_meta(str(wiki / "claims" / "test.md"))
        out = json.loads(capsys.readouterr().out)
        assert out["title"] == "Test Claim"
        assert out["status"] == "proposed"
        assert out["confidence"] == 0.5

    def test_read_single_field(self, wiki, capsys):
        _write_page(wiki, "claims", "test", 'title: Test\nconfidence: 0.7')
        capsys.readouterr()
        rw.read_meta(str(wiki / "claims" / "test.md"), "confidence")
        out = json.loads(capsys.readouterr().out)
        assert out == 0.7

    def test_read_missing_field_exits(self, wiki):
        _write_page(wiki, "claims", "test", 'title: Test')
        with pytest.raises(SystemExit):
            rw.read_meta(str(wiki / "claims" / "test.md"), "nonexistent")

    def test_read_missing_file_exits(self, wiki):
        with pytest.raises(SystemExit):
            rw.read_meta(str(wiki / "claims" / "nope.md"))


class TestSetMeta:
    def test_set_scalar(self, wiki, capsys):
        _write_page(wiki, "claims", "test", 'title: Test\nstatus: proposed\nconfidence: 0.5')
        capsys.readouterr()
        rw.set_meta(str(wiki / "claims" / "test.md"), "confidence", "0.8")
        # Verify the file was updated
        fm = rw._parse_frontmatter(wiki / "claims" / "test.md")
        assert fm["confidence"] == 0.8

    def test_set_string(self, wiki):
        _write_page(wiki, "ideas", "test", 'title: Test\nstatus: proposed\nfailure_reason: ""')
        rw.set_meta(str(wiki / "ideas" / "test.md"), "failure_reason", "GPU OOM")
        fm = rw._parse_frontmatter(wiki / "ideas" / "test.md")
        assert fm["failure_reason"] == "GPU OOM"

    def test_append_to_list(self, wiki, capsys):
        _write_page(wiki, "ideas", "test", 'title: Test\nlinked_experiments: []')
        capsys.readouterr()
        rw.set_meta(str(wiki / "ideas" / "test.md"), "linked_experiments", "exp-1", append=True)
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert out["action"] == "append"
        fm = rw._parse_frontmatter(wiki / "ideas" / "test.md")
        assert "exp-1" in fm["linked_experiments"]

    def test_append_dedup(self, wiki):
        _write_page(wiki, "ideas", "test", 'title: Test\nlinked_experiments: [exp-1]')
        rw.set_meta(str(wiki / "ideas" / "test.md"), "linked_experiments", "exp-1", append=True)
        fm = rw._parse_frontmatter(wiki / "ideas" / "test.md")
        assert fm["linked_experiments"].count("exp-1") == 1

    def test_preserves_body(self, wiki):
        _write_page(wiki, "papers", "test", 'title: Test\nimportance: 3',
                     "\n## Method\n\nSome content here.\n")
        rw.set_meta(str(wiki / "papers" / "test.md"), "importance", "5")
        content = (wiki / "papers" / "test.md").read_text()
        assert "Some content here." in content

    def test_missing_file_exits(self, wiki):
        with pytest.raises(SystemExit):
            rw.set_meta(str(wiki / "papers" / "nope.md"), "title", "x")


# ── find_entities ─────────────────────────────────────────────────────────

class TestFindEntities:
    def test_find_by_status(self, wiki, capsys):
        _write_page(wiki, "claims", "a", 'title: A\nstatus: proposed\nconfidence: 0.3')
        _write_page(wiki, "claims", "b", 'title: B\nstatus: supported\nconfidence: 0.9')
        _write_page(wiki, "claims", "c", 'title: C\nstatus: proposed\nconfidence: 0.5')
        capsys.readouterr()
        rw.find_entities(str(wiki), "claims", [("status", "proposed")])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 2
        slugs = {r["slug"] for r in results}
        assert slugs == {"a", "c"}

    def test_find_by_numeric_comparison(self, wiki, capsys):
        _write_page(wiki, "claims", "a", 'title: A\nconfidence: 0.3')
        _write_page(wiki, "claims", "b", 'title: B\nconfidence: 0.7')
        _write_page(wiki, "claims", "c", 'title: C\nconfidence: 0.9')
        capsys.readouterr()
        rw.find_entities(str(wiki), "claims", [("confidence", "<0.5")])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["slug"] == "a"

    def test_find_by_gte(self, wiki, capsys):
        _write_page(wiki, "papers", "a", 'title: A\nimportance: 3')
        _write_page(wiki, "papers", "b", 'title: B\nimportance: 5')
        _write_page(wiki, "papers", "c", 'title: C\nimportance: 4')
        capsys.readouterr()
        rw.find_entities(str(wiki), "papers", [("importance", ">=4")])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 2

    def test_find_multiple_filters(self, wiki, capsys):
        _write_page(wiki, "papers", "a", 'title: A\ndomain: NLP\nimportance: 5')
        _write_page(wiki, "papers", "b", 'title: B\ndomain: NLP\nimportance: 2')
        _write_page(wiki, "papers", "c", 'title: C\ndomain: CV\nimportance: 5')
        capsys.readouterr()
        rw.find_entities(str(wiki), "papers", [("domain", "NLP"), ("importance", ">=4")])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["slug"] == "a"

    def test_find_empty_result(self, wiki, capsys):
        capsys.readouterr()
        rw.find_entities(str(wiki), "claims", [("status", "proposed")])
        results = json.loads(capsys.readouterr().out)
        assert results == []

    def test_find_in_list_field(self, wiki, capsys):
        _write_page(wiki, "papers", "a", 'title: A\ntags: [ml, nlp]')
        _write_page(wiki, "papers", "b", 'title: B\ntags: [cv, robotics]')
        capsys.readouterr()
        rw.find_entities(str(wiki), "papers", [("tags", "nlp")])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["slug"] == "a"



# ── find-similar-concept ──────────────────────────────────────────────────

class TestFindSimilarConcept:
    """Detect existing concepts that overlap with a candidate before creating a new one.

    The matcher must catch the failure modes observed in test6 OmegaWiki:
      - identical concept created by different parallel subagents under different slugs
        ("LLM-Driven Evolutionary Operators" vs "LLMs as Evolutionary Operators")
      - candidate matches an existing concept's alias (different official name)
      - close paraphrase ("Textual Gradient Descent" vs "Textual Gradient Optimization")
    while NOT generating false positives for unrelated concepts that happen to share a word.
    """

    def test_empty_wiki_returns_empty(self, wiki, capsys):
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Some New Concept")
        assert json.loads(capsys.readouterr().out) == []

    def test_exact_title_match(self, wiki, capsys):
        _write_page(wiki, "concepts", "textual-gradient-descent",
                    'title: "Textual Gradient Descent"\naliases: []\nmaturity: emerging\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Textual Gradient Descent")
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["slug"] == "textual-gradient-descent"
        assert results[0]["score"] == 1.0
        assert "exact" in results[0]["match_reason"]

    def test_alias_match_returns_existing_concept(self, wiki, capsys):
        """Candidate name equals an alias of an existing concept."""
        _write_page(wiki, "concepts", "textual-gradient-descent",
                    'title: "Textual Gradient Descent"\naliases: ["natural language gradient", "text gradient"]\nmaturity: emerging\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Natural Language Gradient")
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["slug"] == "textual-gradient-descent"
        assert results[0]["score"] >= 0.95

    def test_candidate_alias_matches_existing_title(self, wiki, capsys):
        """Candidate has aliases; one of them matches an existing concept's title."""
        _write_page(wiki, "concepts", "textual-gradient-descent",
                    'title: "Textual Gradient Descent"\naliases: []\nmaturity: emerging\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Brand New Concept",
                                ["something else", "Textual Gradient Descent"])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["score"] == 1.0

    def test_real_test6_evolutionary_operators_pair(self, wiki, capsys):
        """Detect the specific duplicate pair seen in test6: 'LLMs as Evolutionary Operators'
        vs 'LLM-Driven Evolutionary Operators' (created by different subagents)."""
        _write_page(wiki, "concepts", "llms-evolutionary-operators",
                    'title: "LLMs as Evolutionary Operators"\naliases: ["LLM mutation operator", "language model evolutionary operators"]\nmaturity: emerging\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "LLM-Driven Evolutionary Operators",
                                ["LLM as evolutionary operator", "LLM crossover and mutation"])
        results = json.loads(capsys.readouterr().out)
        assert len(results) >= 1
        assert results[0]["slug"] == "llms-evolutionary-operators"
        assert results[0]["score"] >= 0.40

    def test_phrase_containment_with_3plus_tokens(self, wiki, capsys):
        """Substring containment matches when the shorter side has 2+ content tokens."""
        _write_page(wiki, "concepts", "scaled-dot-product-attention",
                    'title: "Scaled Dot-Product Attention"\naliases: []\nmaturity: stable\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Multi-Head Scaled Dot-Product Attention")
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["score"] >= 0.80

    def test_unrelated_concept_returns_empty(self, wiki, capsys):
        _write_page(wiki, "concepts", "textual-gradient-descent",
                    'title: "Textual Gradient Descent"\naliases: []\nmaturity: emerging\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Bayesian Optimization with Gaussian Processes")
        assert json.loads(capsys.readouterr().out) == []

    def test_single_token_substring_does_not_trigger(self, wiki, capsys):
        """Avoid 'lora' matching 'lora-low-rank-adaptation' just because it's a substring.
        Phrase containment requires the shorter side to have 2+ tokens."""
        _write_page(wiki, "concepts", "lora",
                    'title: "LoRA"\naliases: []\nmaturity: stable\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "LoRA Low-Rank Adaptation of Large Language Models")
        results = json.loads(capsys.readouterr().out)
        # Score allowed but should not be a containment 0.85; the single-token "lora"
        # cannot trigger the substring rule.
        for r in results:
            assert "phrase containment" not in r["match_reason"]

    def test_results_sorted_descending_by_score(self, wiki, capsys):
        """When multiple matches exist, the highest-score one comes first."""
        _write_page(wiki, "concepts", "textual-gradient-descent",
                    'title: "Textual Gradient Descent"\naliases: []\nmaturity: emerging\nkey_papers: []')
        _write_page(wiki, "concepts", "textual-gradient-optimization",
                    'title: "Textual Gradient Optimization"\naliases: ["text gradient"]\nmaturity: active\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Textual Gradient Descent")
        results = json.loads(capsys.readouterr().out)
        assert len(results) >= 1
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
        assert results[0]["slug"] == "textual-gradient-descent"  # exact wins

    def test_empty_candidate_aliases_optional(self, wiki, capsys):
        _write_page(wiki, "concepts", "foo",
                    'title: "Foo"\naliases: []\nmaturity: emerging\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Bar", None)
        assert json.loads(capsys.readouterr().out) == []

    def test_concepts_dir_missing(self, tmp_path, capsys):
        """No concepts dir at all → return empty (don't crash)."""
        capsys.readouterr()
        rw.find_similar_concept(str(tmp_path), "Anything")
        assert json.loads(capsys.readouterr().out) == []

    def test_foundation_match_outranks_concept(self, wiki, capsys):
        """Foundation hits are tagged entity_type='foundation' and appear before concept hits."""
        _write_page(wiki, "concepts", "selfattn-variant",
                    'title: "Self-Attention Variant X"\naliases: []\nmaturity: emerging\nkey_papers: []')
        _write_page(wiki, "foundations", "attention-mechanism",
                    'title: "Attention Mechanism"\nslug: attention-mechanism\ndomain: NLP\nstatus: mainstream\naliases: ["self-attention", "scaled dot-product attention"]')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Self-Attention")
        results = json.loads(capsys.readouterr().out)
        assert len(results) >= 1
        assert results[0]["entity_type"] == "foundation"
        assert results[0]["slug"] == "attention-mechanism"

    def test_entity_type_tag_present_on_concept_results(self, wiki, capsys):
        _write_page(wiki, "concepts", "textual-gradient-descent",
                    'title: "Textual Gradient Descent"\naliases: []\nmaturity: emerging\nkey_papers: []')
        capsys.readouterr()
        rw.find_similar_concept(str(wiki), "Textual Gradient Descent")
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["entity_type"] == "concept"


# ── find-similar-claim ────────────────────────────────────────────────────

class TestFindSimilarClaim:
    """Detect semantically equivalent claims, including paraphrased versions
    that use different research-vocabulary verbs (the test6 failure mode where
    4 separate claims all expressed 'LLM method beats human prompts')."""

    def test_empty_wiki_returns_empty(self, wiki, capsys):
        capsys.readouterr()
        rw.find_similar_claim(str(wiki), "Some Claim")
        assert json.loads(capsys.readouterr().out) == []

    def test_exact_title_match(self, wiki, capsys):
        _write_page(wiki, "claims", "lora-preserves-quality",
                    'title: "LoRA preserves quality at low rank"\ntags: [peft, fine-tuning]\nstatus: supported\nconfidence: 0.85\nsource_papers: []')
        capsys.readouterr()
        rw.find_similar_claim(str(wiki), "LoRA preserves quality at low rank", ["peft"])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["score"] == 1.0

    def test_synonym_paraphrase_matches(self, wiki, capsys):
        """The CRITICAL test: paraphrased claims with synonym verbs should match.
        Without canonicalization this returns empty; with canonicalization it should match."""
        _write_page(wiki, "claims", "llm-prompts-beat-human",
                    'title: "LLM-optimized prompts outperform human-written prompts"\ntags: [prompt-optimization, llm]\nstatus: weakly_supported\nconfidence: 0.7\nsource_papers: []')
        capsys.readouterr()
        rw.find_similar_claim(str(wiki),
                              "LLM-generated prompts beat human prompts on diverse NLP tasks",
                              ["prompt-optimization", "nlp"])
        results = json.loads(capsys.readouterr().out)
        assert len(results) >= 1, "Synonym paraphrase ('generated/optimized', 'beat/outperform') must match"
        assert results[0]["slug"] == "llm-prompts-beat-human"
        assert results[0]["score"] >= 0.40

    def test_test6_real_duplicate_pair(self, wiki, capsys):
        """Reproduce one of the actual duplicate claim pairs from test6 OmegaWiki."""
        _write_page(wiki, "claims", "llm-optimized-prompts-outperform-human-prompts",
                    'title: "LLM-optimized prompts outperform human-written prompts"\ntags: [prompt-optimization, llm]\nstatus: weakly_supported\nconfidence: 0.7\nsource_papers: [opro]')
        capsys.readouterr()
        # The candidate that should have been deduped against the existing one
        rw.find_similar_claim(str(wiki),
                              "LLM-driven evolutionary prompt optimization outperforms manual baselines",
                              ["prompt-optimization", "llm", "evolutionary"])
        results = json.loads(capsys.readouterr().out)
        assert len(results) >= 1
        assert results[0]["slug"] == "llm-optimized-prompts-outperform-human-prompts"

    def test_substring_containment(self, wiki, capsys):
        _write_page(wiki, "claims", "base-claim",
                    'title: "LLM-optimized prompts outperform human-written prompts"\ntags: [prompt-optimization]\nstatus: supported\nconfidence: 0.8\nsource_papers: []')
        capsys.readouterr()
        rw.find_similar_claim(str(wiki),
                              "EvoPrompt: LLM-optimized prompts outperform human-written prompts on GSM8K",
                              ["prompt-optimization"])
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["score"] >= 0.80

    def test_unrelated_claim_returns_empty(self, wiki, capsys):
        _write_page(wiki, "claims", "lora-preserves-quality",
                    'title: "LoRA preserves quality at low rank"\ntags: [peft]\nstatus: supported\nconfidence: 0.85\nsource_papers: []')
        capsys.readouterr()
        rw.find_similar_claim(str(wiki), "FlashAttention reduces GPU memory usage", ["systems"])
        assert json.loads(capsys.readouterr().out) == []

    def test_same_area_different_proposition(self, wiki, capsys):
        """Same research area (shared tags) but different propositions should NOT match."""
        _write_page(wiki, "claims", "llm-prompts-beat-human",
                    'title: "LLM-optimized prompts outperform human-written prompts"\ntags: [prompt-optimization, llm]\nstatus: weakly_supported\nconfidence: 0.7\nsource_papers: []')
        capsys.readouterr()
        rw.find_similar_claim(str(wiki),
                              "Prompts longer than 200 tokens degrade GPT-4 performance",
                              ["prompt-optimization"])
        results = json.loads(capsys.readouterr().out)
        assert results == [], "Same tag but different proposition must not match"

    def test_tag_overlap_loosens_threshold(self, wiki, capsys):
        """When tags overlap, lower-score matches are returned that would otherwise be filtered."""
        _write_page(wiki, "claims", "fine-tune-quality",
                    'title: "Parameter-efficient fine-tuning preserves model quality"\ntags: [peft, fine-tuning]\nstatus: supported\nconfidence: 0.85\nsource_papers: []')
        capsys.readouterr()
        # Without shared tags: score below 0.45 floor → empty
        rw.find_similar_claim(str(wiki),
                              "PEFT methods preserve quality on downstream tasks",
                              [])
        no_tags = json.loads(capsys.readouterr().out)
        # With shared tag: looser 0.30 floor → may include
        capsys.readouterr()
        rw.find_similar_claim(str(wiki),
                              "PEFT methods preserve quality on downstream tasks",
                              ["peft"])
        with_tags = json.loads(capsys.readouterr().out)
        # Tag-aware version should not be more conservative than tag-blind
        assert len(with_tags) >= len(no_tags)

    def test_results_sorted_descending(self, wiki, capsys):
        _write_page(wiki, "claims", "claim-a",
                    'title: "LLM-optimized prompts outperform human prompts"\ntags: [prompt-optimization]\nstatus: supported\nconfidence: 0.8\nsource_papers: []')
        _write_page(wiki, "claims", "claim-b",
                    'title: "Manual prompts perform worse than LLM-generated ones"\ntags: [prompt-optimization]\nstatus: supported\nconfidence: 0.7\nsource_papers: []')
        capsys.readouterr()
        rw.find_similar_claim(str(wiki),
                              "LLM-generated prompts beat human prompts",
                              ["prompt-optimization"])
        results = json.loads(capsys.readouterr().out)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_claims_dir_missing(self, tmp_path, capsys):
        capsys.readouterr()
        rw.find_similar_claim(str(tmp_path), "Anything", [])
        assert json.loads(capsys.readouterr().out) == []


# ── helpers used by find-similar-* ────────────────────────────────────────

class TestSemanticDedupHelpers:

    def test_normalize_text_lowercases_and_strips_punct(self):
        assert rw._normalize_text("LLM-Optimized Prompts!") == "llm optimized prompts"

    def test_content_tokens_drops_stop_words(self):
        toks = rw._content_tokens("the lora adaptation of large language models")
        assert "the" not in toks
        assert "lora" in toks
        assert "language" in toks

    def test_content_tokens_drops_short_tokens(self):
        toks = rw._content_tokens("a is on the of in")
        assert toks == set()

    def test_phrase_match_score_exact(self):
        assert rw._phrase_match_score("LoRA", "lora") == 1.0

    def test_phrase_match_score_unrelated(self):
        assert rw._phrase_match_score("LoRA", "FlashAttention") == 0.0

    def test_phrase_match_score_substring_requires_2_tokens(self):
        # Single shared word → no substring boost
        assert rw._phrase_match_score("LoRA", "LoRA Adapter Layer") < 0.85
        # Two-word shared phrase → substring boost
        score = rw._phrase_match_score("LoRA Adapter", "LoRA Adapter Layer")
        assert score >= 0.85

    def test_claim_tokens_canonicalizes_synonyms(self):
        a = rw._claim_tokens("LLM-optimized prompts outperform human-written prompts")
        b = rw._claim_tokens("LLM-generated prompts beat human prompts")
        # After canonicalization, both should share the canonical verbs/nouns:
        # produce (optimized/generated), beat (outperform/beat), human, prompt, llm
        shared = a & b
        assert "beat" in shared
        assert "produce" in shared
        assert "human" in shared
        assert "prompt" in shared

    def test_claim_tokens_does_not_destroy_unrelated(self):
        a = rw._claim_tokens("LoRA preserves quality at low rank")
        b = rw._claim_tokens("FlashAttention reduces GPU memory usage")
        # Should have minimal overlap (no shared canonical token)
        assert len(a & b) <= 1


# ── query: weak-claims ────────────────────────────────────────────────────

class TestQueryWeakClaims:
    def test_finds_low_confidence(self, wiki, capsys):
        _write_page(wiki, "claims", "a", 'title: A\nstatus: supported\nconfidence: 0.3')
        _write_page(wiki, "claims", "b", 'title: B\nstatus: supported\nconfidence: 0.8')
        capsys.readouterr()
        rw.query_weak_claims(str(wiki), threshold=0.5)
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["slug"] == "a"

    def test_finds_proposed_status(self, wiki, capsys):
        _write_page(wiki, "claims", "a", 'title: A\nstatus: proposed\nconfidence: 0.8')
        capsys.readouterr()
        rw.query_weak_claims(str(wiki))
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1

    def test_sorted_by_confidence(self, wiki, capsys):
        _write_page(wiki, "claims", "a", 'title: A\nstatus: proposed\nconfidence: 0.4')
        _write_page(wiki, "claims", "b", 'title: B\nstatus: proposed\nconfidence: 0.1')
        capsys.readouterr()
        rw.query_weak_claims(str(wiki))
        results = json.loads(capsys.readouterr().out)
        assert results[0]["confidence"] <= results[1]["confidence"]


# ── query: evidence-for ───────────────────────────────────────────────────

class TestQueryEvidenceFor:
    def test_basic_evidence_chain(self, wiki, capsys):
        _write_page(wiki, "claims", "rank-quality",
                     'title: LoRA rank quality\nstatus: weakly_supported\nconfidence: 0.6\n'
                     'source_papers: [lora-paper]')
        _write_page(wiki, "experiments", "exp-1",
                     'title: Exp 1\nstatus: completed\ntarget_claim: rank-quality\n'
                     'outcome: succeeded\nkey_result: 2% improvement')
        rw.add_edge(str(wiki), "papers/lora-paper", "claims/rank-quality", "supports", "Table 2")
        capsys.readouterr()
        rw.query_evidence_for(str(wiki), "rank-quality")
        result = json.loads(capsys.readouterr().out)
        assert result["claim"]["slug"] == "rank-quality"
        assert len(result["supporting"]) == 1
        assert len(result["experiments"]) == 1
        assert result["experiments"][0]["outcome"] == "succeeded"

    def test_missing_claim_exits(self, wiki):
        with pytest.raises(SystemExit):
            rw.query_evidence_for(str(wiki), "nonexistent")


# ── query: ready-to-test ──────────────────────────────────────────────────

class TestQueryReadyToTest:
    def test_finds_proposed_without_experiments(self, wiki, capsys):
        _write_page(wiki, "ideas", "idea-a",
                     'title: Idea A\nstatus: proposed\npriority: 4\nlinked_experiments: []')
        _write_page(wiki, "ideas", "idea-b",
                     'title: Idea B\nstatus: proposed\npriority: 2\nlinked_experiments: [exp-1]')
        _write_page(wiki, "ideas", "idea-c",
                     'title: Idea C\nstatus: failed\npriority: 5\nlinked_experiments: []')
        capsys.readouterr()
        rw.query_ready_to_test(str(wiki))
        results = json.loads(capsys.readouterr().out)
        assert len(results) == 1
        assert results[0]["slug"] == "idea-a"

    def test_sorted_by_priority(self, wiki, capsys):
        _write_page(wiki, "ideas", "low", 'title: Low\nstatus: proposed\npriority: 1\nlinked_experiments: []')
        _write_page(wiki, "ideas", "high", 'title: High\nstatus: proposed\npriority: 5\nlinked_experiments: []')
        capsys.readouterr()
        rw.query_ready_to_test(str(wiki))
        results = json.loads(capsys.readouterr().out)
        assert results[0]["priority"] == 5


# ── query: orphans ────────────────────────────────────────────────────────

class TestQueryOrphans:
    def test_finds_unconnected_entities(self, wiki, capsys):
        _write_page(wiki, "concepts", "orphan-concept", 'title: Orphan')
        _write_page(wiki, "papers", "connected", 'title: Connected')
        rw.add_edge(str(wiki), "papers/connected", "claims/x", "supports")
        capsys.readouterr()
        rw.query_orphans(str(wiki))
        results = json.loads(capsys.readouterr().out)
        orphan_ids = {r["entity"] for r in results}
        assert "concepts/orphan-concept" in orphan_ids
        assert "papers/connected" not in orphan_ids


# ── neighbors ─────────────────────────────────────────────────────────────

class TestNeighbors:
    def test_depth_1(self, wiki, capsys):
        rw.add_edge(str(wiki), "papers/lora", "claims/rank", "supports")
        rw.add_edge(str(wiki), "papers/lora", "concepts/peft", "extends")
        rw.add_edge(str(wiki), "papers/other", "papers/lora", "extends")
        capsys.readouterr()
        rw.neighbors(str(wiki), "papers/lora", depth=1)
        result = json.loads(capsys.readouterr().out)
        assert result["center"] == "papers/lora"
        assert len(result["nodes"]) == 3

    def test_incoming_only(self, wiki, capsys):
        rw.add_edge(str(wiki), "papers/lora", "claims/rank", "supports")
        rw.add_edge(str(wiki), "papers/other", "papers/lora", "extends")
        capsys.readouterr()
        rw.neighbors(str(wiki), "papers/lora", depth=1, direction="incoming")
        result = json.loads(capsys.readouterr().out)
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == "papers/other"

    def test_outgoing_only(self, wiki, capsys):
        rw.add_edge(str(wiki), "papers/lora", "claims/rank", "supports")
        rw.add_edge(str(wiki), "papers/other", "papers/lora", "extends")
        capsys.readouterr()
        rw.neighbors(str(wiki), "papers/lora", depth=1, direction="outgoing")
        result = json.loads(capsys.readouterr().out)
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == "claims/rank"

    def test_edge_type_filter(self, wiki, capsys):
        rw.add_edge(str(wiki), "papers/lora", "claims/rank", "supports")
        rw.add_edge(str(wiki), "papers/lora", "concepts/peft", "extends")
        capsys.readouterr()
        rw.neighbors(str(wiki), "papers/lora", depth=1, edge_types=["supports"])
        result = json.loads(capsys.readouterr().out)
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["edge"] == "supports"

    def test_depth_2(self, wiki, capsys):
        rw.add_edge(str(wiki), "papers/lora", "claims/rank", "supports")
        rw.add_edge(str(wiki), "claims/rank", "experiments/exp1", "tested_by")
        capsys.readouterr()
        rw.neighbors(str(wiki), "papers/lora", depth=2)
        result = json.loads(capsys.readouterr().out)
        node_ids = {n["id"] for n in result["nodes"]}
        assert "claims/rank" in node_ids
        assert "experiments/exp1" in node_ids


# ── compile_context ───────────────────────────────────────────────────────

class TestCompileContext:
    def test_general_purpose(self, wiki, capsys):
        _write_page(wiki, "papers", "lora", 'title: LoRA\nimportance: 5')
        capsys.readouterr()
        rw.compile_context(str(wiki), "general")
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert out["purpose"] == "general"
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert "LoRA" in content

    def test_ideation_emphasizes_gaps(self, wiki, capsys):
        _write_page(wiki, "claims", "weak", 'title: Weak\nstatus: proposed\nconfidence: 0.2')
        _write_page(wiki, "ideas", "failed-idea", 'title: Bad Idea\nstatus: failed\nfailure_reason: OOM')
        capsys.readouterr()
        rw.compile_context(str(wiki), "ideation")
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert "Failed Ideas" in content
        assert "OOM" in content

    def test_experiment_emphasizes_claims(self, wiki, capsys):
        _write_page(wiki, "claims", "target", 'title: Target Claim\nstatus: proposed\nconfidence: 0.4')
        _write_page(wiki, "experiments", "exp1", 'title: Exp 1\nstatus: completed\ntarget_claim: target')
        capsys.readouterr()
        rw.compile_context(str(wiki), "experiment")
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert "Experiments" in content

    def test_all_purposes_valid(self, wiki, capsys):
        for purpose in rw.CONTEXT_BUDGETS:
            capsys.readouterr()
            rw.compile_context(str(wiki), purpose)
            out = json.loads(capsys.readouterr().out)
            assert out["status"] == "ok"


# ── transition ────────────────────────────────────────────────────────────

class TestTransition:
    def test_valid_idea_transition(self, wiki, capsys):
        _write_page(wiki, "ideas", "test",
                     'title: Test\nstatus: proposed\nlinked_experiments: [exp-1]')
        capsys.readouterr()
        rw.transition(str(wiki / "ideas" / "test.md"), "in_progress")
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert out["old_status"] == "proposed"
        assert out["new_status"] == "in_progress"
        # Verify file was updated
        fm = rw._parse_frontmatter(wiki / "ideas" / "test.md")
        assert fm["status"] == "in_progress"

    def test_invalid_transition_exits(self, wiki):
        _write_page(wiki, "ideas", "test", 'title: Test\nstatus: proposed')
        with pytest.raises(SystemExit):
            rw.transition(str(wiki / "ideas" / "test.md"), "validated")

    def test_idea_failed_requires_reason(self, wiki):
        _write_page(wiki, "ideas", "test", 'title: Test\nstatus: tested')
        with pytest.raises(SystemExit):
            rw.transition(str(wiki / "ideas" / "test.md"), "failed")

    def test_idea_failed_sets_auto_fields(self, wiki, capsys):
        _write_page(wiki, "ideas", "test",
                     'title: Test\nstatus: tested\nfailure_reason: ""\ndate_resolved: ""')
        capsys.readouterr()
        rw.transition(str(wiki / "ideas" / "test.md"), "failed", reason="GPU OOM")
        out = json.loads(capsys.readouterr().out)
        assert "failure_reason" in out.get("auto_set", [])
        assert "date_resolved" in out.get("auto_set", [])
        fm = rw._parse_frontmatter(wiki / "ideas" / "test.md")
        assert fm["failure_reason"] == "GPU OOM"
        assert fm["date_resolved"] != ""

    def test_idea_in_progress_requires_experiments(self, wiki):
        _write_page(wiki, "ideas", "test", 'title: Test\nstatus: proposed\nlinked_experiments: []')
        with pytest.raises(SystemExit):
            rw.transition(str(wiki / "ideas" / "test.md"), "in_progress")

    def test_claim_supported_requires_strong_evidence(self, wiki):
        _write_page(wiki, "claims", "test",
                     'title: Test\nstatus: weakly_supported\nevidence:\n'
                     '  - source: paper-a\n    type: supports\n    strength: moderate\n    detail: ok')
        with pytest.raises(SystemExit):
            rw.transition(str(wiki / "claims" / "test.md"), "supported")

    def test_claim_supported_with_strong_evidence(self, wiki, capsys):
        _write_page(wiki, "claims", "test",
                     'title: Test\nstatus: weakly_supported\nevidence:\n'
                     '  - source: paper-a\n    type: supports\n    strength: strong\n    detail: proven')
        capsys.readouterr()
        rw.transition(str(wiki / "claims" / "test.md"), "supported")
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"

    def test_experiment_completed_requires_key_result(self, wiki):
        _write_page(wiki, "experiments", "test",
                     'title: Test\nstatus: running\nkey_result: ""')
        with pytest.raises(SystemExit):
            rw.transition(str(wiki / "experiments" / "test.md"), "completed")

    def test_nonexistent_file_exits(self, wiki):
        with pytest.raises(SystemExit):
            rw.transition(str(wiki / "ideas" / "nope.md"), "in_progress")

    def test_unknown_entity_type_exits(self, wiki):
        _write_page(wiki, "papers", "test", 'title: Test\nstatus: whatever')
        with pytest.raises(SystemExit):
            rw.transition(str(wiki / "papers" / "test.md"), "published")


# ── batch_edges ───────────────────────────────────────────────────────────

class TestBatchEdges:
    def test_batch_add(self, wiki, capsys, monkeypatch):
        data = json.dumps([
            {"from": "papers/a", "to": "claims/b", "type": "supports", "evidence": "Fig 1"},
            {"from": "papers/a", "to": "concepts/c", "type": "extends"},
        ])
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO(data))
        capsys.readouterr()
        rw.batch_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert out["added"] == 2
        edges = rw.load_edges(str(wiki))
        assert len(edges) == 2

    def test_batch_dedup(self, wiki, capsys, monkeypatch):
        rw.add_edge(str(wiki), "papers/a", "claims/b", "supports")
        data = json.dumps([
            {"from": "papers/a", "to": "claims/b", "type": "supports"},
            {"from": "papers/a", "to": "concepts/c", "type": "extends"},
        ])
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO(data))
        capsys.readouterr()
        rw.batch_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["added"] == 1
        assert out["existed"] == 1

    def test_batch_invalid_type(self, wiki, capsys, monkeypatch):
        data = json.dumps([{"from": "a", "to": "b", "type": "invalid_type"}])
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO(data))
        capsys.readouterr()
        rw.batch_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["added"] == 0
        assert len(out["warnings"]) >= 1


# ── dedup_edges ───────────────────────────────────────────────────────────

class TestDedupEdges:
    def test_no_edges_file(self, wiki, capsys):
        capsys.readouterr()
        rw.dedup_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert out["kept"] == 0
        assert out["removed"] == 0

    def test_no_duplicates_unchanged(self, wiki, capsys):
        rw.add_edge(str(wiki), "papers/a", "claims/b", "supports")
        rw.add_edge(str(wiki), "papers/a", "concepts/c", "extends")
        capsys.readouterr()
        rw.dedup_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["kept"] == 2
        assert out["removed"] == 0
        assert len(rw.load_edges(str(wiki))) == 2

    def test_removes_exact_duplicates(self, wiki, capsys):
        # Simulate parallel agents writing the same edge to separate worktrees,
        # then having both appended after merging
        edges_path = wiki / "graph" / "edges.jsonl"
        import json as _json
        edge = {"from": "papers/a", "to": "claims/b", "type": "supports",
                "evidence": "", "date": "2026-04-10"}
        edges_path.write_text(
            _json.dumps(edge) + "\n" + _json.dumps(edge) + "\n",
            encoding="utf-8",
        )
        capsys.readouterr()
        rw.dedup_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["kept"] == 1
        assert out["removed"] == 1
        assert len(rw.load_edges(str(wiki))) == 1

    def test_different_type_not_deduped(self, wiki, capsys):
        rw.add_edge(str(wiki), "papers/a", "claims/b", "supports")
        rw.add_edge(str(wiki), "papers/a", "claims/b", "contradicts")
        capsys.readouterr()
        rw.dedup_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["kept"] == 2
        assert out["removed"] == 0

    def test_preserves_first_occurrence(self, wiki, capsys):
        import json as _json
        edges_path = wiki / "graph" / "edges.jsonl"
        e1 = {"from": "papers/a", "to": "claims/b", "type": "supports",
              "evidence": "first", "date": "2026-04-09"}
        e2 = {"from": "papers/a", "to": "claims/b", "type": "supports",
              "evidence": "second", "date": "2026-04-10"}
        edges_path.write_text(
            _json.dumps(e1) + "\n" + _json.dumps(e2) + "\n",
            encoding="utf-8",
        )
        capsys.readouterr()
        rw.dedup_edges(str(wiki))
        capsys.readouterr()
        kept = rw.load_edges(str(wiki))
        assert len(kept) == 1
        assert kept[0]["evidence"] == "first"

    def test_many_duplicates(self, wiki, capsys):
        import json as _json
        edges_path = wiki / "graph" / "edges.jsonl"
        lines = []
        # 5 unique edges, each duplicated 3 times = 15 lines total
        pairs = [
            ("papers/p1", "claims/c1", "supports"),
            ("papers/p2", "claims/c2", "supports"),
            ("papers/p3", "concepts/k1", "extends"),
            ("papers/p1", "concepts/k1", "extends"),
            ("papers/p2", "concepts/k2", "inspired_by"),
        ]
        for from_id, to_id, etype in pairs:
            e = {"from": from_id, "to": to_id, "type": etype, "evidence": "", "date": "2026-04-10"}
            for _ in range(3):
                lines.append(_json.dumps(e))
        edges_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        capsys.readouterr()
        rw.dedup_edges(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["kept"] == 5
        assert out["removed"] == 10
        assert len(rw.load_edges(str(wiki))) == 5


# ── rebuild_index ─────────────────────────────────────────────────────────

class TestRebuildIndex:
    def test_generates_index(self, wiki, capsys):
        _write_page(wiki, "papers", "lora", 'title: LoRA\nimportance: 5\ntags: [ml]')
        _write_page(wiki, "claims", "rank", 'title: Rank Quality\nstatus: proposed')
        capsys.readouterr()
        rw.rebuild_index(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert out["entities"]["papers"] == 1
        assert out["entities"]["claims"] == 1

        content = (wiki / "index.md").read_text()
        assert "lora" in content
        assert "LoRA" in content
        assert "rank" in content

    def test_empty_wiki(self, wiki, capsys):
        capsys.readouterr()
        rw.rebuild_index(str(wiki))
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert all(v == 0 for v in out["entities"].values())


# ── CLI integration ───────────────────────────────────────────────────────

class TestCLI:
    TOOL = str(Path(__file__).resolve().parent.parent / "tools" / "research_wiki.py")

    def test_slug_command(self):
        result = subprocess.run(
            [sys.executable, self.TOOL, "slug", "Attention Is All You Need"],
            capture_output=True, text=True)
        assert result.returncode == 0
        assert "attention" in result.stdout.strip()

    def test_init_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        result = subprocess.run(
            [sys.executable, self.TOOL, "init", str(wiki)],
            capture_output=True, text=True)
        assert result.returncode == 0
        assert (wiki / "papers").is_dir()

    def test_stats_json_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        result = subprocess.run(
            [sys.executable, self.TOOL, "stats", str(wiki), "--json"],
            capture_output=True, text=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "papers" in data

    def test_add_edge_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        result = subprocess.run(
            [sys.executable, self.TOOL, "add-edge", str(wiki),
             "--from", "a", "--to", "b", "--type", "supports"],
            capture_output=True, text=True)
        assert result.returncode == 0
        edges = json.loads((wiki / "graph" / "edges.jsonl").read_text().strip())
        assert edges["from"] == "a"

    def test_log_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        result = subprocess.run(
            [sys.executable, self.TOOL, "log", str(wiki), "test message"],
            capture_output=True, text=True)
        assert result.returncode == 0
        assert "test message" in (wiki / "log.md").read_text()

    def test_read_meta_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        (wiki / "claims" / "test.md").write_text(
            "---\ntitle: Test\nstatus: proposed\n---\n")
        result = subprocess.run(
            [sys.executable, self.TOOL, "read-meta",
             str(wiki / "claims" / "test.md"), "status"],
            capture_output=True, text=True)
        assert result.returncode == 0
        assert json.loads(result.stdout) == "proposed"

    def test_compile_context_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        result = subprocess.run(
            [sys.executable, self.TOOL, "compile-context", str(wiki),
             "--for", "ideation"],
            capture_output=True, text=True)
        assert result.returncode == 0
        out = json.loads(result.stdout)
        assert out["purpose"] == "ideation"

    def test_rebuild_context_brief_alias(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        result = subprocess.run(
            [sys.executable, self.TOOL, "rebuild-context-brief", str(wiki)],
            capture_output=True, text=True)
        assert result.returncode == 0
        content = (wiki / "graph" / "context_brief.md").read_text()
        assert "Query Pack" in content

    def test_transition_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        (wiki / "ideas" / "test.md").write_text(
            "---\ntitle: Test\nstatus: proposed\nlinked_experiments: [exp-1]\n---\n")
        result = subprocess.run(
            [sys.executable, self.TOOL, "transition",
             str(wiki / "ideas" / "test.md"), "--to", "in_progress"],
            capture_output=True, text=True)
        assert result.returncode == 0
        out = json.loads(result.stdout)
        assert out["new_status"] == "in_progress"

    def test_rebuild_index_command(self, tmp_path):
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, self.TOOL, "init", str(wiki)],
                       capture_output=True)
        (wiki / "papers" / "lora.md").write_text(
            "---\ntitle: LoRA\nimportance: 5\n---\n")
        result = subprocess.run(
            [sys.executable, self.TOOL, "rebuild-index", str(wiki)],
            capture_output=True, text=True)
        assert result.returncode == 0
        assert "LoRA" in (wiki / "index.md").read_text()


# ── Checkpoint ───────────────────────────────────────────────────────────────

class TestCheckpoint:
    def test_save_and_load(self, wiki):
        rw.checkpoint_save(str(wiki), "test-task", "item-1")
        rw.checkpoint_save(str(wiki), "test-task", "item-2")

        cp_file = wiki / ".checkpoints" / "test-task.json"
        assert cp_file.exists()
        data = json.loads(cp_file.read_text())
        assert "item-1" in data["completed"]
        assert "item-2" in data["completed"]

    def test_save_failed_item(self, wiki):
        rw.checkpoint_save(str(wiki), "test-task", "bad-item", status="failed")

        data = json.loads((wiki / ".checkpoints" / "test-task.json").read_text())
        assert "bad-item" in data["failed"]
        assert "bad-item" not in data["completed"]

    def test_save_idempotent(self, wiki):
        rw.checkpoint_save(str(wiki), "test-task", "item-1")
        rw.checkpoint_save(str(wiki), "test-task", "item-1")

        data = json.loads((wiki / ".checkpoints" / "test-task.json").read_text())
        assert data["completed"].count("item-1") == 1

    def test_load_nonexistent(self, wiki, capsys):
        rw.checkpoint_load(str(wiki), "nonexistent")
        out = json.loads(capsys.readouterr().out.strip().split("\n")[-1])
        assert out["exists"] is False
        assert out["completed"] == []

    def test_load_existing(self, wiki, capsys):
        rw.checkpoint_save(str(wiki), "load-test", "a")
        rw.checkpoint_save(str(wiki), "load-test", "b", status="failed")

        # Clear captured output from saves
        capsys.readouterr()

        rw.checkpoint_load(str(wiki), "load-test")
        out = json.loads(capsys.readouterr().out.strip())
        assert out["exists"] is True
        assert "a" in out["completed"]
        assert "b" in out["failed"]

    def test_clear(self, wiki):
        rw.checkpoint_save(str(wiki), "clear-test", "item")
        cp_file = wiki / ".checkpoints" / "clear-test.json"
        assert cp_file.exists()

        rw.checkpoint_clear(str(wiki), "clear-test")
        assert not cp_file.exists()

    def test_clear_nonexistent(self, wiki, capsys):
        """Clearing a non-existent checkpoint doesn't error."""
        rw.checkpoint_clear(str(wiki), "nope")
        out = json.loads(capsys.readouterr().out.strip().split("\n")[-1])
        assert out["cleared"] is True

    # ── metadata ───────────────────────────────────────────────────────────

    def test_set_meta_creates_file(self, wiki):
        """set_meta on a task with no existing checkpoint creates the file."""
        rw.checkpoint_set_meta(str(wiki), "meta-new", "stash_ref", "stash@{0}")

        cp_file = wiki / ".checkpoints" / "meta-new.json"
        assert cp_file.exists()
        data = json.loads(cp_file.read_text())
        assert data["metadata"] == {"stash_ref": "stash@{0}"}
        assert data["completed"] == []
        assert data["failed"] == []

    def test_set_meta_preserves_lists(self, wiki):
        """set_meta must not clobber pre-existing completed/failed lists."""
        rw.checkpoint_save(str(wiki), "meta-task", "paper-1")
        rw.checkpoint_save(str(wiki), "meta-task", "paper-2", status="failed")
        rw.checkpoint_set_meta(str(wiki), "meta-task", "stash_ref", "stash@{2}")

        data = json.loads((wiki / ".checkpoints" / "meta-task.json").read_text())
        assert data["completed"] == ["paper-1"]
        assert data["failed"] == ["paper-2"]
        assert data["metadata"]["stash_ref"] == "stash@{2}"

    def test_set_meta_overwrites_value_but_not_sibling_keys(self, wiki):
        """Re-setting the same key updates it; other keys survive."""
        rw.checkpoint_set_meta(str(wiki), "meta-task", "stash_ref", "stash@{0}")
        rw.checkpoint_set_meta(str(wiki), "meta-task", "run_id", "abc")
        rw.checkpoint_set_meta(str(wiki), "meta-task", "stash_ref", "stash@{1}")

        data = json.loads((wiki / ".checkpoints" / "meta-task.json").read_text())
        assert data["metadata"] == {"stash_ref": "stash@{1}", "run_id": "abc"}

    def test_get_meta_single_key(self, wiki, capsys):
        rw.checkpoint_set_meta(str(wiki), "meta-task", "stash_ref", "stash@{0}")
        capsys.readouterr()  # clear save output

        rw.checkpoint_get_meta(str(wiki), "meta-task", "stash_ref")
        assert capsys.readouterr().out.strip() == "stash@{0}"

    def test_get_meta_missing_key_prints_empty(self, wiki, capsys):
        """A missing key prints an empty line, exit 0 — safe for bash capture."""
        rw.checkpoint_set_meta(str(wiki), "meta-task", "other", "x")
        capsys.readouterr()

        rw.checkpoint_get_meta(str(wiki), "meta-task", "stash_ref")
        assert capsys.readouterr().out.strip() == ""

    def test_get_meta_no_key_prints_dict(self, wiki, capsys):
        rw.checkpoint_set_meta(str(wiki), "meta-task", "stash_ref", "stash@{0}")
        rw.checkpoint_set_meta(str(wiki), "meta-task", "run_id", "abc")
        capsys.readouterr()

        rw.checkpoint_get_meta(str(wiki), "meta-task", "")
        out = json.loads(capsys.readouterr().out.strip())
        assert out == {"stash_ref": "stash@{0}", "run_id": "abc"}

    def test_get_meta_nonexistent_task(self, wiki, capsys):
        """Reading meta on a task with no checkpoint file returns empty."""
        rw.checkpoint_get_meta(str(wiki), "no-such-task", "anything")
        assert capsys.readouterr().out.strip() == ""

        rw.checkpoint_get_meta(str(wiki), "no-such-task", "")
        assert capsys.readouterr().out.strip() == "{}"

    def test_load_corrupt_checkpoint_reports_error(self, wiki, capsys):
        """Corrupt JSON must surface as exists:false + error — not silently become an empty checkpoint."""
        cp_dir = wiki / ".checkpoints"
        cp_dir.mkdir(parents=True, exist_ok=True)
        (cp_dir / "corrupt.json").write_text("{not valid json,,,")

        rw.checkpoint_load(str(wiki), "corrupt")
        out = json.loads(capsys.readouterr().out.strip())
        assert out["exists"] is False
        assert out.get("error") == "corrupt checkpoint"
        assert out["completed"] == []
        assert out["metadata"] == {}

    def test_load_non_dict_json_reports_error(self, wiki, capsys):
        """Top-level JSON that isn't a dict (e.g. a list) is also corruption."""
        cp_dir = wiki / ".checkpoints"
        cp_dir.mkdir(parents=True, exist_ok=True)
        (cp_dir / "bad-shape.json").write_text("[]")

        rw.checkpoint_load(str(wiki), "bad-shape")
        out = json.loads(capsys.readouterr().out.strip())
        assert out["exists"] is False
        assert out.get("error") == "corrupt checkpoint"

    def test_set_meta_repairs_corrupt_file(self, wiki):
        """Writers are permissive: set-meta on a corrupt file silently rewrites it fresh.

        This is intentional — we don't want a one-byte corruption to permanently wedge
        a long-running /init. The read path (checkpoint_load) still reports the
        corruption for one call, then the next write repairs it.
        """
        cp_dir = wiki / ".checkpoints"
        cp_dir.mkdir(parents=True, exist_ok=True)
        (cp_dir / "recover.json").write_text("garbage")

        rw.checkpoint_set_meta(str(wiki), "recover", "stash_ref", "stash@{0}")

        data = json.loads((cp_dir / "recover.json").read_text())
        assert data["metadata"] == {"stash_ref": "stash@{0}"}
        assert data["completed"] == []
        assert data["failed"] == []

    def test_set_meta_unicode_roundtrip(self, wiki, capsys):
        """ensure_ascii=False should preserve non-ASCII values end-to-end."""
        rw.checkpoint_set_meta(str(wiki), "i18n", "note", "初始化已完成 ✓")
        capsys.readouterr()

        rw.checkpoint_get_meta(str(wiki), "i18n", "note")
        assert capsys.readouterr().out.strip() == "初始化已完成 ✓"

    def test_load_old_checkpoint_without_metadata_field(self, wiki, capsys):
        """Backward compat: pre-metadata checkpoints load cleanly."""
        cp_dir = wiki / ".checkpoints"
        cp_dir.mkdir(parents=True, exist_ok=True)
        (cp_dir / "legacy.json").write_text(
            json.dumps({"task_id": "legacy", "completed": ["a"], "failed": []}))

        rw.checkpoint_load(str(wiki), "legacy")
        out = json.loads(capsys.readouterr().out.strip())
        assert out["exists"] is True
        assert out["completed"] == ["a"]
        assert out["metadata"] == {}

    def test_cli_set_get_meta(self, tmp_path):
        """End-to-end: CLI set-meta → CLI get-meta round-trip."""
        TOOL = str(Path(__file__).resolve().parent.parent / "tools" / "research_wiki.py")
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, TOOL, "init", str(wiki)],
                       capture_output=True)

        subprocess.run(
            [sys.executable, TOOL, "checkpoint-set-meta",
             str(wiki), "init-session", "stash_ref", "stash@{0}"],
            capture_output=True, check=True)

        # Single key → raw value on stdout (shell-capture-friendly)
        result = subprocess.run(
            [sys.executable, TOOL, "checkpoint-get-meta",
             str(wiki), "init-session", "stash_ref"],
            capture_output=True, text=True, check=True)
        assert result.stdout.strip() == "stash@{0}"

        # No key → JSON dict
        result = subprocess.run(
            [sys.executable, TOOL, "checkpoint-get-meta",
             str(wiki), "init-session"],
            capture_output=True, text=True, check=True)
        assert json.loads(result.stdout) == {"stash_ref": "stash@{0}"}

        # Missing key → empty output, exit 0
        result = subprocess.run(
            [sys.executable, TOOL, "checkpoint-get-meta",
             str(wiki), "init-session", "missing"],
            capture_output=True, text=True, check=True)
        assert result.stdout.strip() == ""

    def test_cli_checkpoint_roundtrip(self, tmp_path):
        TOOL = str(Path(__file__).resolve().parent.parent / "tools" / "research_wiki.py")
        wiki = tmp_path / "wiki"
        subprocess.run([sys.executable, TOOL, "init", str(wiki)],
                       capture_output=True)

        # Save
        result = subprocess.run(
            [sys.executable, TOOL, "checkpoint-save", str(wiki), "cli-test", "paper-1"],
            capture_output=True, text=True)
        assert result.returncode == 0

        # Save failed
        subprocess.run(
            [sys.executable, TOOL, "checkpoint-save", str(wiki), "cli-test", "paper-2", "--failed"],
            capture_output=True)

        # Load
        result = subprocess.run(
            [sys.executable, TOOL, "checkpoint-load", str(wiki), "cli-test"],
            capture_output=True, text=True)
        data = json.loads(result.stdout)
        assert "paper-1" in data["completed"]
        assert "paper-2" in data["failed"]

        # Clear
        result = subprocess.run(
            [sys.executable, TOOL, "checkpoint-clear", str(wiki), "cli-test"],
            capture_output=True, text=True)
        assert result.returncode == 0
