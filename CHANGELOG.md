# Changelog

All notable changes to EmpiricalWiki will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.3.0] - 2026-06-12

### Added

- 14 preset schema cards ship with the repo: 9 `datasets/` cards (CSMAR, Wind, CNRDS, 华证 ESG, DIB, iFinD, WinGo, CCER, patent sources) and 5 `identification/` strategy cards (staggered DID, PSM, IV, RDD, TWFE) — every institutional fact web-verified with sources
- Stata template library (`tools/stata-templates/`): five `.do` skeletons with built-in review checkpoints, wired into `/stata-plan --write-do`
- `demo` branch: a complete worked example (23 patient-capital papers, full cross-linked graph) browsable on GitHub
- Agent-native onboarding: Quick Start opens with a copy-paste block for Claude Code / Codex / Cursor; new `AGENTS.md` entry point for any coding agent
- Golden-standard test set (`tests/golden/` + `tools/golden_check.py`) guarding ingest quality across skill changes
- `tools/update_demo.sh`: refresh the demo branch via plumbing, without ever switching branches

### Changed

- `tables` and seven generic entity types documented as on-demand (empty directories are the normal state)
- Derived graph files (`wiki/graph/*.jsonl`, brief, open questions) untracked on main — branch operations can no longer clobber working-tree state

## [0.2.0] - 2026-05

### Added

- Theory-modeling layer: `assumptions` + `propositions` page types and `/theory-ingest`, bridged to the empirical layer through `mechanisms` / `hypotheses` on one shared graph
- Local website view (`tools/view.sh`) via Quartz: interactive graph, full-text search, backlinks
- Empirical specialization: 10 empirical entity types and 5 specialized skills (`/empirical-ingest`, `/theory-ingest`, `/variable-map`, `/empirical-design`, `/stata-plan`)

## [0.1.0] - 2026-04-09

Initial release, downstream of the upstream ΩmegaWiki framework:

- 24 inherited research-lifecycle skills (`/init`, `/ingest`, `/ask`, `/check`, `/ideate`, `/paper-draft`, …)
- Wiki knowledge engine (`tools/research_wiki.py`), typed semantic graph, citation layer
- Multi-source discovery (arXiv RSS, Semantic Scholar, DeepXiv), cross-model review, remote GPU support
- Structural linter with auto-fix, bilingual i18n, one-click setup
