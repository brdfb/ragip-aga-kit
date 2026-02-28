# Ragip Aga Kit — Feature Ideas & Critique Backlog

Canli deneyim, sohbetler ve sistematik kit critique'inden derlenen fikirler.
Oncelik yok, siralama yok — acip bakip "simdi hangisi mantikli" diye degerlendirilecek liste.

Guncelleme: 2026-02-28 (v2 — kit-wide critique sonrasi)

---

## A. Aktif Fikirler

### 1. WebSearch Oran Tutarsizligi (ORTA)

**Sorun:** Ayni bilgiyi (yasal gecikme faizi) uc farkli yoldan aliyor:
- ragip-hesap: ragip_rates.py -> TCMB API -> cache -> fallback
- ragip-arastirma: WebSearch "yasal gecikme faizi 2026"
- ragip-hukuk: WebSearch ayni arama

Paralel calistirilirsa farkli sonuclar bulabilirler. Orchestrator sentezlediginde celiskili rakamlar cikar.

**Cozum secenekleri:**
- a) Oran bilgisi tek kaynak: ragip_rates.py. Diger agent'lar hesap ciktisina bagimli olur (paralelligi kisitlar)
- b) Arastirma ve hukuk'a "oran icin WebSearch yapma, ragip_get_rates.sh kullan" talimati ekle (prompt degisikligi)
- c) Orchestrator'e "once hesap, sonra diger" siralamasini zorunlu kil

**Effort:** Kucuk (b secenegi) / Orta (a veya c)
**Risk:** b secenegi prompt'a guvenme — agent atlayabilir. a secenegi paralelligi bozar.

---

### 2. Arastirma / Hukuk Sinir Netlestirme (ORTA)

**Sorun:** ragip-arastirma ve ragip-hukuk ikisi de sozlesme okuyor, ikisi de yasal referans veriyor. Ayrim kit gelistiricisinin kafasinda net, kullanicinin kafasinda degil.

Kullanici "bu sozlesmeyi incele" dediginde orchestrator hangisine yonlendirecek? Ikisi de "sozlesme oku + yorum yap" yapiyor.

**Gercek fark:**
- arastirma: ticari analiz (vade maddeleri, KDV, risk skoru, muzakere kozlari)
- hukuk: hukuki pozisyon (mevzuat, ispat yuku, zamanasimiI, arabuluculuk)

**Cozum secenekleri:**
- a) Orchestrator prompt'una net yonlendirme tablosu ekle ("sozlesme analizi" -> arastirma, "hakli miyiz" -> hukuk)
- b) Skill/agent aciklamalarini kullanici diline yaklastir
- c) Ikisini birlestir (ADR-0006'yi geri al) — riskli, 4-agent karari iyi gerekcelendirilmis

**Effort:** Kucuk (a secenegi — prompt guncellemesi)
**Risk:** Dusuk — prompt iyilestirmesi, mimari degisiklik degil

---

### 3. ragip-dis-veri Beklenti Yonetimi (ORTA)

**Sorun:** Tek araci WebSearch. "Karsi tarafi arastir" deyince kullanici guclu sonuc bekler, ama:
- Turk sirket verileri web'de duzgun indekslenmemis
- Ticaret Sicil Gazetesi WebSearch ile guvenilir bulunamaz
- Asil degerli kaynaklar (UYAP, Findeks, KKB) kisitli — skill "kullanicidan iste" diyor

Sonuc: Skill tutarli sekilde hayal kirikligi yaratiyor olabilir.

**Cozum secenekleri:**
- a) Skill aciklamasini "kamuya acik kaynaklardan ON arastirma" olarak daralt, beklentiyi dusur
- b) Skill'in ciktisina "Bu sonuclar sinirlidir, kesin bilgi icin Findeks/UYAP gerekir" uyarisini guclendir
- c) Skill'i kaldir, is-veri'yi arastirma agent'indan cikar — asiri tepki

**Effort:** Kucuk (a+b prompt guncellemesi)
**Risk:** Dusuk

---

### 4. FALLBACK_RATES Yaslanma Uyarisi (ORTA)

**Sorun:** ragip_rates.py'de hardcoded fallback:
```
politika_faizi: 37.00, guncelleme: "21 Subat 2026"
```
TCMB faiz karari gelip oran degisirse, API key'i olmayan kullanici eski oranla hesap yapar. `kaynak: "fallback"` yaziyor ama kullanici fark etmeyebilir. Yasal gecikme faizi = avans faizi — ihtar yazisindaki faiz referansi sessizce yanlis olur.

**Cozum secenekleri:**
- a) Fallback kullanildiginda ve X gundan eskiyse acik uyari: "Bu oranlar N gun oncesine ait, guncel olmayabilir"
- b) Skill ciktilarina `kaynak: fallback (N gun once)` notu ekle
- c) TCMB_API_KEY yoksa ilk kullaninda kullaniciya setup talimati goster

**Effort:** Kucuk (a — ragip_rates.py'ye 5 satir kontrol)
**Risk:** Dusuk

---

### 5. Skill Bash Bloklarinda DRY + FinansalHesap Tutarliligi (DUSUK)

**Sorun:** Iki tutarsizlik:
1. 7-8 skill'de ayni Bash preamble tekrarlaniyor (git rev-parse, ragip_crud import)
2. ragip-rapor FinansalHesap metotlarini cagiriyor, ama ragip-vade-farki ayni hesaplamayi inline Python ile yaziyor. Neden?

ragip_crud.py DRY helper olarak yapildi (ADR-0005) ama skill Bash bloklari hala DRY degil.

**Cozum secenekleri:**
- a) ragip-vade-farki'yi FinansalHesap.vade_farki() cagiracak sekilde guncelle (ragip-rapor ile tutarli)
- b) Ortak preamble'i scripts/ragip_skill_preamble.sh'ye tasi
- c) Mevcut durumu kabul et — skill'ler bagimsiz, tekrar kabul edilebilir

**Effort:** Kucuk-orta
**Risk:** Dusuk — refactor, davranis degisikligi yok
**Not:** c secenegi de savunulabilir — her skill bagimsiz calisabilmeli, bagimlilik eklenmemeli

---

### 6. Risk Skoru AI Disclaimer Iyilestirme (DUSUK)

**Sorun:** ragip-analiz risk skoru veriyor (0-50), ragip-degerlendirme "GUCLU/ORTA/ZAYIF" diyor. Bunlar LLM'in subjektif degerlendirmeleri ama kullanici nesnel olcum olarak algilayabilir.

"Risk skoru: 15/50 — DUSUK" gordugunde "sorun yok" diye dusunebilir. Sayisal skor disclaimer'i golgeliyor — insanlar sayiya inanir.

**Cozum:** Skoru kaldirmak degil — skorun hemen altina (disclaimer'in yanina degil) "AI tahmini, hukuki degerlendirme degildir" yazmak. Disclaimer zaten var ama skordan uzakta.

**Effort:** Kucuk — prompt guncellemesi
**Risk:** Dusuk

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

### 8. Firma Bazli Rapor (YUKSEK DEGER)

**Sorun:** Tum raporlar (aging, DSO, DPO) tum faturalar uzerinden calisiyor. "ABC Dagitim icin aging raporu" yapilamiyor.

**Fikir:** Mevcut metotlara `firma_id` filtresi:
```python
FinansalHesap.aging_raporu(faturalar, firma_id=10)
FinansalHesap.dso(faturalar, firma_id=10)
```

**Effort:** Kucuk — her metota 3-4 satir filtre eklemek
**Risk:** Dusuk
**Not:** En dogal kullanim senaryosu, gercek ihtiyac

---

### 9. Fatura Uyari Sistemi (YUKSEK DEGER)

**Sorun:** Faturalar.jsonl'de vade gecmis faturalar var ama kit bunu sadece sorulunca soyluyor. Proaktif degil.

**Fikir:** ragip-ozet skill'ine ekle:
- Vade gecmis faturalar (bugun > vade_tarihi, durum=acik)
- Yaklasan vadeler (7 gun icinde)
- TTK m.21/2 fatura itirazi 8 gun suresi yaklasanlar

**Effort:** Orta — yeni metot + skill prompt
**Risk:** Dusuk
**Not:** ragip-ozet zaten dashboard — uyarilar oraya dogal oturur, yeni skill gereksiz

---

### 10. Nakit Cevrim Dongusu Dashboard (ORTA DEGER)

**Sorun:** DSO, DPO ayri ayri hesaplaniyor. CCC = DSO + DIO - DPO tek rapor olarak yok.

**Fikir:** `FinansalHesap.nakit_cevrim_dashboard()`:
- DSO + DPO + tahsilat orani + aging tek cagri
- Stok varsa DIO dahil (profil'den `stok.var` kontrolu)

**Effort:** Kucuk — mevcut metotlari birlestirmek
**Risk:** Dusuk

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

213 test yapisal dogrulama yapiyor (frontmatter, skill dagilimi, portability). Ama test EDİLMEYEN alanlar:
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
