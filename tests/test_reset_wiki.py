"""Tests for tools/reset_wiki.py — scoped wiki reset helper."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import reset_wiki as rw  # noqa: E402


@pytest.fixture
def project(tmp_path):
    """Build a synthetic project root with wiki/, raw/, and seed content."""
    wiki = tmp_path / "wiki"
    for d in rw.ENTITY_DIRS + ["graph", "outputs"]:
        (wiki / d).mkdir(parents=True)
        (wiki / d / ".gitkeep").touch()
    (wiki / "CLAUDE.md").write_text("# product schema (must survive)")
    (wiki / "log.md").write_text("# OmegaWiki Log\n\n## [2026-04-10] something\n")
    (wiki / "index.md").write_text("# old index")
    (wiki / "graph" / "edges.jsonl").write_text('{"from":"a","to":"b","type":"supports"}\n')

    # Seed entity content
    (wiki / "papers" / "p1.md").write_text("---\ntitle: P1\n---\n")
    (wiki / "concepts" / "c1.md").write_text("---\ntitle: C1\n---\n")
    (wiki / "foundations" / "gradient-descent.md").write_text("---\ntitle: GD\n---\n")
    (wiki / "outputs" / "report.md").write_text("# old report")

    raw = tmp_path / "raw"
    for sub in rw.RAW_SUBDIRS:
        (raw / sub).mkdir(parents=True)
        (raw / sub / ".gitkeep").touch()
    (raw / "papers" / "x.pdf").write_bytes(b"PDF")
    (raw / "notes" / "n.md").write_text("notes")

    return tmp_path


def test_plan_wiki_lists_all_md(project):
    p = rw.plan(project, ["wiki"])
    deletes = set(p["delete_files"])
    assert "wiki/papers/p1.md" in deletes
    assert "wiki/concepts/c1.md" in deletes
    assert "wiki/foundations/gradient-descent.md" in deletes
    assert "wiki/outputs/report.md" in deletes
    # CLAUDE.md and log.md must NOT appear
    assert not any("CLAUDE.md" in f for f in deletes)
    assert not any("log.md" in f for f in deletes)


def test_execute_wiki_deletes_md_keeps_protected_files(project):
    rw.execute(project, ["wiki"])
    assert not (project / "wiki" / "papers" / "p1.md").exists()
    assert not (project / "wiki" / "foundations" / "gradient-descent.md").exists()
    # Protected
    assert (project / "wiki" / "CLAUDE.md").exists()
    assert (project / "wiki" / "log.md").exists()
    # .gitkeep preserved or recreated
    assert (project / "wiki" / "papers" / ".gitkeep").exists()
    assert (project / "wiki" / "foundations" / ".gitkeep").exists()
    # index.md regenerated with all 9 entities
    idx = (project / "wiki" / "index.md").read_text()
    for entity in rw.ENTITY_DIRS:
        assert f"{entity}:" in idx


def test_execute_wiki_resets_graph(project):
    rw.execute(project, ["wiki"])
    edges = (project / "wiki" / "graph" / "edges.jsonl").read_text()
    assert edges == ""


def test_execute_raw_deletes_files_keeps_gitkeep(project):
    rw.execute(project, ["raw"])
    assert not (project / "raw" / "papers" / "x.pdf").exists()
    assert not (project / "raw" / "notes" / "n.md").exists()
    assert (project / "raw" / "papers" / ".gitkeep").exists()
    assert (project / "raw" / "notes" / ".gitkeep").exists()


def test_execute_log_resets_to_template(project):
    rw.execute(project, ["log"])
    txt = (project / "wiki" / "log.md").read_text()
    assert txt == "# OmegaWiki Log\n\n"


def test_execute_all_combines_scopes(project):
    rw.execute(project, ["wiki", "raw", "log"])
    assert not (project / "wiki" / "papers" / "p1.md").exists()
    assert not (project / "raw" / "papers" / "x.pdf").exists()
    assert (project / "wiki" / "log.md").read_text() == "# OmegaWiki Log\n\n"
    assert (project / "wiki" / "CLAUDE.md").exists()


def test_cli_dry_run_does_not_modify(project):
    result = subprocess.run(
        [sys.executable, str(TOOLS_DIR / "reset_wiki.py"),
         "--scope", "wiki", "--project-root", str(project)],
        capture_output=True, text=True, check=True,
    )
    plan = json.loads(result.stdout)
    assert plan["status"] == "plan"
    # File still present
    assert (project / "wiki" / "papers" / "p1.md").exists()


def test_cli_unknown_scope_errors(project):
    result = subprocess.run(
        [sys.executable, str(TOOLS_DIR / "reset_wiki.py"),
         "--scope", "bogus", "--project-root", str(project)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "unknown scope" in result.stdout
