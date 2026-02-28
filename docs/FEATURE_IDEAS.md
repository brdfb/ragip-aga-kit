# Ragip Aga Kit — Feature Ideas & Critique Backlog

Canli deneyim, sohbetler ve sistematik kit critique'inden derlenen fikirler.
Oncelik yok, siralama yok — acip bakip "simdi hangisi mantikli" diye degerlendirilecek liste.

Guncelleme: 2026-03-01 (v2.8.4)

---

## A. Aktif Fikirler

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

## D. Tamamlanan (10/10)

| # | Madde | Versiyon | Ozet |
|---|-------|----------|------|
| 1 | WebSearch Oran Tutarsizligi | v2.8.2 | Oran icin WebSearch kaldirildi, tumu `ragip_get_rates.sh` kullaniyor |
| 2 | Arastirma / Hukuk Sinir Netlestirme | v2.7.1 + v2.8.2 | Orchestrator dispatch tablosu + belirsiz durum yonlendirmesi |
| 3 | ragip-dis-veri Beklenti Yonetimi | v2.7.1 | Skill aciklamasi "on arastirma" olarak daraltildi |
| 4 | FALLBACK_RATES Yaslanma Uyarisi | v2.7.1 + v2.8.2 | >7 gun yaslanma uyarisi + 6 skill'de surfacing |
| 5 | DRY + FinansalHesap Tutarliligi | v2.8.3 | ragip-vade-farki inline hesaplamalar FinansalHesap cagrilariyla degistirildi |
| 6 | Risk Skoru AI Disclaimer | v2.8.3 | ragip-analiz + ragip-degerlendirme'ye inline AI disclaimer |
| 7 | Cikti Kesfedilebilirligi | v2.8.4 | ragip-ozet'e SON CIKTILAR + FIRMA CIKTILARI bolumleri |
| 8 | Firma Bazli Rapor | v2.7.2 | 6 analiz metodu `firma_id` parametresi aldi |
| 9 | Fatura Uyari Sistemi | v2.8.0 | `fatura_uyarilari()` — vade gecmis, yaklasan, TTK itiraz |
| 10 | Nakit Cevrim Dongusu Dashboard | v2.8.1 | `ccc_dashboard()` — DSO + DPO + tahsilat + aging tek cagri |

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
