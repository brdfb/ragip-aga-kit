# ADR-0016: Cikti Disiplini (Tier 3) — 3-Satir Blok + VARSAYIM Damgasi

**Tarih:** 2026-05-13
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici
**Iliski:** ADR-0010 (Savunma katmanlari), ADR-0013 (CoVe + madde_dogrula), ADR-0015 (Tier 2C whitelist)

## Baglam

LLM-driven skill ciktilarinda (ragip-analiz, ragip-strateji, ragip-degerlendirme) iki tekrarli sorun:

### Sorun 1: Kritik bulgu kaybi

Bulgu listeleri serbest-format markdown bullet:
```
- Madde 7'de vade farki sartlari belirsiz, dikkatli incelenmeli
- Karsi tarafin pozisyonu zayif gozukuyor
- Ihtar gondermek faydali olabilir
```

Bu format:
- Spesifik tutar/madde/etki yerine yumusatici dil ("dikkatli", "gozukuyor", "olabilir")
- Aksiyon zayif veya yok
- Tarayici okumayi engelliyor — yuksek-stake bulgular paragraflar arasinda kayboluyor

### Sorun 2: Spekulatif sayisal iddia

Model veri yetersizken bile tek-noktali tahmin verebilir:
```
"Yıllık ~500K kayıp olasıdır"
"Bu strateji ~$100K maliyet getirir"
"3 ay icinde anlasma saglanabilir"
```

Bu ifadeler:
- Veri yoksa LLM extrapolasyon — overconfidence bias (arXiv 2512.16030, 2025)
- Tek nokta tahmin kullaniciyi yanlis kesinlik hissine sokar
- Aralik yerine "kesinlik" hissi karar verdirici olabilir

### Cherry-pick kaynagi

gibibyte-cfo-agent v0.2 (Nisan 2026) bu iki sorunu **K2** ve **3-satir TESPIT/POZISYON/GEREKCE** disipliniyle cozdu:
- K2: "Veri yok = VARSAYIM damgasi + aralik (X-Y TRY). Tek nokta verme."
- 3-satir: "TESPIT: <bulgu>. POZISYON: <fiil ile baslar>. GEREKCE: <opsiyonel>."

Mevcut kit savunma katmanlari:
- **Tier 1 Barnum** (v2.11.0): Generic-bulgu eliminasyonu (prompt-tabanli)
- **Tier 2A madde_dogrula** (v2.12.0): Deterministik kanun maddesi dogrulamasi
- **Tier 2B CoVe** (v2.12.0): Yapisal verification akisi
- **Tier 2C whitelist** (v2.14.0): Citation source authority

Eksik: **Tier 3 — cikti formati ve belirsizlik tanima**.

## Karar

**Tier 3 — Cikti disiplini**, ragip-analiz, ragip-strateji, ragip-degerlendirme'de prompt-level zorunluluk.

### Bilesen 1: 3-satir blok formati (kritik bulgular icin)

```
TESPIT: <1 cumle, somut alıntı + madde + tutar + sure — generic yasak>
POZISYON: <1 cumle, fiil ile baslar — ne yapilacak>
GEREKCE: <opsiyonel; sorulursa veya etki esik ustunde ise>
```

**Hangi bolumlerde zorunlu:**
- ragip-analiz: KRITIK MADDELER, ELINDEKI KOZLAR, RISKLER (her madde 3-satir)
- ragip-strateji: RAGIP AGA'NIN TAVSIYESI, BU HAFTA YAPILACAKLAR
- ragip-degerlendirme: SONUC VE ONERI

**Hangi bolumlerde serbest:**
- Anlatim paragraflari (DOSYA OZETI, HUKUK NOTU, DURUM ANALIZI, HUKUKI DEGERLENDIRME, MADDE BAZLI ANALIZ)
- Senaryo aciklamalari (Kosul, Hedef, Hafta plani)
- Cikti formati orneklemesi

### Bilesen 2: VARSAYIM damgasi (sayisal iddialar icin)

Veri yoksa cikti basina BUYUK harfle:
```
VARSAYIM: 300-700K TRY yillik kayip olasi (aralik)
Bu varsayimdir, kesinlesmek icin son 12 ay fatura datasi gerekli.
```

**Kurallar:**
- Tek nokta tahmin YASAK — daima aralik (X-Y)
- "Bu varsayimdir, kesinlesmek icin [belge/veri] gerekli" cumlesi zorunlu
- Belge gelince varsayim damgasi kaldirilir
- Mevzuatta gercek bir sure/tutar (orn: TBK m.146 = 10 yil) varsa varsayim degil — kesin yaz

### Kapsam matrisi

| Skill | Tier 3 uygulanir | Sebep |
|-------|------------------|-------|
| ragip-analiz | **Evet** | LLM-driven, sozlesme yorumu, spekulatif risk degerlendirme |
| ragip-strateji | **Evet** | LLM-driven, senaryo maliyetleri tahmini |
| ragip-degerlendirme | **Evet** | LLM-driven, hukuki tahmin |
| ragip-rapor | Hayir | Deterministik FinansalHesap ciktisi, sayisal tablo |
| ragip-vade-farki | Hayir | Pure hesap, VARSAYIM gereksiz |
| ragip-arbitraj | Hayir | Deterministik hesap |
| ragip-zamanasimi | Hayir | Mevzuat ve takvim — kesin |
| ragip-delil | Belki gelecek | Liste-bazli, ama gerekirse 3-satir uygulanabilir |
| ragip-ihtar | Hayir | Sablon ciktisi, persona dili |

## Gerekce

| Alternatif | Red nedeni |
|---|---|
| Full markdown template (X5 reddedildi) | Ses mekaniklesir — anlatim sesi her raporda farkli, sablonlaştirma bozar |
| Sadece anlatim metni (mevcut) | Kritik bulgular kayboluyor, spesifiklik yetersiz |
| Tablo format zorunlulugu | ragip-rapor tablo kullaniyor — semantic karisiklik; kritik bulgu farkli yapida |
| Kit-wide cikti standardi (X4 reddedildi) | 19 skill icin erken — sadece kritik 3 LLM skill icin uygulanir |

**Secilen yaklasimin avantajlari:**

- **X5 distinction**: TEMPLATE (full report) degil, KRITIK BULGU BLOK FORMATI — anlatim sesi korunur.
- **Tier 1 Barnum ile uyumlu**: Barnum generic-bulgu filtresi, Tier 3 yapisal sunum — birbirini tamamlar.
- **Tier 2A madde_dogrula ile uyumlu**: Tier 3 spesifiklik talep eder (madde no zorunlu), bu madde_dogrula icin daha temiz input.
- **Geri alinabilir**: Prompt-level — istenmezse silinir.
- **Test edilebilir**: Skill metninde "TESPIT/POZISYON/GEREKCE" ve "VARSAYIM" string'leri regex/grep ile dogrulanir.

**Sinirlamalari:**

- Prompt-level enforcement — model atlayabilir.
- "3-satir blok" gercekten 3 satir mi yoksa 5-6 satira yayilan bullet mi — semantic, kati format degil.
- VARSAYIM damgasi "veri yoksa" tanimi model yargisina bagli — agresif veya laz olabilir.
- ragip-ihtar (sablon ciktisi) kapsamda degil; sablonun kendisi disiplin saglıyor.

## Konsekvanslar

### Pozitif

- Kritik bulgu okuma surati artar — taranabilir format.
- Overconfidence riski azalir — aralik kullanmak modelin "bilmiyorum" demesinin yapisal araci.
- gibibyte-cfo-agent K2 + 3-satir disiplini kit'e tasinir — cross-project tutarlilik.
- Tier 1+2A+2B+2C+3 → tam savunma katmani.

### Negatif

- Model bazi raporlarda "asiri yapisal" gozukebilir — anlatim paragraflari serbest birakilarak dengelenir.
- Yeni LLM skill eklendiginde Tier 3 disiplini hatirlanmali — bu ADR onbil belge olarak yardimci.
- Aralik gerektirir → bazen kullanici "tek sayi soyle" beklerken model VARSAYIM aralik verir. UX trade-off.

### Gelecek calisma

- ragip-delil'e Tier 3 ekleme: delil tablosu zaten yapisal, ama her satira POZISYON ekleyebilir.
- ragip-rapor commentary kismina (FinansalHesap aciklamalari) Tier 3 — opsiyonel.
- Disiplin etkililigi olcumu: sample raporlarda "VARSAYIM" gercek aralik mi tek nokta yamali mi audit.
- Test gevsetme: 3-satir kati pattern degil, semantic dogrulama (LLM ile pattern teyit) — sonraki versiyon.

## Iliski

- **Onceki:** ADR-0010 (Savunma katmanlari); ADR-0013, ADR-0015 ile birlikte Tier 1-2C zinciri tamam.
- **Bu ADR:** Tier 3 cikti formati katmani.
- **Tamamlayici:** Tier 1 (Barnum) generic-bulgu filtre + Tier 3 (3-satir) yapisal sunum birbirini destekler.
- **Sonraki:** ragip-delil ve ragip-rapor commentary'sine genisletme; semantic test pattern'i.

## Kaynaklar

- gibibyte-cfo-agent v0.2 (Nisan 2026) — 5 Operasyonel Kural (K2 + 3-satir TESPIT/POZISYON/GEREKCE)
- arXiv 2512.16030 (2025) — "Do LLMs Know What They Don't Know" overconfidence bias
- FEATURE_IDEAS X4, X5 — kit-wide template ve rapor sablonu reddetme nedenleri
- ADR-0010 — Savunma katmanlari mimari
