# ADR-0020: LLM-Judge — Spirit (Anlamsal) Olcumu

**Tarih:** 2026-05-20
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici
**Iliski:** ADR-0016 (Tier 3), ADR-0018 (Tier 4), ADR-0019 (Tier 5 deterministic enforcement)

## Baglam

v2.19.1 ile **5 katmanli savunma** tamamlandi:
- Tier 1-2: Barnum + madde dogrulama (citation halusinasyon)
- Tier 3: 3-satir zenginlestirilmis blok (Lead With Insight, Quantify, Action 5-bilesen, etiket)
- Tier 4: Tutarlilik denetimi notu (cross-document)
- Tier 5: `ragip_format_dogrula.py` deterministik regex post-write check

16 Mayis 2026 5. davranissal kosumu sonrasi yapisal eslesme **TEMIZ — Exit 0** (TESPIT:4, Etki:4, POZISYON 5-bilesen:4, Anapara etiket:3, Tutarlilik denetimi:1). Disiplinin **HARFI** gecmis.

### Acik kalan sorun: "Ruh" vs "Harf" asimetrisi

Format_dogrula.py **yapisal** kontrol yapar — regex pattern eslesirse PASS. Ama:

- `TESPIT: Anapara 142K USD` — yapisal pass, ama "insight" mi yoksa sadece sayi tekrari mi?
- `Etki: 78K USD (%55) ↑ 30gun` — yapisal pass, ama tutar/yuzde/yon/horizon **mantikli** mi?
- `POZISYON: ... · Sahip: Birisi · Zaman: yakinda · Beklenen: olur` — yapisal pass (5 alan dolu), ama spesifik mi vague mi?
- `GEREKCE: yasal sebepler` — yapisal pass, ama gercek mevzuat referansi yok
- `anapara (kalan) 142K` aynanda baska yerde `borc 142K` — etiket celiskisi (regex yakalamiyor)
- `Tutarlilik denetimi: temiz.` — gercek kontrol mu yoksa rubber-stamp mi?

**Format_dogrula.py bunlari yakalamaz.** LLM "harf"i atlatarak yapisal check'i gecip "ruh"u atlayabilir.

## Karar

**Tier 6 — LLM-judge:** Ikinci bir LLM (Sonnet 4.5) ciktiyi **anlamsal** olarak degerlendirir. 6 dimension rubric, structured JSON output. Yapisal grep'in yakalayamadigi kalite boyutlarini olcer.

### Felsefe

- Tier 5 (deterministik) = HARF (regex pattern)
- Tier 6 (LLM-judge) = RUH (anlamsal kalite)
- **Komplemen, redundant degil.** Ikisi paralel calisir.

### Rubric (6 dimension, Boolean + reasoning)

| Dim | Soru | Yapisal yakalar mi |
|-----|------|--------------------|
| T3-1 TESPIT_quality | Cumle gercek insight mi yoksa sayi tekrari mi? | Hayir |
| T3-2 ETKI_quality | Tutar/yuzde/yon/horizon mantikli mi? | Hayir |
| T3-3 POZISYON_quality | Aksiyon spesifik, sahip net mi? | Hayir |
| T3-4 GEREKCE_quality | Mevzuat referansi gercek mi, generic degil mi? | Hayir |
| T3-5 ETIKET_consistency | Anapara etiketleri cikti icinde celiskisiz mi? | Kismi (regex anapara etiketi var mi yakalar; celiski yakalamaz) |
| T4 TUTARLILIK_genuine | Denetim notu gercek mi, rubber-stamp mi? | Hayir |

JSON output: per-dim Boolean + reasoning, overall (pass/fail/partial), spirit_score (0-6), notes.

### Mimari kararlar

**Judge model: Sonnet 4.5 (`anthropic/claude-sonnet-4-5-20250929`)**

| Alternatif | Red nedeni |
|---|---|
| Haiku 4.5 (ucuz) | Self-enhancement bias (judge != generator zorunlu). Kit sub-agent'lari Haiku kullaniyor — Haiku Haiku'yu yargilarsa onyargili olur. |
| Sonnet 4.6 (yeni) | Kit `call_llm()` Sonnet 4.5 kullaniyor (config tutarlilik). Sonnet 4.6'ya gecerken hem judge hem generator paralel update gerekir. |
| Opus 4.7 | Pahali ($15/$75 1M tok) — judge sadece 6-dim Boolean, overkill. Spirit olcumu icin Sonnet yeterli. |

**Sonnet 4.5 secimi:** Kit ile uyumlu, cross-model judge (judge Sonnet, generator sub-agent Haiku/Sonnet karisik), Anthropic 2026 eval guidance ile uyumlu.

**Schema dogrulamasi: Minimal dict + manual check**

| Alternatif | Red nedeni |
|---|---|
| Pydantic ekle | Kit `requirements.txt` minimal (5 paket). Yeni bagimlilik fayda/maliyet zayif (~6 dimension Boolean+string check yeterli). |
| Sadece JSON parse | Type-check yetersiz (`pass` field bool olmali, string degil). |
| `dataclasses` | Python stdlib ama ekstra boilerplate. Manual check daha sade. |

**Cost guard: Pre-check + Post-check (cumulative state)**

| Yaklasim | Davranis |
|---|---|
| Pre-check: tahmini token x fiyat (input + output) | Tek-cagri limitini (default $0.50) asarsa abort |
| Post-check: gercek usage'dan hesapla + cumulative state'e ekle | Haftalik limit (default $5) tracking, `data/.judge_usage.json` gitignored |
| `--skip-cost-guard` flag | Test/debug icin (TEHLIKELI) |

Sonnet 4.5 fiyat (16 May 2026):
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens
- Cache hit: $0.30 / 1M tokens (Anthropic prompt caching, %90 indirim)

Tipik judge cagrisi (~3K input + ~500 output): **~$0.016**. Cache hit ile: **~$0.011** (%30 tasarruf). Haftalik $5 limit ~300 cagri kapasitesi.

### Cadence

- **Manuel haftalik** (~10 cikti, ~$0.16/hafta gercek, $5 limit cok bol)
- CI auto degil — pytest mock'lu, gercek API cagrisi yapmaz
- Integration test ayri script (ANTHROPIC_API_KEY varsa kosulur)

## Konsekvanslar

### Pozitif

- **Spirit + Letter ikili olcum** — Tier 5 yakalayamayan kalite boyutlari yakalanir
- **Cross-model judge** — generator-judge ayrimi (self-enhancement bias minimum)
- **Cost guard kit-friendly** — yanlislikla $$$ harcanma riski yok
- **Mock-only pytest** — gercek API gerek yok, hizli + ucretsiz + deterministic
- **Manuel haftalik cadence** — kullanim senaryosu netleseyledikce surdurulebilir

### Negatif

- **Judge prompt sensitivity** (JudgeSense arxiv 2604.23478) — paraphrase-pair test gelecek calisma
- **Cost guard tahmini token** (1 token ~= 4 char) — kaba, ama pre-check icin yeterli
- **State file** `data/.judge_usage.json` — workspace ve kit ayri (her birinin kendi state'i)
- **Manuel cadence** — otomatik tetikleme yok (CI ile entegre gelecek)

### Sinirlamalar

- Judge model **Tier 5'i denetlemez** — kendi degerlendirme tutarliligi olculur, yapisal HARFI yine `format_dogrula.py` koruyor
- Judge model **mutlak gercek degildir** — Anthropic 2026 eval guidance: "LLM-as-judge biased, paraphrase-pair test gerekli"
- **Manuel rubric** (6 fixed dimension) — yeni Tier eklendiginde elle update gerek (Tier 6 = bu ADR, sonraki Tier 7 gelecekte)

### Gelecek calisma

- **Paraphrase-pair stability test** — ayni cikti iki farkli prompt-paraphrase ile judge edilince spirit_score eslemeli (JudgeSense)
- **Manuel weekly cron** — `bash scripts/ragip_cron.sh judge` (haftalik tum ciktilar uzerinde judge kosumu)
- **CI integration** (opsiyonel) — pre-commit hook'a judge eklenebilir ama maliyet $-$$/commit
- **Tier 7?** — Multi-model ensemble judge (Sonnet + Haiku ortak karar). Su an gerek yok.

## Iliski

- **Onceki:** ADR-0019 (Tier 5 deterministic enforcement) — Tier 6 onun "ruh" tamamlayicisi
- **Cherry-pick kaynagi:** Yok — kit-ozel, Anthropic 2026 eval guidance baseline
- **Sonraki:** Paraphrase-pair stability (gelecek), weekly cron integration

## Kaynaklar

- Anthropic 2026 eval guidance — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- JudgeSense (arxiv 2604.23478) — Prompt sensitivity benchmark
- Anthropic Sonnet 4.5 pricing — $3/$15 input/output, $0.30 cache hit
- Audit raporu `/tmp/ragip_audit_v218_structural.md` — H3 curutuldu, Tier 5 + 6 gerekligini gosterdi
- 16 Mayis 2026 5. davranissal kosum — TEMIZ (Tier 5), Spirit denetlenmedi (Tier 6 motivasyonu)
