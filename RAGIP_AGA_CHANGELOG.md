# Ragıp Aga — Changelog

Ragıp Aga'ya özgü değişiklik geçmişi. Ana orchestrator CHANGELOG.md'den bağımsızdır.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

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
