# Ragip Aga Kit — Feature Ideas & Critique Backlog

Canli deneyim, sohbetler ve sistematik kit critique'inden derlenen fikirler.
Oncelik yok, siralama yok — acip bakip "simdi hangisi mantikli" diye degerlendirilecek liste.

Guncelleme: 2026-03-19 (v2.8.6)

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

**Not (v2.8.6):** `ciktilar/` retention sorunu `ragip_temizle.sh` ile cozuldu (90 gun / 200 dosya limiti). Meta block (YAML frontmatter icerigi) hala eksik — izlenebilirlik/audit gereksinimi olursa implement edilecek.

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


### 17. Nakit Akis Projeksiyonu (YUKSEK DEGER — VERI BAGIMLI)

**Sorun:** Kit geriye bakiyor (aging, DSO, gecmis faturalar). Ama KOBi sahibini gece uyutmayan soru ileriye bakar: "ayin 15'inde maaslari odeyebilecek miyim?"

**Su an cevaplanamayan sorular:**
- "Onumuzdeki 30 gunde nakit sikisacak mi?" — forward projeksiyon yok
- "Hangi firmanin odeme davranisi kotulesiyir?" — trend analizi yok
- "Portfoy genelinde erken odersem ne kazanirim?" — tek fatura icin var, toplam yok

**Fikir — 3 asama:**

1. **Nakit akis tahmini**: Acik fatura vadeleri uzerinden 30/60/90 gun projeksiyon. `FinansalHesap.nakit_projeksiyon(faturalar, donem_gun=30)` — alacak vadeleri - borc vadeleri = net pozisyon, haftalik kirilim.
2. **Firma odeme trend analizi**: Son N faturanin ortalama gecikme gunu trendi. Kotulesme/iyilesme tespiti. "ABC Dagitim son 3 faturada ortalama 12 gun gec odedi, trend kotulesiyir."
3. **Portfoy erken odeme firsati**: Tum acik borc faturalarinda erken odeme iskontosu simulasyonu. "Bu ay 3 tedarikciye erken odersen toplam 4,200 TL tasarruf."

**Onkosul:** `faturalar.jsonl`'de yeterli veri olmali. MCP adaptor veya toplu import ile gercek fatura akisi baslamadan anlamsiz.

**Effort:** Orta — mevcut FinansalHesap motoruna 2-3 metot + ragip-rapor'a yeni tur
**Risk:** Dusuk — mevcut sema (ADR-0007) yeterli, yeni veri yapisi gerekmiyor
**Oncelik:** Canli veri akisi basladiginda ilk yapilacak is

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

**Degerlendirme zamani:** MCP entegrasyonu tamamlaninca kullanim verisi degerlendirilebilir. "CLI standalone hic cagrilmadi" sonucu cikacak olursa module kaldirmak yerine silmek daha temiz.

### I2. Arbitraj Skill Kullanim Degerlendirmesi

CIP ve carry trade banka hazine masasi araclari. Hedef kullanici KOBI. Canli kullaninda bu skill'ler ne kadar cagrildi? Kullanilmiyorsa karmasiklik bedava tasiniyor. Vade-mevduat mantikli (herkesin isi), CIP/carry trade ise nis.

### I3. Veri Migrasyonu Mekanizmasi

update.sh dosya bazinda 3-way checksum yapiyor (mukemmel). Ama veri semasi degisirse (orn: faturalar.jsonl'e yeni zorunlu alan) mevcut veriyi migrate edecek mekanizma yok. Sema su an stabil — sorun buyudukce degerlendirilir.

### I4. Veri Butunlugu / Yaziş Durumu

ragip_crud.py atomic write (tmp -> rename) yapiyor. Ama iki skill ayni anda ayni JSONL'e yazarsa "son yazan kazanir". Risk dusuk — orchestrator genelde ayni JSONL'e yazan iki skill'i paralel calistirmaz. Ama yapisal koruma yok.

### I5. Test Coverage Boslugu

244 test var (v2.8.6). Katman 1 (structural) ve Katman 2 (unit) saglamdir. Eksik katmanlar:

- **Katman 3 (integration):** Gercek fatura verisiyle FinansalHesap dogrulamasi. MCP veri akisi baslayana kadar anlamli fixture olusturulamaz — sifir gercek fatura var.
- **Katman 4 (e2e LLM):** Orchestrator'un dogru agent'a yonlendirmesi, skill ciktisi kalitesi. Non-deterministic + maliyetli — bilerek kapsam disi. ADR-0008.

**Not (v2.8.7):** ragip_temizle.sh icin Katman 2 testi yazildi (20 test, test_ragip_temizle.py). Toplam 264 test.

**Degerlendirme zamani:** MCP entegrasyonu tamamlaninca Katman 3 yazilir. Katman 4 muhtemelen hic yazilmaz (ADR-0008 gerekceye bakiniz).

### I6. Graceful Degradation Sinirlamasi

v2.8.6'da 4 sub-agent'a "elindeki sonuclari ozetle ve eksik kalanlari belirt" talimati eklendi.

**Arastirma sonucu (2026-03-19):** Bu talimat maxTurns hard cut icin calismaz. Dogrulanmis:

- Anthropic Agent SDK dokumanindaki ResultMessage tablosu: `error_max_turns` durumunda `result` alani YOK. Framework loop'u keser, son LLM cagrisi yapilmaz.
- `claude-agent-sdk-typescript` Issue #58: Son `PostToolUse` hook'u bile atlanabiliyor.
- GitHub Issue #29567 ("Graceful degradation for agent teams"): Anthropic kapatti, duplicate, cozum yok.

**Ne isler, ne islemez:**
- Tool fail / veri eksikligi gibi erken karar durmalarinda talimat devreye girer — isler.
- maxTurns hit'inde talimat okunamaz — islemez.
- **Gercek mitigasyon (zaten uygulamada):** Her sub-agent'in `CIKTI KAYDETME (ZORUNLU)` bolumu — her adim sonucu diske yazilir. Hard stop sonrasi partial output korunur.

**Framework karsilastirmasi:**
- CrewAI `forced_final_answer`: limit dolunca framework 1 LLM cagrisi daha yapar, synthesis prompt inject eder — gercek cozum.
- OpenAI Agents SDK `max_turns`: ayni hard stop pattern — cozum yok.
- Claude Code: hard stop, cleanup handler yok, Claude Code bu API'yi acarsa degerlendirilebilir.

**Oncelik:** Degismedi — skill'ler bounded scope, pratik etki minimal. KISMI SONUC talimati zarar vermez, genel davranis iyilestirici olarak kalabilir ama "graceful degradation sagladi" iddiasi dogruluk disi.

### I7. Uretim Hazirlik Kriterleri

Kit su an prototype asama: mimari saglam, hesaplama motoru yazilmis, test altyapisi kurulu. Ama uretim hazir degil:

- Sifir gercek fatura verisi — FinansalHesap hic gercek veri gorMEDI
- Sifir MCP adaptoru — Parasut/D365 entegrasyonu yok
- Kullanim verisi yok — hangi skill kac kez cagrildi bilinmiyor
- LLM routing dogru calisiyor mu — test edilmemis

**Uretim = en az bir MCP adaptoru + gercek fatura akisi + FinansalHesap gercek veriyle dogrulandi.**

MCP entegrasyonu bu kit'in gercek deger testidir. Oncesinde yapilan her iyilestirme hipoteze dayanir.

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
| 16 | Sub-Agent Graceful Degradation | v2.8.6 | 4 sub-agent'a kismi sonuc talimatı + orchestrator partial failure bildirimi |

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
