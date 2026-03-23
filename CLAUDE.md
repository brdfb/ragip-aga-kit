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
python -m pytest tests/test_ragip_temizle.py -v      # ragip_temizle.sh
python -m pytest tests/test_ragip_integration.py -v  # Katman 3 integration (D365 veri yapisi)
python -m pytest tests/test_ragip_output.py -v       # Cikti yonetimi (firma klasor, manifest, dedup)
python -m pytest tests/test_ragip_errors.py -v      # Hata siniflandirmasi (GECICI/KALICI/POLITIKA)
python -m pytest tests/test_ragip_pii.py -v         # PII temizleyici (maskeleme + hash)

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
- `commit-checklist.md` — Commit ve release kontrol listesi
- `conventions.md` — Genel konvansiyonlar, hardcode yasagi, ADR/FEATURE_IDEAS politikasi

## Mimari Kararlar

`docs/adr/` altinda tarihli karar kayitlari. Yeni bir mimari karar alindiginda ADR yaz.

## Python Scripts

- **`scripts/ragip_aga.py`**: CLI + `FinansalHesap` sinifi. `FALLBACK_RATES`'i ragip_rates.py'den import eder.
- **`scripts/ragip_rates.py`**: TCMB EVDS3 + CollectAPI. Standalone, stdlib only, 4 saat cache TTL.
- **`scripts/ragip_get_rates.sh`**: Skill'ler icin TCMB oran helper. Fallback: API -> cache -> FALLBACK_RATES.
- **`scripts/ragip_crud.py`**: CRUD skill'leri icin paylasimli helper (get_root, load/save, parse_kv, atomic_write) + ADR-0007 sema dogrulamasi (validate_fatura, validate_faturalar).

## Test Yapisi

Testler kit kaynagi (`agents/`) veya kurulu repo (`.claude/agents/`) otomatik tespit eder. `test_ragip_subagents.py` tum agent mimarisini dogrular: frontmatter YAML, skill dagitimi, model atamalari, tasinabilirlik, cikti yonetimi. E2E fixtures: `tests/e2e_ragip_scenario/`.

## Tasarim Kararlari (ADR olmayan)

- FinansalHesap analiz metotlari: tarih-bagli metotlara `bugun` parametresi ekle (aging_raporu, dso, dpo). Test edilebilirlik icin zorunlu.
- Kit ust orchestrator'e ihtiyac duymaz — tek domain (KOBi finans). Ikinci domain agent dogdugunda degerlendir.
- Adaptor arayuzu gereksiz — ADR-0007 JSON semasi yeterli sozlesme. MCP tarafinda dto yazilir.
- Agent tool kisitlama: ragip-aga, ragip-hesap, ragip-veri'de `disallowedTools: [WebSearch, WebFetch]` frontmatter ile mimari seviyede uygulandı. ragip-arastirma ve ragip-hukuk'ta bazi skill'ler WebSearch gerektirdiginden prompt kisitlamasi devam eder.
- MCP tool gorunurlugu: Agent, MCP tool gorunce system prompt talimatini atlayabiliyor — prosedurel skill'lerde `disable-model-invocation` ile korunuyor. Hedef repoda ham MCP tool'lari TUM agent'larda `disallowedTools` ile bloke edilmeli, yalnizca semantic tool (firma_raporu vb.) acik kalmali (ADR-0004, MCP rehberi).
- Persona ve domain knowledge: Ragip Aga system prompt ile tanimlanan bir persona. Model bilgisinin otesinde ozel domain knowledge saglamiyor. Kit'in gercek degeri: dogru yonlendirme + FinansalHesap hesaplama motoru + ERP-agnostik veri duzeni (ADR-0007).

## Commit & Release Kurallari

Detaylar `.claude/rules/commit-checklist.md` altinda.

## Genel Kurallar

Detaylar `.claude/rules/conventions.md` altinda.
