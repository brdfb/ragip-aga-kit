# Ragip Aga Kit — Feature Ideas & Critique Backlog

Canli deneyim, sohbetler ve sistematik kit critique'inden derlenen fikirler.
Oncelik yok, siralama yok — acip bakip "simdi hangisi mantikli" diye degerlendirilecek liste.

Guncelleme: 2026-03-01 (v2.8.2)

---

## A. Aktif Fikirler

### ~~1. WebSearch Oran Tutarsizligi (ORTA)~~ — YAPILDI (v2.8.2)

ragip-analiz, ragip-strateji ve ragip-degerlendirme'den oran icin WebSearch kaldirildi. Tumu `ragip_get_rates.sh` kullaniyor. ragip-degerlendirme'de WebSearch sadece mevzuat guncellemesi icin kaldi (mesru kullanim).

---

### ~~2. Arastirma / Hukuk Sinir Netlestirme (ORTA)~~ — YAPILDI (v2.7.1 + v2.8.2)

v2.7.1'de orchestrator dispatch tablosu eklendi. v2.8.2'de belirsiz durumlar icin acik yonlendirme ornekleri eklendi ("sozlesme incele" → arastirma, "sozlesme hukuken sorunlu mu" → hukuk).

---

### ~~3. ragip-dis-veri Beklenti Yonetimi (ORTA)~~ — YAPILDI (v2.7.1)

Skill aciklamasi "on arastirma" olarak daraltildi, guven seviyeleri ve EKSIK bolumu eklendi.

---

### ~~4. FALLBACK_RATES Yaslanma Uyarisi (ORTA)~~ — YAPILDI (v2.7.1 + v2.8.2)

v2.7.1'de ragip_rates.py'ye >7 gun yaslanma uyarisi eklendi. v2.8.2'de 6 skill'in (vade-farki, strateji, arbitraj x4, analiz, degerlendirme) Bash bloklarina `rates.uyari` surfacing eklendi — uyari artik kullanici ciktisinda gorunuyor.

---

### ~~5. Skill Bash Bloklarinda DRY + FinansalHesap Tutarliligi (DUSUK)~~ — YAPILDI (v2.8.3)

ragip-vade-farki inline hesaplamalar `FinansalHesap.vade_farki()`, `.tvm_gunluk_maliyet()`, `.erken_odeme_iskonto()` cagrilariyla degistirildi — ragip-rapor ile tutarli pattern. ragip-arbitraj benzer sorun ama ayri kapsam.

---

### ~~6. Risk Skoru AI Disclaimer Iyilestirme (DUSUK)~~ — YAPILDI (v2.8.3)

ragip-analiz risk skoru ciktisina ve ragip-degerlendirme verdikt basliklarinin altina inline AI disclaimer eklendi. Skor/verdikt ile disclaimer artik yan yana.

---

### 7. Cikti Kesfedilebilirligi (DUSUK)

**Sorun:** Tum agent'lar `data/RAGIP_AGA/ciktilar/` altina zaman damgali dosya yaziyor ama:
- Indeks/katalog yok — orchestrator onceki ciktilari nasil buluyor?
- 3 ay sonra 200 dosya olunca "ABC Dagitim son analiz" nasil bulunur?
- Temizlik mekanizmasi yok — dosyalar sonsuza kadar birikir

**Cozum secenekleri:**
- a) ragip-ozet'e "son ciktilar" listesi ekle (basit, mevcut skill'e eklenir)
- b) ciktilar/index.jsonl — her cikti yazildiginda index'e kayit ekle
- c) Simdilik yeterli — Glob ile aranabilir, agent zaten yapiyor

**Effort:** Kucuk (a) / Orta (b)
**Risk:** b secenegi over-engineering olabilir — once a dene

---

### ~~8. Firma Bazli Rapor (YUKSEK DEGER)~~ — YAPILDI (v2.7.2)

6 analiz metodu `firma_id=None` parametresi aldi. `musteri_konsantrasyonu` haric (tek firmaya filtrelemek anlamsiz).

---

### ~~9. Fatura Uyari Sistemi (YUKSEK DEGER)~~ — YAPILDI (v2.8.0)

`FinansalHesap.fatura_uyarilari()` + ragip-ozet dashboard entegrasyonu. 3 kategori: vade gecmis, yaklasan vade (7g), TTK m.21/2 itiraz suresi (8g).

---

### ~~10. Nakit Cevrim Dongusu Dashboard (ORTA DEGER)~~ — YAPILDI (v2.8.1)

`FinansalHesap.ccc_dashboard()` — DSO + DPO + tahsilat orani + aging tek cagri. CCC = DSO - DPO (DIO haric — stok verisi yok). ragip-rapor'a `ccc` turu eklendi.

---

### 11. Agent Tool Kisitlama (MCP BAGIMLI)

**Sorun:** Agent, hedef repoda MCP tool gorunde system prompt talimatini atlayip dogrudan MCP'ye yoneliyor.

**Cozum:** Claude Code frontmatter'da `tools:` allowlist. Simdi prompt sertlestirme ile cozuldu (v3) ama yapisal enforcement daha guvenilir.

**Effort:** Kucuk — tek satir frontmatter degisikligi + test
**Risk:** Dusuk
**Oncelik:** MCP entegrasyonu cogaldikca artar

---

### 12. Cikti Dosyalarinda Meta Block (DUSUK)

**Sorun:** Ciktilar'da hangi kit versiyonu, hangi parametrelerle uretildigi belli degil.

**Fikir:** Her cikti dosyasinin basina YAML frontmatter (version, agent, skill, parametreler, tarih).

**Effort:** Kucuk-orta
**Risk:** Dusuk
**Oncelik:** Izlenebilirlik/audit gereksinimi olursa

---

### 13. Coklu Para Birimi Destegi (DURUMSAL)

**Sorun:** Tum hesaplamalar TRY bazli. `para_birimi` alani ADR-0007'de var ama metotlar kullanmiyor.

**Fikir:** Fatura analiz metotlarinda para birimi filtresi veya TCMB kuru ile TRY normalize.

**Effort:** Orta
**Risk:** Orta — kur hangi tarihin kuru? Spot mu, fatura tarihindeki mi?
**Oncelik:** Doviz faturasi olan firmalar icin

---

### 14. Odeme Plani Takibi (BUYUK)

**Sorun:** Kit vade farki hesapliyor, strateji olusturuyor ama onerilen odeme planinin takibi yok.

**Fikir:** `data/RAGIP_AGA/odeme_planlari.jsonl` + CRUD + gorev entegrasyonu.

**Effort:** Orta-buyuk — yeni veri yapisi + CRUD + skill
**Risk:** Orta — scope creep riski
**Oncelik:** Dusuk — once temel raporlama olgunlasmali

---

### 15. E-Fatura / E-Arsiv Parser (DURUMSAL)

**Sorun:** e-fatura zorunlu. Kit fatura semasinda `kaynak` alani var ama UBL-TR XML parse yok.

**Fikir:** `scripts/ragip_efatura_parser.py` — UBL-TR XML -> ADR-0007 semasi.

**Effort:** Orta
**Risk:** Orta — UBL-TR spec karmasik
**Oncelik:** e-fatura entegrasyonu gundemdeyse

---

## B. Reddedilen Fikirler (Critique Sonucu)

### X1. ragip-veri Skill Tool Davranisi (haiku)

**Orijinal fikir:** Haiku modelli ragip-veri Skill tool'u duzgun kullanamiyor olabilir.
**Neden reddedildi:** Cozum arayan cozum. ragip-veri'nin 5 skill'i hepsi `disable-model-invocation: true` — haiku sadece routing yapiyor ve bunu yapabiliyor. Canli kullaninda sorun raporlanmadi. Sorun cikarsa o zaman degerlendirilir.

### X2. ragip-analiz Dosya Yolu Olmadan Calisma

**Orijinal fikir:** ragip-analiz'e dosya yolu verilmezse `faturalar.jsonl`'den otomatik okusun.
**Neden reddedildi:** ragip-analiz belge analiz skill'i (sozlesme metni, fatura goruntusu). faturalar.jsonl yapilandirilmis veri — okunacak metin, analiz edilecek madde yok. Skill kimligini bozar. Kullanici aslinda "faturalara bak" istiyorsa ragip-ozet veya ragip-rapor dogru yonlendirme. Sorun analiz'de degil, orchestrator'de.

### X3. ragip-ihtar Tutar Esigi

**Orijinal fikir:** Belirli bir tutarin altinda ihtar gondermeyi engelle veya uyar.
**Neden reddedildi:** Esik kime gore? 500 TL bakkal icin buyuk, fabrika icin yuvarlama hatasi. Prensip meselesi mi tutar meselesi mi — kit bilemez. Kit danismandir, yasakci degil. Karar dayatmak yerine bilgi sunmak dogru: "Bu ihtarin noter masrafi ~800 TL, tutarla kiyasla."

### X4. Merkezi Cikti Sema Referansi

**Orijinal fikir:** `docs/output-standards.md` ile tum cikti turlerini standartlastir.
**Neden reddedildi:** 15 skill icin erken. Over-engineering. Her skill kendi formatini tanimliyor ve bu yeterli calisiyor. Kit 25+ skill'e cikarsa veya 3. parti kullanici gelirse tekrar degerlendirilir.

### X5. Markdown Rapor Template'leri

**Orijinal fikir:** `templates/ragip_templates.py` ile rapor formatlama kodu merkezilestir.
**Neden reddedildi:** 7 rapor icin erken soyutlama. Simdilik inline formatlama yeterli. Ragip Aga'nin sesi her raporda farkli — sablonlastirma sesi mekaniklestirme riski tasir.

---

## C. Izleme / Gelecek Degerlendirme

Bu maddeler "sorun olabilir ama simdi mudahale gereksiz" kategorisinde.

### I1. ragip_aga.py Monoliti (1643 satir)

CLI + FinansalHesap + dosya okuma + LLM + REPL tek dosyada. FinansalHesap ayri modul olabilir. Ama: tek consumer var, YAGNI. **Soru:** CLI standalone modu gercekten kullaniliyor mu? Kullanilmiyorsa monolitin maliyeti artmadan duruyor. Kullaniliyorsa bolme anlamli olur.

### I2. Arbitraj Skill Kullanim Degerlendirmesi

CIP ve carry trade banka hazine masasi araclari. Hedef kullanici KOBI. Canli kullaninda bu skill'ler ne kadar cagrildi? Kullanilmiyorsa karmasiklik bedava tasiniyor. Vade-mevduat mantikli (herkesin isi), CIP/carry trade ise nis.

### I3. Veri Migrasyonu Mekanizmasi

update.sh dosya bazinda 3-way checksum yapiyor (mukemmel). Ama veri semasi degisirse (orn: faturalar.jsonl'e yeni zorunlu alan) mevcut veriyi migrate edecek mekanizma yok. Sema su an stabil — sorun buyudukce degerlendirilir.

### I4. Veri Butunlugu / Yaziş Durumu

ragip_crud.py atomic write (tmp -> rename) yapiyor. Ama iki skill ayni anda ayni JSONL'e yazarsa "son yazan kazanir". Risk dusuk — orchestrator genelde ayni JSONL'e yazan iki skill'i paralel calistirmaz. Ama yapisal koruma yok.

### I5. Test Coverage Boslugu

237 test yapisal dogrulama yapiyor (frontmatter, skill dagilimi, portability). Ama test EDİLMEYEN alanlar:
- Skill Bash bloklarinin dogru calismasi (inline Python template'ler)
- Orchestrator'un dogru agent'a yonlendirmesi (integration test yok)
- Cikti dosyalarinin dogru formatta yazilmasi

Normal — LLM agent'lari e2e test etmek zor. Ama inline Python Bash bloklarinin birim testi olabilir.

---

## Degerlendirme Kriterleri

Her madde icin uc soru:
1. Gercek kullanici bunu istedi mi / ihtiyac duydu mu?
2. Mevcut cozum (prompt, manuel islem) yeterli mi?
3. Implement edince test edilebilir mi?

Ek sorular (critique'ten):
4. Bu degisiklik baska bir seyi bozar mi? (sema, parallellik, skill kimligi)
5. Prompt degisikligi mi, kod degisikligi mi? (prompt daha ucuz ve geri alinabilir)
6. Kit'in rolu "karar vermek" mi "bilgi sunmak" mi? (bilgi sun, karar dayatma)
