# CLAUDE.md

Ragip Aga Kit — Claude Code agent sistemi. Turk KOBi nakit akisi yonetimi, vade pazarligi, sozlesme uyusmazlik danismanligi.

Hedef repoya `install.sh` ile kurulur. Tum kullanici icerigi **Turkce**.

## Komutlar

```bash
# Test suite
python -m pytest tests/ -v

# Bireysel test dosyalari
python -m pytest tests/test_ragip_subagents.py -v   # Yapisal + bash block
python -m pytest tests/test_ragip_finansal.py -v     # FinansalHesap
python -m pytest tests/test_ragip_rates.py -v        # TCMB rate fetcher
python -m pytest tests/test_ragip_fatura_analiz.py -v # Fatura analiz motorlari
python -m pytest tests/test_ragip_crud.py -v         # CRUD helper
python -m pytest tests/test_ragip_install.py -v      # Install/update

# Tek test
python -m pytest tests/test_ragip_finansal.py::TestVadeFarki::test_basit_hesap -v

# TCMB oranlari
python3 scripts/ragip_rates.py              # JSON
python3 scripts/ragip_rates.py --pretty     # Tablo
python3 scripts/ragip_rates.py --refresh    # Cache yenile

# Kurulum / guncelleme
bash install.sh                             # Hedef repoya kur
bash update.sh [--dry-run|--force]          # Guncelle

# Bagimliliklar
pip install -r requirements.txt
```

## Kurallar

Detayli kurallar `.claude/rules/` altinda:
- `architecture.md` — Agent hiyerarsisi, model atamalari, skill dagitimi
- `portability.md` — Path cozumleme, standalone moduller
- `update-mechanism.md` — Manifest mantigi, uclu checksum, kullanici koruma
- `data-schema.md` — Firma tip alani, jsonl/json yapilari, ortam degiskenleri

## Mimari Kararlar

`docs/adr/` altinda tarihli karar kayitlari. Yeni bir mimari karar alindiginda ADR yaz.

## Python Scripts

- **`scripts/ragip_aga.py`**: CLI + `FinansalHesap` sinifi. `FALLBACK_RATES`'i ragip_rates.py'den import eder.
- **`scripts/ragip_rates.py`**: TCMB EVDS3 + CollectAPI. Standalone, stdlib only, 4 saat cache TTL.
- **`scripts/ragip_get_rates.sh`**: Skill'ler icin TCMB oran helper. Fallback: API -> cache -> FALLBACK_RATES.
- **`scripts/ragip_crud.py`**: CRUD skill'leri icin paylasimli helper (get_root, load/save, parse_kv, atomic_write).

## Test Yapisi

Testler kit kaynagi (`agents/`) veya kurulu repo (`.claude/agents/`) otomatik tespit eder. `test_ragip_subagents.py` tum agent mimarisini dogrular: frontmatter YAML, skill dagitimi, model atamalari, tasinabilirlik, cikti yonetimi. E2E fixtures: `tests/e2e_ragip_scenario/`.
