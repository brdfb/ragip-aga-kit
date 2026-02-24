# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ragip Aga Kit is a portable Claude Code agent system for Turkish SMB cash flow management, due date negotiation, and contract dispute advisory. It installs into any git repo via `install.sh`, copying agents, skills, scripts, and config into the target repo's `.claude/` directory structure.

All user-facing content (agent prompts, skill docs, CLI output) is in **Turkish**.

## Commands

### Tests
```bash
# Full test suite (169 tests)
python -m pytest tests/ -v

# Individual test files
python -m pytest tests/test_ragip_subagents.py -v   # Structural + bash block tests (60)
python -m pytest tests/test_ragip_finansal.py -v     # FinansalHesap unit tests (58)
python -m pytest tests/test_ragip_rates.py -v        # TCMB rate fetcher tests (19)
python -m pytest tests/test_ragip_crud.py -v         # CRUD helper tests (17)
python -m pytest tests/test_ragip_install.py -v      # Install/update tests (15)

# Single test
python -m pytest tests/test_ragip_finansal.py::TestVadeFarki::test_basit_hesap -v
```

### TCMB Rate Fetcher
```bash
python3 scripts/ragip_rates.py              # JSON output (for skills)
python3 scripts/ragip_rates.py --pretty     # Human-readable table
python3 scripts/ragip_rates.py --refresh    # Force cache refresh
```

### Installation (into a target repo)
```bash
cd /path/to/target-repo
bash /path/to/ragip-aga-kit/install.sh
```

### Update (existing installation)
```bash
cd /path/to/hedef-repo
bash /path/to/ragip-aga-kit/update.sh            # Normal update
bash /path/to/ragip-aga-kit/update.sh --dry-run   # Preview changes
bash /path/to/ragip-aga-kit/update.sh --force      # Force same-version update
```

### Dependencies
```bash
pip install -r requirements.txt   # litellm, pyyaml, pdfplumber, pandas, openpyxl
```

## Architecture

### Orchestrator + Sub-Agent Pattern

```
ragip-aga (orchestrator, sonnet, skills: none)
  |
  +-- ragip-hesap (haiku)     → ragip-vade-farki, ragip-arbitraj
  +-- ragip-arastirma (sonnet) → ragip-analiz, ragip-dis-veri, ragip-strateji, ragip-ihtar
  +-- ragip-veri (haiku)       → ragip-firma, ragip-gorev, ragip-import, ragip-ozet, ragip-profil
```

- **ragip-aga** (`agents/ragip-aga.md`): Orchestrator only — dispatches to sub-agents via Task tool, never computes directly. Reads user's firm profile from `data/RAGIP_AGA/profil.json` for context-aware routing.
- **ragip-hesap**: Deterministic financial calculations (interest, TVM, arbitrage). Uses haiku for cost efficiency.
- **ragip-arastirma**: Deep analysis requiring reasoning (contract analysis, strategy, legal drafts). Uses sonnet.
- **ragip-veri**: CRUD operations (firm cards, tasks, CSV import, daily briefing). Uses haiku.

Sub-agents save outputs to `data/RAGIP_AGA/ciktilar/` with format `YYYYMMDD_HHMMSS-{agent}-{skill}-{topic}.md`. Later steps reference prior outputs via file paths.

### Key Design Rules

- All 11 skills must be distributed across the 3 sub-agents with no overlaps (tested by `test_ragip_subagents.py`)
- Prosedural/CRUD skills use `disable-model-invocation: true`; LLM-requiring skills (analiz, dis-veri, strateji, vade-farki, arbitraj) do not
- All file paths in agents/skills use `git rev-parse --show-toplevel` — no hardcoded paths (tested by `TestPortability`)
- `ragip_rates.py` is a standalone zero-dependency module (stdlib only) that can be copied to any repo independently

### Python Scripts

- **`scripts/ragip_aga.py`**: CLI entry point with `FinansalHesap` class (vade farki, TVM, iskonto, forward FX, arbitrage calculations). Imports `FALLBACK_RATES` from `ragip_rates.py` as single source of truth.
- **`scripts/ragip_rates.py`**: Fetches live rates from TCMB EVDS3 API and CollectAPI. Standalone module with 4-hour cache TTL. Exports `FALLBACK_RATES`, `get_rates()`, `get_mevduat()`, `get_kredi()`.
- **`scripts/ragip_get_rates.sh`**: Single-source TCMB rate helper for skills. Fallback chain: live API → cache → FALLBACK_RATES.
- **`scripts/ragip_crud.py`**: Shared CRUD helper module for firma/gorev/profil skills (get_root, load/save jsonl/json, parse_kv, atomic_write).

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `TCMB_API_KEY` | EVDS3 API key for live TCMB rates (fallback values used if missing) |
| `RAGIP_CACHE_DIR` | Override cache directory (default: `scripts/.ragip_cache/`) |
| `COLLECTAPI_KEY` | CollectAPI key for bank deposit/credit rates |

### Runtime Data (gitignored)

- `data/RAGIP_AGA/` — firm cards, tasks, output files, history
- `scripts/.ragip_cache/` — TCMB/CollectAPI rate cache files

## Test Structure

Tests auto-detect whether running from the kit source (`agents/`) or an installed repo (`.claude/agents/`). The structural tests in `test_ragip_subagents.py` validate the entire agent architecture: frontmatter YAML, skill distribution, model assignments, portability, and output management conventions. E2E scenario fixtures are in `tests/e2e_ragip_scenario/` (contract, invoices, CSV for a Microsoft NCE license dispute scenario).
