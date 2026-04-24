"""Tests for tools/prepare_paper_source.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, "tools")
import prepare_paper_source as prep  # noqa: E402


@pytest.fixture
def raw_root(tmp_path):
    raw = tmp_path / "raw"
    for sub in ("papers", "notes", "web", "discovered", "tmp"):
        (raw / sub).mkdir(parents=True)
        (raw / sub / ".gitkeep").touch()
    return raw


def test_prepare_pdf_with_filename_arxiv_prefers_source_fetch(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "2401.00007-seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )

    calls = []

    def _spy_s2_search(query, limit=5):
        calls.append(query)
        return []

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Source Truth Title}\n\\begin{abstract}\nSome content.\n\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(prep, "s2_search", _spy_s2_search)
    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)

    entry = prep.prepare_paper_source(pdf_path, raw_root)

    assert not calls
    assert entry["arxiv_id"] == "2401.00007"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
    assert entry["ingest_format"] == "directory"
    assert entry["title"] == "Source Truth Title"
    assert entry["candidate_id"] == "local:papers-2401-00007-seed-pdf"
    assert "title_source" not in entry


def test_prepare_pdf_with_embedded_filename_arxiv_prefers_source_fetch(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "YOLO1506.02640v5.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("You Only Look Once\nAbstract\nSome content.", []),
    )

    calls = []

    def _spy_s2_search(query, limit=5):
        calls.append(query)
        return []

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{You Only Look Once}\n\\begin{abstract}\nSome content.\n\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(prep, "s2_search", _spy_s2_search)
    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)

    entry = prep.prepare_paper_source(pdf_path, raw_root)

    assert not calls
    assert entry["arxiv_id"] == "1506.02640"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
    assert entry["ingest_format"] == "directory"
    assert entry["title"] == "You Only Look Once"


def test_prepare_pdf_with_supplied_title_uses_title_search(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )

    queries = []

    def _fake_s2_search(query, limit=5):
        queries.append(query)
        return [{"title": "Recovered Title", "externalIds": {"ArXiv": "2401.00001"}}]

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Source Truth Title}\n\\begin{abstract}\nSome content.\n\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(prep, "s2_search", _fake_s2_search)
    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)

    entry = prep.prepare_paper_source(pdf_path, raw_root, title="Recovered Title")

    assert queries == ["Recovered Title"]
    assert entry["arxiv_id"] == "2401.00001"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
    assert entry["ingest_format"] == "directory"
    assert entry["title"] == "Recovered Title"
    assert entry["candidate_id"] == "local:papers-seed-pdf"
    assert "title_source" not in entry


def test_prepare_pdf_with_supplied_arxiv_id_bypasses_title_search(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )

    calls = []

    def _spy_s2_search(query, limit=5):
        calls.append(query)
        return []

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Source Truth Title}\n\\begin{abstract}\nSome content.\n\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(prep, "s2_search", _spy_s2_search)
    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)

    entry = prep.prepare_paper_source(pdf_path, raw_root, title="Recovered Title", arxiv_id="2401.00009v2")

    assert not calls
    assert entry["arxiv_id"] == "2401.00009"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")
    assert entry["title"] == "Recovered Title"


def test_prepare_pdf_without_supplied_title_skips_title_search_and_falls_back_to_synthetic(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )
    monkeypatch.setattr(prep, "_extract_pdf_metadata_title", lambda _path: "")

    calls = []

    def _spy_s2_search(query, limit=5):
        calls.append(query)
        return []

    monkeypatch.setattr(prep, "s2_search", _spy_s2_search)

    entry = prep.prepare_paper_source(pdf_path, raw_root)

    assert not calls
    assert entry["arxiv_id"] == ""
    assert entry["canonical_ingest_path"].endswith(".tex")
    assert entry["title"] == "seed"
    assert entry["candidate_id"] == "local:papers-seed-pdf"
    assert "title_source" not in entry


def test_prepare_pdf_fetched_source_title_is_sanitized_when_no_agent_title(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "YOLO1506.02640v5.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("You Only Look Once\nAbstract\nSome content.", []),
    )

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{\\vspace{-1cm}You Only Look Once: \\\\ Unified, Real-Time Object Detection\\vspace{-.25cm}}\n"
            "\\begin{abstract}\\vspace{-.25cm} Some content.\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)
    monkeypatch.setattr(prep, "s2_search", lambda *_args, **_kwargs: [])

    entry = prep.prepare_paper_source(pdf_path, raw_root)

    assert entry["arxiv_id"] == "1506.02640"
    assert entry["title"] == "You Only Look Once: Unified, Real-Time Object Detection"
    assert entry["abstract_excerpt"] == "Some content."


def test_prepare_pdf_fetched_source_title_does_not_override_agent_title(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )

    def _fake_s2_search(query, limit=5):
        return [{"title": "Recovered Title", "externalIds": {"ArXiv": "2401.00001"}}]

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Hybrid Layout Control for Diffusion Transformer:}\n"
            "\\begin{abstract}Some content.\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(prep, "s2_search", _fake_s2_search)
    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)

    entry = prep.prepare_paper_source(pdf_path, raw_root, title="Recovered Title")

    assert entry["title"] == "Recovered Title"
    assert entry["canonical_ingest_path"].endswith("-arxiv-src")


def test_prepare_pdf_rewrites_fetched_source_title_when_agent_title_supplied(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "YOLO1506.02640v5.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("You Only Look Once\nAbstract\nSome content.", []),
    )

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{\\vspace{-1cm}You Only Look Once: \\\\ Unified, Real-Time Object Detection\\vspace{-.25cm}}\n"
            "\\begin{abstract}\\vspace{-.25cm} Some content.\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)
    monkeypatch.setattr(prep, "s2_search", lambda *_args, **_kwargs: [])

    entry = prep.prepare_paper_source(
        pdf_path,
        raw_root,
        title="You Only Look Once: Unified, Real-Time Object Detection",
        arxiv_id="1506.02640",
    )

    rewritten_tex = raw_root / "tmp" / "papers" / "papers-yolo1506-02640v5-pdf-arxiv-src" / "main.tex"
    assert entry["title"] == "You Only Look Once: Unified, Real-Time Object Detection"
    assert rewritten_tex.exists()
    assert "\\title{You Only Look Once: Unified, Real-Time Object Detection}" in rewritten_tex.read_text(
        encoding="utf-8"
    )


def test_prepare_pdf_uses_metadata_title_only_as_provisional_display(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(prep, "_extract_pdf_text", lambda _path: ("Abstract\nSome content.", []))
    monkeypatch.setattr(prep, "_extract_pdf_metadata_title", lambda _path: "Metadata Title")
    monkeypatch.setattr(prep, "s2_search", lambda *_args, **_kwargs: [])

    entry = prep.prepare_paper_source(pdf_path, raw_root)

    assert entry["title"] == "Metadata Title"
    assert entry["candidate_id"] == "local:papers-seed-pdf"
    assert entry["canonical_ingest_path"].endswith(".tex")
    assert "title_source" not in entry


def test_prepare_pdf_with_supplied_title_falls_back_to_synthetic(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )
    monkeypatch.setattr(
        prep,
        "s2_search",
        lambda query, limit=5: [{"title": "Recovered Title", "externalIds": {"ArXiv": "2401.00002"}}],
    )
    monkeypatch.setattr(
        prep,
        "_download_arxiv_source",
        lambda _arxiv_id, _dest: {"success": False, "format": "", "error": "no source tarball"},
    )

    entry = prep.prepare_paper_source(pdf_path, raw_root, title="Recovered Title")

    assert entry["arxiv_id"] == "2401.00002"
    assert entry["canonical_ingest_path"].endswith(".tex")
    assert entry["ingest_format"] == "tex"
    assert entry["title"] == "Recovered Title"
    assert entry["candidate_id"] == "local:papers-seed-pdf"
    assert any("TeX source download failed" in warning for warning in entry["warnings"])
    assert "title_source" not in entry


def test_prepare_pdf_refreshes_existing_synthetic_title(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )
    monkeypatch.setattr(prep, "_extract_pdf_metadata_title", lambda _path: "")
    monkeypatch.setattr(prep, "s2_search", lambda *_args, **_kwargs: [])

    first = prep.prepare_paper_source(pdf_path, raw_root)
    second = prep.prepare_paper_source(pdf_path, raw_root, title="Recovered Title")

    synthetic_path = raw_root.parent / second["canonical_ingest_path"]
    assert first["title"] == "seed"
    assert second["title"] == "Recovered Title"
    assert "\\title{Recovered Title}" in synthetic_path.read_text(encoding="utf-8")


def test_prepare_pdf_existing_synthetic_tex_does_not_overwrite_agent_title(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(prep, "_extract_pdf_text", lambda _path: ("Recovered body text.", []))
    monkeypatch.setattr(prep, "_extract_pdf_metadata_title", lambda _path: "")
    monkeypatch.setattr(prep, "s2_search", lambda *_args, **_kwargs: [])

    out_path = raw_root / "tmp" / "papers" / "papers-seed-pdf.tex"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\\title{LOSS LANDSCAPES ARE ALL YOU NEED: NEURAL}\n\\begin{abstract}Some content.\\end{abstract}\n",
        encoding="utf-8",
    )

    entry = prep.prepare_paper_source(pdf_path, raw_root, title="Loss Landscapes Are All You Need")

    assert entry["title"] == "Loss Landscapes Are All You Need"
    assert "\\title{Loss Landscapes Are All You Need}" in out_path.read_text(encoding="utf-8")


def test_prepare_pdf_existing_fetched_source_dir_is_rewritten_from_stored_authoritative_title(raw_root, monkeypatch):
    pdf_path = raw_root / "papers" / "seed.pdf"
    pdf_path.write_bytes(b"%PDF")
    monkeypatch.setattr(
        prep,
        "_extract_pdf_text",
        lambda _path: ("Recovered Title\nAbstract\nSome content.", []),
    )

    def _fake_download(arxiv_id, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "main.tex").write_text(
            "\\title{Recovered Title}\n\\begin{abstract}Some content.\\end{abstract}\n",
            encoding="utf-8",
        )
        return {"success": True, "format": "directory", "error": None}

    monkeypatch.setattr(
        prep,
        "s2_search",
        lambda query, limit=5: [{"title": "Recovered Title", "externalIds": {"ArXiv": "2401.00004"}}],
    )
    monkeypatch.setattr(prep, "_download_arxiv_source", _fake_download)

    first = prep.prepare_paper_source(pdf_path, raw_root, title="Recovered Title")
    staged_dir = raw_root.parent / first["canonical_ingest_path"]
    staged_tex = staged_dir / "main.tex"
    staged_tex.write_text(
        "\\title{\\vspace{-1cm}Recovered Title\\\\Extra Formatting\\vspace{-.25cm}}\n"
        "\\begin{abstract}\\vspace{-.25cm} Some content.\\end{abstract}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(prep, "s2_search", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected search")))

    second = prep.prepare_paper_source(pdf_path, raw_root)

    assert second["title"] == "Recovered Title"
    assert "\\title{Recovered Title}" in staged_tex.read_text(encoding="utf-8")


def test_prepare_tex_passthrough(raw_root):
    tex_path = raw_root / "papers" / "seed.tex"
    tex_path.write_text(
        "\\title{Recovered Title}\n\\begin{abstract}Some content.\\end{abstract}\n",
        encoding="utf-8",
    )

    entry = prep.prepare_paper_source(tex_path, raw_root)

    assert entry["canonical_ingest_path"] == "raw/papers/seed.tex"
    assert entry["prepared_path"] is None
    assert entry["title"] == "Recovered Title"
    assert entry["candidate_id"] == "local:papers-seed-tex"
    assert "title_source" not in entry


def test_prepare_source_dir_passthrough(raw_root):
    source_dir = raw_root / "papers" / "seed-dir"
    source_dir.mkdir()
    (source_dir / "main.tex").write_text(
        "\\title{Recovered Title}\n\\begin{abstract}Some content.\\end{abstract}\n",
        encoding="utf-8",
    )

    entry = prep.prepare_paper_source(source_dir, raw_root)

    assert entry["canonical_ingest_path"] == "raw/papers/seed-dir/main.tex"
    assert entry["prepared_path"] is None
    assert entry["title"] == "Recovered Title"
    assert entry["candidate_id"] == "local:papers-seed-dir"
    assert "title_source" not in entry


def test_extract_arxiv_source_metadata_reads_title_and_abstract(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "main.tex").write_text(
        "\\title{Recovered Title}\n\\begin{abstract}\nSome content.\n\\end{abstract}\n",
        encoding="utf-8",
    )

    result = prep._extract_arxiv_source_metadata(source_dir)

    assert result["source_title"] == "Recovered Title"
    assert result["source_abstract"] == "Some content."


def test_prepare_paper_source_cli_outputs_json(raw_root):
    tex_path = raw_root / "papers" / "seed.tex"
    tex_path.write_text("\\title{Recovered Title}\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "tools" / "prepare_paper_source.py"),
            "--raw-root",
            str(raw_root),
            "--source",
            str(tex_path),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    assert payload["title"] == "Recovered Title"
    assert payload["canonical_ingest_path"] == "raw/papers/seed.tex"
    assert "title_source" not in payload
