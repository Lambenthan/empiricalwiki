# Changelog

All notable changes to OmegaWiki will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-04-09

### Added

- 20 Claude Code skills for full research lifecycle: `/init`, `/ingest`, `/ask`, `/edit`, `/check`, `/daily-arxiv`, `/ideate`, `/novelty`, `/review`, `/exp-design`, `/exp-run`, `/exp-status`, `/exp-eval`, `/refine`, `/survey`, `/paper-plan`, `/paper-draft`, `/paper-compile`, `/research`, `/rebuttal`
- Wiki knowledge engine (`tools/research_wiki.py`) with 20 CLI commands
- 8 entity types: papers, concepts, topics, people, ideas, experiments, claims, summaries
- Typed semantic relationship graph (`graph/edges.jsonl`) plus bibliographic citation layer (`graph/citations.jsonl`)
- Daily arXiv automation via GitHub Actions
- Cross-model review via any OpenAI-compatible API (DeepSeek, OpenAI, Qwen, OpenRouter, SiliconFlow, etc.)
- Multi-source data integration: arXiv RSS, Semantic Scholar, DeepXiv
- Remote GPU experiment support (`tools/remote.py`)
- Structural wiki linter with auto-fix (`tools/lint.py`)
- Bilingual support (English + Chinese) with `setup.sh --lang` switching
- One-click setup (`setup.sh`)
- Obsidian-compatible `[[wikilink]]` format throughout
- 2125 tests
