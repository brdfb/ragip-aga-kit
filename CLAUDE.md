# CLAUDE.md

Ragip Aga Kit — Claude Code agent sistemi. Turk KOBi nakit akisi yonetimi, vade pazarligi, sozlesme uyusmazlik danismanligi.

Hedef repoya `install.sh` ile kurulur. Tum kullanici icerigi **Turkce**.

## Ortam

- Python 3.12+, venv: `.venv/` — **`python3` kullan, `python` degil**
- Kullanici ortami: Parasut (ERP) + D365 Sales (CRM), birbirine entegre
- MCP server'lar kit disinda, ayri proje(ler)

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

## Tasarim Kararlari (ADR olmayan)

- FinansalHesap analiz metotlari: tarih-bagli metotlara `bugun` parametresi ekle (aging_raporu, dso, dpo). Test edilebilirlik icin zorunlu.
- Kit ust orchestrator'e ihtiyac duymaz — tek domain (KOBi finans). Ikinci domain agent dogdugunda degerlendir.
- Adaptor arayuzu gereksiz — ADR-0007 JSON semasi yeterli sozlesme. MCP tarafinda dto yazilir.
- Agent tool kisitlama: frontmatter'da `tools:` (allowlist) veya `disallowedTools:` (denylist). Simdilik prompt sertlestirme ile cozuldu, gerekirse yapisal kisitlamaya gecilir.
- MCP tool gorunurlugu: Agent, MCP tool gorunce system prompt talimatini atlayabiliyor — prosedurel skill'lerde `disable-model-invocation` ile korunuyor.

## Commit Kurali (ZORUNLU)

Kod veya prompt degisikligi yapan HER commit'te asagidaki kontrolleri yap:

1. VERSION bump gerekiyor mu? (fix/prompt → patch, feat → minor)
2. config/ragip_aga.yaml version eslesme
3. RAGIP_AGA_CHANGELOG.md yeni giris
4. README.md: test sayisi, tablo sayilari guncel mi
5. CLAUDE.md: test dosya listesi guncel mi
6. install.sh: agent/skill sayilari guncel mi
7. docs/FEATURE_IDEAS.md: eski sayilar var mi

Bu kontrolleri AYRI commit olarak DEGIL, ayni commit icinde yap.
Sadece docs-only degisikliklerde (ADR, FEATURE_IDEAS) versiyon bump gerekmez.

## Release Checklist

- Yukaridaki commit kontrolleri tamam mi
- Testleri calistir
- Tag olustur, push, `gh release create`

## Genel Kurallar

- Sayilari hardcode etme — source'tan oku (`cat VERSION`, `pytest tests/ -v`)
- Yeni mimari karar → ADR yaz (`docs/adr/`)
- Gelecek degerlendirme / YAGNI maddeleri → `docs/FEATURE_IDEAS.md`
