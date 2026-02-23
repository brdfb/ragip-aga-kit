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

## Ne Kuruluyor

| Tip | Sayi | Konum |
|-----|------|-------|
| Agent | 4 | `.claude/agents/ragip-*.md` |
| Skill | 11 | `.claude/skills/ragip-*/SKILL.md` |
| Script | 2 | `scripts/ragip_*.py` |
| Config | 1 | `config/ragip_aga.yaml` |
| Test | 3+5 | `tests/` |

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
