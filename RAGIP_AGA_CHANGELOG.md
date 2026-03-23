# Ragıp Aga — Changelog

Ragıp Aga'ya özgü değişiklik geçmişi. Ana orchestrator CHANGELOG.md'den bağımsızdır.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

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
