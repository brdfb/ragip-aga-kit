# Ragip Aga Kit — Proje Genel Bakis

**Versiyon:** 2.8.15 | **Lisans:** MIT | **Platform:** Claude Code (Anthropic)

---

## Bu Ne?

Ragip Aga Kit, Turk KOBi'lerin **nakit akisi yonetimi, vade pazarligi ve ticari uyusmazlik danismanligi** icin tasarlanmis bir Claude Code agent sistemidir.

Hedef: Isletme sahibi veya muhasebecinin "bu tedarikciyle vade farkini nasil hesaplarim", "hakli miyiz bu uyusmazlikta", "aging raporum nasil gorunuyor" gibi sorularina **hesaplama destekli, mevzuat referansli** cevaplar uretmek.

## Hangi Problemi Cozuyor?

| Problem | Mevcut Durum | Kit ile |
|---------|-------------|---------|
| Vade farki hesabi | Excel'de elle, hataya acik | 21 farkli finansal hesaplama, canli TCMB oranlariyla |
| Fatura analizi | Muhasebeci ay sonu bakar | Aging, DSO, DPO, tahsilat orani, gelir trendi, musteri konsantrasyonu, KDV ozeti, CCC — anlik |
| Ticari uyusmazlik | Avukata git, bekle, para ode | On degerlendirme: haklilik analizi, zamanasimi hesabi, delil stratejisi, ihtar taslagi |
| Karsi taraf arastirmasi | Manuel internet taramasi | Ticaret Sicil, haber arsivi, sirket profili — yapilandirilmis rapor |
| Veri daginiikligi | Parasut ayri, D365 ayri, Excel ayri | ERP-agnostik sema: tum ERP'ler tek formata normalize edilir |

## Kime Hitap Ediyor?

- **Isletme sahipleri** — "Vade uzatayim mi, erken odeme iskontosu mu alayim?" kararlarinda
- **Muhasebeciler** — Fatura analiz raporlari, KDV donem ozeti, nakit cevrim dongusu
- **Mali musavirler** — Firma bazli finansal saglık gostergesi
- **Hukuk danismanlari** — Ticari uyusmazlik on degerlendirmesi (avukat yerine degil, avukata gitmeden once)

## Deger Onerisi

### 1. Hesaplama Motoru (FinansalHesap)

23 metot, tamami test edilmis, Python sinifi:

| Kategori | Metotlar |
|----------|----------|
| **Vade & Faiz** | vade_farki, tvm_gunluk_maliyet, erken_odeme_iskonto, indiferans_iskonto, odeme_plani_karsilastir |
| **Doviz & Ithalat** | doviz_forward, ithalat_maliyet |
| **Arbitraj** | covered_interest_arbitrage, ucgen_kur_arbitraji, vade_mevduat_arbitraji, carry_trade_analizi |
| **Fatura Analiz** | aging_raporu, dso, dpo, tahsilat_orani, gelir_trendi, musteri_konsantrasyonu, kdv_donem_ozeti, ccc_dashboard, fatura_uyarilari |
| **Nakit Akisi** | nakit_projeksiyon, odeme_trend_analizi |
| **Operasyonel** | nakit_cevrim_dongusu |

Tum hesaplamalar **canli TCMB oranlarıyla** calisir. Fallback zinciri: EVDS3 API → CollectAPI → 4 saat cache → hardcoded fallback.

### 2. Agent Mimarisi (5 Agent, 15 Skill)

```
ragip-aga (orchestrator)
  |
  +-- ragip-hesap -------- vade-farki, arbitraj, rapor
  +-- ragip-arastirma ---- analiz, dis-veri, strateji
  +-- ragip-hukuk -------- degerlendirme, zamanasimi, delil, ihtar
  +-- ragip-veri --------- firma, gorev, import, ozet, profil
```

- **Model maliyet optimizasyonu**: Deterministik isler (CRUD, hesaplama) haiku ile, derin analiz (strateji, hukuk) sonnet ile
- **Skill izolasyonu**: Her skill tek sorumluluk, cakisma yok, bagimsiz test edilebilir
- **Tool kisitlama**: Principle of Least Privilege — WebSearch/WebFetch yalnizca ihtiyac duyan skill'lerde acik

### 3. ERP-Agnostik Veri Mimarisi

```
[Parasut] --MCP adaptor--> firmalar.jsonl  ---> FinansalHesap
[D365]    --MCP adaptor--> faturalar.jsonl ---> (hesaplama + rapor)
[Logo]    --MCP adaptor--> gorevler.jsonl  ---> ciktilar/*.md
[Netsis]  --MCP adaptor-->
```

Kit hesaplama yapar, ERP'yi bilmez. MCP adaptorleri veriyi normalize eder.
Yeni ERP eklemek = yeni MCP adaptor yazmak. Kit'e dokunulmaz.

**Standart sema** (ADR-0007): `faturalar.jsonl` — 15 alan, ISO 8601 tarih, ISO 4217 para birimi, alacak/borc yonu, kismi odeme destegi.

**Veri kalitesi sozlesmesi** (v2.8.9): `validate_fatura()` — MCP'den gelen her kayit ADR-0007 semasina karsi dogrulanir. Hatali kayitlar uyari ile atlanir, gecerli kayitlarla hesaplama devam eder. Zorunlu alan, tip, enum, tarih formati, kismi odeme tutarliligi kontrolleri.

### 4. Hukuki Danismanlik Modulu

4 skill, TBK/TTK/IIK/KVKK/HMK referansli:

| Skill | Islem |
|-------|-------|
| ragip-degerlendirme | Haklilik analizi (mevzuat + sozlesme) |
| ragip-zamanasimi | TTK m.21/2 itiraz suresi, TBK m.146-147, arabuluculuk, icra takip |
| ragip-delil | Delil gucu puanlama, eksik delil tespiti, avukata dosya taslagi |
| ragip-ihtar | Vade farki / hizmet kusuru / sozlesme ihlali ihtar yazisi TASLAGI |

**Onemli:** Hukuki moduller avukat yerine gecmez. On degerlendirme ve dosya hazirligi saglar.

## Teknik Ozellikler

| Ozellik | Deger |
|---------|-------|
| Python | 3.12+ |
| Test | 377 (9 katman: yapisal, bash block, finansal, fatura analiz, TCMB, install/update, temizle, integration, cikti) |
| Agent | 5 (1 orchestrator + 4 sub-agent) |
| Skill | 15 (8 prosedurel + 7 LLM) |
| Hesaplama metodu | 23 |
| ADR (mimari karar) | 9 |
| Dis bagimlilik | 4 (pdfplumber, pandas, openpyxl, pyyaml) |
| TCMB entegrasyonu | EVDS3 + CollectAPI, 4 saat cache, 3 katman fallback |
| Kurulum | `bash install.sh` — hedef repoya 33 dosya kopyalar |
| Guncelleme | `bash update.sh` — uclu checksum, kullanici degisikliklerini korur |
| Portability | Tum path'ler `git rev-parse --show-toplevel`, hardcoded path yok |

## Kullanim Senaryolari

### Senaryo 1: Vade Pazarligi

```
Kullanici: "ABC Dagitim 45 gun vade istiyor, 250K fatura. Vade farki ne olur?"
Kit: FinansalHesap.vade_farki(250000, yillik_oran=3.0, gun=45)
     → Net maliyet: 9,246.58 TL (canli TCMB oraniyla)
     → Alternatif: erken_odeme_iskonto → %2.1 iskonto teklif edin
     → Karsilastirma: odeme_plani_karsilastir → 3 secenek TVM analizi
```

### Senaryo 2: Fatura Sagligi

```
Kullanici: "/ragip-rapor hepsi"
Kit: aging_raporu → 0-30: 180K, 31-60: 95K, 61-90: 45K, 90+: 22K
     dso → 38 gun (sektorde ortalama: 45)
     tahsilat_orani → %87.3
     musteri_konsantrasyonu → HHI: 2,450 (orta risk)
     ccc_dashboard → DSO(38) + DIO(0) - DPO(52) = -14 gun (nakit pozitif)
```

### Senaryo 3: Ticari Uyusmazlik

```
Kullanici: "Tedarikci fazla fatura kesti, 6 aydir yanit vermiyor. Ne yapabiliriz?"
Kit: ragip-degerlendirme → TTK m.21/2 kapsaminda itiraz suresi analizi
     ragip-zamanasimi → Fatura itirazi: 8 gun (TTK), genel: 10 yil (TBK m.146)
     ragip-delil → Mevcut deliller puanlanir, eksikler listelenir
     ragip-ihtar → Hukuki dilde ihtar taslagi (avukat kontrolu gerekir)
```

## Bilinen Sinirlamalar

| Sinir | Aciklama | Referans |
|-------|----------|----------|
| **Nested agent dispatch** | Claude Code'da sub-agent baska sub-agent spawn edemez | ADR-0009 |
| **Auto-delegation** | Model skill dispatch etmek yerine kendisi yapmayı tercih edebilir | ADR-0009, GitHub #18352 |
| **MCP adaptor gerekli** | Kit tek basina ERP verisi cekmez — MCP adaptor yazilmali | ADR-0004 |
| **Hukuki sinir** | Avukat tavsiyesi degildir, on degerlendirme saglar | Tum hukuk skill'leri |
| **TCMB bagimliligi** | API key yoksa fallback oranlara duser (guncel olmayabilir) | ragip_rates.py |
| **Arbitraj skill'leri** | CIP ve ucgen kur KOBi icin sinirli faydali, vade-mevduat en relevant | FEATURE_IDEAS I2 |

## Mimari Kararlar (ADR Ozeti)

| ADR | Baslik | Ozet |
|-----|--------|------|
| 0001 | Sub-Agent Mimarisi | Orchestrator + 4 sub-agent, skill izolasyonu |
| 0002 | Version-Manifest-Update | SHA-256 checksum ile guncelleme |
| 0003 | Manifest Kit Hash | Kullanici degisikliklerini koruma |
| 0004 | Kit vs MCP Ayrimi | Kit = zeka + validasyon, MCP = veri + ERP-aware normalizasyon |
| 0005 | DRY Helpers | ragip_get_rates.sh + ragip_crud.py |
| 0006 | Hukuk Sub-Agent | ragip-hukuk + 4 skill |
| 0007 | Standart Fatura Semasi | ERP-agnostik veri sozlesmesi |
| 0008 | Test Stratejisi | Structural oncelikli, behavioral out-of-scope |
| 0009 | Hybrid Orchestrator | Nested spawn desteklenmiyor, Senaryo B birincil |

## Dosya Yapisi

```
ragip-aga-kit/
  agents/             # 5 agent .md dosyasi
  skills/             # 15 skill dizini (SKILL.md)
  scripts/            # Python + bash yardimci moduller
    ragip_aga.py      # FinansalHesap motoru (21 metot)
    ragip_rates.py    # TCMB oran cekmesi (standalone, sifir bagimlilik)
    ragip_crud.py     # CRUD helper (load/save, parse_kv, atomic_write)
    ragip_output.py   # Merkezi cikti yonetimi (kaydet, manifest, t-factor)
    ragip_get_rates.sh # Skill'ler icin oran helper
    ragip_temizle.sh  # Cikti dizini temizleme
  config/             # ragip_aga.yaml + dispatch kuralları
  data/RAGIP_AGA/     # Runtime veri (firmalar, faturalar, gorevler, ciktilar)
  tests/              # 9 test dosyasi, 377 test
  docs/               # ADR'ler, FEATURE_IDEAS, bu dokuman
  install.sh          # Hedef repoya kurulum
  update.sh           # Guncelleme (uclu checksum)
```

## Sonraki Adimlar

1. **MCP adaptor entegrasyonu** — Parasut ve/veya D365 adaptoru yazilarak kit'in gercek ERP verisiyle calismasi saglanacak. Rehber: [MCP_ENTEGRASYON_REHBERI.md](MCP_ENTEGRASYON_REHBERI.md)
2. **Senaryo A guvenilirligi** — Anthropic forced delegation API acarsa ragip-aga dedicated session guvenilir hale gelecek
3. **CLI modu degerlendirmesi** — ragip_aga.py'nin standalone CLI modu kullanim verisi toplanacak (FEATURE_IDEAS I1)

---

*Teknik kurulum, test calistirma ve gelistirme ortami icin: [README.md](../README.md)*
*MCP adaptor yazma rehberi: [MCP_ENTEGRASYON_REHBERI.md](MCP_ENTEGRASYON_REHBERI.md)*
*Gelecek degerlendirmeleri: [FEATURE_IDEAS.md](FEATURE_IDEAS.md)*
*Mimari karar detaylari: [docs/adr/](adr/)*
