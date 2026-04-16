"""Tests for tools/init_discovery.py."""

from __future__ import annotations

import io
import json
import sys
import tarfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, "tools")
import init_discovery as disc  # noqa: E402


def _s2_paper(
    title: str,
    arxiv_id: str,
    *,
    year: int,
    citation: int,
    abstract: str = "",
) -> dict:
    return {
        "title": title,
        "abstract": abstract or title,
        "authors": [{"name": "Author"}],
        "year": year,
        "citationCount": citation,
        "venue": "TestConf",
        "externalIds": {"ArXiv": arxiv_id},
    }


@pytest.fixture
def raw_root(tmp_path):
    raw = tmp_path / "raw"
    for sub in ("papers", "notes", "web", "discovered", "tmp"):
        (raw / sub).mkdir(parents=True)
        (raw / sub / ".gitkeep").touch()
    return raw


def test_prepare_pdf_emits_canonical_tmp_tex(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning for LLMs\nAbstract\nImproves multilingual transfer.", []),
    )

    manifest = disc.prepare_inputs(raw_root)

    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")
    assert entry["prepared_path"].startswith("raw/tmp/papers/")
    assert entry["canonical_ingest_path"] == entry["prepared_path"]
    assert entry["ingest_format"] == "tex"
    assert (raw_root.parent / entry["canonical_ingest_path"]).exists()


def test_prepare_prefers_local_tex_over_pdf_for_same_paper(raw_root, monkeypatch):
    (raw_root / "papers" / "paper.tex").write_text(
        "\\title{Adapter Tuning for LLMs}\n\\begin{abstract}tex version\\end{abstract}\n",
        encoding="utf-8",
    )
    (raw_root / "papers" / "paper.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning for LLMs\nAbstract\npdf version", []),
    )

    manifest = disc.prepare_inputs(raw_root)
    paper_entries = [item for item in manifest["entries"] if item["source_kind"] == "paper"]

    assert len(paper_entries) == 1
    assert paper_entries[0]["source_path"] == "raw/papers/paper.tex"
    assert paper_entries[0]["canonical_ingest_path"] == "raw/papers/paper.tex"
    assert any("duplicate local source skipped" in warning for warning in paper_entries[0]["warnings"])


def test_prepare_translates_notes_into_tmp_sidecar(raw_root, monkeypatch):
    (raw_root / "notes" / "focus.md").write_text("我们想研究多语言 adapter tuning。", encoding="utf-8")
    monkeypatch.setattr(
        disc,
        "_translate_to_english",
        lambda text, _label: ("We want to study multilingual adapter tuning.", ["translated"]),
    )

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "notes")

    assert entry["translated_to_english"] is True
    assert entry["prepared_path"].startswith("raw/tmp/notes/")
    notes_web = disc.scan_notes_web(raw_root, prepared_manifest=manifest)
    assert "multilingual" in notes_web["keywords"]
    assert "adapter" in notes_web["keywords"]


def test_plan_warns_when_chinese_notes_are_detected(raw_root, monkeypatch):
    (raw_root / "notes" / "focus.md").write_text("我们想研究多语言 adapter tuning。", encoding="utf-8")
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("adapter tuning", raw_root, raw_root.parent / "wiki")

    assert plan["notes_web"]["chinese_note_count"] == 1
    assert any(
        warning["source"] == "notes_web_chinese"
        and "Curated Chinese support is planned" in warning["message"]
        for warning in plan["warnings"]
    )


def test_auto_detects_seeded_mode(raw_root, monkeypatch):
    (raw_root / "papers" / "2301.00001-adapter-paper.tex").write_text(
        "\\title{Adapter Tuning for LLMs}\n",
        encoding="utf-8",
    )
    (raw_root / "notes" / "focus.md").write_text(
        "Goal: improve adapter tuning for multilingual tasks.",
        encoding="utf-8",
    )
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("adapter tuning", raw_root, raw_root.parent / "wiki")

    assert plan["mode"] == "seeded"
    assert plan["local_papers"]
    assert "multilingual" in plan["notes_web"]["keywords"]
    assert plan["shortlist"][0]["user_owned"] is True


def test_seeded_mode_accepts_missing_topic(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.tex").write_text(
        "\\title{Adapter Tuning for LLMs}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("", raw_root, raw_root.parent / "wiki")

    assert plan["topic"] == ""
    assert plan["mode"] == "seeded"
    assert plan["shortlist"][0]["user_owned"] is True
    assert not plan["errors"]


def test_seeded_mode_without_external_hits_proceeds_with_local_papers(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.tex").write_text(
        "\\title{Completely Local Paper Without Arxiv}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("", raw_root, raw_root.parent / "wiki")

    assert [item["title"] for item in plan["shortlist"]] == ["Completely Local Paper Without Arxiv"]
    assert not plan["errors"]
    assert any(
        warning["source"] == "seeded_mode"
        and "proceeding with user-owned papers only" in warning["message"]
        for warning in plan["warnings"]
    )


def test_seeded_mode_without_topic_uses_local_terms_for_search_query(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.tex").write_text(
        "\\title{Adapter Tuning for LLMs}\n",
        encoding="utf-8",
    )
    queries: list[str] = []

    def _search(query, *_args, **_kwargs):
        queries.append(query)
        return []

    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", _search)
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    disc.build_plan("", raw_root, raw_root.parent / "wiki")

    assert queries
    assert "adapter" in queries[0].lower()


def test_plan_uses_prepared_manifest_canonical_paths(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning for LLMs\nAbstract\nImproves multilingual transfer.", []),
    )
    manifest = disc.prepare_inputs(raw_root)
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("adapter tuning", raw_root, raw_root.parent / "wiki", prepared_manifest=manifest)

    assert plan["local_papers"][0]["path"].startswith("raw/tmp/papers/")
    assert plan["shortlist"][0]["path"].startswith("raw/tmp/papers/")


def test_plan_cli_writes_output_plan_file(raw_root, monkeypatch, tmp_path, capsys):
    (raw_root / "papers" / "seed.tex").write_text("\\title{Adapter Tuning for LLMs}\n", encoding="utf-8")
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    prepare_manifest = tmp_path / "init-prepare.json"
    plan_json = tmp_path / "init-plan.json"
    prepare_manifest.write_text(json.dumps(disc.prepare_inputs(raw_root)), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "init_discovery.py",
            "plan",
            "--topic", "adapter tuning",
            "--raw-root", str(raw_root),
            "--wiki-root", str(raw_root.parent / "wiki"),
            "--prepared-manifest", str(prepare_manifest),
            "--output-plan", str(plan_json),
        ],
    )

    disc.main()
    captured = capsys.readouterr()

    assert plan_json.exists()
    assert json.loads(plan_json.read_text(encoding="utf-8"))["topic"] == "adapter tuning"
    assert json.loads(captured.out)["topic"] == "adapter tuning"


def test_plan_cli_allows_missing_topic(raw_root, monkeypatch, tmp_path, capsys):
    (raw_root / "papers" / "seed.tex").write_text("\\title{Adapter Tuning for LLMs}\n", encoding="utf-8")
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    prepare_manifest = tmp_path / "init-prepare.json"
    plan_json = tmp_path / "init-plan.json"
    prepare_manifest.write_text(json.dumps(disc.prepare_inputs(raw_root)), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "init_discovery.py",
            "plan",
            "--raw-root", str(raw_root),
            "--wiki-root", str(raw_root.parent / "wiki"),
            "--prepared-manifest", str(prepare_manifest),
            "--output-plan", str(plan_json),
        ],
    )

    disc.main()
    captured = capsys.readouterr()

    assert plan_json.exists()
    assert json.loads(plan_json.read_text(encoding="utf-8"))["topic"] == ""
    assert json.loads(captured.out)["topic"] == ""


def test_auto_detects_bootstrap_mode(raw_root, monkeypatch):
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [
        _s2_paper("A Survey of Adapter Methods", "2401.00001", year=2024, citation=120, abstract="survey"),
        _s2_paper("Fresh Adapter Benchmark", "2403.00002", year=2024, citation=30, abstract="benchmark"),
    ])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("adapter tuning", raw_root, raw_root.parent / "wiki")

    assert plan["mode"] == "bootstrap"
    assert any(item["is_survey"] for item in plan["shortlist"])


def test_no_introduction_returns_only_local_papers(raw_root, monkeypatch):
    (raw_root / "papers" / "2401.12345-topic.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [
        _s2_paper("External Result", "2402.00002", year=2024, citation=50)
    ])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])

    plan = disc.build_plan(
        "topic",
        raw_root,
        raw_root.parent / "wiki",
        allow_introduction=False,
    )

    assert plan["allow_introduction"] is False
    assert len(plan["shortlist"]) == 1
    assert all(item["user_owned"] for item in plan["shortlist"])


def test_deepxiv_unavailable_falls_back_to_s2(raw_root, monkeypatch):
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [
        _s2_paper("Fallback Paper", "2402.00001", year=2024, citation=18)
    ])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("no token")))
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("fallback topic", raw_root, raw_root.parent / "wiki")

    assert any(item["title"] == "Fallback Paper" for item in plan["shortlist"])
    assert any(warning["source"] == "search_deepxiv" for warning in plan["warnings"])


def test_dedup_merges_s2_and_deepxiv_hits(raw_root, monkeypatch):
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [
        _s2_paper("Merged Paper", "2401.00009", year=2024, citation=80)
    ])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [
        {
            "arxiv_id": "2401.00009",
            "title": "Merged Paper",
            "abstract": "semantic hit",
            "authors": ["Author"],
            "year": 2024,
            "citation_count": 50,
            "relevance_score": 0.92,
        }
    ])
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("merged paper", raw_root, raw_root.parent / "wiki")
    merged = [c for c in plan["candidates"] if c["title"] == "Merged Paper"]

    assert len(merged) == 1
    assert set(merged[0]["source_channels"]) == {"search_s2", "search_deepxiv"}


def test_deepxiv_relevance_is_used_explicitly_in_scoring():
    candidates = [
        {
            "candidate_id": "deepxiv-high",
            "title": "Unusual phrasing paper",
            "abstract": "little lexical overlap here",
            "year": disc.CURRENT_YEAR,
            "citation_count": 10,
            "source_channels": ["search_deepxiv"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.95,
            "user_owned": False,
        },
        {
            "candidate_id": "lexical-only",
            "title": "Adapter tuning methods",
            "abstract": "adapter tuning multilingual",
            "year": disc.CURRENT_YEAR,
            "citation_count": 10,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.0,
            "user_owned": False,
        },
    ]

    scored = disc._score_candidates(
        candidates,
        "bootstrap",
        ["adapter", "tuning"],
        ["multilingual"],
        [],
        [],
    )

    deepxiv_candidate = next(item for item in scored if item["candidate_id"] == "deepxiv-high")
    assert deepxiv_candidate["score_components"]["deepxiv_relevance"] == 0.95
    assert deepxiv_candidate["score_components"]["lexical_relevance"] == 0.0


def test_seeded_anchor_bonus_helps_connected_paper():
    candidates = [
        {
            "candidate_id": "arxiv:a",
            "title": "Connected Adapter Tuning",
            "abstract": "adapter tuning multilingual",
            "year": disc.CURRENT_YEAR,
            "citation_count": 10,
            "source_channels": ["citation"],
            "anchor_sources": ["local:seed"],
            "deepxiv_relevance_score": None,
            "user_owned": False,
        },
        {
            "candidate_id": "arxiv:b",
            "title": "Unconnected Adapter Tuning",
            "abstract": "adapter tuning multilingual",
            "year": disc.CURRENT_YEAR,
            "citation_count": 10,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": None,
            "user_owned": False,
        },
    ]

    scored = disc._score_candidates(
        candidates,
        "seeded",
        ["adapter", "tuning"],
        ["multilingual"],
        ["adapter", "tuning"],
        [],
    )

    assert scored[0]["candidate_id"] == "arxiv:a"
    assert scored[0]["score_components"]["anchor_bonus"] > scored[1]["score_components"]["anchor_bonus"]


def test_exclusion_terms_penalize_candidate():
    candidates = [
        {
            "candidate_id": "exclude-me",
            "title": "Vision Adapter Tuning",
            "abstract": "vision adapter tuning",
            "year": disc.CURRENT_YEAR,
            "citation_count": 40,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.8,
            "user_owned": False,
        },
        {
            "candidate_id": "keep-me",
            "title": "Language Adapter Tuning",
            "abstract": "language adapter tuning",
            "year": disc.CURRENT_YEAR,
            "citation_count": 40,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.8,
            "user_owned": False,
        },
    ]

    scored = disc._score_candidates(
        candidates,
        "bootstrap",
        ["adapter", "tuning"],
        ["language"],
        [],
        ["vision"],
    )

    assert scored[0]["candidate_id"] == "keep-me"
    excluded = next(item for item in scored if item["candidate_id"] == "exclude-me")
    assert excluded["score_components"]["exclusion_penalty"] < 0


def test_freshness_beats_multiple_old_papers_after_anchor_slot():
    candidates = [
        {
            "candidate_id": "old-1",
            "title": "Canonical Old Adapter Paper",
            "abstract": "adapter tuning",
            "year": disc.CURRENT_YEAR - 8,
            "citation_count": 5000,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.6,
            "user_owned": False,
            "cluster": "adapter",
            "is_survey": False,
            "total_score": 80.0,
        },
        {
            "candidate_id": "old-2",
            "title": "Another Old Adapter Paper",
            "abstract": "adapter tuning",
            "year": disc.CURRENT_YEAR - 7,
            "citation_count": 4200,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.58,
            "user_owned": False,
            "cluster": "adapter",
            "is_survey": False,
            "total_score": 79.0,
        },
        {
            "candidate_id": "fresh-1",
            "title": "Fresh Adapter Benchmark",
            "abstract": "adapter benchmark",
            "year": disc.CURRENT_YEAR,
            "citation_count": 80,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.8,
            "user_owned": False,
            "cluster": "benchmark",
            "is_survey": False,
            "total_score": 74.0,
        },
    ]

    shortlist = disc._select_shortlist(candidates, "bootstrap", 0, True)
    old_selected = [item for item in shortlist if item["candidate_id"].startswith("old")]

    assert len(old_selected) <= 1
    assert any(item["candidate_id"] == "fresh-1" for item in shortlist)


def test_diversity_penalty_improves_early_cluster_mix():
    candidates = [
        {
            "candidate_id": "same-1",
            "title": "Adapter Variant One",
            "abstract": "adapter tuning",
            "year": disc.CURRENT_YEAR,
            "citation_count": 100,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.8,
            "user_owned": False,
            "cluster": "adapter",
            "is_survey": False,
            "total_score": 88.0,
        },
        {
            "candidate_id": "same-2",
            "title": "Adapter Variant Two",
            "abstract": "adapter tuning",
            "year": disc.CURRENT_YEAR,
            "citation_count": 95,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.79,
            "user_owned": False,
            "cluster": "adapter",
            "is_survey": False,
            "total_score": 87.0,
        },
        {
            "candidate_id": "other-1",
            "title": "Mixture Routing Method",
            "abstract": "routing experts",
            "year": disc.CURRENT_YEAR,
            "citation_count": 70,
            "source_channels": ["search_s2"],
            "anchor_sources": [],
            "deepxiv_relevance_score": 0.7,
            "user_owned": False,
            "cluster": "routing",
            "is_survey": False,
            "total_score": 82.0,
        },
    ]

    shortlist = disc._select_shortlist(candidates, "bootstrap", 0, True)
    first_three = [item["cluster"] for item in shortlist[:3]]
    assert "routing" in first_three


def test_seeded_mode_uses_relevant_local_anchor(raw_root, monkeypatch):
    fixtures = [
        ("a-2301.00001-vision.tex", "\\title{Vision Transformers for Images}\n"),
        ("b-2301.00002-graph.tex", "\\title{Graph Mining Basics}\n"),
        ("c-2301.00003-diffusion.tex", "\\title{Diffusion for Images}\n"),
        ("z-2301.00004-adapter.tex", "\\title{Adapter Tuning for LLMs}\n"),
    ]
    for name, content in fixtures:
        (raw_root / "papers" / name).write_text(content, encoding="utf-8")

    called: list[str] = []

    def _citations(arxiv_id, *_args, **_kwargs):
        called.append(arxiv_id)
        return []

    monkeypatch.setattr(disc, "s2_citations", _citations)
    monkeypatch.setattr(disc, "s2_references", _citations)
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    disc.build_plan("adapter tuning", raw_root, raw_root.parent / "wiki")

    assert "2301.00004" in called


def test_extract_old_style_arxiv_id():
    assert disc._extract_arxiv_id("classic identifier cs/9901001 in title") == "cs/9901001"


def test_download_source_rejects_archive_escape_and_falls_back_to_pdf(raw_root, monkeypatch):
    archive_bytes = io.BytesIO()
    with tarfile.open(fileobj=archive_bytes, mode="w:gz") as tar:
        payload = b"escape"
        info = tarfile.TarInfo("../escape.txt")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))

    source_resp = MagicMock()
    source_resp.ok = True
    source_resp.content = archive_bytes.getvalue()
    source_resp.headers = {"Content-Type": "application/gzip"}

    pdf_resp = MagicMock()
    pdf_resp.ok = True
    pdf_resp.content = b"%PDF-1.7\n"
    pdf_resp.headers = {"Content-Type": "application/pdf"}
    pdf_resp.raise_for_status.return_value = None

    monkeypatch.setattr(disc.requests, "get", MagicMock(side_effect=[source_resp, pdf_resp]))

    result = disc._download_source(
        {"candidate_id": "arxiv:2401.00001", "title": "Safe Fetch", "arxiv_id": "2401.00001"},
        raw_root,
    )

    assert result["status"] == "downloaded_pdf"
    assert not (raw_root / "discovered" / "escape.txt").exists()
    assert not (raw_root / "discovered" / "safe-fetch").exists()
    assert (raw_root / "discovered" / "safe-fetch.pdf").exists()


def test_fetch_writes_into_raw_discovered_only(raw_root, monkeypatch, tmp_path):
    plan_json = tmp_path / "plan.json"
    plan_json.write_text(json.dumps({
        "shortlist": [{
            "candidate_id": "arxiv:2401.00001",
            "title": "Fetched Paper",
            "arxiv_id": "2401.00001",
        }]
    }), encoding="utf-8")

    source_fail = MagicMock()
    source_fail.ok = False
    pdf_ok = MagicMock()
    pdf_ok.raise_for_status.return_value = None
    pdf_ok.content = b"%PDF-1.4"
    monkeypatch.setattr(disc.requests, "get", lambda url, **_kwargs: source_fail if "e-print" in url else pdf_ok)

    result = disc.fetch_from_plan(raw_root, plan_json, ["arxiv:2401.00001"])

    assert result["results"][0]["status"] == "downloaded_pdf"
    assert (raw_root / "discovered" / "fetched-paper.pdf").exists()
    assert not any((raw_root / "papers").glob("*.pdf"))


def test_fetch_skips_prepared_local_duplicate_and_writes_source_manifest(raw_root, monkeypatch, tmp_path):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Fetched Paper\nAbstract\nAdapter tuning setup.", []),
    )
    prepare_manifest = disc.prepare_inputs(raw_root)
    prepare_json = tmp_path / "prepare.json"
    prepare_json.write_text(json.dumps(prepare_manifest), encoding="utf-8")

    plan_json = tmp_path / "plan.json"
    plan_json.write_text(json.dumps({
        "shortlist": [
            {
                "candidate_id": "local:fetched-paper",
                "title": "Fetched Paper",
                "user_owned": True,
                "shortlist_rank": 1,
            },
            {
                "candidate_id": "arxiv:2401.00001",
                "title": "Fetched Paper",
                "arxiv_id": "2401.00001",
                "user_owned": False,
                "shortlist_rank": 2,
            },
        ],
        "candidates": [],
    }), encoding="utf-8")
    output_sources = tmp_path / "init-sources.json"

    result = disc.fetch_from_plan(
        raw_root,
        plan_json,
        ["arxiv:2401.00001"],
        prepared_manifest_json=prepare_json,
        output_sources=output_sources,
    )

    assert result["results"][0]["status"] == "skipped_local_duplicate"
    sources = result["source_manifest"]["sources"]
    assert len(sources) == 1
    assert sources[0]["origin"] == "user_local"
    assert sources[0]["canonical_ingest_path"].startswith("raw/tmp/papers/")
    assert output_sources.exists()
    assert not any((raw_root / "discovered").glob("*.pdf"))


def test_fetch_writes_mixed_source_manifest_from_tmp_and_discovered(raw_root, monkeypatch, tmp_path):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Seed Paper\nAbstract\nLocal adapter seed.", []),
    )
    prepare_manifest = disc.prepare_inputs(raw_root)
    prepare_json = tmp_path / "prepare.json"
    prepare_json.write_text(json.dumps(prepare_manifest), encoding="utf-8")

    plan_json = tmp_path / "plan.json"
    plan_json.write_text(json.dumps({
        "shortlist": [
            {
                "candidate_id": "local:seed-paper",
                "title": "Seed Paper",
                "user_owned": True,
                "shortlist_rank": 1,
            },
            {
                "candidate_id": "arxiv:2402.00002",
                "title": "Fresh External",
                "arxiv_id": "2402.00002",
                "user_owned": False,
                "shortlist_rank": 2,
            },
        ],
        "candidates": [],
    }), encoding="utf-8")

    source_fail = MagicMock()
    source_fail.ok = False
    pdf_ok = MagicMock()
    pdf_ok.raise_for_status.return_value = None
    pdf_ok.content = b"%PDF-1.4"
    monkeypatch.setattr(disc.requests, "get", lambda url, **_kwargs: source_fail if "e-print" in url else pdf_ok)

    output_sources = tmp_path / "init-sources.json"
    result = disc.fetch_from_plan(
        raw_root,
        plan_json,
        ["arxiv:2402.00002"],
        prepared_manifest_json=prepare_json,
        output_sources=output_sources,
    )

    sources = result["source_manifest"]["sources"]
    assert [item["origin"] for item in sources] == ["user_local", "introduced"]
    assert sources[0]["canonical_ingest_path"].startswith("raw/tmp/papers/")
    assert sources[1]["canonical_ingest_path"] == "raw/discovered/fresh-external.pdf"
    assert sources[1]["discovered_path"] == "raw/discovered/fresh-external.pdf"
    assert sources[1]["ingest_format"] == "pdf"
    assert [item["shortlist_rank"] for item in sources] == [1, 2]
    assert output_sources.exists()


def test_download_to_discovered_writes_under_raw_discovered(raw_root, monkeypatch):
    class _Resp:
        def __init__(self, *, ok=True, content=b"", headers=None):
            self.ok = ok
            self.content = content
            self.headers = headers or {}

        def raise_for_status(self):
            if not self.ok:
                raise disc.requests.RequestException("bad status")

    def _fake_get(url, **_kwargs):
        if "/e-print/" in url:
            raise disc.requests.RequestException("no source tarball")
        if "/pdf/" in url:
            return _Resp(content=b"%PDF-1.4 test", headers={"Content-Type": "application/pdf"})
        raise AssertionError(url)

    monkeypatch.setattr(disc.requests, "get", _fake_get)

    result = disc.download_to_discovered(raw_root, "2401.00009", "Fresh External")

    assert result["status"] == "downloaded_pdf"
    assert Path(result["canonical_ingest_path"]).parent == raw_root / "discovered"
    assert Path(result["canonical_ingest_path"]).exists()
