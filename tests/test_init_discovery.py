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


def _shortlist_candidate(
    candidate_id: str,
    title: str,
    *,
    year: int,
    citation_count: int,
    total_score: float,
    cluster: str,
    user_owned: bool = False,
    is_survey: bool = False,
    deepxiv_relevance_score: float = 0.0,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "title": title,
        "abstract": title,
        "year": year,
        "citation_count": citation_count,
        "source_channels": ["search_s2"],
        "anchor_sources": [],
        "deepxiv_relevance_score": deepxiv_relevance_score,
        "user_owned": user_owned,
        "cluster": cluster,
        "is_survey": is_survey,
        "total_score": total_score,
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
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])

    manifest = disc.prepare_inputs(raw_root)

    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")
    assert entry["prepared_path"].startswith("raw/tmp/papers/")
    assert entry["canonical_ingest_path"] == entry["prepared_path"]
    assert entry["ingest_format"] == "tex"
    assert "translated_to_english" not in entry
    assert "original_language" not in entry
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
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])

    manifest = disc.prepare_inputs(raw_root)
    paper_entries = [item for item in manifest["entries"] if item["source_kind"] == "paper"]

    assert len(paper_entries) == 1
    assert paper_entries[0]["source_path"] == "raw/papers/paper.tex"
    assert paper_entries[0]["canonical_ingest_path"] == "raw/papers/paper.tex"
    assert "translated_to_english" not in paper_entries[0]
    assert "original_language" not in paper_entries[0]
    assert any("duplicate local source skipped" in warning for warning in paper_entries[0]["warnings"])


def test_prepare_notes_keep_original_paths(raw_root):
    (raw_root / "notes" / "focus.md").write_text("我们想研究多语言 adapter tuning。", encoding="utf-8")

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "notes")

    assert entry["source_path"] == "raw/notes/focus.md"
    assert entry["prepared_path"] is None
    assert entry["canonical_ingest_path"] == "raw/notes/focus.md"
    assert entry["canonical_read_path"] == "raw/notes/focus.md"
    assert "translated_to_english" not in entry
    assert "original_language" not in entry
    notes_web = disc.scan_notes_web(raw_root, prepared_manifest=manifest)
    assert notes_web["files"][0]["canonical_path"] == "raw/notes/focus.md"
    assert "translated_to_english" not in notes_web["files"][0]
    assert "original_language" not in notes_web["files"][0]
    assert "adapter" in notes_web["keywords"]
    assert "tuning" in notes_web["keywords"]


def test_plan_warns_when_chinese_notes_are_detected(raw_root, monkeypatch):
    (raw_root / "notes" / "focus.md").write_text("我们想研究多语言 adapter tuning。", encoding="utf-8")
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "deepxiv_search", lambda *_args, **_kwargs: [])

    plan = disc.build_plan("adapter tuning", raw_root, raw_root.parent / "wiki")

    assert "chinese_note_count" not in plan["notes_web"]
    assert "chinese_web_count" not in plan["notes_web"]
    assert "untranslated_chinese_count" not in plan["notes_web"]
    assert all("translated_to_english" not in item for item in plan["notes_web"]["files"])
    assert all("original_language" not in item for item in plan["notes_web"]["files"])
    assert any(
        warning["source"] == "notes_web_chinese"
        and "lower-confidence" in warning["message"]
        and "planned for a later release" not in warning["message"]
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
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
    manifest = disc.prepare_inputs(raw_root)
    monkeypatch.setattr(disc, "s2_citations", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(disc, "s2_references", lambda *_args, **_kwargs: [])
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


def test_bootstrap_keeps_one_old_anchor_without_piling():
    candidates = [
        _shortlist_candidate(
            "old-1",
            "Canonical Old Adapter Paper",
            year=disc.CURRENT_YEAR - 8,
            citation_count=5000,
            total_score=80.0,
            cluster="adapter",
            deepxiv_relevance_score=0.6,
        ),
        _shortlist_candidate(
            "old-2",
            "Another Old Adapter Paper",
            year=disc.CURRENT_YEAR - 7,
            citation_count=4200,
            total_score=79.0,
            cluster="adapter-2",
            deepxiv_relevance_score=0.58,
        ),
        _shortlist_candidate(
            "fresh-1",
            "Fresh Adapter Benchmark",
            year=disc.CURRENT_YEAR,
            citation_count=80,
            total_score=74.0,
            cluster="benchmark",
            deepxiv_relevance_score=0.8,
        ),
    ]

    shortlist = disc._select_shortlist(candidates, "bootstrap", 0, True)
    old_selected = [item for item in shortlist if item["candidate_id"].startswith("old")]

    assert [item["candidate_id"] for item in old_selected] == ["old-1"]
    assert any(item["candidate_id"] == "fresh-1" for item in shortlist)


def test_seeded_with_little_room_prefers_fresh_papers_before_old_anchor():
    local_candidates = [
        _shortlist_candidate(
            f"local-{idx}",
            f"Local Seed {idx}",
            year=disc.CURRENT_YEAR,
            citation_count=0,
            total_score=100.0 - idx,
            cluster=f"local-{idx}",
            user_owned=True,
        )
        for idx in range(8)
    ]
    external_candidates = [
        _shortlist_candidate(
            "old-1",
            "Canonical Old Adapter Paper",
            year=disc.CURRENT_YEAR - 8,
            citation_count=5000,
            total_score=92.0,
            cluster="old-a",
        ),
        _shortlist_candidate(
            "old-2",
            "Another Old Adapter Paper",
            year=disc.CURRENT_YEAR - 7,
            citation_count=4200,
            total_score=90.0,
            cluster="old-b",
        ),
        _shortlist_candidate(
            "fresh-1",
            "Fresh Adapter Benchmark",
            year=disc.CURRENT_YEAR,
            citation_count=150,
            total_score=86.0,
            cluster="fresh-a",
        ),
        _shortlist_candidate(
            "fresh-2",
            "Fresh Routing Method",
            year=disc.CURRENT_YEAR - 1,
            citation_count=120,
            total_score=85.0,
            cluster="fresh-b",
        ),
        _shortlist_candidate(
            "fresh-3",
            "Fresh Mixture Method",
            year=disc.CURRENT_YEAR - 1,
            citation_count=110,
            total_score=84.0,
            cluster="fresh-c",
        ),
    ]

    shortlist = disc._select_shortlist(local_candidates + external_candidates, "seeded", 8, True)
    introduced_ids = [item["candidate_id"] for item in shortlist if not item["user_owned"]]
    old_selected = [candidate_id for candidate_id in introduced_ids if candidate_id.startswith("old")]

    assert introduced_ids[:3] == ["fresh-1", "fresh-2", "fresh-3"]
    assert old_selected == ["old-1"]


def test_seeded_with_little_room_caps_old_external_papers_at_one():
    local_candidates = [
        _shortlist_candidate(
            f"local-{idx}",
            f"Local Seed {idx}",
            year=disc.CURRENT_YEAR,
            citation_count=0,
            total_score=100.0 - idx,
            cluster=f"local-{idx}",
            user_owned=True,
        )
        for idx in range(8)
    ]
    external_candidates = [
        _shortlist_candidate(
            "old-1",
            "Canonical Old Adapter Paper",
            year=disc.CURRENT_YEAR - 9,
            citation_count=7000,
            total_score=96.0,
            cluster="old-a",
        ),
        _shortlist_candidate(
            "old-2",
            "Classic Old Routing Paper",
            year=disc.CURRENT_YEAR - 8,
            citation_count=6500,
            total_score=95.0,
            cluster="old-b",
        ),
        _shortlist_candidate(
            "old-3",
            "Historic Old Prompting Paper",
            year=disc.CURRENT_YEAR - 7,
            citation_count=6000,
            total_score=94.0,
            cluster="old-c",
        ),
        _shortlist_candidate(
            "fresh-1",
            "Fresh Adapter Benchmark",
            year=disc.CURRENT_YEAR,
            citation_count=60,
            total_score=70.0,
            cluster="fresh-a",
        ),
        _shortlist_candidate(
            "fresh-2",
            "Fresh Routing Method",
            year=disc.CURRENT_YEAR - 1,
            citation_count=55,
            total_score=69.0,
            cluster="fresh-b",
        ),
        _shortlist_candidate(
            "fresh-3",
            "Fresh Mixture Method",
            year=disc.CURRENT_YEAR - 1,
            citation_count=50,
            total_score=68.0,
            cluster="fresh-c",
        ),
        _shortlist_candidate(
            "fresh-4",
            "Fresh Retrieval Method",
            year=disc.CURRENT_YEAR - 1,
            citation_count=45,
            total_score=67.0,
            cluster="fresh-d",
        ),
    ]

    shortlist = disc._select_shortlist(local_candidates + external_candidates, "seeded", 8, True)
    old_selected = [
        item["candidate_id"]
        for item in shortlist
        if not item["user_owned"] and item["candidate_id"].startswith("old")
    ]

    assert old_selected == ["old-1"]


def test_roomy_seeded_mode_can_still_keep_one_old_anchor():
    local_candidates = [
        _shortlist_candidate(
            f"local-{idx}",
            f"Local Seed {idx}",
            year=disc.CURRENT_YEAR,
            citation_count=0,
            total_score=100.0 - idx,
            cluster=f"local-{idx}",
            user_owned=True,
        )
        for idx in range(4)
    ]
    external_candidates = [
        _shortlist_candidate(
            "old-1",
            "Canonical Old Adapter Paper",
            year=disc.CURRENT_YEAR - 8,
            citation_count=5000,
            total_score=85.0,
            cluster="old-a",
        ),
        _shortlist_candidate(
            "old-2",
            "Classic Old Routing Paper",
            year=disc.CURRENT_YEAR - 7,
            citation_count=4500,
            total_score=82.0,
            cluster="old-b",
        ),
        _shortlist_candidate(
            "fresh-1",
            "Fresh Adapter Benchmark",
            year=disc.CURRENT_YEAR,
            citation_count=120,
            total_score=84.0,
            cluster="fresh-a",
        ),
        _shortlist_candidate(
            "fresh-2",
            "Fresh Routing Method",
            year=disc.CURRENT_YEAR - 1,
            citation_count=110,
            total_score=83.0,
            cluster="fresh-b",
        ),
        _shortlist_candidate(
            "fresh-3",
            "Fresh Mixture Method",
            year=disc.CURRENT_YEAR - 1,
            citation_count=95,
            total_score=80.0,
            cluster="fresh-c",
        ),
    ]

    shortlist = disc._select_shortlist(local_candidates + external_candidates, "seeded", 4, True)
    introduced_ids = [item["candidate_id"] for item in shortlist if not item["user_owned"]]
    old_selected = [candidate_id for candidate_id in introduced_ids if candidate_id.startswith("old")]

    assert "old-1" in introduced_ids
    assert old_selected == ["old-1"]
    assert "fresh-1" in introduced_ids


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
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
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
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [])
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


def test_prepare_pdf_recovers_arxiv_id_by_title(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning for LLMs\nAbstract\nImproves multilingual transfer.", []),
    )

    def _fake_s2_search(query, limit=5):
        if "adapter tuning" in query.lower():
            return [
                {
                    "title": "Adapter Tuning for LLMs",
                    "abstract": "Improves multilingual transfer.",
                    "authors": [{"name": "Author"}],
                    "year": 2024,
                    "citationCount": 50,
                    "venue": "TestConf",
                    "externalIds": {"ArXiv": "2401.00001"},
                    "url": "https://arxiv.org/abs/2401.00001",
                }
            ]
        return []

    monkeypatch.setattr(disc, "s2_search", _fake_s2_search)

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Adapter Tuning for LLMs}\n"
            "\\begin{abstract}\nImproves multilingual transfer.\n\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(disc, "_download_arxiv_source", _fake_download)

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["arxiv_id"] == "2401.00001"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
    assert entry["ingest_format"] == "directory"
    assert (raw_root.parent / entry["canonical_ingest_path"]).exists()


def test_prepare_pdf_prefers_arxiv_tex_over_synthetic(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning for LLMs\nAbstract\nSome content.", []),
    )
    monkeypatch.setattr(
        disc,
        "s2_search",
        lambda query, limit=5: [
            {
                "title": "Adapter Tuning for LLMs",
                "externalIds": {"ArXiv": "2401.00002"},
            }
        ],
    )

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text("\\title{Adapter Tuning for LLMs}\n", encoding="utf-8")
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(disc, "_download_arxiv_source", _fake_download)

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["original_format"] == "pdf"
    assert entry["ingest_format"] == "directory"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
    assert "recovered arXiv ID" in entry["warnings"][0]


def test_prepare_pdf_falls_back_to_synthetic_when_tex_unavailable(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning for LLMs\nAbstract\nSome content.", []),
    )
    monkeypatch.setattr(
        disc,
        "s2_search",
        lambda query, limit=5: [
            {
                "title": "Adapter Tuning for LLMs",
                "externalIds": {"ArXiv": "2401.00003"},
            }
        ],
    )
    monkeypatch.setattr(
        disc,
        "_download_arxiv_source",
        lambda _arxiv_id, _dest: {"success": False, "format": "", "error": "no source tarball"},
    )

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["arxiv_id"] == "2401.00003"
    assert entry["canonical_ingest_path"].endswith(".tex")
    assert entry["ingest_format"] == "tex"
    assert any("TeX source download failed" in w for w in entry["warnings"])


def test_prepare_pdf_arxiv_recovery_warns_on_api_failure(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning for LLMs\nAbstract\nSome content.", []),
    )
    monkeypatch.setattr(
        disc,
        "s2_search",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("network down")),
    )

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["usable"] is True
    assert entry["canonical_ingest_path"].endswith(".tex")
    assert entry["arxiv_id"] == ""


def test_prepare_pdf_skips_title_search_when_arxiv_id_in_text(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: (
            "arXiv:2401.00004\nAdapter Tuning for LLMs\nAbstract\nSome content.",
            [],
        ),
    )

    calls = []

    def _spy_s2_search(query, limit=5):
        calls.append(query)
        return []

    monkeypatch.setattr(disc, "s2_search", _spy_s2_search)

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Adapter Tuning for LLMs}\n"
            "\\begin{abstract}\nSome content.\n\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(disc, "_download_arxiv_source", _fake_download)

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["arxiv_id"] == "2401.00004"
    assert not calls  # s2_search should not have been called


def test_guess_title_skips_conference_header():
    text = "Published as a conference paper at ICLR 2023\nReal Paper Title Here\nAbstract\nSome content."
    assert disc._guess_title_from_text(text, "fallback") == "Real Paper Title Here"


def test_guess_title_skips_arxiv_line():
    text = "arXiv:2401.00001 [cs.CL]\nActual Paper Title\nAbstract\nContent."
    assert disc._guess_title_from_text(text, "fallback") == "Actual Paper Title"


def test_extract_arxiv_id_from_pdf_metadata(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "meta.pdf"
    pdf_path.write_bytes(b"%PDF")

    class FakeDoc:
        def __init__(self, metadata):
            self.metadata = metadata
        def close(self):
            pass

    class FakeFitz:
        @staticmethod
        def open(path):
            return FakeDoc({"subject": "See arXiv:2106.09685", "keywords": "", "title": ""})

    monkeypatch.setattr(disc, "HAS_PYMUPDF", True)
    monkeypatch.setattr(disc, "fitz", FakeFitz())

    result = disc._extract_arxiv_id_from_pdf_metadata(pdf_path)
    assert result == "2106.09685"


def test_extract_arxiv_id_from_pdf_metadata_tries_all_fields(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "meta.pdf"
    pdf_path.write_bytes(b"%PDF")

    class FakeDoc:
        def __init__(self, metadata):
            self.metadata = metadata
        def close(self):
            pass

    class FakeFitz:
        @staticmethod
        def open(path):
            return FakeDoc({"subject": "", "keywords": "", "title": "Paper on arXiv:2107.00001"})

    monkeypatch.setattr(disc, "HAS_PYMUPDF", True)
    monkeypatch.setattr(disc, "fitz", FakeFitz())

    result = disc._extract_arxiv_id_from_pdf_metadata(pdf_path)
    assert result == "2107.00001"


def test_extract_arxiv_source_metadata_reads_title_and_abstract(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "main.tex").write_text(
        "\\title{Adapter Tuning for LLMs}\n"
        "\\begin{abstract}\nImproves multilingual transfer.\n\\end{abstract}\n",
        encoding="utf-8",
    )
    result = disc._extract_arxiv_source_metadata(source_dir)
    assert result["source_title"] == "Adapter Tuning for LLMs"
    assert result["source_abstract"] == "Improves multilingual transfer."


def test_extract_arxiv_source_metadata_handles_missing_title_tex(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "main.tex").write_text(
        "\\section{Body}\nNo title here.\n",
        encoding="utf-8",
    )
    result = disc._extract_arxiv_source_metadata(source_dir)
    assert result == {"source_title": "", "source_abstract": ""}


def test_prepare_pdf_refreshes_metadata_from_accepted_arxiv_source(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: (
            "Adapter Tuning\n"
            "Abstract\n"
            "We study efficient multilingual transfer for large language models with low-rank adapters "
            "and parameter-efficient finetuning.",
            [],
        ),
    )
    monkeypatch.setattr(
        disc,
        "s2_search",
        lambda query, limit=5: [
            {
                "title": "Adapter Tuning for Large Language Models",
                "externalIds": {"ArXiv": "2401.00005"},
            }
        ],
    )

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Adapter Tuning for Large Language Models}\n"
            "\\begin{abstract}\n"
            "We study efficient multilingual transfer for large language models with low-rank adapters "
            "and parameter-efficient finetuning.\n"
            "\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(disc, "_download_arxiv_source", _fake_download)

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["title"] == "Adapter Tuning for Large Language Models"
    assert entry["candidate_id"] == f"local:{disc.slugify('Adapter Tuning for Large Language Models')}"
    assert entry["abstract_excerpt"].startswith("We study efficient multilingual transfer")
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")


def test_prepare_pdf_keeps_fetched_source_with_weak_local_abstract(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning\nAbstract\nBrief note.", []),
    )
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [
        {"title": "Adapter Tuning for Large Language Models", "externalIds": {"ArXiv": "2401.00001"}}
    ])

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Adapter Tuning for Large Language Models}\n"
            "\\begin{abstract}\nWe study efficient multilingual transfer for large language models.\n\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(disc, "_download_arxiv_source", _fake_download)

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["arxiv_id"] == "2401.00001"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
    assert entry["ingest_format"] == "directory"
    assert any("using fetched TeX source" in w for w in entry["warnings"])


def test_prepare_pdf_keeps_fetched_source_without_source_metadata(raw_root, monkeypatch):
    (raw_root / "papers" / "seed.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(
        disc,
        "_extract_pdf_text",
        lambda _path: ("Adapter Tuning\nAbstract\nBrief note.", []),
    )
    monkeypatch.setattr(disc, "s2_search", lambda *_args, **_kwargs: [
        {"title": "Adapter Tuning for Large Language Models", "externalIds": {"ArXiv": "2401.00006"}}
    ])

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text("\\section{Body}\nNo title metadata.\n", encoding="utf-8")
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(disc, "_download_arxiv_source", _fake_download)

    manifest = disc.prepare_inputs(raw_root)
    entry = next(item for item in manifest["entries"] if item["source_kind"] == "paper")

    assert entry["arxiv_id"] == "2401.00006"
    assert entry["title"] == "Adapter Tuning"
    assert entry["abstract_excerpt"] == "Brief note."
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
