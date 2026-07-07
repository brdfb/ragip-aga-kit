# Ragıp Aga — Changelog

Ragıp Aga'ya özgü değişiklik geçmişi. Ana orchestrator CHANGELOG.md'den bağımsızdır.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [2.21.0] - 2026-07-07

### Sonnet 4.5 → Sonnet 5 model güncellemesi (ADR-0022)

7 Temmuz 2026 sağlık kontrolunde hardcoded model referanslarının **10 aylık eski** olduğu tespit edildi (`anthropic/claude-sonnet-4-5-20250929`, Eylül 2025). Mevcut Claude 5 family (Sonnet 5, Opus 4.8, Haiku 4.5) için orchestrator + Tier 6 judge model'i güncellenir.

### Changed

- `config/ragip_aga.yaml` — orchestrator `model: "anthropic/claude-sonnet-4-5-20250929"` → `"anthropic/claude-sonnet-5"`
- `scripts/ragip_judge.py` — Tier 6 judge `DEFAULT_MODEL` → `"anthropic/claude-sonnet-5"`
- `tests/test_ragip_prompt_caching.py` — 5 test satirinda model string güncel (prefix mantigi test edildiği için davranissal etki yok, sadece tutarlı sürüm kaydı)
- VERSION 2.20.3 → 2.21.0 (minor bump — kullanıcı görünür davranış değişikliği)

### Notlar

- **Agent frontmatter kısayolları (`model: sonnet`, `model: haiku`) korundu** — Claude Code otomatik en güncel sürüme resolv ediyor, hardcoded ID gerekmiyor.
- **Fiyat sabitleri (`SONNET_*_USD_PER_MTOK`) dokunulmadı** — Sonnet 5 pricing Anthropic sayfasından teyit edilmediği için muhafazakâr tahmin olarak bırakıldı. Doğrulanınca ayrı patch ile güncellenecek. Cost guard bu nedenle fazla-tutucu tarafta ($0.50 tek/$5 haftalık limit korundu).
- **Tier 6 judge davranissal etkisi ilk kez gerçek modelle** ölçülebilir hale gelir (workspace tarafında API key + litellm sonrası).

### Added

- `docs/adr/0022-model-guncelleme-sonnet-5.md` — Karar gerekçesi ve alternatifler (Opus 4.8 reddedildi, tarihli ID vs alias tercihi).

---

## [2.20.3] - 2026-07-06

### Docs cleanup Faz C — 4 Gibibyte-spesifik skill kit'ten kaldırıldı (ADR-0004 uygulaması, ADR-0021)

v2.20.2 sonrası kit özet kontrolünde "emin misin?" sorusu 4 Nisan 2026 commit `a968919`'un ADR-0004 kural ihlali içerdiğini ortaya çıkardı. **Faz C** bu ihlali düzeltir.

### Removed

- `skills/ragip-teklif/` (Ingram maliyet + MCI teşvik + mevduat float + 3 senaryolu fiyat modeli — Gibibyte satış ekibi)
- `skills/ragip-maliyet/` (Ingram YA vs YM, NCE prim hesabı — Gibibyte satış)
- `skills/ragip-yenileme/` (Lisans yenileme kit list değişim, SKU fark analizi — Gibibyte satış)
- `skills/ragip-esles/` (Satış-alış fatura çapraz doğrulama, kaçak kontrolü — Gibibyte iç kontrol)

Bilgi kaybı yok — bu 4 skill workspace'te identik olarak zaten var (diff -qr temiz). Kit-workspace kopyaları `install.sh` üzerinden her seferinde workspace'in üzerine yazılıyordu (silent duplicate/override).

### Changed

- `agents/ragip-hesap.md` frontmatter: `skills:` listesinden 3 satır çıkarıldı (`teklif`, `maliyet`, `yenileme`)
- `agents/ragip-veri.md` frontmatter: `skills:` listesinden 1 satır çıkarıldı (`esles`)
- `tests/test_ragip_subagents.py`: 3 skill dağılım set'i güncel (global expected + hesap + veri)
- `README.md`: skill listesi (68-72), mimari tablo (95-114) ve rakam tablosu (44) güncel (19 → 15)
- `install.sh`: hardcoded `Skills: 19` → `Skills: 15`
- `docs/FEATURE_IDEAS.md`: `ragip-teklif Adim 3.5` referansına "**workspace-side skill (ADR-0021)**" notu

### Added

- `docs/adr/0021-gibibyte-spesifik-skiller-workspace.md` — Kural takviyesi: skill Gibibyte-spesifik terim/marka/program içeriyorsa workspace'e ait. "Başka bir MSP hedef repo'ya install edilse işe yarar mı?" sınav testi.

### Notlar

- Bu 3 aylık "unutulmuş kısa yol" (4 Nisan 2026 Zeren UAT acil ihtiyacı) v2.20.x doc cleanup silsilesi (Faz A-B-C) sırasında ortaya çıktı — cleanup silsilesinin dolaylı faydası.
- Workspace tarafında dokunulmadı (workspace commit gerekmez — dosyalar zaten orada, olduğu yerde kalıyor).
- Kit'te docs/adr/ 20 → 21, skills/ 19 → 15.

---

## [2.20.2] - 2026-07-05

### Docs cleanup Faz B — 3 sirket dokumanı knowledge-source + continuity-hub'a tasındı

Memory'deki `project_doc_cleanup.md` planının **Faz B** kısmı tamamlandı. Kit'te "gibibyte" konulu 3 doküman doğru repolara taşındı, kit-side kaynak dosyalar silindi.

### Removed

- `docs/GIBIBYTE_DIJITAL_MIMARI.md` → **gibibyte-continuity-hub/docs/**. Doküman website + lead capture implementasyon mimarisi (Brevo/Vercel/D365 pipeline, deploy workflow, blog envanteri) — kit'te değil continuity-hub'da ait. Formal RAG donusumu gerekmedi (docs klasoru build/deploy'a girmez). PR#1 MERGED (`6030b2b6`).
- `docs/REKABET_ISTIHBARATI.md` → **gibibyte-knowledge-source/core_docs/rag/knowledge/KB_COMPETITIVE_INTELLIGENCE.md**. Formal RAG donusumu: YAML frontmatter + 9 major section, her biri RAG-ID + explicit anchor. tool2 + rag-validate full suite PASSED.
- `docs/URUN_YOL_HARITASI.md` → **gibibyte-knowledge-source/core_docs/rag/knowledge/KB_PRODUCT_ROADMAP.md**. Formal RAG donusumu: 7 major section. gb_business_plan.md §1.3+§1.4 ile tamamlayıcı (business_plan resmi/versiyonlu, roadmap operasyonel/çeyreklik). tool2 + rag-validate full suite PASSED.

Knowledge-source PR#15 MERGED (2 KB dokumanı + inventory.json guncel, 65→67 doc).

### Notlar

- Kit-side 3 kaynak dokumanın icerigi git history'de korunuyor (v2.20.1'e checkout ile geri alinabilir).
- Faz B planı `project_doc_cleanup.md` memory'sinde bitmis olarak isaretlendi.
- Kit'te docs/ altinda su an sadece 3 dokuman kaldı: `ECOSYSTEM_MAP.md` (dev-internal repo haritası, kit'te kalır), `FEATURE_IDEAS.md` (kit-relevant backlog), ve `adr/` klasoru (mimari kararlar).

---

## [2.20.1] - 2026-05-21

### Docs cleanup — yanlis yerdeki dokumanlar tasındı/silindi

Memory'deki `project_doc_cleanup.md` planinin Faz A'si. Kit'te uzun suredir bekleyen 2 dokuman temizligi.

### Changed

- `docs/MCP_ENTEGRASYON_REHBERI.md` → **workspace/docs/** tasındı. Workspace MCP'leri burada calıstırır; kullanim rehberi kit'te degil orada olmali. Workspace tarafindaki commit: `d31d654`.

### Removed

- `docs/PROJE_GENEL_BAKIS.md` silindi. README + CHANGELOG ile buyuk olcude duplicate, v2.11.0'da donmus, yanıltıcı eski sayılar iceriyordu (533 test → su an 746, 15 skill → 19). Belge zaten kendi notunda "README.md'ye bakın" diyordu.
- `README.md`'den ilgili tanıtım link satırı cıkarıldı.
- Icerik git history'de korunuyor; gerekirse geri alınabilir.

### Notlar

- `docs/adr/0004-kit-mcp-ayrimi.md` MCP_ENTEGRASYON_REHBERI'ne referans veriyor — **dokunulmadi** (tarihli karar, gecmis referansı).
- `docs/ECOSYSTEM_MAP.md` kit'te kalır. Karar gerekcesi: dev-internal repo haritası, knowledge-source'un formal RAG standardına (YAML frontmatter, RAG-ID, anchor) uymaz; gibibyte-coordinator'a yazma yasagi var; kit'in baslangıc dokumanı.
- Faz B (`GIBIBYTE_DIJITAL_MIMARI`, `REKABET_ISTIHBARATI`, `URUN_YOL_HARITASI` → knowledge-source) **ayrı oturumlara** bırakıldı. Her biri formal RAG donusumu (frontmatter + RAG-ID + anchor + feature branch + rag-validate + PR + CI gate) gerektirir; bu kapsamı atomik bir docs-only patch'e sıgmaz.

---

## [2.20.0] - 2026-05-20

### Tier 6 — LLM-judge Spirit (anlamsal kalite) olcumu (ADR-0020)

v2.19.1 ile 5 katmanli savunma tamamlandi ve davranissal disiplin "harfi" calisti (TEMIZ — Exit 0). Bu surum **ruh** olcumunu ekler.

**Felsefe:**
- Tier 5 (`format_dogrula.py`) = HARF (regex pattern eslesme)
- Tier 6 (`ragip_judge.py`) = RUH (anlamsal kalite)
- **Komplemen, redundant degil.**

### Added

- `scripts/ragip_judge.py` (~370 satir) — LLM-judge Spirit olcumu. Sonnet 4.5 model, 6 dimension Boolean + reasoning JSON, structured output, cost guard
- `scripts/ragip_judge.sh` (~40 satir) — venv-aware bash wrapper, .env'den ANTHROPIC_API_KEY otomatik yukler
- `tests/test_ragip_judge.py` (~280 satir, 27 test) — mock-only, gercek API gerekmez

### 6 Rubric Dimension (anlamsal)

| Dim | Sorgu | Yapisal yakalar mi |
|-----|-------|--------------------|
| T3-1 TESPIT_quality | Insight cumlesi mi yoksa sayi tekrari mi? | Hayir |
| T3-2 ETKI_quality | Tutar/yon/horizon mantikli mi? | Hayir |
| T3-3 POZISYON_quality | Aksiyon spesifik, sahip net mi? | Hayir |
| T3-4 GEREKCE_quality | Mevzuat referansi gercek mi, generic degil mi? | Hayir |
| T3-5 ETIKET_consistency | Anapara etiketleri celiskisiz mi? | Kismi |
| T4 TUTARLILIK_genuine | Denetim notu gercek mi, rubber-stamp mi? | Hayir |

JSON output: `{T3_1_TESPIT_quality: {pass, reasoning}, ..., overall, spirit_score, notes}`.

### Cost guard

- **Pre-check:** tahmini token × fiyat, tek-cagri limitini asarsa abort
- **Post-check:** gercek usage'dan cumulative state guncelle
- **Default:** `--max-budget-usd 0.50` (tek cagri), `--max-cumulative-usd 5.0` (haftalik)
- **State file:** `data/.judge_usage.json` (gitignored, kit ve workspace ayri)
- **Anthropic prompt caching destegi:** cache_control ephemeral, cache hit %90 indirim ($0.30/1M token)

Tipik judge cagrisi: ~$0.016 (3K input + 500 output). Cache hit ile ~$0.011. Haftalik $5 limit ~300 cagri kapasitesi.

### Mimari kararlar (ADR-0020 detayli)

- **Sonnet 4.5 default:** kit `call_llm()` ile uyumlu, judge != generator (Haiku self-enhancement bias)
- **Minimal dict + manual validation:** Pydantic yeni bagimlilik gereksiz (kit requirements minimal 5 paket)
- **Mock-only pytest:** gercek API gerekmez, hizli + ucretsiz + deterministic
- **Manuel cadence:** haftalik (~10 cikti), CI auto degil

### Changed

- `tests/test_ragip_install.py:73` — manifest dosya sayisi 57 → 59 (judge.py + judge.sh + test eklenmesi nedeniyle)
- `README.md` madde 21 — Tier 6 LLM-judge referansi
- `CLAUDE.md` test listesi — `test_ragip_judge.py` eklendi
- `docs/FEATURE_IDEAS.md` #19b — Tier 6 (B2 LLM-judge) tamamlandi notu

### Sinirlamalar ve gelecek

- **Judge prompt sensitivity** (JudgeSense arxiv 2604.23478) — paraphrase-pair stability test gelecek calisma
- **Tahmini token guard** (1 token ~= 4 char) kaba, ama pre-check icin yeterli
- **Manuel cadence** — otomatik tetik gelecek (`scripts/ragip_cron.sh judge` haftalik)
- **Integration test** — `ANTHROPIC_API_KEY` env'de varsa manuel calistir (pytest'te degil)

### Tests

746 test (719 + 27 yeni `test_ragip_judge.py`). Mock-only, hepsi gecti, gercek API gerekmez.

---

## [2.19.1] - 2026-05-16

### Tier 5 regex multi-line fix (5. davranissal kosum gozlemine yanit)

16 Mayis 5. Yontem 2B kosumu **buyuk basari** verdi: v2.19.0 sonrasi cikti dosyasi yazildi, manuel rubric **11/13 esleme** (onceki 0/13'lerden buyuk iyilesme). Ama Tier 5 format_dogrula scripti Exit 2 verdi — POZISYON 5-bilesen "0" diye raporladi.

**Sebep:** Skill ornegi POZISYON satirini tek-satir middot (`·`) ile gosteriyor, ama LLM dogal yaziminda **2-satir + pipe (`|`)** kullandi:

```
POZISYON: Noter ihtari gonder
  Sahip: Hukuk | Zaman: 5 is gunu | Beklenen: 30 gun tahsilat
```

Bilgi mevcut, satirlandirma farkli. Regex `^POZISYON:.*Sahip:\s*\S+.*Zaman:\s*\S+.*Beklenen:\s*\S+` newline kabul etmedigi icin yakalayamadi.

### Changed — Tier 5 RE_POZ_5BIL regex multi-line

**Onceki:** `r"^POZISYON:.*Sahip:\s*\S+.*Zaman:\s*\S+.*Beklenen:\s*\S+"` (tek satir)

**Yeni:** `r"^POZISYON:[\s\S]{1,300}?Sahip:[\s\S]{1,100}?Zaman:[\s\S]{1,100}?Beklenen:"`

- `[\s\S]{1,300}?` newline-iceren, non-greedy, max ~300 char (yaklasik 3-4 satir)
- POZISYON: ile sonraki 1-3 satir araliginda Sahip/Zaman/Beklenen kabul

### Added — test fixture

- `MULTI_LINE_POZ_TEMIZ` fixture: 5. davranissal kosumun gercek format (2 satir + pipe separator)
- `test_multi_line_pozisyon_temiz`: regex multi-line yakaliyor mu

### Davranissal etki

5. kosum cikti'sina `bash scripts/ragip_format_dogrula.sh` tekrar kosulduktan sonra: **TEMIZ — Exit 0** (TESPIT:4, Etki:4, POZISYON:4 5-bilesen:4, Anapara etiket:3, Tutarlilik denetimi:1). Tier 3/4 disiplinin **tamamen calisiyor**.

### Tests

720 test (719 onceki + 1 yeni `test_multi_line_pozisyon_temiz`). Hepsi gecti.

### Sonuc — v2.16 → v2.19.1 yolculugu

| Versiyon | Yaklasim | Yapisal eslesme |
|----------|----------|------------------|
| v2.16.0  | Tier 3 skill'e eklendi | 0/13 |
| v2.17.0  | Tier 4 eklendi | 0/13 |
| v2.18.0  | Tier 3 zenginlestirme | 0/13 |
| v2.18.1  | Agent prompt koordinasyon | dosya yazmadi |
| v2.18.2  | maxTurns 12 → 20 | dosya yazmadi (yine maxTurns) |
| v2.19.0  | Tier 5 deterministic script | **11/13** (Tier 5 Exit 2 — false positive) |
| **v2.19.1** | **Regex multi-line fix** | **13/13 (TEMIZ — Exit 0)** ✓ |

**Ana ders:** Prompt-engineering + agent koordinasyon + maxTurns + Tier 5 deterministic + regex pratiklik — **5 katmanli savunma** birlikte calismali. Tek bir katman yetersiz.

---

## [2.19.0] - 2026-05-16

### Tier 5 deterministic format enforcement (ADR-0019 revize)

**Workspace prototyping → kit propagation.** 15 Mayis workspace'te audit H3 hipotezi (few-shot block confusion) **curutuldu** — agent system prompt'una Tier 3/4 spec'i v2.18.1 ile eklendi ama 4. Yontem 2B kosumunda **yine 0/13 esleme**. Prompt-engineering (Tier 1-4) yapisal sinira ulasti.

Cozum: **Tier 5 deterministic regex post-write check.** LLM ciktisini script ile tarayip 5 zorunlu sinyali dogrular. Exit 2 = blok eksik → LLM raporu duzeltmek zorunda. Audit fallback secenegi (d) regenerate cycle'in basit hali.

**5 zorunlu sinyal:**

1. **[T3-1]** `TESPIT:` bullet (SONUC VE ONERILER icinde Tier 3 blok)
2. **[T3-2]** `Etki:` satiri ($ tutar / % / yon ↑↓⇄ / horizon)
3. **[T3-3]** `POZISYON:` 5-bilesen (fiil · Sahip · Zaman · Beklenen)
4. **[T3-4]** Anapara etiketi `(nominal)` veya `(kalan)` — kelime gectiyse zorunlu
5. **[T4]** `Tutarlilik denetimi:` kapanis notu (`temiz.` veya `X celiski bulundu`)

### Added

- `scripts/ragip_format_dogrula.py` (171 satir, regex-based detector) — 5 sinyal kontrol, Exit 0/1/2 kodlari, JSON ve text cikti
- `scripts/ragip_format_dogrula.sh` (37 satir, venv-aware bash wrapper)
- `tests/test_ragip_format_dogrula.py` (22 test: unit + CLI + bash + gercek cikti regression)

### Changed — 3 LLM skill'inde Tier 5 Adim 11 eklendi

- `skills/ragip-degerlendirme/SKILL.md` — Adim 11 FORMAT DOGRULAMA (Madde dogrula sonrasi, dosya yazildiktan sonra)
- `skills/ragip-analiz/SKILL.md` — Adim 7c FORMAT DOGRULAMA
- `skills/ragip-strateji/SKILL.md` — Adim 4b FORMAT DOGRULAMA

Davranis: Skill rapor dosyasini yazdiktan sonra `bash scripts/ragip_format_dogrula.sh <cikti>` zorunlu calistirir. Exit 2 → eksik sinyalleri okuyup raporu duzeltir, tekrar dogrula. Exit 0 → temiz, devam.

### ADR-0019 revize

- **H3 (few-shot block confusion) curutuldu** — agent file `ragip-hukuk.md:182-211` v2.18.1 sonrasi Tier 3 spec icermesine ragmen 0 esleme. Block confusion ana sebep degildi.
- **Tier 5 implementation log** eklendi — 5 sinyal kontrolu, prompt-engineering 0/13 → script-enforcement %100 (test edildi).
- **Sonraki gelisim:** `scripts/ragip_blok_regenerate.py` (LLM self-correction loop) — maxTurns hard cut + Exit 2 sinyali iletisiminde gerekli olabilir.

### Tests

719 test gecti (697 onceki + 22 yeni `test_ragip_format_dogrula.py`).
22 yeni test:
- Unit (regex detector): TESPIT/Etki/POZISYON/Anapara/Tutarlilik kontrol
- CLI: Exit kodlari, --json output, stdin input
- Bash wrapper: venv detection, hata kodlari
- Regression: 3 gercek cikti (Guven Pres v2.16.0, v2.17.0, v2.18.0) hepsi Exit 2 (Tier 5 eksik) — beklenen davranis

### Davranissal test (manuel, workspace v2.19.0'da)

3 senaryo (Guven Pres + Plastay + Demo stratejik) tekrar kosulmali. Bu sefer skill icinde Tier 5 dogrulamasi calisacak — LLM eksik bloklari gormeden raporu teslim edemez. Beklenti: yapisal eslesme 10+/13 (5 zorunlu sinyal + 3-5 niyet sinyali).

### Sinirlar ve gelecek

- **Tier 5 maxTurns'a duyarli:** Sub-agent rapor yazma + Exit 2 + duzeltme dongusu 3-4 turn yer. ragip-hukuk/arastirma maxTurns: 20 (v2.18.2) tampon saglar ama yetmezse `ragip_blok_regenerate.py` (LLM self-correction harici loop) gerekli olur.
- **Sub-agent dispatch'te:** Sub-agent skill icinde Tier 5 cagrisi yapar. Orchestrator (ragip-aga) direkt yapmaz — sub-agent sorumluluk dagilimi korunur.
- **B2 LLM-judge (FEATURE_IDEAS #19):** Tier 5'in meta-testi olarak hala backlog'da. Tier 5 deterministik ama "ruh"u olcmez (niyet sinyaller, etiket tutarliligi vb). B2 spirit + letter ikisi.

### Memory

`feedback_skill_agent_koordinasyon.md` update edilmeli (sonraki oturum) — H3 curutuldu, Tier 5 eklendi, prompt-engineering sinirina ulasildi yorumu.

---

## [2.18.2] - 2026-05-15

### Sub-agent maxTurns hard-cut fix (spot-patch)

**Bulgu (15 Mayis 2026, v2.18.1 sonrasi Yontem 2B kosumu):** v2.18.1 koordinasyon fix dogru ama davranissal test edilemedi — sub-agent CoVe akisi (10 adim: Read+Bash+verification+sentez+dosya yaz+madde dogrula+Tier 4) 12 turn maxTurns limitine vuruyor, **dosya yazma adimina ulasmadan** kesiliyor. 16 tool use'a uzayan kosum stdout'ta cikti uretiyor ama disk'e yazmadan duruyor.

**Asil sebep:** Adim 8 (final yaz + dosya kayit) skill akisinin 8/10'unda. CoVe disiplinli skill'lerde Adim 1-7 internal/Bash/Read agirligi 10-12 turn yiyor — Adim 8'e varilmiyor. Sub-agent ciktida "raporu yaziyorum" diyip kesiliyor.

### Changed — maxTurns degerleri

| Agent | Eski | Yeni | Sebep |
|-------|-----:|-----:|-------|
| `agents/ragip-hukuk.md:38` | 12 | **20** | CoVe + madde_dogrula + Tier 4 |
| `agents/ragip-arastirma.md:37` | 12 | **20** | DRAFT + 3-senaryo + Tier 4 |
| `agents/ragip-hesap.md` | 12 | 12 | Hesap motoru CoVe disiplinsiz, test patterni "5-12 turn" koruyor — degisme |
| `agents/ragip-veri.md` | 12 | 12 | CRUD basit, degisme |
| `agents/ragip-aga.md` | 20 | 20 | Orchestrator, degisme |

### Etki

- Sub-agent kosum maliyeti ~%30 artar (en kotu durum), ama davranissal disiplinin uygulanmasi icin gerekli mekanik alan acilir.
- v2.18.1 fix (skill ↔ agent koordinasyon) bu spot-fix ile davranissal olarak test edilebilir hale gelir.
- Adim 5 ve 8'in birlestirilmesi (DRAFT-as-final) gelecek calisma (v2.19.0+ — CoVe disiplini ile uyumlu mu degil mi degerlendirme gerek).

### Tests

Tum 697 test gecti (yapisal). Pre-commit hook calisti.

### Davranissal test (manuel — workspace v2.18.2'de)

3 senaryo (Guven Pres + Plastay + Demo stratejik) tekrar kosulmali. Bu sefer maxTurns artisi nedeniyle dosya yazma adimina ulasilmasi beklenir. Rubric grep ile yapisal eslesme hedef: **8+/13**.

---

## [2.18.1] - 2026-05-14

### Tier 3/4 propagation fix — Skill ↔ Agent koordinasyon (audit-driven)

**Bulgu:** 14 Mayis Yontem 2B regresyon testleri (3 ardisik versiyon: v2.16.0/v2.17.0/v2.18.0) gosterdi ki Tier 3/4 prompt-level disiplin **modele davranis olarak yansimadi** — 3 farkli run, hepsinde 0/13 yapisal eslesme (TESPIT/POZISYON/GEREKCE blok, Etki:, Sahip/Zaman/Beklenen, anapara nominal/kalan etiketi, Tutarlilik denetimi notu, VARSAYIM damgasi). Niyet eslesmesi 6/9 — model disiplinin **ruhunu** yakaladi, **harfini** atlatdi.

**Yapisal kok sebep (audit, /tmp/ragip_audit_v218_structural.md):** Skill SKILL.md'lere Tier 3/4 spec'i eklendi ama **agent system prompt'lari guncellenmedi**. `ragip-hukuk.md:182-192` ve `ragip-arastirma.md:168-178` "YANIT FORMATIN" bolumleri Tier 3/4 ile celisen narrative format dayatiyor. Model agent prompt'unu **birincil otorite** olarak okuyor, skill format'i ikincil rehber.

### Changed — Agent system prompt'lari

- `agents/ragip-hukuk.md:182-218` — "YANIT FORMATIN" bolumu Tier 3/4 spec ozeti ile birlestirildi. 6-bolum narrative koruma + SONUC VE ONERILER icinde **Tier 3 ZORUNLU 3-satir blok** + RISK NOTU sonrasi **TUTARLILIK DENETIMI ZORUNLU** kapanis bolumu. Persona vs format ayrimi acikca yazildi ("Evladim" narrative, TESPIT: format — celismez).
- `agents/ragip-arastirma.md:168-198` — Ayni patern: 6-bolum koruma + SOMUT ADIMLAR icinde **Tier 3 ZORUNLU** + TUTARLILIK DENETIMI kapanis.

### Changed — Skill basina Tier 3/4 ozet (Lost-in-the-Middle fix)

3 skill'in **2. satirinda** (description'dan hemen sonra) `## CIKTI FORMATI (Tier 3/4 ZORUNLU — ILK OKU)` bolumu eklendi. Modelin ilk dikkat hattinda Tier 3/4 zorunlulugu hatirlatilir. Detay (CORRECT/WRONG ornek) skill ortasinda kalir:

- `skills/ragip-degerlendirme/SKILL.md:12-30` — eklendi
- `skills/ragip-analiz/SKILL.md:10-26` — eklendi
- `skills/ragip-strateji/SKILL.md:10-26` — eklendi

### Changed — WRONG/CORRECT ornek firma adlari notrlestirildi

Model few-shot ornegi "**bu firma icin yazildi**" gibi okuyordu (audit H3 hipotezi). Notr ad ile "format ornegi" oldugu daha net algilanir:

- `skills/ragip-degerlendirme/SKILL.md:200` — "Guven Pres" → "Demo Sanayi A.S."
- `skills/ragip-strateji/SKILL.md:129, 138` — "Zeren" → "Demo IT Hizmetleri"
- `skills/ragip-analiz/SKILL.md` — "ABC Dagitim" zaten notr, degisiklik yok

### Changed — Tier 4 cikti template'e gomuldu (3 skill cikti format bolumu)

Tier 4 talimat skill'in arkasinda kalmis, model "bitti" diyince denetim adimini atlamis (audit H5). Cikti template'ine **`### TUTARLILIK DENETIMI`** bolumu zorunlu kapanis olarak gomuldu:

- `skills/ragip-degerlendirme/SKILL.md:279-310` — SONUC VE ONERI Tier 3 zenginlestirme + TUTARLILIK DENETIMI bolumu
- `skills/ragip-analiz/SKILL.md:314-336` — ONERILEN ADIMLAR Tier 3 zenginlestirme + TUTARLILIK DENETIMI bolumu
- `skills/ragip-strateji/SKILL.md:218-258` — RAGIP AGA'NIN TAVSIYESI + BU HAFTA YAPILACAKLAR Tier 3 + TUTARLILIK DENETIMI bolumu

### Documentation

- `docs/adr/0019-skill-agent-koordinasyon.md` — yeni ADR. Skill'e yeni cikti disiplin eklendiginde **ilgili agent system prompt'unun da guncellenmesi zorunlu** kurali. Yoksa agent prompt skill spec'ini override eder. Audit raporu line-no kanitlari ile.

### Behavioral test (manuel)

v2.18.1 sonrası 3 kosum tekrari (Guven Pres Yontem 2B + Senaryo A + ucuncu firma) gerekli. Yapisal eslesme oranı **8+/13** beklenir (audit B1 (a) yaklasimi). 0/13 hala duruyorsa v2.19.0'da (c) structured output veya (b) post-process Python.

### Tests

Tum 697 test gecti (yapisal Tier 4 dahil). Davranissal test dahil edilmedi — manuel kosum ile gozlemlenir.

---

## [2.18.0] - 2026-05-14

### Tier 3 yeniden tasarim — Lead With Insight + Quantify Impact + Action 5-bilesen + Etiket

**Cherry-pick:** AI CFO Assistant System Prompt v2.0 (Master Pack v2.0, Mayis 2026). Tier 3 cikti disiplini 4 yeni boyutla genisletildi. Mevcut TESPIT/POZISYON/GEREKCE iskeleti korundu, format **3-satir → 5-satir zenginlestirilmis** hale getirildi.

### Changed — Tier 3 formati

Yeni blok formati (3 LLM skill'inde):

```
TESPIT: <insight cumlesi — somut alıntı + madde + tutar + ETIKET>
   Etki: <X TL/USD> (%<Y>) <↑↓⇄> <30/60/90 gun veya kalici>
POZISYON: <fiil> · Sahip: <kim> · Zaman: <ne zaman> · Beklenen: <X>
GEREKCE: <opsiyonel>
```

4 yeni boyut:
1. **A1 Lead With the Insight** — TESPIT sayisal degil **yorum** ile baslar. WRONG/CORRECT ornek skill prompt'unda few-shot.
2. **A2 Quantify Impact 4-bilesen** — Etki satiri: $ tutar / % etki / yon (↑↓⇄) / horizon (gun/kalici).
3. **A4 Action Format 5-bilesen** — POZISYON inline: fiil + Sahip + Zaman + Beklenen.
4. **#3 Etiket netligi** — Sayisal iddialar acik etiketli (`nominal` vs `kalan` vs `vade tutari`). Patch #4'un Tier 3 entegrasyonu.

Her 3 skill icin domain-spesifik WRONG/CORRECT ornekler:
- **ragip-analiz**: vade farki uygulanmamis sozlesme bulgu
- **ragip-strateji**: Zeren-tarzi rakip pazarlik MCI+Float kozu
- **ragip-degerlendirme**: Guven Pres alacak ihtari (konkordato bağlamı)

### Files

- **skills/ragip-analiz/SKILL.md**, **skills/ragip-strateji/SKILL.md**, **skills/ragip-degerlendirme/SKILL.md**: Tier 3 bolumu yeniden yazildi.
- **docs/adr/0016-cikti-disiplini-tier-3.md**: v2.18.0 Genisletme bolumu eklendi. Cherry-pick gerekce, 4 boyut, davranissal beklenti, sinirlamalar.
- **tests/test_ragip_cikti_disiplini.py**: TestTier3V218Zenginlestirme + TestAdr0016V218Genisletme sinifları. 17 yeni test (A1 ornek, A2 4-bilesen, A4 5-bilesen, #3 etiket, cherry-pick kaynagi, ADR v2.18.0 bolumu + yeni format ornegi).

### Test toplam

680 → **697** (+17 yeni). 0 regression.

### Davranissal beklenti (henuz dogrulanmadi)

v2.18.0 sonrasi Yontem 2B regresyon testi (Guven Pres veya benzeri):
- Tier 3 5-satir blok ciktida gozlemlenebilir mi? Wrong/Correct few-shot ile davranissal uyum **artmali**.
- Etki satiri ($/%/yon/horizon) cikti'da?
- POZISYON 5-bilesen (Sahip/Zaman/Beklenen) acik?
- Etiket (nominal/kalan) "anapara" bahislerinde?

**Davranissal test altyapisi v2.19.0 LLM-judge ile gelir** — bu surumdeki yapisal degisiklikler few-shot prompting ile davranissal etkiyi artirmayi hedefler ama olcum sonraki release.

### Migration

Workspace tarafinda `bash <kit>/update.sh` ile gelir. Mevcut Tier 4 (ADR-0018) ve Tier 1 (A5) korunur — Tier 3 yeni format onlarla **uyumlu** (Tutarlilik denetimi etiketleri uygulanir, kesinlik kalibi yeni Etki satirina genisler).

### Why

v2.16.0/v2.17.0 davranissal regresyon testleri (Guven Pres, 14 Mayis 2026) gosterdi ki orijinal 3-satir blok format (TESPIT/POZISYON/GEREKCE) **prompt'ta var ama model uygulamiyor** — gozlem: cikti'da 0 esleme. Iki sebebi var:

1. **Format yetersiz**: Sayisal etki/sahip/zaman/beklenen gibi karar verici icin kritik alanlar yok. Model "TESPIT ne anlama geliyor?" sorusunu kendi cevaplayabilirken bunu formata sigdiramiyor.
2. **Few-shot yok**: Mevcut prompt sadece template tarif eder — Wrong/Correct gercekci ornek yok. Model formati anlamak icin orneklere bagimli.

v2.18.0 ikisini de kapatir: zenginlestirilmis format **karar veriye dair tum boyutlari** yakalar, Wrong/Correct ornek **model davranissinin sekillenmesini** kolaylastir.

Bu degisiklik kit kapsam genisletme **degildir** — mevcut LLM skill'lerinde Tier 3 prensibi gucturlur, yeni kavram eklenmez. AI CFO Assistant System Prompt v2.0 cherry-pick'i kit-disi bir urunun system prompt'undan **disiplin pattern'leri** turetir; o urunun mimari/kapsami farkli kalir.

## [2.17.1] - 2026-05-14

### Self-review duzeltmeleri

v2.17.0 sonrasi `/review` self-review bulgularinin (5 suggestion + 1 yardimci) hizli kazan paketi. Davranissal etki yok ama prompt netligi, terminoloji ve yedek temizlik araclari.

### Changed — A5 pozitif yonlendirme

"Kesinlik kalibi" kurali sadelestirildi: iki acik kural (1) veri yoksa olasilik dili kullan ("olası/muhtemel/tahmin/belirsiz"), (2) mutlak ifadeler SADECE veri-yok durumunda yasak. Onceki mutlak yasagi Turkce'de legitimate kullanimlari (orn: "hukum kesinlesti", "kesin alacak") yakaliyordu.

- **skills/ragip-analiz/SKILL.md**, **skills/ragip-strateji/SKILL.md**, **skills/ragip-degerlendirme/SKILL.md**: 6b/2b/Adim-8 kurallari yeniden yazildi.
- **tests/test_ragip_cikti_disiplini.py**: 6 yeni test (TestKesinlikKalibi sinifina pozitif_olasilik_dili + veri_yok_kosullu_yasak, 3 skill x 2 test).

### Changed — Patch #1 PRD prompt sadelestirme

Onceki fallback metni model environment'i goremezken "ortam degiskeni" tetikleyici onerdi — yanlislik kabul edildi. Yeni semantik:

- Fallback ANCAK kullanici acik sinyal verirse tetiklenir (orn: "non-interactive moddayim", `[CRON]` etiketi)
- Belirsiz sessizlik fallback YOK (yanlis dispatch riski)
- Asil cozumun kit-disi (CLI/wrapper) oldugu acikca belirtildi → v2.19.0+

Dosyalar:
- **agents/ragip-aga.md**: Non-interactive fallback bolumu yeniden yazildi.
- **tests/test_ragip_prd_disiplini.py**: TestNonInteractiveFallback.test_v2_17_1_acik_sinyal_semantigi yeni test.

### Docs — ADR-0018 metadata netlestirme

Cherry-pick referansinin sabit URL/yol icermesi gibibyte-cfo-agent'in yer karari beklemesi nedeniyle riskli. ADR-0018'e kaynak yeri belirsizligi notu eklendi (disiplin pattern'i alindi, kod dosyasi degil; kaynak yeri degisirse ADR icerigi etkilenmez).

- **docs/adr/0018-tier-4-dokuman-tutarlilik.md**: Cherry-pick kaynagi alt-bolumu genisletildi.

### Added — Yedek temizleme yardimcisi (scripts/ragip_yedek_temizle.sh)

update.sh manifest tutarsizligi sonucu olusan SAHTE yedekleri (`.kullanici-yedek-YYYYMMDD` formatli, icerigi kit history'sindeki herhangi bir versiyonla ayni) ayikla. Gercek kullanici ozellestirmesi olan yedekler KORUNUR. Dry-run varsayilan.

- **scripts/ragip_yedek_temizle.sh**: Yeni script. Git history araştırmasi ile kit versiyonu eslemesi.
- **tests/test_ragip_yedek_temizle.py**: 6 test (script var, --help, sahte sil, gercek koru, bos repo, manifest yok).
- **install.sh**: Yeni script kopyalanir ve manifest'e eklenir (10 → 11 script).

### Test toplam

667 → **680** (+13 yeni: A5 6 + Patch #1 1 + yedek_temizle 6 — install manifest count 54 → 56).

### Migration

- Workspace tarafinda eski yedek dosyalarini (v2.17.0 update'inden olusan 19 sahte) temizlemek icin:
  ```bash
  cd <workspace>
  bash <kit>/scripts/ragip_yedek_temizle.sh           # Dry-run rapor
  bash <kit>/scripts/ragip_yedek_temizle.sh --apply   # Gercekten sil
  ```
- Yeni v2.17.1 dosyalari `bash <kit>/update.sh` ile gelir (kucuk degisiklikler, regresyon yok).

### Why

v2.17.0 commit'inden hemen sonra yapilan self-review 5 prompt netligi sorunu + 1 yardimci araç ihtiyaci tespit etti. Hizli kazanlar paketi (v2.17.1 patch release) bunlari yapisal degisiklik olmadan duzeltir. Davranissal etki sinirli ama **prompt netligi ve terminoloji** ileride v2.18.0/v2.19.0 calismasi icin temiz zemin saglar.

## [2.17.0] - 2026-05-14

### Test bulgulari + disiplin guclendirme

14 Mayis 2026 Guven Pres gercek senaryo testi (Yontem 2A/2B) bulgulari:
- PRD orchestrator non-interactive modda stuck (Patch #1)
- Tier 2C reactive nature belirsiz (Patch #3, belge)
- Acik alacak tutar etiket netligi (Patch #4)
- update.sh "yeni" dosya yedeksiz uzerine yazma bug (Patch #5)
- Tier 3 cikti disiplini gercek davranisi zayif → Tier 4 (cherry-pick CFO K3, B1) ve Tier 1 ek (cherry-pick CFO K2, A5)

### Added — Tier 4 dokuman tutarlilik kontrolu (B1, ADR-0018)

Defense-in-depth dorduncu katman: ragip-analiz/strateji/degerlendirme cikti sentez fazinin son adimi olarak self-check. Sayisal/etiket/mantik/senaryo tutarliligi. Cherry-pick: gibibyte-cfo-agent v0.2 K3.

- **skills/ragip-analiz/SKILL.md**, **skills/ragip-strateji/SKILL.md**, **skills/ragip-degerlendirme/SKILL.md**: "Tutarlilik denetimi (Tier 4)" alt-adimi eklendi. 4 kategori (SAYI/ETIKET/MANTIK/SENARYO), cikti notu formati.
- **docs/adr/0018-tier-4-dokuman-tutarlilik.md**: Yeni ADR. Cherry-pick gerekce, kapsam tablosu, sinirlamalar (model self-check zayif olabilir), gelecek calisma (LLM-judge, programmatik check).
- **tests/test_ragip_tutarlilik.py**: 18 test — prompt'larda Tier 4 terimi, ADR-0018 referansi, 4-kategori, denetim notu formati, deterministik skill'lerde uygulanmamis, ADR icerigi/cherry-pick kaynagi.

### Added — Tier 1 Barnum 'Do not fabricate certainty' (A5)

Veri eksik/tutarsizken mutlak ifade ("kesin", "muhakkak", "kesinlikle") yasagi. Cherry-pick: gibibyte-cfo-agent v0.2 K2 + AI CFO Assistant System Prompt Data Quality Rule.

- **skills/ragip-analiz/SKILL.md** (6b), **skills/ragip-strateji/SKILL.md** (2b), **skills/ragip-degerlendirme/SKILL.md** (Adim 8): "Kesinlik kalibi" alt-kurali Barnum yanina eklendi.
- **tests/test_ragip_cikti_disiplini.py**: TestKesinlikKalibi sinifi, 9 test (kurali var, "Do not fabricate certainty" ifadesi, mutlak ifade yasagi ornekleri).

### Fixed — Patch #1: PRD non-interactive fallback

ragip-aga orchestrator `claude -p` modunda kullanici girdisi olmadigi icin PRD onay sorusu sonsuza kadar bekledi (test bulgusu: 10 dk timeout). Fallback davranisi: PRD ozetini cikti basina yaz, otomatik dispatch.

- **agents/ragip-aga.md**: PRD DISIPLINI bolumune "Non-interactive fallback" eklendi. Stuck olmaz, audit korunur (PRD ozeti cikti'da).
- **docs/adr/0017-orchestrator-prd-disiplini.md**: Sinirlamalar listesine non-interactive notu, "Non-interactive fallback (v2.17.0)" alt-bolumu.
- **tests/test_ragip_prd_disiplini.py**: TestNonInteractiveFallback sinifi, 3 test (agent prompt'unda non-interactive kelimesi, fallback kavramlari, ADR referansi).

### Fixed — Patch #4: Acik alacak tutar etiket netligi

`aging_raporu` doc string ve cikti dict'i netlestirildi. Kismi odeme varsa nominal vs kalan ayrimi acik (hukuki ihtar/alacak bildirim sirasinda kritik).

- **scripts/ragip_aga.py:aging_raporu**: Doc string genisletildi (toplam vs kalan tanimi). Yeni cikti alanlari: `nominal_acik_toplam_tl`, `kismi_odenmis_adet`. Yorum metni kismi odeme varsa nominal+kalan ikisini de gosterir. Geriye uyumlu (mevcut `toplam_acik_alacak_tl` korundu).
- **tests/test_ragip_fatura_analiz.py**: 3 yeni test (nominal vs kalan farki, kismi odeme yoksa nominal=kalan, yorum metni kismi uyarisi).

### Fixed — Patch #5: update.sh "yeni" dosya yedeksiz uzerine yazma

Manifest'te olmayan ama disk'te bulunan dosyalar (manuel sync senaryosu) yedeksiz uzerine yaziliyordu — kullanici ozellestirmesi varsa veri kaybi.

- **update.sh**: `new_files` dongusu disk varligi kontrol eder. Hash ayni → skipped_unchanged. Hash farkli → conflicts (yedek + uzerine yaz).
- **tests/test_ragip_install.py**: 2 yeni test (manifest dısı disk-ayni → yedek olmamali, manifest dısı disk-farkli → yedek olusmali).

### Docs — Patch #3: Tier 2C reactive notu

WebSearch tetiklenmedikce Tier 2C devreye girmez — "bos koruma" izlenimi vermesin diye reactive nature ADR'a yazildi.

- **docs/adr/0015-citation-source-whitelist.md**: "Tetik kosulu (reactive, v2.17.0 netlestirmesi)" alt-bolumu. Proactive tetik tasarim karari (hayir — opt-in).

### Why

Gercek senaryo testi gostermistir ki v2.14.0-2.16.0 (Tier 2C/3/PRD) cherry-pick'leri tek baslarina yetmiyor — non-interactive senaryo, etiket belirsizligi, post-generation cross-check eksikligi gibi bosluklar var. v2.17.0 bu bosluklari sistemli kapatir: Tier 4 (dokuman tutarlilik), Tier 1 ek (kesinlik kalibi), Patch #1-5 (test-driven bugfix). Hepsi prompt-level, geri alinabilir, davranissal test ile dogrulanabilir.

### Test toplam

667 test (onceki 632 + 35 yeni: Patch #5 2 + Patch #1 3 + A5 9 + Patch #4 3 + B1 18).

### Migration

Workspace v2.16.0 → v2.17.0 update.sh ile gecirilebilir. Tier 4 prompt'lari skill'lere otomatik gelir. FinansalHesap.aging_raporu cikti dict'i geriye uyumlu (yeni alanlar eklendi, mevcut alanlar degismedi). update.sh new-file bug fix mevcut workspace'lerde sahte cakisma yedeklerini onler.

## [2.16.0] - 2026-05-13

### Added — Orchestrator PRD Disiplini (FEATURE_IDEAS #22, ADR-0017)

ragip-aga orchestrator karmasik isler icin **PRD (Plan/Recap/Direction) zorunlu**: dispatch oncesi 1-2 satir plan + kullanici onayi. Trivial isler bypass (hesaplama, listele, ozet — dogrudan dispatch). gibibyte-cfo-agent v0.2 K4 cherry-pick.

- **agents/ragip-aga.md**: "PRD DISIPLINI" bolumu eklendi. Karmasik is tetigi anahtar kelimeleri (tam analiz, strateji, ihtar, dosya hazirla, firma degerlendirmesi), PRD formati ornegi, onay/red akisi, trivial bypass kategorileri. CALISMA AKISI Adim 2'ye "PRD karari" eklendi.
- **tests/test_ragip_prd_disiplini.py**: 20 test — PRD section header, ADR referansi, cherry-pick kaynagi, tetik anahtar kelimeleri (5 kategori), PRD format ornegi, onay/red kelimeleri, trivial bypass ornekleri, CALISMA AKISI entegrasyonu.
- **docs/adr/0017-orchestrator-prd-disiplini.md**: K4 K4 disiplinin kit'e uyarlanmasi, alternatif yaklasimlar (her dispatch'te PRD reddedildi cunku trivial overhead), I8 Senaryo A sinirlarini disipline cevirme.

### Why

ragip-aga karmasik dispatch'ler icin (sozlesme analizi + strateji + ihtar dosyasi) Agent tool ile dogrudan dispatch yapiyordu. Yanlis dispatch maliyeti yuksek (saatler kaybedilir, kullanici geri donus geriyle gelir). PRD disiplini yanlis dispatch oranını azaltir, karmasik isler kullaniciyla onceden hizalanir. Trivial bypass kullanici frustrationunu engeller.

I8 Senaryo A: ragip-aga interaktif modda ilk mesajda dispatch yapmama davranisini gozlemlemis ama yapisal degildi. PRD disiplini bu davranisi DISIPLINE cevirir — "dispatch yapma" yerine "PRD ver" yapisal alternatif.

### Test toplam

632 test (onceki 612 + 20 PRD disiplini).

### install.sh

`test_manifest_file_count`: 52 → 53 (+1 test dosyasi).

---

## [2.15.0] - 2026-05-13

### Added — Tier 3 Cikti Disiplini: 3-satir blok + VARSAYIM damgasi (FEATURE_IDEAS #20, ADR-0016)

ragip-analiz, ragip-strateji, ragip-degerlendirme LLM-driven skill'lere **3-satir TESPIT/POZISYON/GEREKCE** kritik-bulgu formati ve **VARSAYIM damgasi** zorunluluk olarak eklendi. Tier 1 (Barnum) + Tier 2A/B/C (citation defense) ustune **besinci savunma katmani** — cikti formati ve belirsizlik tanima.

- **skills/ragip-analiz/SKILL.md**: Step 7 "Cikti disiplini" eklendi (Madde dogrulama 8→9). Output Format: KRITIK MADDELER, ELINDEKI KOZLAR, RISKLER her biri 3-satir blok.
- **skills/ragip-strateji/SKILL.md**: Step 3 "Cikti disiplini" eklendi (Madde dogrulama 3→4). RAGIP AGA'NIN TAVSIYESI + BU HAFTA YAPILACAKLAR 3-satir formatinda.
- **skills/ragip-degerlendirme/SKILL.md**: Step 8 Barnum + Cikti disiplini birlestirildi. SONUC VE ONERI 3-satir formatinda. Anlatim paragraflari (HUKUKI DEGERLENDIRME, MADDE BAZLI ANALIZ) serbest.
- **tests/test_ragip_cikti_disiplini.py**: 23 test — uc skill icin TESPIT/POZISYON/GEREKCE, VARSAYIM damgasi, aralik kurali, ses korundu kontrolu, deterministik skill'lerin kapsam disi.
- **docs/adr/0016-cikti-disiplini-tier-3.md**: X5 reddi (full template) ile distinction: kritik bulgu blok formati, full template degil. K2 + 3-satir disiplini gibibyte-cfo-agent v0.2 cherry-pick.

### Why

Mevcut bulgu listeleri serbest-format, yumusatici dil ("dikkatli incelenmeli", "olabilir") icerebiliyor, kritik bulgular paragraflar arasinda kayboluyor. Sayisal iddialarda LLM tek-noktali tahmin verirken overconfidence bias (arXiv 2512.16030, 2025) — kullaniciyi yanlis kesinlik hissine sokuyor. Tier 3 disiplini yapisal sunumla okuma surati arttirir, VARSAYIM damgasi aralik kullanmayi modelin "bilmiyorum" demesinin yapisal araci yapar.

### Test toplam

612 test (onceki 589 + 23 cikti disiplini).

### install.sh

`test_manifest_file_count`: 51 → 52 (+1 test dosyasi).

---

## [2.14.0] - 2026-05-13

### Added — Citation Source Whitelist Tier 2C (FEATURE_IDEAS #21, ADR-0015)

Hukuki citation icin **resmi kaynak domain whitelist** zorunlulugu. ADR-0013 (Tier 1 Barnum + Tier 2A madde_dogrula + Tier 2B CoVe) uzerine dorduncu savunma katmani.

- **agents/ragip-hukuk.md**: "TIER 2C — KAYNAK DOMAIN WHITELIST" bolumu eklendi. 8 resmi domain (mevzuat.gov.tr, resmigazete.gov.tr, yargitay.gov.tr, karararama.yargitay.gov.tr, danistay.gov.tr, anayasa.gov.tr, adalet.gov.tr, hsk.gov.tr) listelendi.
- **skills/ragip-degerlendirme/SKILL.md**:
  - `allowed-tools` icine `WebFetch` eklendi (whitelist domaininde teyit icin).
  - Adim 3 guncellendi: `site:mevzuat.gov.tr` filtreli arama, whitelist disi sonuclar reddedilir, "Resmi kaynaktan teyit edilemedi" notu zorunlu.
- **tests/test_ragip_kaynak_whitelist.py**: 13 test — whitelist tutarliligi (agent vs skill), WebFetch eklenmis, ADR-0015 referansi, diger hukuk skill'lerinde WebSearch yok kontrolu.
- **docs/adr/0015-citation-source-whitelist.md**: Kaynak otoritesi zorunlulugu, alternatif yaklasimlar (settings.json kit-level reddedildi cunku ragip-dis-veri'yi etkiler), prompt-level enforcement sinirlari.

### Why

ADR-0013 sonrasi acik kalan bosluk: madde_dogrula sadece kanun maddesi pattern'ini yakalar, "Yargıtay 11. HD 2024/X karar" gibi mahkeme karari ve doktrin alintilarini kapsamiyordu. Model gerçek-gibi-gözüken-uydurma-karar üretebilir. Tier 2C kaynak otoritesini prompt-level zorunluluga baglar.

gibibyte-cfo-agent v0.2 (Nisan 2026) settings.json WebFetch whitelist pattern'inden ilham — vergi domain'inde uygulanan disiplin hukuki citation'a tasındı.

### Test toplam

589 test (onceki 576 + 13 whitelist).

### install.sh

`test_manifest_file_count`: 50 → 51 (+1 test dosyasi).

---

## [2.13.0] - 2026-05-13

### Added — Prompt Caching (FEATURE_IDEAS I10, ADR-0014)

CLI mode'da (`scripts/ragip_aga.py call_llm()`) Anthropic provider icin `cache_control: {"type": "ephemeral"}` eklendi. Tekrar eden CLI cagrilarinda system prompt 5dk cache'lenir, input token maliyeti ~%90 duser.

- **scripts/ragip_aga.py**: `_build_messages()` saf yardimci fonksiyon. Model prefix'ine (`anthropic/...` veya `claude-...`) gore Anthropic ise structured content + cache_control, degilse standart string content (geriye uyumlu).
- **tests/test_ragip_prompt_caching.py**: 9 yeni test — Anthropic prefix'leri, OpenAI/Gemini/Ollama (cache yok), multiline/empty system prompt, user prompt korunmasi.
- **docs/adr/0014-prompt-caching-policy.md**: Iki katmanli politika dokumante edildi:
  - Claude Code orchestration: otomatik (kit dokunmaz)
  - CLI mode litellm: explicit cache_control (kit kontrol eder)

### Why

Kit v2.7.x'ten beri `call_llm()` litellm uzerinden Anthropic'e direkt cagri yapiyor ama cache_control eksikti. Agent system prompt'lari ~5k token (`agents/ragip-aga.md` 357 satir) — repeat CLI calistirmalarinda yeniden tokenize ediliyordu. Bu kayip kapatildi.

### Test toplam

576 test (onceki 567 + 9 prompt caching).

### install.sh

`test_manifest_file_count`: 49 → 50 (+1 test dosyasi).

---

## [2.12.1] - 2026-05-12

### Added — ragip-analiz PII Backport (workspace → kit)

Workspace'te 1 Nisan 2026'da eklenen `ragip-analiz` PII maskeleme entegrasyonu kit'e geri tasindi. v2.11.0'da eklenen altyapi (`ragip_pii.py`, `validate_sozlesme`) ilk kez SKILL.md seviyesinde gercek kullaniliyor.

- **skills/ragip-analiz/SKILL.md**: Iki yeni adim eklendi:
  - **1b. Sozlesme ise PII maskeleme**: Analiz oncesi `ragip_pii.maskele_geri_donusturulabilir()` ile firma/kisi/email/telefon/TCKN/IBAN/tutar/tarih/adres maskele; mapping `.mapping.json`'a; maskelenmis metin `.masked.md`'ye. Analiz bitince `geri_cevir()` ile placeholder'lari original'a cevir.
  - **1c. Sozlesme metadata**: `sozlesmeler.jsonl`'e kayit ekle (`validate_sozlesme()` semasi: tur/durum/tarih/taraflar/dosya/masked_dosya/mapping).

### Why

Kit v2.11.0'de eklenen sozlesme altyapisi (ragip_pii + validate_sozlesme) **hicbir skill tarafindan kullanilmiyordu** — workspace altyapiyi gercek kullaniyordu. Backport ile pattern kit'in resmi parcasi oldu. Bundan sonra `bash install.sh` ile kurulan her workspace bu pattern'i alir.

---

## [2.12.0] - 2026-05-12

### Added — Citation Validation + CoVe (FEATURE_IDEAS #19, ADR-0013)

Tier 2 savunma katmani: ragip-degerlendirme, ragip-analiz, ragip-strateji ciktilarinda sahte yasal madde citation halusinasyonunu yakalar. Tier 1 (Barnum filtresi prompt-tabanli) ustune deterministik kontrol.

- **config/kanun_maddeleri.json**: 5 mevzuat (TBK, TTK, IIK, KVKK, HMK) + 25 madde manuel curated. SKILL.md'lerden cikartilan tum referanslari kapsar. Genisletilebilir (kullanici manuel ekler).
- **scripts/ragip_madde_dogrula.py**: Regex extractor + validator. Yakaladiklari: tek madde (`TBK m.117`), fikra (`TTK m.21/2`), fikra+bent (`TTK m.23/1-c`), range (`TBK m.117-120` → 4 madde), Turkce karakter (`İİK` → `IIK` normalize). LLM-bagimsiz, ragip_get_rates.sh tarzi standalone.
- **scripts/ragip_madde_dogrula.sh**: Bash wrapper — skill'lerden kolay cagri.
- **tests/test_ragip_madde_dogrula.py**: 34 yeni test — kanun veri butunlugu, normalize, referans cikarma, dogrulama, CLI (exit kodu, stdin, JSON format), bash wrapper, portability.
- **docs/adr/0013-chain-of-verification.md**: CoVe pattern + Tier 2 mimari karar. Defense-in-depth: Tier 1 Barnum + Tier 2A madde_dogrula deterministik + Tier 2B CoVe yapisal.
- **skills/ragip-degerlendirme/SKILL.md**: 4-fazli CoVe akisi (DRAFT → VERIFICATION SORULARI → FRESH-LOOK CEVAP → SENTEZ + dogrulama). Adim 9 zorunlu madde dogrulama.
- **skills/ragip-analiz/SKILL.md**: Adim 8 — madde referansi varsa zorunlu dogrulama.
- **skills/ragip-strateji/SKILL.md**: Adim 3 — yasal yola atifsa zorunlu dogrulama.

### Changed

- **install.sh**: Script count 8 → 10 (+ragip_madde_dogrula.py, +ragip_madde_dogrula.sh). Config count 1 → 2 (+kanun_maddeleri.json). Manifest builder genisletildi.
- **tests/test_ragip_install.py**: `test_manifest_file_count` 45 → 49 (+1 test + 2 script + 1 config).
- **README.md**: Script 8→10, Config 1→2, Test 12→13. Yeni test katmani (13. Madde dogrulama) eklendi.
- **CLAUDE.md**: Test komut listesine `test_ragip_madde_dogrula.py` eklendi.
- **docs/FEATURE_IDEAS.md**: #19 "Aktif" → "Tamamlanan (12)".

### Test toplam

567 test (onceki 533 + 34 madde_dogrula).

---

## [2.11.0] - 2026-03-27

### Added — Sozlesme Yonetimi Altyapisi

- **scripts/ragip_pii.py**: Geri donusturulabilir maskeleme — `maskele_geri_donusturulabilir(metin, firma_adlari, kisi_adlari)` ve `geri_cevir(metin, mapping)`. Sozlesme analizi oncesi PII korumasi: firma, kisi, email, telefon, TCKN, IBAN, tutar, tarih, adres placeholder'lari. Mapping dict ile orijinal degerlere geri donus.
- **scripts/ragip_crud.py**: `validate_sozlesme()` — sozlesmeler.jsonl sema dogrulamasi. Turler: gizlilik/hizmet/tedarik/distributorluk/diger. Durumlar: taslak/inceleme/imzali/aktif/suresi_doldu/iptal.
- **tests/test_ragip_pii.py**: 21 yeni test — geri donusturulabilir maskeleme (firma, kisi, email, tutar, tarih, karisik metin, tam dongu).
- **tests/test_ragip_crud.py**: 13 yeni test — sozlesme validasyonu (zorunlu alanlar, tur/durum enum, tarih format, taraflar).
- Toplam test: ~499 → ~533

---

## [2.10.0] - 2026-03-27

### Added — Zamanlanmis Gorevler (ADR-0012)

- **scripts/ragip_cron.sh**: Cron wrapper script — `run rates`, `run temizle`, `--setup`, `--status`, `--remove`, `--list`. Cron ortaminda PATH/venv/.env izolasyonu, gunluk log rotasyonu (`data/RAGIP_AGA/logs/cron_YYYYMMDD.log`).
- **tests/test_ragip_cron.py**: 34 test — script saglik, run komutlari, loglama, .env yukleme, venv tespit, crontab setup/remove/status/idempotency.
- **docs/adr/0012-zamanlanmis-gorevler.md**: Mimari karar kaydi — WSL2 crontab tercih gerekceleri.
- **install.sh**: ragip_cron.sh kopyalama + manifest eklendi (toplam 41 dosya).
- Toplam test: ~465 → ~499

---

## [2.9.0] - 2026-03-23

### Added — Savunma Katmanlari (ADR-0010)

gibibyte-agent'ta (v0.9.0) kanitlanmis 4 muhendislik pattern'i kit'e tasinarak jenerik altyapi guclendirmesi yapildi.

- **scripts/ragip_errors.py**: Yapilandirilmis hata siniflandirmasi — HataTuru (GECICI/KALICI/POLITIKA), RagipHata exception sinifi, siniflandir() ve tekrar_denenebilir() helper'lari
- **scripts/ragip_pii.py**: PII temizleyici — email/telefon/TCKN/IBAN regex maskeleme + firma/musteri alan hash'leme (SHA-256). MSP multi-tenant senaryolari icin
- **scripts/ragip_output.py**: Idempotency — _parmak_izi() SHA-256 fingerprint + 24h dedup penceresi. kaydet() fonksiyonuna dedup=True ve pii_temizle=False parametreleri eklendi
- **scripts/ragip_rates.py**: TCMB Protocol pattern — OranSaglayici Protocol, StubSaglayici (test), EVDSSaglayici (production), saglayici_olustur() factory
- **docs/adr/0010-savunma-katmanlari.md**: Mimari karar kaydi
- **docs/FEATURE_IDEAS.md**: I9 — Prompt caching izleme maddesi eklendi
- Toplam test: 386 → ~443, Script: 5 → 7

---

## [2.8.16] - 2026-03-22

### Added — Kur Farki Hesaplama

- **scripts/ragip_aga.py**: `kur_farki_hesapla()` — dovizli faturalarin kur farki analizi. Formul: (odeme_kuru - fatura_kuru) × tutar. Kayip/kazanc ayirimi, firma filtresi, eksik kur uyarisi.
- **tests/test_ragip_integration.py**: 9 yeni kur farki testi (kayip, kazanc, TRY atlama, eksik kur, iptal, karisik, firma filtre, D365 veri)
- **docs/FEATURE_IDEAS.md**: M13 guncelleme — kur farki metodu ve MCP standardizasyonu belgelendi
- Toplam test: 377 → 386, Hesaplama metodu: 23 → 24

---

## [2.8.15] - 2026-03-22

### Changed — ADR-0007 Doviz Kuru Semasi

- **docs/adr/0007-standart-fatura-semasi.md**: `fatura_kuru` ve `odeme_kuru` alanlari eklendi, `doviz` → `para_birimi` standardizasyonu belgelendi, kur farki hesaplama formulu ve MCP/DTO esleme tablosu eklendi
- **scripts/ragip_crud.py**: `validate_fatura()` — fatura_kuru/odeme_kuru pozitiflik ve tip kontrolu eklendi
- **tests/test_ragip_integration.py**: Test verisi `doviz` → `para_birimi` standardize edildi, `TRL` → `TRY` (ISO 4217), 7 yeni doviz kuru testi
- **tests/test_ragip_crud.py**: 8 yeni fatura_kuru/odeme_kuru validasyon testi
- **.claude/rules/data-schema.md**: Doviz kuru alanlari ve MCP esleme kurali eklendi
- Toplam test: 364 → 377

---

## [2.8.14] - 2026-03-22

### Changed — ragip_output Entegrasyonu + Sentez Kaydetme

- **agents/ragip-hesap.md, ragip-arastirma.md, ragip-hukuk.md, ragip-veri.md**: Inline bash+Python cikti kaydetme kodu kaldirildi, `ragip_output.kaydet()` ile degistirildi — frontmatter, manifest, firma klasoru otomatik
- **agents/ragip-aga.md**: Sentez ciktisini kaydetme kurali eklendi — orchestrator interaktif modda is yaptiginda da cikti kayit altina aliniyor (agent='aga', skill='sentez')
- **tests/test_ragip_subagents.py**: 2 yeni test — sub-agent'larin ragip_output kullanimini ve orchestrator sentez kaydetme kuralini dogruluyor
- **docs/PROJE_GENEL_BAKIS.md**: v2.8.14, 364 test, 23 metot, ragip_output.py dosya yapisina eklendi
- Toplam test: 362 → 364

---

## [2.8.13] - 2026-03-21

### Added — Nakit Projeksiyon + Cikti Altyapisi (Faz 5)

- **scripts/ragip_aga.py**: `nakit_projeksiyon()` — 30/60/90 gun forward nakit akis projeksiyonu, haftalik kirilim, vadesi gecmis alacak
- **scripts/ragip_aga.py**: `odeme_trend_analizi()` — firma bazli gecikme trendi (iyilesme/kotulesme tespiti)
- **scripts/ragip_output.py**: Merkezi cikti yonetimi — firma bazli klasor, YAML frontmatter, manifest.jsonl, slug donusumu
- **skills/ragip-rapor**: `projeksiyon` ve `trend` rapor turleri eklendi
- **tests/test_ragip_output.py**: 19 test (slug, frontmatter, kaydet, manifest sorgu)
- **tests/test_ragip_integration.py**: 11 yeni test (nakit projeksiyon + odeme trend)
- Toplam test: 327 → 357

### Changed — Agent Dispatch Iyilestirmesi (Faz 5 E2E bulgulari)

- **agents/ragip-aga.md**: Dispatch zorunlulugu guclendirildi — "kendin YAPMA" + neden aciklamasi + "tam analiz" anahtar kelimesi
- **agents/ragip-aga.md**: Firma degerlendirme akisi 5 adima cikti — Adim 3'te kullaniciya "arastirma/hukuk ister misin?" sorusu
- **agents/ragip-aga.md**: Onceki cikti referansi ZORUNLU — sub-agent dispatch prompt'una dosya yolu eklenmeli
- **agents/ragip-arastirma.md, ragip-hesap.md, ragip-hukuk.md**: "Once analiz et, SONRA kaydet" siralama kurali eklendi

---

## [2.8.12] - 2026-03-20

### Fixed — DTO Uyumluluk (ragip-workspace)

- **scripts/ragip_aga.py**: `musteri_konsantrasyonu()` metodu `tek_firma_raporu=False` parametresi aldi — D365 DTO uyumlulugu (tek firma raporlarinda konsantrasyon bilgisi)
- **tests/test_ragip_fatura_analiz.py**: 3 yeni test (tek_firma_raporu True/False/bos veri)
- Toplam test: 297 → 300
- **ragip-workspace'teki 26 DTO test fail'i bu degisiklikle cozulur**

---

## [2.8.11] - 2026-03-20

### Fixed — MCP Entegrasyon Hazirlik (Ongorulen Patlama Noktalari)

- **scripts/ragip_aga.py**: `firma_id` karsilastirmasi `str()` ile tip-guvenli yapildi — int/str/GUID hepsi calisiyor (7 metot)
- **scripts/ragip_aga.py**: `_para_birimi_uyarisi()` helper — farkli para birimleri karisik toplaninca uyari
- **scripts/ragip_aga.py**: `ccc_dashboard` sonucuna `para_birimi_uyarisi` alani eklendi
- **scripts/ragip_crud.py**: `validate_fatura()` firma_id tip kontrolu eklendi (int veya str kabul, diger tipler hata)
- **tests/test_ragip_crud.py**: 3 yeni test (firma_id int/str/gecersiz tip)
- **tests/test_ragip_fatura_analiz.py**: 4 yeni test (firma_id string filtre, int/str eslesme, para birimi uyari var/yok)
- Toplam test: 290 → 297

---

## [2.8.10] - 2026-03-20

### Changed — .claude/ Best Practice Refactoring

- **`.claude/settings.json`**: Paylasilan izinler ayrildi (settings.local.json kisisel kaldi, gitignore'a alindi)
- **`.claude/rules/commit-checklist.md`**: CLAUDE.md'den commit/release kontrol listesi tasindi (always-loaded rule)
- **`.claude/rules/conventions.md`**: CLAUDE.md'den genel konvansiyonlar tasindi (always-loaded rule)
- **`CLAUDE.md`**: Tasnan bolumler yerine rules referanslari, 101 → 84 satir

---

## [2.8.9] - 2026-03-19

### Added — Data Quality Contract (ADR-0007 Validasyon)

- **scripts/ragip_crud.py**: `validate_fatura()` ve `validate_faturalar()` — ADR-0007 sema dogrulamasi. Zorunlu alan, tip, enum, tarih formati, kismi odeme tutarliligi kontrolleri.
- **skills/ragip-rapor/SKILL.md**: Rapor uretmeden once sema validasyonu. Hatali kayitlar uyari ile atlanir, gecerli kayitlarla devam eder.
- **tests/test_ragip_crud.py**: 21 yeni test (TestValidateFatura 17 + TestValidateFaturalar 4). Toplam test: 269 → 290.

### Added — Orchestrator Dispatch Uyarisi

- **agents/ragip-aga.md**: BILINEN SINIRLAR bolumu eklendi — Senaryo A (dedicated session) dispatch sinirlamasi, Senaryo B (ana session) onerilir.
- **agents/ragip-aga.md**: maxTurns 12 → 16. FIRMA DEGERLENDIRME AKISI + TURN LIMITI bolumleri eklendi.

### Changed — ADR-0004 Guncelleme

- **docs/adr/0004-kit-mcp-ayrimi.md**: "MCP = veri" → "MCP = veri + ERP-aware normalizasyon". DTO katmani, validate_fatura rolleri netlesti.

### Added — MCP Entegrasyon Rehberi

- **docs/MCP_ENTEGRASYON_REHBERI.md**: Yeni ERP/CRM MCP adaptoru yazma rehberi. MCP server, DTO normalizasyonu, validasyon, yapilandirma adimlari.

## [2.8.8] - 2026-03-19

### Fixed — Orchestrator Dispatch: Task tool → Agent tool

- **agents/ragip-aga.md**: "Task tool" → "Agent tool" (8 occurrence) — araç adı ilk committe yanlış yazılmıştı, hiç test edilmemişti
- **agents/ragip-aga.md**: subagent_type invocation formatı düzeltildi — `subagent_type: "ragip-X", prompt: [görev]`
- **tests/e2e_ragip_scenario/SENARYO_VE_TEST_REHBERI.md**: "Task tool" → "Agent tool"

### Added — Hybrid Orchestrator + Dispatch Rules

- **config/ragip_dispatch.md**: Hedef repoya kurulan routing dosyası (YENİ) — Senaryo B (ana session direkt dispatch) için
- **install.sh**: `.claude/rules/ragip_dispatch.md` kurulumu eklendi
- **.claude/rules/architecture.md**: "Dispatch Kuralları" bölümü eklendi — routing tablosu + Senaryo A/B açıklaması
- **docs/adr/0009-hybrid-orchestrator.md**: Nested spawn bulgusu, Senaryo A/B kararı dokümante edildi
- **tests/test_ragip_subagents.py**: `TestOrchestratorDispatch` — 5 yeni test:
  - `test_no_task_tool_in_orchestrator`: "Task tool" kalmadığını doğrula
  - `test_agent_tool_dispatch_in_orchestrator`: "Agent tool" varlığını doğrula
  - `test_subagent_type_format_in_orchestrator`: Her sub-agent için subagent_type formatını doğrula
  - `test_dispatch_file_exists`: config/ragip_dispatch.md varlığını doğrula
  - `test_dispatch_file_has_routing_table`: Routing tablosu içeriğini doğrula
- Toplam test: 264 → 269

---

## [2.8.7] - 2026-03-19

### Added — Test Coverage: ragip_temizle.sh

- **tests/test_ragip_temizle.py**: ragip_temizle.sh icin 20 fonksiyonel test eklendi
  - TestScriptSaglik: varlik + calistirilabilir + graceful exit
  - TestYasBazliTemizlik: 91 gun+ silme, sinir (89 gun) koruma, coklu silme
  - TestLimitBazliTemizlik: 200 siniri, en eski silme, mesaj dogrulamasi
  - TestDryRun: silme yok, mesaj var, bos dizin
  - TestDosyaFiltresi: sadece .md, alt dizin korunur
  - TestCiktiMesaji: "Tamamlandi. Kalan:" her zaman var
- Manifest sayisi 32 → 33 (7 test dosyasi)
- Toplam test: 244 → 264

---

## [2.8.6] - 2026-03-19

### Added — Graceful Degradation + ciktilar Retention

- **4 sub-agent (hesap, arastirma, veri, hukuk)**: Kismi sonuc talimati eklendi — maxTurns limitinde sessiz kesim yerine elindeki sonuclari ozetleyip eksikleri bildir (FEATURE_IDEAS #16)
- **ragip-aga sentezleme**: Eksik/basarisiz alt-ajan yaniti icin partial failure bildirimi kurali
- **scripts/ragip_temizle.sh**: ciktilar/ bakim scripti — 90 gun / 200 dosya limiti, --dry-run destegi
- **ragip-aga CIKTI YONETIMI**: 200 dosya uyarisi + temizleme komutu referansi
- Test: 4 sub-agent class'ina `test_graceful_degradation` eklendi (240 → 244 test)

---

## [2.8.5] - 2026-03-18

### Security — Principle of Least Privilege

- **ragip-aga, ragip-hesap, ragip-veri**: `disallowedTools: [WebSearch, WebFetch]` frontmatter ile WebSearch/WebFetch mimari seviyede engellendi
- Prompt-level kısıtlama → runtime enforcement: araç görünmez, atlanamaz
- ragip-arastirma ve ragip-hukuk: skill-level farklılık nedeniyle prompt kısıtlaması devam eder (dis-veri ve degerlendirme skill'leri WebSearch kullanır)
- Test: `TestOrchestrator.test_no_websearch`, `TestSubAgentHesap.test_no_websearch`, `TestSubAgentVeri.test_no_websearch`

---

## [2.8.4] - 2026-03-01

### Added — Cikti Kesfedilebilirligi (Backlog #7)

- **ragip-ozet (tam ozet)**: SON CIKTILAR bolumu eklendi — `data/RAGIP_AGA/ciktilar/` dizinindeki son 10 ciktiyi tarih, agent/skill, konu olarak listeler
- **ragip-ozet (firma detay)**: FIRMA CIKTILARI bolumu eklendi — firma adina gore filtrelenmis son 5 cikti
- **ragip-ozet**: HIZLI KOMUTLAR'a ciktilar dizin listelemesi eklendi

---

## [2.8.3] - 2026-03-01

### Changed — DRY Refactor + AI Disclaimer (Backlog #5, #6)

- **ragip-vade-farki**: Inline hesaplamalar `FinansalHesap.vade_farki()`, `.tvm_gunluk_maliyet()`, `.erken_odeme_iskonto()` cagrilariyla degistirildi — ragip-rapor ile tutarli pattern (#5)
- **ragip-analiz**: Risk skoru ciktisina inline AI disclaimer eklendi — `(AI tahmini — hukuki degerlendirme degildir)` (#6)
- **ragip-degerlendirme**: TARAFIMIZIN / KARSI TARAFIN POZISYONU verdiktlerine inline AI disclaimer eklendi (#6)

---

## [2.8.2] - 2026-03-01

### Fixed — Prompt & Rate Warning Fixes (Backlog #1, #2, #4)

- **ragip-analiz**: WebSearch oran aramasi kaldirildi — `ragip_get_rates.sh` ile degistirildi, `allowed-tools`'dan WebSearch cikarildi (#1)
- **ragip-strateji**: Cift oran cekme (WebSearch + Bash) kaldirildi — sadece Bash blogu kaldi, `allowed-tools`'dan WebSearch cikarildi (#1)
- **ragip-degerlendirme**: Oran ve mevzuat adimi ayrildi — oranlar icin `ragip_get_rates.sh`, mevzuat guncellemeleri icin WebSearch (mesru kullanim) (#1)
- **ragip-vade-farki**: Fallback uyarisi (`rates.uyari`) skill ciktisinda gosteriliyor (#4)
- **ragip-arbitraj**: 4 Bash blogunun (CIP, ucgen, vade-mevduat, carry trade) hepsinde fallback uyarisi gosteriliyor (#4)
- **ragip-aga**: Orchestrator dispatch'ine arastirma vs hukuk belirsiz durumlar icin acik yonlendirme eklendi (#2)

---

## [2.8.1] - 2026-03-01

### Added — Nakit Cevrim Dongusu Dashboard (Backlog #10)

- **FinansalHesap.ccc_dashboard()**: Birlesik nakit cevrim dongusu raporu — mevcut DSO, DPO, tahsilat_orani, aging_raporu metotlarini orkestre eder
  - CCC = DSO - DPO (DIO haric — stok verisi yok)
  - Yorum: uzun (>60g), orta (>30g), kisa (<=30g), negatif (tedarikci finansmani)
  - `donem_gun`, `bugun`, `firma_id` parametreleri
- **ragip-rapor**: `ccc` rapor turu eklendi (`hepsi` modunda da calisir)
- 5 yeni test: `TestCccDashboard` sinifi (237 test toplam)

---

## [2.8.0] - 2026-02-28

### Added — Fatura Uyari Sistemi (Backlog #9)

- **FinansalHesap.fatura_uyarilari()**: Proaktif fatura uyari metodu — 3 kategori:
  - **Vade gecmis**: Vadesi gecmis acik alacak faturalari (gecikme gunu + kalan tutar)
  - **Yaklasan vade**: 7 gun icinde vadesi dolacak alacak faturalari
  - **TTK m.21/2 itiraz suresi**: Alinan (borc) faturalarda 8 gunluk itiraz suresi dolmak uzere (<=3 gun kala uyari)
- `bugun` + `firma_id` parametreleri (testability + firma filtresi)
- **ragip-ozet**: Dashboard'a fatura uyari bolumu eklendi — vade gecmis, yaklasan, TTK itiraz ozeti
- 7 yeni test: `TestFaturaUyarilari` sinifi (232 test toplam)

---

## [2.7.2] - 2026-02-28

### Added — Firma Bazli Rapor Filtresi (Backlog #8)

- **FinansalHesap**: 6 analiz metodu `firma_id=None` parametresi aldi — aging, DSO, DPO, tahsilat, gelir trendi, KDV donem ozeti
- None ise mevcut davranis (tum faturalar), deger verilirse sadece o firmanin faturalari islenir
- Dondurulen dict'e `firma_id` anahtari eklendi ("tumu" veya verilen id)
- `musteri_konsantrasyonu` haric — firma bazinda gruplama yapiyor, tek firmaya filtrelemek anlamsiz
- **ragip-rapor**: `firma_id=` parametresi eklendi (argument-hint + Bash blogu)
- 6 yeni test: her metot icin `test_firma_id_filtresi` (225 test toplam)

---

## [2.7.1] - 2026-02-28

### Fixed — Kit-wide Critique Duzeltmeleri

- **ragip-arastirma, ragip-hukuk**: WebSearch ile oran arama kaldirdi — `ragip_get_rates.sh` kullanacak sekilde guncellendi (paralel calistirmada tutarsiz oran riski giderildi)
- **ragip-aga**: Orchestrator dispatch'ine arastirma vs hukuk yonlendirme notlari eklendi (kullanici talebinin dogru agent'a gitmesi icin)
- **ragip-dis-veri**: "veri topla" ifadesi "on arastirma" olarak guncellendi, WebSearch sinirlilik notu eklendi (beklenti yonetimi)
- **ragip_rates.py**: Fallback oranlarinda `guncelleme` alaninin simdiki zamanla uzerine yazilmasi kaldirildi — >7 gun eskiyse yaslanma uyarisi eklendi (`FALLBACK_DATE` sabiti)

### Added

- 2 yeni test: fallback yaslanma uyarisi tespiti (219 test toplam)

### Changed

- **FEATURE_IDEAS.md**: Kit-wide critique sonuclariyla yeniden yapilandirildi — 15 aktif fikir, 5 reddedilen (gerekceyle), 5 izleme maddesi

---

## [2.7.0] - 2026-02-26

### Added — ragip-rapor Skill

- **ragip-rapor** (ragip-hesap): 7 fatura analiz raporu tek skill'de — aging, DSO, DPO, tahsilat orani, gelir trendi, musteri konsantrasyonu, KDV donem ozeti
- `hepsi` modu: 7 raporu sirayla calistirir
- `disable-model-invocation: true` — deterministik, FinansalHesap motorunu dogrudan cagirir

### Fixed

- **ragip-ihtar**: `disable-model-invocation: true` kaldirildi (LLM gerekli — template placeholder'lari doldurulmasi lazim), cikti kaydetme blogu eklendi
- **ragip-import**: Import edilen firma kartlarina `tip: diger` varsayilan alani eklendi (firmalar.jsonl semasina uyum)

### Changed

- **ragip-hesap**: Skills listesine ragip-rapor eklendi, GOREVIN bolumunerakam analiz satirlari eklendi
- **ragip-aga**: Dispatch tablosuna rapor trigger'lari eklendi (aging, DSO, tahsilat vb.)
- **architecture.md**: ragip-hesap skill listesi + LLM skill listesine ihtar eklendi
- Mimari: 14 skill -> 15 skill

---

## [2.6.0] - 2026-02-25

### Added — ragip-hukuk Sub-Agent

- **ragip-hukuk** (sonnet): Yeni hukuk danismanligi sub-agent'i
- **ragip-degerlendirme**: Hukuki haklilik degerlendirmesi (GUCLU/ORTA/ZAYIF verdikt, madde bazli analiz)
- **ragip-zamanasimi**: Yasal sure ve zamanasimi hesaplayici (fatura itirazi, sozlesme, icra, KVKK)
- **ragip-delil**: Delil stratejisi ve avukata dosya hazirligi (delil gucu puanlama, KEP/noter rehberi)

### Changed

- **ragip-ihtar**: ragip-arastirma'dan ragip-hukuk'a tasindi (icerik degisikligi yok)
- **ragip-arastirma**: Skill listesi guncellendi (ihtar cikarildi)
- **ragip-aga**: Orchestrator dispatch tablosuna ragip-hukuk eklendi
- Mimari: 3 sub-agent -> 4 sub-agent

---

## [2.5.2] - 2026-02-24

### Changed — Doküman Yapısı Yenileme

- **`.claude/rules/`**: Kural dosyaları oluşturuldu (architecture, portability, update-mechanism, data-schema)
- **`docs/adr/`**: ADR kayıtları oluşturuldu (sub-agent mimarisi, version-manifest, kit-hash fix, kit-mcp ayrımı, DRY helpers)
- **`CLAUDE.md`**: Yalınlaştırıldı — hardcoded sayılar kaldırıldı, rules/ADR referansları eklendi
- **`MEMORY.md`**: Tarihsel bilgi ADR'lere taşındı, sadece index kaldı

### Prensip

- Sayı yazma, kaynak göster (`cat VERSION`, `pytest tests/ -v`)
- Kural = zamansız (`.claude/rules/`), karar = tarihli + bağlamlı (`docs/adr/`)

---

## [2.5.1] - 2026-02-24

### Fixed — Manifest Hash Bug (Kritik)

- **`update.sh`**: Manifest'e kullanıcı hash'i yerine **kit hash'i** yazılıyor
  - Eski davranış: Kullanıcı bir skill'i özelleştirince ilk update koruyor ama ikinci update sessizce üzerine yazıyordu
  - Yeni davranış: Kullanıcı değişiklikleri **tüm ardışık update'lerde** korunur
  - Sebep: 3 ayrı manifest yazma döngüsü → tek döngü, her zaman `kit_files[rel_path]["new_hash"]`

### Added — Update Güvenlik Testleri

- **`test_user_change_preserved_across_updates`**: Ardışık 2 update'de kullanıcı değişikliği korunuyor mu
- **`test_manifest_stores_kit_hash_not_user_hash`**: Manifest'te kit hash'i saklandığını doğrular
- **`test_conflict_backup_content`**: Çakışma yedek dosyasının kullanıcı içeriğini taşıdığını doğrular

---

## [2.5.0] - 2026-02-23

### Fixed — Bare Placeholder Bug (P0)

- **ragip-vade-farki**: `anapara = ANAPARA` (NameError) → `float(os.environ['ANAPARA_VAL'])` env var pattern
- **ragip-strateji**: `tutar = TUTAR` (NameError) → `float(os.environ['TUTAR_VAL'])` env var pattern
- Her iki skill'de hata durumunda net Türkçe mesaj ve örnek kullanım gösterilir

### Added — DRY Refactoring

- **`scripts/ragip_get_rates.sh`**: TCMB oran çekme tek kaynak helper (fallback zinciri: canlı API → cache → FALLBACK_RATES)
- **`scripts/ragip_crud.py`**: CRUD skill'leri için paylaşımlı yardımcı modül (get_root, load/save jsonl/json, parse_kv, atomic_write, next_id)
- 3 oran skill'inde (vade-farki, strateji, arbitraj) tekrarlanan 6 fetch+fallback bloğu → 1 helper + tek satır çağrı
- 3 CRUD skill'inde (firma, gorev, profil) ~60% boilerplate azaltma → ragip_crud.py import

### Added — Test Coverage

- **`TestBashBlocks`**: Skill bash bloklarının yapısal doğrulaması
  - Python sözdizimi kontrolü, bare placeholder tespiti, env var eşleştirme
  - Helper kullanım kontrolü (get_rates.sh, ragip_crud.py)
  - Bash değişken tırnaklama kontrolü
- **`test_ragip_install.py`**: install.sh ve update.sh otomatik testleri
  - Fresh install: dosya varlığı, manifest yapısı, checksum doğrulama, gitignore
  - Update: aynı versiyon reddi, --force, kullanıcı değişikliği koruma, silinen dosya geri yükleme, --dry-run
- **`test_ragip_crud.py`**: ragip_crud.py unit testleri
  - parse_kv, load/save jsonl/json, atomic write, next_id, today

### Added — Firma Tip Alanı

- **`ragip-firma`**: Firma kartlarına `tip` alanı eklendi (`tedarikci` | `musteri` | `distributor` | `diger`)
- Nakit akışı yönetiminde tedarikçiye "geç öde" vs müşteriye "erken tahsil et" ayrımı artık yapılabilir
- `listele`: Firmalar tipe göre gruplanarak gösterilir (TDR/MUS/DST/DGR etiketleri)
- `ekle`/`guncelle`: `tip=tedarikci` parametresi ile tip atanır, validasyonlu
- `ara`: Tip alanında da arama yapılır
- Geriye uyumlu: mevcut kayıtlar `diger` varsayılanıyla çalışır

### Changed

- `install.sh`: ragip_get_rates.sh + ragip_crud.py kopyalama ve manifest'e ekleme
- `update.sh`: Yeni script dosyalarını tanıma desteği

---

## [2.4.0] - 2026-02-23

### Added — Versiyon Takibi ve Güncelleme Mekanizması

**Kit artık kurulumları takip edebiliyor ve güvenli güncelleme yapabiliyor.**

- **`VERSION` dosyası**: Kit kökünde tek kaynak versiyon bilgisi (semver)
- **`update.sh`**: Manifest-tabanlı güvenli güncelleme scripti
  - Üçlü checksum karşılaştırma (kurulum vs manifest vs yeni kit)
  - Kullanıcı değişiklikleri otomatik korunur
  - Çakışmalarda `.kullanici-yedek-YYYYMMDD` yedek oluşturur
  - `--dry-run`, `--force`, `--source PATH` flagleri
- **Kurulum manifesti**: `config/.ragip_manifest.json` — core dosyaların SHA-256 checksum'ları
- **Mevcut kurulum tespiti**: `install.sh` artık mevcut kurulumu algılayıp `update.sh` önerir

### Changed

- `install.sh`: Versiyon okuma, manifest oluşturma, mevcut kurulum kontrolü eklendi
- `config/ragip_aga.yaml`: Eski `version: "1.0.0"` → `"2.4.0"` olarak senkronize edildi

### Tests

- `TestVersionManifest`: VERSION semver, changelog uyumu, config uyumu, manifest yapısı, manifest dosya varlığı

---

## [2.3.0] - 2026-02-22

### Changed — Standalone Taşınabilir Modül

**`ragip_rates.py` artık tek dosya, sıfır bağımlılık, herhangi bir repoya kopyala-yapıştır ile taşınabilir.**

- **Cache path'leri taşınabilir**: `ROOT = Path(__file__).parent.parent` kaldırıldı → `RAGIP_CACHE_DIR` env var (varsayılan: `scripts/.ragip_cache/`)
- **`.env` parser kaldırıldı**: `get_env_key()` fonksiyonu silindi → `os.environ.get()` ile değiştirildi. Çağıran uygulama kendi `.env`'ini yükler.
- **`__all__` export listesi** eklendi — API yüzeyini netleştir
- **Portability docstring** eklendi — 4 adımda taşıma talimatı

### Fixed — Tutarsız Fallback Değerler

- `ragip_aga.py`: Kendi fallback dict'i (42.5, 52.0) kaldırıldı → `ragip_rates.FALLBACK_RATES` import edildi
- `ragip_aga.py`: 8 adet inline `.get("key", HARDCODED)` çağrısı → `_FB["key"]` referanslarıyla değiştirildi
- 3 skill dosyası (arbitraj, vade-farki, strateji): Hardcoded fallback sabitleri kaldırıldı → `ragip_rates.py` JSON çıktısından alınıyor

### Security

- Git geçmişinden 5 yanlışlıkla commit edilmiş dosya tamamen silindi (`git-filter-repo`)
- `.gitignore`'a eklendi: `data/NOTES/`, `scripts/.ragip_cache/`

### Docs

- `RAGIP_AGA.md` v2.3.0: Standalone modül bölümü, env var tablosu, cache dizini bilgisi
- `RAGIP_AGA_TASIMA_REHBERI.md`: "Sadece ragip_rates.py" hızlı başlangıç bölümü eklendi

### Tests

- `get_env_key` mock'ları kaldırıldı → `os.environ` mock'ları
- Yeni testler: `TestCacheDir`, `TestAllExports`

---

## [2.2.0] - 2026-02-21

### Added — Firma Profili (ragip-profil)

- Yeni skill: `/ragip-profil kaydet firma_adi=X sektor=Y is_tipi=Z`
- Sektöre duyarlı KOBİ profili — döviz riski, stok durumu, vade bilgisi
- Profil verisi tüm Ragıp Aga yanıtlarına otomatik context olarak eklenir
- CRUD: goster / kaydet / guncelle / sil

---

## [2.1.0] - 2026-02-21

### Added — Arbitraj Hesaplamaları

- **CIP faiz paritesi arbitrajı**: Teorik vs piyasa forward kuru karşılaştırması
- **Üçgen kur arbitrajı**: EUR-USD-TRY döngüsünde tutarsızlık tespiti
- **Vade farkı vs mevduat arbitrajı**: Geç öde mi, mevduata yatır mı?
- **Carry trade analizi**: USD borç → TL mevduat → başabaş kur
- Yeni skill: `/ragip-arbitraj [cip|ucgen|vade-mevduat|carry-trade]`

### Changed — TCMB EVDS2 → EVDS3 Migration

- Tüm API URL'leri `evds2.tcmb.gov.tr` → `evds3.tcmb.gov.tr/igmevdsms-dis/` olarak güncellendi
- Seri kodları güncellendi (TP.APF.* → TP.APIFON4, TP.REESAVANS.*)

---

## [2.0.0] - 2026-02-19

### Changed — Sub-Agent Mimarisi

- `ragip-aga` tek agent → orchestrator hub'a dönüştürüldü
- 3 sub-agent eklendi: `ragip-hesap` (haiku), `ragip-arastirma` (sonnet), `ragip-veri` (haiku)
- 11 skill 3 sub-agent'a dağıtıldı
- Hardcoded `~/.orchestrator` path'leri → `git rev-parse --show-toplevel` ile dinamik

### Added

- `ragip-ozet`: Günlük brifing özeti skill'i
- `ragip-import`: CSV/Excel veri aktarımı (cari hesap listeleri)
- Output persistence layer: Sub-agent'lar `data/RAGIP_AGA/ciktilar/` altına yazar

### Fixed

- Shell injection koruması (skill Bash bloklarında)
- Undefined `df` variable (ragip-import)
- Atomic write (cache dosyaları için `*.tmp → rename`)

### Tests

- `test_ragip_subagents.py`: Portability, skill dağılımı, dosya varlığı yapısal testleri

---

## [1.1.0] - 2026-02-17

### Fixed — Kritik Bug'lar

- **ZeroDivisionError**: `vade_farki()` gun=0 durumu
- **Türkçe sayı parse**: `45.000` (binlik ayırıcı) vs `45.000` (ondalık) ayrımı
- **Falsy-zero**: `if not value` → `if value is None` (0.0 geçerli değer)
- Invoice regex: TR/EN fatura formatları için iyileştirme

### Added

- Input validation: Negatif anapara, 0-1000 oran aralığı, negatif gün kontrolü
- Atomic write: Cache dosyaları için `*.tmp → rename` pattern
- Path traversal guard: Dosya okuma fonksiyonlarında

### Tests

- `test_ragip_finansal.py`: FinansalHesap sınıfı unit testleri
- `test_ragip_rates.py`: TCMB oran çekici testleri

---

## [1.0.0] - 2026-02-15

### Added — İlk Sürüm

- **CLI**: `ragip "soru"`, `ragip --calc`, `ragip --tcmb`, `ragip --interactive`
- **Hesap motoru**: Vade farkı, TVM, erken ödeme iskontosu, indiferans, NCD, döviz forward, ithalat maliyet
- **Dosya okuma**: PDF (pdfplumber/pypdf), DOCX, TXT, CSV — fatura meta çıkarımı
- **TCMB entegrasyonu**: EVDS API'den canlı faiz/kur verisi, 4 saat cache, fallback
- **CollectAPI**: Banka mevduat ve kredi oranları
- **Claude Code agent**: `.claude/agents/ragip-aga.md` — WebSearch, Read, Bash
- **6 skill**: vade-farki, analiz, dis-veri, strateji, ihtar, firma, gorev
- **LLM fallback**: claude-sonnet-4-5 → gpt-4o → gemini-2.5-flash
- **Rich output**: Terminal'de renkli tablo, syntax highlighting
- **Geçmiş**: `data/RAGIP_AGA/history.jsonl`
