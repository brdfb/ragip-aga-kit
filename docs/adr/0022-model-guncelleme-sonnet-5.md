# ADR-0022: Sonnet 4.5 → Sonnet 5 model güncellemesi

**Tarih:** 2026-07-07
**Durum:** Kabul edildi
**İlgili:** ADR-0014 (Prompt Caching Policy), ADR-0020 (LLM-judge Spirit Ölçümü)

## Bağlam

Kit'in hardcoded model referansları **Sonnet 4.5** (`anthropic/claude-sonnet-4-5-20250929`, Eylül 2025) sürümünde kalmıştı. 7 Temmuz 2026 sağlık kontrolünde model'in **10 aylık eski** olduğu tespit edildi. Şu anda mevcut:

- `claude-sonnet-5` (2026 family — güncel Sonnet)
- `claude-opus-4-8`
- `claude-haiku-4-5-20251001`

Sabit ID'nin bulunduğu 3 yer:
1. `config/ragip_aga.yaml:12` — orchestrator model default
2. `scripts/ragip_judge.py:54` — Tier 6 LLM-judge DEFAULT_MODEL
3. `tests/test_ragip_prompt_caching.py` (5 satır) — `_build_messages()` prefix testleri

Agent frontmatter'ları (`model: sonnet` / `model: haiku`) **kısayol** kullanıyor — Claude Code otomatik en güncel sürüme resolv ediyor, dokunmaya gerek yok.

## Gerekçe

**Neden şimdi:**
- Tier 6 judge'ın amacı "**anlamsal kalite**" ölçmek — daha iyi bir judge (Sonnet 5) daha doğru ölçüm verir. 10 ay eski modelle ölçüm, Tier 6'nın değer önerisini fiilen zayıflatıyor.
- Kit'te 47 gündür Tier 6 gerçek çıktı üzerinde çalıştırılmadı. İlk gerçek çalıştırma **doğru modelle** olmalı (baseline değerin geleceğe taşınacağı için).
- Modelin yeni sürümleri genellikle daha ucuz + daha hızlı + daha kaliteli — üç boyutta iyileşme beklenir.

**Neden `anthropic/claude-sonnet-5` (tarihsiz):**
- Litellm registry'sinde `anthropic/claude-sonnet-5` mevcut (doğrulandı).
- Tarihsiz alias en son Sonnet 5 sürümüne resolv olur — otomatik güncelleme yakalanır.
- Deterministik sürüm kaydı gerekirse (regression) ileride tarihli ID'ye (`anthropic/claude-sonnet-5-YYYYMMDD`) geçilebilir. Şu an için alias yeterli.

## Karar

1. **3 fonksiyonel yerde model ID güncellenir:**
   - `config/ragip_aga.yaml` — orchestrator default
   - `scripts/ragip_judge.py` — Tier 6 judge default
   - `tests/test_ragip_prompt_caching.py` — 5 test satırı

2. **Agent frontmatter kısayolları (`sonnet`, `haiku`) korunur** — Claude Code otomatik güncel modele resolv ediyor. Bir gün spesifik model ID istenirse (regression test için) hardcoded ID eklenebilir ama şu an gerek yok.

3. **`ragip_judge.py` içindeki `SONNET_*_USD_PER_MTOK` fiyat sabitleri geçici olarak dokunulmadı** — Sonnet 5 fiyatlaması Anthropic pricing sayfasından teyit edilmediği için mevcut (Sonnet 4.5 seviyesi) muhafazakâr tahmin olarak kalıyor. Doğrulanınca ayrı bir minor patch ile güncellenecek. Cost guard bu nedenle karar-güvenli tarafta ($0.50 tek çağrı / $5 haftalık limit korunuyor).

4. **Version bump:** patch değil **minor** (2.20.3 → **2.21.0**). Model değişimi hem `.ragip_manifest.json` checksum'ını değiştirir hem de kullanıcı görünür bir davranış farkı yaratır — minor semantic uygun.

## Sonuçlar

**Olumlu:**
- Tier 6 judge güncel modelle ölçüm yapabilir (Sonnet 5)
- Orchestrator default'u güncel
- 10 aylık modernizasyon borcu kapanır
- Prompt caching davranışı korunur (prefix kontrolü mantığı değişmedi)

**Riskler:**
- Sonnet 5 output'unun Tier 6'nın 6-dimension JSON şemasına uyumluluğu **litellm çağrısında test edilecek** — sistematik farklılık varsa `SPIRIT_RUBRIC` prompt'unun revizyonu gerekebilir. Mock testler yapısal doğruluğu geçtiğinden bu sorun kısa vadede beklenmiyor.
- Fiyat sabitlerinin (`SONNET_*_USD_PER_MTOK`) Sonnet 4.5 seviyesinde olması **muhafazakar tahmin** — gerçek maliyet Sonnet 5 için daha düşük olabilir. Cost guard fazla-tutucu tarafta hata verir; feature'ı bloke etmez, sadece bütçe hesabı gerçekten üstte durur.

**Nötr:**
- Test'lerdeki model ID prefix mantığını test ediyordu, ID'nin kendisi değil — test'ler pass etmeli (sadece string güncelleme).

## Etki alanı

- `config/ragip_aga.yaml` — 1 satır
- `scripts/ragip_judge.py` — 1 satır (DEFAULT_MODEL)
- `tests/test_ragip_prompt_caching.py` — 5 satır (aynı string, farklı fixture'lar)
- VERSION, config/ragip_aga.yaml versiyon, CHANGELOG (minor bump)

## Alternatifler değerlendirildi

**Alternatif A: Sürüm ID'yi tarihli tut (`anthropic/claude-sonnet-5-20260XXX`).** Reddedildi — determinizm için ileride yapılabilir; şu an alias yeterli, otomatik minor bump güncellemesi yakalanır. Şu an `20260XXX` alanı için doğrulanmış tarih yok.

**Alternatif B: Frontmatter'da da hardcoded ID.** Reddedildi — kısayol Claude Code'un güncel resolv mekanizmasıyla otomatik senkron. Hardcoded ID buna gerek yaratmaz, sadece maintenance yükü ekler.

**Alternatif C: Opus 4.8'e geç (Tier 6 judge için).** Reddedildi — Opus daha pahalı, cost guard'ı zorlar. Tier 6'nın amacı "kalite ölçmek", hedef prod-quality anlamsal değerlendirme; Sonnet 5 yeterli olmalı. Eğer Sonnet 5 ölçümü Tier 6'nın 6-dimension rubric'i için tutarsız çıkarsa, o zaman Opus 4.8 revize kararı ayrı bir ADR ile.
