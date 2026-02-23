# Ragip Aga Kit

Claude Code icin nakit akisi yonetimi, vade muzakeresi ve sozlesme uyusmazliklari danismanligi sistemi.

40 yillik piyasa tecrubesiyle: vade farki hesaplama, TCMB canli oranlar, sozlesme analizi, 3 senaryolu strateji, ihtar taslagi, firma/gorev takibi.

## Hizli Kurulum

```bash
# 1. Clone et
git clone https://github.com/brdfb/ragip-aga-kit.git /tmp/ragip-aga-kit

# 2. Hedef repoya git
cd /path/to/senin-repo

# 3. Kur
bash /tmp/ragip-aga-kit/install.sh

# 4. Dogrula
python -m pytest tests/test_ragip_subagents.py -v
```

## Guncelleme

Mevcut kurulumu guncellemek icin:

```bash
cd /path/to/senin-repo
bash /path/to/ragip-aga-kit/update.sh
```

- Sizin degisiklikleriniz otomatik korunur
- Cakisma varsa `.kullanici-yedek-YYYYMMDD` yedeginiz olusur
- Onizleme icin: `bash update.sh --dry-run`
- Ayni surumde zorla: `bash update.sh --force`

Her kurulumda `config/.ragip_manifest.json` dosyasina 20 core dosyanin SHA-256 checksum'i kaydedilir. Guncelleme sirasinda uclu karsilastirma yapilir: manifest (kurulum anindaki hash) vs mevcut dosya vs yeni kit. Kullanici degisikligi tespit edilirse dosyaya dokunulmaz.

## Ne Kuruluyor

| Tip | Sayi | Konum |
|-----|------|-------|
| Agent | 4 | `.claude/agents/ragip-*.md` |
| Skill | 11 | `.claude/skills/ragip-*/SKILL.md` |
| Script | 4 | `scripts/ragip_*.py` + `ragip_get_rates.sh` |
| Config | 1 | `config/ragip_aga.yaml` |
| Manifest | 1 | `config/.ragip_manifest.json` |
| Test | 4+5 | `tests/` |

## Kullanim

### Slash Komutlari (Skill)

```
/ragip-firma listele                    — Tum firma kartlari
/ragip-firma ekle ABC Dagitim vade=60   — Yeni firma ekle
/ragip-gorev ekle Avukata gonder        — Gorev ekle
/ragip-gorev listele                    — Aktif gorevler
/ragip-vade-farki 250000 3 45           — Vade farki hesapla
/ragip-arbitraj                         — Arbitraj firsatlari (CIP, ucgen kur, carry trade)
/ragip-profil ABC Dagitim               — Sektor-aware firma profili
/ragip-ozet                             — Gunluk brifing
/ragip-import dosya.csv                 — CSV/Excel import
```

### Dogal Dil (Agent)

```
"Ragip Aga, bu sozlesmeyi analiz et"
"vade farki hesapla 100K %3 45 gun"
"ABC Dagitim hakkinda bilgi topla"
"3 senaryo strateji olustur"
"ihtar taslagi hazirla - vade farki"
```

## Mimari

```
ragip-aga (orchestrator, sonnet)
  |
  +-- ragip-hesap (haiku) -------- ragip-vade-farki
  |                                ragip-arbitraj
  |
  +-- ragip-arastirma (sonnet) --- ragip-analiz
  |                                ragip-dis-veri
  |                                ragip-strateji
  |                                ragip-ihtar
  |
  +-- ragip-veri (haiku) --------- ragip-firma
                                   ragip-gorev
                                   ragip-import
                                   ragip-ozet
                                   ragip-profil
```

**Orchestrator** (ragip-aga) kullanicinin istegini anlar ve uygun sub-agent'a yonlendirir. Kendisi hesaplama/analiz yapmaz.

**Sub-agent'lar** model maliyetine gore optimize edilmistir:
- **haiku**: Deterministik islemler (CRUD, hesaplama) — ucuz ve hizli
- **sonnet**: Derin dusunme gerektiren islemler (analiz, strateji) — kaliteli

### Paylasimli Yardimci Moduller (v2.5.0)

- **`scripts/ragip_get_rates.sh`** — TCMB oranlarini cekmek icin tek kaynak. Fallback zinciri: canli API → cache → FALLBACK_RATES. Tum oran kullanan skill'ler (vade-farki, arbitraj, strateji) bu helper'i cagirir.
- **`scripts/ragip_crud.py`** — CRUD skill'leri (firma, gorev, profil) icin paylasimli yardimci modul. `load/save_jsonl`, `load/save_json`, `parse_kv`, `atomic_write`, `next_id` fonksiyonlari.

## Test

```bash
# Tam suite (164 test)
python -m pytest tests/ -v

# Dosya bazli
python -m pytest tests/test_ragip_subagents.py -v   # Yapisal + bash block (58 test)
python -m pytest tests/test_ragip_finansal.py -v     # FinansalHesap (58 test)
python -m pytest tests/test_ragip_rates.py -v        # TCMB rate fetcher (19 test)
python -m pytest tests/test_ragip_crud.py -v         # CRUD helper (17 test)
python -m pytest tests/test_ragip_install.py -v      # Install/update (12 test)
```

Testler 5 katmani kapsar:
1. **Yapisal** — Agent frontmatter, skill dagilimi, model atamalari, portability
2. **Bash block** — Python sozdizimi, bare placeholder, env var eslestirme, helper kullanimi
3. **Finansal** — Vade farki, TVM, arbitraj, carry trade hesaplamalari
4. **TCMB** — Oran cekme, cache, fallback, format
5. **Install/Update** — Fresh install, manifest, checksum, update senaryolari (kullanici degisikligi koruma, conflict backup, dry-run)

## Bagimlilklar

```
pdfplumber>=0.10.0   # Fatura/sozlesme PDF analizi
pandas>=2.0.0        # CSV/Excel import
openpyxl>=3.1.0      # Excel dosya destegi
pyyaml>=6.0          # Konfigurasyon
```

## Portability

Tum path'ler `git rev-parse --show-toplevel` ile cozumlenir. Herhangi bir git reposuna kurulabilir, hardcoded path yoktur.

`ragip_rates.py` standalone calisabilir — sifir bagimlilik, tek dosya:
```bash
# Sadece TCMB oranlarini kullanmak icin:
cp scripts/ragip_rates.py /yeni-repo/scripts/
export TCMB_API_KEY=xxx                    # EVDS API anahtari
export RAGIP_CACHE_DIR=/yeni-repo/.cache   # Opsiyonel, varsayilan: scripts/.ragip_cache/
python3 scripts/ragip_rates.py --pretty
```

Runtime veri (`data/RAGIP_AGA/`, `scripts/.ragip_cache/`) otomatik olusturulur ve `.gitignore`'a eklenir.

## Lisans

MIT
